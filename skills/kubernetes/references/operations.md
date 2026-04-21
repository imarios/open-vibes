# Kubernetes Operations

> Scaling, rollouts, resource management, workload types, pod lifecycle, and multi-tenancy patterns.

## Scaling & Resource Management

- **Declarative scaling:** `kubectl scale deploy <name> --replicas=X` updates desired state; controllers reconcile by creating or deleting pods.
  - Scale to zero to pause workloads and save compute without losing configuration.
- **Horizontal autoscaling:** Kubernetes can monitor resource usage and adjust replica counts automatically to handle fluctuating load.
- **Resource requests & limits:** Always constrain CPU and memory per container to prevent resource starvation of the node or system processes (enforced via Linux cgroups).
  - Use the Downward API (`resourceFieldRef`) to inject limits as env vars so memory-aware runtimes (e.g., JVMs) know their boundaries.

## Rollout Strategies

| Strategy | Behavior | When to use |
|---|---|---|
| **RollingUpdate** (default) | Replaces pods gradually; service stays up. Tuned via `maxSurge` and `maxUnavailable` (both default to 25%). | Most apps |
| **Recreate** | Deletes all old pods before creating new ones — guarantees downtime. | Apps that cannot run two versions concurrently |

- **Rollback:** `kubectl rollout undo deploy <name>` — Deployments retain old ReplicaSets as revision history. StatefulSets use `ControllerRevision` objects.
- **Pause/resume:** `kubectl rollout pause` / `kubectl rollout resume` — pause midway to observe a canary pod before continuing.

## Workload Types

| Controller | Use when |
|---|---|
| **Deployment** | Stateless apps — pods are interchangeable, freely scaled and replaced |
| **StatefulSet** | Stateful apps — requires stable network identity and dedicated persistent storage |
| **DaemonSet** | Node-level agents — exactly one pod per node (log collectors, CNI plugins, kube-proxy) |
| **Job** | Finite run-to-completion tasks — database migrations, batch processing, report generation |
| **CronJob** | Scheduled Jobs — wraps a Job with a time-based schedule (e.g., daily at midnight) |

## Pod Lifecycle

- **Init containers:** Run sequentially before main containers start. Use for setup tasks (pre-populating files, waiting for a dependency) — never put init logic in the main app.
- **`postStart` hook:** Executes immediately after a container starts.
- **`preStop` hook:** Executes before `SIGTERM` is sent, but the `terminationGracePeriodSeconds` countdown starts in parallel. If the hook exceeds the grace period, `SIGKILL` is sent regardless. Budget the hook's execution time within the total grace period — a 25-second hook on a 30-second grace period leaves only ~5 seconds for your app to handle `SIGTERM`.

## Namespaces & Multi-Tenancy

Namespaces split a physical cluster into logical virtual clusters — one per team or tenant.

**What namespaces give you:**
- **Naming scope** — different teams can deploy resources with identical names without collision
- **RBAC boundaries** — users can be restricted to their own namespace via Role-Based Access Control
- **Resource quotas** — limit CPU/memory consumption per namespace

**What namespaces do NOT give you:**
- **Compute isolation** — pods across namespaces share the same nodes and OS kernel; resource exhaustion or a container breakout in one namespace affects others
- **Network isolation** — by default, pods in any namespace can freely communicate with pods in any other namespace. To enforce cross-namespace traffic restrictions, you must explicitly configure `NetworkPolicy` objects.

## Golden Rules

- **Always set `minReadySeconds` on Deployments.** This forces Kubernetes to wait after a pod reports Ready before continuing the rollout. If the pod crashes within that window, it never becomes Available, so the controller stalls — preventing a broken release from propagating. Pair with `progressDeadlineSeconds` (default 600s), which marks the rollout as `ProgressDeadlineExceeded` after the timeout. Note: Kubernetes does not automatically roll back — external tooling or manual intervention is required.

- **Define Readiness, Liveness, and Startup probes correctly — never test external dependencies.**
  - *Liveness* restarts stuck apps. *Readiness* removes unready pods from traffic rotation.
  - Probes that check an external database will take your frontend offline when that database blips, causing cascading failures.
  - Use a *Startup probe* for slow-booting apps — it gives extra boot time before handing off to the stricter Liveness probe.

- **Never use namespaces to separate Production, Staging, and Dev.** Namespaces lack runtime and network isolation. A runaway dev workload can starve production pods on the same node. Use separate physical clusters for prod vs. non-prod.

- **Never use Deployments for stateful apps.** Deployments treat pods as interchangeable cattle. Stateful apps need stable identities and dedicated volumes — always use **StatefulSets** to guarantee at-most-one semantics and prevent split-brain data corruption.

- **Always configure a `preStop` hook if your app ignores `SIGTERM`.** If your application drops connections on termination, use a `preStop` hook to drain gracefully before the signal is sent — no application code changes required. Keep the hook fast: its execution time counts against `terminationGracePeriodSeconds`.
