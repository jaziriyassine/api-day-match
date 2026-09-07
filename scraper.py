import json
import requests
from bs4 import BeautifulSoup

def fetch_matches():
    # استخدام رابط live-scores لتفادي خطأ 404
    url = "https://www.goal.com/ar/live-scores"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ar-TN,ar;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    matches = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # البحث عن العناصر البرمجية للمباريات
        match_containers = soup.select("div[data-testid='match-row'], div.match-row, article.match-card")

        for match in match_containers:
            team_names = match.select("span[data-testid='team-name'], span.team-name, .team-title")
            time_elem = match.select_one("time, .match-status, .status")

            if len(team_names) >= 2:
                matches.append({
                    "home_team": team_names[0].get_text(strip=True),
                    "away_team": team_names[1].get_text(strip=True),
                    "time": time_elem.get_text(strip=True) if time_elem else "N/A"
                })

        data = {
            "status": "success",
            "total_matches": len(matches),
            "matches": matches
        }

    except Exception as e:
        data = {
            "status": "error",
            "message": str(e),
            "total_matches": 0,
            "matches": []
        }

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_matches()
