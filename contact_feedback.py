"""Estimate a held object's XY center from two fingertip contact surfaces."""
import math

def center_from_contacts(left,right,tool):
    def closest(points):
        usable=[p for p in points if len(p)>=3 and math.dist(p,tool)<.12]
        return min(usable,key=lambda p:math.dist(p,tool)) if usable else None
    a,b=closest(left),closest(right)
    if a is None or b is None:return None
    return ((a[0]+b[0])/2,(a[1]+b[1])/2)
