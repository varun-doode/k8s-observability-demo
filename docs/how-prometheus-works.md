# How Prometheus collects metrics for observability

This is a practical explainer of *how* Prometheus gets metrics out of your
applications and infrastructure, and *why* that model is well suited to
observability.

## The core idea: pull, not push

Most monitoring systems make your app **push** metrics to a server. Prometheus
does the opposite — it **pulls** (scrapes). You expose your metrics on an HTTP
endpoint (by convention `/metrics`), and Prometheus periodically fetches that
endpoint on a schedule you configure (the *scrape interval*, e.g. every 15s).

```
                 scrape every 15s
Prometheus  ───────────────────────▶  http://your-app:8080/metrics
   │                                        (plain-text metrics)
   │  stores samples in its
   ▼  time-series database (TSDB)
 [ query with PromQL ]  ◀──────────  Grafana / Alertmanager
```

Why pull is nice in practice:
- **Service discovery does the wiring.** In Kubernetes, Prometheus discovers
  pods/services automatically — you don't hardcode targets.
- **Health for free.** If a scrape fails, Prometheus records the target as
  `up == 0`, which is itself a useful signal.
- **No app-side buffering.** Your app just exposes current values; Prometheus
  owns collection and retention.

## What a `/metrics` endpoint looks like

Metrics are plain text, one series per line. Example:

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/",status="200"} 1027
http_requests_total{method="GET",path="/health",status="200"} 8342

# HELP http_request_duration_seconds Request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 24054
http_request_duration_seconds_bucket{le="0.5"} 33444
http_request_duration_seconds_bucket{le="+Inf"} 33499
```

The `{key="value"}` parts are **labels** — dimensions you can filter and group
by in queries (by method, path, status, pod, etc.).

## The four metric types

| Type | What it's for | Example |
|------|---------------|---------|
| **Counter** | Only goes up (reset on restart) | total requests, total errors |
| **Gauge** | Goes up and down | memory in use, queue depth, temperature |
| **Histogram** | Distribution via buckets | request latency, response sizes |
| **Summary** | Client-side quantiles | similar to histogram, computed in-app |

## Getting metrics *out of an app*: instrumentation

Your app needs a Prometheus client library to expose `/metrics`. Every major
language has one. A minimal Python example (also in [`app/`](../app)):

```python
from prometheus_client import Counter, start_http_server
import time

REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["path"])

start_http_server(8080)          # serves /metrics on :8080
while True:
    REQUESTS.labels(path="/").inc()
    time.sleep(1)
```

For things you can't instrument (databases, nodes, the OS), you run an
**exporter** — a small sidecar that translates a system's stats into the
Prometheus format (e.g. `node_exporter`, `kube-state-metrics`,
`postgres_exporter`).

## How Prometheus finds targets in Kubernetes

You annotate pods/services, and Prometheus's `kubernetes_sd_config` discovers
them. The common convention:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

See [`manifests/prometheus/prometheus-config.yaml`](../manifests/prometheus/prometheus-config.yaml)
for a working scrape config that honors these annotations.

## Querying with PromQL

Once data is in the TSDB, you ask questions with PromQL. A few that map to the
**RED method** (Rate, Errors, Duration) — the go-to trio for request-driven
services:

```promql
# Rate: requests per second over the last 5 minutes
rate(http_requests_total[5m])

# Errors: fraction of requests that are 5xx
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# Duration: 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## From metrics to observability

Metrics are one of the three pillars (metrics, logs, traces). Prometheus owns
the **metrics** pillar and feeds:

- **Grafana** — dashboards (see [`manifests/grafana/`](../manifests/grafana))
- **Alertmanager** — alerting on SLO breaches (e.g. error rate > 1% for 5m)

For **logs**, teams often pair Prometheus with Loki or ship logs to Splunk —
which is covered in [`docs/metrics-to-splunk.md`](metrics-to-splunk.md).
