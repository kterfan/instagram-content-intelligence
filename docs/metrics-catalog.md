# Instagram metrics catalog and provenance rules

This catalog reflects official sources accessed during the 2026-08-29 research pass. Re-check current Meta documentation before changing an API contract.

## Reel media API

The current media-insights reference documents Reel metrics including comments, crossposted/Facebook views, likes, reach, reposts, saves, shares, views, average watch time, total video watch time, and skip rate. Several are estimated and/or in development. Media data can be delayed and retention differs from Story data.

The current media reference does not document Reel-level `profile_activity`, `profile_visits`, or `follows`. Instagram's Help Center does describe Reel follows in the UI. Therefore a Reel follow/profile field must retain Dashboard/manual provenance unless Meta's API contract changes.

## Story media API

Story navigation breakdown distinguishes Next Story (`SWIPE_FORWARD`), Back (`TAP_BACK`), Exit (`TAP_EXIT`), and Forward (`TAP_FORWARD`). Story data is time-sensitive, small values can be unavailable, and UI/API/webhook values can differ. Collect before expiration and retain the route.

## Account breakdown

Account-level reach/views can expose follower/non-follower and media-product breakdowns. This is an account-interval distribution, not automatic attribution to a specific Reel.

## Derived ratios

- `share_per_reach = shares / reach`
- `save_per_reach = saves / reach`
- `interaction_per_reach = (likes + comments + saves + shares) / reach`
- Story frame-drop proxy = `(previous frame reach - current frame reach) / previous frame reach`
- Profile conversion must name the chosen numerator and denominator. Dashboard-attributed follows/reach and account profile-visits/reach are different constructs.

Zero denominators return unavailable, not zero performance. Derived ratios are not native Instagram metrics.

