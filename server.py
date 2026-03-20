import sqlite3

server = sqlite3.connect('server.db')
server.execute("PRAGMA foreign_keys = ON")

server.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(25) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
""")

server.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    notename VARCHAR(25),
    contents TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

server.execute("""INSERT INTO users (username, password) VALUES(?, ?)""", ("test", "pass"))

server.execute("""INSERT INTO notes (user_id, notename, contents) VALUES(?, ?, ?)""", ("1", "note1", "hei, content"))
server.execute("""INSERT INTO notes (user_id, notename, contents) VALUES(?, ?, ?)""", ("1", "note2", "hei2, content2"))
server.execute("""INSERT INTO notes (user_id, notename, contents) VALUES(?, ?, ?)""", ("1", "note3", "hei3, content3"))

server.commit()