# Architecture

## Layers

1. **Acquisition** — authorized Meta API, time-sensitive Story webhook, Professional Dashboard/manual import, official exports, user-provided media, and configured public-source adapters.
2. **Provenance** — every datum records kind, source, collection time, scope, version, estimated status, and limitations.
3. **Deterministic analysis** — rates, Story frame loss, trend normalization/scoring, Content Matrix selection, Voice DNA corpus features, local Reel features, cloud response audits, and retention/timeline alignment.
4. **Interpretation skills** — native-video/evidence-pack Reel understanding, competing explanations, strategy, scripts, adaptations, and experiment design. These outputs remain labeled inference.
5. **Production** — provider-generated base images, deterministic exact-text RTL rendering, and QA.
6. **Validation** — schema tests, unit/property tests, synthetic/golden fixtures, and benchmark reports.

## Key boundary

```text
source data -> provenance record -> deterministic feature JSON -> skill interpretation -> experiment -> measured result
```

An LLM may interpret measured data, but it does not rewrite the measurements. A Dashboard-only observation may be analyzed, but it cannot masquerade as a Meta API field.

## Reel execution modes

```text
authorized video -> cloud-video-native -> audited structured response
authorized evidence pack -> cloud-evidence-pack -> audited structured response
authorized video -> local-measured -> reproducible feature JSON
cloud response + local measurements -> hybrid-verified -> disagreement/coverage audit
```

Gemini is the preferred documented native-video route. ChatGPT video attachment is product-surface dependent and carries a completeness warning. Claude uses the evidence-pack route unless its host exposes a documented video tool. Local packages are optional; hybrid verification is the highest-confidence path.

## Account portability

Shared code contains no niche names. Account adapters provide language, region, audience jobs, categories, risk, weights, brand tokens, source registry choices, and private baselines. A profile can inherit repository defaults and override only justified fields.

Brand Voice is a versioned evidence object, not a list of adjectives. Owner intent, positive/negative samples, observed corpus traits, performance observations, format variants, and gaps remain distinct. Automatic fit scores screen candidates; blinded owner evaluation accepts or rejects them.
