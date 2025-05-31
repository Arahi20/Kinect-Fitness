import pygame
from gui.base_menu import BaseMenu
from button import Button

class ExerciseMenu(BaseMenu):
    def __init__(self, kinect_manager, config):
        super().__init__(kinect_manager, config)

        colors_cfg = config.get("colors", {})
        buttons_cfg = config.get("buttons", {})
        fonts_cfg = config.get("fonts", {})
        exercises_cfg = config.get("exercises", {})

        font_name = fonts_cfg.get("font_name", "Arial")
        main_size = fonts_cfg.get("main_size", 50)
        medium_size = fonts_cfg.get("medium_size", 36)
        button_border_width = buttons_cfg.get("border_width", 2)
        min_font_size = buttons_cfg.get("min_font_size", 14)

        self.medium_font = pygame.font.SysFont(font_name, medium_size)
        self.exercise_buttons = []

        squats_cfg = exercises_cfg.get("squats", {})
        squats_button_config = {
            "rect": squats_cfg.get("rect"),
            "text": "Squats",
            "font_name": font_name,
            "font_size": medium_size,
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("exercise_button", [0, 150, 255]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        squats_button = Button(squats_button_config)
        squats_button.action = "squats"
        self.exercise_buttons.append(squats_button)

        jumping_jacks_cfg = exercises_cfg.get("jumping_jacks", {})
        jumping_jacks_button_config = {
            "rect": jumping_jacks_cfg.get("rect"),
            "text": "Jumping Jacks",
            "font_name": font_name,
            "font_size": medium_size,
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("exercise_button", [0, 150, 255]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        jumping_jacks_button = Button(jumping_jacks_button_config)
        jumping_jacks_button.action = "jumping_jacks"
        self.exercise_buttons.append(jumping_jacks_button)

        bicep_curls_cfg = exercises_cfg.get("bicep_curls", {})
        bicep_curls_button_config = {
            "rect": bicep_curls_cfg.get("rect"),
            "text": "Bicep Curls",
            "font_name": font_name,
            "font_size": medium_size,
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("exercise_button", [0, 150, 255]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        bicep_curls_button = Button(bicep_curls_button_config)
        bicep_curls_button.action = "bicep_curls"
        self.exercise_buttons.append(bicep_curls_button)

        free_mode_cfg = exercises_cfg.get("free_mode", {})
        free_mode_button_config = {
            "rect": free_mode_cfg.get("rect"),
            "text": "Free Mode",
            "font_name": font_name,
            "font_size": medium_size,
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("free_mode_button", [255, 255, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        free_mode_button = Button(free_mode_button_config)
        free_mode_button.action = "free_mode"
        self.exercise_buttons.append(free_mode_button)

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

        self.buttons = self.exercise_buttons + [self.back_button]

    def update(self, surface):
        hand_pos = self.get_hand_position()
        return self.handle_button_interaction(hand_pos)

    def draw(self, surface):
        self.draw_background(surface)
        title_surface = self.title_font.render("Choose Exercise", True, self.text_color)
        title_rect = title_surface.get_rect(center=(surface.get_width() // 2, 150))
        surface.blit(title_surface, title_rect)
        subtitle_surface = self.font.render("Select your workout:", True, self.text_color)
        subtitle_rect = subtitle_surface.get_rect(center=(surface.get_width() // 2, 220))
        surface.blit(subtitle_surface, subtitle_rect)
        for button in self.buttons:
            button.draw(surface)
        self.draw_hold_indicator(surface)