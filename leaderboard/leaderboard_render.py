import pygame
from gui.base_menu import BaseMenu
from button import Button
from leaderboard.leaderboard_manager import LeaderboardManager

class LeaderboardRender(BaseMenu):
    def __init__(self, kinect_manager, config):
        super().__init__(kinect_manager, config)
        
        self.leaderboard = LeaderboardManager()
        
        colors_cfg = config.get("colors", {})
        buttons_cfg = config.get("buttons", {})
        fonts_cfg = config.get("fonts", {})
        font_name = fonts_cfg.get("font_name", "Arial")
        button_border_width = buttons_cfg.get("border_width", 2)
        min_font_size = buttons_cfg.get("min_font_size", 14)
        
        back_button_cfg = buttons_cfg.get("back", {})
        back_button_config = {
            "rect": back_button_cfg.get("rect", [1550, 800, 200, 80]),
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
        
        self.scroll_offset = 0
        self.max_scroll = 0
        
    def update(self, surface):
        hand_pos = self.get_hand_position()
        return self.handle_button_interaction(hand_pos)
    
    def draw(self, surface):
        self.draw_background(surface)
        
        title_surface = self.title_font.render("Personal Records", True, self.text_color)
        title_rect = title_surface.get_rect(center=(surface.get_width() // 2, 80))
        surface.blit(title_surface, title_rect)
        
        y_pos = 150 - self.scroll_offset
        
        overall_stats = self.leaderboard.get_overall_stats()
        
        if overall_stats["total_workouts"] > 0:
            overall_text = "Overall Stats"
            overall_surface = self.font.render(overall_text, True, (255, 215, 0))
            surface.blit(overall_surface, (50, y_pos))
            y_pos += 50
            
            stats_lines = [
                "Total Workouts: {}".format(overall_stats['total_workouts']),
                "Lifetime Reps: {}".format(overall_stats['total_lifetime_reps']),
                "Average Form Quality: {}% ({})".format(overall_stats['avg_form_quality'], self.leaderboard.get_form_quality_text(overall_stats['avg_form_quality']))
            ]
            
            for line in stats_lines:
                line_surface = self.small_font.render(line, True, self.text_color)
                surface.blit(line_surface, (70, y_pos))
                y_pos += 30
            
            y_pos += 20
            
            exercises = ["squats", "jumping_jacks", "bicep_curls", "arm_raises"]
            exercise_names = ["Squats", "Jumping Jacks", "Bicep Curls", "Arm Raises"]
            
            for exercise_type, display_name in zip(exercises, exercise_names):
                stats = self.leaderboard.get_exercise_stats(exercise_type)
                
                if stats and stats["total_sessions"] > 0:
                    exercise_title = "{} Records".format(display_name)
                    title_surface = self.font.render(exercise_title, True, (100, 200, 255))
                    surface.blit(title_surface, (50, y_pos))
                    y_pos += 40
                    
                    if stats["best_reps"] > 0:
                        best_text = "Personal Best: {} reps".format(stats['best_reps'])
                        best_surface = self.small_font.render(best_text, True, (0, 255, 0))
                        surface.blit(best_surface, (70, y_pos))
                        y_pos += 25
                        
                        form_text = "Best Session Form: {}% ({})".format(stats['best_form_score'], self.leaderboard.get_form_quality_text(stats['best_form_score']))
                        form_color = self.get_form_color(stats['best_form_score'])
                        form_surface = self.small_font.render(form_text, True, form_color)
                        surface.blit(form_surface, (70, y_pos))
                        y_pos += 25
                    
                    lifetime_text = "Total: {} reps in {} sessions".format(stats['total_reps'], stats['total_sessions'])
                    lifetime_surface = self.small_font.render(lifetime_text, True, self.text_color)
                    surface.blit(lifetime_surface, (70, y_pos))
                    y_pos += 25
                    
                    avg_form_text = "Average Form: {}% ({})".format(stats['avg_form_score'], self.leaderboard.get_form_quality_text(stats['avg_form_score']))
                    avg_form_color = self.get_form_color(stats['avg_form_score'])
                    avg_form_surface = self.small_font.render(avg_form_text, True, avg_form_color)
                    surface.blit(avg_form_surface, (70, y_pos))
                    y_pos += 25
                    
                    consistency_text = "Consistency: {}% good form sessions".format(stats['consistency_percent'])
                    consistency_surface = self.small_font.render(consistency_text, True, self.text_color)
                    surface.blit(consistency_surface, (70, y_pos))
                    y_pos += 35
        else:
            no_data_text = "No workout data yet!"
            no_data_surface = self.font.render(no_data_text, True, self.text_color)
            no_data_rect = no_data_surface.get_rect(center=(surface.get_width() // 2, 300))
            surface.blit(no_data_surface, no_data_rect)
            
            instruction_text = "Complete some exercises to see your personal records here."
            instruction_surface = self.small_font.render(instruction_text, True, self.text_color)
            instruction_rect = instruction_surface.get_rect(center=(surface.get_width() // 2, 350))
            surface.blit(instruction_surface, instruction_rect)
        
        self.back_button.draw(surface)
        self.draw_hold_indicator(surface)
    
    def get_form_color(self, score):
        if score >= 90:
            return (0, 255, 0)
        elif score >= 70:
            return (255, 255, 0)
        elif score >= 50:
            return (255, 165, 0)
        else:
            return (255, 0, 0)