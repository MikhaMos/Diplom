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
        self.max_ik_iterations = 300 #максимальное количество итераций
        self.end_effector_link_index = 6

        # Для автоматичекого режима
        self.automatic_mode = False
        self.automatic_thread = None
        self.automatic_lock = Lock()
        self.target_points = []
        self.target_orientations = []
        self.current_point_index = 0
        self.loop_enabled = True

        # Ограничения SSM зоны радиус
        self.ssm_zones= {
            'normal': {
                'inner':2.5,
                'outer':4
            },
            'restricted': {
                'inner':2.5, # 3 человек
                'outer':6
            }
        }
        self.current_ssm_mode = 'normal'
        self.current_speed_mode = 'full'

        self.robot_speeds = { # рад/c
            'automatic':{
                'full':1.2,  # Полная скорость (зеленая/синяя зона)
                'adaptive':0.6, # Скорость при усталости
                'reduced':0.48 # Пониженная скорость (желтая/фиолетовая зона)
            },
            'manual':{
                'full':1,  # Полная скорость (зеленая/синяя зона)
                'adaptive':0.4, # Скорость при усталости
                'reduced':0.36 # Пониженная скорость (желтая/фиолетовая зона)
            }
        }
        self.zone_visuals = {
            'outer':None, # Внешняя зона (желтая/фиолетовая)
            'inner':None # Внутренняя зона (зеленая/синяя)
        }
        self.human_id=None

    def connect(self):
        if self.gui:
            self.physics_client = p.connect(p.GUI)
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        else:
            self.physics_client = p.connect(p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,-9.8)

        plane_id=p.loadURDF("plane.urdf")
        #Стол
        table_pos = [0.0, 0.0, 0.0]
        table_ori = p.getQuaternionFromEuler([0, 0, 0])
        self.table_id = p.loadURDF("table/table.urdf", table_pos, table_ori)  
        # конечное место работы
        table_square_pos = [-1.3, -0.4, 0.0]
        table_square_ori = p.getQuaternionFromEuler([0, 0, 0])
        self.table_square_id = p.loadURDF("table_square/table_square.urdf", 
                                          table_square_pos, 
                                          table_square_ori) 
        #Робот
        robot_start_pos =[-0.5,0,0.6]
        robot_start_ori = p.getQuaternionFromEuler([0,0,0])
        self.robot_id = p.loadURDF("kuka_iiwa/model.urdf",
                                   robot_start_pos,
                                   robot_start_ori,
                                   useFixedBase=True)
        #человек
        human_start_pos = [-3.5,0,1.1]
        human_start_ori = p.getQuaternionFromEuler([1.5,0,0])
        self.human_id = p.loadURDF("humanoid/humanoid.urdf",
                                   human_start_pos,
                                   human_start_ori,
                                   useFixedBase=True,
                                   globalScaling=0.3)
        
        self.create_objects()

        self._init_joints()

        self.visualize_ssm_zones()

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
            self._check_human_position()
            time.sleep(1/240)
    
    def _update_positions(self):
        for i, joint_idx in enumerate(self.joint_indices):
            joint_state = p.getJointState(self.robot_id, joint_idx)
            self.current_positions[i] = joint_state[0]
        self.end_effector_link_state = p.getLinkState(self.robot_id, self.end_effector_link_index)
        self.current_FramePos = list(self.end_effector_link_state[0])
        self.current_orientation = list(self.end_effector_link_state[1])
        
    def visualize_ssm_zones(self):
        for key in self.zone_visuals:
            if self.zone_visuals[key] is not None:
                p.removeBody(self.zone_visuals[key])
                self.zone_visuals[key] = None
                
        # Получаем позицию базы робота
        robot_pos,_= p.getBasePositionAndOrientation(self.robot_id)
        zones = self.ssm_zones[self.current_ssm_mode]


        if self.current_ssm_mode == 'normal':
            inner_color=[1,1,0,0.18] # Желеный, полупрозрачный]
            outer_color=[0,1,0,0.18] # Зеленый, полупрозрачный
            inner_radius = zones['inner']
            outer_radius = zones['outer']
        else:
            inner_color=[1,0,1,0.10] # Финий, полупрозрачный]
            outer_color=[0,0,1,0.10] # Сиолетовый, полупрозрачный
            inner_radius = zones['inner']
            outer_radius = zones['outer']

        inner_visual_shape =  p.createVisualShape(
            p.GEOM_SPHERE, 
            radius=inner_radius, 
            rgbaColor=inner_color
            ) 
        inner_collision_shape = p.createCollisionShape(
            p.GEOM_SPHERE, 
            radius=inner_radius
            )
        self.zone_visuals['inner'] = p.createMultiBody(
            0,
            inner_collision_shape,
            inner_visual_shape,
            basePosition=robot_pos
        )
        p.setCollisionFilterGroupMask(self.zone_visuals['inner'],-1,0,0)
        p.changeVisualShape(self.zone_visuals['inner'],-1,rgbaColor=inner_color)

        outer_visual_shape =  p.createVisualShape(
            p.GEOM_SPHERE,
            radius=outer_radius,
            rgbaColor=outer_color
        )
        outer_collision_shape = p.createCollisionShape(
            p.GEOM_SPHERE,
            radius=outer_radius
        )
        self.zone_visuals['outer'] = p.createMultiBody(
            0,
            outer_collision_shape,
            outer_visual_shape,
            basePosition=robot_pos
        )
        p.setCollisionFilterGroupMask(self.zone_visuals['outer'],-1,0,0)
        p.changeVisualShape(self.zone_visuals['outer'],-1,rgbaColor=outer_color)
        
        logger.info(f"SSM zones visualized: mode={self.current_ssm_mode}, inner={inner_radius}, outer={outer_radius}")
        
        
    def set_adaptive_mode(self, adaptive_mode, speed_mode_type):
        if adaptive_mode:
            ssm_zone_type = 'restricted'
        else:
            ssm_zone_type = 'normal'
        if ssm_zone_type in self.ssm_zones.keys():
            self.current_ssm_mode = ssm_zone_type
            self.visualize_ssm_zones()
            logger.info(f"Workspace changed to {ssm_zone_type}")
            self.current_speed_mode = speed_mode_type
            logger.info(f"Speed mode changed to {speed_mode_type}")
            return True
        return False
    
    def _check_human_position(self):
        #Проверка расстояния между роботом и человеком
        if not self.human_id:
            return 
        
        robot_pos,_= p.getBasePositionAndOrientation(self.robot_id)
        human_body_pos,_ = p.getBasePositionAndOrientation(self.human_id)

        dx = human_body_pos[0] - robot_pos[0]
        dy = human_body_pos[1] - robot_pos[1]
        dz = human_body_pos[2] - robot_pos[2] # игнорируем
        distance = math.sqrt(dx*dx + dy*dy)

        old_mode = self.current_ssm_mode
        old_speed_mode = self.current_speed_mode

        if distance < self.ssm_zones[self.current_ssm_mode]['outer'] and distance > self.ssm_zones[self.current_ssm_mode]['inner']:
            #человек внутри зеленой зоны - полная рабочая скорость
            if self.current_speed_mode != 'adaptive':
                self.current_speed_mode = 'full'
        elif distance < self.ssm_zones[self.current_ssm_mode]['inner']:
            #человек внутри желтой зоны - половина рабочей скорости
            self.current_speed_mode = 'reduced'
        elif distance > self.ssm_zones[self.current_ssm_mode]['outer']:
            # человек вне зон
            if self.current_speed_mode != 'adaptive':
                self.current_speed_mode = 'full'
        # else человек у робота

        self.automatic_move_speed = self.robot_speeds['automatic'][self.current_speed_mode]
        self.manual_move_speed = self.robot_speeds['manual'][self.current_speed_mode]

        if old_speed_mode != self.current_speed_mode:
            logger.info(f"Speed mode changed to {self.current_speed_mode}")
        if old_mode != self.current_ssm_mode:
            logger.info(f"SSM mode changed to {self.current_ssm_mode}")

    
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
                force=800, # Для наглядности изменения скорости
                maxVelocity=self.manual_move_speed
            )
            return True, f"Joint {joint_index} moved to {new_pos:.3f}"
        return False, f"Invalid joint index: {joint_index}"
    
    def get_joint_positions(self):
        positions_deg = [pos * 180 / np.pi for pos in self.current_positions]
        return {
                'JointPositions': positions_deg,
                'FramePositions':self.current_FramePos,
                'End_effector_Orientation':self.current_orientation,
                'velosity': self.automatic_move_speed if self.automatic_mode else self.manual_move_speed
                }

    def reset_positions(self):
        for i, joint_idx in enumerate(self.joint_indices):
            p.setJointMotorControl2(
                self.robot_id,
                joint_idx,
                p.POSITION_CONTROL,
                targetPosition=0.0,
                force=800,
                maxVelocity=self.automatic_move_speed
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
                        force=800,
                        maxVelocity=self.automatic_move_speed
                    )
            start_time = time.time()
            timeout = 10.0
            position_tolerance = 0.03
            #orientation_tolerance = 0.1
        
            while time.time() - start_time < timeout:
                if self.automatic_mode == False:
                    return False, "Automatic mode is off"
                p.stepSimulation()
                
                current_state = p.getLinkState(self.robot_id, self.end_effector_link_index, computeForwardKinematics=True)
                current_position = current_state[0]
                current_orientation = current_state[1]
                position_distance = np.linalg.norm(np.array(current_position) - np.array(target_position))
                
                # Считаем, что кватернионы уже нормализованы
                #dot_product = np.abs(np.dot(current_orientation, target_orientation))
                # Угол = 2 * arccos(dot_product), но для близости можно сравнивать dot_product с порогом
                #orientation_ok = dot_product > np.cos(orientation_tolerance/2)

                if position_distance < position_tolerance: #and orientation_ok: # Допуск 
                    logger.info(f"Move to point IK completed in {time.time() - start_time:.3f} seconds")
                    logger.debug(f"Point completed, distance: {position_distance:.3f}")
                    return True, f"Point {target_position} completed"
                time.sleep(0.05)
            return False, f"Move to point IK timed out after {timeout} seconds"
        
        except Exception as e:
            logger.error(f"Error moving to point with IK: {e}")
            return False, str(e)

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

            self.automatic_thread = Thread(target=self._automatic_mode_loop, daemon=True)
            self.automatic_thread.start()

            logger.info(f"Automatic mode started. Points: {len(self.target_points)}")
            return  True,f'Automatic mode started. Points: {len(self.target_points)}'
        
    def stop_automatic_mode(self):
        with self.automatic_lock:
            if not self.automatic_mode:
                return
            self.automatic_mode = False
            logger.info("Automatic mode stopped")
        return True, f'Automatic mode stopped'
    
    def _automatic_mode_loop(self):
        #Цикл автоматического управления
        logger.info("Automatic mode loop started")
        while self.automatic_mode and self.is_running:
            try:
                if self.automatic_mode == False:
                    break
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
                        

            