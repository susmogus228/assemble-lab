import unittest
from assemble import run
from sequence_probe import run as run_figure
from work.controller_v3 import run as run_fast

class SimulationContracts(unittest.TestCase):
    def test_invalid_shape_is_rejected(self):
        with self.assertRaises(ValueError): run(shape='triangle')
    def test_cube_collision_is_simulated_and_both_parts_attempted(self):
        result=run_figure(push=True)
        self.assertGreater(result['push']['cube_contact_steps'], 0)
        self.assertGreater(result['push']['second_displacement_mm'], 5)
        self.assertEqual(len(result['parts']), 2)
    def test_fast_controller_reference_scene_preserves_physical_collision(self):
        result=run_fast(push=True)
        self.assertTrue(result['complete'])
        self.assertGreater(result['push']['cube_contact_steps'], 0)
        self.assertGreater(result['push']['second_displacement_mm'], 5)
    def test_figure_has_recorded_real_poses(self):
        result=run_figure()
        self.assertTrue(result['frames'])
        self.assertEqual(len(result['frames'][0]['parts']),2)
        self.assertEqual(len(result['final_recheck']),2)

if __name__=='__main__': unittest.main()
