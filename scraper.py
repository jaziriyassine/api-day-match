import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_matches():
    # استخدام كشط للبيانات الهيكلية من موقع كرة قدم عربي مستقر
    url = "https://www.yallakora.com/match-center"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    matches = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # استخراج البطولات والمباريات من الصفحة
        championships = soup.find_all("div", class_="matchCard")

        for champ in championships:
            league_title = champ.find("h2").text.strip() if champ.find("h2") else "بطولة عامة"
            all_matches = champ.find_all("div", class_="allData")

            for m in all_matches:
                team_a = m.find("div", class_="teamA").text.strip() if m.find("div", class_="teamA") else "N/A"
                team_b = m.find("div", class_="teamB").text.strip() if m.find("div", class_="teamB") else "N/A"
                match_time = m.find("span", class_="time").text.strip() if m.find("span", class_="time") else "N/A"
                match_status = m.find("div", class_="matchStatus").text.strip() if m.find("div", class_="matchStatus") else "N/A"

                matches.append({
                    "league": league_title,
                    "home_team": team_a,
                    "away_team": team_b,
                    "time": match_time,
                    "status": match_status
                })

        output = {
            "status": "success",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_matches": len(matches),
            "matches": matches
        }

    except Exception as e:
        output = {
            "status": "error",
            "message": str(e),
            "total_matches": 0,
            "matches": []
        }

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_matches()
