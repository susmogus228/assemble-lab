"""Color-selective prototype with calibrated simulated RGB-D and a wrist-mounted ray."""
import math, random
import pybullet as p
import pybullet_data
from work.held_camera import snapshot as side_snapshot, held_center
from work.held_camera_visible import snapshot as checked_side_snapshot
from work.hold_guard import stable_grasp, bounded_step
from work.reobserve_policy_v2 import reobserve_targets, has_unexpected_contact
from work.held_camera_multiview import combine_centers
from work.held_tracking_geometry import HeldTracker

class HoldStopped(Exception):
    pass
from sensors import camera_snapshot
from work.base_camera_highres import camera_snapshot as camera_verify_snapshot
from sequence_probe import evaluate_figure
from tower_targets import choose_base_observation
from contact_feedback import center_from_contacts

COLORS={'red':[.95,.05,.03,1], 'blue':[.03,.15,.95,1], 'green':[.03,.9,.05,1], 'yellow':[.95,.85,.03,1], 'magenta':[.9,.03,.8,1], 'cyan':[.03,.8,.85,1]}
PICKABLE=('red','blue','red2')
EXTRAS=[('green',(.36,-.12,.025)),('yellow',(.35,-.27,.025)),('magenta',(.58,-.26,.025)),('cyan',(.59,-.13,.025))]

def run(selected,layout='tower',source_offset=(0,0),extra_count=0,feedback='oracle',scene_seed=0,same_red=False,verify=True,retry=False,occlude=False):
    if not selected or len(selected)>2 or len(set(selected))!=len(selected) or any(c not in PICKABLE for c in selected):raise ValueError('Choose one or two different available colors')
    if layout not in ('tower','row'):raise ValueError('Invalid layout')
    if type(extra_count) is not int or not 0<=extra_count<=4:raise ValueError('Extra count must be between 0 and 4')
    if feedback not in ('oracle','sensor'):raise ValueError('Invalid feedback mode')
    if type(same_red) is not bool or type(verify) is not bool or type(retry) is not bool or type(occlude) is not bool:raise ValueError('Invalid scene options')
    if same_red and extra_count<1:raise ValueError('Two red cubes need at least one extra cube')
    if 'red2' in selected and not same_red:raise ValueError('Second red cube is not present')
    if occlude and not same_red:raise ValueError('Occlusion scene needs two red cubes')
    cid=p.connect(p.DIRECT)
    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath());p.setGravity(0,0,-9.81);p.setTimeStep(1/240);p.setPhysicsEngineParameter(numSolverIterations=150,deterministicOverlappingPairs=1)
        col=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.65,.65,.025]);vis=p.createVisualShape(p.GEOM_BOX,halfExtents=[.65,.65,.025],rgbaColor=[.23,.23,.23,1]);p.createMultiBody(0,col,vis,basePosition=[.5,0,-.025])
        arm=p.loadURDF('franka_panda/panda.urdf',useFixedBase=True,flags=p.URDF_USE_INERTIA_FROM_FILE)
        # Couple only the two Panda finger joints. The cube remains a free rigid body.
        gear=p.createConstraint(arm,9,arm,10,p.JOINT_GEAR,[1,0,0],[0,0,0],[0,0,0])
        p.changeConstraint(gear,gearRatio=-1,erp=.1,maxForce=50)
        for j,q in enumerate([0,-.5,0,-2.,0,1.5,.785]):p.resetJointState(arm,j,q)
        for j in (9,10):p.resetJointState(arm,j,.04);p.changeDynamics(arm,j,lateralFriction=1.5,spinningFriction=.01)
        plate_col=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.07,.07,.0125]);plate_vis=p.createVisualShape(p.GEOM_BOX,halfExtents=[.07,.07,.0125],rgbaColor=[.45,.45,.45,1]);plate=p.createMultiBody(0,plate_col,plate_vis,basePosition=[.56,.10,.0125])
        shape=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.025]*3);parts={}
        rng=random.Random(scene_seed)
        extra_objects=list(EXTRAS[:extra_count])
        if same_red:extra_objects[0]=('red2',(.48,-.14,.075) if occlude else extra_objects[0][1])
        for color,pos in [('red',(.48,-.14,.025)),('blue',(.45,-.27,.025))]+extra_objects:
            jitter=(rng.uniform(-.006,.006),rng.uniform(-.006,.006)) if scene_seed and not (occlude and color in ('red','red2')) else (0,0)
            v=p.createVisualShape(p.GEOM_BOX,halfExtents=[.025]*3,rgbaColor=COLORS['red' if color=='red2' else color]);part=p.createMultiBody(.06,shape,v,basePosition=[pos[0]+source_offset[0]+jitter[0],pos[1]+source_offset[1]+jitter[1],pos[2]])
            p.changeDynamics(part,-1,lateralFriction=1.2,spinningFriction=.01);parts[color]=part
        colors=list(parts);frames=[];inspections=[];out=[];failure=None;verification=[];anchors={};diagnostics={};base_observations=[];held_tracking=[];hold_checks=[];reobservations=[]
        orn=p.getQuaternionFromEuler([math.pi,0,0]); start_positions={c:p.getBasePositionAndOrientation(b)[0] for c,b in parts.items()}
        def stage(pos,finger,n,label,index,ray=None):
            recovery_start=p.getLinkState(arm,11,computeForwardKinematics=1)[4] if label=='camera recovery' else None
            lost=0
            for step in range(n):
                progress=(step+1)/n
                commanded=[recovery_start[j]+(pos[j]-recovery_start[j])*progress for j in range(3)] if recovery_start is not None else pos
                q=p.calculateInverseKinematics(arm,11,commanded,orn,maxNumIterations=100,residualThreshold=1e-5)
                for j in range(7):p.setJointMotorControl2(arm,j,p.POSITION_CONTROL,targetPosition=q[j],force=150,positionGain=.2,velocityGain=1)
                for j in (9,10):p.setJointMotorControl2(arm,j,p.POSITION_CONTROL,targetPosition=finger,force=50,positionGain=.2)
                p.stepSimulation()
                if label=='camera recovery':
                    arm_contacts=[{'body':c[2]} for c in p.getContactPoints(bodyA=arm)]
                    held_contacts=[{'body':c[2]} for c in p.getContactPoints(bodyA=hit[0])]
                    if has_unexpected_contact(arm_contacts,arm,hit[0]) or has_unexpected_contact(held_contacts,hit[0],arm):
                        raise HoldStopped('Unexpected contact during camera recovery')
                    left=p.getContactPoints(bodyA=arm,bodyB=hit[0],linkIndexA=9)
                    right=p.getContactPoints(bodyA=arm,bodyB=hit[0],linkIndexA=10)
                    lost=0 if left and right else lost+1
                    if lost>=4:raise HoldStopped('Grasp lost during camera recovery')
                if step%8==0:
                    links=[p.getBasePositionAndOrientation(arm)] + [p.getLinkState(arm,j,computeForwardKinematics=1)[4:6] for j in range(p.getNumJoints(arm))]
                    f={'links':links,'parts':[p.getBasePositionAndOrientation(parts[c]) for c in colors],'stage':label,'part_number':index+1,'active_color':selected[index]}
                    if ray is not None:
                        lp,lo=links[12]; start,_=p.multiplyTransforms(lp,lo,[.065,0,-.04],[0,0,0,1]);end,_=p.multiplyTransforms(lp,lo,[.065,0,.36],[0,0,0,1]);h=p.rayTest(start,end)[0];f['ray']=[start,h[3] if h[0]!=-1 else end]
                    frames.append(f)
            if label in ('fine align','place','release','retreat'):
                obj_pos,obj_rot=p.getBasePositionAndOrientation(parts[selected[index]])
                diagnostics.setdefault(selected[index],{})[label]={'position':list(obj_pos),'yaw_degrees':math.degrees(p.getEulerFromQuaternion(obj_rot)[2])}
        try:
            for index,color in enumerate(selected):
                base_point=None
                if index:stage([.30,.21,.38],.04,300,'camera reposition',index)
                if index==1 and layout=='tower':
                    stage([.30,.21,.38],.04,1,'base observation',index)
                    base_snap=camera_verify_snapshot();base_color_name='red' if selected[0]=='red2' else selected[0]
                    base_candidates=base_snap.get('instances',{}).get(base_color_name,[])
                    base=choose_base_observation(base_candidates,[.56,.10],.035)
                    base_observations.append({'color':selected[0],'point':base['point'] if base else None,'candidates':len(base_candidates)})
                    if base is None:
                        failure='Lower cube not uniquely visible near the target';break
                    base_point=base['point']
                snap=camera_snapshot()
                base_color='red' if color=='red2' else color
                candidates=snap.get('instances',{}).get(base_color,[])
                if not candidates and base_color in snap['detections']:candidates=[snap['detections'][base_color]]
                if same_red and base_color=='red' and not anchors:
                    reds=sorted(snap.get('instances',{}).get('red',[]),key=lambda a:a['point'][0])
                    if len(reds)==2:anchors={'red2':reds[0]['point'], 'red':reds[1]['point']}
                if same_red and base_color=='red':
                    det=min(candidates,key=lambda a:math.dist(a['point'][:2],anchors[color][:2])) if color in anchors and candidates else None
                    if det and math.dist(det['point'][:2],anchors[color][:2])>.04:det=None
                else:det=snap['detections'].get(base_color)
                inspection={'color':color,'camera':snap['image'],'detections':snap['detections'],'laser':None};inspections.append(inspection)
                if not det:failure=f'Camera did not detect {color}';break
                x,y,_=det['point'];stage([x-.065,y,.22],.04,360,'laser scan',index,ray=True)
                lp,lo=p.getLinkState(arm,11,computeForwardKinematics=1)[4:6];start,_=p.multiplyTransforms(lp,lo,[.065,0,-.04],[0,0,0,1]);end,_=p.multiplyTransforms(lp,lo,[.065,0,.36],[0,0,0,1]);hit=p.rayTest(start,end)[0]
                point=hit[3];valid=hit[0]!=-1 and point[2]>.035 and math.dist(point[:2],(x,y))<.03
                inspection['laser']={'hit':bool(valid),'point':list(point) if hit[0]!=-1 else None}
                if not valid:failure=f'Laser could not confirm {color} at the detected point';break
                x,y=point[:2];target=([.56,.10,.05] if index==0 else [.56,.10,.10]) if layout=='tower' else ([.53,.10,.05] if index==0 else [.585,.10,.05])
                nominal_target=list(target)
                if base_point is not None:target=[base_point[0],base_point[1],.10]
                part=parts[color] # Object identity is used for evaluation; oracle mode also reads its pose.
                stage([x,y,.30],.04,260,'approach',index);stage([x,y,.035],.04,300,'descend',index);stage([x,y,.035],0,250,'grasp',index)
                grasp_tool=p.getLinkState(arm,11,computeForwardKinematics=1)[4]
                assumed_offset=(x-grasp_tool[0],y-grasp_tool[1],-.01)
                tracker=HeldTracker(max_missing=2)
                def observe_hold(label):
                    samples=[]
                    for _ in range(3):
                        p.stepSimulation()
                        left=p.getContactPoints(bodyA=arm,bodyB=hit[0],linkIndexA=9)
                        right=p.getContactPoints(bodyA=arm,bodyB=hit[0],linkIndexA=10)
                        samples.append((sum(c[9] for c in left),sum(c[9] for c in right)))
                    tool_pos=p.getLinkState(arm,11,computeForwardKinematics=1)[4]
                    if index==1:
                        measured,tracking_mode=tracker.update(checked_side_snapshot('side_x').get(base_color,[]),checked_side_snapshot('side_y').get(base_color,[]),tool_pos)
                    else:
                        measured=held_center(side_snapshot('side_x').get(base_color,[]),tool_pos);tracking_mode='single'
                    if index==1 and label=='lift' and tracking_mode=='conflict' and stable_grasp(samples):
                        for waypoint in reobserve_targets(tool_pos):
                            attempt={'stage':label,'before':list(tool_pos),'target':waypoint,'result':'moving'}
                            reobservations.append(attempt)
                            stage(waypoint,0,160,'camera recovery',index)
                            tool_pos=p.getLinkState(arm,11,computeForwardKinematics=1)[4]
                            samples=[]
                            for _ in range(3):
                                p.stepSimulation()
                                left=p.getContactPoints(bodyA=arm,bodyB=hit[0],linkIndexA=9)
                                right=p.getContactPoints(bodyA=arm,bodyB=hit[0],linkIndexA=10)
                                samples.append((sum(c[9] for c in left),sum(c[9] for c in right)))
                            measured,tracking_mode=tracker.update(checked_side_snapshot('side_x').get(base_color,[]),checked_side_snapshot('side_y').get(base_color,[]),tool_pos)
                            attempt['after']=list(tool_pos);attempt['result']=tracking_mode
                            if not stable_grasp(samples):raise HoldStopped('Grasp lost after camera recovery')
                            if measured is not None:break
                    accepted=stable_grasp(samples) and measured is not None
                    hold_checks.append({'color':color,'stage':label,'accepted':accepted,'bilateral':stable_grasp(samples),'camera':measured is not None,'tracking_mode':tracking_mode,'forces':samples})
                    # Truth is for evaluation only, never used for the decision.
                    truth=p.getBasePositionAndOrientation(part)[0]
                    held_tracking.append({'color':color,'estimate':list(measured) if measured else None,'truth':list(truth),'tracking_mode':tracking_mode})
                    if not accepted:raise HoldStopped('Grasp or held-object camera observation lost during '+label)
                    return measured,tool_pos
                stage([x,y,.20],0,320,'lift',index)
                held,tool=observe_hold('lift')
                dx=target[0]-(held[0]-tool[0])-.012;dy=target[1]-(held[1]-tool[1])-.020;height=.060+(.05*index if layout=='tower' else 0)
                stage([dx,dy,.25],0,380,'transfer',index)
                for _ in range(10):
                    held,tool=observe_hold('align')
                    dx,dy=bounded_step(held,tool[:2],target[:2])
                    stage([dx,dy,height+.05],0,100,'align',index)
                for k in range(1,7):
                    held,tool=observe_hold('descent')
                    dx,dy=bounded_step(held,tool[:2],target[:2])
                    stage([dx,dy,height+.05*(1-k/6)],0,80,'controlled descent',index)
                observe_hold('before release')
                stage([dx,dy,height],.04,240,'release',index)
                for k in range(16):stage([dx,dy,height+(.24-height)*(k+1)/16],.04,24,'retreat',index)
                stage([dx,dy,.24],.04,240,'settle',index)
                if verify:
                    stage([.30,.21,.38],.04,240,'verify view',index)
                    verification_snap=camera_verify_snapshot();visible=verification_snap.get('instances',{}).get(base_color,[])
                    if not visible and base_color in verification_snap['detections']:visible=[verification_snap['detections'][base_color]]
                    ambiguous_same_color=same_red and base_color=='red' and any(c in ('red','red2') for c in selected[:index])
                    nearest=min(visible,key=lambda a:math.dist(a['point'][:2],target[:2])) if visible and not ambiguous_same_color else None
                    measured=math.dist(nearest['point'][:2],target[:2])*1000 if nearest else None
                    check={'color':color,'visible':bool(nearest),'xy_error_mm':measured,'retried':False,'after_error_mm':None,'ambiguity':ambiguous_same_color}
                    verification.append(check)
                    if retry and index == 0 and nearest and 6<measured<35:
                        check['retried']=True
                        vx,vy,_=nearest['point'];stage([vx-.065,vy,.22],.04,250,'verify laser',index,ray=True)
                        lp,lo=p.getLinkState(arm,11,computeForwardKinematics=1)[4:6];start,_=p.multiplyTransforms(lp,lo,[.065,0,-.04],[0,0,0,1]);end,_=p.multiplyTransforms(lp,lo,[.065,0,.36],[0,0,0,1]);hit=p.rayTest(start,end)[0]
                        if hit[0]!=-1 and math.dist(hit[3][:2],(vx,vy))<.03 and hit[3][2]>.035:
                            # Plan only from the camera and wrist range measurement. The Bullet body
                            # identifier acts as an idealized contact sensor, not a position source.
                            dx=target[0]-vx;dy=target[1]-vy;distance=math.hypot(dx,dy)
                            if distance>1e-6:
                                ux,uy=dx/distance,dy/distance;startx=vx-ux*.075;starty=vy-uy*.075
                                z=target[2]+.01
                                stage([startx,starty,.25],0,240,'correct approach',index)
                                stage([startx,starty,z],0,240,'correct descend',index)
                                touched=False;touchpos=None
                                for push_step in range(18):
                                    px=startx+ux*.005*(push_step+1);py=starty+uy*.005*(push_step+1)
                                    stage([px,py,z],0,30,'correct contact search',index)
                                    if p.getContactPoints(bodyA=arm,bodyB=hit[0]):touched=True;touchpos=(px,py);break
                                check['push_contact']=touched
                                if touched:
                                    amount=min(.012,distance*.65)
                                    stage([touchpos[0]+ux*amount,touchpos[1]+uy*amount,z],0,100,'correct push',index)
                                else:check['retry_error']='Pusher did not make contact'
                                tool=p.getLinkState(arm,11,computeForwardKinematics=1)[4]
                                for k in range(12):stage([tool[0],tool[1],z+(.24-z)*(k+1)/12],0,20,'correct retreat',index)
                                stage([.30,.21,.38],.04,240,'retry verify view',index)
                                after_snap=camera_verify_snapshot();after_candidates=after_snap.get('instances',{}).get(base_color,[])
                                if after_candidates:check['after_error_mm']=min(math.dist(d['point'][:2],target[:2])*1000 for d in after_candidates)
                        else:check['retry_error']='Laser did not confirm the placed item'
                actual,_=p.getBasePositionAndOrientation(part);out.append({'color':color,'target':nominal_target,'actual':actual})
        except HoldStopped as exc:
            failure=str(exc)
        states=[]
        for index,color in enumerate(selected):
            part=parts[color];position,orientation=p.getBasePositionAndOrientation(part);velocity,_=p.getBaseVelocity(part);roll,pitch,yaw=p.getEulerFromQuaternion(orientation);supported=bool(p.getContactPoints(bodyA=part,bodyB=parts[selected[0]] if layout=='tower' and index==1 else plate))
            states.append({'position':position,'yaw':math.degrees(yaw),'tilt':math.degrees(math.hypot(roll,pitch)),'speed':math.sqrt(sum(v*v for v in velocity)),'robot_contacts':len(p.getContactPoints(arm,part)),'supported':supported})
        if len(out)==len(selected) and len(selected)==2:criteria=evaluate_figure(states,[x['target'] for x in out],layout)
        elif len(out)==len(selected)==1:
            v=states[0];t=out[0]['target'];ok=math.dist(v['position'][:2],t[:2])<=.003 and abs(v['position'][2]-t[2])<=.004 and abs(((v['yaw']+45)%90)-45)<=3 and v['tilt']<=3 and v['speed']<.01 and v['robot_contacts']==0 and v['supported'];criteria={'success':ok,'piece_checks':[ok],'relative_offset_mm':None,'relative_yaw_degrees':None}
        else:criteria={'success':False,'piece_checks':[False]*len(selected),'relative_offset_mm':None,'relative_yaw_degrees':None}
        checks=[{'part':i+1,'color':c,'actual':states[i]['position'],'success':criteria['piece_checks'][i]} for i,c in enumerate(selected)]
        unselected={c:math.dist(start_positions[c],p.getBasePositionAndOrientation(parts[c])[0])*1000 for c in colors if c not in selected}
        if any(distance>5 for distance in unselected.values()):
            criteria['success']=False; failure=failure or 'An unselected cube moved more than 5 mm'
        return {'frames':frames,'selected':selected,'colors':colors,'inspections':inspections,'complete':criteria['success'],'criteria':criteria,'parts':out,'final_recheck':checks,'failure':failure,'unselected_displacement_mm':unselected,'destination':[.56,.10], 'final_position':states[-1]['position'],'target':out[-1]['target'] if out else [.56,.10,.05],'speed':None,'robot_contacts':sum(x['robot_contacts'] for x in states),'success':criteria['success'],'mode':'rgbd-laser-coupled-fingers-scripted','feedback':feedback,'extra_count':extra_count,'same_red':same_red,'occlude':occlude,'verification':verification,'diagnostics':diagnostics,'base_observations':base_observations,'held_tracking':held_tracking,'hold_checks':hold_checks,'reobservations':reobservations,'note':('RGB-D + wrist ray; post-grasp placement uses exact simulated object pose.' if feedback=='oracle' else 'RGB-D + wrist ray; post-grasp controller uses two side RGB-D observations, bounded prediction on occlusion and bilateral idealized contact checks at each checkpoint; simulator ground truth is used only for evaluation.')+' No ML.'}
    finally:p.disconnect(cid)








