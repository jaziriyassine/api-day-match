import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import firebase_admin
import requests
from firebase_admin import credentials, db
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("matchday-sync")

SPORTMONKS_BASE = "https://api.sportmonks.com/v3/football"
TOKEN = os.getenv("SPORTMONKS_API_TOKEN", "").strip()
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "").strip().rstrip("/")
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
REQUEST_TIMEOUT = int(os.getenv("SPORTMONKS_TIMEOUT_SECONDS", "20"))

app = FastAPI(title="StreamBox Match Day Sync", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])


def init_firebase() -> None:
    if firebase_admin._apps:
        return
    if not FIREBASE_DATABASE_URL or not FIREBASE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("FIREBASE_DATABASE_URL and FIREBASE_SERVICE_ACCOUNT_JSON are required")
    info = json.loads(FIREBASE_SERVICE_ACCOUNT_JSON)
    cred = credentials.Certificate(info)
    firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})


def sportmonks_get(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    if not TOKEN:
        raise RuntimeError("SPORTMONKS_API_TOKEN is not configured")
    query = dict(params or {})
    query["api_token"] = TOKEN
    response = requests.get(f"{SPORTMONKS_BASE}{path}", params=query, timeout=REQUEST_TIMEOUT)
    if not response.ok:
        raise RuntimeError(f"Sportmonks HTTP {response.status_code}: {response.text[:300]}")
    return response.json()


def normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def participants(raw: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    rows = raw.get("participants") or []
    home = next((p for p in rows if normalize((p.get("meta") or {}).get("location")) == "home"), None)
    away = next((p for p in rows if normalize((p.get("meta") or {}).get("location")) == "away"), None)
    return home or (rows[0] if rows else None), away or (rows[1] if len(rows) > 1 else None)


def score_for(raw_scores: Any, side: str) -> int | None:
    if not isinstance(raw_scores, list):
        return None
    preferred = {"CURRENT", "CURRENT_SCORE", "FULL_TIME", "2ND_HALF"}
    candidates = []
    for row in raw_scores:
        if not isinstance(row, dict):
            continue
        code = normalize(((row.get("type") or {}).get("code")))
        description = normalize(row.get("description"))
        if code.upper() in preferred or description.upper() in preferred:
            candidates.append(row)
    candidates += [r for r in raw_scores if isinstance(r, dict) and r not in candidates]
    for row in candidates:
        meta = ((row.get("participant") or {}).get("meta") or {})
        location = normalize(meta.get("location"))
        if location and location != side:
            continue
        value = row.get("score")
        if isinstance(value, dict):
            value = value.get("goals")
        if value is None:
            value = row.get("goals")
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def status_of(state: Any) -> str:
    value = normalize((state or {}).get("state") if isinstance(state, dict) else state).upper()
    mapping = {
        "NS": "upcoming", "NOT STARTED": "upcoming", "SCHEDULED": "upcoming",
        "LIVE": "live", "INPLAY": "live", "IN PLAY": "live", "1ST HALF": "live", "2ND HALF": "live",
        "HT": "halftime", "HALFTIME": "halftime", "PAUSED": "halftime",
        "FT": "finished", "FINISHED": "finished", "AET": "finished", "PEN": "finished",
        "POSTPONED": "postponed", "PST": "postponed", "CANCELLED": "cancelled", "CANC": "cancelled",
    }
    return mapping.get(value, "unknown")


def map_match(raw: dict[str, Any]) -> dict[str, Any]:
    home, away = participants(raw)
    league = raw.get("league") or {}
    broadcasters = []
    for row in raw.get("tvstations") or raw.get("tvStations") or []:
        station = row.get("tvstation") or row.get("tvStation") or {}
        country = row.get("country") or {}
        if not station.get("name"):
            continue
        broadcasters.append({
            "id": station.get("id"),
            "name": station.get("name"),
            "logoUrl": station.get("image_path") or station.get("imagePath"),
            "country": country.get("name"),
            "countryCode": country.get("iso2") or country.get("iso2_code"),
        })
    # Stable de-duplication.
    seen = set(); broadcasters = [b for b in broadcasters if not ((k := f"{normalize(b['name'])}|{normalize(b.get('countryCode'))}") in seen or seen.add(k))]
    return {
        "id": str(raw["id"]),
        "name": raw.get("name") or f"{(home or {}).get('name', '')} vs {(away or {}).get('name', '')}",
        "homeTeam": (home or {}).get("name", ""),
        "awayTeam": (away or {}).get("name", ""),
        "league": league.get("name") or "Football",
        "leagueLogoUrl": league.get("image_path"),
        "startTime": raw.get("starting_at") or "",
        "timestamp": raw.get("starting_at_timestamp"),
        "status": status_of(raw.get("state") or raw.get("status") or raw.get("state_id")),
        "minute": raw.get("minute") or ((raw.get("state") or {}).get("minute") if isinstance(raw.get("state"), dict) else None),
        "homeScore": score_for(raw.get("scores"), "home"),
        "awayScore": score_for(raw.get("scores"), "away"),
        "broadcasters": broadcasters,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }


def sync_date(date: str) -> dict[str, Any]:
    init_firebase()
    payload = sportmonks_get(f"/fixtures/date/{date}", {
        "include": "country;participants;scores;state;league;tvStations.tvstation;tvStations.country"
    })
    rows = payload.get("data") or []
    matches = [map_match(row) for row in rows if isinstance(row, dict) and row.get("id")]
    ref = db.reference(f"match_day/{date}/matches")
    ref.set({m["id"]: m for m in matches})
    db.reference(f"match_day/{date}/meta").set({
        "date": date, "updatedAt": datetime.now(timezone.utc).isoformat(), "count": len(matches), "source": "sportmonks"
    })
    log.info("Synced %s: %s matches", date, len(matches))
    return {"date": date, "count": len(matches)}


@app.get("/")
def health():
    return {"status": "ok", "service": "matchday-sync"}


@app.post("/api/sync/today")
def sync_today():
    try:
        date = datetime.now().date().isoformat()
        return sync_date(date)
    except Exception as exc:
        log.exception("sync today failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/sync/{date}")
def sync(date: str):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return sync_date(date)
    except Exception as exc:
        log.exception("sync failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/status/{date}")
def status(date: str):
    try:
        init_firebase()
        return db.reference(f"match_day/{date}/meta").get() or {"date": date, "count": 0}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
