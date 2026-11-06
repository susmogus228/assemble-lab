import json
import pybullet as p
import assemble
original_step=p.stepSimulation
original_create=p.createMultiBody
ids=[]; contacts={'both':0,'left_only':0,'right_only':0}; closest=[]
def create(*args,**kwargs):
    body=original_create(*args,**kwargs)
    mass=args[0] if args else kwargs.get('baseMass')
    if mass==.06:ids.append(body)
    return body
def step(*args,**kwargs):
    result=original_step(*args,**kwargs)
    if ids:
        part=ids[-1]; arm=1
        left=bool(p.getContactPoints(arm,part,linkIndexA=9));right=bool(p.getContactPoints(arm,part,linkIndexA=10))
        if left and right:contacts['both']+=1
        elif left:contacts['left_only']+=1
        elif right:contacts['right_only']+=1
    return result
p.createMultiBody=create;p.stepSimulation=step
r=assemble.run();print(json.dumps({'success':r['success'],'contact_steps':contacts,'final_robot_contacts':r['robot_contacts']},indent=2))
