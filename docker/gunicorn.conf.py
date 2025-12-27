# Gunicorn configuration file for Dinner Roulette
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Access log format - include timing, status, and request details
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
# Format explanation:
# %(h)s - remote address
# %(l)s - '-'
# %(u)s - user name
# %(t)s - date of the request
# %(r)s - status line (e.g. GET / HTTP/1.1)
# %(s)s - status code
# %(b)s - response length
# %(f)s - referer
# %(a)s - user agent
# %(D)s - request time in microseconds

# Don't capture stdout/stderr - let app logging go through
capture_output = False

# Preload app for better memory efficiency
preload_app = True

# Restart workers after this many requests (helps with memory leaks)
max_requests = 1000
max_requests_jitter = 50