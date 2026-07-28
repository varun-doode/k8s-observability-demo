# Getting metrics into Splunk

Prometheus is great at scraping and short-term storage, but many organizations
standardize on **Splunk** for long-term retention, cross-signal correlation
(metrics + logs + traces in one place), and enterprise dashboards/alerting.

This doc covers the main ways to get your metrics into Splunk. Pick the one that
matches your setup.

---

## The two Splunk destinations

Splunk can ingest metrics into two different places — know which you're targeting:

1. **Splunk metrics index** (Splunk Enterprise / Cloud) — a purpose-built
   metric store queried with `mstats`. Most efficient for numeric time series.
2. **Splunk Observability Cloud** (formerly SignalFx) — a dedicated
   observability product with native Prometheus/OpenTelemetry ingestion.

---

## Option 1 (recommended): OpenTelemetry Collector

The cleanest, most future-proof path. The **OpenTelemetry (OTel) Collector**
scrapes Prometheus endpoints (or receives remote-write) and exports to Splunk.
Splunk ships and supports its own distro: the **Splunk Distribution of the
OpenTelemetry Collector**.

Flow:

```
your app /metrics ──▶ OTel Collector (prometheus receiver)
                          │  splunk_hec exporter
                          ▼
                   Splunk (HEC endpoint / metrics index)
```

Minimal collector config ([`manifests/splunk/otel-collector-config.yaml`](../manifests/splunk/otel-collector-config.yaml)):

```yaml
receivers:
  prometheus:
    config:
      scrape_configs:
        - job_name: "k8s-apps"
          scrape_interval: 15s
          static_configs:
            - targets: ["sample-app.default.svc:8080"]

exporters:
  splunk_hec:
    token: "${SPLUNK_HEC_TOKEN}"
    endpoint: "https://<your-splunk-host>:8088/services/collector"
    index: "metrics_index"
    source: "otel"
    sourcetype: "prometheus"

service:
  pipelines:
    metrics:
      receivers: [prometheus]
      exporters: [splunk_hec]
```

Why this is the preferred option:
- One collector handles metrics **and** logs **and** traces.
- Vendor-neutral config — swap `splunk_hec` for another exporter later.
- Actively maintained by both Splunk and the OTel community.

---

## Option 2: Prometheus `remote_write` → OTel → Splunk

If you already run Prometheus and don't want the collector to scrape directly,
have Prometheus **remote-write** to the OTel Collector's `prometheusremotewrite`
receiver, which then exports to Splunk.

In `prometheus.yml`:

```yaml
remote_write:
  - url: "http://otel-collector:9411/api/v1/prometheus"
```

Use this when Prometheus stays your primary collector and Splunk is a
downstream/long-term sink.

---

## Option 3: HTTP Event Collector (HEC) directly

For quick tests or simple setups, you can POST metrics straight to Splunk's
**HTTP Event Collector**. Splunk expects a specific metric JSON shape:

```bash
curl -k https://<splunk-host>:8088/services/collector \
  -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" \
  -d '{
        "time": 1706400000,
        "event": "metric",
        "source": "sample-app",
        "sourcetype": "prometheus",
        "index": "metrics_index",
        "fields": {
          "metric_name:http_requests_total": 1027,
          "path": "/",
          "status": "200"
        }
      }'
```

Note the `metric_name:<name>` convention inside `fields` — that's how Splunk
recognizes a numeric metric vs a log event. Good for a proof of concept; use an
exporter/collector for anything production.

---

## Option 4: Splunk Connect for Kubernetes / OTel Helm chart

For a whole cluster, don't wire this per-app. Deploy Splunk's Helm chart
(`splunk-otel-collector-chart`) as a DaemonSet + Deployment; it auto-discovers
pods, scrapes Prometheus annotations, and ships metrics + logs to Splunk.

```bash
helm repo add splunk-otel-collector-chart \
  https://signalfx.github.io/splunk-otel-collector-chart
helm install splunk-otel splunk-otel-collector-chart/splunk-otel-collector \
  --set="splunkPlatform.endpoint=https://<host>:8088/services/collector" \
  --set="splunkPlatform.token=<HEC_TOKEN>" \
  --set="splunkPlatform.metricsIndex=metrics_index"
```

---

## Querying metrics in Splunk

Once metrics land in a metrics index, query with `mstats`:

```spl
| mstats avg(_value) prestats=true
    WHERE index=metrics_index AND metric_name="http_requests_total"
    BY path span=1m
| timechart avg(_value) BY path
```

---

## Which should you use?

| Situation | Recommended path |
|-----------|------------------|
| Greenfield, want one tool for everything | **Option 1** (OTel Collector) |
| Already run Prometheus, add Splunk as sink | **Option 2** (remote_write) |
| Quick demo / PoC | **Option 3** (HEC direct) |
| Whole cluster, minimal wiring | **Option 4** (Helm chart) |

For most teams doing this today, **OpenTelemetry Collector (Option 1 or 4) is
the standard** — it's where both the vendor and the community are investing.
