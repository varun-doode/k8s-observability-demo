"""
Sample instrumented service.

Exposes Prometheus metrics on /metrics and a couple of demo endpoints that
generate traffic. Run locally:

    pip install -r requirements.txt
    python app.py
    # then: curl localhost:8080/  and  curl localhost:8080/metrics
"""
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# --- Metric definitions -----------------------------------------------------
REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["path"],
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        start = time.perf_counter()

        if self.path == "/metrics":
            body = generate_latest()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(body)
            return

        # Simulate some work + occasional errors for realistic metrics
        time.sleep(random.uniform(0.01, 0.2))
        status = 500 if random.random() < 0.05 else 200

        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok\n" if status == 200 else b"error\n")

        LATENCY.labels(path=self.path).observe(time.perf_counter() - start)
        REQUESTS.labels(method="GET", path=self.path, status=str(status)).inc()

    def log_message(self, *args):
        pass  # quiet default logging


if __name__ == "__main__":
    print("Listening on :8080  (/ and /metrics)")
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
