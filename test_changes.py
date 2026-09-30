import unittest

from backend.change_detection import ChangeThresholds, compare_scenes
from backend.change_detection.matcher import match_objects
from tests.helpers import det


def kinds(report):
    out = {}
    for c in report.changes + report.unchanged:
        out.setdefault(c.type, set()).add(c.label)
    return out


class ChangeDetectionTests(unittest.TestCase):
    def test_spec_example_added_removed_unchanged(self):
        a = [det("charger", .8, .5), det("notebook", .2, .5), det("phone", .5, .5)]
        b = [det("notebook", .2, .5), det("phone", .5, .5), det("bottle", .3, .3)]
        k = kinds(compare_scenes(a, b))
        self.assertEqual(k["removed"], {"charger"})
        self.assertEqual(k["added"], {"bottle"})
        self.assertEqual(k["unchanged"], {"notebook", "phone"})
        self.assertNotIn("moved", k)

    def test_moved_object(self):
        r = compare_scenes([det("notebook", .2, .5)], [det("notebook", .6, .7)])
        self.assertEqual([c.type for c in r.changes], ["moved"])
        self.assertGreater(r.changes[0].displacement, 0.06)

    def test_small_shift_is_unchanged(self):
        r = compare_scenes([det("mouse", .5, .5)], [det("mouse", .52, .51)])
        self.assertEqual(r.count, 0)
        self.assertEqual(len(r.unchanged), 1)

    def test_threshold_is_configurable(self):
        a, b = [det("mouse", .5, .5)], [det("mouse", .53, .5)]
        self.assertEqual(compare_scenes(a, b, ChangeThresholds(move_distance=0.01)).count, 1)
        self.assertEqual(compare_scenes(a, b, ChangeThresholds(move_distance=0.1)).count, 0)

    def test_low_confidence_ignored(self):
        r = compare_scenes([], [det("cup", .5, .5, conf=0.1)])
        self.assertEqual(r.count, 0)

    def test_empty_scenes(self):
        self.assertEqual(compare_scenes([], []).headline, "No changes detected")

    def test_duplicate_class_matches_nearest(self):
        a = [det("cup", .2, .5), det("cup", .8, .5)]
        b = [det("cup", .21, .5), det("cup", .5, .5)]   # right cup moved to centre
        r = compare_scenes(a, b)
        self.assertEqual([c.type for c in r.changes], ["moved"])
        self.assertEqual(len(r.unchanged), 1)

    def test_matcher_pairs_only_same_class(self):
        pairs, oa, ob = match_objects([det("cup", .5, .5)], [det("phone", .5, .5)], ChangeThresholds())
        self.assertEqual((pairs, len(oa), len(ob)), ([], 1, 1))

    def test_headline_counts(self):
        r = compare_scenes([det("a", .1, .1)], [det("b", .9, .9)])
        self.assertEqual(r.headline, "2 changes detected")


if __name__ == "__main__":
    unittest.main()
