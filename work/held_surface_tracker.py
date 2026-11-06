"""Bounded tracker of held cube surface estimates."""
from work.held_surface_cloud import estimate_center
class SurfaceTracker:
    def __init__(self,max_missing=2):self.max_missing=max_missing;self.offset=None;self.missing=0
    def update(self,x,y,tool):
        if len(x)>=9 and len(y)>=9:
            value=estimate_center(x,y,tool)
            if value is None:self.offset=None;return None,'conflict'
            self.offset=(value[0]-tool[0],value[1]-tool[1]);self.missing=0;return value,'observed'
        self.missing+=1
        if self.offset is None or self.missing>self.max_missing:return None,'unavailable'
        return (tool[0]+self.offset[0],tool[1]+self.offset[1]),'predicted'
