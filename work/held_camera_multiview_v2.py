"""Experimental two-view center estimate for 50 mm axis-aligned cubes."""
import math

def combine_centers(x_faces,y_faces,tool,limit=.012):
    def unique(items):
        candidates=[]
        for item in items:
            point=item.get('point',())
            if len(point)==3 and all(math.isfinite(v) for v in point) and math.dist(point,tool)<.095:
                candidates.append(point)
        return candidates[0] if len(candidates)==1 else None
    x=unique(x_faces);y=unique(y_faces)
    if x is None or y is None:return None
    cx=x[0]-.025; cy=y[1]+.025
    # Each view supplies one face coordinate and a partial silhouette on the other axis.
    if abs(cx-y[0])>.020 or abs(cy-x[1])>limit:return None
    return (cx,cy)

