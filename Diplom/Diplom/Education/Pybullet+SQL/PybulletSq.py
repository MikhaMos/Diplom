import pybullet as p
import pybullet_data
import time
import json
import numpy as np
from SQL import RobotDatabase



class Kuka:
    def __init__(self, gui=True, db_name = "RobotTelemetry.db", log_frequency=0.1):
        self.gui = gui
        self.log_frequency = log_frequency
        self.last_log_time=0
        self.physics_client = p.connect(p.GUI)
        self.sim_time =0
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0,0,-9.8)
        
        plane_id=p.loadURDF("plane.urdf")
        
        robot_start_pos =[0,0,0]
        robot_start_ori = p.getQuaternionFromEuler([0,0,0])
        
        self.robot_id = p.loadURDF("kuka_iiwa/model.urdf",
                                   robot_start_pos,
                                   robot_start_ori,
                                   useFixedBase=True)
        
        self.joint_indices = []
        self.joint_names = []
        
        num_joints = p.getNumJoints(self.robot_id)
        
        for i in range(num_joints):
            joint_info = p.getJointInfo(self.robot_id, i)
            if joint_info[2] == p.JOINT_REVOLUTE:
                self.joint_indices.append(i)
                self.joint_names.append(joint_info[1])
                print("Joint Name: ", joint_info[1], "Joint Type: ", joint_info[2])
        
        print(f"Robot initialized with {len(self.joint_indices)} joints")

        self.time_step = 1.0/240.0
        p.setTimeStep(self.time_step)

        self.joint_anglles = [0.0]*len(self.joint_indices)
        self.joint_anglles_step = 0.1


        self.db = RobotDatabase(db_name)
        self.session_id = self.db.start_new_session(f"Kuka Simulation {time.strftime('%Y-%m-%d %H:%M:%S')}")

        self.keys_pressed={}

        print("Simulation started. Control:")
        print("  1-7: increase/decrease joint angles")
        print("  Shift+1-7: increase/decrease joint angles in radians")
        print("  w/s: move forward/backward")
        print("  a/d: +/- rotation")
        print("  q/e: move up/down")
        print("  r: reset")
        print("  SPACE: save current telemetry")
        print("  ESC: exit")


    
    def get_joint_states(self):
        joint_states = p.getJointStates(self.robot_id, self.joint_indices)
        joint_positions = [state[0] for state in joint_states]
        joint_velocities = [state[1] for state in joint_states]
        joint_torques = [state[3] for state in joint_states]
        return joint_positions, joint_velocities, joint_torques
    
    def get_end_effector_pose(self):
        if self.joint_indices:
            end_effector_index = self.joint_indices[-1]
            link_state = p.getLinkState(
                self.robot_id,
                end_effector_index,
                computeForwardKinematics=True
            )
            return link_state[0], link_state[1]
        return [0, 0, 0], [0, 0, 0, 1]
    
    def save_current_telemetry(self):
        joint_positions, joint_velocities, joint_torques = self.get_joint_states()
        end_effector_positions, end_effector_orn = self.get_end_effector_pose()
        sim_time = self.get_simulation_time()
        self.db.save_telemetry(self.session_id, 
                               sim_time, 
                               joint_positions, 
                               joint_velocities, 
                               joint_torques, 
                               end_effector_positions, 
                               end_effector_orn)

    def update_joint_angles(self):
        for i, joint_idx in enumerate(self.joint_indices):
            p.setJointMotorControl2(self.robot_id, 
                                    joint_idx, 
                                    p.POSITION_CONTROL, 
                                    targetPosition=self.joint_anglles[i], 
                                    force=500,
                                    positionGain=0.5,
                                    velocityGain=0.5
                                    )
            
    def get_simulation_time(self):
        params = p.getPhysicsEngineParameters()

        # Пробуем разные возможные ключи
        if 'physicsTime' in params:
            return params['physicsTime']
        elif 'time' in params:
            return params['time']
        elif 'realTimeSimulation' in params:
            # Некоторые версии используют этот ключ
            return params.get('realTimeSimulation', 0)
        else:
            # Если ни один ключ не найден, используем наше собственное время
            return self.sim_time
             
    def handle_keyboard(self):
        keys = p.getKeyboardEvents()

        for key, state in keys.items():
            # Сохраняем состояние клавиши
            if state & 1:
                self.keys_pressed[key] = True
            elif state & 4:
                self.keys_pressed[key] = False
            
            # Обрабатываем только нажатия
            if state & 1:
                # ESC для выхода
                if key == 65307 or key == 27:
                    return False
                
                # Управление отдельными суставами (клавиши 1-7)
                elif ord('1') <= key <= ord('7'):
                    joint_index = key - ord('1')
                    if joint_index < len(self.joint_indices):
                         
                        shift_pressed = False
                    for shift_key in [65505, 65506]:  # Левый и правый Shift
                        if shift_key in self.keys_pressed and self.keys_pressed[shift_key]:
                            shift_pressed = True
                            break
                        
                        if shift_pressed:
                            self.joint_anglles[joint_index] -= self.joint_anglles_step
                            action = f"Уменьшить сустав {joint_index + 1}"
                        else:
                            self.joint_anglles[joint_index] += self.joint_anglles_step
                            action = f"Увеличить сустав {joint_index + 1}"
                        
                        print(f"Сустав {joint_index + 1}: {self.joint_anglles[joint_index]:.3f} рад")
                        self.db.save_control_event(
                            self.session_id, 
                            chr(key) + ("+Shift" if shift_pressed else ""),
                            action
                        )
                
                # Движение вперед/назад (w/s)
                elif key == ord('w'):
                    # Простое декартово движение - двигаем все суставы одинаково
                    for i in range(len(self.joint_anglles)):
                        self.joint_anglles[i] += 0.05
                    self.db.save_control_event(self.session_id, "w", "Движение вперед")
                    print("Движение вперед")
                
                elif key == ord('s'):
                    for i in range(len(self.joint_anglles)):
                        self.joint_anglles[i] -= 0.05
                    self.db.save_control_event(self.session_id, "s", "Движение назад")
                    print("Движение назад")
                
                # Движение влево/вправо (a/d)
                elif key == ord('a'):
                    # Двигаем только первые суставы для бокового движения
                    for i in range(min(3, len(self.joint_anglles))):
                        self.joint_anglles[i] += 0.05
                    self.db.save_control_event(self.session_id, "a", "Движение влево")
                    print("Движение влево")
                
                elif key == ord('d'):
                    for i in range(min(3, len(self.joint_anglles))):
                        self.joint_anglles[i] -= 0.05
                    self.db.save_control_event(self.session_id, "d", "Движение вправо")
                    print("Движение вправо")
                
                # Движение вверх/вниз (q/e)
                elif key == ord('q'):
                    # Двигаем последние суставы для вертикального движения
                    for i in range(max(0, len(self.joint_anglles)-3), len(self.joint_anglles)):
                        self.joint_anglles[i] += 0.05
                    self.db.save_control_event(self.session_id, "q", "Движение вверх")
                    print("Движение вверх")
                
                elif key == ord('e'):
                    for i in range(max(0, len(self.joint_anglles)-3), len(self.joint_anglles)):
                        self.joint_anglles[i] -= 0.05
                    self.db.save_control_event(self.session_id, "e", "Движение вниз")
                    print("Движение вниз")
                
                # Сброс (r)
                elif key == ord('r'):
                    self.joint_anglles = [0.0] * len(self.joint_indices)
                    self.db.save_control_event(self.session_id, "r", "Сброс позиции")
                    print("Позиция сброшена")
                
                # Принудительное сохранение (SPACE)
                elif key == 32:
                    self.save_current_telemetry()
                    self.db.save_control_event(self.session_id, "SPACE", "Принудительное сохранение")
                    print("Телеметрия сохранена")
        
        return True
    
    def run(self):
        sim_time = 0
        print("Starting simulation...")

        while True:

            if not self.handle_keyboard():
                break

            self.update_joint_angles()

            p.stepSimulation()
            sim_time += self.time_step

            current_time = time.time()
            if current_time - self.last_log_time > self.log_frequency:
                self.save_current_telemetry()
                self.last_log_time = current_time
            
            if self.gui:
                time.sleep(self.time_step)

        self.db.end_session(self.session_id)
        self.db.close()
        print("Simulation ended.")
        p.disconnect()

    def print_telemetry_summary(self) -> None:
        """Выводит краткую сводку сохраненной телеметрии."""
        telemetry = self.db.get_telemetry(self.session_id, limit=5)
        
        print(f"\nПоследние {len(telemetry)} записей телеметрии:")
        for i, record in enumerate(telemetry):
            print(f"Запись {i+1}:")
            print(f"  Время симуляции: {record[3]:.2f} с")
            print(f"  Позиции суставов: {[f'{x:.3f}' for x in record[4]]}")
            print(f"  Позиция концевика: {[f'{x:.3f}' for x in record[7]]}")


def main():
    sim = Kuka(
        gui=True,
        db_name = "RobotTelemetry.db",
        log_frequency=0.5
    )

    try:
        sim.run()
        sim.print_telemetry_summary()
    except KeyboardInterrupt:
        print("Simulation stopped by user.")
    finally:
        if hasattr(sim, 'db'):
            sim.db.close()
        p.disconnect()


if __name__ == "__main__":
    main()