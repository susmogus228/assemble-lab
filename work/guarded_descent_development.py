import json,math,random
from pathlib import Path
from work.color_tower_guarded_v1 import run
rows=[]
for seed,extra in [(0,0),(223,2),(503,0),(521,4)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,feedback='sensor',retry=True)
 row={'seed':seed,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'hold_checks':r['hold_checks']};rows.append(row);print(json.dumps({**row,'hold_checks':len(row['hold_checks'])}),flush=True);Path('outputs/guarded-descent-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
