import unittest
import numpy as np
from work.held_surface_tracker import SurfaceTracker
class SurfaceTrackerTests(unittest.TestCase):
    def test_prediction_expires_and_conflicting_cloud_invalidates_history(self):
        t=SurfaceTracker(2);tool=[.5,.2,.2];a=np.array([[.525,.2,.2]]*10);b=np.array([[.5,.175,.2]]*10);bad=np.array([[.7,.175,.2]]*10)
        self.assertEqual(t.update(a,b,tool)[1],'observed')
        self.assertEqual(t.update([],[],tool)[1],'predicted')
        self.assertEqual(t.update([],[],tool)[1],'predicted')
        self.assertEqual(t.update([],[],tool),(None,'unavailable'))
        self.assertEqual(t.update(a,b,tool)[1],'observed')
        self.assertEqual(t.update(a,bad,tool),(None,'conflict'))
        self.assertEqual(t.update([],[],tool),(None,'unavailable'))
