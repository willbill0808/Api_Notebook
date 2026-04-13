from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json
from urllib.parse import urlparse, parse_qs


API_KEY = "mysecret123"  # Simple API key for authentication (not secure in production)


# -------------------------------
# Database setup
# -------------------------------

# Connect to SQLite database
# check_same_thread=False allows using the same connection across multiple requests
conn = sqlite3.connect("server.db", check_same_thread=False)
cursor = conn.cursor()

# Enable foreign key constraints (important!)
conn.execute("PRAGMA foreign_keys = ON")

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique user ID
    username VARCHAR(25) UNIQUE NOT NULL,   -- Username (must be unique)
    password VARCHAR(255) NOT NULL          -- Password (stored in plaintext here - NOT secure)
);
""")

# Create notes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                         -- Unique note ID
    user_id INTEGER NOT NULL,                                     -- Link to user
    notename VARCHAR(25) NOT NULL,                                -- Note title
    contents TEXT,                                                -- Content (text or JSON)
    type TEXT CHECK(type IN ('note', 'todo')) not null,           -- Type: note or todo list
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- When created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- Last updated

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- Delete notes if user is deleted
);
""")

conn.commit()


# -------------------------------
# HTTP Handler
# -------------------------------
class Handler(BaseHTTPRequestHandler):
    """
    This class handles all HTTP requests (GET and POST).
    """

    def is_authorized(self):
        """
        Simple API key check in headers.
        """
        return self.headers.get("X-API-Key") == API_KEY

    def do_GET(self):
        """
        Handles GET requests.
        """
        if not self.is_authorized():
            self.send_response(403)
            self.end_headers()
            return

        parsed = urlparse(self.path)

        # -------------------------------
        # Get all notes
        # -------------------------------
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

            # Send JSON back to client
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """
        Handles POST requests (create, update, delete).
        """
        if not self.is_authorized():
            self.send_response(403)
            self.end_headers()
            return

        parsed = urlparse(self.path)

        # Read request body (used in almost all POST requests)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # -------------------------------
        # Create new note
        # -------------------------------
        if parsed.path == "/make-note":
            try:
                title = json.loads(body)[0]
                user_id = json.loads(body)[1]
                print("New note:", title)

                cursor.execute(
                    """INSERT INTO notes (user_id, notename, contents, type) VALUES(?, ?, ?, ?)""",
                    (user_id, title, "", "note")
                )

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}
                print(response)
        
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        # -------------------------------
        # Get all notes (POST version)
        # -------------------------------
        elif parsed.path == "/notes":
            try:
                user_id = json.loads(body)

                cursor.execute("SELECT * FROM notes WHERE user_id = ?", (user_id,))
                rows = cursor.fetchall()

                print(rows)

                response = {
                    "status": "ok",
                    "data": rows
                }
            except Exception as e:
                response = {
                    "status": "error",
                    "message": str(e)
                }
        
        # -------------------------------
        # Get user data (login)
        # -------------------------------
        elif parsed.path == "/login":
            try:
                username = json.loads(body)
                print("username:", username)

                cursor.execute(
                    """SELECT * FROM users WHERE username LIKE ?""",
                    (username,)
                )

                rows = cursor.fetchall()
                print(rows)

                response = {
                    "status": "ok",
                    "data": rows
                }

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        # -------------------------------
        # Create new user
        # -------------------------------
        elif parsed.path == "/create_user":
            try:
                data = json.loads(body)

                cursor.execute(
                    """INSERT INTO users (username, password) VALUES(?, ?)""", 
                    (data[0], data[1])
                )

                response = {
                    "status": "ok",
                }

            except Exception as e:
                response = {"status": "error", "message": str(e)}
        
        # -------------------------------
        # Create new todo list
        # -------------------------------
        elif parsed.path == "/make-todo":
            try:
                title = json.loads(body)[0]
                user_id = json.loads(body)[1]
                print("New todo:", title)

                cursor.execute(
                    """INSERT INTO notes (user_id, notename, contents, type) VALUES(?, ?, ?, ?)""",
                    (user_id, title, "", "todo")
                )

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        # -------------------------------
        # Add todo item
        # -------------------------------
        elif parsed.path == "/add-todo":
            try:
                info = json.loads(body)

                list_name = info[0]
                title = info[1]
                complete = info[2]

                # Fetch existing list
                cursor.execute("SELECT contents FROM notes WHERE notename = ?", (list_name,))
                row = cursor.fetchone()

                new_item = {"title": title, "complete": complete}

                if row and row[0]:
                    try:
                        items = json.loads(row[0])
                    except:
                        items = []
                else:
                    items = []

                items.append(new_item)

                # Save back as JSON
                cursor.execute("""
                    UPDATE notes
                    SET contents = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE notename = ?
                """, (json.dumps(items), list_name))

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        # -------------------------------
        # Update notes
        # -------------------------------
        elif parsed.path == "/update":
            try:
                notes = json.loads(body)

                for note in notes:
                    cursor.execute("""
                        UPDATE notes
                        SET notename = ?, contents = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (note["title"], note["content"], note["id"]))

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        # -------------------------------
        # Update checkbox
        # -------------------------------
        elif parsed.path == "/update-CB":
            try:
                note_id, cb_index, new_state = json.loads(body)

                cursor.execute("SELECT contents FROM notes WHERE id = ?", (note_id,))
                row = cursor.fetchone()

                if row:
                    items = json.loads(row[0]) if row[0] else []

                    if 0 <= cb_index < len(items):
                        items[cb_index]["complete"] = new_state

                        cursor.execute("""
                            UPDATE notes
                            SET contents = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (json.dumps(items), note_id))

                        conn.commit()
                        response = {"status": "ok"}
                    else:
                        response = {"status": "error", "message": "Invalid index"}
                else:
                    response = {"status": "error", "message": "Note not found"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        # -------------------------------
        # Delete note
        # -------------------------------
        elif parsed.path == "/delete-tab":
            try:
                note_id = json.loads(body)

                cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                conn.commit()

                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        else:
            response = {"status": "error", "message": "Unknown endpoint"}

        # Send response back
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


# -------------------------------
# Start server
# -------------------------------
server = HTTPServer(("0.0.0.0", 8000), Handler)

print("Server running at http://localhost:8000")

# Starts a blocking loop that handles requests one at a time
server.serve_forever()