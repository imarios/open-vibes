# Helm

> The Kubernetes package manager. Define, install, and upgrade complex applications as versioned, repeatable releases.

## Core Concepts

- **Chart** — A bundle of Kubernetes YAML manifests using Go templating (supports variables, `if/else`, loops, and 60+ Sprig functions).
- **Values** — Variables injected into templates. Charts ship a default `values.yaml`; you supply your own to override without touching the chart source.
- **Release** — A deployed instance of a chart. Multiple releases of the same chart can coexist in the same cluster, each tracked independently.

## Common Commands

| Command | What it does |
|---|---|
| `helm repo add <name> <url>` | Connect to a remote chart repository |
| `helm repo update` | Refresh local cache of all added repos |
| `helm search repo <keyword>` | Search added repos for a chart |
| `helm install <release> <chart> -f values.yaml` | Deploy a chart as a new release |
| `helm upgrade --install <release> <chart> -f values.yaml --atomic` | **CI/CD golden command** — installs or upgrades; `--atomic` auto-rolls back on failure |
| `helm rollback <release> <revision>` | Revert to a previous revision (omit revision to go back one) |
| `helm history <release>` | Show all revisions for a release — check before rolling back |
| `helm template <release> <chart> -f values.yaml` | Render templates to raw YAML locally without touching the cluster — use to debug values overrides |
| `helm lint <chart>` | Validate chart structure and templates before deploying |
| `helm ls` / `helm list -A` | List releases in current namespace / all namespaces |
| `helm uninstall <release>` | Remove release and associated resources |

## Best Practices

### Chart Authoring

- **Add `values.schema.json`** to every chart. Helm validates against it during `install`, `upgrade`, `template`, and `lint`. Use the `helm-values-schema-json` plugin to auto-generate a starting schema from existing `values.yaml`, then refine.
- **Namespace all `define` templates** — e.g., `{{- define "myapp.fullname" -}}`, not `{{- define "fullname" -}}`. Defined templates are globally accessible across subcharts and will collide.
- **Use `include`, not `template`** — `template` cannot participate in pipelines, so `{{ include "myapp.labels" . | indent 4 }}` works but `{{ template ... | indent 4 }}` does not.
- **Never hardcode namespaces in templates.** Use `{{ .Release.Namespace }}` or omit `metadata.namespace` and let `--namespace` handle it.
- **Use `required` for mandatory values:** `{{ required "database.host is required!" .Values.database.host }}` — fails fast with a clear message instead of deploying a broken release.
- **Favor flat values over deeply nested ones.** Deep nesting requires existence checks at every level in templates. Use nesting only for clusters of related values. Prefer maps over lists — `--set servers.foo.port=80` is more ergonomic than `--set servers[0].port=80`.

### CI/CD Pipeline

Minimum viable pipeline: `helm lint` → `kubeconform` → `helm diff` → deploy.

- **`helm diff`** (plugin) — preview changes before every production upgrade:
  ```
  helm diff upgrade myapp ./mychart -f values.yaml --suppress-secrets --detailed-exitcode
  ```
  `--suppress-secrets` prevents leaking sensitive values in CI logs. `--detailed-exitcode` returns exit code 2 when changes exist, enabling approval gates.
- **`kubeconform`** (successor to deprecated `kubeval`) — validates rendered manifests against Kubernetes OpenAPI schemas. Catches invalid fields, wrong API versions, and missing CRDs that `--dry-run=client` and `helm lint` miss.
- **Always use `--atomic --timeout 5m`** for production deployments. Add `--cleanup-on-fail` to remove new resources created during a failed upgrade.

### Secrets

Never store secrets in `values.yaml` or Git. Use one of:
- **External Secrets Operator** referencing Vault / AWS Secrets Manager / Azure Key Vault (recommended for GitOps)
- **helm-secrets plugin** with Mozilla SOPS for encrypting values files before committing
- **Sealed Secrets** for in-cluster encryption

### ConfigMap/Secret Restart Trigger

Templates re-execute on every `helm upgrade`. To force a rolling restart when a ConfigMap changes, add a checksum annotation:
```yaml
annotations:
  checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

### Umbrella Charts

Use umbrella charts for tightly coupled infrastructure stacks (monitoring, logging). For independently deployable microservices, use one chart per service — an umbrella creates deployment coupling where a change to one service forces redeployment of the entire stack.

## Key Caveats

- `helm uninstall` does **not** remove CRDs, PVCs, or namespaces — these are intentionally preserved to avoid data loss. Add `helm.sh/resource-policy: keep` to PVCs or other stateful resources to prevent deletion even on uninstall.
- Add `--namespace <ns> --create-namespace` to `install`/`upgrade` to target or create a namespace in one step.
- Use `--wait` with install/upgrade to block until resources reach a ready state before declaring success.
- Beware `randAlphaNum` in templates — random values regenerate on every `helm upgrade`, causing unnecessary restarts. Use `lookup` to check if a Secret exists before generating.
