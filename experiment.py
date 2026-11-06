"""Small research experiment: learn residual target corrections from physical runs."""
import json, random, time
from pathlib import Path
import numpy as np
from assemble import run

ROOT=Path(__file__).resolve().parent

def features(source,dest):
    return [1, source[0]-.48, source[1]+.12, dest[0]-.55, dest[1]-.10]

def scenes(seed,n):
    r=random.Random(seed)
    return [((round(r.uniform(.44,.51),4),round(r.uniform(-.16,-.10),4)),
             (round(r.uniform(.52,.58),4),round(r.uniform(.07,.13),4))) for _ in range(n)]

def stripped(x): return {k:v for k,v in x.items() if k!='frames'}

def train():
    training=scenes(320,20); holdout=scenes(823,10)
    rows=[]
    for source,dest in training:
        result=run(source,dest)
        error=[result['final_position'][i]-dest[i] for i in range(2)]
        # Failed grasps are not valid placement demonstrations.
        if result['final_position'][2]>.043 and max(abs(v) for v in error)<.05:
            rows.append((features(source,dest),[-v for v in error]))
    if len(rows)<5: raise RuntimeError('Insufficient valid placement demonstrations')
    X=np.array([r[0] for r in rows]); y=np.array([r[1] for r in rows])
    regularizer=np.diag([1e-6,.001,.001,.001,.001])
    weights=np.linalg.solve(X.T@X+regularizer,X.T@y)
    cases=[]
    for source,dest in holdout:
        baseline=run(source,dest)
        correction=np.clip(np.array(features(source,dest))@weights,-.03,.03).tolist()
        learned=run(source,dest,correction=correction)
        cases.append({'baseline':stripped(baseline),'learned':stripped(learned),'correction':correction})
    summary={'method':'ridge regression on placement residuals','input':'privileged source and destination positions in simulation','train_generated':len(training),'train_usable':len(rows),'holdout':len(cases),'baseline_success':sum(c['baseline']['success'] for c in cases),'learned_success':sum(c['learned']['success'] for c in cases),'weights':weights.tolist(),'cases':cases,'note':'Single-part placement; separate holdout locations; not a learned multi-step assembly policy or vision system.'}
    (ROOT/'outputs'/'residual-experiment.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('cases','weights')},indent=2),flush=True)

if __name__=='__main__': train()
