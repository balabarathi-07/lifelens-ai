import tempfile
import unittest
from pathlib import Path

import numpy as np

from backend.memory.database import Database
from backend.memory.repository import SceneRepository
from backend.vision.spatial import describe_location
from tests.helpers import det


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "t.db")
        self.repo = SceneRepository(self.db, Path(self.tmp.name) / "snaps")
        self.img = np.zeros((120, 160, 3), np.uint8)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def add(self, dets):
        return self.repo.add_scene(self.img, dets, "CPU", "test", 5.0)

    def test_store_and_read_scene(self):
        sid = self.add([det("phone", .5, .5)])
        s = self.repo.get_scene(sid)
        self.assertEqual(s["object_count"], 1)
        self.assertEqual(s["objects"][0]["label"], "phone")
        self.assertTrue(self.repo.snapshot_path(sid).exists())

    def test_last_seen_returns_latest_occurrence(self):
        self.add([det("charger", .8, .5)])
        s2 = self.add([det("charger", .2, .2)])
        self.add([det("phone", .5, .5)])
        hit = self.repo.find_last_seen("charger")
        self.assertEqual(hit["scene_id"], s2)
        self.assertEqual(hit["location"], "Upper-left area")
        self.assertFalse(hit["in_latest_scene"])

    def test_last_seen_alias_and_missing(self):
        self.add([det("cell phone", .5, .5)])
        self.assertIsNotNone(self.repo.find_last_seen("phone"))
        self.assertIsNone(self.repo.find_last_seen("charger"))

    def test_delete_all_removes_rows_and_files(self):
        sid = self.add([det("phone", .5, .5)])
        path = self.repo.snapshot_path(sid)
        self.assertEqual(self.repo.delete_all(), 1)
        self.assertEqual(self.repo.count(), 0)
        self.assertFalse(path.exists())
        self.assertEqual(self.db.conn.execute("SELECT COUNT(*) FROM objects").fetchone()[0], 0)

    def test_latest_two(self):
        self.assertIsNone(self.repo.latest_two())
        a, b = self.add([]), self.add([])
        self.assertEqual(self.repo.latest_two(), (b, a))

    def test_location_phrases(self):
        self.assertEqual(describe_location(.8, .5), "Right side of desk")
        self.assertEqual(describe_location(.5, .5), "Center area")
        self.assertEqual(describe_location(.1, .1), "Upper-left area")
        self.assertEqual(describe_location(.5, .9), "Lower-center area")


if __name__ == "__main__":
    unittest.main()
