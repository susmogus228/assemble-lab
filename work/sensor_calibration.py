import math,json,time
from pathlib import Path
import pybullet as p
from sensors import camera_snapshot as old
from work.sensors_candidate import camera_snapshot as new
p.connect(p.DIRECT);p.setGravity(0,0,-9.81)
c=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.65,.65,.025]);v=p.createVisualShape(p.GEOM_BOX,halfExtents=[.65,.65,.025],rgbaColor=[.23,.23,.23,1]);p.createMultiBody(0,c,v,basePosition=[.5,0,-.025])
shape=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.025]*3);v=p.createVisualShape(p.GEOM_BOX,halfExtents=[.025]*3,rgbaColor=[.03,.15,.95,1]);b=p.createMultiBody(.06,shape,v,basePosition=[.56,.10,.025]);rows=[]
for x in [.541,.559,.577]:
 for y in [.084,.101,.117]:
  p.resetBasePositionAndOrientation(b,[x,y,.025],[0,0,0,1]); row={'actual':[x,y]}
  for k,fn in [('old',old),('candidate',new)]:
   t=time.perf_counter();o=fn()['detections'].get('blue');row[k]={'error_mm':round(math.dist([x,y],o['point'][:2])*1000,3) if o else None,'point':o['point'] if o else None,'seconds':round(time.perf_counter()-t,3)}
  rows.append(row)
p.disconnect();Path('outputs/camera-resolution-audit.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
