"""Axis-aligned 50 mm cube face consistency gate for simulated cameras."""
import math

def combine_faces(x_faces,y_faces,tool):
    def unique(items):
        near=[]
        for item in items:
            p=item.get('point',())
            if len(p)==3 and all(math.isfinite(v) for v in p) and math.dist(p,tool)<.095:near.append(p)
        return near[0] if len(near)==1 else None
    x=unique(x_faces);y=unique(y_faces)
    if x is None or y is None:return None
    cx=x[0]-.025;cy=y[1]+.025
    # These are visible face points, which can lie anywhere within a 50 mm face.
    # Allow 3 mm for rendering and grasp-height approximations; not arbitrary shapes.
    half_extent=.028;estimated_z=tool[2]-.010
    if abs(cx-y[0])>half_extent or abs(cy-x[1])>half_extent:return None
    if abs(x[2]-estimated_z)>half_extent or abs(y[2]-estimated_z)>half_extent:return None
    return cx,cy
