from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class StoryFramePlan:
    frame: int
    role: str
    promise: str
    copy: str
    visual_change: str
    interaction: str | None
    continuation_cue: str | None
    measurement: tuple[str, ...]


DEFAULT_ROLES = (
    "pattern_interrupt",
    "problem_recognition",
    "tension_or_gap",
    "value_delivery",
    "proof_or_example",
    "interaction",
    "resolution",
    "cta",
)


def design_story_sequence(
    objective: str,
    audience_job: str,
    promise: str,
    frame_count: int = 7,
    interaction_frames: Iterable[int] = (3, 6),
) -> dict:
    """Create a measurable sequence skeleton; copy remains a content-layer responsibility."""

    if not 3 <= frame_count <= 15:
        raise ValueError("frame_count must be between 3 and 15")
    interaction_set = set(interaction_frames)
    roles = [DEFAULT_ROLES[min(round(i * (len(DEFAULT_ROLES) - 1) / (frame_count - 1)), len(DEFAULT_ROLES) - 1)] for i in range(frame_count)]
    plans = []
    for index, role in enumerate(roles, start=1):
        interaction = "context-appropriate sticker" if index in interaction_set else None
        plans.append(
            StoryFramePlan(
                frame=index,
                role=role,
                promise=promise,
                copy=f"[{role}] Advance the audience job: {audience_job}",
                visual_change="Change composition, scale, crop, or motion from previous frame",
                interaction=interaction,
                continuation_cue=None if index == frame_count else "Open loop with a truthful next-frame payoff",
                measurement=("reach", "navigation", "replies", "shares") if interaction else ("reach", "navigation"),
            )
        )
    return {
        "objective": objective,
        "audience_job": audience_job,
        "promise": promise,
        "frames": [asdict(plan) for plan in plans],
        "guardrails": [
            "Each frame must pay off or advance the opening promise.",
            "Do not infer causality from a drop-off flag without a controlled comparison.",
            "Interactions must serve the narrative, not add arbitrary friction.",
            "Log the version, publish window, and audience context before comparison.",
        ],
    }

