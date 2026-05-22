import requests
import pandas as pd

def get_club_players_final(club_qid):
    # 1. 사용자가 혹시 소문자 'q'를 입력했을 경우를 대비해 대문자 'Q'로 강제 변환
    club_qid = str(club_qid).strip().upper()
    if not club_qid.startswith('Q'):
        club_qid = 'Q' + club_qid

    url = 'https://query.wikidata.org/sparql'
    
    # 2. 위키데이터가 가장 정확하게 인식하는 표준 축구선수-소속팀 매핑 쿼리
    query = f"""
    SELECT DISTINCT ?player ?playerLabel ?countryLabel WHERE {{
      ?player wdt:p106 wd:q934851 .       # 직업: 축구 선수
      ?player wdt:p54 wd:{club_qid} .      # 소속 팀: 입력한 구단 ID (대문자 Q 보장)
      
      # 국적 정보는 안전하게 선택적으로 가져옴
      OPTIONAL {{ ?player wdt:p27 ?country . }}
      
      # 한글 이름 우선, 없으면 영어 이름 출력
      SERVICE wikibase:label {{ 
        bd:serviceParam wikibase:language "ko,en". 
      }}
    }}
    """
    
    # 서버 차단을 막기 위한 표준 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FootballDBProject/1.0'
    }
    
    print(f"📡 위키데이터에서 구단 번호 [{club_qid}]의 역대 선수단을 최종 수집 중...")
    
    try:
        response = requests.get(url, params={'format': 'json', 'query': query}, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ 서버 응답 실패 (에러 코드: {response.status_code})")
            return
            
        data = response.json()
        results = []
        
        for item in data['results']['bindings']:
            # 선수 고유 QID 분리
            qid = item['player']['value'].split('/')[-1]
            player_name = item['playerLabel']['value']
            nationality = item['countryLabel']['value'] if 'countryLabel' in item else "정보 없음"
            
            results.append({
                '위키식별번호(QID)': qid,
                '선수이름': player_name,
                '국적': nationality,
                '검색구단': club_qid
            })
            
        df = pd.DataFrame(results)
        filename = f"club_{club_qid}_final_lineup.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print("\n==================================================")
        print(f"✅ 수집 완료! 총 {len(df)}명의 역대 선수를 찾았습니다.")
        print(f"📂 저장된 파일명: {filename}")
        print("==================================================")
        
    except Exception as e:
        print(f"❌ 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # 소문자 'q8682'를 넣어도 코드 내부에서 자동으로 대문자 'Q8682'로 바꿔서 처리합니다!
    get_club_players_final("Q8682")