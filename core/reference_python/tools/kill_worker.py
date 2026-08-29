from pathlib import Path
import sqlite3, sys, os, time, json

db = Path(sys.argv[1])
phase = sys.argv[2]

conn = sqlite3.connect(db)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=FULL")
conn.execute("CREATE TABLE IF NOT EXISTS killtest(id INTEGER PRIMARY KEY, value TEXT)")
conn.commit()

if phase == "before_begin":
    os._exit(71)

conn.execute("BEGIN IMMEDIATE")
if phase == "after_begin":
    os._exit(72)

conn.execute("INSERT INTO killtest(value) VALUES ('committed-or-rolled-back')")
if phase == "after_write_before_commit":
    os._exit(73)

conn.commit()
if phase == "after_commit":
    os._exit(74)

conn.close()
sys.exit(0)
