import tempfile
import unittest
from pathlib import Path

from backend.config import Settings
from backend.services import LifeLensService, UserError
from scripts.demo_scenes import demo_scene_bytes


class ServiceFlowTests(unittest.TestCase):
    """End-to-end demo scenario without HTTP (runs even if FastAPI is not installed)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        s = Settings()
        s.data_dir = Path(self.tmp.name)
        s.model_path = Path(self.tmp.name) / "missing.onnx"
        self.svc = LifeLensService(s)

    def tearDown(self):
        self.svc.db.close()
        self.tmp.cleanup()

    def test_demo_scenario(self):
        self.svc.capture_bytes(demo_scene_bytes(1))
        self.svc.capture_bytes(demo_scene_bytes(2))
        r = self.svc.compare()
        types = {(c["type"], c["label"]) for c in r["changes"]}
        self.assertEqual(types, {("moved", "notebook"), ("removed", "charger"), ("added", "headphones")})
        hit = self.svc.search_object("Where was my charger?")
        self.assertEqual((hit["scene_id"], hit["location"]), (1, "Right side of desk"))
        self.assertEqual(len(self.svc.timeline()), 5)

    def test_compare_needs_two_scenes(self):
        with self.assertRaises(UserError):
            self.svc.compare()

    def test_bad_upload(self):
        with self.assertRaises(UserError):
            self.svc.capture_bytes(b"xyz")

    def test_unknown_object(self):
        self.assertFalse(self.svc.search_object("teapot")["found"])

    def test_system_reports_real_backend(self):
        info = self.svc.system_info()
        self.assertEqual(info["inference_backend"], "CPU")
        self.assertTrue(info["local_processing"])
        self.assertIn("hardware validation required", info["npu_status"])


if __name__ == "__main__":
    unittest.main()
