import unittest
from work.color_push_candidate import run
class PushCandidateTests(unittest.TestCase):
    def test_tuned_scene_uses_real_contact_and_reduces_error(self):
        result=run(['blue'],feedback='sensor',retry=True)
        self.assertTrue(result['verification'][0]['push_contact'])
        self.assertTrue(result['success'])
        self.assertLess(result['unselected_displacement_mm']['red'],5)
    def test_occluded_red_stops_without_moving(self):
        result=run(['red2'],extra_count=1,same_red=True,occlude=True,feedback='sensor',retry=True)
        self.assertFalse(result['success'])
        self.assertEqual(result['parts'],[])
