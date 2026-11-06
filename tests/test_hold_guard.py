import unittest
from work.hold_guard import stable_grasp, bounded_step

class HoldGuardTests(unittest.TestCase):
    def test_two_sided_contact_must_be_sustained(self):
        self.assertTrue(stable_grasp([(1,1),(1,1),(0,0)]))
        self.assertFalse(stable_grasp([(1,0),(0,1),(1,0)]))
        self.assertFalse(stable_grasp([]))
        self.assertFalse(stable_grasp([(float('nan'),1)]*3))
    def test_camera_loss_never_generates_a_motion(self):
        self.assertIsNone(bounded_step(None, [0,0], [1,1]))
        self.assertEqual(bounded_step([0,0], [0,0], [1,-1]), (.002,-.002))
        self.assertEqual(bounded_step([.001,0], [0,0], [0,0]), (-.00025,0))
