from .base_exercises import BaseExercise
from pykinect2 import PyKinectV2

class BicepCurlsExercise(BaseExercise):
    def __init__(self, config=None):
        super(BicepCurlsExercise, self).__init__(config)
        self.extended_threshold = 0.35
        self.curled_threshold = 0.15
        self.is_curled = False
        self.last_left_hand_shoulder_distance = 0
        self.last_right_hand_shoulder_distance = 0
        self.curl_confirm_frames = 0
        self.extend_confirm_frames = 0
        self.min_confirm_frames = 5

    def get_required_joints(self):
        return [
            PyKinectV2.JointType_ShoulderLeft,
            PyKinectV2.JointType_ShoulderRight,
            PyKinectV2.JointType_HandLeft,
            PyKinectV2.JointType_HandRight
        ]

    def _exercise_logic(self, joints):
        shoulder_left = joints[PyKinectV2.JointType_ShoulderLeft]
        shoulder_right = joints[PyKinectV2.JointType_ShoulderRight]
        hand_left = joints[PyKinectV2.JointType_HandLeft]
        hand_right = joints[PyKinectV2.JointType_HandRight]

        left_distance = self.calculate_distance(hand_left, shoulder_left)
        right_distance = self.calculate_distance(hand_right, shoulder_right)
        avg_distance = (left_distance + right_distance) / 2

        self.last_left_hand_shoulder_distance = left_distance
        self.last_right_hand_shoulder_distance = right_distance

        if not self.is_curled:
            if avg_distance <= self.curled_threshold:
                self.curl_confirm_frames += 1
                self.extend_confirm_frames = 0

                if self.curl_confirm_frames >= self.min_confirm_frames:
                    self.is_curled = True
                    self.current_state = "curled"
                    self.form_feedback = "Good curl! Now extend your arms"
                    self.curl_confirm_frames = 0
                else:
                    self.current_state = "curling"
                    self.form_feedback = "Curling... ({}/{})".format(self.curl_confirm_frames, self.min_confirm_frames)
            else:
                self.curl_confirm_frames = 0
                self.current_state = "ready"
                self.form_feedback = "Ready - curl your arms up to your shoulders"
        else:
            if avg_distance >= self.extended_threshold:
                self.extend_confirm_frames += 1
                self.curl_confirm_frames = 0

                if self.extend_confirm_frames >= self.min_confirm_frames:
                    if self.is_curled:
                        self.rep_count += 1
                        self.is_curled = False
                        self.current_state = "completed"
                        self.form_feedback = "Rep {} completed! Excellent!".format(self.rep_count)
                    self.extend_confirm_frames = 0
                else:
                    self.current_state = "extending"
                    self.form_feedback = "Extending... ({}/{})".format(self.extend_confirm_frames, self.min_confirm_frames)
            else:
                self.extend_confirm_frames = 0
                self.current_state = "curled"
                if avg_distance < self.curled_threshold * 0.8:
                    self.form_feedback = "Perfect curl position! Now extend down"
                else:
                    self.form_feedback = "Good curl! Now extend your arms down"

    def get_progress_info(self):
        base_info = super(BicepCurlsExercise, self).get_progress_info()
        base_info.update({
            'avg_hand_shoulder_distance': round((self.last_left_hand_shoulder_distance + self.last_right_hand_shoulder_distance) / 2, 2),
            'left_hand_shoulder_distance': round(self.last_left_hand_shoulder_distance, 2),
            'right_hand_shoulder_distance': round(self.last_right_hand_shoulder_distance, 2),
            'curled_threshold': self.curled_threshold,
            'extended_threshold': self.extended_threshold,
            'is_curled': self.is_curled
        })
        return base_info