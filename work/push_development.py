import json,math,hashlib
from pathlib import Path
from color_assembly import run as baseline
from work.color_contact_candidate import run as contact
from work.color_push_candidate import run as push
manifest=json.loads(Path('work/frozen-20261105/manifest.json').read_text(encoding='utf8'));rows=[]
for c in manifest['cases']['development']:
 for strategy,runner,retry in [('no_retry',baseline,False),('contact',contact,True),('push',push,True)]:
  r=runner([c['color']],scene_seed=c['seed'],source_offset=c['offset'],extra_count=c['extra'],same_red=c.get('same_red',False),feedback='sensor',retry=retry)
  row={'scene':c,'strategy':strategy,'success':r['success'],'error_mm':round(math.dist(r['final_position'][:2],r['target'][:2])*1000,2),'verification':r['verification'],'unselected_mm':r['unselected_displacement_mm'],'failure':r['failure']}
  rows.append(row);print(json.dumps(row),flush=True)
Path('outputs/push-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
