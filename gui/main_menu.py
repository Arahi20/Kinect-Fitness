import pygame
from gui.base_menu import BaseMenu
from button import Button

class MainMenu(BaseMenu):
    def __init__(self, kinect_manager, config):
        super().__init__(kinect_manager, config)
        colors_cfg = config.get("colors", {})
        buttons_cfg = config.get("buttons", {})
        fonts_cfg = config.get("fonts", {})
        font_name = fonts_cfg.get("font_name", "Arial")
        main_size = fonts_cfg.get("main_size", 50)
        medium_size = fonts_cfg.get("medium_size", 36)
        button_border_width = buttons_cfg.get("border_width", 2)
        min_font_size = buttons_cfg.get("min_font_size", 14)

        # Start button
        start_button_cfg = buttons_cfg.get("start", {})
        start_button_config = {
            "rect": start_button_cfg.get("rect", [760, 320, 400, 100]),
            "text": "Start",
            "font_name": font_name,
            "font_size": main_size,
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("start_button", [0, 255, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.start_button = Button(start_button_config)
        self.start_button.action = "start"

        # Heart Rate Monitor button (Experimental)
        heart_rate_button_cfg = buttons_cfg.get("heart_rate", {})
        heart_rate_button_config = {
            "rect": heart_rate_button_cfg.get("rect", [760, 440, 400, 100]),
            "text": "Heart Rate Monitor (Experimental)",
            "font_name": font_name,
            "font_size": medium_size,  # Smaller font to fit longer text
            "text_color": colors_cfg.get("heart_rate_button", [255, 100, 150]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.heart_rate_button = Button(heart_rate_button_config)
        self.heart_rate_button.action = "heart_rate"

        # Leaderboard button
        leaderboard_button_cfg = buttons_cfg.get("leaderboard", {})
        leaderboard_button_config = {
            "rect": leaderboard_button_cfg.get("rect", [760, 560, 400, 100]),
            "text": "Leaderboard",
            "font_name": font_name,
            "font_size": main_size,
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("leaderboard_button", [255, 215, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.leaderboard_button = Button(leaderboard_button_config)
        self.leaderboard_button.action = "leaderboard"

        # Quit button
        quit_button_cfg = buttons_cfg.get("quit", {})
        quit_button_config = {
            "rect": quit_button_cfg.get("rect", [760, 680, 400, 100]),
            "text": "Quit",
            "font_name": font_name,
            "font_size": main_size,
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("quit_button", [255, 0, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.quit_button = Button(quit_button_config)
        self.quit_button.action = "quit"

        self.buttons = [self.start_button, self.heart_rate_button, self.leaderboard_button, self.quit_button]
        self.title = config.get("window", {}).get("title", "Kinect Fitness Playground")

    def update(self, surface):
        hand_pos = self.get_hand_position()
        return self.handle_button_interaction(hand_pos)

    def draw(self, surface):
        self.draw_background(surface)
        title_surface = self.title_font.render(self.title, True, self.text_color)
        title_rect = title_surface.get_rect(center=(surface.get_width() // 2, 200))
        surface.blit(title_surface, title_rect)
        
        for button in self.buttons:
            button.draw(surface)
            
        self.draw_hold_indicator(surface)