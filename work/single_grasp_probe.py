"""One-cube physics probe: compare setpoint and interpolated motion, without attachment.
Ground-truth cube pose is used only for measurement; the grasp starts from a known pose.
"""
import math
import pybullet as p
import pybullet_data

def run(source=(.48,-.14), path='forward', smooth=False):
    cid=p.connect(p.DIRECT)
    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath());p.setGravity(0,0,-9.81);p.setTimeStep(1/240);p.setPhysicsEngineParameter(numSolverIterations=150,deterministicOverlappingPairs=1)
        table=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.65,.65,.025]);p.createMultiBody(0,table,basePosition=[.5,0,-.025])
        arm=p.loadURDF('franka_panda/panda.urdf',useFixedBase=True,flags=p.URDF_USE_INERTIA_FROM_FILE)
        for j,q in enumerate([0,-.5,0,-2.,0,1.5,.785]):p.resetJointState(arm,j,q)
        for j in (9,10):p.resetJointState(arm,j,.04);p.changeDynamics(arm,j,lateralFriction=1.5,spinningFriction=.01)
        shape=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.025]*3)
        cube=p.createMultiBody(.06,shape,basePosition=[*source,.025]);p.changeDynamics(cube,-1,lateralFriction=1.2,spinningFriction=.01)
        orn=p.getQuaternionFromEuler([math.pi,0,0]);samples=[]
        def local():
            wp,wo=p.getLinkState(arm,11,computeForwardKinematics=1)[4:6]; cp,co=p.getBasePositionAndOrientation(cube);ip,io=p.invertTransform(wp,wo);return p.multiplyTransforms(ip,io,cp,co)[0]
        def stage(target,finger,n,label,interpolate=False):
            start=p.getLinkState(arm,11,computeForwardKinematics=1)[4]
            for i in range(n):
                # Smoothstep avoids the abrupt velocity change of a direct target.
                a=min(1.,(i+1)/max(1,int(n*.8))) if interpolate else 1.;a=a*a*(3-2*a)
                pos=[start[j]+(target[j]-start[j])*a for j in range(3)]
                q=p.calculateInverseKinematics(arm,11,pos,orn,maxNumIterations=100,residualThreshold=1e-5)
                for j in range(7):p.setJointMotorControl2(arm,j,p.POSITION_CONTROL,targetPosition=q[j],force=150,positionGain=.2,velocityGain=1)
                for j in (9,10):p.setJointMotorControl2(arm,j,p.POSITION_CONTROL,targetPosition=finger,force=50,positionGain=.2)
                p.stepSimulation()
                if label in ('transfer','settle') and i%8==0:
                    lp=p.getContactPoints(bodyA=arm,bodyB=cube,linkIndexA=9);rp=p.getContactPoints(bodyA=arm,bodyB=cube,linkIndexA=10);cp=p.getBasePositionAndOrientation(cube)[0]
                    samples.append({'stage':label,'local':local(),'height':cp[2],'bilateral':bool(lp and rp)})
        x,y=source
        stage([x,y,.30],.04,260,'approach');stage([x,y,.035],.04,300,'descend');stage([x,y,.035],0,250,'grasp');stage([x,y,.20],0,320,'lift')
        ref=local();initial_height=p.getBasePositionAndOrientation(cube)[0][2]
        goals={'forward':[(x+.07,y+.18,.22)],'diagonal':[(x+.10,y+.16,.25)],'turn':[(x-.04,y+.12,.23),(x+.08,y+.18,.23)]}[path]
        for goal in goals:stage(goal,0,380,'transfer',smooth)
        stage(goals[-1],0,240,'settle')
        slips=[math.dist(ref,s['local'])*1000 for s in samples];last=p.getBasePositionAndOrientation(cube)[0]
        return {'source':source,'path':path,'smooth':smooth,'lift_height_mm':initial_height*1000,'final_height_mm':last[2]*1000,'peak_slip_mm':max(slips,default=None),'final_slip_mm':slips[-1] if slips else None,'loss_samples':sum(not s['bilateral'] for s in samples),'samples':len(samples),'retained':initial_height>.12 and last[2]>.12 and all(s['bilateral'] for s in samples),'trace':samples}
    finally:p.disconnect(cid)
