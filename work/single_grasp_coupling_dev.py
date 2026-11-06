import json
from pathlib import Path
from work.single_grasp_coupling_probe import run
cases=[((.48,-.14),'forward'),((.46,-.16),'diagonal'),((.50,-.12),'turn')];out=[]
for source,path in cases:
 for coupled in (False,True):
  r=run(source,path,False,coupled);out.append(r);print(json.dumps({k:v for k,v in r.items() if k!='trace'}),flush=True)
Path('outputs/single-grasp-coupling-development.json').write_text(json.dumps(out,indent=2),encoding='utf8')
