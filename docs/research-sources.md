# Research sources

Primary or original sources were preferred. Practitioner frameworks are identified as such.

| Area | Source | Key use | Limitation |
|---|---|---|---|
| Insights overview | [Meta Instagram Platform Insights](https://developers.facebook.com/docs/instagram-platform/insights/) | permissions, endpoints, availability | login variant and access level differ |
| Media metrics | [Meta Instagram Media Insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights) | Reel/Story metrics, breakdowns, delay, retention | several fields estimated/in development |
| Account metrics | [Meta Instagram Account Insights](https://developers.facebook.com/docs/instagram-platform/api-reference/instagram-user/insights) | follower/media-product breakdowns | account interval is not per-media attribution; naming inconsistency must be validated live |
| Reel Dashboard | [Instagram Help: Reel insights](https://www.facebook.com/help/instagram/202865988324236) | UI views, watch time, viewers, follows | Dashboard surface is not an API contract |
| Account Dashboard | [Instagram Help: account/content insights](https://www.facebook.com/help/instagram/1533933820244654) | 90-day web range and public-account requirements | visible fields can vary by account type |
| Hashtags | [IG Hashtag Search](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag-search) and [IG Hashtag](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag/) | authorized recent/top discovery | 30 unique hashtag searches per seven days |
| Ranking | [Instagram Ranking Explained](https://about.instagram.com/blog/announcements/instagram-ranking-explained) | surface-specific ranking descriptions | published explanation, not full/current ranking code |
| Experiments | [Trial Reels](https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best/) | non-follower-first test surface | product behavior, not causal guarantee |
| Search trends | [Google Trends FAQ](https://support.google.com/trends/answer/4365533) | normalization and sampling semantics | not absolute volume or a poll |
| Trend method | [Kleinberg, Bursty and Hierarchical Structure in Streams](https://www.cs.cornell.edu/home/kleinber/bhs.pdf) | burst-detection foundation | requires adaptation to heterogeneous sources |
| Matrix | [Chaffey, Content Marketing Matrix](https://www.smartinsights.com/content-management/content-marketing-strategy/the-content-marketing-matrix-new-infographic/) | content/audience mapping | practitioner framework |
| Intent | [Kaushik, See-Think-Do-Care](https://www.kaushik.net/avinash/see-think-do-content-marketing-measurement-business-framework/) | intent and measurement alignment | practitioner framework; journeys need not be linear |
| Diversity | [Carbonell & Goldstein, MMR](https://dl.acm.org/doi/10.1145/290941.291025) | relevance-diversity reranking | similarity and lambda require calibration |
| Scholarly source | [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | searchable publication metadata | completeness/copyright differ by field |
| Biomedical source | [NCBI APIs](https://www.ncbi.nlm.nih.gov/home/develop/api/) | PubMed/PMC discovery | category-specific; usage rules apply |
| Community source | [Reddit developer guidelines](https://developers.reddit.com/docs/guidelines) | authorized community adapter boundary | terms, representativeness, and rate limits |
| Transcription | [OpenAI Whisper](https://github.com/openai/whisper) | multilingual ASR and timestamps | accuracy varies by language/audio; ffmpeg required |
| Shot detection | [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | cut/transition detection | thresholds require fixture calibration |
| Persian OCR | [Tesseract tessdata_best Persian](https://github.com/tesseract-ocr/tessdata_best/blob/main/fas.traineddata) | on-screen Persian text | stylized/animated text can reduce accuracy |
| Persian font | [Vazirmatn](https://github.com/rastikerdar/vazirmatn) | redistributable RTL typography | verify renderer and fallback fonts |
| Image API | [OpenAI image generation guide](https://developers.openai.com/api/docs/guides/image-generation) | generation/edit provider adapter | model availability, cost, and access evolve |
| Codex skills | [OpenAI Build skills](https://developers.openai.com/codex/build-skills) | plugin/skill packaging | host dependencies must be explicit |

