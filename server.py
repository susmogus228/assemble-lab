"""Local research server; synchronous Bullet runs are deliberately serialized."""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import json, os
import numpy as np
from assemble import run
from experiment import features
from sequence_probe import run as run_figure
from work.controller_v3 import run as run_figure_fast
from color_assembly import run as run_color
from work.color_contact_candidate import run as run_color_contact
from work.color_push_candidate import run as run_color_push
from work.color_camera_candidate import run as run_color_top_depth
from work.color_tower_v2 import run as run_color_tower
from work.color_tower_base_camera_v1 import run as run_color_highres
from work.color_tower_coupled_v1 import run as run_color_coupled
from work.color_tower_multiview_v5 import run as run_color_multiview
from work.color_tower_surface_v1 import run as run_color_surface
ROOT=Path(__file__).resolve().parent
os.chdir(ROOT/'web')
class Handler(SimpleHTTPRequestHandler):
    def json(self,obj,status=200):
        payload=json.dumps(obj).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(payload))); self.end_headers(); self.wfile.write(payload)
    def do_GET(self):
        if urlsplit(self.path).path=='/api/results':
            path=ROOT/'outputs'/'residual-experiment.json'
            return self.json(json.loads(path.read_text(encoding='utf8')) if path.exists() else {'status':'not available'})
        return super().do_GET()
    def do_POST(self):
        if urlsplit(self.path).path not in ('/api/run','/api/figure','/api/colors'): return self.json({'error':'Not found'},404)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 1<=size<=1024: raise ValueError('Invalid request size')
            data=json.loads(self.rfile.read(size))
            if urlsplit(self.path).path=='/api/colors':
                import random
                selected=data.get('colors',[]); seed=int(data.get('seed',0));layout=data.get('layout','tower')
                if not 0<=seed<=10000 or not isinstance(selected,list): raise ValueError('Invalid colors or seed')
                rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
                method=data.get('retry_method','legacy')
                if method not in ('legacy','contact','push','top_depth','tower_visual','highres_guard','coupled_guard','multiview_guard','surface_guard'):raise ValueError('Invalid retry method')
                if method in ('highres_guard','coupled_guard','multiview_guard','surface_guard') and (layout!='tower' or data.get('feedback','oracle')!='sensor' or len(selected)!=2): raise ValueError('Guarded mode requires two cubes, tower layout and sensor feedback')
                runner=run_color_surface if method=='surface_guard' else run_color_multiview if method=='multiview_guard' else run_color_coupled if method=='coupled_guard' else run_color_highres if method=='highres_guard' else run_color_tower if method=='tower_visual' else run_color_top_depth if method=='top_depth' else run_color_push if method=='push' else run_color_contact if method=='contact' else run_color
                result=runner(selected,layout=layout,source_offset=offset,extra_count=data.get('extra_count',0),feedback=data.get('feedback','oracle'),scene_seed=seed,same_red=data.get('same_red',False),verify=True,retry=data.get('retry',False),occlude=data.get('occlude',False))
                result['retry_method']=method;return self.json(result)
            if urlsplit(self.path).path=='/api/figure':
                layout=data.get('layout','tower'); seed=int(data.get('seed',0)); push=data.get('push',False)
                if not 0<=seed<=10000 or type(push) is not bool: raise ValueError('Invalid seed or push flag')
                import random
                rng=random.Random(seed); offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
                figure_controller=data.get('mode','baseline')
                if figure_controller not in ('baseline','fast'): raise ValueError('Choose a scripted figure controller')
                runner=run_figure_fast if figure_controller=='fast' else run_figure
                result=runner(layout=layout,source_offset=offset,push=push); result.update({'mode':figure_controller,'destination':[.56,.10], 'final_position':result['final_recheck'][len(result['parts'])-1]['actual'], 'target':result['parts'][-1]['target'], 'speed':None, 'robot_contacts':sum(row['robot_contacts'] for row in result['parts']), 'success':result['complete']}); return self.json(result)
            seed=int(data.get('seed',1))
            if seed<0 or seed>10000: raise ValueError('Seed must be between 0 and 10000')
            mode=data.get('mode','baseline')
            if mode not in ('baseline','learned'): raise ValueError('Invalid controller')
            import random
            rng=random.Random(seed)
            src=(round(rng.uniform(.44,.51),4),round(rng.uniform(-.16,-.10),4))
            dest=(round(rng.uniform(.52,.58),4),round(rng.uniform(.07,.13),4)); correction=(0,0)
            if mode=='learned':
                path=ROOT/'outputs'/'residual-experiment.json'
                if not path.exists(): raise ValueError('Trained experiment is not available')
                weights=np.array(json.loads(path.read_text(encoding='utf8'))['weights'])
                correction=np.clip(np.array(features(src,dest))@weights,-.03,.03).tolist()
            result=run(src,dest,correction=correction); result.update({'mode':mode,'correction':correction,'seed':seed})
            return self.json(result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc: return self.json({'error':str(exc)},400)
        except Exception as exc: return self.json({'error':'Simulation failed: '+str(exc)},500)
if __name__=='__main__':
    port=int(os.getenv('ASSEMBLELAB_PORT','8810'))
    print(f'AssembleLab: http://127.0.0.1:{port}/',flush=True)
    HTTPServer(('127.0.0.1',port),Handler).serve_forever()
