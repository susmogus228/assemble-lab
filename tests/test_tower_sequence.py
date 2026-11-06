import unittest
from work.color_tower_v2 import run
class TowerSequenceTests(unittest.TestCase):
    def test_base_observed_before_upper_laser(self):
        r=run(['red','blue'],scene_seed=2,source_offset=(.0137,.009),extra_count=4,feedback='sensor',retry=True)
        stages=[f['stage'] for f in r['frames'] if f['part_number']==2]
        self.assertIn('base observation',stages)
        self.assertIn('laser scan',stages)
        self.assertLess(stages.index('base observation'),stages.index('laser scan'))
