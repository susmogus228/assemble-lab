import unittest
import numpy as np
from work.held_surface_cloud import estimate_center
class SurfaceCloudTests(unittest.TestCase):
    def test_reconstructs_cube_from_two_visible_faces(self):
        a=np.array([[.525,.18+.004*i,.18+.002*i] for i in range(10)])
        b=np.array([[.48+.004*i,.175,.18+.002*i] for i in range(10)])
        p=estimate_center(a,b,[.5,.2,.2]);self.assertIsNotNone(p);self.assertAlmostEqual(p[0],.5,places=3);self.assertAlmostEqual(p[1],.2,places=3)
    def test_rejects_missing_and_incompatible_clouds(self):
        a=np.array([[.525,.2,.2]]*10);b=np.array([[.7,.175,.2]]*10)
        self.assertIsNone(estimate_center(a,b,[.5,.2,.2]))
        self.assertIsNone(estimate_center(a,np.empty((0,3)),[.5,.2,.2]))
    def test_rejects_cloud_whose_points_do_not_fit_proposed_cube(self):
        x=np.array([[.525,.175+i*.0025,.19] for i in range(21)])
        erroneous_y=np.array([[.5,.155,.19]]*20)
        self.assertIsNone(estimate_center(x,erroneous_y,[.5,.2,.2]))
