# نشر سريع

Render/Railway/Fly/أي VPS:
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Secrets: SPORTMONKS_API_TOKEN, FIREBASE_DATABASE_URL, FIREBASE_SERVICE_ACCOUNT_JSON

بعد النشر، نفّذ:
`POST /api/sync/YYYY-MM-DD`

ثم سيقرأ StreamBox من Firebase مباشرة ولا يحتاج Sportmonks Token داخل التطبيق.
