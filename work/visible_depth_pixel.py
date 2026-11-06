"""Select an observed color pixel near a component centroid for depth sampling."""
import numpy as np

def nearest_visible_pixel(rgb,color,x,y,radius=8):
    a=np.asarray(rgb,dtype=np.int16);h,w=a.shape[:2]; cx=round(x);cy=round(y)
    left=max(0,cx-radius);right=min(w,cx+radius+1);top=max(0,cy-radius);bottom=min(h,cy+radius+1)
    r,g,b=(a[top:bottom,left:right,i] for i in range(3))
    masks={'red':(r>90)&(r>g*1.6)&(r>b*1.6),'blue':(b>70)&(b>r*1.5)&(b>g*1.25),'green':(g>70)&(g>r*1.4)&(g>b*1.25)}
    if color not in masks:return None
    yy,xx=np.where(masks[color])
    if not len(xx):return None
    d=(xx+left-x)**2+(yy+top-y)**2; i=int(np.argmin(d))
    if d[i]>radius*radius:return None
    return int(xx[i]+left),int(yy[i]+top)
