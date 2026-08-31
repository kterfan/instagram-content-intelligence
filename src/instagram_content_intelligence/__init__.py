"""Instagram Content Intelligence public API."""

from .brand_voice import build_interview, build_voice_dna, detect_voice_drift, score_voice_fit
from .cloud_reel import align_retention, audit_cloud_result, build_prompt_pack, compare_reports, verify_hybrid
from .insights import analyze_reel, analyze_story_sequence
from .matrix import ContentCandidate, MatrixConfig, select_portfolio
from .trends import TrendObservation, TrendProfile, score_trends

__all__ = [
    "ContentCandidate",
    "MatrixConfig",
    "TrendObservation",
    "TrendProfile",
    "align_retention",
    "analyze_reel",
    "analyze_story_sequence",
    "audit_cloud_result",
    "build_interview",
    "build_prompt_pack",
    "build_voice_dna",
    "compare_reports",
    "detect_voice_drift",
    "score_voice_fit",
    "score_trends",
    "select_portfolio",
    "verify_hybrid",
]

__version__ = "0.2.0"
