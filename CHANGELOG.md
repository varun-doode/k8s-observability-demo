# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-07-28

### Added
- Instrumented Python sample app exposing Prometheus metrics.
- Prometheus deployment with annotation-based service discovery + RBAC.
- Grafana deployment with a preconfigured Prometheus datasource.
- OpenTelemetry Collector config for exporting metrics to Splunk.
- Docs: how Prometheus collects metrics, and getting metrics into Splunk.
- CI workflow: Python compile check + YAML lint.
