# Amazon EKS

> Production Kubernetes on AWS. Covers cluster setup, IAM, autoscaling, CI/CD with per-PR namespaces, and operational patterns.

## Cluster Setup

### Auto Mode vs Self-Managed

| Mode | Best for | What AWS manages |
|---|---|---|
| **Auto Mode** (2024+) | New clusters, teams that want minimal infra ops | Compute (Karpenter-based), networking (VPC CNI), storage (EBS CSI), load balancing — all managed by AWS |
| **Self-managed node groups** | Full control over AMIs, GPUs, custom kernels | You manage everything: AMIs, scaling, CNI config, add-on versions |
| **Managed node groups** | Middle ground — AWS manages EC2 lifecycle | AWS handles node provisioning/updates; you control instance types and AMIs |

**Start with Auto Mode** for new clusters unless you need custom AMIs or GPU workloads. Auto Mode bundles Karpenter, VPC CNI, CoreDNS, and kube-proxy as AWS-managed components.

### Provisioning with Terraform

Use the official `terraform-aws-modules/eks/aws` module:

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "my-cluster"
  cluster_version = "1.31"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access = true

  # Auto Mode handles compute — no node groups needed
  cluster_compute_config = {
    enabled = true
  }
}
```

### VPC Design

| Subnet type | Use for | Notes |
|---|---|---|
| **Private subnets** | Worker nodes, pods | Nodes should never be directly internet-accessible |
| **Public subnets** | Load balancers only | Tag with `kubernetes.io/role/elb` for auto-discovery |
| **Pod subnets** (optional) | Dedicated pod CIDR | Use VPC CNI custom networking when node subnet IPs are scarce |

Tag subnets for automatic discovery:
- Private: `kubernetes.io/role/internal-elb = 1`
- Public: `kubernetes.io/role/elb = 1`
- Both: `kubernetes.io/cluster/<cluster-name> = shared`

## IAM & Security

### Pod Identity (Recommended)

Pod Identity replaces IRSA (IAM Roles for Service Accounts). Simpler setup, no OIDC provider needed:

| Step | Command/Action |
|---|---|
| Install add-on | `aws eks create-addon --cluster-name my-cluster --addon-name eks-pod-identity-agent` |
| Create IAM role | Trust policy references `pods.eks.amazonaws.com`, not an OIDC URL |
| Associate | `aws eks create-pod-identity-association --cluster-name my-cluster --namespace <ns> --service-account <sa> --role-arn <arn>` |

Pod Identity is scoped to a specific namespace + ServiceAccount pair. Pods automatically receive temporary credentials — no annotation on the ServiceAccount needed.

### Cluster Access (Access Entries)

Access Entries replace the legacy `aws-auth` ConfigMap:

| Method | Status | Notes |
|---|---|---|
| **Access Entries** | Recommended | API-managed, auditable, no risk of locking yourself out by misconfiguring a ConfigMap |
| **aws-auth ConfigMap** | Legacy | Still supported; a single bad edit can lock out all users |

```
aws eks create-access-entry --cluster-name my-cluster --principal-arn <iam-arn> --type STANDARD
aws eks associate-access-policy --cluster-name my-cluster --principal-arn <iam-arn> \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --access-scope type=cluster
```

### Network Security

| Layer | Tool | Notes |
|---|---|---|
| **Pod-to-pod** | VPC CNI Network Policies | Native in VPC CNI 1.14+ — no Calico needed. See `references/networking.md` for NetworkPolicy patterns |
| **Node-to-node** | Security Groups | Standard AWS SGs on node ENIs |
| **Pod-level SGs** | Security Groups for Pods | Assign AWS SGs directly to individual pods (requires VPC CNI `ENABLE_POD_ENI`) |

### Secrets

| Approach | When to use |
|---|---|
| **AWS Secrets Manager + CSI driver** | Production — secrets stored externally, mounted as volumes, auto-rotated |
| **External Secrets Operator** | Multi-cloud or when you need to sync secrets from multiple backends (Vault, AWS, GCP) |
| **Sealed Secrets** | GitOps — encrypt secrets in Git, decrypt in-cluster |

Install the Secrets Store CSI driver + AWS provider:
```
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver --namespace kube-system
helm install secrets-provider-aws aws-secrets-manager/secrets-store-csi-driver-provider-aws --namespace kube-system
```

## Autoscaling

### Karpenter (Recommended)

Karpenter provisions nodes in seconds by calling EC2 directly (no ASGs). Default autoscaler in Auto Mode.

| Concept | Purpose |
|---|---|
| **NodePool** | Defines constraints: instance types, zones, capacity type (on-demand/spot), limits |
| **EC2NodeClass** | AWS-specific config: AMI, subnets, security groups, user data |
| **Consolidation** | Automatically replaces underutilized nodes with cheaper/smaller ones |

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand", "spot"]
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["m5.large", "m5.xlarge", "m6i.large", "m6i.xlarge"]
  limits:
    cpu: "100"
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
```

### Karpenter vs Cluster Autoscaler

| | Karpenter | Cluster Autoscaler |
|---|---|---|
| **Provisioning** | Direct EC2 API — seconds | ASG-based — minutes |
| **Instance selection** | Picks optimal type per workload | Limited to ASG instance types |
| **Consolidation** | Built-in bin-packing and node replacement | No native consolidation |
| **Spot handling** | Native multi-instance-type diversification | Requires separate ASG per type |
| **Use when** | Default choice for all new clusters | Legacy clusters already on ASGs |

### Cost Optimization with Spot

- **Diversify instance types** — list 10+ types in NodePool `requirements` to maximize Spot availability
- **Use `topologySpreadConstraints`** to spread across AZs — Spot interruptions are usually AZ-scoped
- **Set `terminationGracePeriodSeconds`** appropriately — Spot gives a 2-minute warning before termination
- **Never run stateful workloads on Spot** — use `nodeSelector` or taints to pin StatefulSets to on-demand nodes

## CI/CD with GitHub Actions

### Per-PR Preview Environments

Each PR gets its own namespace. GitHub Actions builds, pushes, deploys, and cleans up:

```yaml
# .github/workflows/preview.yml
name: Preview Environment
on:
  pull_request:
    types: [opened, synchronize, reopened]
  pull_request_target:
    types: [closed]  # More reliable than pull_request for cleanup — won't silently skip on merge conflicts

permissions:
  id-token: write   # OIDC for AWS auth
  contents: read
  pull-requests: write  # Post preview URL as PR comment

env:
  CLUSTER_NAME: my-cluster
  AWS_REGION: us-east-1
  ECR_REPO: my-app
  NAMESPACE: preview-${{ github.event.pull_request.number }}

jobs:
  deploy:
    if: github.event.action != 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-eks
          aws-region: ${{ env.AWS_REGION }}

      - uses: aws-actions/amazon-ecr-login@v2
        id: ecr

      - name: Build and push image
        run: |
          IMAGE=${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPO }}:pr-${{ github.event.pull_request.number }}-${{ github.sha }}
          docker build -t $IMAGE .
          docker push $IMAGE
          echo "IMAGE=$IMAGE" >> $GITHUB_ENV

      - run: aws eks update-kubeconfig --name ${{ env.CLUSTER_NAME }} --region ${{ env.AWS_REGION }}

      - name: Deploy to preview namespace
        run: |
          helm upgrade --install preview-${{ github.event.pull_request.number }} ./deploy/helm \
            --namespace ${{ env.NAMESPACE }} --create-namespace \
            --set image.repository=${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPO }} \
            --set image.tag=pr-${{ github.event.pull_request.number }}-${{ github.sha }} \
            --set ingress.host=pr-${{ github.event.pull_request.number }}.preview.example.com \
            --atomic --timeout 5m

      - name: Post preview URL
        uses: actions/github-script@v8
        with:
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner, repo: context.repo.repo,
              issue_number: context.payload.pull_request.number,
              body: `Preview deployed: https://pr-${context.payload.pull_request.number}.preview.example.com`
            })

  cleanup:
    if: github.event_name == 'pull_request_target'
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-eks
          aws-region: ${{ env.AWS_REGION }}

      - run: aws eks update-kubeconfig --name ${{ env.CLUSTER_NAME }} --region ${{ env.AWS_REGION }}

      - name: Delete preview namespace
        run: |
          helm uninstall preview-${{ github.event.pull_request.number }} --namespace ${{ env.NAMESPACE }} --ignore-not-found
          kubectl delete namespace ${{ env.NAMESPACE }} --ignore-not-found
```

### GitHub Actions → AWS Authentication

Use **OIDC federation** — no long-lived AWS keys stored in GitHub Secrets:

| Step | Action |
|---|---|
| 1. Create OIDC provider | In IAM, add `token.actions.githubusercontent.com` as an identity provider |
| 2. Create IAM role | Trust policy scoped to your repo: `repo:my-org/my-app:*` (must use `StringLike` condition, not `StringEquals`, when using wildcards) |
| 3. Grant permissions | ECR push, EKS describe/update-kubeconfig, and the Kubernetes RBAC permissions the role needs |
| 4. Use in workflow | `aws-actions/configure-aws-credentials@v6` with `role-to-assume` (shown above) |

### Per-PR Namespace Hygiene

| Concern | Solution |
|---|---|
| **Resource limits** | Apply `LimitRange` and `ResourceQuota` via Helm chart templates in the preview namespace |
| **Cleanup** | `pull_request: closed` event triggers `helm uninstall` + `kubectl delete namespace`; add a CronJob safety net to garbage-collect orphaned namespaces older than 7 days |
| **Isolation** | Apply `NetworkPolicy` default-deny per namespace — see `references/networking.md` |
| **Secrets** | Use External Secrets Operator — `ClusterExternalSecret` with `namespaceSelectors` auto-syncs to any namespace with a matching label |
| **DNS** | Wildcard DNS (`*.preview.example.com`) + AWS Load Balancer Controller; use `alb.ingress.kubernetes.io/group.name` annotation to share a single ALB across all preview namespaces |

### Optional: GitOps with Argo CD

For teams that prefer pull-based deployments, Argo CD can replace the `helm upgrade` step. GitHub Actions builds and pushes the image, then updates a Git manifest. Argo CD detects the change and syncs:

```yaml
# In the GHA workflow, replace helm upgrade with:
- name: Update image tag in Git
  run: |
    yq -i '.image.tag = "${{ github.sha }}"' deploy/envs/preview-${{ github.event.pull_request.number }}/values.yaml
    git commit -am "preview: update image to ${{ github.sha }}"
    git push
```

Argo CD **ApplicationSet** with the **Pull Request Generator** can also auto-create Applications per PR — see [Argo CD docs](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-Pull-Request/).

### Container Images in ECR

```
aws ecr create-repository --repository-name my-app --image-tag-mutability IMMUTABLE
# Helm charts as OCI artifacts (Helm 3.8+) — ECR repo must include chart name:
aws ecr create-repository --repository-name charts/mychart
helm push mychart-0.1.0.tgz oci://<account>.dkr.ecr.<region>.amazonaws.com/charts
```

Enable ECR image scanning and lifecycle policies to auto-expire untagged images.

## Observability

| Layer | Tool | Notes |
|---|---|---|
| **Logs** | Fluent Bit (DaemonSet) → CloudWatch Logs | AWS-native; install via `aws-for-fluent-bit` Helm chart |
| **Metrics** | Amazon Managed Prometheus + Grafana | Or self-hosted Prometheus — use `kube-prometheus-stack` chart |
| **Traces** | AWS Distro for OpenTelemetry (ADOT) | Collector DaemonSet → X-Ray or any OTLP backend |
| **Dashboard** | Container Insights | Quick cluster-level overview; enable via CloudWatch agent add-on |

## Cluster Upgrades

EKS supports N-1 version skew (upgrade one minor version at a time).

| Step | Action |
|---|---|
| 1. **Control plane** | `aws eks update-cluster-version --name my-cluster --kubernetes-version 1.32` — takes ~25 min, zero downtime |
| 2. **Add-ons** | Update CoreDNS, VPC CNI, kube-proxy to compatible versions (Auto Mode handles this) |
| 3. **Data plane** | Managed node groups: update launch template + rolling update. Karpenter: `drift` triggers automatic node replacement |

**Test upgrades in a staging cluster first.** Use `pluto` to detect deprecated APIs before upgrading.

## Golden Rules

- **Use Pod Identity, not IRSA.** Pod Identity is simpler (no OIDC provider), more secure (shorter credential chains), and is the AWS-recommended path forward.
- **Use Access Entries, not aws-auth.** A single misconfigured aws-auth ConfigMap can lock out your entire team. Access Entries are API-managed and recoverable.
- **Start with Auto Mode.** Unless you need custom AMIs or GPU scheduling, Auto Mode eliminates most cluster operations (compute, CNI, storage, kube-proxy).
- **Diversify Spot instance types.** Never pin Spot to a single instance type — list 10+ types across multiple families to avoid capacity shortages. Pin stateful workloads to on-demand.
- **Always deploy nodes in private subnets.** Public subnets are for load balancers only. Nodes should access the internet via NAT Gateway.
- **Automate preview environment cleanup.** The `pull_request: closed` workflow handles cleanup, but add a CronJob safety net. Orphaned namespaces accumulate resources and cost.
