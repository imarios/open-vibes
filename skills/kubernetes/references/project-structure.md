# Project Structure

> How to organize Kubernetes manifests, Helm charts, and environment configs in your repository. Read this when starting a new project or adding K8s deployment files for the first time.

## Repository Strategy

| Strategy | Best for | Trade-offs |
|---|---|---|
| **Manifests with app code** | Small teams, single-service repos | Simple — one PR changes code + deployment. Breaks down at scale: manifest changes trigger CI builds, and access control can't be separated |
| **Separate GitOps config repo** | Multi-service orgs, production GitOps | Clean audit trail, no infinite CI loops, independent access control. Recommended by Argo CD and Flux for production |
| **Hybrid** (chart in app repo, env values in config repo) | Teams that want chart ownership with environment separation | Chart stays with the developers who maintain it; platform team controls environment-specific values |

**Natural progression:** Start with manifests in the app repo. Split out a config repo when you hit pain points — CI builds firing on config-only changes, multiple services needing shared infra config, or the need for separate access control on production manifests. The hybrid approach is the bridge: move environment values to the config repo first, keep the chart with the app code.

## Single-Service App Repo

### With Helm

```
my-service/
├── src/
├── Dockerfile
├── chart/                    # singular — one chart per repo
│   ├── Chart.yaml
│   ├── values.yaml           # defaults only
│   ├── values-prod.yaml      # environment overrides
│   └── templates/
│       ├── _helpers.tpl
│       ├── deployment.yaml
│       ├── service.yaml
│       └── tests/
└── .github/workflows/
```

For a repo hosting multiple charts, use `charts/` (plural): `charts/frontend/`, `charts/api/`, etc.

### With Kustomize

```
my-service/
├── src/
├── Dockerfile
├── deploy/
│   ├── base/
│   │   ├── kustomization.yaml
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── overlays/
│       ├── dev/
│       │   ├── kustomization.yaml    # references ../../base
│       │   └── replica-patch.yaml
│       ├── staging/
│       └── production/
└── .github/workflows/
```

Use `components/` alongside `overlays/` when features are independently togglable (e.g., monitoring, debug sidecar) rather than representing full environments. Google's microservices-demo uses this pattern.

### With Raw Manifests

```
my-service/
├── src/
├── Dockerfile
├── k8s/                      # or manifests/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
└── .github/workflows/
```

Deploy a whole directory: `kubectl apply -f k8s/` — add `-R` to recurse subdirectories. See `references/manifests.md`.

## Multi-Service Projects

Most real projects have containers with fundamentally different production stories. Organize by lifecycle, not by technology:

| Category | Examples | Dev | Prod |
|---|---|---|---|
| **Application** | FastAPI server, ARQ alert-analysis worker, ARQ integrations worker | Containers you build | Same containers, different config |
| **Simulators** | Splunk SIEM, OpenLDAP directory, echo HTTP server | Run locally for testing/demos | **Don't exist** — real Splunk, corporate LDAP, and live APIs replace them |
| **Infrastructure** | Postgres, Valkey (Redis), MinIO, Vault, Keycloak | Containers | **Managed services** — Aurora/RDS, ElastiCache, S3, Secrets Manager, Cognito |
| **Observability** | Prometheus, Grafana, Postgres Exporter | Optional lightweight stack | kube-prometheus-stack / LGTM — see `references/observability.md` |

### Directory Layout

```
deploy/
├── app/                        # What you ship — API + workers
│   ├── chart/
│   │   ├── templates/
│   │   │   ├── api-deployment.yaml
│   │   │   ├── alert-worker-deployment.yaml
│   │   │   └── integrations-worker-deployment.yaml
│   │   └── values.yaml
│   └── values-prod.yaml
├── simulators/                 # Dev/test ONLY — never referenced from prod overlays
│   ├── splunk/
│   ├── openldap/
│   └── echo-server/
├── infrastructure/
│   ├── dev/                    # Containerized: Postgres, Valkey, MinIO, Vault, Keycloak
│   └── prod/                   # ExternalName Services pointing to RDS, ElastiCache, S3, etc.
└── observability/              # Separate lifecycle
    └── values.yaml             # kube-prometheus-stack overrides
```

**Why this matters:**
- **Simulators have no prod overlay.** They are structurally absent from production — no one can accidentally deploy a Splunk simulator to prod.
- **Infrastructure swaps cleanly.** In dev, `postgres` is a pod running `postgres:15-alpine`. In prod, it's an `ExternalName` Service pointing at your RDS endpoint — same DNS name inside the cluster, app connects to `postgres:5432` regardless.
- **Observability has its own lifecycle.** Upgrading Grafana should not require redeploying your API. Keep it in a separate directory (or separate Helm release).

### Infrastructure Swapping Pattern

The same Kubernetes Service name resolves in both environments — the app connects to `postgres:5432` regardless:

```yaml
# dev: containerized Postgres
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
  ports:
    - port: 5432

# prod: managed RDS via ExternalName
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  type: ExternalName
  externalName: my-cluster.abc123.us-east-1.rds.amazonaws.com
```

Same pattern applies to Valkey → ElastiCache, MinIO → S3 (via endpoint config), and Vault → Secrets Manager (via Pod Identity). Use Kustomize overlays or Helm values to swap between the two.

## GitOps Config Repo

Three top-level concerns — consistent across Flux, Argo CD, and Red Hat patterns:

```
gitops-config/
├── clusters/                 # Per-cluster entrypoints (Flux Kustomizations or Argo CD apps)
│   ├── production/
│   └── staging/
├── infrastructure/           # Platform tooling (ingress, cert-manager, monitoring)
│   ├── controllers/
│   └── configs/
└── apps/                     # Application workloads
    ├── my-service/
    │   ├── base/
    │   └── overlays/
    │       ├── dev/
    │       ├── staging/
    │       └── production/
    └── other-service/
```

- `clusters/` is the only directory that varies per cluster — it points Flux/Argo at the other directories
- `infrastructure/` vs `apps/` separation lets you deploy platform tooling independently from application workloads
- Each app follows the same `base/` + `overlays/` Kustomize pattern (or Helm values layering)

## Naming Conventions

| Directory name | When to use |
|---|---|
| `chart/` | Single Helm chart in an app repo |
| `charts/` | Multiple Helm charts (monorepo or umbrella) |
| `deploy/` | General-purpose — Go ecosystem convention; may contain Helm, Kustomize, or raw YAML |
| `k8s/` or `manifests/` | Raw YAML without templating |
| `kustomize/` | Kustomize alongside other deploy methods |
| `infrastructure/` | Cluster-level resources in a GitOps repo |

## Golden Rules

- **Keep Dockerfiles next to their source code.** The Dockerfile and the code it builds should be in the same directory to keep the build context self-contained.

- **Never reference `HEAD` or mutable branches in Kustomize bases or Helm dependencies.** Always pin to a Git tag or commit SHA. `github.com/org/repo//manifests?ref=main` will break silently when main changes.

- **Don't duplicate manifests across environments.** Use Kustomize `base/` + `overlays/` or Helm `values.yaml` + `values-<env>.yaml` layering. If you're copying YAML between `dev/` and `prod/`, you're doing it wrong. See `references/manifests.md` → Kustomize.

- **Don't set `replicas` in manifests if an HPA controls scaling.** The manifest and the autoscaler will fight each other on every deployment, causing thrashing.

- **Separate infrastructure provisioning from application deployment.** Terraform creates clusters and networks. Helm/Kustomize deploys apps. Mixing them (e.g., Terraform's Helm provider deploying apps) creates tight coupling and long plan/apply cycles.

- **Use a separate config repo at scale.** When manifest changes in the app repo trigger CI builds, and CI builds update image tags in manifests, you get infinite loops. A separate GitOps repo breaks the cycle and gives your platform team independent access control.
