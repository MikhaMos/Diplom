import pybullet as p
import pybullet_data
import time
import json
import math
import numpy as np
from threading import Thread, Lock
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
        self.current_orientation = [0.0, 0.0, 0.0, 1.0] # [x,y,z,w]
        

        self.is_running=True

        # Для обратной кинематики
        self.ik_tolerance = 0.01 #допуск ошибки
        self.max_ik_iterations = 100 #максимальное количество итераций
        self.end_effector_link_index = 6

        # Для автоматичекого редима
        self.automatic_mode = False
        self.automatic_thread = None
        self.automatic_lock = Lock()
        self.target_points = []
        self.target_orientations = []
        self.current_point_index = 0
        self.loop_enabled = True
        self.automatic_move_speed = 0.8

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
        self.end_effector_link_state = p.getLinkState(self.robot_id, self.end_effector_link_index)
        self.current_FramePos = list(self.end_effector_link_state[0])
        self.current_orientation = list(self.end_effector_link_state[1])
        
        
    

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
    
    # только для _check_workspace_violation (возможно поменять)
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
                'FramePositions':self.current_FramePos,
                'End_effector_Orientation':self.current_orientation
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

    def calculate_inverse_kinematics(self, target_position, target_orientation): #target_orientation=None):
        try:
            
            joint_positions = p.calculateInverseKinematics(
                self.robot_id,
                self.end_effector_link_index,
                target_position,
                targetOrientation=target_orientation,
                lowerLimits=[lim[0] for lim in self.joint_limits],
                upperLimits=[lim[1] for lim in self.joint_limits],
                jointRanges=[lim[1] - lim[0] for lim in self.joint_limits],
                restPoses = [0.0, -0.5, 0.0, 1.0, 0.0, 0.0],
                maxNumIterations=self.max_ik_iterations,
                residualThreshold=self.ik_tolerance
            )

            result = list(joint_positions[:len(self.joint_indices)])
            for i, angle in enumerate(result):
                lower,upper = self.joint_limits[i]
                result[i] = max(lower, min(angle, upper))
            
            logger.info(f"Calculated joint positions successfully")
            return result
        except Exception as e:
            logger.error(f"Error calculating inverse kinematics: {e}")
            return None
        
    def move_to_point_ik(self, target_position,target_orientation):
        try:

            joint_angles = self.calculate_inverse_kinematics(target_position, target_orientation)
            if joint_angles is None:
                return False, "Failed to calculate inverse kinematics"

            for i, joint_idx in enumerate(self.joint_indices):
                p.setJointMotorControl2(
                    self.robot_id,
                    joint_idx,
                    p.POSITION_CONTROL,
                    targetPosition=joint_angles[i],
                    force=500,
                    maxVelocity=self.automatic_move_speed
                )
            
            start_time = time.time()
            timeout = 5.0
        
            while time.time() - start_time < timeout:
                
                current_state = p.getLinkState(self.robot_id, self.end_effector_link_index, computeForwardKinematics=True)
                current_position = current_state[0]
                current_orientation = current_state[1]
                
                position_distance = np.linalg.norm(np.array(current_position) - np.array(target_position))
                """
                orientation_ok = True
                if target_orientation is not None:
                    orientation_diff = self.quaternion_angle_diff(current_orientation, target_orientation)
                    orientation_ok = orientation_diff < 0.2  # 0.1 радиан (~5.7 градусов)
                else:
                    orientation_ok = True
                print("orientation_diff",orientation_diff)
                print("position_distance",position_distance)
                print("orientation_ok",orientation_ok)
                """
                if position_distance < 0.55: #and orientation_ok: # Допуск  см
                    logger.info(f"Move to point IK completed in {time.time() - start_time:.3f} seconds")
                    logger.debug(f"Point completed, distance: {position_distance:.3f}")
                    return True, f"Point {target_position} completed"
                    
                time.sleep(2)
                return False, f"Move to point IK timed out after {timeout} seconds"
        
        except Exception as e:
            logger.error(f"Error moving to point with IK: {e}")
            return False, str(e)
    """
    def quaternion_angle_diff(self, q1, q2):
        # Вычисление угловой разницы медлу двумя квартерионами

        # Нормализуем кватернионы
        q1_norm=np.linalg.norm(q1)
        q2_norm=np.linalg.norm(q2)
        if q1_norm == 0 or q2_norm == 0:
            return math.pi
        
        q1 = np.array(q1) / q1_norm
        q2 = np.array(q2) / q2_norm

        # Скалярное произведение квартерионов
        dot = np.dot(q1, q2)

         # Кватернионы q и -q представляют одну и ту же ориентацию!
        # Берем абсолютное значение и ограничиваем
        dot = abs(dot)
        dot = abs(dot)
        dot = min(1.0,max(-1.0,dot))

        # Угол между ориентациями
        angle = 2 * math.acos(dot)

        # Кватернионы имеют двойное покрытие: q ≡ -q
        # Поэтому минимальный угол всегда <= π/2
        if angle > math.pi:
            angle = 2 * math.pi - angle
        
        return angle
    """

    
    def start_automatic_mode(self,points,orientation,loop_programming = True):
        with self.automatic_lock:
            if self.automatic_mode:
                return False
            
            if not points:
                return False, "No points provided"
            
            self.target_points = points
            self.target_orientations = orientation
            self.current_point_index = 0
            self.loop_enabled = loop_programming
            self.automatic_mode = True

            #self.target_orientations = [self.current_orientation for _ in range(len(points))]
            self.automatic_thread = Thread(target=self._automatic_mode_loop, daemon=True)
            self.automatic_thread.start()

            logger.info(f"Automatic mode started. Points: {len(self.target_points)}")
            return True
        
    def stop_automatic_mode(self):
        with self.automatic_lock:
            if not self.automatic_mode:
                return
            self.automatic_mode = False
            logger.info("Automatic mode stopped")
    
    def _automatic_mode_loop(self):
        #Цикл автоматического управления
        logger.info("Automatic mode loop started")
        while self.automatic_mode and self.is_running:
            try:
                with self.automatic_lock:
                    if not self.target_points or self.current_point_index >= len(self.target_points):

                        if self.loop_enabled:
                            self.current_point_index = 0
                            logger.info("Looping to the first point")

                        else:
                            self.automatic_mode = False
                            logger.info("Automatic mode stopped")
                            break
                    
                    # получаем текущую точку
                    target_point = self.target_points[self.current_point_index]
                    target_orientation = self.target_orientations[self.current_point_index]

                    # Преобразуем в массив
                    if isinstance(target_point, list):
                        target_point = np.array(target_point, dtype=np.float32)

                    point_num = self.current_point_index + 1
                    total_points = len(self.target_points)
                    logger.info(f"Moving to point {point_num}/{total_points} ({target_point})")
                    
                    success, message = self.move_to_point_ik(target_point, target_orientation)
                    if success:
                        self.current_point_index += 1
                        logger.info(f"Point {target_point} completed")
                        time.sleep(0.5)
                    else:
                        logger.warning(f"Failed to move to point {target_point}: {message}")
                        self.current_point_index += 1
                        time.sleep(1)

            except Exception as e:
                logger.error(f"Error in automatic mode loop: {e}")

    logger.info("Automatic mode loop stopped")
        
    def disconnect(self):
        self.is_running = False
        # Останавливаем автоматический режим
        self.stop_automatic_mode()

        #Ждем завершения потоков
        if hasattr(self, 'automatic_thread') and self.automatic_thread:
            self.automatic_thread.join(timeout=1.0)

        if hasattr(self, 'sim_thread') and self.sim_thread:
            self.sim_thread.join(timeout=1.0)
        if self.physics_client is not None:
            p.disconnect()

if __name__ == "__main__":
    robot = KukaRobot(gui=True)
    robot.connect()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        robot.disconnect()
                        

            