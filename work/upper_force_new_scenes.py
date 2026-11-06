import hashlib,json,math,random
from pathlib import Path
from work.color_tower_base_camera_v1 import run as baseline
from work.color_tower_upper_force_v1 import run as candidate
files=['work/color_tower_base_camera_v1.py','work/color_tower_upper_force_v1.py','work/hold_guard.py','work/held_camera.py','work/base_camera_highres.py','work/sensors_candidate.py','sensors.py','tower_targets.py','sequence_probe.py']
cases=[{'seed':809,'extra':0,'same_red':False},{'seed':811,'extra':2,'same_red':False},{'seed':821,'extra':4,'same_red':False},{'seed':823,'extra':1,'same_red':True}]
manifest={'files':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files},'cases':cases,'selection':'8 N upper finger limit selected before fresh paired evaluation; original limit 50 N retained for lower piece. Development included a drop; this experiment tests rather than assumes improvement.','scope':'same simulated cubes, camera and ground-truth success criteria; upper fall based on final height; no hardware claims'}
Path('work/frozen-upper-force-v1').mkdir(exist_ok=True);Path('work/frozen-upper-force-v1/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');rows=[]
for c in cases:
 rng=random.Random(c['seed']);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 for name,run in [('current',baseline),('upper_force_8',candidate)]:
  assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in manifest['files'].items())
  r=run(['red','blue'],scene_seed=c['seed'],source_offset=offset,extra_count=c['extra'],same_red=c['same_red'],feedback='sensor',retry=True)
  checks=r['final_recheck'];row={'scene':c,'offset':offset,'method':name,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'relative_yaw':r['criteria']['relative_yaw_degrees'],'checks':checks,'upper_final_height_mm':checks[1]['actual'][2]*1000,'base_xy_error_mm':math.dist(checks[0]['actual'][:2],(.56,.1))*1000,'unselected':r['unselected_displacement_mm'],'verification':r['verification'],'hold_checks':len(r.get('hold_checks',[]))};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/upper-force-new-scenes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
