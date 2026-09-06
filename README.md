# Instagram Content Intelligence

An evidence-backed, general-purpose Instagram system for strategy, trend research, Insights analytics, Story retention, cloud/local Reel reverse engineering, validated Brand Voice, visual generation, and reproducible experimentation.

It is a Codex plugin **and** a deterministic Python toolkit. It is not a collection of prompts. LinkedIn and YouTube are intentionally out of scope.

## What makes it different

- A configurable Content Matrix that covers audience, job, intent, pillar, objective, surface, format, angle, evidence, narrative, CTA, lifecycle, effort, and risk—then selects a diverse constrained portfolio instead of generating a useless Cartesian grid.
- General trend intelligence for any account, language, country, or category. It scores velocity, acceleration, recency, source convergence, relevance, evidence quality, saturation, and risk while retaining source limitations.
- Explicit Instagram data provenance. Meta API, Professional Dashboard, manual import, derived metric, and model inference are never silently mixed.
- Story sequence design and frame-level drop-off diagnostics.
- Cloud-native Reel Prompt Packs for Gemini and compatible ChatGPT surfaces, evidence packs for Claude, optional local measurement, hybrid verification, response audit, retention alignment, and cross-report comparison.
- A Brand Voice Interview Engine that combines adaptive questions, positive/negative samples, versioned Voice DNA, heuristic screening, blind owner validation, and format variants.
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

System packages for the optional local/hybrid Reel measurement path: `ffmpeg`/`ffprobe`, Tesseract with `fas` language data, and the dependencies documented by Whisper and PySceneDetect. They are not required to generate a cloud Prompt Pack.

## Quick start

```bash
ici trends examples/trends.json
ici matrix examples/matrix.json
ici insights reel examples/reel-insights.json --duration 31
ici insights story examples/story-insights.json
ici reel toolchain
ici reel manifest --media my-reel.mp4 --permission-basis owned
ici reel prompt-pack --input examples/reel-cloud-context.json --provider gemini --output-dir reel-pack
ici reel audit --input model-response.json --manifest reel-pack/reel-analysis-manifest.json
ici reel hybrid-verify --input model-response.json --measured measured_features.json
ici voice interview --input examples/brand-voice-interview.json
ici voice dna --input examples/brand-voice-interview.json --output voice-dna.json
ici visual --headline "یک تیتر دقیق" --body "متن فارسی بدون حدس در تصویر" --html frame.html --png frame.png
```

For an installed plugin, replace `ici` with `python "${PLUGIN_ROOT}/scripts/ici.py"`. Run `doctor` first. Core analytics needs only Python 3.10+. Reel media stages and PNG/image stages declare missing dependencies and degrade without fabricating output.

Run quality gates:

```bash
python -m unittest discover -s tests -t . -v
python benchmarks/run_benchmarks.py
```

## Plugin packaging

- Codex: `.codex-plugin/plugin.json`
- Claude Code/Cowork-compatible package: `.claude-plugin/plugin.json`
- Claude marketplace: `.claude-plugin/marketplace.json`
- Shared skills: `skills/*/SKILL.md`
- Installation-free runtime: `scripts/ici.py`

All version-bearing manifests and package files are checked for exact version parity in CI.

## Skills

| Skill | Responsibility |
|---|---|
| `instagram-account-foundation` | General account context, evidence, constraints, measurement, and Voice DNA linkage |
| `instagram-brand-voice` | Adaptive interview, corpus evidence, Voice DNA, blind validation, and drift control |
| `instagram-content-matrix` | Multidimensional portfolio design, scoring, coverage, and diversity |
| `instagram-trend-intelligence` | Multi-source, source-aware trend research for any account |
| `instagram-insights-analyst` | Reel, Story, post, and account Insights with scope/provenance rules |
| `instagram-story-sequence` | Story narrative continuity and frame-loss control |
| `instagram-reel-reverse-engineering` | Cloud-native/evidence/local/hybrid teardown, audit, retention alignment, and originality-safe adaptation |
| `instagram-reel-script` | Original timecoded Reel production briefs |
| `instagram-visual-generator` | Provider image generation plus deterministic RTL rendering |
| `instagram-experiment-lab` | Experiments, tests, and benchmarks |

## Data boundaries

The project does not scrape or download third-party Reels. Reverse engineering accepts owned, licensed, user-provided, or otherwise authorized files/evidence packs. Private account exports, media, voice corpora, and tokens must not be committed. Use synthetic or redistributable fixtures in public tests. Cloud upload is a user choice and remains subject to the selected provider's account, retention, and privacy settings.

Current Meta documentation contains important scope differences: account follower/non-follower breakdown is not automatically a per-media metric; some Dashboard Reel fields are not listed on the current media-insights endpoint; Story availability is time-sensitive; and several values are estimated or in development. See [the metrics catalog](docs/metrics-catalog.md).

## Research and design boundaries

Platform facts and formulas are sourced in [research sources](docs/research-sources.md). Product weights and thresholds are declared design choices and must be calibrated per account. `radio_erfun` can be used as a private first validation account, but no domain-specific logic or private raw data belongs in this repository.

## Upstream attribution

This repository started from the Git history of Charlie Hills' MIT-licensed [`social-media-skills`](https://github.com/charlie947/social-media-skills). The implementation, scope, architecture, skills, analytics, and tests have been rewritten for Instagram Content Intelligence. See [NOTICE](NOTICE).

## فارسی

نسخهٔ 0.3 گردش‌کار فارسی نسخه‌دار، تقویم شمسی و ICS، بسته تولید Reel/Story/Carousel،
فونت همراه بسته، زیرنویس SRT/VTT، ثبت خصوصی آمار و ارزیابی کور کیفیت را اضافه می‌کند.
[راهنمای کامل و مثال‌های قابل‌اجرا](docs/persian-workflow.md).

```bash
python scripts/ici.py workflow init --project private/my-account
python scripts/ici.py workflow compose --project private/my-account
python scripts/ici.py workflow export --project private/my-account --output-dir outputs/my-account
```

برای تقویم `pip install -e ".[calendar]"` و برای خروجی PNG گروه `visual` به‌همراه
Chromium لازم است. هستهٔ تولید، زیرنویس، دفتر نتایج و ارزیابی انسانی وابستگی اجباری
جدید ندارند. متن اصیل توسط کاربر یا Skill میزبان نوشته می‌شود؛ این ابزار انتشار
خودکار یا ادعای تضمین رشد ندارد. رجیستری مناسبت‌ها فعلاً دو مناسبت فرهنگی دارای
منبع است، نه تقویم کامل تعطیلات رسمی.

راهنمای [پردازش فارسی و معنای داده ناقص](docs/persian-analysis.md) شامل
یکسان‌سازی حروف و ارقام برای مقایسه، فیلتر زبان/کشور مشاهده، پاسخ عددی فارسی
در مصاحبه لحن و تفکیک نبود آمار از نرخ صفر است.

این پروژه برای یک حوزه خاص ساخته نشده است. زبان، کشور، دسته بندی، سطح ریسک، منابع ترند، وزن ها و محدودیت های Content Matrix همگی قابل تنظیم اند. داده `radio_erfun` فقط می تواند fixture خصوصی اعتبارسنجی باشد و هیچ داده خام خصوصی وارد ریپوی عمومی نمی شود.

## License

MIT. See [LICENSE](LICENSE).
