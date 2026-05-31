from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "football_players.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def home():
    return {"message": "Football player search API is running"}


@app.get("/search/player")
def search_player(q: str = Query(..., description="검색할 선수 이름 또는 별칭")):
    conn = get_db_connection()
    cur = conn.cursor()

    keyword = f"%{q}%"

    cur.execute("""
        SELECT DISTINCT
            p.qid,
            p.display_name,
            p.wikidata_name
        FROM players p
        LEFT JOIN player_aliases pa
        ON p.qid = pa.qid
        WHERE p.has_korean_name = 1
          AND (
              p.display_name LIKE ?
              OR p.wikidata_name LIKE ?
              OR pa.alias LIKE ?
          )
        ORDER BY p.display_name
    """, (keyword, keyword, keyword))

    rows = cur.fetchall()
    conn.close()

    results = []

    for row in rows:
        results.append({
            "qid": row["qid"],
            "display_name": row["display_name"],
            "wikidata_name": row["wikidata_name"]
        })

    return results

@app.get("/players/{qid}")
def get_player_detail(qid: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT qid, display_name, wikidata_name
        FROM players
        WHERE qid = ?
          AND has_korean_name = 1
    """, (qid,))

    player = cur.fetchone()

    if player is None:
        conn.close()
        return {"error": "선수를 찾을 수 없습니다."}

    cur.execute("""
        SELECT DISTINCT country
        FROM player_countries
        WHERE qid = ?
        ORDER BY country
    """, (qid,))

    countries = [row["country"] for row in cur.fetchall()]

    cur.execute("""
        SELECT DISTINCT c.club_qid, c.club_name
        FROM player_clubs pc
        JOIN clubs c
        ON pc.club_qid = c.club_qid
        WHERE pc.qid = ?
        ORDER BY c.club_name
    """, (qid,))

    clubs = [
        {
            "club_qid": row["club_qid"],
            "club_name": row["club_name"]
        }
        for row in cur.fetchall()
    ]

    conn.close()

    return {
        "qid": player["qid"],
        "display_name": player["display_name"],
        "wikidata_name": player["wikidata_name"],
        "countries": countries,
        "clubs": clubs
    }

@app.get("/search/club")
def search_club(q: str):
    conn = get_db_connection()
    cur = conn.cursor()

    keyword = f"%{q}%"

    cur.execute("""
        SELECT club_qid, club_name
        FROM clubs
        WHERE club_name LIKE ?
        ORDER BY club_name
    """, (keyword,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "club_qid": row["club_qid"],
            "club_name": row["club_name"]
        }
        for row in rows
    ]
    

@app.get("/clubs")
def get_clubs():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT club_qid, club_name
        FROM clubs
        ORDER BY club_name
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "club_qid": row["club_qid"],
            "club_name": row["club_name"]
        }
        for row in rows
    ]
    
@app.get("/club/{club_qid}")
def get_players_by_club(club_qid: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT
            p.qid,
            p.display_name,
            p.wikidata_name
        FROM players p
        JOIN player_clubs pc
        ON p.qid = pc.qid
        WHERE pc.club_qid = ?
          AND p.has_korean_name = 1
        ORDER BY p.display_name
    """, (club_qid,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "qid": row["qid"],
            "display_name": row["display_name"],
            "wikidata_name": row["wikidata_name"]
        }
        for row in rows
    ]
    
@app.get("/search/country")
def search_country(q: str):
    conn = get_db_connection()
    cur = conn.cursor()

    keyword = f"%{q}%"

    cur.execute("""
        SELECT DISTINCT
            p.qid,
            p.display_name,
            p.wikidata_name,
            pc.country
        FROM players p
        JOIN player_countries pc
        ON p.qid = pc.qid
        WHERE p.has_korean_name = 1
          AND pc.country LIKE ?
        ORDER BY p.display_name
    """, (keyword,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "qid": row["qid"],
            "display_name": row["display_name"],
            "wikidata_name": row["wikidata_name"],
            "country": row["country"]
        }
        for row in rows
    ]

@app.get("/search/country-list")
def search_country_list(q: str):
    conn = get_db_connection()
    cur = conn.cursor()

    keyword = f"%{q}%"

    cur.execute("""
        SELECT DISTINCT country
        FROM player_countries
        WHERE country LIKE ?
        ORDER BY country
    """, (keyword,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "country": row["country"]
        }
        for row in rows
    ]