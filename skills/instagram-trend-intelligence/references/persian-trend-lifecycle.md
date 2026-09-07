# Persian sources, account fit and trend lifecycle

This is a research and decision procedure for the host model, not an automatic
collector, scheduled monitor or new calibrated scoring model. Reviewed 2026-09-07.

## Discover in the audience's language

Resolve language, country/city or diaspora, category, audience job and publication
horizon. Persian language does not imply residence in Iran. Build query variants
using Persian/Arabic Yeh and Kaf, ZWNJ/space, transliteration, colloquial terms and
relevant hashtags. Preserve original source wording in evidence; normalization is
for discovery and deduplication only. Exclude unrelated homonyms explicitly.

## Select sources by their job

| Evidence job | Where to look | What it cannot prove |
|---|---|---|
| Verify an event, product or deadline | Original organizer, official institution, product announcement or original creator | An announcement alone does not prove audience interest |
| Persian reporting and discovery | Relevant desks of ISNA (https://www.isna.ir/) and IRNA (https://www.irna.ir/), plus category publishers with named authors and original sourcing | A publisher's name does not certify every claim or neutrality; syndicated reports are not independent corroboration |
| Technology/culture/category detail | Find the original product, festival, publisher or specialist report behind the Persian article | A translated report does not establish a local trend |
| Search demand | Official Google Trends export, matched geography/query/window | Search interest is not Instagram reach or absolute volume |
| Native adoption | Authorized Instagram observations from multiple distinct relevant creators over time | One viral post, hashtag count or copied format is insufficient |
| Actual audience relevance | Authorized account Insights, recurring questions and reviewed audience feedback | One account is not representative of all Persian speakers |

Publisher homepages are discovery seeds, not citations for specific claims. Open
the exact article; record author, original evidence, event date, publication date,
updated date if present and collection time with timezone. Check editorial origin,
commercial incentive, corrections and subject expertise. Verify disputed claims
against independent original sources; official status identifies provenance, not
universal truth. Never invent RSS endpoints, access permissions or collection results.
If a page is inaccessible, mark it unverified and use an accessible primary source.
Do not describe this seed list as exhaustive or permanently vetted.

News recirculation can make an old event look new. Separate event time from article
time and from the time the topic gained attention. Search snippets, crawl dates and
'updated today' labels do not prove a new event. If the date is missing, state unknown.
Deduplicate by original report/event and content lineage, not just domain or URL.

Google's data guidance: https://support.google.com/trends/answer/4365533?hl=en
and https://newsinitiative.withgoogle.com/resources/trainings/fundamentals/google-trends-understanding-the-data/.
Use matched exports and comparison windows; normalized indices are relative, not
absolute counts. Low or missing data is not proof of zero interest. Do not compare
independently normalized exports as if they share one raw scale.

## Account-fit gate

Answer concretely: which audience problem does this serve, why would this account
credibly discuss it, what original value can it add, can the format be produced
before the moment passes, and does the tone fit the audience's circumstances?
Keep relevance separate from popularity. A very popular but unrelated topic is
skip, not publish. Sensitive news needs relevance and factual care; do not turn
harm or tragedy into a decorative engagement hook.

Publish only with sufficient fresh evidence, a credible account angle and feasible
timing. Use test for plausible fit with weak adoption evidence, watch for unresolved
facts/timing and skip for irrelevance, stale premise or unacceptable factual risk.
Do not disguise these judgments as calibrated probabilities or automatic scores.

## Lifecycle and expiry

Classify emerging, growing, crowded, declining, event-ended, evergreen or unknown.
Support direction using comparable observation windows. Without a baseline use
unknown/newly observed; never infer acceleration from one snapshot.

Specify recheck_at (ISO timestamp with timezone), production lead time and explicit
expiry conditions. Suggested recheck intervals below are editable editorial
defaults, not measurements of a trend's half-life or scheduled tasks:

| Topic type | Starting recheck interval | Typical invalidation condition |
|---|---|---|
| Fast news/live event | 2–6 hours, and immediately before publication | Correction, new event phase, outdated claim |
| Native meme/audio/format | 12–24 hours | Comparable adoption declines, audience mismatch, saturation removes original value |
| Product/launch | 24–72 hours or before publication | Offer/version/availability changes |
| Cultural/calendar moment | Before production and publication | Relevant local event window ends or date changes |
| Durable audience problem | 7–30 days | Supporting facts change; relevance persists independently of the spike |

If production completion is later than the useful window, skip the reactive angle
or propose an explicitly evergreen treatment. Expired evidence does not imply the
underlying topic is worthless. Do not invent a precise expires_at without an actual
deadline; use conditional expiry. Never create monitoring automation unless requested.

## Compact dossier and handoff

Include topic and locale, original URLs and timestamps, independent origins,
baseline/current window, lifecycle evidence, fit rationale, saturation uncertainty,
decision, recheck_at, expiry conditions and one original angle. Distinguish observed
facts from interpretation. Send accepted angles plus evidence to Content Matrix
or Story/Reel writing; do not transfer an expired claim as approved copy.

## Behavioral checks (not claimed completed human evaluations)

- Five sites republish one announcement: count one origin, not five confirmations.
- Old Persian article reposted today: retain the old event date and inspect why-now.
- Global English trend for a local Persian account: require local audience fit.
- Large search spike but no native evidence: label search-interest candidate.
- Event ends before assets are ready: skip reactive timing or choose evergreen value.
- No baseline: unknown trajectory, no invented velocity or expiration date.
- Relevant topic after a correction: revise the claim before producing content.
