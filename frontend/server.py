#!/usr/bin/env python3
"""
Simple HTTP server for the AI Dubbing Studio frontend
Serves static files from the frontend directory

Usage:
    python server.py [port]

Default port: 3000
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers"""

    def end_headers(self) -> None:
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self) -> None:
        """Handle preflight OPTIONS requests"""
        self.send_response(200)
        self.end_headers()


def run_server(port: int = 3000) -> None:
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║  AI Dubbing Studio - Frontend Server                    ║
╚══════════════════════════════════════════════════════════╝

Server running at:
  → http://localhost:{port}

Press Ctrl+C to stop the server
""")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.server_close()


if __name__ == '__main__':
    # Get port from command line argument or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

    # Change to frontend directory
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)

    run_server(port)
