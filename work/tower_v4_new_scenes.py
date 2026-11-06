import json,random,math,hashlib
from pathlib import Path
from work.color_tower_v2 import run as baseline
from work.color_tower_v4 import run as candidate
files=['work/color_tower_v2.py','work/color_tower_v4.py','work/sensors_candidate.py','sensors.py','tower_targets.py','sequence_probe.py','contact_feedback.py']
cases=[{'seed':401,'extra':0,'same_red':False},{'seed':409,'extra':2,'same_red':False},{'seed':419,'extra':4,'same_red':False},{'seed':421,'extra':1,'same_red':True}]
manifest={'files':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files},'cases':cases,'selection':'v4 preserves lower-cube correction and does not push stacked top cube; selected before new-scene comparison','criteria':'original nominal targets; position and relative alignment <=3 mm; angle <=3 degrees; unselected displacement <=5 mm'}
Path('work/frozen-tower-v4').mkdir(exist_ok=True);Path('work/frozen-tower-v4/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
rows=[]
for c in cases:
 rng=random.Random(c['seed']); offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 for name,run in [('v2',baseline),('v4',candidate)]:
  assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==v for f,v in manifest['files'].items())
  r=run(['red','blue'],scene_seed=c['seed'],source_offset=offset,extra_count=c['extra'],same_red=c['same_red'],feedback='sensor',retry=True)
  row={'scene':c,'offset':offset,'method':name,'success':r['success'],'failure':r['failure'],'base_error_mm':math.dist(r['final_recheck'][0]['actual'][:2],(.56,.1))*1000,'relative_mm':r['criteria']['relative_offset_mm'],'relative_yaw':r['criteria']['relative_yaw_degrees'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'verification':r['verification']};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/tower-v4-new-scenes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
