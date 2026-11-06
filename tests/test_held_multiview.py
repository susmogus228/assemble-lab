import unittest
from work.held_camera_multiview import combine_centers
class MultiViewTests(unittest.TestCase):
    def test_uses_x_face_for_x_y_face_for_y(self):
        x=[{'point':[.525,.197,.20]}];y=[{'point':[.499,.175,.20]}]
        result=combine_centers(x,y,[.5,.2,.18]); self.assertAlmostEqual(result[0],.5); self.assertAlmostEqual(result[1],.2)
    def test_rejects_absent_ambiguous_or_disagreeing_views(self):
        x=[{'point':[.525,.2,.20]}]
        self.assertIsNone(combine_centers(x,[],[.5,.2,.18]))
        self.assertIsNone(combine_centers(x,[{'point':[.50,.15,.2]}],[.5,.2,.18]))
        self.assertIsNone(combine_centers(x,[{'point':[.50,.175,.2]},{'point':[.51,.18,.2]}],[.5,.2,.18]))

