import unittest
from assemble import assess_placement

class PlacementTest(unittest.TestCase):
    def test_placement_requires_release_alignment_and_stability(self):
        self.assertTrue(assess_placement([.50, .0, .075], [.50, .0, .075], .001, 0))
        self.assertFalse(assess_placement([.54, .0, .075], [.50, .0, .075], .001, 0))
        self.assertFalse(assess_placement([.50, .0, .075], [.50, .0, .075], .03, 0))
        self.assertFalse(assess_placement([.50, .0, .075], [.50, .0, .075], .001, 1))

if __name__ == '__main__': unittest.main()
