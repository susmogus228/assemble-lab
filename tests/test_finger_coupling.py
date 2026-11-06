import unittest
from unittest.mock import patch
import pybullet as p
from work.single_grasp_coupling_probe import run

class CouplingTests(unittest.TestCase):
    def test_constraint_joins_fingers_not_object(self):
        create=p.createConstraint
        with patch.object(p,'createConstraint', wraps=create) as spy:
            result=run((.48,-.14),'forward',False,True)
        args=spy.call_args.args
        self.assertEqual(spy.call_count,1)
        self.assertEqual(args[0],args[2])
        self.assertEqual((args[1],args[3],args[4]),(9,10,p.JOINT_GEAR))
        self.assertTrue(result['retained'])
        self.assertLess(result['peak_slip_mm'],2)
