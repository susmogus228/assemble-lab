import json,random,math
from pathlib import Path
from work.color_tower_reobserve_v2 import run
rows=[]
for seed,extra in [(1009,0),(1019,4),(1013,2),(1021,1)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,same_red=seed==1021,feedback='sensor',retry=True)
 tr=[x for x in r['held_tracking'] if x['color']=='blue' and x['estimate'] is not None];e=[math.dist(x['estimate'],x['truth'][:2])*1000 for x in tr]
 row={'seed':seed,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'reobservations':r['reobservations'],'tracking_mean_mm':sum(e)/len(e) if e else None};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/reobserve-v2-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')

