# StreamBox Match Day Backend

هذا الجزء مستقل عن تطبيق IPTV.

`matchday-sync` يجلب بيانات Sportmonks ويخزنها في Firebase Realtime Database. تطبيق StreamBox لا يحتاج Sportmonks token؛ يقرأ البيانات الجاهزة من Firebase ويطابق القناة الناقلة مع قنوات IPTV.
