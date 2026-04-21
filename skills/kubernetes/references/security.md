# Kubernetes Security

> Securing workloads against container escapes, credential leakage, and lateral movement.

## Core Concepts

- **Containers share the kernel.** Unlike VMs, a compromised container can affect the host node and other pods. Enforce isolation via:
  - **Linux Capabilities** — grant only specific privileges rather than root
  - **Seccomp profiles** — filter the system calls a container is allowed to make
  - **AppArmor / SELinux** — mandatory access controls on top of capabilities

- **Secrets are encoded, not encrypted.** Kubernetes Secrets are Base64 plain text. Unless cluster admins explicitly enable encryption at rest, they are stored unencrypted in `etcd`. Anyone with API access can read them. Enforce strict RBAC and use external secret management for production. See Golden Rules.

- **No network isolation between namespaces by default.** A compromised pod in Dev can freely reach pods in Prod. Use `NetworkPolicy` to explicitly restrict cross-namespace traffic. See `references/networking.md` → NetworkPolicy.

## Pro-Tips

- **Disable automatic ServiceAccount token mounting.** By default, Kubernetes mounts a valid API token into almost every pod via a `kube-api-access` volume. If your app doesn't query the Kubernetes API, set `automountServiceAccountToken: false` in the pod spec to remove it from the attack surface.

- **Tighten Secret volume permissions.** The default file mode for Secret volumes is `0644` (world-readable). Set `mode: 0600` or `0640`. If the app runs as a non-root user, set `securityContext.fsGroup` to match the app's group ID so it can still read the files.

- **Use Init Containers for one-time authentication.** If a pod must authenticate with an external service at startup (e.g., fetch a bootstrap token), do it in an Init Container. The token stays in the ephemeral Init Container's filesystem and is never exposed to the main container.

## Golden Rules

- **Never pass Secrets as environment variables.** Env vars are leaked in startup logs, crash reports, and child processes. Always mount Secrets as read-only volume files — they are stored in memory (tmpfs) and never touch disk.

- **Never use `hostPath` for regular workloads.** Mounting the host's root directory or container socket (`/var/run/docker.sock`) gives the container full root access to the node. See `references/storage.md` → hostPath for specific attack vectors.

- **Never use `hostNetwork: true` unless building a system-level proxy.** Giving a pod the host's network namespace lets it bind to any port on the node, enabling man-in-the-middle attacks against other pods and host services.

- **Follow least privilege for capabilities.** Never set `privileged: true` except for critical node-level agents (e.g., CNI plugins). Instead, drop all capabilities, run as non-root, set a read-only root filesystem, and apply a seccomp profile:
  ```yaml
  securityContext:
    runAsNonRoot: true
    readOnlyRootFilesystem: true
    allowPrivilegeEscalation: false
    seccompProfile:
      type: RuntimeDefault
    capabilities:
      drop: ["ALL"]
      add: ["NET_ADMIN"]   # only if required
  ```

- **Enforce Pod Security Standards at the namespace level.** Pod Security Admission (stable since Kubernetes 1.25) enforces security profiles via namespace labels. The `restricted` profile automatically rejects pods that violate the rules above (non-root, drop capabilities, seccomp required):
  ```yaml
  metadata:
    labels:
      pod-security.kubernetes.io/enforce: restricted
  ```

- **Do not rely solely on Kubernetes for secret management in production.** Kubernetes Secrets have no rotation, no audit trail per-secret, and no fine-grained access controls. Integrate an external secrets manager (e.g., HashiCorp Vault) for dynamic secret generation and automatic rotation.
