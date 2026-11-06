import random,math
from work.color_tower_multiview_v5 import run as old
from work.color_tower_reobserve_v1 import run as new
rng=random.Random(1009);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
a=old(['red','blue'],scene_seed=1009,source_offset=offset,feedback='sensor',retry=True);b=new(['red','blue'],scene_seed=1009,source_offset=offset,feedback='sensor',retry=True)
for i,(x,y) in enumerate(zip(a['frames'],b['frames'])):
 if x['stage']!=y['stage'] or math.dist(x['parts'][0][0],y['parts'][0][0])>1e-7 or math.dist(x['links'][12][0],y['links'][12][0])>1e-7:
  print('first difference',i,x['stage'],y['stage'],'arm',math.dist(x['links'][12][0],y['links'][12][0]),'cube',math.dist(x['parts'][0][0],y['parts'][0][0]));break
else:print('no difference')
print('length',len(a['frames']),len(b['frames']),'reobserve',b['reobservations'])
