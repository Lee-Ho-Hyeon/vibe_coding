import sqlite3
import pandas as pd


DB_PATH = "football_players.db"
PLAYER_CSV_PATH = "club_Q2609_players.csv"
CLUB_CSV_PATH = "C:\\Users\\LG\\Documents\\GitHub\\vibe_coding\\data\\club_qid_list.csv"


def create_tables(conn):
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players (
        qid TEXT PRIMARY KEY,
        wikidata_name TEXT,
        display_name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS player_countries (
        qid TEXT,
        country TEXT,
        UNIQUE(qid, country),
        FOREIGN KEY(qid) REFERENCES players(qid)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS player_aliases (
        qid TEXT,
        alias TEXT,
        UNIQUE(qid, alias),
        FOREIGN KEY(qid) REFERENCES players(qid)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clubs (
        club_qid TEXT PRIMARY KEY,
        club_name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS player_clubs (
        qid TEXT,
        club_qid TEXT,
        UNIQUE(qid, club_qid),
        FOREIGN KEY(qid) REFERENCES players(qid),
        FOREIGN KEY(club_qid) REFERENCES clubs(club_qid)
    )
    """)

    conn.commit()


def insert_clubs(conn, club_csv_path):
    df = pd.read_csv(club_csv_path, encoding="utf-8-sig")

    cur = conn.cursor()

    for _, row in df.iterrows():
        club_qid = str(row["club_qid"]).strip()
        club_name = str(row["club_name"]).strip()

        cur.execute("""
        INSERT OR REPLACE INTO clubs (club_qid, club_name)
        VALUES (?, ?)
        """, (club_qid, club_name))

    conn.commit()


def insert_players_from_csv(conn, player_csv_path):
    df = pd.read_csv(player_csv_path, encoding="utf-8-sig")

    cur = conn.cursor()

    for _, row in df.iterrows():
        qid = str(row["qid"]).strip()
        wikidata_name = str(row["wikidata_name"]).strip()
        display_name = str(row["display_name"]).strip()
        country = str(row["country"]).strip()
        club_qid = str(row["club_qid"]).strip()

        alias_raw = row.get("alias", "")
        alias_raw = "" if pd.isna(alias_raw) else str(alias_raw)

        cur.execute("""
        INSERT OR REPLACE INTO players (qid, wikidata_name, display_name)
        VALUES (?, ?, ?)
        """, (qid, wikidata_name, display_name))

        if country and country != "정보 없음":
            cur.execute("""
            INSERT OR IGNORE INTO player_countries (qid, country)
            VALUES (?, ?)
            """, (qid, country))

        cur.execute("""
        INSERT OR IGNORE INTO player_clubs (qid, club_qid)
        VALUES (?, ?)
        """, (qid, club_qid))

        aliases = [a.strip() for a in alias_raw.split(",") if a.strip()]

        for alias in aliases:
            cur.execute("""
            INSERT OR IGNORE INTO player_aliases (qid, alias)
            VALUES (?, ?)
            """, (qid, alias))

    conn.commit()


def main():
    conn = sqlite3.connect(DB_PATH)

    create_tables(conn)
    insert_clubs(conn, CLUB_CSV_PATH)
    insert_players_from_csv(conn, PLAYER_CSV_PATH)

    conn.close()

    print("DB 저장 완료:", DB_PATH)


if __name__ == "__main__":
    main()