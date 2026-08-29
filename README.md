# Instagram Content Intelligence

An evidence-backed, general-purpose Instagram system for strategy, trend research, Insights analytics, Story retention, Reel reverse engineering, visual generation, and reproducible experimentation.

It is a Codex plugin **and** a deterministic Python toolkit. It is not a collection of prompts. LinkedIn and YouTube are intentionally out of scope.

## What makes it different

- A configurable Content Matrix that covers audience, job, intent, pillar, objective, surface, format, angle, evidence, narrative, CTA, lifecycle, effort, and risk—then selects a diverse constrained portfolio instead of generating a useless Cartesian grid.
- General trend intelligence for any account, language, country, or category. It scores velocity, acceleration, recency, source convergence, relevance, evidence quality, saturation, and risk while retaining source limitations.
- Explicit Instagram data provenance. Meta API, Professional Dashboard, manual import, derived metric, and model inference are never silently mixed.
- Story sequence design and frame-level drop-off diagnostics.
- Local Reel reverse engineering with ffprobe/FFmpeg, Whisper, PySceneDetect, and Persian-capable Tesseract. Measured features are separated from interpretation.
- Internal image generation through provider adapters plus deterministic Persian/RTL typography and Playwright overflow QA.
- Reproducible unit tests, schemas, synthetic fixtures, and benchmarks.

## Install

The plugin ships an installation-free runner. Installed Claude/Codex skills call:

```bash
python "${PLUGIN_ROOT}/scripts/ici.py" doctor
```

This works without `pip install` and from any current working directory. Optional Python package installation is still available for the global `ici` command:

```bash
python -m pip install -e .
```

Optional media and visual toolchains:

```bash
python -m pip install -e ".[reels,visual,dev]"
playwright install chromium
```

System packages for the full Reel pipeline: `ffmpeg`/`ffprobe`, Tesseract with `fas` language data, and the dependencies documented by Whisper and PySceneDetect.

## Quick start

```bash
ici trends examples/trends.json
ici matrix examples/matrix.json
ici insights reel examples/reel-insights.json --duration 31
ici insights story examples/story-insights.json
ici reel toolchain
ici reel manifest --media my-reel.mp4 --permission-basis owned
ici visual --headline "یک تیتر دقیق" --body "متن فارسی بدون حدس در تصویر" --html frame.html --png frame.png
```

For an installed plugin, replace `ici` with `python "${PLUGIN_ROOT}/scripts/ici.py"`. Run `doctor` first. Core analytics needs only Python 3.10+. Reel media stages and PNG/image stages declare missing dependencies and degrade without fabricating output.

Run quality gates:

```bash
python -m unittest discover -s tests -v
python benchmarks/run_benchmarks.py
```

## Plugin packaging

- Codex: `.codex-plugin/plugin.json`
- Claude Code/Cowork-compatible package: `.claude-plugin/plugin.json`
- Claude marketplace: `.claude-plugin/marketplace.json`
- Shared skills: `skills/*/SKILL.md`
- Installation-free runtime: `scripts/ici.py`

All four version-bearing files are checked for exact version parity in CI.

## Skills

| Skill | Responsibility |
|---|---|
| `instagram-account-foundation` | General account context, evidence, brand, constraints, and measurement |
| `instagram-content-matrix` | Multidimensional portfolio design, scoring, coverage, and diversity |
| `instagram-trend-intelligence` | Multi-source, source-aware trend research for any account |
| `instagram-insights-analyst` | Reel, Story, post, and account Insights with scope/provenance rules |
| `instagram-story-sequence` | Story narrative continuity and frame-loss control |
| `instagram-reel-reverse-engineering` | Measured transcript/shot/OCR/audio teardown without copying |
| `instagram-reel-script` | Original timecoded Reel production briefs |
| `instagram-visual-generator` | Provider image generation plus deterministic RTL rendering |
| `instagram-experiment-lab` | Experiments, tests, and benchmarks |

## Data boundaries

The project does not scrape or download third-party Reels. Reverse engineering accepts owned, licensed, user-provided, or otherwise authorized local files. Private account exports and tokens must not be committed. Use synthetic or redistributable fixtures in public tests.

Current Meta documentation contains important scope differences: account follower/non-follower breakdown is not automatically a per-media metric; some Dashboard Reel fields are not listed on the current media-insights endpoint; Story availability is time-sensitive; and several values are estimated or in development. See [the metrics catalog](docs/metrics-catalog.md).

## Research and design boundaries

Platform facts and formulas are sourced in [research sources](docs/research-sources.md). Product weights and thresholds are declared design choices and must be calibrated per account. `radio_erfun` can be used as a private first validation account, but no domain-specific logic or private raw data belongs in this repository.

## Upstream attribution

This repository started from the Git history of Charlie Hills' MIT-licensed [`social-media-skills`](https://github.com/charlie947/social-media-skills). The implementation, scope, architecture, skills, analytics, and tests have been rewritten for Instagram Content Intelligence. See [NOTICE](NOTICE).

## فارسی

این پروژه برای یک حوزه خاص ساخته نشده است. زبان، کشور، دسته بندی، سطح ریسک، منابع ترند، وزن ها و محدودیت های Content Matrix همگی قابل تنظیم اند. داده `radio_erfun` فقط می تواند fixture خصوصی اعتبارسنجی باشد و هیچ داده خام خصوصی وارد ریپوی عمومی نمی شود.

## License

MIT. See [LICENSE](LICENSE).
