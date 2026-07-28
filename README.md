# k8s-observability-demo

An end-to-end observability stack on Kubernetes: a sample app instrumented with metrics, scraped by **Prometheus**, and visualized in **Grafana**. Designed to run locally on `kind` or `minikube` in a few minutes.

## What's inside

```
.
├── app/                  # Sample instrumented service (exposes /metrics)
├── manifests/
│   ├── prometheus/       # Prometheus scrape config
│   ├── grafana/          # Grafana deployment + preloaded dashboard
│   ├── app/              # Sample app Deployment + Service
│   └── splunk/           # OTel Collector config (Prometheus → Splunk)
├── docs/                 # Explainers (Prometheus, Splunk integration)
└── Makefile              # One-command setup / teardown
```

## Repository contents

| Path | What it provides |
|------|------------------|
| `docs/how-prometheus-works.md` | Explainer: the pull-vs-push model, the `/metrics` format, the four metric types, instrumentation, Kubernetes service discovery, and PromQL / the RED method. |
| `docs/metrics-to-splunk.md` | Four ways to get metrics into Splunk — OpenTelemetry Collector, Prometheus `remote_write`, HEC direct, and the Splunk Helm chart — plus `mstats` querying. |
| `app/app.py` + `app/requirements.txt` | A working instrumented Python service that exposes `/metrics` with request counters and a latency histogram. |
| `manifests/prometheus/` | A Prometheus scrape config that discovers pods via `prometheus.io/scrape` annotations. |
| `manifests/app/` | The sample-app `Deployment` + `Service`, annotated for scraping. |
| `manifests/splunk/` | An OpenTelemetry Collector `ConfigMap` that scrapes Prometheus and exports to Splunk HEC. |
| `Makefile` | One-command deploy / port-forward / teardown helpers. |

## Quick start

```bash
# 1. Spin up a local cluster (kind)
kind create cluster --name obs-demo

# 2. Deploy the stack
make deploy

# 3. Port-forward Grafana and open it
make grafana
# → http://localhost:3000  (admin / admin)
```

## What you'll learn

- Instrumenting a service with Prometheus client metrics
- Writing Prometheus scrape configs for Kubernetes service discovery
- Building Grafana dashboards for the RED method (Rate, Errors, Duration)
- Wiring up SLO-oriented alerting rules
- Forwarding metrics to Splunk via the OpenTelemetry Collector

## Documentation

- [How Prometheus collects metrics for observability](docs/how-prometheus-works.md)
  — the pull model, instrumentation, service discovery, and PromQL.
- [Getting metrics into Splunk](docs/metrics-to-splunk.md)
  — OpenTelemetry Collector, `remote_write`, HEC, and the Splunk Helm chart.

## Teardown

```bash
make clean
kind delete cluster --name obs-demo
```

## License

MIT
