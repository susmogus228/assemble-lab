import json,math,time
from pathlib import Path
from color_assembly import run
scenes=[(0,(0,0),0),(1,(-.01,.005),2),(2,(.01,-.005),4)]
rows=[]
for seed,offset,extra in scenes:
 for mode in ('oracle','sensor'):
  t=time.perf_counter();r=run(['red','blue'],source_offset=offset,scene_seed=seed,extra_count=extra,feedback=mode)
  rows.append({'seed':seed,'offset':offset,'extra':extra,'feedback':mode,'seconds':round(time.perf_counter()-t,2),'success':r['success'],'failure':r['failure'],'detected':[{'color':i['color'],'seen':list(i['detections']),'laser_confirmed':bool(i['laser'] and i['laser']['hit'])} for i in r['inspections']],'attempted':[p['color'] for p in r['parts']],'errors_mm':[round(math.dist(part['actual'][:2],part['target'][:2])*1000,2) for part in r['parts']],'unselected_mm':r['unselected_displacement_mm'],'criteria':r['criteria']})
Path('outputs/clutter-feedback-comparison.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
