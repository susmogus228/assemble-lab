import random
import unittest
from work.color_tower_base_camera_v1 import run

class RealLostGraspScenarioTests(unittest.TestCase):
    def test_cluttered_scene_stops_before_upper_release(self):
        seed=811
        rng=random.Random(seed)
        offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
        result=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=2,feedback='sensor',retry=True)
        self.assertFalse(result['success'])
        self.assertIn('lost during lift',result['failure'])
        self.assertFalse(any(f['part_number']==2 and f['stage']=='release' for f in result['frames']))
