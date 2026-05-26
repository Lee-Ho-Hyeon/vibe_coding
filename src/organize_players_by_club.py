import os
import requests
import pandas as pd


def load_name_corrections(path="name_corrections.csv"):
    """
    name_corrections.csv 형식:
    qid,wikidata_name,display_name
    Q11571,크리스티아누 호날두,크리스티아누 호날두
    Q441756,프란시스코 요렌테 헨토,마르코스 요렌테
    """

    if not os.path.exists(path):
        print(f"보정 파일이 없습니다. 새로 생성하세요: {path}")
        return {}

    df = pd.read_csv(path, encoding="utf-8-sig")

    corrections = {}
    for _, row in df.iterrows():
        qid = str(row["qid"]).strip()
        display_name = str(row["display_name"]).strip()

        if qid and display_name:
            corrections[qid] = display_name

    return corrections


def get_club_players(club_qid, correction_path="name_corrections.csv"):
    club_qid = str(club_qid).strip().upper()
    if not club_qid.startswith("Q"):
        club_qid = "Q" + club_qid

    name_corrections = load_name_corrections(correction_path)

    url = "https://query.wikidata.org/sparql"

    query = f"""
    SELECT DISTINCT ?player ?playerLabel ?playerAltLabel ?countryLabel WHERE {{
      ?player p:P54 ?statement .
      ?statement ps:P54 wd:{club_qid} .

      OPTIONAL {{ ?player wdt:P27 ?country . }}

      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "ko,en".
        ?player rdfs:label ?playerLabel .
        ?player skos:altLabel ?playerAltLabel .
        ?country rdfs:label ?countryLabel .
      }}
    }}
    """

    headers = {
        "User-Agent": "FootballDBProject/1.0"
    }

    response = requests.get(
        url,
        params={"format": "json", "query": query},
        headers=headers,
        timeout=30
    )

    if response.status_code != 200:
        print("서버 응답 실패:", response.status_code)
        print(response.text[:1000])
        return

    data = response.json()
    rows = []

    for item in data["results"]["bindings"]:
        qid = item["player"]["value"].split("/")[-1]
        wikidata_name = item.get("playerLabel", {}).get("value", "")
        alias = item.get("playerAltLabel", {}).get("value", "")
        country = item.get("countryLabel", {}).get("value", "정보 없음")

        display_name = name_corrections.get(qid, wikidata_name)

        rows.append({
            "qid": qid,
            "wikidata_name": wikidata_name,
            "display_name": display_name,
            "alias": alias,
            "country": country,
            "club_qid": club_qid
        })

    df = pd.DataFrame(rows)

    if df.empty:
        print("수집 결과가 없습니다.")
        return

    df = (
        df.groupby(
            ["qid", "wikidata_name", "display_name", "country", "club_qid"],
            as_index=False
        )
        .agg({
            "alias": lambda x: ", ".join(sorted(set(v for v in x if v)))
        })
    )

    filename = f"club_{club_qid}_players.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print("수집 완료:", len(df), "명")
    print("저장 파일:", filename)

    print("\n이름 보정 적용 예시:")
    corrected = df[df["wikidata_name"] != df["display_name"]]
    print(corrected.head(20))

    return df


if __name__ == "__main__":
    get_club_players("Q2609")