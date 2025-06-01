from .base_exercises import BaseExercise
from pykinect2 import PyKinectV2

class ArmRaisesExercise(BaseExercise):
    def __init__(self, config=None):
        super(ArmRaisesExercise, self).__init__(config)
        self.raised_threshold = 0.15
        self.lowered_threshold = -0.05
        self.are_raised = False
        self.last_left_hand_shoulder_height = 0
        self.last_right_hand_shoulder_height = 0
        self.last_avg_height = 0
        self.raise_confirm_frames = 0
        self.lower_confirm_frames = 0
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

        left_height = hand_left.Position.y - shoulder_left.Position.y
        right_height = hand_right.Position.y - shoulder_right.Position.y
        avg_height = (left_height + right_height) / 2

        self.last_left_hand_shoulder_height = left_height
        self.last_right_hand_shoulder_height = right_height
        self.last_avg_height = avg_height

        if not self.are_raised:
            if avg_height >= self.raised_threshold:
                self.raise_confirm_frames += 1
                self.lower_confirm_frames = 0

                if self.raise_confirm_frames >= self.min_confirm_frames:
                    self.are_raised = True
                    self.current_state = "raised"
                    self.form_feedback = "Good raise! Now lower your arms"
                    self.raise_confirm_frames = 0
                else:
                    self.current_state = "raising"
                    self.form_feedback = "Raising... ({}/{})".format(self.raise_confirm_frames, self.min_confirm_frames)
            else:
                self.raise_confirm_frames = 0
                self.current_state = "ready"
                self.form_feedback = "Ready - raise your arms up to shoulder level"
        else:
            if avg_height <= self.lowered_threshold:
                self.lower_confirm_frames += 1
                self.raise_confirm_frames = 0

                if self.lower_confirm_frames >= self.min_confirm_frames:
                    if self.are_raised:
                        self.rep_count += 1
                        self.are_raised = False
                        self.current_state = "completed"
                        self.form_feedback = "Rep {} completed! Excellent!".format(self.rep_count)
                    self.lower_confirm_frames = 0
                else:
                    self.current_state = "lowering"
                    self.form_feedback = "Lowering... ({}/{})".format(self.lower_confirm_frames, self.min_confirm_frames)
            else:
                self.lower_confirm_frames = 0
                self.current_state = "raised"
                if avg_height > self.raised_threshold * 1.2:
                    self.form_feedback = "Perfect height! Now lower your arms"
                else:
                    self.form_feedback = "Good raise! Now lower your arms down"

    def get_progress_info(self):
        base_info = super(ArmRaisesExercise, self).get_progress_info()
        base_info.update({
            'avg_hand_shoulder_height': round(self.last_avg_height, 2),
            'left_hand_shoulder_height': round(self.last_left_hand_shoulder_height, 2),
            'right_hand_shoulder_height': round(self.last_right_hand_shoulder_height, 2),
            'raised_threshold': self.raised_threshold,
            'lowered_threshold': self.lowered_threshold,
            'are_raised': self.are_raised
        })
        return base_info