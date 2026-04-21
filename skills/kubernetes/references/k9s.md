# k9s

> Terminal UI for Kubernetes. Use for interactive exploration and debugging. Use kubectl for scripting and CI/CD automation. They are complementary.

**Install:** `brew install derailed/k9s/k9s` (macOS) — requires kubectl and a configured kubeconfig.

## Navigation

| Key | Action |
|---|---|
| `?` | Help — shows all active shortcuts |
| `j` / `k` | Move down / up (vim-style) |
| `Esc` | Go back to previous view |
| `Ctrl+a` | Show all available resource aliases |
| `:pod`, `:deploy`, `:svc`, `:ns`, `:ctx`, `:pvc` | Jump to resource view |
| `:pod kube-system` | Jump to resource view scoped to a namespace |
| `/pattern` | Filter by regex |
| `/!pattern` | Exclude matches |
| `/-l app=web` | Filter by label selector |

## Key Operations

| Key | Action |
|---|---|
| `d` | Describe resource (equivalent to `kubectl describe`) |
| `y` | View YAML |
| `e` | Edit resource in-place |
| `l` | View container logs |
| `p` | View logs from previous (crashed) container |
| `s` | Shell into container |
| `Shift+f` | Create port-forward |
| `Shift+c` / `Shift+m` | Sort by CPU / Memory |
| `Ctrl+d` | Delete resource (with confirmation) |
| `Ctrl+k` | Force-delete resource (no confirmation) |

## Special Views

- **Pulses** (`:pulses`) — real-time dashboard of cluster health and resource usage
- **XRay** — dependency tree showing relationships between resources (Deployments → ReplicaSets → Pods)

## Best Practices

- **Use different skins per environment** (dev/staging/prod) to prevent accidental operations on the wrong cluster. Set `skin` per context in `~/.config/k9s/`.
- **Enable read-only mode** (`readOnly: true` in config) on production clusters to prevent accidental edits or deletes.
- k9s can be slow on very large clusters — fall back to kubectl when precision or automation is needed.
