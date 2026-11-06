import math
import unittest
import pybullet as p
from work.base_camera_highres import camera_snapshot

class BaseCameraTests(unittest.TestCase):
    def setUp(self):
        self.client=p.connect(p.DIRECT)
    def tearDown(self):
        p.disconnect(self.client)
    def test_detects_base_and_separate_same_color_distractor(self):
        shape=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.025]*3)
        visual=p.createVisualShape(p.GEOM_BOX,halfExtents=[.025]*3,rgbaColor=[.95,.05,.03,1])
        for x,y in [(.56,.10),(.40,-.15)]:
            p.createMultiBody(.06,shape,visual,basePosition=[x,y,.025])
        found=camera_snapshot()['instances']['red']
        self.assertEqual(len(found),2)
        self.assertLess(min(math.dist(item['point'][:2],[.56,.10]) for item in found),.003)
