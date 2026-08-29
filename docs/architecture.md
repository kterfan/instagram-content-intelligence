# Architecture

## Layers

1. **Acquisition** — authorized Meta API, time-sensitive Story webhook, Professional Dashboard/manual import, official exports, user-provided media, and configured public-source adapters.
2. **Provenance** — every datum records kind, source, collection time, scope, version, estimated status, and limitations.
3. **Deterministic analysis** — rates, Story frame loss, trend normalization/scoring, Content Matrix selection, and measured Reel features.
4. **Interpretation skills** — competing explanations, strategy, scripts, adaptations, and experiment design. These outputs remain labeled inference.
5. **Production** — provider-generated base images, deterministic exact-text RTL rendering, and QA.
6. **Validation** — schema tests, unit/property tests, synthetic/golden fixtures, and benchmark reports.

## Key boundary

```text
source data -> provenance record -> deterministic feature JSON -> skill interpretation -> experiment -> measured result
```

An LLM may interpret measured data, but it does not rewrite the measurements. A Dashboard-only observation may be analyzed, but it cannot masquerade as a Meta API field.

## Account portability

Shared code contains no niche names. Account adapters provide language, region, audience jobs, categories, risk, weights, brand tokens, source registry choices, and private baselines. A profile can inherit repository defaults and override only justified fields.

