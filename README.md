# k8s-observability-demo

An end-to-end observability stack on Kubernetes: a sample app instrumented with metrics, scraped by **Prometheus**, and visualized in **Grafana**. Designed to run locally on `kind` or `minikube` in a few minutes.

## What's inside

```
.
├── app/                  # Sample instrumented service (exposes /metrics)
├── manifests/
│   ├── prometheus/       # Prometheus deployment + scrape config
│   ├── grafana/          # Grafana deployment + preloaded dashboard
│   └── app/              # Sample app Deployment + Service
└── Makefile              # One-command setup / teardown
```

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

## Teardown

```bash
make clean
kind delete cluster --name obs-demo
```

## License

MIT
