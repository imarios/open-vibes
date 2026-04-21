# kubectl

> Core commands for inspecting, managing, and debugging Kubernetes resources. For interactive cluster navigation, see `references/k9s.md`.

## Useful Shortcuts

- **Built-in docs:** `kubectl explain <resource>` — no need to Google API specs. Drill down with dot notation: `kubectl explain pod.spec.containers`
- **Generate YAML without applying:** `kubectl create deploy my-app --image=my-image --dry-run=client -o yaml > app.yaml`
- **Short resource names:** `po` (pods), `deploy` (deployments), `svc` (services), `ns` (namespaces), `cm` (configmaps), `rs` (replicasets)

## Inspecting & Monitoring

| Command | What it does |
|---|---|
| `kubectl get <resource>` | List resources |
| `kubectl get <resource> -o wide` | List with extra details (node, IP) |
| `kubectl get <resource> -o yaml` | Dump full manifest |
| `kubectl get <resource> -w` | Stream live state updates |
| `kubectl get <resource> -l <key>=<value>` | Filter by label selector |
| `kubectl get <resource> -A` | List across all namespaces |
| `kubectl describe <resource> <name>` | Deep details — check **Events** at the bottom first |

## Creating & Modifying

| Command | What it does |
|---|---|
| `kubectl apply -f <file.yaml>` | Declarative create or update from manifest (also accepts a directory) |
| `kubectl edit <resource> <name>` | Edit live object in-place (`export KUBE_EDITOR="nano"` to set editor) |
| `kubectl scale deploy <name> --replicas=X` | Scale a Deployment or ReplicaSet |

## Debugging & Troubleshooting

| Command | What it does |
|---|---|
| `kubectl logs <pod>` | Dump container logs |
| `kubectl logs <pod> -f` | Stream logs live |
| `kubectl logs <pod> -c <container>` | Target a specific container in a multi-container pod |
| `kubectl logs <pod> --previous` | Logs from a crashed/restarted container |
| `kubectl exec -it <pod> -- sh` | Interactive shell inside a running container |
| `kubectl debug <pod> -it --image <image>` | Attach an ephemeral container — use when the pod has no shell or tools |
| `kubectl port-forward <pod-or-svc> <local>:<remote>` | Tunnel from localhost directly to a pod or service, bypassing load balancers |
| `kubectl label pod <pod> app-` | Remove a label to detach a pod from its controller — see below |

### Detach a Pod for Live Debugging

Change or remove a pod's labels to detach it from its Deployment/ReplicaSet. The controller sees one fewer matching pod and spins up a replacement, while the broken pod stays running for you to investigate — without affecting production traffic:

```
kubectl label pod my-app-7d6f8b5c9-x2k4z app-    # removes the "app" label
```

The pod is now orphaned: no controller manages it, no Service routes traffic to it, but it's still running and you can `exec`, inspect logs, or attach a debug container at your leisure. Delete it manually when done. See also `references/local-dev.md` → Live Debugging.
