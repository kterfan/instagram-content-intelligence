# General Trend Intelligence specification

## Definition

A trend candidate is a topic, format, behavior, sound, visual grammar, or audience question showing time-bounded change in one or more applicable sources. A single popular item is an observation, not sufficient proof of a trend.

## Applicability before scoring

Each source declares language, geography, categories, latency, evidence quality, authentication, terms, and limitations. The account profile selects the applicable subset. PubMed can be strong evidence for a health account and irrelevant for a fashion account; RSS quality depends on the configured publisher allowlist; community chatter is not population-representative.

## Normalization

Raw counts remain within their source. Each observation is converted to change relative to its own historical baseline, then robustly scaled within the evaluation batch. Google Trends exports preserve their 0–100 relative meaning and are never labeled volume.

## Score and confidence

Score combines velocity, acceleration, recency, source convergence, account relevance, and evidence quality, then subtracts saturation and risk above the account tolerance. Confidence combines source convergence, evidence quality, and repeated observations. Weights are normalized and versioned.

High score + low confidence means **test quickly**. High confidence + low relevance means **do not chase it**. High relevance + high saturation requires a differentiated angle.

## Required dossier

Every recommended trend includes query, sources, observation times, transformations, source count, score, confidence, saturation, risk, audience relevance, expiry hypothesis, original angles, and a validation test.

