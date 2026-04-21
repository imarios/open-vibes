# Local Kubernetes Development

> Fast iteration patterns for local clusters — from tool choice to live debugging.

## Choosing a Local Cluster

| Tool | Best for | Notes |
|---|---|---|
| **Minikube** | Most users — the safest, most standard starting point | Mature, community-maintained; runs a more recent K8s version than Docker Desktop; defaults to Docker or vfkit driver on macOS (HyperKit deprecated); supports multi-node clusters |
| **kind** (Kubernetes IN Docker) | Multi-node cluster simulation, advanced debugging, minimal resource footprint | Nodes run as Docker containers (not VMs); use when you need to test multi-node behavior locally |
| **Docker Desktop** | macOS/Windows beginners who want zero setup | Built-in single-node cluster; K8s version may lag behind Minikube and kind |

## Fast Dev Loop

- **Port-forward instead of configuring Services:** `kubectl port-forward <pod> 8080:8080` — skip Ingress setup during local testing
- **API proxy shortcut:** `kubectl get --raw /api/v1/namespaces/<ns>/pods/<pod>/proxy/` — access HTTP apps directly through the API server, no port-forward needed
- **Lock your namespace:** Stop appending `-n my-namespace` to every command: `kubectl config set-context --current --namespace <my-dev-ns>`
- **Generate boilerplate YAML:** See `references/manifests.md` — `--dry-run=client -o yaml`

## Testing Resource Limits Locally with Docker

Before defining `resources` in a pod manifest, test limits directly via Docker:

| Flag | What it does |
|---|---|
| `--cpuset-cpus="1,2"` | Pin container to specific CPU cores |
| `--cpus="0.5"` | Restrict to half a CPU core of time |
| `--memory="100m"` | Cap memory at 100 megabytes |

## Live Debugging

- **Ephemeral debug containers:** Production images should have no shells or tools. Attach one on demand:
  ```
  kubectl debug <pod> -it --image nicolaka/netshoot --target=<container-name>
  ```
  The `--target` flag shares the PID namespace with the specified container so you can see its processes — without modifying the pod spec or restarting the pod. Requires containerd 1.5.0+ (standard on any modern cluster).

- **Hot-swap files:** Inject a file without rebuilding the image:
  ```
  kubectl cp ./local-file.html <pod>:/path/in/container
  ```

- **Crash logs:** `kubectl logs <pod>` shows the current instance. Use `--previous` (`-p`) to read logs from a crashed/restarted container.

- **Attach to stdin:** `kubectl attach -i <pod>` — connects your terminal directly to the app's stdin stream for interactive input.

- **Detach a pod for live debugging:** Remove a label to disconnect a broken pod from its controller. The controller spins up a healthy replacement while you debug the original in-place, without affecting traffic:
  ```
  kubectl label pod my-app-7d6f8b5c9-x2k4z app-
  ```
  The pod is now orphaned — no Service routes to it, but it's still running for inspection. Delete manually when done. See also `references/kubectl.md` → Debugging.

## Golden Rules

- **Decouple config from images.** Never hardcode config in your Dockerfile. Use ConfigMaps for env vars and Secrets for credentials — your local pod manifest should be structurally identical to your production manifest.

- **Avoid `hostPath` volumes.** Mounting your local filesystem into a pod breaks portability and introduces security risks. Use `emptyDir` for scratch space or provision local PersistentVolumes properly.

- **Scale pods, not containers.** Horizontal scaling duplicates the entire pod. Keep frontend and database in separate pods — scaling a combined pod causes unnecessary database lock conflicts.
