"""Bullet pick-and-place feasibility trial. No constraints attach parts to the robot."""
import json, math, time
from pathlib import Path
import pybullet as p
import pybullet_data

ROOT = Path(__file__).resolve().parent

def assess_placement(actual, target, speed, robot_contacts):
    return (math.dist(actual[:2], target[:2]) <= .012 and abs(actual[2]-target[2]) <= .008
            and speed < .01 and robot_contacts == 0)

def run(source=(.48, -.14), destination=(.56,.10), miss=False, correction=(0,0), shape='cube'):
    if shape not in ('cube','cylinder','sphere'): raise ValueError('Unsupported shape')
    cid = p.connect(p.DIRECT)
    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,-9.81); p.setTimeStep(1/240)
        p.setPhysicsEngineParameter(numSolverIterations=150, deterministicOverlappingPairs=1)
        table = p.createCollisionShape(p.GEOM_BOX, halfExtents=[.65,.65,.025])
        p.createMultiBody(0,table,basePosition=[.5,0,-.025])
        arm = p.loadURDF('franka_panda/panda.urdf',useFixedBase=True,flags=p.URDF_USE_INERTIA_FROM_FILE)
        for j,q in enumerate([0,-.5,0,-2.,0,1.5,.785]): p.resetJointState(arm,j,q)
        for j in (9,10):
            p.resetJointState(arm,j,.04); p.changeDynamics(arm,j,lateralFriction=1.5,spinningFriction=.01)
        base_col=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.07,.07,.0125])
        base=p.createMultiBody(0,base_col,basePosition=[*destination,.0125])
        part_col=(p.createCollisionShape(p.GEOM_BOX,halfExtents=[.025]*3) if shape=='cube' else p.createCollisionShape(p.GEOM_CYLINDER,radius=.025,height=.05) if shape=='cylinder' else p.createCollisionShape(p.GEOM_SPHERE,radius=.025))
        part=p.createMultiBody(.06,part_col,basePosition=[*source,.025])
        p.changeDynamics(part,-1,lateralFriction=1.2,spinningFriction=.01)
        orn=p.getQuaternionFromEuler([math.pi,0,0]); frames=[]; contact_steps={'both':0,'left_only':0,'right_only':0}
        def stage(target, fingers, steps, label):
            for k in range(steps):
                q=p.calculateInverseKinematics(arm,11,target,orn,maxNumIterations=100,residualThreshold=1e-5)
                for j in range(7): p.setJointMotorControl2(arm,j,p.POSITION_CONTROL,targetPosition=q[j],force=150,positionGain=.2,velocityGain=1)
                for j in (9,10): p.setJointMotorControl2(arm,j,p.POSITION_CONTROL,targetPosition=fingers,force=50,positionGain=.2)
                p.stepSimulation()
                left=bool(p.getContactPoints(arm,part,linkIndexA=9)); right=bool(p.getContactPoints(arm,part,linkIndexA=10))
                if left and right: contact_steps['both']+=1
                elif left: contact_steps['left_only']+=1
                elif right: contact_steps['right_only']+=1
                if k%8 == 0:
                    states=[p.getBasePositionAndOrientation(arm)] + [p.getLinkState(arm,i,computeForwardKinematics=1)[4:6] for i in range(p.getNumJoints(arm))]
                    frames.append({'links':states,'part':p.getBasePositionAndOrientation(part),'stage':label})
        x,y=source; dx,dy=destination; x += .12 if miss else 0
        stage([x,y,.30],.04,360,'approach'); stage([x,y,.035],.04,360,'descend')
        stage([x,y,.035],0,300,'grasp'); stage([x,y,.20],0,400,'lift')
        # Privileged simulation pose is used to compensate for object slip in the gripper.
        tool=p.getLinkState(arm,11,computeForwardKinematics=1)[4]
        held,_=p.getBasePositionAndOrientation(part)
        cx=dx-(held[0]-tool[0])+correction[0]; cy=dy-(held[1]-tool[1])+correction[1]
        stage([cx,cy,.20],0,480,'transfer'); stage([cx,cy,.060],0,400,'place')
        stage([cx,cy,.060],.04,240,'release'); stage([cx,cy,.25],.04,360,'retreat')
        for _ in range(240): p.stepSimulation()
        pos,quat=p.getBasePositionAndOrientation(part); vel,_=p.getBaseVelocity(part)
        speed=math.sqrt(sum(v*v for v in vel)); contacts=len(p.getContactPoints(arm,part))
        target=[dx,dy,.05]; success=assess_placement(pos,target,speed,contacts)
        return {'success':success,'source':source,'destination':destination,'final_position':pos,'target':target,'speed':speed,'robot_contacts':contacts,'contact_steps':contact_steps,'shape':shape,'frames':frames}
    finally: p.disconnect(cid)

if __name__=='__main__':
    t=time.perf_counter(); result=run(); result['elapsed_seconds']=round(time.perf_counter()-t,2)
    (ROOT/'outputs'/'physics-smoke.json').write_text(json.dumps(result),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='frames'},indent=2))


