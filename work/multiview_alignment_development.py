import json,math,random
from pathlib import Path
from work.color_tower_multiview_v1 import run
rows=[]
for seed,extra in [(907,0),(911,2),(919,4),(929,1)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,same_red=seed==929,feedback='sensor',retry=True)
 track=[t for t in r['held_tracking'] if t['color']=='blue' and t['estimate'] is not None];errs=[math.dist(x['estimate'],x['truth'][:2])*1000 for x in track]
 row={'seed':seed,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'upper_seen':len(track),'upper_mean_err':sum(errs)/len(errs) if errs else None,'upper_max_err':max(errs) if errs else None,'hold_checks':len(r['hold_checks'])};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/multiview-alignment-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
