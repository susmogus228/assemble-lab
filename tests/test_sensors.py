import unittest
import numpy as np
from sensors import detect_colors, detect_instances

class SensorTests(unittest.TestCase):
    def test_color_detection_only_uses_image(self):
        image=np.zeros((20,30,3),dtype=np.uint8)
        image[2:8,3:9]=[240,55,25];image[10:17,20:27]=[20,100,240]
        detected=detect_colors(image)
        self.assertEqual(set(detected),{'red','blue'})
        self.assertAlmostEqual(detected['red'][0],5.5)
        self.assertAlmostEqual(detected['blue'][1],13)
    def test_distinct_same_color_components_are_separate(self):
        image=np.zeros((30,40,3),dtype=np.uint8);image[4:10,4:10]=[240,30,20];image[15:21,25:31]=[240,30,20]
        components=detect_instances(image)['red']
        self.assertEqual(len(components),2)
    def test_depth_filters_side_face_when_estimating_top_center(self):
        from work.sensors_candidate import detect_instances
        image=np.zeros((20,25,3),dtype=np.uint8);image[4:12,4:17]=[20,100,240]
        depth=np.ones((20,25),dtype=float);depth[4:12,4:12]=.90;depth[4:12,12:17]=.92
        point=detect_instances(image,depth)['blue'][0]
        self.assertAlmostEqual(point[0],7.5)
    def test_noise_and_unknown_are_not_objects(self):
        image=np.zeros((20,20,3),dtype=np.uint8);image[1,1]=[255,0,0]
        self.assertEqual(detect_colors(image),{})
if __name__=='__main__': unittest.main()
