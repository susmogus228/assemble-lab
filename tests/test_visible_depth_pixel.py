import unittest
import numpy as np
from work.visible_depth_pixel import nearest_visible_pixel
class VisibleDepthPixelTests(unittest.TestCase):
    def test_selects_real_color_pixel_not_occluding_hand(self):
        a=np.zeros((9,9,3),dtype=np.uint8);a[4,6]=[250,0,0]
        self.assertEqual(nearest_visible_pixel(a,'red',4,4,3),(6,4))
    def test_returns_none_when_color_is_missing_or_too_far(self):
        a=np.zeros((9,9,3),dtype=np.uint8);a[0,0]=[250,0,0]
        self.assertIsNone(nearest_visible_pixel(a,'red',4,4,2))
        self.assertIsNone(nearest_visible_pixel(a,'blue',4,4,8))
