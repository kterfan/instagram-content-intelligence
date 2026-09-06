# گردش‌کار فارسی از ایده تا نتیجه — 0.3.0

این نسخه یک گردش‌کار محلی برای تولید، بازبینی و یادگیری است. متن اصیل را صاحب
حساب یا Skill میزبان می‌نویسد؛ ابزار Python قرارداد، نسخه، خروجی و آمار را
مدیریت می‌کند. خروجی مدل همیشه پیش‌نویس است و هیچ انتشار خودکاری انجام نمی‌شود.

## شروع ساده، بدون ویرایش JSON

از ریشه Plugin اجرا کنید؛ اگر جای دیگری هستید مسیر کامل `scripts/ici.py` را بدهید.
داده شخصی را در پوشه خصوصی خودتان نگه دارید.

```powershell
python scripts/ici.py workflow init --project private/my-account
python scripts/ici.py workflow compose --project private/my-account
python scripts/ici.py workflow export --project private/my-account --output-dir outputs/my-account
python scripts/ici.py workflow status --project private/my-account
```

`init` درباره حساب، مخاطب، زبان، کشور، منطقه زمانی، موضوع، هدف، وعده، لحن و
قالب سؤال می‌کند. زبان فارسی کشور مخاطب را تعیین نمی‌کند. `compose` متن هر
بخش، تصویر، صدا، دلیل ادامه و مبنای ادعا را می‌گیرد. اگر ادعا به منبع بیرونی
وابسته باشد، منبع و شاهد را هم می‌پرسد. برای Reel، گفتار و مدت هر بخش لازم است.

برای کار با دستیار، پس از init از `workflow prompt` استفاده کنید. پاسخ دستیار
باید با `schemas/production.schema.json` سازگار باشد؛ سپس آن را وارد کنید:

```powershell
python scripts/ici.py workflow prompt --project private/my-account --output private/prompt.json
python scripts/ici.py workflow import --project private/my-account --input private/production.json
```

نسخه‌ها با hash زمینه و متن ذخیره می‌شوند. تغییر کپشن یا زمینه، نسخه تازه
می‌سازد؛ تاریخچه قبلی پاک نمی‌شود. `status` امکان ادامه پروژه قبلی را می‌دهد.
فریم نهایی باید نقش `payoff` داشته باشد؛ ابزار وجود ساختار را می‌سنجد، اما
درستی معنایی پاسخ وعده و صحت منبع همچنان نیازمند بررسی صاحب محتواست.

## خروجی تولید

هر خروجی زیر پوشه نسخه خود قرار می‌گیرد و شامل این موارد است:

- `production.json` و `production.md`: متن و زمینه نسخه‌دار، فرضیه و شاخص‌ها.
- `shot-list.csv`: شات، صدا، گفتار و زمان؛ سلول‌های فرمول‌مانند بی‌اثر می‌شوند.
- `caption.txt`: کپشن و CTA.
- `frame-*.html` و `cover.html`: قالب RTL مستقل با فونت محلی Vazirmatn.
- برای Reel: فایل‌های UTF-8 با پسوند SRT و VTT و هشدار بار خواندن زیرنویس.

Story و Reel با بوم ۱۰۸۰×۱۹۲۰، Carousel و Cover با بوم ۱۰۸۰×۱۳۵۰ ساخته می‌شوند.
این ابعاد و safe area انتخاب طراحی‌اند؛ ادعای انطباق دائمی با UI اینستاگرام ندارند.
فونت از v33.003 پروژه Vazirmatn و با مجوز OFL همراه بسته است؛ رندر به اینترنت
یا فونت نصب‌شده روی دستگاه متکی نیست. PNG به Playwright و Chromium نیاز دارد:

```powershell
python -m pip install -e ".[visual]"
python -m playwright install chromium
python scripts/ici.py workflow export --project private/my-account --output-dir outputs/my-account --png
```

رندر قبل از ساخت PNG بارگذاری فونت و سرریز را بررسی می‌کند. متن بلند حذف یا
خلاصه نمی‌شود؛ خطا می‌دهد تا متن یا چیدمان اصلاح شود. زمان‌بندی زیرنویس داده
ورودی است و هم‌ترازی اندازه‌گیری‌شده با صدای واقعی محسوب نمی‌شود. حدود پیش‌فرض
۳۲ نویسه، دو خط و ۲۰ نویسه در ثانیه، معیارهای قابل‌تنظیم طراحی‌اند.

## تقویم شمسی و مناسبت‌ها

```powershell
python -m pip install -e ".[calendar]"
python scripts/ici.py calendar --start ۱۴۰۵-۰۹-۲۸ --days 7 --timezone Asia/Tehran --time 18:00 --events config/iran-occasions.json --ics outputs/calendar.ics --output outputs/calendar.json
```

تبدیل تاریخ با `jdatetime` انجام می‌شود. تاریخ شمسی و میلادی، منطقه زمانی، ساعت
محلی و UTC در خروجی می‌مانند. ICS زمان پیشنهادی تولید/انتشار را وارد تقویم
می‌کند؛ اتصال یا ارسال به Google Calendar در کار نیست. ساعت‌های مبهم یا ناموجود
ناشی از DST رد می‌شوند. اگر timezone database روی ویندوز موجود نباشد، `tzdata`
از گروه calendar آن را فراهم می‌کند؛ UTC بدون آن هم قابل استفاده است.

رجیستری اولیه شامل **دو مناسبت فرهنگی** نوروز و یلدا با منبع و تاریخ بررسی
است؛ تقویم رسمی کامل تعطیلات نیست. نوروز اول فروردین با مناسبت ثابت ۲۱ مارس
سازمان ملل یکی فرض نمی‌شود. مناسبت‌های قمری یا رویدادهای متغیر را با تاریخ
دقیق، تقویم ورودی، منبع و وضعیت `verified` یا `needs_review` وارد کنید. منبعی
که در زمان برنامه‌ریزی بیش از ۳۶۵ روز از بررسی‌اش گذشته باشد برای بازبینی علامت
می‌خورد. تناسب مناسبت با برند باید جدا بررسی شود.

## ثبت نتایج و بازخورد به انتخاب محتوا

```powershell
python scripts/ici.py results record --database private/results.sqlite --project private/my-account --input private/result.json
python scripts/ici.py results import-csv --database private/results.sqlite --input private/results.csv
python scripts/ici.py results compare --database private/results.sqlite --metric save_per_reach --output outputs/comparison.json
```

قرارداد `schemas/publication-result.schema.json` و نمونه
`examples/publication-result.json` را ببینید. `--project` شناسه حساب، محتوا، نسخه،
قالب و هدف را از پروژه می‌گیرد؛ برای انتشار نسخه قدیمی، hash همان نسخه را در
`revision` بدهید. snapshotها بر اساس حساب، media_id، بازه و منبع یکتا هستند.
ورود دوباره همان داده بی‌اثر است؛ داده متناقض رد می‌شود. واردکردن یک batch در
SQLite تراکنشی است و خطا کل batch را برمی‌گرداند.

فیلد `reviewed=true` برای بازبینی انسانی ورودی لازم است. داده دستی، API و
Dashboard جدا می‌مانند. اسکرین‌شات می‌تواند توسط میزبان خوانده شود، اما مقدار
نامطمئن تا بازبینی وارد تحلیل نمی‌شود؛ این نسخه موتور OCR اختصاصی جدید ندارد.
ارقام فارسی، ممیز `٫` و جداکننده هزارگان `٬` پذیرفته می‌شوند. مقادیر خالی null
می‌مانند. بازه گزارش باید با زمان انتشار و مشاهده هم‌خوان باشد.

مقایسه در گروه‌های همسان حساب، قالب، هدف، بازه، نوع ترافیک، منبع و آزمایش انجام
می‌شود. حد پیش‌فرض پنج انتشار برای هر variant است، نه تضمین کفایت آماری.
خروجی میانه و بازه bootstrap تفاوت میانه‌ها را گزارش می‌کند. داده همبستگی است؛
نسبت‌دادن نتیجه به تغییر سناریو نیازمند طراحی آزمایش دارد.

در گروه با داده کافی، `advisory_historical_priors` رتبه نسبی میانه‌ها در همان
گروه را بین صفر و یک می‌دهد. این عدد احتمال موفقیت نیست. Skill ماتریس می‌تواند
با ثبت گروه مرجع و پس از بررسی تناسب، آن را در `scores.historical_prior`
کاندید مرتبط به کار ببرد؛ وزن‌های اصلی یا نسخه پروفایل خودکار تغییر نمی‌کنند.

## ارزیابی واقعی کیفیت فارسی

```powershell
python scripts/ici.py evaluate prepare --input examples/quality-candidates.json --output-dir private/evaluation --seed 42
python scripts/ici.py evaluate score --input private/evaluation/blind.json --ratings private/evaluation/ratings-completed.json --output outputs/quality-report.json
```

بستهٔ ارزیابی و کلید پاسخ در دو فایل جدا هستند. فقط `blind.json` را به ارزیاب
بدهید؛ کلید را قبل از امتیازدهی نبیند. طبیعی‌بودن فارسی، لحن، وضوح، قابلیت اجرا
و پشتوانه ادعا هر کدام ۱ تا ۵ و همراه دلیل سنجیده می‌شوند. قالب ratings حاوی
null است؛ داده ناقص هرگز قبولی محسوب نمی‌شود. شناسه ارزیابی جلوی قاطی‌شدن
امتیازها میان دو چینش متفاوت را می‌گیرد.

شش نمونه اولیه در سه حوزه آموزش، فروشگاه و طراحی **مصنوعی و برای راه‌اندازی
روش** هستند؛ نتیجه ارزیابی انسانی یا معیار عمومی بازار محسوب نمی‌شوند.
برای سنجش واقعی، نمونه‌های مجاز حساب و یک مجموعه جدا از داده توسعه فراهم
کنید. کیفیت متن و عملکرد اینستاگرام دو گزارش جدا هستند؛ این نسخه هیچ بهبود
بازدید یا رتبه انسانی ساختگی گزارش نمی‌کند.

## اجرای نمونه کامل و آزمون

```powershell
python scripts/ici.py workflow init --project private/demo --input examples/persian-brief.json
python scripts/ici.py workflow import --project private/demo --input examples/persian-production.json
python scripts/ici.py workflow export --project private/demo --output-dir outputs/demo --png
python scripts/ici.py results record --project private/demo --database private/demo.sqlite --input examples/publication-result.json
python -m unittest discover -s tests -t . -v
```

برای تست تصویری `ICI_VISUAL_TESTS=1` بگذارید. CI دو مسیر دارد: هسته بدون
وابستگی‌های اختیاری و مسیر کامل تقویم/مرورگر/Schema. بسته wheel هم مستقل از
ریپو نصب و بارگذاری فونتش بررسی می‌شود. `doctor` قابلیت‌های حاضر را گزارش می‌کند.
