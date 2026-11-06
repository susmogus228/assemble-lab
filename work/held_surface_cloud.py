"""Experimental two-view 3D color surface estimator for a 50 mm cube."""
import numpy as np
import pybullet as p
from work.held_camera_visible import VIEWS

def color_cloud(view_name,color,tool):
    eye,target=VIEWS[view_name];width=384;height=384
    view=p.computeViewMatrix(eye,target,[0,0,1]);proj=p.computeProjectionMatrixFOV(60,1,.05,2.5)
    _,_,rgba,depth,_=p.getCameraImage(width,height,view,proj,renderer=p.ER_TINY_RENDERER)
    rgb=np.asarray(rgba,dtype=np.int16).reshape(height,width,4);depth=np.asarray(depth).reshape(height,width)
    r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    mask={'red':(r>90)&(r>g*1.6)&(r>b*1.6),'blue':(b>70)&(b>r*1.5)&(b>g*1.25),'green':(g>70)&(g>r*1.4)&(g>b*1.25)}.get(color)
    if mask is None:return np.empty((0,3))
    yy,xx=np.where(mask)
    if not len(xx):return np.empty((0,3))
    inv=np.linalg.inv(np.asarray(proj).reshape(4,4,order='F')@np.asarray(view).reshape(4,4,order='F'))
    clip=np.stack((2*(xx+.5)/width-1,1-2*(yy+.5)/height,2*depth[yy,xx]-1,np.ones(len(xx))))
    world=inv@clip;world=(world[:3]/world[3]).T
    diff=world-np.asarray(tool);valid=np.all(np.isfinite(world),axis=1)&(np.linalg.norm(diff,axis=1)<.095)&(np.abs(diff[:,2]+.010)<.032)
    return world[valid]

def estimate_center(x_cloud,y_cloud,tool):
    x=np.asarray(x_cloud,dtype=float);y=np.asarray(y_cloud,dtype=float)
    if x.ndim!=2 or y.ndim!=2 or x.shape[1]!=3 or y.shape[1]!=3 or len(x)<9 or len(y)<9:return None
    if not np.isfinite(x).all() or not np.isfinite(y).all():return None
    cx=float(np.quantile(x[:,0],.95)-.025);cy=float(np.quantile(y[:,1],.05)+.025)
    if abs(cx-float(np.median(y[:,0])))>.028 or abs(cy-float(np.median(x[:,1])))>.028:return None
    if np.linalg.norm(np.array([cx,cy])-np.asarray(tool[:2]))>.065:return None
    for cloud in (x,y):
        within=(np.abs(cloud[:,0]-cx)<=.030)&(np.abs(cloud[:,1]-cy)<=.030)
        if float(np.mean(within))<.90:return None
    return cx,cy

