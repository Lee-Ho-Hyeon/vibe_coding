import requests
import csv
import time

BASE_URL = "https://fcplayer.org/api/cards/{}"

START_ID = 1
END_ID = 10000   # 원하는 범위로 수정

OUTPUT_CSV = "fcplayer_unique_names.csv"

headers = {
    "User-Agent": "Mozilla/5.0"
}

seen_names = set()
results = []

for card_id in range(START_ID, END_ID + 1):
    url = BASE_URL.format(card_id)

    try:
        response = requests.get(url, headers=headers, timeout=10)

        # 응답 실패 시 넘어가기
        if response.status_code != 200:
            print(f"[SKIP] {card_id} - Status: {response.status_code}")
            continue

        # JSON 변환 시도
        try:
            data = response.json()
        except:
            print(f"[SKIP] {card_id} - Invalid JSON")
            continue

        # not found 처리
        if isinstance(data, dict):
            if data.get("message") == "Not Found":
                print(f"[NOT FOUND] {card_id}")
                continue

            if data.get("success") is False:
                print(f"[FAILED] {card_id}")
                continue

        # name 추출
        name = data.get("name")

        if not name:
            print(f"[NO NAME] {card_id}")
            continue

        # 중복 제거
        if name in seen_names:
            print(f"[DUPLICATE] {card_id}: {name}")
            continue

        seen_names.add(name)
        results.append([name])

        print(f"[OK] {card_id}: {name}")

    except Exception as e:
        print(f"[ERROR] {card_id}: {e}")

    time.sleep(0.1)

# CSV 저장
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["name"])
    writer.writerows(results)

print(f"\n저장 완료: {OUTPUT_CSV}")
print(f"총 선수 수: {len(results)}")