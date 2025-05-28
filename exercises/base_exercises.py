import math
from pykinect2 import PyKinectV2

class BaseExercise:
    def __init__(self, config=None):
        self.config = config or {}
        self.rep_count = 0
        self.current_state = "ready"
        self.last_state = "ready"
        self.state_frames = 0
        self.min_state_frames = 8
        self.form_feedback = ""
    
    def calculate_angle(self, joint1, joint2, joint3):
        try:
            x1, y1 = joint1.Position.x, joint1.Position.y
            x2, y2 = joint2.Position.x, joint2.Position.y
            x3, y3 = joint3.Position.x, joint3.Position.y
            v1 = (x1 - x2, y1 - y2)
            v2 = (x3 - x2, y3 - y2)
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            magnitude1 = math.sqrt(v1[0]**2 + v1[1]**2)
            magnitude2 = math.sqrt(v2[0]**2 + v2[1]**2)
            if magnitude1 == 0 or magnitude2 == 0:
                return 180
            cos_angle = max(-1, min(1, dot_product / (magnitude1 * magnitude2)))
            angle_rad = math.acos(cos_angle)
            angle_deg = math.degrees(angle_rad)
            return angle_deg
        except (AttributeError, ZeroDivisionError):
            return 180
    
    def calculate_distance(self, joint1, joint2):
        try:
            x1, y1, z1 = joint1.Position.x, joint1.Position.y, joint1.Position.z
            x2, y2, z2 = joint2.Position.x, joint2.Position.y, joint2.Position.z
            distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
            return distance
        except AttributeError:
            return 0
    
    def is_joint_tracked(self, joint):
        return joint.TrackingState == PyKinectV2.TrackingState_Tracked
    
    def get_required_joints(self):
        return []
    
    def calibrate(self, joints):
        if self.calibrated:
            return
        self.calibration_frames += 1
        if self.calibration_frames >= self.max_calibration_frames:
            self.calibrated = True
    
    def detect_exercise(self, joints):
        required_joints = self.get_required_joints()
        for joint_type in required_joints:
            if not self.is_joint_tracked(joints[joint_type]):
                self.form_feedback = "Make sure your whole body is visible"
                return
        self._exercise_logic(joints)
    
    def _exercise_logic(self, joints):
        raise NotImplementedError("Subclasses must implement exercise logic")
    
    def _update_state(self, new_state):
        if new_state == self.current_state:
            self.state_frames += 1
        else:
            if self.state_frames >= self.min_state_frames:
                self.last_state = self.current_state
                self.current_state = new_state
                self.state_frames = 0
                return True
            else:
                self.state_frames = 0
        return False
    
    def get_progress_info(self):
        return {
            "reps": self.rep_count,
            "state": self.current_state,
            "form_feedback": self.form_feedback
        }
