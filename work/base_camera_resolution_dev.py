import json,math,random,time
from pathlib import Path
import pybullet as p
from work.sensors_candidate import camera_snapshot as baseline
from work.base_camera_highres import camera_snapshot as highres
p.connect(p.DIRECT);p.setGravity(0,0,-9.81)
c=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.65,.65,.025]);v=p.createVisualShape(p.GEOM_BOX,halfExtents=[.65,.65,.025],rgbaColor=[.23,.23,.23,1]);p.createMultiBody(0,c,v,basePosition=[.5,0,-.025])
shape=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.025]*3);v=p.createVisualShape(p.GEOM_BOX,halfExtents=[.025]*3,rgbaColor=[.95,.05,.03,1]);b=p.createMultiBody(.06,shape,v,basePosition=[.56,.1,.025]);rows=[]
rng=random.Random(731)
for i in range(16):
 x=rng.uniform(.54,.58);y=rng.uniform(.08,.12);yaw=rng.uniform(-.2,.2);p.resetBasePositionAndOrientation(b,[x,y,.025],p.getQuaternionFromEuler([0,0,yaw]));row={'xy':[x,y],'yaw':yaw}
 for name,fn in [('standard',baseline),('highres',highres)]:
  start=time.perf_counter();o=fn()['detections'].get('red');row[name]={'error_mm':math.dist([x,y],o['point'][:2])*1000 if o else None,'seconds':time.perf_counter()-start}
 rows.append(row)
p.disconnect();Path('outputs/base-camera-resolution-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
for name in ('standard','highres'):
 err=[r[name]['error_mm'] for r in rows if r[name]['error_mm'] is not None];print(name,'count',len(err),'mean',sum(err)/len(err),'max',max(err),'seconds',sum(r[name]['seconds'] for r in rows)/len(rows))
