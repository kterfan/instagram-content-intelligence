---
name: instagram-reel-reverse-engineering
description: Reverse engineer an owned, licensed, user-provided, or authorized reference Reel using measured transcript, timing, shots, OCR, audio, hook, payoff, and CTA structure. Use for Reel teardown, forensic analysis, viral-mechanism analysis, or adaptation without copying.
---

# Instagram Reel Reverse Engineering

Measure first, interpret second, adapt mechanisms rather than protected expression.

## Intake and rights

Accept local media with an explicit permission basis: owned, licensed, user-provided, or public reference. Do not add a scraping/downloading shortcut. An optional acquisition adapter must document authorization, terms, and provenance.

## Pipeline

1. Check dependencies: `ici reel toolchain`.
2. Create the audit manifest: `ici reel manifest --media <file> --permission-basis user_provided`.
3. For an installed toolchain, run the measurable pipeline: `ici reel pipeline --media <file> --output-dir <folder> --permission-basis user_provided --language fa`.
4. Probe the container and streams with ffprobe.
5. Extract audio/frames with FFmpeg.
6. Transcribe speech with Whisper, retaining word timestamps and language confidence.
7. Detect shot boundaries with PySceneDetect.
8. OCR on-screen text with Tesseract; use `fas+eng` when Persian and English coexist.
9. Store measured words, pauses, shots, overlays, and audio events in JSON.
10. Run `ici reel features --input <measured.json>` when analyzing a separately prepared fixture.
11. Interpret hook promise, first-three-second density, pattern interrupts, escalation, proof, payoff, CTA, loop, and likely skip points. Label these as inference.
12. Produce an originality-safe adaptation brief: reusable mechanism, what must change, and what must not be copied.

## Quality gate

- Transcript, shot, and OCR confidence or failure is visible.
- Every timestamp claim traces to measured data.
- Performance claims use Insights data if available; content structure alone cannot prove causality.
- The output includes at least two alternative explanations and a validation experiment.
