# Contributing

Thanks for your interest in improving this demo! Contributions are welcome.

## Getting started

1. Fork the repo and create a feature branch off `main`.
2. Make your change.
3. Run the local checks below.
4. Open a pull request with a clear description of what and why.

## Local checks

Validate Kubernetes manifests (requires `kubectl`):

```bash
kubectl apply --dry-run=client -f manifests/ -R
```

Check the sample app runs and exposes metrics:

```bash
cd app
pip install -r requirements.txt
python app.py &
curl -s localhost:8080/metrics | head
```

If you have [`yamllint`](https://github.com/adrienverge/yamllint) installed:

```bash
yamllint manifests/
```

## Guidelines

- Keep manifests minimal and runnable on `kind` / `minikube`.
- Document any new component in the README's "Repository contents" table.
- Prefer annotations-based discovery over hardcoded scrape targets.

## Reporting issues

Use the issue templates. For security issues, see [SECURITY.md](SECURITY.md).
