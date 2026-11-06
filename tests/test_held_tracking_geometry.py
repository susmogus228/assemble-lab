import unittest
from work.held_tracking_geometry import HeldTracker
class GeometryTrackerTests(unittest.TestCase):
    def test_predictions_expire_after_two_samples(self):
        t=HeldTracker(2);tool=[.5,.2,.2];x=[{'point':[.525,.197,.21]}];y=[{'point':[.499,.175,.2]}]
        self.assertEqual(t.update(x,y,tool)[1],'observed')
        self.assertEqual(t.update([],[],tool)[1],'predicted')
        self.assertEqual(t.update([],[],tool)[1],'predicted')
        self.assertEqual(t.update([],[],tool),(None,'unavailable'))
    def test_impossible_depth_invalidates_previous_estimate(self):
        t=HeldTracker();tool=[.5,.2,.2];x=[{'point':[.525,.2,.2]}];y=[{'point':[.5,.175,.2]}]
        self.assertEqual(t.update(x,y,tool)[1],'observed')
        self.assertEqual(t.update(x,[{'point':[.5,.175,.27]}],tool),(None,'conflict'))
        self.assertEqual(t.update([],[],tool),(None,'unavailable'))

