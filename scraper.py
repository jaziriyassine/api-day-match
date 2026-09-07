import json
import requests
from datetime import datetime

def fetch_matches():
    today = datetime.now().strftime("%Y%m%d")
    
    # API مجاني ومباشر وجاهز لبيانات المباريات اليومية
    url = f"https://www.fotmob.com/api/matches?date={today}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    matches = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        for league in data.get("leagues", []):
            league_name = league.get("name", "غير معروف")
            for match in league.get("matches", []):
                home_team = match.get("home", {}).get("name", "N/A")
                away_team = match.get("away", {}).get("name", "N/A")
                
                # استخراج توقيت المباراة
                match_time = match.get("status", {}).get("startTimeStr", "N/A")
                status = match.get("status", {}).get("reason", {}).get("short", "N/A")

                matches.append({
                    "league": league_name,
                    "home_team": home_team,
                    "away_team": away_team,
                    "time": match_time,
                    "status": status
                })

        result = {
            "status": "success",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_matches": len(matches),
            "matches": matches
        }

    except Exception as e:
        result = {
            "status": "error",
            "message": str(e),
            "total_matches": 0,
            "matches": []
        }

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_matches()
