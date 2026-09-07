import json
import requests
from bs4 import BeautifulSoup

def scrape_goal_matches():
    url = "https://www.goal.com/ar/%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA-%D8%A7%D9%84%D9%8A%D9%88%D9%85"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    matches_data = []

    # البحث عن عناصر المباريات في Goal.com
    match_containers = soup.select("div[class*='match-row'], article[class*='match-card'], div[data-testid='match-row']")

    if not match_containers:
        # البحث كخطة بديلة عن الحاويات العريضة للمباريات
        match_containers = soup.find_all("div", class_=lambda c: c and 'match' in c.lower())

    for match in match_containers:
        try:
            home_elem = match.select_one("[class*='team-home'], [class*='home-team'], [class*='team-name-home']")
            away_elem = match.select_one("[class*='team-away'], [class*='away-team'], [class*='team-name-away']")
            time_elem = match.select_one("[class*='match-status'], [class*='time'], [class*='kickoff']")
            channel_elem = match.select_one("[class*='broadcaster'], [class*='channel'], [class*='tv']")

            if home_elem and away_elem:
                home = home_elem.text.strip()
                away = away_elem.text.strip()
                match_time = time_elem.text.strip() if time_elem else "غير محدد"
                channel = channel_elem.text.strip() if channel_elem else "غير محددة"

                matches_data.append({
                    "home_team": home,
                    "away_team": away,
                    "time": match_time,
                    "channel": channel
                })
        except Exception:
            continue

    # حفظ النتيجة في ملف JSON
    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(matches_data, f, ensure_ascii=False, indent=2)

    print(f"تم سحب {len(matches_data)} مباراة بنجاح!")

if __name__ == "__main__":
    scrape_goal_matches()
