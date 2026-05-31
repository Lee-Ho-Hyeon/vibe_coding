import sqlite3
import pandas as pd
from pathlib import Path
import re


DB_PATH = "football_players.db"

BASE_DIR = Path(r"C:\Users\LG\Documents\GitHub\vibe_coding")
DATA_DIR = BASE_DIR / "data"

CLUB_CSV_PATH = DATA_DIR / "club_qid_list.csv"


def has_korean(text):
    if pd.isna(text):
        return False
    return bool(re.search(r"[가-힣]", str(text)))


def create_tables(conn):
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players (
        qid TEXT PRIMARY KEY,
        wikidata_name TEXT,
        display_name TEXT,
        has_korean_name INTEGER DEFAULT 0
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

        aliases = [a.strip() for a in alias_raw.split("|") if a.strip()]

        korean_flag = (
            has_korean(wikidata_name)
            or has_korean(display_name)
            or any(has_korean(alias) for alias in aliases)
        )

        cur.execute("""
        INSERT OR REPLACE INTO players
        (qid, wikidata_name, display_name, has_korean_name)
        VALUES (?, ?, ?, ?)
        """, (qid, wikidata_name, display_name, 1 if korean_flag else 0))

        if country and country != "정보 없음":
            cur.execute("""
            INSERT OR IGNORE INTO player_countries (qid, country)
            VALUES (?, ?)
            """, (qid, country))

        cur.execute("""
        INSERT OR IGNORE INTO player_clubs (qid, club_qid)
        VALUES (?, ?)
        """, (qid, club_qid))

        for alias in aliases:
            cur.execute("""
            INSERT OR IGNORE INTO player_aliases (qid, alias)
            VALUES (?, ?)
            """, (qid, alias))

    conn.commit()


def insert_all_club_player_csvs(conn):
    club_df = pd.read_csv(CLUB_CSV_PATH, encoding="utf-8-sig")

    for _, row in club_df.iterrows():
        club_qid = str(row["club_qid"]).strip()
        player_csv_path = DATA_DIR / f"club_{club_qid}_players.csv"

        if not player_csv_path.exists():
            print(f"파일 없음, 건너뜀: {player_csv_path}")
            continue

        print(f"DB 저장 중: {player_csv_path.name}")
        insert_players_from_csv(conn, player_csv_path)


def main():
    conn = sqlite3.connect(DB_PATH)

    create_tables(conn)
    insert_clubs(conn, CLUB_CSV_PATH)
    insert_all_club_player_csvs(conn)

    conn.close()

    print("DB 저장 완료:", DB_PATH)


if __name__ == "__main__":
    main()