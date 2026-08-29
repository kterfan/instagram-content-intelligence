# Contributing

Contributions are welcome when they preserve the project's evidence, provenance, portability, and reproducibility rules.

## Development

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python benchmarks/run_benchmarks.py
python scripts/validate_repository.py
```

## Rules

- Keep shared logic independent of any one account, language, country, or niche.
- Add primary-source documentation for new Instagram fields or external adapters.
- Label platform fact, derived metric, model inference, and product-design choice separately.
- Never commit tokens, private Insights exports, third-party media, or account-private fixtures.
- Add or update a deterministic test for every behavior change.
- New trend adapters must declare authentication, terms URL, coverage, latency, evidence quality, and limitations.
- New media acquisition adapters must require a documented authorization basis.
- Skill folder and frontmatter names must match and use lowercase hyphenated names.

Use Conventional Commit prefixes such as `feat:`, `fix:`, `docs:`, and `test:`.
