import json,math
from pathlib import Path
from color_assembly import run
rows=[]
for selected,seed,offset,extra,same in [(['blue'],0,(0,0),0,False),(['red'],1,(-.01,.005),2,False),(['red2'],0,(0,0),1,True)]:
 for retry in (False,True):
  r=run(selected,source_offset=offset,scene_seed=seed,extra_count=extra,same_red=same,feedback='sensor',retry=retry)
  rows.append({'selected':selected,'seed':seed,'extras':extra,'same_red':same,'retry':retry,'success':r['success'],'failure':r['failure'],'verification':r['verification'],'unselected_mm':r['unselected_displacement_mm'],'final_xy_error_mm':round(math.dist(r['final_position'][:2],r['target'][:2])*1000,2),'action_colors':[a['color'] for a in r['parts']]})
Path('outputs/verification-retry-comparison.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
