"""Optional Jalali conversion, sourced occasions and UTC calendar exports."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .contracts import text_field
from .persian import comparison_key


def _jalali():
    try:
        import jdatetime
        return jdatetime
    except ImportError as exc:
        raise RuntimeError("برای تقویم نصب کنید: python -m pip install 'jdatetime>=5.2,<7' tzdata") from exc


def parse_date(value: str, calendar: str = "jalali") -> date:
    value = comparison_key(value).replace("/", "-")
    if calendar == "gregorian":
        return date.fromisoformat(value)
    if calendar != "jalali":
        raise ValueError("calendar must be jalali or gregorian")
    year, month, day = map(int, value.split("-"))
    return _jalali().date(year, month, day).togregorian()


def jalali_label(value: date) -> str:
    result = _jalali().date.fromgregorian(date=value)
    return f"{result.year:04d}-{result.month:02d}-{result.day:02d}"


def local_instant(day: date, time: str, zone: str) -> datetime:
    try:
        tz = timezone.utc if zone == "UTC" else ZoneInfo(zone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("منطقه زمانی ناشناخته است؛ در ویندوز tzdata را نصب کنید") from exc
    raw = datetime.fromisoformat(f"{day.isoformat()}T{comparison_key(time).replace('٫', '.')}")
    if raw.tzinfo:
        raise ValueError("time باید ساعت محلی بدون offset باشد")
    local = raw.replace(tzinfo=tz)
    if local.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None) != raw:
        raise ValueError("این ساعت در تغییر ساعت تابستانی وجود ندارد")
    if local.utcoffset() != raw.replace(tzinfo=tz, fold=1).utcoffset():
        raise ValueError("ساعت محلی مبهم است؛ یک ساعت دیگر انتخاب کنید")
    return local


def calendar_days(start: str, days: int, *, calendar="jalali", zone="Asia/Tehran", time="18:00", events=()) -> list[dict]:
    if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= 366:
        raise ValueError("days must be between 1 and 366")
    first = parse_date(start, calendar)
    validated = []
    for event in events:
        for key in ("title", "source_url", "verified_on", "status"):
            text_field(event, key)
        if not event["source_url"].startswith("https://"):
            raise ValueError("event source_url must be HTTPS")
        date.fromisoformat(event["verified_on"])
        if event["status"] not in {"verified", "needs_review"}:
            raise ValueError("event status must be verified or needs_review")
        if "date" in event:
            parse_date(event["date"], event.get("calendar", "jalali"))
        elif not (1 <= event.get("month", 0) <= 12 and 1 <= event.get("day", 0) <= 31):
            raise ValueError("event needs a date or month/day")
        validated.append(event)
    rows = []
    for offset in range(days):
        day = first + timedelta(days=offset)
        local = local_instant(day, time, zone)
        label = jalali_label(day)
        matches = []
        for event in validated:
            if "date" in event:
                match = parse_date(event["date"], event.get("calendar", "jalali")) == day
            else:
                match = (int(label[5:7]), int(label[8:10])) == (event["month"], event["day"])
            if match:
                matched = dict(event)
                matched["source_age_days_at_schedule"] = (day - date.fromisoformat(event["verified_on"])).days
                if matched["source_age_days_at_schedule"] > 365:
                    matched["status"] = "needs_review"
                matches.append(matched)
        rows.append({"jalali": label, "gregorian": day.isoformat(), "timezone": zone,
                     "local": local.isoformat(), "utc": local.astimezone(timezone.utc).isoformat(),
                     "occasions": matches, "schedule_status": "proposed_not_published"})
    return rows


def _ics_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\r", "").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


def _fold(line: str) -> str:
    lines, current = [], ""
    for char in line:
        if len((current + char).encode("utf-8")) > 75:
            lines.append(current)
            current = " "
        current += char
    return "\r\n".join(lines + [current])


def write_ics(rows: list[dict], output: str | Path, *, title="برنامه محتوای اینستاگرام") -> Path:
    import hashlib
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Instagram Content Intelligence//FA//EN"]
    for row in rows:
        start = datetime.fromisoformat(row["utc"]).astimezone(timezone.utc)
        uid = hashlib.sha256((row["utc"] + title).encode()).hexdigest()[:24]
        lines.extend(["BEGIN:VEVENT", f"UID:{uid}@ici.local", f"DTSTAMP:{stamp}",
                      "DTSTART:" + start.strftime("%Y%m%dT%H%M%SZ"),
                      "DTEND:" + (start + timedelta(minutes=30)).strftime("%Y%m%dT%H%M%SZ"),
                      "SUMMARY:" + _ics_escape(title),
                      "DESCRIPTION:" + _ics_escape(row["jalali"] + " — زمان پیشنهادی؛ انتشار خودکار نیست"),
                      "END:VEVENT"])
    lines.append("END:VCALENDAR")
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(("\r\n".join(_fold(line) for line in lines) + "\r\n").encode("utf-8"))
    return target
