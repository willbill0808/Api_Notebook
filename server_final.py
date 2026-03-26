from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json
from urllib.parse import urlparse, parse_qs


API_KEY = "mysecret123"


# -------------------------------
# Database setup
# -------------------------------

# Connect to SQLite database (thread-safe access)
conn = sqlite3.connect("server.db", check_same_thread=False)
cursor = conn.cursor()

# Enable foreign key constraints
conn.execute("PRAGMA foreign_keys = ON")

# Create "users" table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique user ID
    username VARCHAR(25) UNIQUE NOT NULL,   -- Username must be unique
    password VARCHAR(255) NOT NULL          -- Password storage (plain text here; consider hashing in production)
);
""")

# Create "notes" table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                         -- Unique note ID
    user_id INTEGER NOT NULL,                                     -- Foreign key to users table
    notename VARCHAR(25) NOT NULL,                                -- Note title
    contents TEXT,                                                -- Note contents,
    type TEXT CHECK(type IN ('note', 'todo')) not null,           -- Either note or todo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- Creation timestamp
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- Last updated timestamp

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- Ensure notes are deleted if user is deleted
);
""")

# Insert a default user for testing (only if this DB is new)
try:
    cursor.execute("""INSERT INTO users (username, password) VALUES(?, ?)""", ("test", "pass"))
except Exception as e:
    print(e)
    

# Commit database changes
conn.commit()


# -------------------------------
# HTTP Server Handler
# -------------------------------
class Handler(BaseHTTPRequestHandler):
    """
    Handles HTTP GET and POST requests for the notes app.
    """
    

    def is_authorized(self):
        return self.headers.get("X-API-Key") == API_KEY

    def do_GET(self):
        if not self.is_authorized():
            self.send_response(403)
            self.end_headers()
            return
        """
        Handles GET requests.
        Currently supports:
        - /notes : Returns a list of all notes.
        """
        parsed = urlparse(self.path)

        if parsed.path == "/notes" and self.command == "GET":
            try:
                # Fetch all notes from the database
                cursor.execute("SELECT * FROM notes")
                rows = cursor.fetchall()

                response = {
                    "status": "ok",
                    "data": rows
                }
            except Exception as e:
                # Handle database errors
                response = {
                    "status": "error",
                    "message": str(e)
                }

            # Send JSON response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        if not self.is_authorized():
            self.send_response(403)
            self.end_headers()
            return
        """
        Handles POST requests.
        Currently supports:
        - /make-note : Create a new note
        - /update    : Update existing notes
        """
        parsed = urlparse(self.path)

        # -------------------------------
        # Create a new note
        # -------------------------------
        if parsed.path == "/make-note":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                # Expect a JSON string with the note title
                title = json.loads(body)
                print("New tab name received:", title)

                # Insert new note for user_id=1 with empty content
                cursor.execute(
                    """INSERT INTO notes (user_id, notename, contents, type) VALUES(?, ?, ?, ?)""",
                    (1, title, "", "note")
                )

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                # Handle insertion errors (e.g., foreign key issues)
                response = {"status": "error", "message": str(e)}

            # Send JSON response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        # -------------------------------
        # Create a new To-do list
        # -------------------------------
        if parsed.path == "/make-todo":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                # Expect a JSON string with the note title
                title = json.loads(body)
                print("New tab name received:", title)

                # Insert new note for user_id=1 with empty content
                cursor.execute(
                    """INSERT INTO notes (user_id, notename, contents, type) VALUES(?, ?, ?, ?)""",
                    (1, title, "", "todo")
                )

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                # Handle insertion errors (e.g., foreign key issues)
                response = {"status": "error", "message": str(e)}

            # Send JSON response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        # -------------------------------
        # Create a new To-do element
        # -------------------------------
        if parsed.path == "/add-todo":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                # Expect a JSON string with the note info
                info_checkbox = json.loads(body)
                print("New checkbox info received:", info_checkbox)

                list_name = info_checkbox[0]
                title = info_checkbox[1]
                complete = info_checkbox[2]

                # Read current contents from DB
                cursor.execute("SELECT contents FROM notes WHERE notename = ?", (list_name,))
                rows = cursor.fetchall()
                print(rows)

                # Build the new item
                new_item = {"title": title, "complete": complete}

                if rows:
                    # If there is existing content, parse it
                    try:
                        current_items = json.loads(rows[0][0])
                    except:
                        current_items = []
                    # Append new item
                    current_items.append(new_item)
                else:
                    current_items = [new_item]

                # Save back to DB as JSON string
                cursor.execute("""
                    UPDATE notes
                    SET contents = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE notename = ?
                """, (json.dumps(current_items), list_name))

                conn.commit()


                # Insert new note for user_id=1 with empty content
                #cursor.execute(
                #    """INSERT INTO notes (user_id, notename, contents, type) VALUES(?, ?, ?, ?)""",
                #    (1, title, "", "todo")
                #)

                #conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                # Handle insertion errors (e.g., foreign key issues)
                response = {"status": "error", "message": str(e)}

            # Send JSON response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        # -------------------------------
        # Update existing notes
        # -------------------------------
        if parsed.path == "/update":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                # Expect a JSON list of notes with id, title, and content
                notes = json.loads(body)
                print("Notes received:", notes)

                # Update each note in the database
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

                conn.commit()  # Save all updates
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

            # Send JSON response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        # -------------------------------
        # sletter tab
        # -------------------------------
        if parsed.path == "/delete-tab":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                note_id = json.loads(body)
                print(note_id)
                
                if note_id is not None:
                    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                    conn.commit()
                    response = {"status": "ok"}
                else:
                    response = {"status": "error", "message": "No note id provided"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

            # Send JSON response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())


# -------------------------------
# Start the server
# -------------------------------
server = HTTPServer(("0.0.0.0", 8000), Handler)
print("Server running at http://localhost:8000")
server.serve_forever()