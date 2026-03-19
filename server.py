import sqlite3

conn = sqlite3.connect('example.db')

conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
conn.commit()

print(conn.execute("SELECT * FROM users "))