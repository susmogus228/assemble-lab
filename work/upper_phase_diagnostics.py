import json,math,random
from pathlib import Path
from work.color_tower_base_camera_v1 import run
rows=[]
for seed,extra in [(701,0),(709,2),(719,4),(727,1)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,same_red=seed==727,feedback='sensor',retry=True)
 spans=[]
 for f in r['frames']:
  if f['part_number']!=2:continue
  stage=f['stage'];bottom=f['parts'][0][0];top=f['parts'][1][0]
  if not spans or spans[-1]['stage']!=stage:spans.append({'stage':stage,'first_top':top,'last_top':top,'first_bottom':bottom,'last_bottom':bottom})
  else:spans[-1]['last_top']=top;spans[-1]['last_bottom']=bottom
 stages=[]
 for s in spans:
  if s['stage'] not in ('grasp','lift','transfer','align','controlled descent','release','retreat','settle','verify view'):continue
  stages.append({'stage':s['stage'],'first_top':s['first_top'],'last_top':s['last_top'],'relative_start_mm':round(math.dist(s['first_top'][:2],s['first_bottom'][:2])*1000,2),'relative_end_mm':round(math.dist(s['last_top'][:2],s['last_bottom'][:2])*1000,2),'top_motion_mm':round(math.dist(s['first_top'][:2],s['last_top'][:2])*1000,2),'bottom_motion_mm':round(math.dist(s['first_bottom'][:2],s['last_bottom'][:2])*1000,2)})
 row={'seed':seed,'success':r['success'],'failure':r['failure'],'stages':stages,'held_tracking':[v for v in r['held_tracking'] if v['color']=='blue'],'base_observations':r['base_observations']};rows.append(row);print(json.dumps({'seed':seed,'success':r['success'],'stages':stages}),flush=True);Path('outputs/upper-phase-diagnostics.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
