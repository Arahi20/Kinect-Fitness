import pygame
from gui.base_menu import BaseMenu
from button import Button
from skeleton_renderer import SkeletonRenderer
from leaderboard.leaderboard_manager import LeaderboardManager

class ExerciseRunner(BaseMenu):
    def __init__(self, kinect_manager, config, exercise_type):
        super().__init__(kinect_manager, config)
        self.exercise_type = exercise_type
        self.skeleton_renderer = SkeletonRenderer(kinect_manager, config)
        self.leaderboard = LeaderboardManager()
        self.session_recorded = False
        self.exercise_detector = None
        if exercise_type == "squats":
            from exercises.squats import SquatsExercise
            self.exercise_detector = SquatsExercise(config)
        elif exercise_type == "jumping_jacks":
            from exercises.jumping_jacks import JumpingJacksExercise
            self.exercise_detector = JumpingJacksExercise(config)
        elif exercise_type == "bicep_curls":
            from exercises.bicep_curls import BicepCurlsExercise
            self.exercise_detector = BicepCurlsExercise(config)
        elif exercise_type == "arm_raises":
            from exercises.arm_raises import ArmRaisesExercise
            self.exercise_detector = ArmRaisesExercise(config)

        colors_cfg = config.get("colors", {})
        buttons_cfg = config.get("buttons", {})
        fonts_cfg = config.get("fonts", {})
        font_name = fonts_cfg.get("font_name", "Arial")
        button_border_width = buttons_cfg.get("border_width", 2)
        min_font_size = buttons_cfg.get("min_font_size", 14)

        back_button_cfg = buttons_cfg.get("back", {})
        back_button_config = {
            "rect": back_button_cfg.get("rect"),
            "text": "Back",
            "font_name": font_name,
            "font_size": fonts_cfg.get("small_size", 24),
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("back_button", [255, 165, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.back_button = Button(back_button_config)
        self.back_button.action = "back"
        self.buttons = [self.back_button]

        self.exercise_titles = {
            "squats": "Squats Challenge",
            "pushups": "Push-ups Challenge",
            "jumping_jacks": "Jumping Jacks Challenge",
            "bicep_curls": "Bicep Curls Challenge",
            "arm_raises": "Arm Raises Challenge",
            "free_mode": "Free Mode - Move Around!"
        }
        self.current_title = self.exercise_titles.get(self.exercise_type, "Exercise Mode")

    def update(self, surface):
        hand_pos = self.get_hand_position()
        action = self.handle_button_interaction(hand_pos)
        
        if action == "back" and self.exercise_detector and not self.session_recorded:
            reps = self.exercise_detector.rep_count
            if reps > 0:
                self.leaderboard.record_session(self.exercise_type, reps, self.exercise_detector)
                self.session_recorded = True
        
        if self.exercise_detector:
            bodies = self.kinect_manager.get_bodies()
            if bodies is not None:
                for i in range(self.kinect_manager.kinect.max_body_count):
                    body = bodies.bodies[i]
                    if body.is_tracked:
                        self.exercise_detector.detect_exercise(body.joints)
                        break
        return action

    def draw(self, surface):
        self.draw_background(surface)
        bodies = self.kinect_manager.get_bodies()
        self.skeleton_renderer.draw(bodies, surface)
        title_surface = self.font.render(self.current_title, True, self.text_color)
        surface.blit(title_surface, (50, 50))

        if self.exercise_detector:
            progress = self.exercise_detector.get_progress_info()
            rep_text = "Reps: {}".format(progress['reps'])
            rep_surface = self.font.render(rep_text, True, self.text_color)
            surface.blit(rep_surface, (50, 100))
            if progress['state'] != "ready":
                state_text = "State: {}".format(progress['state'].replace('_', ' ').title())
                state_surface = self.small_font.render(state_text, True, self.text_color)
                surface.blit(state_surface, (50, 150))
            feedback_text = "Form: {}".format(progress['form_feedback'])
            feedback_surface = self.small_font.render(feedback_text, True, self.text_color)
            surface.blit(feedback_surface, (50, 180))
            if 'hand_head_distance' in progress:
                hand_text = "Hand-Head: {}m (Up: >{}m)".format(progress['hand_head_distance'], progress['arms_up_threshold'])
                hand_color = (0, 255, 0) if progress['hand_head_distance'] > progress['arms_up_threshold'] else (255, 255, 255)
                hand_surface = self.small_font.render(hand_text, True, hand_color)
                surface.blit(hand_surface, (50, 210))

                foot_text = "Foot Distance: {}m (Apart: >{}m)".format(progress['foot_distance'], progress['legs_apart_threshold'])
                foot_color = (0, 255, 0) if progress['foot_distance'] > progress['legs_apart_threshold'] else (255, 255, 255)
                foot_surface = self.small_font.render(foot_text, True, foot_color)
                surface.blit(foot_surface, (50, 240))

                arms_status = "UP" if progress['arms_up'] else "DOWN"
                legs_status = "APART" if progress['legs_apart'] else "TOGETHER"
                status_text = "Arms: {} | Legs: {}".format(arms_status, legs_status)
                status_surface = self.small_font.render(status_text, True, (255, 255, 0))
                surface.blit(status_surface, (50, 270))

            if 'avg_hand_shoulder_distance' in progress:
                avg_distance_text = "Avg Hand-Shoulder: {}m".format(progress['avg_hand_shoulder_distance'])
                avg_surface = self.small_font.render(avg_distance_text, True, (255, 255, 255))
                surface.blit(avg_surface, (50, 210))

                left_text = "Left: {}m".format(progress['left_hand_shoulder_distance'])
                left_color = (0, 255, 0) if progress['left_hand_shoulder_distance'] < progress['curled_threshold'] else (255, 255, 255)
                left_surface = self.small_font.render(left_text, True, left_color)
                surface.blit(left_surface, (50, 240))

                right_text = "Right: {}m".format(progress['right_hand_shoulder_distance'])
                right_color = (0, 255, 0) if progress['right_hand_shoulder_distance'] < progress['curled_threshold'] else (255, 255, 255)
                right_surface = self.small_font.render(right_text, True, right_color)
                surface.blit(right_surface, (200, 240))

                curl_status = "CURLED" if progress['is_curled'] else "EXTENDED"
                curl_surface = self.small_font.render("Position: {}".format(curl_status), True, (255, 255, 0))
                surface.blit(curl_surface, (50, 270))

            if 'avg_hand_shoulder_height' in progress:
                avg_height_text = "Avg Hand Height: {}m".format(progress['avg_hand_shoulder_height'])
                avg_surface = self.small_font.render(avg_height_text, True, (255, 255, 255))
                surface.blit(avg_surface, (50, 210))

                left_text = "Left: {}m".format(progress['left_hand_shoulder_height'])
                left_color = (0, 255, 0) if progress['left_hand_shoulder_height'] > progress['raised_threshold'] else (255, 255, 255)
                left_surface = self.small_font.render(left_text, True, left_color)
                surface.blit(left_surface, (50, 240))

                right_text = "Right: {}m".format(progress['right_hand_shoulder_height'])
                right_color = (0, 255, 0) if progress['right_hand_shoulder_height'] > progress['raised_threshold'] else (255, 255, 255)
                right_surface = self.small_font.render(right_text, True, right_color)
                surface.blit(right_surface, (200, 240))

                raise_status = "RAISED" if progress['are_raised'] else "LOWERED"
                raise_surface = self.small_font.render("Position: {}".format(raise_status), True, (255, 255, 0))
                surface.blit(raise_surface, (50, 270))

        self.back_button.draw(surface)
        self.draw_hold_indicator(surface)