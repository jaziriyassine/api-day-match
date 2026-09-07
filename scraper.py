import json
import re
import requests
from bs4 import BeautifulSoup

def fetch_matches():
    url = "https://www.goal.com/ar/%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA-%D8%A7%D9%84%D9%8A%D9%88%D9%85"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        matches = []
        
        # البحث عن كروت المباريات بأكثر من نمط محتمل
        match_cards = soup.find_all("div", class_=re.compile(r"match-row|match-card|fixture", re.I))

        for card in match_cards:
            teams = card.find_all(["span", "div"], class_=re.compile(r"team-name|name|title", re.I))
            time_elem = card.find(["time", "span", "div"], class_=re.compile(r"time|status|date", re.I))

            if len(teams) >= 2:
                matches.append({
                    "home_team": teams[0].get_text(strip=True),
                    "away_team": teams[1].get_text(strip=True),
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
