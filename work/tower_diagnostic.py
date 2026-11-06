import json,random,math,time
from pathlib import Path
from color_assembly import run as base
from work.color_camera_candidate import run as top
rows=[]
for seed,extra in [(0,0),(1,2),(2,4)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
 for mode,fn,retry in [('no_retry',base,False),('top_depth',top,True)]:
  r=fn(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,feedback='sensor',retry=retry);frames=r['frames']
  before=next((f['parts'][0][0] for f in reversed(frames) if f['part_number']==1),None);after=frames[-1]['parts'][0][0] if frames else None
  row={'seed':seed,'extra':extra,'offset':offset,'mode':mode,'success':r['success'],'failure':r['failure'],'checks':r['final_recheck'],'verification':r['verification'],'base_shift_mm':round(math.dist(before[:2],after[:2])*1000,2) if before and after else None,'relative_mm':r['criteria']['relative_offset_mm'],'unselected':r['unselected_displacement_mm']}
  rows.append(row);print(json.dumps(row),flush=True)
Path('outputs/tower-development-baseline.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
