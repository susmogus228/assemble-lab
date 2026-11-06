import random
import unittest
from unittest.mock import patch
from work.color_tower_multiview_v5 import run as baseline
from work.color_tower_reobserve_v3 import run as candidate
from work.held_tracking_geometry import HeldTracker

def case(fn):
    rng=random.Random(1013);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
    return fn(['red','blue'],scene_seed=1013,source_offset=offset,extra_count=2,feedback='sensor',retry=True)

class ReobserveIntegrationTests(unittest.TestCase):
    def test_reobservation_is_guarded_and_triggered(self):
        update=HeldTracker.update;calls=[]
        def trigger_once(self,x,y,tool):
            calls.append(1)
            if len(calls)==1:return None,'conflict'
            return update(self,x,y,tool)
        with patch.object(HeldTracker,'update',trigger_once):result=case(candidate)
        self.assertTrue(result['reobservations'])
        self.assertTrue(any(f['stage']=='camera recovery' for f in result['frames']))
        self.assertNotEqual(result['failure'],'Unexpected contact during camera recovery')
    def test_unmodified_laser_sequence_matches_baseline(self):
        old=case(baseline);new=case(candidate)
        old_scan=[f for f in old['frames'] if f['stage']=='laser scan' and f['part_number']==1]
        new_scan=[f for f in new['frames'] if f['stage']=='laser scan' and f['part_number']==1]
        self.assertEqual(len(old_scan),len(new_scan))
        for a,b in zip(old_scan,new_scan):
            for x,y in zip(a['links'][12][0],b['links'][12][0]):self.assertAlmostEqual(x,y,places=6)
