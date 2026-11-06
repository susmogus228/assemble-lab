"""Two-part sequential assembly physics probe with fixed plate and no object constraints."""
import json, math
from pathlib import Path
import pybullet as p
import pybullet_data
from assemble import assess_placement

ROOT=Path(__file__).resolve().parent

def evaluate_figure(states, targets, layout):
    checks=[]
    for item, target in zip(states, targets):
        error=math.dist(item['position'][:2],target[:2])*1000
        height=abs(item['position'][2]-target[2])*1000
        angle=abs(((item['yaw']+45)%90)-45)
        checks.append(error<=3 and height<=4 and angle<=3 and item['tilt']<=3 and item['speed']<.01 and item['robot_contacts']==0 and item['supported'])
    relative=math.dist(states[0]['position'][:2],states[1]['position'][:2])*1000 if layout=='tower' and len(states)==2 else None
    relative_yaw=abs(((states[1]['yaw']-states[0]['yaw']+45)%90)-45) if len(states)==2 else None
    success=len(states)==len(targets)==2 and all(checks) and (relative is None or relative<=3) and relative_yaw is not None and relative_yaw<=3
    return {'success':success,'piece_checks':checks,'relative_offset_mm':relative,'relative_yaw_degrees':relative_yaw,'position_tolerance_mm':3,'rotation_tolerance_degrees':3}

def run(layout='tower', source_offset=(0,0), push=False):
    if layout not in ('tower','row'): raise ValueError('Invalid figure')
    cid=p.connect(p.DIRECT)
    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath());p.setGravity(0,0,-9.81);p.setTimeStep(1/240)
        p.setPhysicsEngineParameter(numSolverIterations=150,deterministicOverlappingPairs=1)
        table=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.65,.65,.025]);p.createMultiBody(0,table,basePosition=[.5,0,-.025])
        arm=p.loadURDF('franka_panda/panda.urdf',useFixedBase=True,flags=p.URDF_USE_INERTIA_FROM_FILE)
        for j,q in enumerate([0,-.5,0,-2.,0,1.5,.785]):p.resetJointState(arm,j,q)
        for j in (9,10):p.resetJointState(arm,j,.04);p.changeDynamics(arm,j,lateralFriction=1.5,spinningFriction=.01)
        plate=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.07,.07,.0125]);p.createMultiBody(0,plate,basePosition=[.56,.10,.0125])
        shape=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.025]*3)
        initial= ((.43,-.14,.025),(.53,-.14,.025)) if push else ((.48,-.14,.025),(.45,-.22,.025))
        parts=[p.createMultiBody(.06,shape,basePosition=(pos[0]+source_offset[0],pos[1]+source_offset[1],pos[2])) for pos in initial]
        for b in parts:p.changeDynamics(b,-1,lateralFriction=1.2,spinningFriction=.01)
        orn=p.getQuaternionFromEuler([math.pi,0,0]);out=[];frames=[];cube_contact_steps=0
        def stage(pos,finger,n,label,part_number):
            nonlocal cube_contact_steps
            for step in range(n):
                q=p.calculateInverseKinematics(arm,11,pos,orn,maxNumIterations=100,residualThreshold=1e-5)
                for j in range(7):p.setJointMotorControl2(arm,j,p.POSITION_CONTROL,targetPosition=q[j],force=150,positionGain=.2,velocityGain=1)
                for j in (9,10):p.setJointMotorControl2(arm,j,p.POSITION_CONTROL,targetPosition=finger,force=50,positionGain=.2)
                p.stepSimulation()
                if label=='push' and p.getContactPoints(parts[0],parts[1]):cube_contact_steps+=1
                if step % 8 == 0:
                    states=[p.getBasePositionAndOrientation(arm)] + [p.getLinkState(arm,j,computeForwardKinematics=1)[4:6] for j in range(p.getNumJoints(arm))]
                    frames.append({'links':states,'parts':[p.getBasePositionAndOrientation(b) for b in parts],'part':p.getBasePositionAndOrientation(parts[part_number-1]),'stage':label,'part_number':part_number})
        push_info={'requested':push,'contact_steps':0,'displacement_mm':0.0,'second_displacement_mm':0.0,'cube_contact_steps':0}
        for i,part in enumerate(parts):
            pos,_=p.getBasePositionAndOrientation(part);x,y=pos[:2]
            target=[.53,.10,.05] if layout=='row' and i==0 else [.585,.10,.05] if layout=='row' else [.56,.10,.05] if i==0 else [.56,.10,.10]
            stage([x,y,.30],.04,360,'approach',i+1);stage([x,y,.035],.04,360,'descend',i+1);stage([x,y,.035],0,300,'grasp',i+1)
            if push and i==0:
                before=p.getBasePositionAndOrientation(part)[0]; second_before=p.getBasePositionAndOrientation(parts[1])[0]
                for k in range(14):
                    stage([x+.005*(k+1),y,.040],0,65,'push',i+1)
                    if p.getContactPoints(arm,part): push_info['contact_steps']+=1
                after=p.getBasePositionAndOrientation(part)[0]
                push_info['displacement_mm']=math.dist(before[:2],after[:2])*1000
                second_after=p.getBasePositionAndOrientation(parts[1])[0]
                push_info['second_displacement_mm']=math.dist(second_before[:2],second_after[:2])*1000
                push_info['cube_contact_steps']=cube_contact_steps
                x,y=p.getLinkState(arm,11,computeForwardKinematics=1)[4][:2]
            stage([x,y,.20],0,400,'lift',i+1)
            tool=p.getLinkState(arm,11,computeForwardKinematics=1)[4];held,_=p.getBasePositionAndOrientation(part)
            dx=target[0]-(held[0]-tool[0])-.012;dy=target[1]-(held[1]-tool[1])-.020;height=.060+(.05*i if layout=='tower' else 0)
            stage([dx,dy,.25],0,480,'transfer',i+1)
            # Use simulated part pose as feedback while held. This is an oracle, not camera sensing.
            for correction_step in range(7):
                held,held_orientation=p.getBasePositionAndOrientation(part)
                tool=p.getLinkState(arm,11,computeForwardKinematics=1)[4]
                dx=tool[0]+target[0]-held[0];dy=tool[1]+target[1]-held[1]
                stage([dx,dy,height+.05],0,320,'align',i+1)
            dy-=(.021 if i==0 else .014)
            stage([dx,dy,height],0,400,'place',i+1);stage([dx,dy,height],.04,240,'release',i+1)
            for retreat_step in range(16): stage([dx,dy,height+(.24-height)*(retreat_step+1)/16],.04,24,'retreat',i+1)
            for settle_step in range(240):
                p.stepSimulation()
                if settle_step % 8 == 0:
                    states=[p.getBasePositionAndOrientation(arm)] + [p.getLinkState(arm,j,computeForwardKinematics=1)[4:6] for j in range(p.getNumJoints(arm))]
                    frames.append({'links':states,'parts':[p.getBasePositionAndOrientation(b) for b in parts],'part':p.getBasePositionAndOrientation(part),'stage':'settle','part_number':i+1})
            actual,_=p.getBasePositionAndOrientation(part);velocity,_=p.getBaseVelocity(part);speed=math.sqrt(sum(v*v for v in velocity));contacts=len(p.getContactPoints(arm,part))
            out.append({'part':i+1,'actual':actual,'target':target,'success':assess_placement(actual,target,speed,contacts),'robot_contacts':contacts})
            # Continue the second attempt in simulation even if the first missed; report final failure honestly.
        final=[]; states=[]
        targets=[[.56,.10,.05],[.56,.10,.10]] if layout=='tower' else [[.53,.10,.05],[.585,.10,.05]]
        for i,part in enumerate(parts):
            actual,orientation=p.getBasePositionAndOrientation(part);velocity,_=p.getBaseVelocity(part)
            roll,pitch,yaw=p.getEulerFromQuaternion(orientation)
            support=any(c[2] == (parts[0] if layout=='tower' and i==1 else 2) for c in p.getContactPoints(bodyA=part))
            states.append({'position':actual,'yaw':math.degrees(yaw),'tilt':math.degrees(math.hypot(roll,pitch)),'speed':math.sqrt(sum(v*v for v in velocity)),'robot_contacts':len(p.getContactPoints(arm,part)),'supported':support})
        criteria=evaluate_figure(states,targets,layout)
        final=[{'part':i+1,'actual':state['position'],'success':criteria['piece_checks'][i],'yaw':state['yaw'],'supported':state['supported']} for i,state in enumerate(states)]
        return {'frames':frames,'complete':criteria['success'],'criteria':criteria,'parts':out,'final_recheck':final,'layout':layout,'targets':targets,'push':push_info,'note':'Scripted controller using privileged simulation poses; no trained sequence policy.'}
    finally:p.disconnect(cid)
if __name__=='__main__':
    result=run();(ROOT/'outputs'/'two-part-probe.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in result.items() if k!='frames'},indent=2))





