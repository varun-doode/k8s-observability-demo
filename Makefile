.PHONY: deploy grafana prometheus clean

deploy:
	kubectl apply -f manifests/app/
	kubectl apply -f manifests/prometheus/
	kubectl apply -f manifests/grafana/
	@echo "Stack deployed. Run 'make grafana' to open the dashboard."

grafana:
	@echo "Grafana → http://localhost:3000 (admin/admin)"
	kubectl port-forward svc/grafana 3000:3000

prometheus:
	@echo "Prometheus → http://localhost:9090"
	kubectl port-forward svc/prometheus 9090:9090

clean:
	kubectl delete -f manifests/grafana/ --ignore-not-found
	kubectl delete -f manifests/prometheus/ --ignore-not-found
	kubectl delete -f manifests/app/ --ignore-not-found
