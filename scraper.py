import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def convert_to_tunisia_time(time_str):
    """تحويل التوقيت وتعديله ليطابق توقيت تونس المحلي تماماً"""
    try:
        clean_time = time_str.strip()
        
        # معالجة الصيغة إذا كانت تحتوي على مساءً/صباحاً أو ص/م
        if "م" in clean_time or "PM" in clean_time.upper():
            clean_time = clean_time.replace("م", "").replace("PM", "").strip()
            parts = clean_time.split(":")
            hour = int(parts[0])
            if hour < 12:
                hour += 12
            match_dt = datetime.strptime(f"{hour}:{parts[1]}", "%H:%M")
        elif "ص" in clean_time or "AM" in clean_time.upper():
            clean_time = clean_time.replace("ص", "").replace("AM", "").strip()
            parts = clean_time.split(":")
            hour = int(parts[0])
            if hour == 12:
                hour = 0
            match_dt = datetime.strptime(f"{hour}:{parts[1]}", "%H:%M")
        else:
            match_dt = datetime.strptime(clean_time, "%H:%M")

        # طرح ساعتين للوصول للتوقيت المحلي في تونس (من 21:00 إلى 19:00)
        tunisia_dt = match_dt - timedelta(hours=2)
        return tunisia_dt.strftime("%H:%M")
    except Exception:
        return time_str

def fetch_matches():
    base_url = "https://www.yallakora.com"
    url = f"{base_url}/match-center"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    matches = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        championships = soup.find_all("div", class_="matchCard")

        for champ in championships:
            league_title = champ.find("h2").text.strip() if champ.find("h2") else "بطولة عامة"
            all_matches = champ.find_all("div", class_="allData")

            for m in all_matches:
                team_a = m.find("div", class_="teamA").text.strip() if m.find("div", class_="teamA") else "N/A"
                team_b = m.find("div", class_="teamB").text.strip() if m.find("div", class_="teamB") else "N/A"
                raw_time = m.find("span", class_="time").text.strip() if m.find("span", class_="time") else "N/A"
                match_status = m.find("div", class_="matchStatus").text.strip() if m.find("div", class_="matchStatus") else "N/A"

                # تحويل الوقت المجلوب إلى توقيت تونس الصحيح (19:00)
                tunisia_time = convert_to_tunisia_time(raw_time) if raw_time != "N/A" else "N/A"

                # القناة الناقلة
                channel_elem = m.find("div", class_="channel")
                channel_name = channel_elem.text.strip() if channel_elem and channel_elem.text.strip() else "غير معلنة"

                # اسم المعلق
                commentator = "غير محدد"

                # جلب التفاصيل الإضافية (القناة والمعلق)
                match_link_elem = m.find("a", href=True)
                if match_link_elem:
                    detail_url = match_link_elem["href"]
                    if not detail_url.startswith("http"):
                        detail_url = base_url + detail_url
                    
                    try:
                        detail_res = requests.get(detail_url, headers=headers, timeout=5)
                        if detail_res.status_code == 200:
                            detail_soup = BeautifulSoup(detail_res.content, "html.parser")
                            
                            channel_det = detail_soup.find("div", class_="channel")
                            if channel_det and channel_det.text.strip():
                                channel_name = channel_det.text.strip()
                                
                            commentator_elem = detail_soup.find("div", class_="commentator")
                            if commentator_elem and commentator_elem.text.strip():
                                commentator = commentator_elem.text.strip()
                    except Exception:
                        pass

                matches.append({
                    "league": league_title,
                    "home_team": team_a,
                    "away_team": team_b,
                    "time": tunisia_time,
                    "status": match_status,
                    "channel": channel_name,
                    "commentator": commentator
                })

        output = {
            "status": "success",
            "timezone": "Tunisia (GMT+1)",
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
