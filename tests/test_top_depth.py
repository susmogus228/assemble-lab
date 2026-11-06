import unittest
from work.color_camera_candidate import run
class TopDepthTests(unittest.TestCase):
    def test_reference_red_scene_uses_vision_and_contact(self):
        r=run(['red'],scene_seed=1,source_offset=(-.01,.005),extra_count=2,feedback='sensor',retry=True)
        self.assertTrue(r['success'])
        self.assertTrue(r['verification'][0]['push_contact'])
        self.assertTrue(r['inspections'][0]['laser']['hit'])
    def test_ambiguous_overlapping_cubes_stop(self):
        r=run(['red2'],extra_count=1,same_red=True,occlude=True,feedback='sensor',retry=True)
        self.assertEqual(r['parts'],[])
        self.assertFalse(r['success'])
