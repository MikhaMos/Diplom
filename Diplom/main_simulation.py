import pybullet as p
import pybullet_data
import time
import json
import numpy as np
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KukaRobot:
    def __init__(self, gui=True):
        self.gui = gui
        self.physics_client = None
        self.robot_id=None
        self.joint_indices = []
        self.joint_limits = []
        self.current_positions = [0.0] * 6
        self.current_FramePos = [0.0]*3
        self.is_running=True

        # Ограничения рабочей зоны (x,y,z в)
        self.workspace_limits = {
            'normal':{
                'x':[-0.8, 0.8],
                'y':[-0.8, 0.8],
                'z':[0.0, 2.0]
            },
            'restricted':{
                'x':[-0.4, 0.4],
                'y':[-0.4, 0.4],
                'z':[0.2, 0.8]
            }
        }
        self.current_workspace = 'normal'

        # Визуализация рабочей зоны
        self.workspace_visual = None

    def connect(self):
        if self.gui:
            self.physics_client = p.connect(p.GUI)
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        else:
            self.physics_client = p.connect(p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,-9.8)

        plane_id=p.loadURDF("plane.urdf")

        table_pos = [0.0, 0.0, 0.0]
        table_ori = p.getQuaternionFromEuler([0, 0, 0])
        self.table_id = p.loadURDF("table/table.urdf", table_pos, table_ori)   
        
        robot_start_pos =[0,0,0.6]
        robot_start_ori = p.getQuaternionFromEuler([0,0,0])

        self.robot_id = p.loadURDF("kuka_iiwa/model.urdf",
                                   robot_start_pos,
                                   robot_start_ori,
                                   useFixedBase=True)
        
        self.create_objects()

        self._init_joints()

        self.visualize_workspace()

        self.sim_thread = Thread(target=self._simulation_loop, daemon=True)
        self.sim_thread.start()

        return True

    def create_objects(self):
        """Create objects in the environment"""
        cube_size = 0.05
        cube_mass = 0.1

        cube_positions = [
            [0.3,0.3,0.7],
            [-0.3,0.3,0.7],
            [0.3, -0.3, 0.7],
            [-0.3, -0.3, 0.7]
        ]

        self.cubes = []

        for pos in cube_positions:
            cube_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[cube_size]*3)
            cube_visual_shape = p.createVisualShape(p.GEOM_BOX, halfExtents=[cube_size]*3, rgbaColor=[0.8,0.2,0.2,1])
            cube_id = p.createMultiBody(cube_mass, 
                                        cube_shape, 
                                        cube_visual_shape, 
                                        basePosition=pos)
            self.cubes.append(cube_id)
            
    def _init_joints(self):
        num_joints = p.getNumJoints(self.robot_id)
        self.joint_indices=[]
        self.joint_limits=[]

        for i in range(num_joints):
            joint_info = p.getJointInfo(self.robot_id, i)
            if joint_info[2] == p.JOINT_REVOLUTE:
                self.joint_indices.append(i)
                self.joint_limits.append((joint_info[8], joint_info[9]))
                print("Joint Name: ", joint_info[1], "Joint Type: ", joint_info[2])

        self.joint_indices = self.joint_indices[:6]
        self.joint_limits = self.joint_limits[:6]

        logger.info(f"Robot initialized with {len(self.joint_indices)} joints")
        logger.info(f"Joint limits: {self.joint_limits}")
    
    def _simulation_loop(self):
        while self.is_running:

            p.stepSimulation()
            self._update_positions()
            self._check_workspace_violation()
            time.sleep(1/240)
    
    def _update_positions(self):
        for i, joint_idx in enumerate(self.joint_indices):
            joint_state = p.getJointState(self.robot_id, joint_idx)
            self.current_positions[i] = joint_state[0]
        self.current_FramePos = list(p.getLinkState(self.robot_id, self.joint_indices[5])[0])
        
        
    
    def visualize_workspace(self):
        if self.workspace_visual:
            p.removeBody(self.workspace_visual)

        limits = self.workspace_limits[self.current_workspace]

        x_min, x_max = limits['x']
        y_min, y_max = limits['y']
        z_min, z_max = limits['z']

        center = [(x_min+x_max)/2, (y_min+y_max)/2, (z_min+z_max)/2]
        half_size = [(x_max-x_min)/2, (y_max-y_min)/2, (z_max-z_min)/2]

        if self.current_workspace == 'normal':
            color = [0,1,0,0.1] # Зеленый, полупрозрачный
        else:
            color = [1,0,0,0.1] # Красный, полупрозрачный

        visual_shape =  p.createVisualShape(p.GEOM_BOX, halfExtents=half_size, rgbaColor=color) 
        self.workspace_visual = p.createMultiBody(0, visual_shape, basePosition=center)
    
    def set_workspace(self, workspace_type):
        if workspace_type in self.workspace_limits:
            self.current_workspace = workspace_type
            self.visualize_workspace()
            logger.info(f"Workspace changed to {workspace_type}")
            return True
        return False
    
    def _check_workspace_violation(self):
        #Проверка нарушений рабочей зоны
        # получаем позицию конца эффектора
        end_effector_pos = self.get_end_effector_position()
        

        if end_effector_pos:
            limits = self.workspace_limits[self.current_workspace]

            #Проверяем выходы за пределы
            violation = False
            if not limits['x'][0] <= end_effector_pos[0] <= limits['x'][1]:
                violation = True
            if not limits['y'][0] <= end_effector_pos[1] <= limits['y'][1]:
                violation = True
            if not limits['z'][0] <= end_effector_pos[2] <= limits['z'][1]:
                violation = True

            if violation:
               logger.info(f"Workspace violation detected! Position: ({end_effector_pos[0]:.3f}, {end_effector_pos[1]:.3f}, {end_effector_pos[2]:.3f})")
    
    def get_end_effector_position(self):
        if self.robot_id and len(self.joint_indices) > 0:
            end_effector_link = 6
            joint_state = p.getLinkState(self.robot_id, end_effector_link, computeForwardKinematics=True)
            
            return joint_state[0]
        return None
    
    def move_joint(self, joint_index, direction, step=0.1):
        if 0 <= joint_index < len(self.joint_indices):
            # проверяем не выдет ли ноовое положение за пределы рабочей зоны
            current_pos = p.getJointState(self.robot_id, self.joint_indices[joint_index])[0]
            new_pos = current_pos + (direction * step)

            # Проверяем пределы сустава
            lower, upper = self.joint_limits[joint_index]
            new_pos = max(lower, min(new_pos, upper))

            p.setJointMotorControl2(
                self.robot_id,
                self.joint_indices[joint_index],
                p.POSITION_CONTROL,
                targetPosition=new_pos,
                force=500,
                maxVelocity=0.5
            )
            return True, f"Joint {joint_index} moved to {new_pos:.3f}"
        return False, f"Invalid joint index: {joint_index}"

    def get_joint_positions(self):
        positions_deg = [pos * 180 / np.pi for pos in self.current_positions]
        return {
                'JointPositions': positions_deg,
                'FramePositions':self.current_FramePos
                }

    def reset_positions(self):
        for i, joint_idx in enumerate(self.joint_indices):
            p.setJointMotorControl2(
                self.robot_id,
                joint_idx,
                p.POSITION_CONTROL,
                targetPosition=0,
                force=500,
                maxVelocity=0.5
            )

    def disconnect(self):
        self.is_running = False
        if self.sim_thread.is_alive():
            self.sim_thread.join(timeout=1.0)
        p.disconnect()

if __name__ == "__main__":
    robot = KukaRobot(gui=True)
    robot.connect()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        robot.disconnect()
                        

            