import sqlite3

conn = sqlite3.connect("prices.db")
cur = conn.cursor()

cur.execute("""
    ALTER TABLE prices
    ADD COLUMN category TEXT
""")

conn.commit()
conn.close()

print("➕ Category column added")

