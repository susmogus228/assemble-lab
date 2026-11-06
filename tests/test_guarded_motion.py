import unittest
from unittest.mock import patch
from work.color_tower_guarded_v1 import run

class GuardedMotionTests(unittest.TestCase):
    def test_stops_if_held_camera_is_lost(self):
        with patch('work.color_tower_guarded_v1.side_snapshot', return_value={}):
            result=run(['red','blue'],feedback='sensor',retry=True)
        self.assertIn('camera observation lost', result['failure'])
        self.assertFalse(result['success'])
        self.assertFalse(result['hold_checks'][-1]['accepted'])
        self.assertFalse(any(f['stage']=='release' for f in result['frames']))

    def test_stops_if_finger_contacts_are_lost(self):
        with patch('work.color_tower_guarded_v1.p.getContactPoints', return_value=[]):
            result=run(['red','blue'],feedback='sensor',retry=True)
        self.assertIn('Grasp', result['failure'])
        self.assertFalse(result['success'])
        self.assertFalse(result['hold_checks'][-1]['bilateral'])
        self.assertFalse(any(f['stage']=='release' for f in result['frames']))
