import os

bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 100
max_requests_jitter = 10