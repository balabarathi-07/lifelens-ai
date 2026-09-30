import unittest

import cv2
import numpy as np

from backend.ai.detector import Detector
from backend.ai.inference import DemoColorInference, InferenceEngine
from backend.utils.helpers import extract_object_name
from backend.vision.postprocessing import decode_yolo
from backend.vision.preprocessing import InvalidImageError, decode_image, letterbox
from scripts.demo_scenes import demo_scene_bytes


class DetectionTests(unittest.TestCase):
    def test_demo_scene_detection(self):
        dets = Detector(DemoColorInference()).detect(decode_image(demo_scene_bytes(1)))
        self.assertIsNone(dets.error)
        self.assertEqual({d.label for d in dets.detections}, {"notebook", "charger", "phone", "bottle"})

    def test_invalid_image_rejected(self):
        with self.assertRaises(InvalidImageError):
            decode_image(b"not an image")
        with self.assertRaises(InvalidImageError):
            decode_image(b"")

    def test_engine_failure_does_not_crash(self):
        class Broken(InferenceEngine):
            def detect(self, image):
                raise RuntimeError("boom")
        r = Detector(Broken()).detect(np.zeros((64, 64, 3), np.uint8))
        self.assertIn("boom", r.error)

    def test_no_engine_message(self):
        self.assertIn("No inference engine", Detector(None).detect(np.zeros((64, 64, 3), np.uint8)).error)

    def test_empty_detection_warns(self):
        r = Detector(DemoColorInference()).detect(np.full((200, 200, 3), 48, np.uint8))
        self.assertEqual(r.detections, [])
        self.assertIsNotNone(r.warning)

    def test_yolo_decode_round_trip(self):
        img = np.zeros((480, 640, 3), np.uint8)
        _, scale, pad = letterbox(img, 640)
        # one box centred at (320, 320) in letterboxed space, 100x100, class 3 with score .9
        out = np.zeros((1, 4 + 5, 1), np.float32)
        out[0, :4, 0] = [320, 320, 100, 100]
        out[0, 4 + 3, 0] = 0.9
        dets = decode_yolo(out, ["a", "b", "c", "d", "e"], scale, pad, img.shape, 0.35, 0.45)
        self.assertEqual(len(dets), 1)
        self.assertEqual(dets[0].label, "d")
        cx, cy = dets[0].center
        self.assertAlmostEqual(cx, 0.5, places=2)
        self.assertAlmostEqual(cy, 0.5, places=2)

    def test_query_parsing(self):
        self.assertEqual(extract_object_name("Where was my charger?"), "charger")
        self.assertEqual(extract_object_name("water bottle"), "water bottle")


if __name__ == "__main__":
    unittest.main()
