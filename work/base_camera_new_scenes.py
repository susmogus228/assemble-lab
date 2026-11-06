import hashlib,json,math,random
from pathlib import Path
from work.color_tower_guarded_v1 import run as baseline
from work.color_tower_base_camera_v1 import run as candidate
files=['work/color_tower_guarded_v1.py','work/color_tower_base_camera_v1.py','work/hold_guard.py','work/held_camera.py','work/base_camera_highres.py','work/sensors_candidate.py','sensors.py','tower_targets.py','sequence_probe.py']
cases=[{'seed':701,'extra':0,'same_red':False},{'seed':709,'extra':2,'same_red':False},{'seed':719,'extra':4,'same_red':False},{'seed':727,'extra':1,'same_red':True}]
manifest={'files':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files},'cases':cases,'selection':'higher-resolution overhead camera frozen before comparison; same nominal target, motion controller and success criteria','scope':'paired Bullet simulation, fixed shapes; no real hardware validation'}
Path('work/frozen-base-camera-v1').mkdir(exist_ok=True);Path('work/frozen-base-camera-v1/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');rows=[]
for c in cases:
 rng=random.Random(c['seed']);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 for name,run in [('guarded',baseline),('highres',candidate)]:
  assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in manifest['files'].items())
  r=run(['red','blue'],scene_seed=c['seed'],source_offset=offset,extra_count=c['extra'],same_red=c['same_red'],feedback='sensor',retry=True)
  row={'scene':c,'offset':offset,'method':name,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'relative_yaw':r['criteria']['relative_yaw_degrees'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'verification':r['verification'],'base_observations':r['base_observations'],'hold_checks':len(r.get('hold_checks',[]))};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/base-camera-new-scenes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
