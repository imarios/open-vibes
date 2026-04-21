# Kubernetes Networking

> Pod-to-pod communication, stable service discovery, and external traffic exposure.

## Core Concepts

- **Flat network:** Every pod gets a unique IP. All pods communicate directly across the cluster without NAT, regardless of which node they run on — including across namespaces. There is no network isolation between namespaces by default. Use `NetworkPolicy` objects to explicitly restrict cross-namespace traffic. See `references/operations.md` → Namespaces & Multi-Tenancy.
- **Intra-pod networking:** Containers in the same pod share a network namespace — same IP, same port space, communicate via `localhost`.

### Service Types (Layer 4)

| Type | Accessibility | How it works |
|---|---|---|
| `ClusterIP` | Internal only (default) | Stable virtual IP accessible within the cluster |
| `NodePort` | External via node IP | Opens a port (e.g., 30080) on every node and forwards to the service |
| `LoadBalancer` | External via cloud LB | Triggers cloud provider to provision a load balancer in front of NodePorts |

### Ingress & Gateway API (Layer 7)

- **Ingress:** Reverse proxy exposing multiple HTTP/HTTPS services through a single public IP using host-based or path-based routing. Handles TLS termination.
- **Gateway API:** The modern evolution of Ingress. Separates concerns by role — cluster admins manage `Gateway` objects, developers manage `HTTPRoute` / `TCPRoute` / `TLSRoute`. Natively supports L4 protocols and cross-namespace routing.

## NetworkPolicy

By default all pods can communicate with all other pods across all namespaces. `NetworkPolicy` objects let you explicitly restrict this.

**CNI plugin required:** The Kubernetes API will accept `NetworkPolicy` objects even if your cluster can't enforce them. They only take effect if your cluster uses a CNI plugin that supports network policies (e.g., Calico, Cilium, Weave Net). Flannel and kind's default network do not enforce them without extra configuration.

### Two-Step Tenant Isolation Pattern

**Step 1 — Default deny all traffic in the namespace:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: tenant-a
spec:
  podSelector: {}       # Selects all pods in this namespace
  policyTypes:
  - Ingress
  - Egress
```

**Step 2 — Explicitly allow what you need:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: tenant-a
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}   # Allows traffic from any pod in the same namespace
```

For cross-namespace access (e.g., a shared monitoring service), use `namespaceSelector` in the `from` rules to target pods by namespace label rather than opening all traffic.

## Pro-Tips

- **DNS shortcuts:** Within the same namespace, use `http://<service-name>`. Across namespaces, use `http://<service-name>.<namespace>`.
- **Headless services:** Set `clusterIP: None` to skip load-balancing — DNS returns raw pod IPs instead. Essential for stateful apps (e.g., MongoDB replica sets) that need direct peer discovery.
- **Keep traffic local:** Set `internalTrafficPolicy: Local` on a service to ensure client pods only talk to the DaemonSet agent on their own node, avoiding cross-node hops.
- **Topology-aware hints:** In multi-zone clusters, enable topology-aware hints to route traffic to endpoints in the same availability zone — avoids cross-zone data transfer costs.
- **Debug routing issues:** Services track `EndpointSlices`, not pods directly. If a service isn't routing, check `kubectl get endpointslices` to verify pod IPs are actively registered.

## Golden Rules

- **Never rely on pod IPs.** They change every time a pod is recreated or rescheduled. Always communicate through a Service or Gateway.

- **Services cannot do cookie-based session affinity.** Services operate at L4 (TCP/UDP) and cannot read HTTP headers or cookies. For sticky sessions, use an Ingress or Gateway (L7).

- **Understand the `externalTrafficPolicy` trade-off.** The default forwards traffic to pods on any node (extra hop, client IP hidden). Setting `externalTrafficPolicy: Local` preserves the client IP and removes the hop — but traffic arriving at a node with no local pod for that service is **dropped**, not rerouted, causing uneven load distribution if pods are not evenly spread across nodes.

- **Always define Readiness probes to protect your Services.** A pod is only added to a Service's endpoints when it is Ready. Without a probe, Kubernetes assumes instant readiness and sends traffic before the app has finished booting — causing dropped connections.

- **Never test external dependencies in Readiness probes.** If your frontend's readiness probe checks the database, a transient database blip will pull all frontend pods from the Service endpoints, taking the entire frontend offline. Scope probes strictly to the pod itself.
