import json
import requests
from bs4 import BeautifulSoup


def fetch_matches():
    # رابط صفحة المباريات في موقع Goal العربي
    url = "https://www.goal.com/ar/%D9%85%D0%A0%D8%A7%D9%83%D8%B2-%D8%A7%D9%84%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ar-TN,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    matches_data = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # البحث عن بطاقات المباريات داخل الصفحة
        match_cards = soup.find_all("div", class_="match-row") or soup.find_all(
            "article", class_="match-card"
        )

        for card in match_cards:
            try:
                # الفريق الأول والثاني
                teams = card.find_all(["span", "div"], class_="team-name")
                home_team = (
                    teams[0].text.strip()
                    if len(teams) > 0
                    else "فريق غير معروف"
                )
                away_team = (
                    teams[1].text.strip()
                    if len(teams) > 1
                    else "فريق غير معروف"
                )

                # النتيجة أو الوقت
                status_elem = card.find(
                    ["span", "div"], class_=["match-status", "time", "score"]
                )
                status = (
                    status_elem.text.strip()
                    if status_elem
                    else "غير محدد"
                )

                # القناة الناقلة والمعلق (إن وجد)
                channel_elem = card.find(
                    ["span", "div"], class_=["channel", "broadcaster"]
                )
                channel = (
                    channel_elem.text.strip()
                    if channel_elem
                    else "غير متوفر"
                )

                matches_data.append(
                    {
                        "home_team": home_team,
                        "away_team": away_team,
                        "status_or_time": status,
                        "channel": channel,
                    }
                )
            except Exception:
                continue

    except Exception as e:
        print(f"حدث خطأ أثناء جلب البيانات: {e}")

    # كتابة البيانات وحفظها في ملف matches.json دائماً حتى لو كانت القائمة فارغة
    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "status": "success",
                "total_matches": len(matches_data),
                "matches": matches_data,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"تم تحديث matches.json بنجاح! عدد المباريات: {len(matches_data)}")


if __name__ == "__main__":
    fetch_matches()
