import pygame
import math
from pykinect2 import PyKinectV2

BONES = [
    (PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck),
    (PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder),
    (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid),
    (PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase),
    (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight),
    (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft),
    (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight),
    (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft),
    (PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight),
    (PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight),
    (PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight),
    (PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft),
    (PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft),
    (PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft),
    (PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight),
    (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight),
    (PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight),
    (PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft),
    (PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft),
    (PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft),
]

class SkeletonRenderer:
    def __init__(self, kinect_manager, config=None):
        self.kinect_manager = kinect_manager
        if config is None:
            config = {}
        colors_cfg = config.get("colors", {})
        skeleton_cfg = config.get("skeleton", {})
        self.bone_color = tuple(colors_cfg.get("skeleton_bones", [0, 255, 0]))
        self.joint_color = tuple(colors_cfg.get("skeleton_joints", [255, 0, 0]))
        self.bone_thickness = skeleton_cfg.get("bone_thickness", 4)
        self.joint_radius = skeleton_cfg.get("joint_radius", 5)

    def is_valid_point(self, point):
        return not math.isinf(point.x) and not math.isinf(point.y)

    def draw(self, bodies, surface):
        if bodies is None:
            return
        for i in range(self.kinect_manager.kinect.max_body_count):
            body = bodies.bodies[i]
            if not body.is_tracked:
                continue
            joints = body.joints
            joint_points = self.kinect_manager.kinect.body_joints_to_color_space(joints)
            for bone in BONES:
                start_joint, end_joint = bone
                if joints[start_joint].TrackingState == PyKinectV2.TrackingState_NotTracked or \
                   joints[end_joint].TrackingState == PyKinectV2.TrackingState_NotTracked:
                    continue
                start = joint_points[start_joint]
                end = joint_points[end_joint]
                if self.is_valid_point(start) and self.is_valid_point(end):
                    pygame.draw.line(surface, self.bone_color,
                                     (int(start.x), int(start.y)), (int(end.x), int(end.y)), 
                                     self.bone_thickness)
            for joint_id in range(PyKinectV2.JointType_Count):
                joint = joints[joint_id]
                point = joint_points[joint_id]
                if joint.TrackingState != PyKinectV2.TrackingState_NotTracked and self.is_valid_point(point):
                    pygame.draw.circle(surface, self.joint_color, 
                                       (int(point.x), int(point.y)), self.joint_radius)
