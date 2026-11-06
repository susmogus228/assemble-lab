import json,random,math
from pathlib import Path
from work.color_tower_candidate import run
rows=[]
for seed,extra in [(0,0),(1,2),(2,4)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,feedback='sensor',retry=True);frames=r['frames'];before=next((f['parts'][0][0] for f in reversed(frames) if f['part_number']==1),None);after=frames[-1]['parts'][0][0] if frames else None
 row={'seed':seed,'extra':extra,'success':r['success'],'failure':r['failure'],'checks':r['final_recheck'],'relative_mm':r['criteria']['relative_offset_mm'],'base_shift_mm':round(math.dist(before[:2],after[:2])*1000,2) if before and after else None,'base_observations':r['base_observations'],'verification':r['verification'],'unselected':r['unselected_displacement_mm']};rows.append(row);print(json.dumps(row),flush=True)
Path('outputs/tower-candidate-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
