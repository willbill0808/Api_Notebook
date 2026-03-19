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

server.commit()