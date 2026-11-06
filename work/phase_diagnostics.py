import json,math
from pathlib import Path
from work.color_contact_candidate import run
manifest=json.loads(Path('work/frozen-20261105/manifest.json').read_text(encoding='utf8'))
stages=['verify view','retry grasp','retry lift','retry transfer','retry place','retry release','retry retreat','retry verify view'];rows=[]
for c in manifest['cases']['development']:
 r=run([c['color']],scene_seed=c['seed'],source_offset=c['offset'],extra_count=c['extra'],same_red=c.get('same_red',False),feedback='sensor',retry=True)
 idx=r['colors'].index(c['color']);record=[]
 for name in stages:
  x=next((f for f in reversed(r['frames']) if f['stage']==name),None)
  if x:
   pos=x['parts'][idx][0];record.append({'stage':name,'xy_mm':[round(1000*v,2) for v in pos[:2]],'error_mm':round(1000*math.dist(pos[:2],[.56,.10]),2)})
 rows.append({'scene':c,'phases':record,'verification':r['verification'],'success':r['success']});print(json.dumps(rows[-1]),flush=True)
Path('outputs/phase-diagnostics-20261105.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
