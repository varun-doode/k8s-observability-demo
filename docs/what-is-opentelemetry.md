# What is OpenTelemetry?

**OpenTelemetry** (often shortened to **OTel**) is an open-source, vendor-neutral
standard and toolkit for generating and collecting telemetry — the metrics,
traces, and logs you need to understand what your software is doing in
production. It's a CNCF project, the same foundation behind Kubernetes.

This explainer sits alongside the other docs in this repo:
[how Prometheus collects metrics](how-prometheus-works.md) and
[getting metrics into Splunk](metrics-to-splunk.md). OpenTelemetry is the
vendor-neutral glue that connects the two.

## The problem it solves

Before OTel, every monitoring vendor shipped its own agent and data format. If
you instrumented your app for one vendor and later wanted to switch, you had to
rip out and rewrite all of that instrumentation — classic vendor lock-in.

OpenTelemetry fixes this: **instrument your code once, in a standard format, then
send that data anywhere.** You change backends by editing config, not code.

## The three signals

OTel handles all three pillars of observability in one framework:

| Signal | Answers | Example |
|--------|---------|---------|
| **Metrics** | "How much / how many?" | request rate, latency, memory usage |
| **Traces** | "Where did the time go?" | one request across five services |
| **Logs** | "What happened at this instant?" | "payment failed for order 123" |

The standout capability is **distributed tracing** — following a single request
end-to-end across many services to see exactly which step was slow or failed.

## How it works

```
┌─────────────┐  1. instrument   ┌──────────────┐  3. export   ┌──────────────┐
│ Your app    │──with OTel SDK──▶│ OTel          │─────────────▶│ Backend(s)   │
│ (any lang)  │  emits signals   │ Collector     │  translate   │ Prometheus / │
└─────────────┘                  │ receive →     │              │ Splunk /     │
                                 │ process →     │              │ Grafana /    │
                                 │ export        │              │ Datadog ...  │
                                 └──────────────┘              └──────────────┘
```

### 1. Instrument

Add the OTel SDK (available for Python, Java, Go, JavaScript, .NET, and more) to
your app so it emits metrics, traces, and logs. Much of this is **automatic** —
OTel's auto-instrumentation hooks common libraries (HTTP servers, database
clients, gRPC) so you get useful telemetry with very little code.

A minimal manual example in Python:

```python
from opentelemetry import trace

tracer = trace.get_tracer("checkout-service")

with tracer.start_as_current_span("process_payment"):
    charge_card()          # this work is timed and traced automatically
```

### 2. Collect

The **OpenTelemetry Collector** is a standalone agent that:

- **Receives** telemetry from your apps (or scrapes existing sources like
  Prometheus endpoints)
- **Processes** it — batching, filtering, adding resource metadata
- **Exports** it to one or more backends

Its config is three matching sections — receivers, processors, exporters — wired
together into pipelines:

```yaml
receivers:
  otlp:                     # receive OTel-native data from apps
    protocols:
      grpc:
  prometheus:               # or scrape Prometheus /metrics endpoints
    config:
      scrape_configs:
        - job_name: "apps"
          static_configs:
            - targets: ["sample-app:8080"]

processors:
  batch: {}

exporters:
  prometheusremotewrite:    # send metrics to Prometheus...
    endpoint: "http://prometheus:9090/api/v1/write"
  splunk_hec:               # ...and/or to Splunk at the same time
    token: "${SPLUNK_HEC_TOKEN}"
    endpoint: "https://splunk:8088/services/collector"

service:
  pipelines:
    metrics:
      receivers: [otlp, prometheus]
      processors: [batch]
      exporters: [prometheusremotewrite, splunk_hec]
```

Note the same metrics stream can fan out to **multiple** backends at once — a big
reason teams put the Collector in the middle.

### 3. Export

The Collector ships data to whatever backend you choose. Swapping Splunk for
Datadog (or adding a second destination) is an exporter change, not an app
change.

## OTLP: the wire format

Signals travel in **OTLP** (OpenTelemetry Protocol) — the standard format apps
use to talk to the Collector, and Collectors use to talk to each other. It's what
makes "instrument once, export anywhere" actually work.

## A concrete example: reading a trace

A user clicks "checkout." The request touches `web → cart → payment → database`.
A trace shows the timing as a waterfall:

```
checkout request ───────────────────────────── 850ms total
├─ web              ▏ 20ms
├─ cart-service     ▏▏ 45ms
├─ payment-service  ▏▏▏▏▏▏▏▏▏▏▏▏▏▏ 720ms          ← slow
│   └─ external API ▏▏▏▏▏▏▏▏▏▏▏▏▏ 680ms           ← the real culprit
└─ database         ▏ 15ms
```

Without tracing you'd only know "checkout is slow." With it, you see the payment
service's external API call is the bottleneck — in seconds.

## How this maps to this repo

In [`manifests/splunk/otel-collector-config.yaml`](../manifests/splunk/otel-collector-config.yaml)
this repo uses the Collector's **Prometheus receiver** to scrape the sample app's
`/metrics` endpoint and the **`splunk_hec` exporter** to forward those metrics to
Splunk. That's OpenTelemetry acting purely as the bridge between Prometheus-style
metrics and a Splunk backend — the collect-and-export role from step 2 above.

## Why it matters

- It's become the **industry standard** for observability instrumentation.
- It's **vendor-neutral** — the glue between your apps and Prometheus, Grafana,
  Splunk, Datadog, and others.
- Knowing OTel signals you understand *modern* observability rather than a single
  vendor's product — a core SRE skill.

## In one sentence

OpenTelemetry is a vendor-neutral standard for generating and collecting metrics,
traces, and logs from your apps, so you can send that data to any observability
backend without rewriting your instrumentation.
