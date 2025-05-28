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
        button_border_width = buttons_cfg.get("border_width", 2)

        start_button_cfg = buttons_cfg.get("start", {})
        start_button_config = {
            "rect": start_button_cfg.get("rect", [760, 400, 400, 100]),
            "text": "Start",
            "font_name": font_name,
            "font_size": main_size,
            "text_color": colors_cfg.get("start_button", [0, 255, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.start_button = Button(start_button_config)
        self.start_button.action = "start"

        leaderboard_button_cfg = buttons_cfg.get("leaderboard", {})
        leaderboard_button_config = {
            "rect": leaderboard_button_cfg.get("rect", [760, 530, 400, 100]),
            "text": "Leaderboard",
            "font_name": font_name,
            "font_size": main_size,
            "text_color": colors_cfg.get("leaderboard_button", [255, 215, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.leaderboard_button = Button(leaderboard_button_config)
        self.leaderboard_button.action = "leaderboard"

        quit_button_cfg = buttons_cfg.get("quit", {})
        quit_button_config = {
            "rect": quit_button_cfg.get("rect", [760, 660, 400, 100]),
            "text": "Quit",
            "font_name": font_name,
            "font_size": main_size,
            "text_color": colors_cfg.get("quit_button", [255, 0, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.quit_button = Button(quit_button_config)
        self.quit_button.action = "quit"

        self.buttons = [self.start_button, self.leaderboard_button, self.quit_button]
        self.title = config.get("window", {}).get("title", "Kinect Fitness Playground")

    def update(self, surface):
        hand_pos = self.get_hand_position()
        return self.handle_button_interaction(hand_pos)

    def draw(self, surface):
        self.draw_background(surface)
        title_surface = self.title_font.render(self.title, True, self.text_color)
        title_rect = title_surface.get_rect(center=(surface.get_width() // 2, 200))
        surface.blit(title_surface, title_rect)
        self.start_button.draw(surface)
        self.leaderboard_button.draw(surface)
        self.quit_button.draw(surface)
        self.draw_hold_indicator(surface)
