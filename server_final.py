from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json
from urllib.parse import urlparse, parse_qs


API_KEY = "mysecret123"  # Enkel API-nøkkel for autentisering (ikke sikker i produksjon)


# -------------------------------
# Database-oppsett
# -------------------------------

# Koble til SQLite database
# check_same_thread=False gjør at vi kan bruke samme connection i flere requests
conn = sqlite3.connect("server.db", check_same_thread=False)
cursor = conn.cursor()

# Aktiver foreign key constraints (viktig!)
conn.execute("PRAGMA foreign_keys = ON")

# Opprett brukertabell
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unik bruker-ID
    username VARCHAR(25) UNIQUE NOT NULL,   -- Brukernavn (må være unikt)
    password VARCHAR(255) NOT NULL          -- Passord (lagres i klartekst her - IKKE trygt)
);
""")

# Opprett notat-tabell
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                         -- Unik note-ID
    user_id INTEGER NOT NULL,                                     -- Kobling til bruker
    notename VARCHAR(25) NOT NULL,                                -- Tittel på notat
    contents TEXT,                                                -- Innhold (tekst eller JSON)
    type TEXT CHECK(type IN ('note', 'todo')) not null,           -- Type: vanlig notat eller todo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- Når opprettet
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- Sist oppdatert

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- Slett noter hvis bruker slettes
);
""")

# Legg inn testbruker hvis den ikke finnes
try:
    cursor.execute("""INSERT INTO users (username, password) VALUES(?, ?)""", ("test", "pass"))
except Exception as e:
    print(e)  # feiler hvis brukeren allerede finnes

conn.commit()


# -------------------------------
# HTTP Handler
# -------------------------------
class Handler(BaseHTTPRequestHandler):
    """
    Denne klassen håndterer alle HTTP-requests (GET og POST).
    """

    def is_authorized(self):
        """
        Enkel sjekk av API-nøkkel i header.
        """
        return self.headers.get("X-API-Key") == API_KEY

    def do_GET(self):
        """
        Håndterer GET requests.
        """
        if not self.is_authorized():
            self.send_response(403)
            self.end_headers()
            return

        parsed = urlparse(self.path)

        # -------------------------------
        # Hent alle notater
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

            # Send JSON tilbake til klient
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """
        Håndterer POST requests (oppretting, oppdatering, sletting).
        """
        if not self.is_authorized():
            self.send_response(403)
            self.end_headers()
            return

        parsed = urlparse(self.path)

        # Les body (gjelder nesten alle POST requests)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # -------------------------------
        # Lag nytt notat
        # -------------------------------
        if parsed.path == "/make-note":
            try:
                title = json.loads(body)
                print("Ny note:", title)

                cursor.execute(
                    """INSERT INTO notes (user_id, notename, contents, type) VALUES(?, ?, ?, ?)""",
                    (1, title, "", "note")
                )

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        # -------------------------------
        # Lag ny todo-liste
        # -------------------------------
        elif parsed.path == "/make-todo":
            try:
                title = json.loads(body)
                print("Ny todo:", title)

                cursor.execute(
                    """INSERT INTO notes (user_id, notename, contents, type) VALUES(?, ?, ?, ?)""",
                    (1, title, "", "todo")
                )

                conn.commit()
                response = {"status": "ok"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        # -------------------------------
        # Legg til todo-element
        # -------------------------------
        elif parsed.path == "/add-todo":
            try:
                info = json.loads(body)

                list_name = info[0]
                title = info[1]
                complete = info[2]

                # Hent eksisterende liste
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

                # Lagre tilbake som JSON
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
        # Oppdater noter
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
        # Oppdater checkbox
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
                        response = {"status": "error", "message": "Index feil"}
                else:
                    response = {"status": "error", "message": "Fant ikke note"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

        # -------------------------------
        # Slett note
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
            response = {"status": "error", "message": "Ukjent endpoint"}

        # Send svar tilbake
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


# -------------------------------
# Start server
# -------------------------------
server = HTTPServer(("0.0.0.0", 8000), Handler)

print("Server kjører på http://localhost:8000")

# Starter en blocking loop som håndterer requests én etter én
server.serve_forever()