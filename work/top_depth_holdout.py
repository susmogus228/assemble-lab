import json,math,hashlib
from pathlib import Path
from color_assembly import run as no_retry
from work.color_push_candidate import run as baseline
from work.color_camera_candidate import run as candidate
m=json.loads(Path('work/frozen-top-depth/manifest.json').read_text(encoding='utf8'))
for name,sha in m['hashes'].items():assert hashlib.sha256(Path('work',name).read_bytes()).hexdigest()==sha
rows=[]
for c in m['cases']:
 for mode,runner,retry in [('no_retry',no_retry,False),('baseline',baseline,True),('top_depth',candidate,True)]:
  r=runner([c['color']],scene_seed=c['seed'],source_offset=c['offset'],extra_count=c['extra'],same_red=c.get('same_red',False),feedback='sensor',retry=retry)
  row={'scene':c,'mode':mode,'success':r['success'],'failure':r['failure'],'error_mm':round(math.dist(r['final_position'][:2],r['target'][:2])*1000,2),'verification':r['verification'],'unselected':r['unselected_displacement_mm']};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/top-depth-holdout.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
