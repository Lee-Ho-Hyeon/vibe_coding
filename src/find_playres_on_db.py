import sqlite3
import pandas as pd

conn = sqlite3.connect("football_players.db")

df = pd.read_sql_query("""
SELECT * FROM players
""", conn)

print(df)

conn.close()