# Configuration: ConfigMaps & Downward API

> Injecting environment-specific config into pods without baking it into the container image.

## ConfigMaps

ConfigMaps store configuration data as key-value pairs — properties files, URLs, entire config files — outside the image. Inject them into pods two ways:

| Method | How | Live-updates on change? |
|---|---|---|
| Environment variable | `envFrom` / `valueFrom.configMapKeyRef` | **No** — pod must restart |
| Mounted volume file | `volumes` + `volumeMounts` | **Yes** — file is updated automatically |

## Downward API

Lets a running container discover facts about itself at runtime — without hardcoding them in the manifest or querying the API server:

| What you can inject | How |
|---|---|
| Pod name, namespace, IP | `fieldRef` in env var or mounted file |
| CPU/memory requests & limits | `resourceFieldRef` in env var |

Use `resourceFieldRef` to inject memory limits as env vars so memory-aware runtimes (e.g., JVMs) can size themselves correctly. Limits are enforced by the Linux kernel via **cgroups** — without them, a single container can starve the entire node.

```yaml
env:
  - name: MAX_CPU_CORES
    valueFrom:
      resourceFieldRef:
        resource: limits.cpu       # whole cores; use divisor: 1m for milli-cores
  - name: MAX_MEMORY_KB
    valueFrom:
      resourceFieldRef:
        resource: limits.memory
        divisor: 1k                # 1k = kilobytes, 1Ki = kibibytes, 1M = megabytes
```

## Golden Rules

- **ConfigMap env vars do not live-update.** Changes to a ConfigMap are not reflected in running containers that consumed it as an environment variable. You must restart the pod. If you need live config changes, mount the ConfigMap as a file instead.

- **`subPath` mounts never receive live updates.** If you mount a ConfigMap volume using `subPath` (to inject a single file without overwriting the directory), that file will not auto-update when the ConfigMap changes. You must restart the pod or use a full directory mount instead.

- **Never mount Secrets as env vars.** Env vars leak in crash reports and child processes. Mount Secrets as read-only volume files (stored in tmpfs). See `SKILL.md` Golden Rules for the full rationale.
