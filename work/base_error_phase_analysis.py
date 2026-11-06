import json,math,random
from pathlib import Path
from work.color_tower_guarded_v1 import run
rows=[]
for seed,extra in [(601,0),(607,2),(613,4),(617,1)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,same_red=seed==617,feedback='sensor',retry=True)
 spans=[]
 for f in r['frames']:
  key=(f['part_number'],f['stage']);v=f['parts'][0][0]
  if not spans or spans[-1]['key']!=key:spans.append({'key':key,'first':list(v),'last':list(v)})
  else:spans[-1]['last']=list(v)
 selected=[{'part':s['key'][0],'stage':s['key'][1],'position':s['last'],'xy_error_mm':round(math.dist(s['last'][:2],(.56,.1))*1000,2),'delta_mm':round(math.dist(s['first'][:2],s['last'][:2])*1000,2)} for s in spans if s['key'][1] in ('controlled descent','release','retreat','verify view','correct descend','correct contact search','correct push','retry verify view','base observation')]
 row={'seed':seed,'success':r['success'],'failure':r['failure'],'stages':selected,'verification':r['verification'],'base_observations':r['base_observations'],'checks':r['final_recheck'],'tracking':r['held_tracking']};rows.append(row);print(json.dumps({'seed':seed,'stages':selected,'verification':r['verification'],'base_observations':r['base_observations']}),flush=True);Path('outputs/base-error-phase-analysis.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
