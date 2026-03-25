from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json
from urllib.parse import urlparse, parse_qs

conn = sqlite3.connect("server.db", check_same_thread=False)
cursor = conn.cursor()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/notes":
            try:
                cursor.execute("SELECT * FROM notes")
                rows = cursor.fetchall()

                response = {
                    "status": "ok",
                    "data": rows
                }
            except Exception as e:
                response = {
                    "status": "error",
                    "message": str(e)
                }
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())


server = HTTPServer(("0.0.0.0", 8000), Handler)
print("Server running at http://localhost:8000")
server.serve_forever()