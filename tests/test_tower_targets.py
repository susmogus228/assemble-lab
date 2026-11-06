import unittest
from tower_targets import choose_base_observation
class TowerTargetTests(unittest.TestCase):
    def test_valid_base(self):
        d=choose_base_observation([{'point':[.559,.101,.075]}],[.56,.10],.035)
        self.assertEqual(d['point'][:2],[.559,.101])
    def test_ambiguous_and_missing_base_rejected(self):
        self.assertIsNone(choose_base_observation([], [.56,.10],.035))
        self.assertIsNone(choose_base_observation([{'point':[.56,.10,.075]},{'point':[.57,.10,.075]}],[.56,.10],.035))
        self.assertIsNone(choose_base_observation([{'point':[.4,-.2,.05]}],[.56,.10],.035))
