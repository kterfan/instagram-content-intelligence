# Persian analysis and missing-data semantics

## فارسی

کلید مقایسه فارسی برای تحقیق ترند و ارزیابی لحن مشترک است: ی/ک عربی و فارسی،
ارقام فارسی/عربی/لاتین و فاصله/نیم‌فاصله را یکدست می‌کند. متن اصلی برای نمایش
و شواهد حفظ می‌شود. اعراب و نشانه‌گذاری حذف نمی‌شوند و شکل چسبیده واژه‌ها حدس
زده نمی‌شود. این ابزار، مترجم یا اصلاح‌گر متن نهایی نیست.

زبان و کشور هر مشاهده باید با پروفایل سازگار باشد. `*` به معنی نامعلوم است؛
این مشاهده‌ها برای سازگاری با ورودی‌های قبلی پذیرفته می‌شوند، اما تعدادشان در
`unknown_locale_observation_count` نمایش داده می‌شود. برای پژوهش محدود به
داده با زبان و کشور مشخص، در `profile` ورودی ترند این گزینه را قرار دهید:

```json
"allow_unknown_locale": false
```

زبان `fa` به‌تنهایی کشور `IR` را اثبات نمی‌کند. اطلاعات منبع عمومی هم جای
زبان و کشور خود مشاهده را نمی‌گیرد.

پاسخ عددی مصاحبه لحن می‌تواند مثل `۰٫۷` نوشته شود. مقدار نامعتبر، خارج از
بازه صفر تا یک یا نامتناهی، شکاف ورودی محسوب می‌شود. عبارت‌های ترجیحی را
می‌توان با ویرگول فارسی جدا کرد. کنترل عبارت ممنوع، معادل‌های فارسی را
می‌شناسد و «کار» را داخل «کاربرد» تطبیق نمی‌دهد.

## Compatibility and interpretation

- Exact repeated trend measurements are deduplicated before scaling and scoring.
  Identity includes normalized topic, source, timestamp, measurements, locale,
  categories and evidence URL. Equivalent timezone representations compare equal.
  Measurements at different times or from different sources remain distinct.
  This is not semantic deduplication or a model of publisher independence.
- `confidence_kind` explicitly marks trend confidence as a heuristic, not a
  calibrated probability. Unknown locale counts are disclosed, not automatically
  discounted by an invented numeric penalty.
- `interaction_per_reach` is unavailable unless shares, saves, likes and comments
  are all supplied. `interaction_coverage` distinguishes missing, partial and
  complete inputs. Complete all-zero counts still yield zero when reach is positive.
  Consumers must handle `null`; it no longer means zero engagement.
- Account follower/non-follower shares require both counts. A missing count must
  not produce a misleading 100% share for the other group.
- Voice numeric dimensions accept only finite values in [0, 1]. Invalid answers
  are asked again and keep DNA in draft status. Heuristic voice scores can change
  because matching is normalized and respects word boundaries; re-score saved
  candidates before comparing with new scores.
- Original visual copy is untouched. These changes do not provide a Jalali
  calendar, new content-generation model, or an automatic publication service.

Regression coverage: `tests/test_persian_integrity.py`.
