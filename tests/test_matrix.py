import unittest

from instagram_content_intelligence.matrix import ContentCandidate, MatrixConfig, select_portfolio


DIMENSIONS = {
    "audience": "segment-a",
    "job": "learn",
    "intent_stage": "see",
    "pillar": "education",
    "objective": "reach",
    "surface": "reel",
    "format": "explainer",
    "angle": "myth",
    "evidence": "primary-source",
    "narrative": "gap-proof-payoff",
    "cta": "save",
    "lifecycle": "evergreen",
}


def candidate(identifier, pillar, objective, score, embedding):
    dimensions = dict(DIMENSIONS, pillar=pillar, objective=objective)
    scores = {key: score for key in (
        "strategic_fit", "audience_relevance", "platform_fit", "evidence_strength",
        "novelty", "trend_opportunity", "historical_prior", "feasibility", "conversion_clarity"
    )}
    return ContentCandidate(identifier, identifier, dimensions, scores, embedding=embedding)


class MatrixTests(unittest.TestCase):
    def test_caps_and_coverage(self):
        result = select_portfolio(
            [
                candidate("a", "education", "reach", 0.95, (1, 0)),
                candidate("b", "education", "reach", 0.94, (0.98, 0.02)),
                candidate("c", "trust", "engage", 0.85, (0, 1)),
                candidate("d", "conversion", "convert", 0.80, (-1, 0)),
            ],
            MatrixConfig(
                portfolio_size=3,
                max_per_dimension_value={"pillar": 1},
                min_coverage={"objective": 3, "pillar": 3},
            ),
        )
        self.assertTrue(result["complete"])
        self.assertEqual({item["id"] for item in result["selected"]}, {"a", "c", "d"})

    def test_missing_dimension_fails_explicitly(self):
        bad = candidate("bad", "x", "y", 0.8, ())
        bad.dimensions.pop("cta")
        with self.assertRaisesRegex(ValueError, "cta"):
            select_portfolio([bad], MatrixConfig(portfolio_size=1))

    def test_infeasible_coverage_is_reported(self):
        result = select_portfolio(
            [candidate("a", "same", "same", 0.9, ())],
            MatrixConfig(portfolio_size=1, min_coverage={"objective": 2}),
        )
        self.assertFalse(result["complete"])
        self.assertEqual(result["unmet_coverage"]["objective"], 1)


if __name__ == "__main__":
    unittest.main()

