import json,random,math
from pathlib import Path
from work.color_tower_v3 import run
rows=[]
for seed,extra in [(0,0),(1,2),(2,4),(223,2),(307,0),(311,2),(313,4),(317,1)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,same_red=seed==317,feedback='sensor',retry=True)
 row={'seed':seed,'extra':extra,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'base_error_mm':math.dist(r['final_recheck'][0]['actual'][:2],(.56,.1))*1000,'unselected':r['unselected_displacement_mm'],'verification':r['verification'],'checks':r['final_recheck']};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/tower-v3-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
