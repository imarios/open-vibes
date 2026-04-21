# Observability

> Logs, metrics, and traces for Kubernetes workloads. Covers collection architecture, tool choices, and how to wire the three signals together.

## Recommended Open-Source Stack

| Signal | Collector | Backend | Query language |
|---|---|---|---|
| **Metrics** | Prometheus (via kube-prometheus-stack) | Grafana Mimir | PromQL |
| **Logs** | Grafana Alloy (DaemonSet) | Grafana Loki | LogQL |
| **Traces** | OpenTelemetry Collector | Grafana Tempo | TraceQL |
| **Visualization** | — | Grafana | All three, correlated |

This is the **Grafana LGTM stack** (Loki + Grafana + Tempo + Mimir). It dominates open-source K8s observability in 2026 because Loki and Tempo use object storage (S3/GCS) instead of expensive indexing — 10x cheaper than Elasticsearch at scale. If you need full-text log search (SIEM, compliance), add OpenSearch for that subset alongside Loki.

## Collection Architecture

### How Telemetry Leaves Pods

| Pattern | How it works | When to use |
|---|---|---|
| **stdout/stderr → DaemonSet agent** | App logs to stdout; container runtime writes to node disk; DaemonSet agent tails and ships | Default for everything — `kubectl logs` works, simple, low overhead |
| **Sidecar agent** | Dedicated collector per pod | Multi-tenant isolation, per-pod routing, or apps that must log to files |
| **Direct-to-backend** | App ships telemetry via SDK | Discouraged — couples app to infra, loses buffering/retry guarantees |

**Always log to stdout/stderr.** Use a sidecar only for legacy apps that write to files. Native sidecar containers (K8s 1.33+, `restartPolicy: Always` on init containers) fix the old startup/shutdown ordering issues — the log sidecar now starts before and stops after the app container.

### Two-Tier Collection

```
Pods ──OTLP──→ Alloy DaemonSet ──→ OTEL Collector gateway (2+ replicas) ──→ Backends
                (per node)          (centralized processing)
```

- **Tier 1 (DaemonSet):** Alloy on each node — receives OTLP from local pods, tails log files, scrapes host metrics, adds K8s metadata via `k8sattributes`, forwards to gateway
- **Tier 2 (Deployment):** OTEL Collector gateway — tail sampling, filtering, attribute scrubbing, export batching. Scales independently via HPA

For tail sampling, use the `loadbalancingexporter` on Tier-1 to route by trace ID — ensures all spans for a trace reach the same gateway instance.

## Logging

### Log Collector

Use **Grafana Alloy** — it is the Grafana ecosystem's OTEL-compatible collector, replacing the deprecated Promtail (EOL March 2026). It handles logs, metrics, and traces in a single agent, so you don't need a separate tool alongside the OTEL Collector.

If you are not using the Grafana stack: **Fluent Bit** (~16MB RAM, CNCF graduated) for simple forwarding, or **Vector** (Rust, 2x+ throughput) for complex transformations.

### Structured Logging

**Always use JSON.** Minimum fields in every log line:

| Field | Why |
|---|---|
| `timestamp` | ISO 8601, always UTC |
| `level` | info/warn/error — consistent across all services |
| `message` | Human-readable event description |
| `service`, `version` | Identify what emitted the log |
| `trace_id`, `span_id` | Link to distributed traces — OTEL injects automatically via log bridge |

**Generate a correlation ID at the edge** (API gateway/ingress) and propagate via `X-Request-ID` header through all service calls. Log it in every entry. This is trivial at the start and painful to retrofit.

## Tracing

### OpenTelemetry Is the Standard

All OTEL signals are GA (traces, metrics, logs). Jaeger v1 deprecated Jan 2026; Jaeger v2 rebuilt on the OTEL Collector. Zipkin exporter deprecated Dec 2025. **Do not use vendor-specific or legacy tracing SDKs for new services.**

### Auto-Instrumentation (OTEL Operator)

The OTEL Operator injects instrumentation via mutating webhook — no code changes, no image rebuilds:

| Language | Status |
|---|---|
| Java, .NET, Python, Node.js | Production-ready |
| Go | Experimental (eBPF-based) |

```yaml
# Annotate pods or namespaces:
instrumentation.opentelemetry.io/inject-java: "true"
instrumentation.opentelemetry.io/inject-python: "true"
```

The webhook fires on pod creation only — restart pods to pick up changes.

### Trace Backend

Use **Grafana Tempo** — index-free, object-storage backed, cheapest option. You find traces by jumping from metrics (exemplars) or logs (`trace_id`), not by querying traces directly. Use Jaeger v2 only if you need standalone indexed trace search and can budget for Cassandra/Elasticsearch.

## Metrics

### kube-prometheus-stack

The standard Helm chart for K8s monitoring. One `helm install` gives you:

| Component | Role |
|---|---|
| **Prometheus Operator** | Manages Prometheus via CRDs (ServiceMonitor, PodMonitor, PrometheusRule) |
| **Prometheus** | Scrapes metrics, evaluates alerting rules |
| **Alertmanager** | Deduplicates, routes, and sends alerts (Slack, PagerDuty) |
| **Grafana** | Pre-configured cluster dashboards |
| **Node Exporter** | Host-level metrics (CPU, memory, disk) per node |
| **kube-state-metrics** | K8s object state (pod counts, deployment status) |

### Long-Term Metrics Storage

Single-instance Prometheus handles ~10M active series. Beyond that, use **Grafana Mimir** — horizontally scalable, multi-tenant, completes the LGTM stack. VictoriaMetrics is simpler to operate if you are not in the Grafana ecosystem. Thanos is the least disruptive migration path from existing Prometheus (sidecar pattern). Do not start new deployments on Cortex (superseded by Mimir).

### OTEL + Prometheus

They complement each other — OTEL does not replace Prometheus:
- Keep Prometheus for scraping existing `/metrics` endpoints (mature ecosystem)
- Use OTEL Collector's Prometheus receiver to bridge existing exporters into the OTEL pipeline
- Instrument new services with OTEL SDKs — the Collector exports to Prometheus/Mimir

## Correlating the Three Signals

The killer feature of the LGTM stack — jump between metrics, traces, and logs in Grafana:

| Link | How |
|---|---|
| **Metrics → Traces** | **Exemplars**: attach `trace_id` to metric samples. Click a latency spike → jump to the exact trace. Enable `exemplar-storage` on Prometheus |
| **Logs → Traces** | Embed `trace_id` in structured logs (OTEL does this automatically). Click a log line → full trace in Tempo |
| **Traces → Logs** | Click a span in Tempo → see all logs emitted during that span, filtered by `trace_id` in Loki |
| **All → K8s context** | OTEL Collector `k8sattributes` processor enriches all signals with pod, namespace, node, deployment labels |

## Golden Rules

- **Log to stdout, not files.** If the app writes to files, add a streaming sidecar that tails the file and emits to stdout. Never ship logs directly to a backend from application code.

- **Never put high-cardinality values in metric labels.** User IDs, request IDs, URLs with path parameters, commit SHAs — these create millions of time series, crash Prometheus, and spike costs. Put high-cardinality data in traces and logs, not metrics.

- **Sample traces.** 100% trace collection is almost never necessary. Use head-based sampling (1-10%) for routine traffic and tail-based sampling (OTEL Collector `tailsampling` processor) to keep 100% of errors and slow requests.

- **Set retention and downsampling policies.** Full-resolution metrics for 2-4 weeks, 5-minute resolution for 3-6 months, 1-hour resolution for 1+ year. Thanos and VictoriaMetrics support this natively. Without policies, storage costs grow unbounded.

- **Enrich at the collector, not the app.** Let the DaemonSet agent add K8s metadata (pod, namespace, node, labels) automatically via `k8sattributes`. Applications should not emit infrastructure context.

- **Wire correlation from day one.** Exemplars (metrics→traces) and trace_id in logs (logs→traces) are trivial to set up at the start. Retrofitting across dozens of services is a multi-quarter project.
