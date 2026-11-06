import unittest
from sequence_probe import evaluate_figure

def pose(x,y,z,yaw=0):
    import math
    return {'position':[x,y,z], 'yaw':yaw, 'tilt':0, 'speed':0, 'robot_contacts':0, 'supported':True}
class FigureCriteriaTests(unittest.TestCase):
    def test_bad_relative_alignment_fails_even_if_individual_targets_pass(self):
        states=[pose(.56,.10,.05),pose(.565,.10,.10)]
        result=evaluate_figure(states, [[.56,.10,.05],[.56,.10,.10]],'tower')
        self.assertFalse(result['success'])
    def test_yaw_and_support_are_required(self):
        states=[pose(.56,.10,.05),pose(.56,.10,.10,4)]
        self.assertFalse(evaluate_figure(states,[[.56,.10,.05],[.56,.10,.10]],'tower')['success'])
        states[1]['yaw']=0; states[1]['supported']=False
        self.assertFalse(evaluate_figure(states,[[.56,.10,.05],[.56,.10,.10]],'tower')['success'])
    def test_good_alignment(self):
        states=[pose(.56,.10,.05),pose(.561,.10,.10,1)]
        self.assertTrue(evaluate_figure(states,[[.56,.10,.05],[.56,.10,.10]],'tower')['success'])
if __name__=='__main__':unittest.main()
