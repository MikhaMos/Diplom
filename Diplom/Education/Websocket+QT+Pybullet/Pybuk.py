import pybullet as p
import pybullet_data
import time
import json
from threading import Thread
import asyncio
import numpy as np


class KukaRobot:
    def __init__(self, gui=True):
        self.gui = gui
        self.physics_client = None
        self.robot_id=None
        self.joint_indices = []
        self.joint_limits = []
        self.current_positions = [0.0] * 6
        self.is_running=True

    def connect(self):
        if self.gui:
            self.physics_client = p.connect(p.GUI)
        else:
            self.physics_client = p.connect(p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,-9.8)

        plane_id=p.loadURDF("plane.urdf")
        
        robot_start_pos =[0,0,0]
        robot_start_ori = p.getQuaternionFromEuler([0,0,0])

        self.robot_id = p.loadURDF("kuka_iiwa/model.urdf",
                                   robot_start_pos,
                                   robot_start_ori,
                                   useFixedBase=True)
        
        self._init_joints()
        
        self.sim_thread = Thread(target=self._simulation_loop, daemon=True)
        self.sim_thread.start()

        return True

    def _init_joints(self):
        num_joints = p.getNumJoints(self.robot_id)
        self.joint_indices=[]

        for i in range(num_joints):
            joint_info = p.getJointInfo(self.robot_id, i)
            if joint_info[2] == p.JOINT_REVOLUTE:
                self.joint_indices.append(i)
                self.joint_limits.append((joint_info[8], joint_info[9]))
                print("Joint Name: ", joint_info[1], "Joint Type: ", joint_info[2])

        self.joint_indices = self.joint_indices[:6]
        self.joint_limits = self.joint_limits[:6]

        print(f"Robot initialized with {len(self.joint_indices)} joints")
        print(f"Joint limits: {self.joint_limits}")
    
    def _simulation_loop(self):
        while self.is_running:
            p.stepSimulation()
            self._update_positions()
            time.sleep(1/240)
    
    def _update_positions(self):
        for i, joint_idx in enumerate(self.joint_indices):
            joint_state = p.getJointState(self.robot_id, joint_idx)
            self.current_positions[i] = joint_state[0]
    
    def move_joint(self,joint_index,direction,step=0.1): # Скорость задается шагом за команду
        if 0<= joint_index< len(self.joint_indices):
            current_pos = p.getJointState(self.robot_id, self.joint_indices[joint_index])[0]
            new_pos = current_pos + (direction * step)

            lower, upper = self.joint_limits[joint_index]  
            new_pos = min(max(lower, new_pos), upper)
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
        positions_deg= [pos*180/np.pi for pos in self.current_positions]
        return positions_deg

    def reset_positions(self):
        for i,joint_idx in enumerate(self.joint_indices):
            p.setJointMotorControl2(
                self.robot_id,
                joint_idx,
                p.POSITION_CONTROL,
                targetPosition=0,
                force=500,
                maxVelocity=1
            )

    def disconnect(self):
        self.is_running=False
        if self.sim_thread.is_alive():
            self.sim_thread.join()
        p.disconnect()