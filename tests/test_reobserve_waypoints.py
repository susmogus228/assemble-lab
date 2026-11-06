import unittest
from work.reobserve_policy_v2 import reobserve_targets
class ReobserveWaypointsTests(unittest.TestCase):
    def test_three_bounded_high_waypoints(self):
        paths=reobserve_targets([.45,-.25,.20]);self.assertEqual(len(paths),3)
        for p in paths:
            self.assertLessEqual(abs(p[0]-.45),.020001);self.assertLessEqual(abs(p[1]+.25),.020001);self.assertEqual(p[2],.20)
    def test_no_unsafe_waypoints(self):
        self.assertEqual(reobserve_targets([.45,-.25,.12]),[])
        self.assertEqual(reobserve_targets([.8,-.25,.20]),[])
