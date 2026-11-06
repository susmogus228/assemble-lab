import unittest
from work.reobserve_policy import reobserve_target, has_unexpected_contact
class ReobservePolicyTests(unittest.TestCase):
    def test_never_moves_near_surface_or_outside_workspace(self):
        self.assertIsNone(reobserve_target([.45,-.25,.12]))
        self.assertIsNone(reobserve_target([.8,-.25,.20]))
        target=reobserve_target([.45,-.25,.20]); self.assertAlmostEqual(target[0],.47);self.assertAlmostEqual(target[1],-.23);self.assertAlmostEqual(target[2],.20)
    def test_detects_contact_with_anything_except_grasped_object_or_self(self):
        self.assertFalse(has_unexpected_contact([{'body':5},{'body':1}],1,5))
        self.assertTrue(has_unexpected_contact([{'body':5},{'body':7}],1,5))

