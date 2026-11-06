import json,math,random
from pathlib import Path
from work.color_tower_upper_force_v2 import run
rows=[]
for seed,extra in [(701,0),(709,2),(719,4),(727,1)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,same_red=seed==727,feedback='sensor',retry=True)
 row={'seed':seed,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'verification':r['verification']};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/upper-force-v2-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
