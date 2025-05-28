from .base_exercises import BaseExercise
from pykinect2 import PyKinectV2

class SquatsExercise(BaseExercise):
    def __init__(self, config=None):
        super(SquatsExercise, self).__init__(config)
        self.squat_threshold = 0.15
        self.standing_threshold = 0.25
        self.is_squatting = False
        self.last_hip_knee_distance_left = 0
        self.last_hip_knee_distance_right = 0
        self.last_avg_distance = 0
        self.squat_confirm_frames = 0
        self.stand_confirm_frames = 0
        self.min_confirm_frames = 5

    def get_required_joints(self):
        return [
            PyKinectV2.JointType_HipLeft,
            PyKinectV2.JointType_HipRight,
            PyKinectV2.JointType_KneeLeft,
            PyKinectV2.JointType_KneeRight
        ]

    def _exercise_logic(self, joints):
        hip_left = joints[PyKinectV2.JointType_HipLeft]
        hip_right = joints[PyKinectV2.JointType_HipRight]
        knee_left = joints[PyKinectV2.JointType_KneeLeft]
        knee_right = joints[PyKinectV2.JointType_KneeRight]

        hip_center_y = (hip_left.Position.y + hip_right.Position.y) / 2
        hip_to_left_knee = abs(hip_center_y - knee_left.Position.y)
        hip_to_right_knee = abs(hip_center_y - knee_right.Position.y)
        avg_hip_knee_distance = (hip_to_left_knee + hip_to_right_knee) / 2

        self.last_hip_knee_distance_left = hip_to_left_knee
        self.last_hip_knee_distance_right = hip_to_right_knee
        self.last_avg_distance = avg_hip_knee_distance

        if not self.is_squatting:
            if avg_hip_knee_distance <= self.squat_threshold:
                self.squat_confirm_frames += 1
                self.stand_confirm_frames = 0

                if self.squat_confirm_frames >= self.min_confirm_frames:
                    self.is_squatting = True
                    self.current_state = "squatting"
                    self.form_feedback = "Good squat! Now stand back up"
                    self.squat_confirm_frames = 0
                else:
                    self.current_state = "going_down"
                    self.form_feedback = "Going down... ({}/{})".format(self.squat_confirm_frames, self.min_confirm_frames)
            else:
                self.squat_confirm_frames = 0
                self.current_state = "ready"
                self.form_feedback = "Ready - squat down until hips near knees"
        else:
            if avg_hip_knee_distance >= self.standing_threshold:
                self.stand_confirm_frames += 1
                self.squat_confirm_frames = 0

                if self.stand_confirm_frames >= self.min_confirm_frames:
                    if self.is_squatting:
                        self.rep_count += 1
                        self.is_squatting = False
                        self.current_state = "completed"
                        self.form_feedback = "Rep {} completed! Excellent!".format(self.rep_count)
                    self.stand_confirm_frames = 0
                else:
                    self.current_state = "going_up"
                    self.form_feedback = "Rising up... ({}/{})".format(self.stand_confirm_frames, self.min_confirm_frames)
            else:
                self.stand_confirm_frames = 0
                self.current_state = "squatting"
                if avg_hip_knee_distance < self.squat_threshold * 0.8:
                    self.form_feedback = "Excellent depth! Now stand up"
                else:
                    self.form_feedback = "Good squat! Now stand up"

    def get_progress_info(self):
        base_info = super(SquatsExercise, self).get_progress_info()
        base_info.update({
            'avg_hip_knee_distance': round(self.last_avg_distance, 2),
            'left_hip_knee_distance': round(self.last_hip_knee_distance_left, 2),
            'right_hip_knee_distance': round(self.last_hip_knee_distance_right, 2),
            'squat_threshold': self.squat_threshold,
            'standing_threshold': self.standing_threshold,
            'is_squatting': self.is_squatting
        })
        return base_info
