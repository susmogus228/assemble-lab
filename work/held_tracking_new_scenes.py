import hashlib,json,math,random
from pathlib import Path
from work.color_tower_v2 import run as baseline
from work.color_tower_held_v2 import run as tracked
files=['work/color_tower_v2.py','work/color_tower_held_v2.py','work/held_camera.py','work/sensors_candidate.py','sensors.py','tower_targets.py','sequence_probe.py']
cases=[{'seed':503,'extra':0,'same_red':False},{'seed':509,'extra':2,'same_red':False},{'seed':521,'extra':4,'same_red':False},{'seed':523,'extra':1,'same_red':True}]
manifest={'files':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files},'cases':cases,'choice':'held_v2 selected before new scenes, as held_v1 dropped a cube during development','scope':'simulated 50 mm axis-aligned cubes; no arbitrary geometry or hardware validation'}
Path('work/frozen-held-v2').mkdir(exist_ok=True);Path('work/frozen-held-v2/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
rows=[]
for c in cases:
 rng=random.Random(c['seed']);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 for name,run in [('baseline',baseline),('tracked',tracked)]:
  assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in manifest['files'].items())
  r=run(['red','blue'],scene_seed=c['seed'],source_offset=offset,extra_count=c['extra'],same_red=c['same_red'],feedback='sensor',retry=True)
  tr=r.get('held_tracking',[]);valid=[x for x in tr if x['estimate'] is not None];errors=[math.dist(x['estimate'],x['truth'][:2])*1000 for x in valid]
  row={'scene':c,'offset':offset,'method':name,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'relative_yaw':r['criteria']['relative_yaw_degrees'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'tracking_count':len(tr),'tracking_valid':len(valid),'tracking_mean_error_mm':sum(errors)/len(errors) if errors else None,'tracking_max_error_mm':max(errors) if errors else None,'diagnostics':r['diagnostics']};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/held-tracking-new-scenes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
