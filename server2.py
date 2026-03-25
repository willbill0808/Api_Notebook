from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json
from urllib.parse import urlparse, parse_qs

conn = sqlite3.connect("server.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(25) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    notename VARCHAR(25) NOT NULL,
    contents TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/notes" and self.command == "GET":
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

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/make-note":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                title = json.loads(body)
                print("New tab name received:", title)
                
                cursor.execute(
                    """INSERT INTO notes (user_id, notename, contents) VALUES(?, ?, ?)""",
                    (1, title, "")  # user_id=1, contents empty string
                )

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())


        if parsed.path == "/update":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                # Expecting a list of notes: [{"id":..., "title":..., "content":...}, ...]
                notes = json.loads(body)
                print("Notes received:", notes)

                for note in notes:
                    note_id = note.get("id")
                    title = note.get("title")
                    content = note.get("content")

                    if note_id is not None:
                        cursor.execute("""
                            UPDATE notes
                            SET notename = ?, contents = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (title, content, note_id))

                conn.commit()  # Save all changes
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())


server = HTTPServer(("0.0.0.0", 8000), Handler)
print("Server running at http://localhost:8000")
server.serve_forever()