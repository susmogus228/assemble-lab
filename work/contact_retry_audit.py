import json,math,time
from pathlib import Path
from color_assembly import run as baseline
from work.color_contact_candidate import run as candidate
cases=[('blue-reference',['blue'],0,(0,0),0,False),('red-clutter',['red'],1,(-.01,.005),2,False),('red-duplicate',['red2'],0,(0,0),1,True),('blue-unseen',['blue'],7,(.008,-.004),4,False),('red-unseen',['red'],11,(-.006,-.007),2,False)]
rows=[]
for name,selected,seed,offset,extra,same in cases:
 for strategy in ('no_retry','legacy','contact'):
  runner=candidate if strategy=='contact' else baseline
  start=time.perf_counter();r=runner(selected,source_offset=offset,scene_seed=seed,extra_count=extra,same_red=same,feedback='sensor',retry=strategy!='no_retry')
  row={'case':name,'development':name=='blue-reference','strategy':strategy,'seconds':round(time.perf_counter()-start,2),'success':r['success'],'failure':r['failure'],'verification':r['verification'],'unselected_mm':r['unselected_displacement_mm'],'final_xy_error_mm':round(math.dist(r['final_position'][:2],r['target'][:2])*1000,2),'action_colors':[a['color'] for a in r['parts']]}
  rows.append(row);print(json.dumps(row),flush=True)
  Path('outputs/contact-retry-evaluation.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
