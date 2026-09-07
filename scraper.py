import json
import requests
from datetime import datetime

def fetch_matches():
    # الحصول على تاريخ اليوم بتنسيق YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    
    # API المباريات التابع لـ Goal.com
    url = f"https://www.goal.com/api/v7/competitions/matches?startDate={today}&endDate={today}&locale=ar"
    
    # ترويسات تحاكي متصفحاً حقيقياً وتحدد المنطقة واللغة
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ar-TN,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.goal.com",
        "Referer": "https://www.goal.com/ar"
    }

    matches = []

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        # استخراج البيانات الهيكلية للمباريات
        for comp in data.get("competitions", []):
            league_name = comp.get("name", "بطولة غير محددة")
            for match in comp.get("matches", []):
                home = match.get("homeTeam", {}).get("name", "N/A")
                away = match.get("awayTeam", {}).get("name", "N/A")
                match_time = match.get("time", "N/A")
                status = match.get("status", "N/A")

                matches.append({
                    "league": league_name,
                    "home_team": home,
                    "away_team": away,
                    "time": match_time,
                    "status": status
                })

        output = {
            "status": "success",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_matches": len(matches),
            "matches": matches
        }

    except Exception as err:
        output = {
            "status": "error",
            "message": str(err),
            "total_matches": 0,
            "matches": []
        }

    # حفظ النتائج في ملف JSON
    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_matches()
