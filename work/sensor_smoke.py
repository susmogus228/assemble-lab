import pybullet as p,pybullet_data
from sensors import camera_snapshot
p.connect(p.DIRECT);p.setAdditionalSearchPath(pybullet_data.getDataPath());p.setGravity(0,0,-9.81)
t=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.65,.65,.025]);tv=p.createVisualShape(p.GEOM_BOX,halfExtents=[.65,.65,.025],rgbaColor=[.25,.25,.25,1]);p.createMultiBody(0,t,tv,basePosition=[.5,0,-.025])
a=p.loadURDF('franka_panda/panda.urdf',useFixedBase=True)
for j,q in enumerate([0,-.5,0,-2.,0,1.5,.785]):p.resetJointState(a,j,q)
for x,y,c in [(.48,-.14,[.9,.05,.03,1]),(.45,-.22,[.03,.15,.95,1])]:
 col=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.025]*3);vis=p.createVisualShape(p.GEOM_BOX,halfExtents=[.025]*3,rgbaColor=c);p.createMultiBody(.06,col,vis,basePosition=[x,y,.025])
a=camera_snapshot();print(a['detections'])
import base64;open('outputs/camera-check.png','wb').write(base64.b64decode(a['image'].split(',')[1]));p.disconnect()
