#!/usr/bin/env python3
"""Static file server for local testing that disables browser caching.

Usage: uv run --no-project python dev_server.py [port]
"""
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Serving on http://localhost:{port} (no-cache)")
    ThreadingHTTPServer(("", port), NoCacheHandler).serve_forever()
