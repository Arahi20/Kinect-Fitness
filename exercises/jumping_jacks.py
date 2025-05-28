from .base_exercises import BaseExercise
from pykinect2 import PyKinectV2

class JumpingJacksExercise(BaseExercise):
    def __init__(self, config=None):
        super(JumpingJacksExercise, self).__init__(config)
        self.arms_up_threshold = 0.4
        self.legs_apart_threshold = 0.45
        self.recent_arms_up = []
        self.recent_legs_apart = []
        self.overlap_window_frames = 6
        self.last_hand_head_distance = 0
        self.last_foot_distance = 0
        self.waiting_for_return = False

    def get_required_joints(self):
        return [
            PyKinectV2.JointType_Head,
            PyKinectV2.JointType_HandLeft,
            PyKinectV2.JointType_HandRight,
            PyKinectV2.JointType_FootLeft,
            PyKinectV2.JointType_FootRight
        ]

    def _exercise_logic(self, joints):
        hand_left = joints[PyKinectV2.JointType_HandLeft]
        hand_right = joints[PyKinectV2.JointType_HandRight]
        foot_left = joints[PyKinectV2.JointType_FootLeft]
        foot_right = joints[PyKinectV2.JointType_FootRight]
        head = joints[PyKinectV2.JointType_Head]

        left_hand_height = head.Position.y - hand_left.Position.y
        right_hand_height = head.Position.y - hand_right.Position.y
        avg_hand_height = (left_hand_height + right_hand_height) / 2

        foot_distance = abs(foot_left.Position.x - foot_right.Position.x)

        self.last_hand_head_distance = avg_hand_height
        self.last_foot_distance = foot_distance

        arms_up_now = avg_hand_height > self.arms_up_threshold
        legs_apart_now = foot_distance > self.legs_apart_threshold

        complete_jack_now = arms_up_now and legs_apart_now

        self.recent_arms_up.append(arms_up_now)
        self.recent_legs_apart.append(legs_apart_now)

        if len(self.recent_arms_up) > self.overlap_window_frames:
            self.recent_arms_up.pop(0)
        if len(self.recent_legs_apart) > self.overlap_window_frames:
            self.recent_legs_apart.pop(0)

        arms_up_in_window = any(self.recent_arms_up)
        legs_apart_in_window = any(self.recent_legs_apart)

        complete_jack_detected = arms_up_in_window and legs_apart_in_window

        max_arm_height_in_window = max([i for i, arm_up in enumerate(self.recent_arms_up) if arm_up], default=-1)
        max_leg_distance_in_window = max([i for i, leg_apart in enumerate(self.recent_legs_apart) if leg_apart], default=-1)

        if max_arm_height_in_window >= 0 and max_leg_distance_in_window >= 0:
            time_gap = abs(max_arm_height_in_window - max_leg_distance_in_window)
            currently_in_jack = complete_jack_detected and time_gap <= 6
        else:
            currently_in_jack = False

        if not self.waiting_for_return:
            if currently_in_jack:
                self.waiting_for_return = True
                self.waiting_timeout = 0
                self.current_state = "jack_position"
                self.form_feedback = "Perfect jumping jack detected!"
            else:
                self.current_state = "ready"
                if arms_up_now and not legs_apart_now:
                    self.form_feedback = "Good arms! Now spread your legs apart too!"
                elif not arms_up_now and legs_apart_now:
                    self.form_feedback = "Good legs! Now raise your arms above your head!"
                else:
                    self.form_feedback = "Ready - jump with BOTH arms up AND legs apart!"
        else:
            arms_clearly_down = not arms_up_now and avg_hand_height < (self.arms_up_threshold - 0.05)
            legs_clearly_together = not legs_apart_now and foot_distance < (self.legs_apart_threshold - 0.05)
            clear_neutral_position = arms_clearly_down and legs_clearly_together
            both_conditions_expired = not arms_up_in_window and not legs_apart_in_window

            if not hasattr(self, 'waiting_timeout'):
                self.waiting_timeout = 0
            self.waiting_timeout += 1
            timeout_triggered = self.waiting_timeout > 20

            if clear_neutral_position or both_conditions_expired or timeout_triggered:
                self.rep_count += 1
                self.waiting_for_return = False
                self.waiting_timeout = 0
                self.current_state = "ready"
                self.form_feedback = "Rep {} completed! Ready for next one!"
                self.recent_arms_up = []
                self.recent_legs_apart = []
            else:
                self.current_state = "jack_position"
                self.form_feedback = "Great! Return to starting position to complete the rep!"

    def get_progress_info(self):
        base_info = super(JumpingJacksExercise, self).get_progress_info()
        base_info.update({
            'hand_head_distance': round(self.last_hand_head_distance, 2),
            'foot_distance': round(self.last_foot_distance, 2),
            'arms_up_threshold': self.arms_up_threshold,
            'legs_apart_threshold': self.legs_apart_threshold,
            'arms_up': self.last_hand_head_distance > self.arms_up_threshold,
            'legs_apart': self.last_foot_distance > self.legs_apart_threshold
        })
        return base_info
