import random
import unittest
from unittest.mock import patch
import pybullet as p
from work.held_tracking_geometry import HeldTracker
from work.color_tower_reobserve_v3 import run
class ReobserveCollisionTests(unittest.TestCase):
    def test_unexpected_contact_stops_recovery_before_upper_release(self):
        orig_update=HeldTracker.update;orig_contacts=p.getContactPoints;calls=[]
        def trigger_once(self,x,y,tool):
            calls.append(1)
            if len(calls)==1:return None,'conflict'
            return orig_update(self,x,y,tool)
        def obstacle(*args,**kwargs):
            if kwargs.get('bodyA')==1 and 'bodyB' not in kwargs:return [(0,1,999)]
            return orig_contacts(*args,**kwargs)
        rng=random.Random(1013);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
        with patch.object(HeldTracker,'update',trigger_once),patch.object(p,'getContactPoints',obstacle):
            result=run(['red','blue'],scene_seed=1013,source_offset=offset,extra_count=2,feedback='sensor',retry=True)
        self.assertEqual(result['failure'],'Unexpected contact during camera recovery')
        self.assertFalse(result['success'])
        self.assertFalse(any(f['part_number']==2 and f['stage']=='release' for f in result['frames']))
