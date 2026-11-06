"""Calibrated RGB-D camera helpers; color localization uses pixels, not body IDs."""
import base64, struct, zlib
import numpy as np
import pybullet as p

def detect_instances(rgb,depth=None):
    a=np.asarray(rgb,dtype=np.int16); r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    masks={'red':(r>90)&(r>g*1.6)&(r>b*1.6),'blue':(b>70)&(b>r*1.5)&(b>g*1.25),'green':(g>70)&(g>r*1.4)&(g>b*1.25)}
    result={}
    for name,mask in masks.items():
        remaining=mask.copy(); h,w=mask.shape; components=[]
        for y,x in zip(*np.where(mask)):
            if not remaining[y,x]:continue
            remaining[y,x]=False; stack=[(int(y),int(x))]; points=[]
            while stack:
                cy,cx=stack.pop();points.append((cy,cx))
                for ny,nx in ((cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)):
                    if 0<=ny<h and 0<=nx<w and remaining[ny,nx]:remaining[ny,nx]=False;stack.append((ny,nx))
            if len(points)>=9:
                if depth is not None:
                    nearest=min(float(depth[py,px]) for py,px in points)
                    top=[(py,px) for py,px in points if float(depth[py,px])<=nearest+.00015]
                    if len(top)>=9:points=top
                yy,xx=zip(*points);components.append((float(np.median(xx)),float(np.median(yy)),len(points)))
        if components:result[name]=sorted(components,key=lambda c:c[0])
    return result

def detect_colors(rgb):
    return {name:max(items,key=lambda c:c[2]) for name,items in detect_instances(rgb).items()}

def png_data(rgb):
    h,w,_=rgb.shape;raw=b''.join(b'\x00'+rgb[i,:,:3].astype(np.uint8).tobytes() for i in range(h))
    def chunk(t,d):return struct.pack('!I',len(d))+t+d+struct.pack('!I',zlib.crc32(t+d)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
    return 'data:image/png;base64,'+base64.b64encode(png).decode('ascii')

def camera_snapshot():
    width=256;height=256
    view=p.computeViewMatrix([.48,-.10,.9],[.48,-.10,0],[0,1,0]);projection=p.computeProjectionMatrixFOV(55,1,.05,2)
    _,_,rgba,depth,_=p.getCameraImage(width,height,view,projection,renderer=p.ER_TINY_RENDERER)
    rgb=np.asarray(rgba,dtype=np.uint8).reshape(height,width,4)[:,:,:3]; depth=np.asarray(depth).reshape(height,width)
    components=detect_instances(rgb,depth); inv=np.linalg.inv(np.array(projection).reshape(4,4,order='F') @ np.array(view).reshape(4,4,order='F'))
    instances={}
    for name,items in components.items():
        instances[name]=[]
        for x,y,n in items:
            ix,iy=round(x),round(y); d=depth[iy,ix]
            clip=np.array([2*(x+.5)/width-1,1-2*(y+.5)/height,2*float(d)-1,1]); world=inv@clip; world=world[:3]/world[3]
            instances[name].append({'pixel':[x,y],'pixels':n,'point':world.tolist()})
    found={name:max(items,key=lambda item:item['pixels']) for name,items in instances.items()}
    return {'image':png_data(rgb),'detections':found,'instances':instances}
