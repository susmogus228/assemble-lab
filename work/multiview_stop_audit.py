import json,random
from work.color_tower_multiview_v5 import run
for seed,extra in [(1009,0),(1019,4)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,feedback='sensor',retry=True)
 print(json.dumps({'seed':seed,'failure':r['failure'],'last_check':r['hold_checks'][-1]}),flush=True)
