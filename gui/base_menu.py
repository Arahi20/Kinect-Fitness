import pygame
import time
from pykinect2 import PyKinectV2
from blur_effect import BlurEffect

class BaseMenu:
    def __init__(self, kinect_manager, config):
        self.kinect_manager = kinect_manager
        self.config = config

        self.blur_effect = BlurEffect(config)

        fonts_cfg = config.get("fonts", {})
        font_name = fonts_cfg.get("font_name", "Arial")
        main_size = fonts_cfg.get("main_size", 50)
        small_size = fonts_cfg.get("small_size", 24)
        title_size = fonts_cfg.get("title_size", 72)

        self.font = pygame.font.SysFont(font_name, main_size)
        self.small_font = pygame.font.SysFont(font_name, small_size)
        self.title_font = pygame.font.SysFont(font_name, title_size)

        colors_cfg = config.get("colors", {})
        self.bg_color = tuple(colors_cfg.get("background", [0, 0, 0]))
        self.text_color = tuple(colors_cfg.get("text", [255, 255, 255]))
        self.holding_text_color = tuple(colors_cfg.get("holding_text", [255, 255, 0]))

        timing_cfg = config.get("timing", {})
        self.hold_threshold = timing_cfg.get("hold_time", 1.5)

        self.holding_start_time = None
        self.holding_button = None

        self.buttons = []

    def get_hand_position(self):
        bodies = self.kinect_manager.get_bodies()
        if bodies is None:
            return None

        for i in range(self.kinect_manager.kinect.max_body_count):
            body = bodies.bodies[i]
            if not body.is_tracked:
                continue

            joints = body.joints
            joint_points = self.kinect_manager.kinect.body_joints_to_color_space(joints)
            hand_right = joint_points[PyKinectV2.JointType_HandRight]

            if not (hand_right.x == float('inf') or hand_right.y == float('inf')):
                return (hand_right.x, hand_right.y)

        return None

    def handle_button_interaction(self, hand_pos):
        if not hand_pos:
            self.holding_start_time = None
            self.holding_button = None
            return None

        hovered_button = None
        for button in self.buttons:
            if button.rect.collidepoint(hand_pos):
                hovered_button = button.action
                break

        if hovered_button:
            if self.holding_button == hovered_button:
                elapsed = time.time() - self.holding_start_time
            else:
                self.holding_start_time = time.time()
                self.holding_button = hovered_button
                elapsed = 0
        else:
            self.holding_start_time = None
            self.holding_button = None
            elapsed = 0

        if self.holding_button and elapsed >= self.hold_threshold:
            action = self.holding_button
            self.holding_start_time = None
            self.holding_button = None
            return action

        return None

    def draw_hold_indicator(self, surface):
        if not self.holding_button or not self.holding_start_time:
            return

        elapsed = time.time() - self.holding_start_time
        if elapsed <= 0:
            return

        target_button = None
        for button in self.buttons:
            if button.action == self.holding_button:
                target_button = button
                break

        if target_button:
            hold_text = self.small_font.render("Holding: {:.1f}s".format(elapsed), True, self.holding_text_color)
            text_x = target_button.rect.centerx - hold_text.get_width() // 2
            text_y = target_button.rect.top - hold_text.get_height() - 10
            surface.blit(hold_text, (text_x, text_y))

    def draw_background(self, surface):
        surface.fill(self.bg_color)
        color_frame_surface = self.kinect_manager.get_color_frame()
        if color_frame_surface:
            if self.blur_effect.enabled:
                color_frame_surface = self.blur_effect.apply_blur(color_frame_surface)
            surface.blit(color_frame_surface, (0, 0))

    def update(self, surface):
        pass

    def draw(self, surface):
        pass
