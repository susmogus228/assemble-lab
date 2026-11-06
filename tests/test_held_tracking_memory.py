import unittest
from work.held_tracking_memory import HeldTracker
class HeldTrackerTests(unittest.TestCase):
    def test_tracks_from_last_dual_observation_with_bounded_age(self):
        tracker=HeldTracker(max_missing=2);tool=[.5,.2,.18]
        x=[{'point':[.525,.197,.20]}];y=[{'point':[.499,.175,.20]}]
        self.assertIsNotNone(tracker.update(x,y,tool)[0])
        self.assertAlmostEqual(tracker.update([],[],[.501,.2,.18])[0][0],.501)
        self.assertEqual(tracker.update([],[],[.502,.2,.18])[1],'predicted')
        self.assertEqual(tracker.update([],[],tool),(None,'unavailable'))
    def test_disagreeing_or_ambiguous_views_never_use_old_estimate(self):
        tracker=HeldTracker();tool=[.5,.2,.18];x=[{'point':[.525,.2,.2]}];y=[{'point':[.5,.175,.2]}]
        tracker.update(x,y,tool)
        self.assertEqual(tracker.update(x,[{'point':[.5,.15,.2]}],tool),(None,'conflict'))
        self.assertEqual(tracker.update([],[],tool),(None,'unavailable'))
