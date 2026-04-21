# Kubernetes Storage

> Kubernetes separates the request for storage (developer concern) from the provisioning of storage (cluster concern).

## The Abstraction Layer

| Object | Who creates it | What it does |
|---|---|---|
| **PersistentVolumeClaim (PVC)** | Developer | Requests storage — "I need 10GB of fast SSD" |
| **StorageClass** | Cluster admin | Defines how storage is provisioned (cloud driver, disk type) |
| **PersistentVolume (PV)** | Cluster (dynamic) | The actual provisioned storage, matched to the PVC via the StorageClass |

The developer only ever interacts with PVCs. The cluster handles provisioning via CSI drivers.

**Access modes** — PVCs declare how they can be mounted:

| Mode | Meaning |
|---|---|
| `ReadWriteOnce` (RWO) | Single node can mount read-write (most common default) |
| `ReadOnlyMany` (ROX) | Many nodes can mount read-only |
| `ReadWriteMany` (RWX) | Many nodes can mount read-write (requires NFS or compatible CSI driver) |
| `ReadWriteOncePod` (RWOP) | Single pod can mount read-write (strictest) |

## Persistent Data Pattern

For any stateful application, follow this layered approach:

**1. Abstract storage with PVCs + dynamic provisioning**
Never hardcode a specific storage technology (EBS volume, NFS share) into a pod manifest. Declare a PVC with a `StorageClass` and let the CSI driver provision the PV on demand.

**2. Use StatefulSets with `volumeClaimTemplates`**
Never use a Deployment to run a stateful app — all replicas would compete for the same PVC, causing lock conflicts and crashes. StatefulSets give each pod a unique ordinal identity (`quiz-0`, `quiz-1`) and use `volumeClaimTemplates` to automatically provision a dedicated PVC per replica.

**3. Use an Operator for complex stateful apps**
StatefulSets provide stable identity and storage, but they don't understand application-level logic. Scaling a MongoDB StatefulSet won't automatically reconfigure the replica set — you'd need to do that manually. A **Kubernetes Operator** encodes this operational knowledge as a custom controller. You declare a custom resource (e.g., `MongoDBCommunity`) and the Operator manages the StatefulSet, Services, Secrets, clustering, and failovers automatically. For any production database or stateful middleware, prefer an Operator over a hand-rolled StatefulSet.

## Volume Types

| Type | Lifetime | Use for |
|---|---|---|
| `emptyDir` | Pod lifetime (survives container restarts, deleted when pod is removed) | Scratch space, sharing files between containers in the same pod |
| `PersistentVolume` | Independent of pod | Databases, stateful apps, anything that must survive pod deletion |
| `hostPath` | Node filesystem | **Avoid** — dangerous, breaks portability (see Golden Rules) |

## Golden Rules

- **Never use `emptyDir` for true persistence.** It survives container restarts but is permanently erased when the pod is deleted or evicted. Use PVCs for anything that must outlive a pod.

- **Never use `hostPath` unless strictly necessary.** It is one of the most dangerous volume types. Specific attack vectors:
  - **docker.sock escalation** — mounting `/var/run/docker.sock` lets the container run arbitrary commands on the host as root
  - **Filesystem compromise** — pointing `hostPath` at `/` gives a root-running container full read/write access to the entire host filesystem
  - **No guardrails by default** — Kubernetes does not prevent regular users from creating pods with `hostPath`; this requires explicit RBAC or admission policies to lock down

  Beyond security, `hostPath` is also unsafe for stateful data: if a pod is rescheduled to a different node, it will find a different filesystem and lose all previously written data. If you need low-latency node-local storage, use **local PersistentVolumes** instead — they are admin-provisioned, have proper security boundaries, and force the scheduler to always place the pod on the node where its storage lives.

- **Mind PVC retention when scaling down StatefulSets.** Deleting a StatefulSet's pods does not delete the PVCs — data is retained by design to prevent accidental loss. Manually clean up old PVCs or you will accumulate unexpected cloud storage costs. As of Kubernetes 1.27+, you can set `persistentVolumeClaimRetentionPolicy.whenScaled: Delete` on the StatefulSet to auto-delete PVCs on scale-down.

- **Mind the reclaim policy on dynamic PVs.** Dynamically provisioned PVs default to a `Delete` reclaim policy — deleting the PVC destroys the underlying storage. For data you must keep, set the reclaim policy to `Retain` on the StorageClass or PV.
