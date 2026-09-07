# Match Day Sync — Sportmonks → Firebase

هذا المشروع مستقل عن تطبيق StreamBox: وظيفته الوحيدة جلب مباريات اليوم من Sportmonks وتخزينها في Firebase Realtime Database.

المسار الذي يكتب إليه:
`match_day/{YYYY-MM-DD}/matches/{fixtureId}`

والبيانات تشمل الفرق، الدوري، وقت البداية، الحالة، النتيجة، و`tvStations` مع الدولة.

## التشغيل
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
ثم:
```bash
curl -X POST http://127.0.0.1:8000/api/sync/2026-09-06
```

## المتغيرات
- `SPORTMONKS_API_TOKEN`
- `FIREBASE_DATABASE_URL`
- `FIREBASE_SERVICE_ACCOUNT_JSON`

لا تضع أي مفتاح داخل Git أو APK. خزّن الأسرار في Secrets الخاصة بخدمة الاستضافة.

## جدولة التحديث
يمكن استدعاء `/api/sync/{date}` من Cron خارجي. للمباريات المباشرة يفضل استدعاء endpoint كل 30–60 ثانية أثناء المباريات فقط، أو استخدام جدولة الاستضافة.
