import unittest
from color_assembly import run
from unittest.mock import patch
class SelectionTest(unittest.TestCase):
    def test_invalid_choices_fail(self):
        for colors in ([],['green'],['red','red']):
            with self.assertRaises(ValueError):run(colors)
    def test_missing_detection_cannot_trigger_grasp(self):
        with patch('color_assembly.camera_snapshot',return_value={'image':'','detections':{}}):
            result=run(['red'])
        self.assertFalse(result['complete'])
        self.assertEqual(result['parts'],[])
        self.assertIn('did not detect',result['failure'])
    def test_invalid_clutter_is_rejected(self):
        for count in (-1,5):
            with self.assertRaises(ValueError):run(['red'],extra_count=count)
    def test_invalid_feedback_is_rejected(self):
        with self.assertRaises(ValueError):run(['red'],feedback='unknown')
    def test_clutter_frames_include_all_cubes(self):
        result=run(['blue'],extra_count=2)
        self.assertEqual(len(result['colors']),4)
        self.assertEqual(len(result['frames'][0]['parts']),4)
        self.assertTrue(result['inspections'][0]['laser']['hit'])
        self.assertIn('green',result['unselected_displacement_mm'])
    def test_same_red_requires_two_visible_instances(self):
        one={'image':'','detections':{'red':{'point':[.4,-.1,.05]}},'instances':{'red':[{'point':[.4,-.1,.05]}]}}
        with patch('color_assembly.camera_snapshot',return_value=one):
            result=run(['red2'],extra_count=1,same_red=True)
        self.assertFalse(result['complete'])
        self.assertEqual(result['parts'],[])
    def test_physically_occluded_same_color_fails_closed(self):
        result=run(['red2'],extra_count=1,same_red=True,occlude=True,feedback='sensor')
        self.assertEqual(result['parts'],[])
        self.assertFalse(result['complete'])
        self.assertIn('did not detect',result['failure'])
    def test_select_second_red_keeps_first_stationary(self):
        result=run(['red2'],extra_count=1,same_red=True,feedback='sensor',retry=False)
        self.assertEqual([item['color'] for item in result['parts']],['red2'])
        self.assertLess(result['unselected_displacement_mm']['red'],5)
        self.assertTrue(result['verification'][0]['visible'])
    def test_single_color_uses_rgbd_and_ray(self):
        result=run(['blue'])
        self.assertEqual(result['selected'],['blue'])
        self.assertIn('blue',result['inspections'][0]['detections'])
        self.assertTrue(result['inspections'][0]['laser']['hit'])
        self.assertTrue(all(part['color']=='blue' for part in result['parts']))
        self.assertIn('red',result['unselected_displacement_mm'])
if __name__=='__main__':unittest.main()
