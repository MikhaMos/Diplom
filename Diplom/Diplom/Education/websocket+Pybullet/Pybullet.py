import pybullet as p
import pybullet_data
import time


class SimpleRobot:
    def __init__(self):
        p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)

        p.loadURDF("plane.urdf")

        self.robot= p.loadURDF(
            "kuka_iiwa/model.urdf",
            [0, 0, 0],
            p.getQuaternionFromEuler([0, 0, 0]),
            useFixedBase=True
        )

        self.num_joints = p.getNumJoints(self.robot)
        self.joint_indices=[]

        for i in range(self.num_joints):
            info = p.getJointInfo(self.robot, i)
            jointName = info[1]
            jointType = info[2]
            if jointType == p.JOINT_REVOLUTE:
                self.joint_indices.append(i)
                print("Joint Name: ", jointName, "Joint Type: ", jointType)
        
        self.joint_indices = self.joint_indices[:6]
        self.current_positions = [0.0]*6

        print(f"Robot initialized with {len(self.joint_indices)} joints") 

    def set_joint_position(self,positions):
        for i, joint_idx in enumerate(self.joint_indices):
            p.setJointMotorControl2(
                self.robot,
                joint_idx,
                p.POSITION_CONTROL,
                targetPosition=positions[i],
                force=100
            )
            self.current_positions[i] = positions[i]
        print(f"Joint positions: {positions}")
        return True

    def reset(self):
        zero_positions = [0.0]*6
        self.set_joint_position(zero_positions)
        print("Robot reset")

    def get_state(self):
        return {
            "joint_positions": self.current_positions.copy(),
            "num_joints": len(self.joint_indices)
        }
    
    def step(self):
        p.stepSimulation()
        time.sleep(1/240)

if __name__ == "__main__":
    robot = SimpleRobot()
    robot.reset()
    while True:
        robot.step()
        time.sleep(0.01)
