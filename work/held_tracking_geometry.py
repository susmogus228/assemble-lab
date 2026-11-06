"""Limited dead reckoning for an object in a mechanically coupled gripper."""
import math
from work.held_face_geometry import combine_faces as combine_centers

class HeldTracker:
    def __init__(self,max_missing=2):
        self.max_missing=max_missing;self.offset=None;self.missing=0
    def update(self,x_faces,y_faces,tool):
        def near(items):
            return [i for i in items if len(i.get('point',()))==3 and all(math.isfinite(v) for v in i['point']) and math.dist(i['point'],tool)<.095]
        x=near(x_faces);y=near(y_faces)
        if len(x)>1 or len(y)>1:
            self.offset=None;return None,'conflict'
        if x and y:
            value=combine_centers(x,y,tool)
            if value is None:
                self.offset=None;return None,'conflict'
            self.offset=(value[0]-tool[0],value[1]-tool[1]);self.missing=0
            return value,'observed'
        self.missing+=1
        if self.offset is None or self.missing>self.max_missing:return None,'unavailable'
        return (tool[0]+self.offset[0],tool[1]+self.offset[1]),'predicted'


