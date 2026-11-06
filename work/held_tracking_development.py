import json,random,math
from pathlib import Path
from work.color_tower_v2 import run as baseline
from work.color_tower_held_v1 import run as candidate
rows=[]
for seed,extra in [(0,0),(2,4),(223,2)]:
 rng=random.Random(seed); offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
 for name,run in [('baseline',baseline),('tracked',candidate)]:
  r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,feedback='sensor',retry=True)
  tr=r.get('held_tracking',[]);valid=[x for x in tr if x['estimate'] is not None]
  row={'seed':seed,'method':name,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'tracking_count':len(tr),'tracking_valid':len(valid),'tracking_error_mm':[round(math.dist(x['estimate'],x['truth'][:2])*1000,2) for x in valid]};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/held-tracking-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
