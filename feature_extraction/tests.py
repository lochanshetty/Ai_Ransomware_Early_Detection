"""Feature extraction unit tests."""

from django.test import SimpleTestCase

from feature_extraction.aggregator import FEATURE_NAMES, FeatureAggregator
from feature_extraction.entropy import shannon_entropy


class FeatureExtractionTests(SimpleTestCase):
    def test_feature_vector_has_expected_dimensions(self):
        aggregator = FeatureAggregator(window_seconds=20.0)
        vector = aggregator.build(
            file_path="",
            action="modify",
            process_known=True,
        )
        self.assertEqual(len(vector.names), len(FEATURE_NAMES))
        self.assertEqual(len(vector.as_array()), len(FEATURE_NAMES))

    def test_shannon_entropy_bounds(self):
        low = shannon_entropy(b"aaaaaaa")
        high = shannon_entropy(bytes(range(256)))
        self.assertLess(low, high)
        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 8.0)
