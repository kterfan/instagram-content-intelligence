"""Instagram Content Intelligence public API."""

from .insights import analyze_reel, analyze_story_sequence
from .matrix import ContentCandidate, MatrixConfig, select_portfolio
from .trends import TrendObservation, TrendProfile, score_trends

__all__ = [
    "ContentCandidate",
    "MatrixConfig",
    "TrendObservation",
    "TrendProfile",
    "analyze_reel",
    "analyze_story_sequence",
    "score_trends",
    "select_portfolio",
]

__version__ = "0.1.1"
