from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ToolStatus:
    name: str
    available: bool
    path: str | None
    purpose: str


TOOLS = {
    "ffprobe": "container, stream, duration, frame-rate, and codec metadata",
    "ffmpeg": "audio and frame extraction",
    "whisper": "multilingual speech transcription with timestamps",
    "scenedetect": "shot-boundary detection",
    "tesseract": "on-screen text OCR; install the Persian fas language pack when needed",
}


def inspect_toolchain() -> list[dict[str, Any]]:
    return [
        asdict(ToolStatus(name, bool(path := shutil.which(name)), path, purpose))
        for name, purpose in TOOLS.items()
    ]


def _run(command: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout)


def probe_media(path: str | Path) -> dict[str, Any]:
    media = Path(path).resolve()
    if not media.is_file():
        raise FileNotFoundError(media)
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe is required and was not found")
    completed = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(media),
        ]
    )
    return json.loads(completed.stdout)


def build_analysis_manifest(path: str | Path, permission_basis: str) -> dict[str, Any]:
    if permission_basis not in {"owned", "licensed", "user_provided", "public_reference"}:
        raise ValueError("Declare a supported permission_basis")
    media = Path(path).resolve()
    return {
        "media": str(media),
        "permission_basis": permission_basis,
        "acquisition": "local_file_only",
        "toolchain": inspect_toolchain(),
        "stages": [
            {"id": "probe", "tool": "ffprobe", "output": "media.json"},
            {"id": "audio", "tool": "ffmpeg", "output": "audio.wav"},
            {"id": "transcript", "tool": "whisper", "output": "transcript.json", "language": "auto_or_explicit"},
            {"id": "shots", "tool": "scenedetect", "output": "shots.csv"},
            {"id": "ocr", "tool": "tesseract", "output": "on_screen_text.json", "language": "fas+eng"},
            {"id": "features", "tool": "ici", "output": "measured_features.json"},
            {"id": "interpretation", "tool": "skill", "output": "reverse_engineering_report.md"},
        ],
        "guardrails": [
            "Do not download third-party media without an authorized, terms-compliant adapter.",
            "Separate measured features from model interpretation.",
            "Abstract reusable patterns; do not reproduce protected expression or creator identity.",
        ],
    }


def run_local_pipeline(
    path: str | Path,
    output_dir: str | Path,
    permission_basis: str,
    *,
    whisper_model: str = "turbo",
    language: str | None = None,
    ocr_language: str = "fas+eng",
    ocr_interval_seconds: float = 1.0,
    strict: bool = False,
) -> dict[str, Any]:
    """Execute the measurable local pipeline and retain every stage failure.

    Optional Python packages are imported only inside their stages. In non-strict
    mode an unavailable stage is recorded and the remaining stages continue.
    """

    media = Path(path).resolve()
    if not media.is_file():
        raise FileNotFoundError(media)
    manifest = build_analysis_manifest(media, permission_basis)
    folder = Path(output_dir).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    status: list[dict[str, Any]] = []

    def stage(name: str, callback):
        try:
            value = callback()
            status.append({"stage": name, "status": "complete"})
            return value
        except Exception as exc:  # stage isolation is intentional
            status.append({"stage": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
            if strict:
                raise
            return None

    metadata = stage("probe", lambda: probe_media(media))
    if metadata is not None:
        _write_json(folder / "media.json", metadata)

    audio_path = folder / "audio.wav"

    def extract_audio():
        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg is required")
        _run(["ffmpeg", "-y", "-i", str(media), "-vn", "-ac", "1", "-ar", "16000", str(audio_path)])
        return audio_path

    audio = stage("audio", extract_audio)

    def transcribe():
        if audio is None:
            raise RuntimeError("audio stage did not complete")
        try:
            import whisper
        except ImportError as exc:
            raise RuntimeError("Install the reels extra to enable Whisper") from exc
        model = whisper.load_model(whisper_model)
        options: dict[str, Any] = {"word_timestamps": True}
        if language:
            options["language"] = language
        result = model.transcribe(str(audio_path), **options)
        _write_json(folder / "transcript.json", result)
        return result

    transcript = stage("transcript", transcribe)

    def detect_shots():
        try:
            from scenedetect import ContentDetector, SceneManager, open_video
        except ImportError as exc:
            raise RuntimeError("Install the reels extra to enable PySceneDetect") from exc
        video = open_video(str(media))
        manager = SceneManager()
        manager.add_detector(ContentDetector())
        manager.detect_scenes(video)
        shots = [
            {"start": start.get_seconds(), "end": end.get_seconds()}
            for start, end in manager.get_scene_list()
        ]
        _write_json(folder / "shots.json", shots)
        return shots

    shots = stage("shots", detect_shots)

    frames_dir = folder / "ocr-frames"

    def extract_ocr_frames():
        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg is required")
        frames_dir.mkdir(exist_ok=True)
        _run(
            [
                "ffmpeg", "-y", "-i", str(media), "-vf", f"fps=1/{ocr_interval_seconds}",
                str(frames_dir / "frame-%06d.jpg"),
            ]
        )
        return sorted(frames_dir.glob("frame-*.jpg"))

    frames = stage("ocr_frames", extract_ocr_frames)

    def run_ocr():
        if frames is None:
            raise RuntimeError("OCR frame extraction did not complete")
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Install the reels extra and Pillow to enable OCR") from exc
        results = []
        for index, frame in enumerate(frames):
            data = pytesseract.image_to_data(
                Image.open(frame), lang=ocr_language, output_type=pytesseract.Output.DICT
            )
            tokens = [
                {"text": text.strip(), "confidence": float(conf)}
                for text, conf in zip(data["text"], data["conf"])
                if text.strip() and float(conf) >= 0
            ]
            results.append({"start": index * ocr_interval_seconds, "frame": frame.name, "tokens": tokens})
        _write_json(folder / "on_screen_text.json", results)
        return results

    overlays = stage("ocr", run_ocr)
    measured = {
        "duration_seconds": _duration_from_probe(metadata),
        "words": _flatten_words(transcript),
        "shots": shots or [],
        "overlays": _flatten_overlays(overlays),
    }
    _write_json(folder / "measured_features.json", measured)
    features = analyze_measured_features(measured)
    _write_json(folder / "analysis.json", features)
    result = {
        "manifest": manifest,
        "status": status,
        "measured": measured,
        "analysis": features,
        "output_dir": str(folder),
    }
    _write_json(folder / "pipeline-result.json", result)
    return result


def analyze_measured_features(payload: dict[str, Any]) -> dict[str, Any]:
    duration = float(payload.get("duration_seconds") or 0)
    words = payload.get("words", [])
    shots = payload.get("shots", [])
    overlays = payload.get("overlays", [])
    first_spoken = min((float(item.get("start", 0)) for item in words), default=None)
    cuts = max(0, len(shots) - 1)
    return {
        "duration_seconds": duration,
        "speech": {
            "first_spoken_second": first_spoken,
            "words_per_minute": (len(words) / duration * 60) if duration else None,
        },
        "editing": {
            "shot_count": len(shots),
            "cuts_per_minute": (cuts / duration * 60) if duration else None,
            "median_shot_seconds": _median_shot_length(shots),
        },
        "visual_text": {
            "overlay_count": len(overlays),
            "first_overlay_second": min((float(item.get("start", 0)) for item in overlays), default=None),
        },
        "interpretation_questions": [
            "What promise is established in the first three seconds?",
            "Where do visual or semantic pattern interrupts occur?",
            "Which beats create curiosity, proof, payoff, or action?",
            "Which reusable mechanism can be adapted without copying expression?",
        ],
    }


def _median_shot_length(shots: list[dict[str, Any]]) -> float | None:
    lengths = sorted(
        float(shot["end"]) - float(shot["start"])
        for shot in shots
        if shot.get("end") is not None and shot.get("start") is not None
    )
    if not lengths:
        return None
    middle = len(lengths) // 2
    return lengths[middle] if len(lengths) % 2 else (lengths[middle - 1] + lengths[middle]) / 2


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def _duration_from_probe(metadata: dict[str, Any] | None) -> float | None:
    if not metadata:
        return None
    try:
        return float(metadata.get("format", {}).get("duration"))
    except (TypeError, ValueError):
        return None


def _flatten_words(transcript: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not transcript:
        return []
    words = []
    for segment in transcript.get("segments", []):
        if segment.get("words"):
            words.extend(segment["words"])
        elif segment.get("text"):
            words.append({"word": segment["text"], "start": segment.get("start"), "end": segment.get("end")})
    return words


def _flatten_overlays(frames: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not frames:
        return []
    overlays = []
    for frame in frames:
        text = " ".join(token["text"] for token in frame.get("tokens", []))
        if text:
            confidences = [token["confidence"] for token in frame["tokens"]]
            overlays.append({"start": frame["start"], "text": text, "confidence": sum(confidences) / len(confidences)})
    return overlays
