import tempfile
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient
    HAVE_FASTAPI = True
except Exception:  # FastAPI/httpx not installed
    HAVE_FASTAPI = False

from backend.config import Settings


@unittest.skipUnless(HAVE_FASTAPI, "fastapi + httpx not installed (pip install -r requirements.txt)")
class ApiTests(unittest.TestCase):
    def setUp(self):
        from backend.main import create_app
        self.tmp = tempfile.TemporaryDirectory()
        s = Settings()
        s.data_dir = Path(self.tmp.name)
        s.model_path = Path(self.tmp.name) / "missing.onnx"
        self.client = TestClient(create_app(s))

    def tearDown(self):
        self.client.app.state.service.db.close()
        self.tmp.cleanup()

    def test_health_and_system(self):
        self.assertEqual(self.client.get("/api/health").json(), {"status": "ok"})
        sysinfo = self.client.get("/api/system").json()
        self.assertTrue(sysinfo["local_processing"])
        self.assertIn(sysinfo["inference_backend"], ("CPU", "GPU", "NPU"))

    def test_demo_flow(self):
        self.assertEqual(self.client.post("/api/scenes/demo/1").status_code, 200)
        self.assertEqual(self.client.post("/api/scenes/demo/2").status_code, 200)
        r = self.client.post("/api/compare", json={}).json()
        self.assertEqual(r["count"], 3)
        found = self.client.get("/api/search/object/charger").json()
        self.assertTrue(found["found"])
        self.assertEqual(found["location"], "Right side of desk")
        self.assertEqual(self.client.get("/api/scenes/1/image").status_code, 200)
        self.assertEqual(len(self.client.get("/api/timeline").json()["events"]), 5)

    def test_errors(self):
        self.assertEqual(self.client.post("/api/scenes/capture", content=b"junk").status_code, 422)
        self.assertEqual(self.client.post("/api/compare", json={}).status_code, 409)
        self.assertEqual(self.client.get("/api/scenes/99").status_code, 404)

    def test_delete_memory(self):
        self.client.post("/api/scenes/demo/1")
        self.assertEqual(self.client.delete("/api/memory").json()["deleted_scenes"], 1)
        self.assertEqual(self.client.get("/api/scenes").json()["scenes"], [])


if __name__ == "__main__":
    unittest.main()
