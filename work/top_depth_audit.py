import json,math,hashlib
from pathlib import Path
from work.color_push_candidate import run as baseline
from work.color_camera_candidate import run as candidate
cases=json.loads(Path('work/frozen-20261105/manifest.json').read_text(encoding='utf8'))['cases']['development'];rows=[]
for c in cases:
 for label,fn in [('baseline',baseline),('top_depth',candidate)]:
  d=fn([c['color']],scene_seed=c['seed'],source_offset=c['offset'],extra_count=c['extra'],same_red=c.get('same_red',False),feedback='sensor',retry=True)
  row={'scene':c,'mode':label,'success':d['success'],'failure':d['failure'],'error_mm':round(math.dist(d['final_position'][:2],d['target'][:2])*1000,2),'verification':d['verification'],'unselected':d['unselected_displacement_mm']};rows.append(row);print(json.dumps(row),flush=True)
Path('outputs/top-depth-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
