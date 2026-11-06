import unittest
from work.held_face_geometry import combine_faces
class FaceGeometryTests(unittest.TestCase):
    def test_visible_edge_can_be_far_from_face_center(self):
        x=[{'point':[.525,.186,.215]}];y=[{'point':[.5,.175,.186]}]
        value=combine_faces(x,y,[.5,.2,.2]);self.assertIsNotNone(value);self.assertAlmostEqual(value[0],.5);self.assertAlmostEqual(value[1],.2)
    def test_rejects_impossible_geometry_height_and_ambiguity(self):
        t=[.5,.2,.2];x=[{'point':[.525,.2,.2]}]
        self.assertIsNone(combine_faces(x,[{'point':[.54,.175,.2]}],t))
        self.assertIsNone(combine_faces(x,[{'point':[.50,.175,.3]}],t))
        self.assertIsNone(combine_faces(x,[{'point':[.5,.175,.2]},{'point':[.51,.18,.2]}],t))
