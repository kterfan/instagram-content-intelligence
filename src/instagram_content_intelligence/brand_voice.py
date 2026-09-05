from __future__ import annotations

import hashlib
import math
import random
import re
import unicodedata
from collections import Counter
from statistics import mean
from typing import Any

from .persian import comparison_key, contains_phrase

NUMERIC_DIMENSIONS = {
    "directness", "warmth", "humor", "authority", "emotional_intensity",
    "formality", "metaphor_density",
}


QUESTION_BANK = [
    ("brand_promise", "مخاطب بعد از دنبال‌کردن شما چه تغییر مشخصی باید تجربه کند؟", "positioning"),
    ("desired_feeling", "مخاطب پس از شنیدن صدای برند باید دقیقاً چه احساسی داشته باشد؟", "identity"),
    ("audience_relationship", "نقش شما برای مخاطب چیست: دوست، مربی، متخصص، منتقد یا ترکیبی از آن‌ها؟", "identity"),
    ("directness", "از ۰ تا ۱ چقدر مستقیم و بی‌مقدمه حرف می‌زنید؟", "dimensions"),
    ("warmth", "از ۰ تا ۱ میزان صمیمیت و گرمای لحن چقدر است؟", "dimensions"),
    ("humor", "از ۰ تا ۱ شوخی چقدر وارد محتوا می‌شود و چه نوع شوخی ممنوع است؟", "dimensions"),
    ("authority", "از ۰ تا ۱ لحن چقدر مقتدر است و چه شواهدی باید پشت ادعا باشد؟", "dimensions"),
    ("emotional_intensity", "از ۰ تا ۱ شدت عاطفی متن چقدر است؟", "dimensions"),
    ("formality", "از ۰ تا ۱ لحن چقدر رسمی است و مرز محاوره‌ای‌شدن کجاست؟", "dimensions"),
    ("metaphor_density", "از ۰ تا ۱ استعاره و تصویرسازی کلامی چقدر استفاده می‌شود؟", "dimensions"),
    ("code_switching", "استفاده از واژه‌های انگلیسی یا تغییر زبان چه قاعده‌ای دارد؟", "mechanics"),
    ("preferred_words", "چه کلمات، خطاب‌ها یا تکیه‌کلام‌هایی واقعاً مال این برندند؟", "lexical"),
    ("forbidden_phrases", "چه عبارت‌ها، کلیشه‌ها یا CTAهایی هرگز نباید استفاده شوند؟", "lexical"),
    ("emoji_policy", "ایموجی، علامت تعجب، سه‌نقطه و نیم‌فاصله چه قاعده‌ای دارند؟", "mechanics"),
    ("cta_style", "درخواست اقدام باید مستقیم، دعوتی، کنجکاوی‌محور یا بدون CTA باشد؟", "conversion"),
    ("claim_rules", "کدام ادعاها نیازمند منبع، تجربه شخصی یا هشدار عدم‌قطعیت‌اند؟", "evidence"),
    ("format_variants", "لحن در Reel، Story، Caption و Comment چه تفاوت‌هایی دارد؟", "formats"),
]

STOPWORDS = {
    "است", "این", "آن", "را", "به", "از", "در", "که", "و", "یا", "با", "برای", "یک", "اول",
    "the", "a", "an", "and", "or", "to", "of", "in", "is", "it", "this", "that",
}


def build_interview(payload: dict[str, Any]) -> dict[str, Any]:
    """Return only unanswered, high-value questions and evidence requests."""
    answers = payload.get("answers", {})
    questions = [
        {"id": key, "question": question, "section": section}
        for key, question, section in QUESTION_BANK
        if _missing(answers.get(key)) or (key in NUMERIC_DIMENSIONS and _bounded(answers.get(key)) is None)
    ]
    evidence_requests = []
    if len(payload.get("positive_samples", [])) < 3:
        evidence_requests.append("حداقل سه نمونه تأییدشده که واقعاً شبیه صدای برند هستند ارائه کنید.")
    if len(payload.get("negative_samples", [])) < 2:
        evidence_requests.append("حداقل دو نمونه که خوب‌اند اما شبیه این برند نیستند ارائه کنید.")
    if not payload.get("format_samples"):
        evidence_requests.append("در صورت امکان از Reel، Story، Caption و پاسخ Comment نمونه جدا بدهید.")
    return {
        "complete": not questions and not evidence_requests,
        "answered": len(QUESTION_BANK) - len(questions),
        "total": len(QUESTION_BANK),
        "questions": questions,
        "evidence_requests": evidence_requests,
        "next_step": "voice-dna" if not questions and not evidence_requests else "continue-interview",
    }


def build_voice_dna(payload: dict[str, Any]) -> dict[str, Any]:
    answers = payload.get("answers", {})
    positive = [_sample_text(item) for item in payload.get("positive_samples", [])]
    negative = [_sample_text(item) for item in payload.get("negative_samples", [])]
    positive = [item for item in positive if item]
    negative = [item for item in negative if item]
    stats = _corpus_stats(positive)
    negative_stats = _corpus_stats(negative)
    preferred = _as_list(answers.get("preferred_words"))
    preferred.extend(_distinctive_words(positive, negative)[:12])
    forbidden = _as_list(answers.get("forbidden_phrases"))
    gaps = [key for key, _, _ in QUESTION_BANK if _missing(answers.get(key))
            or (key in NUMERIC_DIMENSIONS and _bounded(answers.get(key)) is None)]
    if len(positive) < 3:
        gaps.append("positive_samples<3")
    if len(negative) < 2:
        gaps.append("negative_samples<2")
    dimensions = {
        key: _bounded(answers.get(key))
        for key in (
            "directness", "warmth", "humor", "authority", "emotional_intensity",
            "formality", "metaphor_density",
        )
    }
    return {
        "schema_version": "1.0",
        "version": str(payload.get("version", "draft-1")),
        "identity": {
            "brand_promise": answers.get("brand_promise"),
            "desired_feeling": answers.get("desired_feeling"),
            "audience_relationship": answers.get("audience_relationship"),
        },
        "dimensions": dimensions,
        "lexical": {
            "preferred": sorted(set(item.strip() for item in preferred if item.strip())),
            "forbidden": sorted(set(item.strip() for item in forbidden if item.strip())),
            "observed_top_words": stats["top_words"],
        },
        "rhythm": {
            "observed_average_sentence_words": stats["average_sentence_words"],
            "observed_question_rate": stats["question_rate"],
            "observed_exclamation_rate": stats["exclamation_rate"],
        },
        "mechanics": {
            "emoji_policy": answers.get("emoji_policy"),
            "observed_emoji_per_100_words": stats["emoji_per_100_words"],
            "observed_latin_token_rate": stats["latin_token_rate"],
            "code_switching": answers.get("code_switching"),
            "cta_style": answers.get("cta_style"),
            "claim_rules": answers.get("claim_rules"),
        },
        "format_variants": answers.get("format_variants", {}),
        "evidence": {
            "positive_sample_count": len(positive),
            "negative_sample_count": len(negative),
            "positive_corpus_fingerprint": _fingerprint(positive),
            "negative_corpus_fingerprint": _fingerprint(negative),
            "negative_corpus_stats": negative_stats,
            "owner_answers_present": sorted(key for key, value in answers.items() if not _missing(value)),
        },
        "gaps": sorted(set(gaps)),
        "status": "validated-input-ready" if not gaps else "draft-with-gaps",
    }


def score_voice_fit(text: str, dna: dict[str, Any]) -> dict[str, Any]:
    lexical = dna.get("lexical", {})
    preferred = list({comparison_key(item): item for item in lexical.get("preferred", [])}.values())
    forbidden = list({comparison_key(item): item for item in lexical.get("forbidden", [])}.values())
    preferred_hits = [item for item in preferred if contains_phrase(text, item)]
    forbidden_hits = [item for item in forbidden if contains_phrase(text, item)]
    stats = _corpus_stats([text])
    target = dna.get("rhythm", {}).get("observed_average_sentence_words")
    if target:
        rhythm = max(0.0, 1 - abs(stats["average_sentence_words"] - float(target)) / max(float(target), 1))
    else:
        rhythm = 0.5
    lexical_score = min(1.0, 0.5 + len(preferred_hits) * 0.1) if preferred else 0.5
    penalty = min(1.0, len(forbidden_hits) * 0.35)
    score = max(0.0, min(1.0, lexical_score * 0.55 + rhythm * 0.45 - penalty))
    return {
        "score": round(score, 4),
        "preferred_hits": preferred_hits,
        "forbidden_hits": forbidden_hits,
        "rhythm_similarity": round(rhythm, 4),
        "warning": "Heuristic fit is a screening signal; owner blind testing is the acceptance gate.",
    }


def build_blind_test(candidates: list[dict[str, Any]], *, seed: int = 0) -> dict[str, Any]:
    if len(candidates) < 2:
        raise ValueError("At least two candidates are required")
    prepared = []
    for index, item in enumerate(candidates, 1):
        if not item.get("text") or not item.get("label"):
            raise ValueError("Each candidate needs text and label")
        prepared.append({"candidate_id": f"candidate-{index}", "text": item["text"], "label": item["label"]})
    random.Random(seed).shuffle(prepared)
    return {
        "schema_version": "1.0",
        "items": [{"blind_id": f"voice-{index}", "text": item["text"]} for index, item in enumerate(prepared, 1)],
        "answer_key": {f"voice-{index}": item["label"] for index, item in enumerate(prepared, 1)},
        "instructions": "Without viewing answer_key, identify which item sounds most authentic and explain concrete cues.",
    }


def evaluate_blind_test(pack: dict[str, Any], selections: dict[str, str]) -> dict[str, Any]:
    key = pack.get("answer_key", {})
    results = [
        {"blind_id": blind_id, "expected": expected, "selected": selections.get(blind_id), "correct": selections.get(blind_id) == expected}
        for blind_id, expected in key.items()
    ]
    return {
        "total": len(results),
        "correct": sum(item["correct"] for item in results),
        "accuracy": round(sum(item["correct"] for item in results) / len(results), 4) if results else 0.0,
        "results": results,
    }


def rank_candidates(candidates: list[dict[str, Any]], dna: dict[str, Any]) -> dict[str, Any]:
    ranked = [
        {"id": item.get("id", str(index)), "text": item["text"], **score_voice_fit(item["text"], dna)}
        for index, item in enumerate(candidates)
    ]
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return {"ranked": ranked, "acceptance_requires_owner_blind_test": True}


def detect_voice_drift(previous: dict[str, Any], current: dict[str, Any], *, threshold: float = 0.2) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    previous_dimensions = previous.get("dimensions", {})
    current_dimensions = current.get("dimensions", {})
    for key in sorted(set(previous_dimensions) | set(current_dimensions)):
        old = previous_dimensions.get(key)
        new = current_dimensions.get(key)
        if old is None or new is None:
            continue
        delta = abs(float(new) - float(old))
        if delta >= threshold:
            changes.append({"field": f"dimensions.{key}", "previous": old, "current": new, "delta": round(delta, 4)})

    old_words = set(previous.get("lexical", {}).get("preferred", []))
    new_words = set(current.get("lexical", {}).get("preferred", []))
    union = old_words | new_words
    lexical_change = 0.0 if not union else 1 - len(old_words & new_words) / len(union)
    if lexical_change >= threshold:
        changes.append({
            "field": "lexical.preferred",
            "change": round(lexical_change, 4),
            "added": sorted(new_words - old_words),
            "removed": sorted(old_words - new_words),
        })

    old_rhythm = _float_or_none(previous.get("rhythm", {}).get("observed_average_sentence_words"))
    new_rhythm = _float_or_none(current.get("rhythm", {}).get("observed_average_sentence_words"))
    if old_rhythm is not None and new_rhythm is not None:
        rhythm_change = abs(new_rhythm - old_rhythm) / max(abs(old_rhythm), 1)
        if rhythm_change >= threshold:
            changes.append({"field": "rhythm.average_sentence_words", "change": round(rhythm_change, 4)})
    return {
        "drift_detected": bool(changes),
        "threshold": threshold,
        "changes": changes,
        "requires_owner_review": bool(changes),
        "warning": "Drift is descriptive; create a new accepted DNA version only after owner review.",
    }


def _corpus_stats(texts: list[str]) -> dict[str, Any]:
    sentences = []
    words = []
    question_count = 0
    exclamation_count = 0
    emoji_count = 0
    for text in texts:
        parts = [part.strip() for part in re.split(r"[.!?؟\n]+", text) if part.strip()]
        sentences.extend(parts)
        tokens = _tokens(text)
        words.extend(tokens)
        question_count += text.count("?") + text.count("؟")
        exclamation_count += text.count("!")
        emoji_count += sum(unicodedata.category(char) in {"So", "Sk"} for char in text)
    sentence_lengths = [len(_tokens(sentence)) for sentence in sentences]
    denominator = max(len(sentences), 1)
    word_denominator = max(len(words), 1)
    top = Counter(word for word in words if len(word) > 2 and word not in STOPWORDS).most_common(20)
    return {
        "text_count": len(texts),
        "word_count": len(words),
        "average_sentence_words": round(mean(sentence_lengths), 3) if sentence_lengths else 0.0,
        "question_rate": round(question_count / denominator, 4),
        "exclamation_rate": round(exclamation_count / denominator, 4),
        "emoji_per_100_words": round(emoji_count / word_denominator * 100, 4),
        "latin_token_rate": round(sum(bool(re.fullmatch(r"[a-z0-9_]+", word)) for word in words) / word_denominator, 4),
        "top_words": [{"word": word, "count": count} for word, count in top],
    }


def _distinctive_words(positive: list[str], negative: list[str]) -> list[str]:
    pos = Counter(_tokens(" ".join(positive)))
    neg = Counter(_tokens(" ".join(negative)))
    scored = [
        (word, count - neg[word])
        for word, count in pos.items()
        if len(word) > 2 and word not in STOPWORDS and count - neg[word] > 0
    ]
    return [word for word, _ in sorted(scored, key=lambda item: (-item[1], item[0]))]


def _sample_text(item: Any) -> str:
    return str(item.get("text", "")) if isinstance(item, dict) else str(item)


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [part.strip() for part in re.split("[,،]", str(value)) if part.strip()]


def _bounded(value: Any) -> float | None:
    if value is None or value == "" or isinstance(value, bool):
        return None
    try:
        number = float(comparison_key(str(value)).replace("٫", "."))
        return round(number, 4) if math.isfinite(number) and 0 <= number <= 1 else None
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _missing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _fingerprint(texts: list[str]) -> str | None:
    if not texts:
        return None
    normalized = "\n".join(re.sub(r"\s+", " ", text.strip()) for text in texts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _tokens(text: str) -> list[str]:
    return re.findall(
        r"[A-Za-z0-9_\u0621-\u063A\u0641-\u064A\u0660-\u0669\u0671-\u06D3\u06F0-\u06F9]+",
        comparison_key(text),
    )
