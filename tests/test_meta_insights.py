import unittest

from instagram_content_intelligence.meta_insights import MetaClientConfig, MetaInsightsClient, redact_meta_url


class MetaInsightsTests(unittest.TestCase):
    def test_non_meta_host_is_rejected(self):
        with self.assertRaises(ValueError):
            MetaClientConfig("secret", host="https://example.test")

    def test_reel_metric_contract_rejects_profile_activity(self):
        client = MetaInsightsClient(MetaClientConfig("secret"), lambda url, timeout: {"data": []})
        with self.assertRaisesRegex(ValueError, "profile_activity"):
            client.media_insights("1", ["reach", "profile_activity"], "REELS")

    def test_url_token_can_be_redacted(self):
        self.assertNotIn("secret", redact_meta_url("https://example.test/x?metric=reach&access_token=secret"))

    def test_normalized_metric_has_api_scope(self):
        captured = {}

        def transport(url, timeout):
            captured["url"] = url
            return {"data": [{"name": "reach", "period": "lifetime", "values": [{"value": 10}]}]}

        result = MetaInsightsClient(MetaClientConfig("secret"), transport).media_insights("99", ["reach"], "REELS")
        provenance = result["metrics"][0]["provenance"]
        self.assertEqual(provenance["kind"], "meta_api")
        self.assertEqual(provenance["scope"], "single_media")
        self.assertIn("metric=reach", captured["url"])


if __name__ == "__main__":
    unittest.main()
