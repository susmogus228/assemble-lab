import json,random,math
from pathlib import Path
from work.color_tower_v2 import run
rows=[]
for seed,extra in [(307,0),(311,2),(313,4),(317,1)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,same_red=seed==317,feedback='sensor',retry=True)
 spans=[]
 for f in r['frames']:
  key=(f['part_number'],f['stage']); pos=f['parts'][0][0]
  if not spans or spans[-1]['key']!=key: spans.append({'key':key,'start':pos,'end':pos})
  else: spans[-1]['end']=pos
 moves=[{'stage':s['key'],'delta_mm':round(math.dist(s['start'][:2],s['end'][:2])*1000,2),'end':s['end'][:2]} for s in spans if math.dist(s['start'][:2],s['end'][:2])>.001]
 row={'seed':seed,'moves':moves,'diagnostics':r['diagnostics'],'verification':r['verification'],'base_observations':r['base_observations'],'checks':r['final_recheck'],'criteria':r['criteria']};rows.append(row);print(json.dumps(row),flush=True)
Path('outputs/tower-stage-diagnostics.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
