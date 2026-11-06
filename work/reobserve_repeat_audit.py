import json,random
from work.color_tower_multiview_v5 import run as old
from work.color_tower_reobserve_v1 import run as new
for name,fn in [('old1',old),('new',new),('old2',old)]:
 rng=random.Random(1009);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=fn(['red','blue'],scene_seed=1009,source_offset=offset,extra_count=0,feedback='sensor',retry=True)
 print(json.dumps({'method':name,'success':r['success'],'failure':r['failure'],'relative':r['criteria']['relative_offset_mm'],'reobservations':r.get('reobservations',[]),'checks':r['final_recheck']}),flush=True)
