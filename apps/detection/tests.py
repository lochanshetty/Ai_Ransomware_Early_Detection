"""CRDS detection pipeline tests."""

from django.db.models.signals import post_save
from django.test import TestCase

from apps.detection.models import SecurityLog, Threat
from apps.detection.services.hybrid_scorer import score_event
from apps.detection.services.pipeline import analyze_log
from apps.detection.signals import run_detection_pipeline
from feature_extraction.aggregator import FeatureAggregator


class DetectionPipelineTests(TestCase):
    def setUp(self):
        self.aggregator = FeatureAggregator(window_seconds=20.0)
        post_save.disconnect(run_detection_pipeline, sender=SecurityLog)

    def tearDown(self):
        post_save.connect(run_detection_pipeline, sender=SecurityLog)

    def test_benign_log_below_threshold(self):
        log = SecurityLog.objects.create(
            source="test",
            event_type="file_event",
            action="modify",
            file_path="/tmp/test.txt",
            message="Benign modification",
            metadata={"file_mod_count": 1, "process_known": True},
        )
        result = analyze_log(log)
        self.assertIn("confidence_score", result)
        self.assertFalse(result["is_suspicious"] or result.get("threat_id") is not None)

    def test_burst_modifications_trigger_threat(self):
        log = SecurityLog.objects.create(
            source="test",
            event_type="file_event",
            action="modify",
            file_path="/tmp/encrypted.locked",
            message="Burst modifications",
            metadata={
                "file_mod_count": 12,
                "window_seconds": 10,
                "files_modified_per_second": 5.0,
                "entropy_delta": 4.0,
                "process_known": False,
                "rename_ratio": 0.8,
            },
        )
        result = analyze_log(log)
        self.assertTrue(result["is_suspicious"])
        self.assertIsNotNone(result["threat_id"])
        threat = Threat.objects.get(id=result["threat_id"])
        self.assertGreater(threat.confidence_score, 0.5)

    def test_hybrid_scorer_returns_explanation(self):
        log = SecurityLog.objects.create(
            source="test",
            event_type="file_event",
            action="rename",
            file_path="/tmp/file.locked",
            message="Rename event",
            metadata={"file_mod_count": 8, "entropy_delta": 3.5},
        )
        features = self.aggregator.build(
            file_path="/tmp/file.locked",
            action="rename",
            previous_path="/tmp/file.txt",
            process_known=False,
        )
        score = score_event(log, features, honeypot_hit=False)
        self.assertIn("explanation", score.to_dict())
        self.assertGreaterEqual(score.total_score, 0.0)
