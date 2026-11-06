import random
import unittest
from work.color_tower_v4 import run

class TowerRetrySafetyTests(unittest.TestCase):
    def test_no_push_on_stacked_upper_cube(self):
        rng = random.Random(307)
        offset = (round(rng.uniform(-.015, .015), 4), round(rng.uniform(-.01, .01), 4))
        result = run(['red', 'blue'], scene_seed=307, source_offset=offset, feedback='sensor', retry=True)
        upper = result['verification'][1]
        self.assertGreater(upper['xy_error_mm'], 6)
        self.assertFalse(upper['retried'])
        self.assertFalse(any(f['part_number'] == 2 and f['stage'].startswith('correct') for f in result['frames']))

if __name__ == '__main__':
    unittest.main()
