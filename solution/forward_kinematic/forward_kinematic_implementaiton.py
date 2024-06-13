#TODO FK function implementation
import numpy as np
import pybullet as p
import pybullet_data
import time

### FK Class
class RobotKinematics:
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.base_position, self.base_orientation = p.getBasePositionAndOrientation(robot_id)
        self.joints = self.get_joints_info()
        self.links = self.get_links_info()
        self.end_effector_transform = None

    def get_joints_info(self):
        num_joints = p.getNumJoints(self.robot_id)
        joints = {}
        for i in range(num_joints):
            joint_info = p.getJointInfo(self.robot_id, i)
            joint_name = joint_info[1].decode('utf-8')
            print(joint_name,i)
            joints[joint_name] = {
                'index': i,
                'parent': joint_info[16],  # Parent link index
                'child': joint_info[12].decode('utf-8'),  # Child link name
                'xyz': joint_info[14],  # Joint origin xyz
                'rpy': joint_info[15],  # Joint origin rpy
                'axis': joint_info[13]  # Joint axis
            }
        return joints

    def get_links_info(self):
        num_joints = p.getNumJoints(self.robot_id)
        links = {}
        for i in range(num_joints):
            link_info = p.getJointInfo(self.robot_id, i)
            link_name = link_info[12].decode('utf-8')
            links[link_name] = {
                'parent': link_info[1].decode('utf-8'),  # parent joint name
                'children': []  # Will be filled in later
            }
        for joint_name, joint_info in self.joints.items():
            if joint_info['parent'] >= 0:
                parent_link_name = p.getJointInfo(self.robot_id, joint_info['parent'])[12].decode('utf-8')
                links[parent_link_name]['children'].append(joint_name)
        print(links)
        return links

    def build_fk_transforms(self, joint_angles):
        base_transform = generate_translation_matrix(*self.base_position)
        base_rotation = p.getMatrixFromQuaternion(self.base_orientation)
        base_rotation = np.array(base_rotation).reshape(3, 3)
        base_transform[:3, :3] = base_rotation

        self.end_effector_transform = self.traverse_fk_link('base', base_transform, joint_angles)

    def traverse_fk_link(self, link_name, parent_transform, joint_angles):
        link = self.links.get(link_name)
        print("getting link",link)
        if link is None:
            return parent_transform

        for joint_name in link['children']:
            joint = self.joints[joint_name]
            index = joint['index']
            angle = joint_angles[index]
            joint_transform = self.traverse_fk_joint(joint, angle)
            current_transform = matrix_multiply(parent_transform, joint_transform)
            child_link_name = joint['child']
            self.end_effector_transform = self.traverse_fk_link(child_link_name, current_transform, joint_angles)
        
        return self.end_effector_transform

    def traverse_fk_joint(self, joint, angle):
        translation = generate_translation_matrix(*joint['xyz'])
        rotateX = generate_rotation_matrix_X(joint['rpy'][0])
        rotateY = generate_rotation_matrix_Y(joint['rpy'][1])
        rotateZ = generate_rotation_matrix_Z(joint['rpy'][2])
        axis = joint['axis']
        q = quaternion_from_axisangle(axis, angle)
        qmatrix = quaternion_to_rotation_matrix(q)
        transform = generate_identity()
        transform = matrix_multiply(transform, translation)
        transform = matrix_multiply(transform, rotateZ)
        transform = matrix_multiply(transform, rotateY)
        transform = matrix_multiply(transform, rotateX)
        joint_transform = matrix_multiply(transform, qmatrix)
        return joint_transform
    

### Matrix 
def generate_translation_matrix(x, y, z):
    """
    Generate a translation matrix.
    """
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1]
    ])

def generate_rotation_matrix_X(angle):
    """
    Generate a rotation matrix around the X-axis.
    """
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(angle), -np.sin(angle), 0],
        [0, np.sin(angle), np.cos(angle), 0],
        [0, 0, 0, 1]
    ])

def generate_rotation_matrix_Y(angle):
    """
    Generate a rotation matrix around the Y-axis.
    """
    return np.array([
        [np.cos(angle), 0, np.sin(angle), 0],
        [0, 1, 0, 0],
        [-np.sin(angle), 0, np.cos(angle), 0],
        [0, 0, 0, 1]
    ])

def generate_rotation_matrix_Z(angle):
    """
    Generate a rotation matrix around the Z-axis.
    """
    return np.array([
        [np.cos(angle), -np.sin(angle), 0, 0],
        [np.sin(angle), np.cos(angle), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def matrix_multiply(A, B):
    """
    Multiply two matrices.
    """
    return np.dot(A, B)

def generate_identity():
    return np.eye(4)

### Quaternion
def quaternion_from_axisangle(axis, angle):
    q = {}
    q['a'] = np.cos(angle / 2)
    q['b'] = axis[0] * np.sin(angle / 2)
    q['c'] = axis[1] * np.sin(angle / 2)
    q['d'] = axis[2] * np.sin(angle / 2)
    return q

def quaternion_to_rotation_matrix(q):
    q0 = q['a']
    q1 = q['b']
    q2 = q['c']
    q3 = q['d']
    q02 = q0 * q0
    q12 = q1 * q1
    q22 = q2 * q2
    q32 = q3 * q3
    return np.array([
        [q02 + q12 - q22 - q32, 2 * (q1 * q2 - q0 * q3), 2 * (q0 * q2 + q1 * q3), 0],
        [2 * (q1 * q2 + q0 * q3), q02 - q12 + q22 - q32, 2 * (q2 * q3 - q0 * q1), 0],
        [2 * (q1 * q3 - q0 * q2), 2 * (q0 * q1 + q2 * q3), q02 - q12 - q22 + q32, 0],
        [0, 0, 0, 1]
    ])
