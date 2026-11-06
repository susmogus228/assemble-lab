import base64,json,random
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pybullet as p
from work.held_camera_visible import VIEWS
from work.sensors_candidate import png_data
from work.held_tracking_memory_v2 import HeldTracker
from work.color_tower_multiview_v5 import run
out=Path('outputs/camera-conflict-audit');out.mkdir(exist_ok=True)
for seed,extra in [(1009,0),(1019,4)]:
 events=[];orig=HeldTracker.update
 def capture(self,x,y,tool):
  result=orig(self,x,y,tool)
  if result[1]=='conflict':
   imgs={}
   for name in ('side_x','side_y'):
    eye,target=VIEWS[name];view=p.computeViewMatrix(eye,target,[0,0,1]);projection=p.computeProjectionMatrixFOV(60,1,.05,2.5)
    _,_,rgba,_,_=p.getCameraImage(384,384,view,projection,renderer=p.ER_TINY_RENDERER);rgb=np.asarray(rgba,dtype=np.uint8).reshape(384,384,4)[:,:,:3]
    path=out/f'{seed}-{name}.png';path.write_bytes(base64.b64decode(png_data(rgb).split(',',1)[1]));imgs[name]=str(path)
   points=p.getContactPoints(bodyA=1,linkIndexA=9);ids=[a[2] for a in points]
   actual=[list(p.getBasePositionAndOrientation(b)[0]) for b in ids]
   events.append({'x':x,'y':y,'tool':list(tool),'contact_positions_for_analysis_only':actual,'images':imgs})
  return result
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 with patch.object(HeldTracker,'update',capture):r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,feedback='sensor',retry=True)
 (out/f'{seed}.json').write_text(json.dumps({'failure':r['failure'],'events':events},indent=2),encoding='utf8');print(json.dumps({'seed':seed,'failure':r['failure'],'events':events}),flush=True)
