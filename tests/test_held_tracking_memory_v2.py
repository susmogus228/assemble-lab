import unittest
from work.held_tracking_memory_v2 import HeldTracker
class MultiViewProductionTrackerTests(unittest.TestCase):
    def test_uses_recent_observation_for_only_two_missing_samples(self):
        t=HeldTracker(2); tool=[.5,.2,.18];x=[{'point':[.525,.197,.2]}];y=[{'point':[.512,.175,.2]}]
        self.assertEqual(t.update(x,y,tool)[1],'observed')
        self.assertEqual(t.update([],[],tool)[1],'predicted')
        self.assertEqual(t.update([],[],tool)[1],'predicted')
        self.assertEqual(t.update([],[],tool),(None,'unavailable'))
    def test_genuine_cross_view_conflict_invalidates_history(self):
        t=HeldTracker();tool=[.5,.2,.18];x=[{'point':[.525,.2,.2]}];y=[{'point':[.5,.175,.2]}]
        self.assertEqual(t.update(x,y,tool)[1],'observed')
        self.assertEqual(t.update(x,[{'point':[.5,.15,.2]}],tool),(None,'conflict'))
        self.assertEqual(t.update([],[],tool),(None,'unavailable'))
