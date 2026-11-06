import unittest
from work.held_camera import held_center

class HeldCenterTests(unittest.TestCase):
    def test_surface_offset_and_unrelated_objects(self):
        found=held_center([{'point':[.525,.2,.2],'pixels':30},{'point':[.9,.8,.2],'pixels':30}], [.5,.2,.18])
        self.assertAlmostEqual(found[0],.5)
        self.assertAlmostEqual(found[1],.2)

    def test_ambiguous_missing_and_invalid_are_rejected(self):
        self.assertIsNone(held_center([], [.5,.2,.18]))
        self.assertIsNone(held_center([{'point':[.525,.2,.2]}, {'point':[.53,.21,.2]}], [.5,.2,.18]))
        self.assertIsNone(held_center([{'point':[float('nan'),.2,.2]}], [.5,.2,.18]))
