import json,math,random
from pathlib import Path
from work.color_tower_coupled_v1 import run
rows=[]
for seed,extra in [(907,0),(911,2),(919,4),(929,1)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,same_red=seed==929,feedback='sensor',retry=True)
 obs=[]
 for check,track in zip(r['hold_checks'],r['held_tracking']):
  if check['color']!='blue':continue
  estimate=track['estimate']; truth=track['truth']; base=r['base_observations'][0]['point']
  obs.append({'stage':check['stage'],'estimate':estimate,'truth':truth,'error_vec_mm':[(estimate[i]-truth[i])*1000 for i in (0,1)] if estimate else None,'estimate_target_mm':math.dist(estimate,base[:2])*1000 if estimate else None,'truth_target_mm':math.dist(truth[:2],base[:2])*1000})
 row={'seed':seed,'success':r['success'],'relative':r['criteria']['relative_offset_mm'],'base':r['base_observations'],'observations':obs};rows.append(row);print(json.dumps({'seed':seed,'relative':row['relative'],'observations':obs[-7:]}),flush=True);Path('outputs/coupled-alignment-diagnostic.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
