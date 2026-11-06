"""Experimental simulated side RGB-D view for observing held parts."""
import numpy as np
import pybullet as p
from work.sensors_candidate import detect_instances

VIEWS={
 'side_x':([1.2,-.10,.48],[.48,-.10,.15]),
 'side_y':([.48,-.85,.48],[.48,-.10,.15]),
 'diagonal':([1.0,-.65,.55],[.48,-.10,.15]),
}

def snapshot(view_name):
    eye,target=VIEWS[view_name];width=384;height=384
    view=p.computeViewMatrix(eye,target,[0,0,1]);projection=p.computeProjectionMatrixFOV(60,1,.05,2.5)
    _,_,rgba,depth,_=p.getCameraImage(width,height,view,projection,renderer=p.ER_TINY_RENDERER)
    rgb=np.asarray(rgba,dtype=np.uint8).reshape(height,width,4)[:,:,:3];depth=np.asarray(depth).reshape(height,width)
    comp=detect_instances(rgb,depth);inv=np.linalg.inv(np.asarray(projection).reshape(4,4,order='F')@np.asarray(view).reshape(4,4,order='F'))
    out={}
    for name,items in comp.items():
        out[name]=[]
        for x,y,n in items:
            d=depth[round(y),round(x)];q=inv@np.array([2*(x+.5)/width-1,1-2*(y+.5)/height,2*float(d)-1,1]);w=q[:3]/q[3]
            out[name].append({'point':w.tolist(),'pixels':n})
    return out

def held_center(candidates, tool):
    """Estimate XY from the visible +X face of a known, axis-aligned 50 mm cube.

    Return None for absent or multiple plausible observations. This geometric
    approximation is not suitable for arbitrary shapes or large cube rotations.
    """
    import math
    nearby=[]
    for item in candidates:
        point=item.get('point',())
        if len(point)!=3 or not all(math.isfinite(v) for v in point):
            continue
        if math.dist(point,tool) < .095:
            nearby.append(point)
    if len(nearby)!=1:
        return None
    point=nearby[0]
    return (point[0]-.025,point[1])
