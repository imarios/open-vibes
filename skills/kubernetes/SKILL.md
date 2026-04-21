---
name: kubernetes
description: Use this skill when working with Kubernetes — writing manifests, managing clusters, debugging workloads, setting up observability, or deploying to EKS. Covers local dev, Helm, kubectl, k9s, Kustomize, OpenTelemetry, Grafana stack, and CI/CD with GitHub Actions.
version: 1.0.0
---

# Kubernetes

## Golden Rules

1. **One process per container** — Only co-locate multiple containers in a pod when they are tightly coupled and must share the same host (e.g., app + sidecar proxy).
2. **Always define Readiness and Liveness Probes — but never test external dependencies** — Probes that check a database will cause cascading restarts across your entire system when that database goes down.
3. **Always handle `SIGTERM` gracefully** — Kubernetes sends `SIGTERM` before killing a pod. Fix your application to shut down cleanly — do not shorten the grace period as a workaround. See `references/operations.md` for `preStop` hook details.
4. **Secrets: mount as volumes, never env vars** — Env vars leak in crash reports and child processes. Mount Secrets as read-only volume files (stored in tmpfs). Remember: Secrets are Base64-encoded, not encrypted — enforce strict RBAC or use external secret management. See `references/security.md`.
5. **Least privilege for containers** — Drop all capabilities, run as non-root, apply a seccomp profile. Never grant full privileges unless absolutely required. See `references/security.md` for the full `securityContext` pattern.

## Reference Routing Table

### Author

| Reference | Read when you need to… |
|-----------|------------------------|
| `project-structure.md` | Start a new project or add K8s deployment files — repo strategy, directory layouts, naming conventions |
| `manifests.md` | Author Deployments, Services, ConfigMaps, Secrets, Ingress — YAML structure, field conventions, Kustomize overlays |
| `configuration.md` | Work with ConfigMaps or inject runtime metadata via Downward API — includes the live-update gotcha (env var vs volume-mounted) |

### Deploy

| Reference | Read when you need to… |
|-----------|------------------------|
| `helm.md` | Install charts or author a new Helm chart — values, templating, release management, CI/CD pipelines, secrets handling |
| `local-dev.md` | Set up a local cluster (Minikube, kind, Docker Desktop) — fast dev loops, live debugging, ephemeral containers |

### Cloud

| Reference | Read when you need to… |
|-----------|------------------------|
| `eks.md` | Provision, secure, or operate EKS clusters on AWS — Pod Identity, Karpenter autoscaling, per-PR preview environments, cluster upgrades |

### Operate

| Reference | Read when you need to… |
|-----------|------------------------|
| `kubectl.md` | Run core commands (logs, exec, port-forward, describe, debug) or troubleshoot pods and cluster state |
| `k9s.md` | Navigate or debug a cluster interactively — keyboard shortcuts, filtering, special views (Pulses, XRay) |
| `operations.md` | Handle scaling, rollouts, workload types (DaemonSets, Jobs, CronJobs), pod lifecycle, production readiness, multi-tenancy |
| `observability.md` | Set up logging, metrics, tracing — collection architecture, OTEL Collector patterns, Grafana LGTM stack, signal correlation |

### Harden

| Reference | Read when you need to… |
|-----------|------------------------|
| `security.md` | Secure workloads, configure container privileges, handle Secrets — capabilities, ServiceAccount tokens, hostNetwork, Pod Security Standards |
| `networking.md` | Configure Services, Ingress, DNS, or network policies — connectivity, exposure patterns, namespace isolation |
| `storage.md` | Work with PVCs, PersistentVolumes, StorageClasses, emptyDir — retention policies, access modes, hostPath risks |
