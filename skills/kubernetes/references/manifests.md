# Kubernetes Manifests

> YAML/JSON files that declare desired state. Store in Git — no imperative shell scripts.

## Anatomy of a Manifest

Every Kubernetes object has four sections:

| Section | Purpose |
|---|---|
| `apiVersion` + `kind` | Type metadata (e.g., `apps/v1`, `Deployment`) |
| `metadata` | Name, namespace, labels, annotations |
| `spec` | **Your job** — the desired state you declare |
| `status` | **Kubernetes' job** — the actual live state (never write this) |

## Pro-Tips

- **Generate boilerplate, don't type it:** `kubectl run my-app --image=my-image --dry-run=client -o yaml > pod.yaml`
- **Look up fields in the terminal:** `kubectl explain pod.spec.containers` — no need to search online
- **Deploy a whole directory at once:** `kubectl apply -f ./manifests/` — add `-R` to recurse subdirectories

## Kustomize

Kustomize is built into kubectl (`-k` flag instead of `-f`). It customizes manifests without templating — maintain one base manifest and apply environment-specific patches.

- **Invoke:** `kubectl apply -k ./overlays/production/` (processes through Kustomize before applying)
- **Driven by `kustomization.yaml`:** Lists base manifests and patches (partial YAML or JSON Patch format). Kustomize merges them into final manifests.
- **Primary use case:** Deploying the same app across dev/staging/prod without duplicating manifests. One base + small per-environment patches.

For Helm-style templating with variables and logic, see `references/helm.md`. Kustomize is the lighter alternative when you just need config overrides.

## Golden Rules

- **Always quote ambiguous YAML strings.** Unquoted `true`, `false`, `yes`, `no`, `on`, `off`, and bare numbers are silently cast to booleans or integers by the YAML parser. If Kubernetes expects a string (e.g., env vars, annotations), this produces cryptic errors like `ReadString: expects " or n, but found t`. Always use quotes: `"true"`, `"123"`.

- **Never write the `status` block.** You own `spec`. Kubernetes controllers own `status` and will overwrite whatever you put there.

- **Mind whitespace in multi-line strings.** When using `|` or `|-` in ConfigMaps or scripts, trailing spaces on any line cause the YAML emitter (including kubectl's) to fall back to double-quoted style with `\n` escapes when re-serializing (e.g., `kubectl get -o yaml`). The data is not corrupted, but the output becomes unreadable. Strip trailing whitespace.

- **Always declare `namespace` in the manifest.** Never rely on the active `kubectl` context to determine where an object lands. Hardcode the namespace in `metadata` to prevent accidental deployments to the wrong environment.

- **Always attach labels.** Labels are functional, not decorative. Services and ReplicaSets use label selectors to discover which pods they own or route traffic to. Apply standard labels (`app`, `version`, `rel`) consistently across all objects.
