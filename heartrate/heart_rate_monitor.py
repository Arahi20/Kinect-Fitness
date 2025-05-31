import pygame
import cv2
import numpy as np
from gui.base_menu import BaseMenu
from button import Button
from heartrate.heart_rate_detector import HeartRateDetector

class HeartRateMonitor(BaseMenu):
    def __init__(self, kinect_manager, config):
        super().__init__(kinect_manager, config)
        
        self.hr_detector = HeartRateDetector(config)
        
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
        
        start_button_config = {
            "rect": buttons_cfg.get("hr_start", {}).get("rect", [200, 800, 300, 80]),
            "text": "Start Measurement",
            "font_name": font_name,
            "font_size": fonts_cfg.get("medium_size", 36),
            "min_font_size": min_font_size,
            "text_color": colors_cfg.get("start_button", [0, 255, 0]),
            "bg_color": colors_cfg.get("background", [0, 0, 0]),
            "border_color": colors_cfg.get("button_text", [255, 255, 255]),
            "border_width": button_border_width,
        }
        self.start_button = Button(start_button_config)
        self.start_button.action = "start_hr"
        
        self.buttons = [self.back_button, self.start_button]
        
        self.measurement_started = False
        
    def update(self, surface):
        hand_pos = self.get_hand_position()
        action = self.handle_button_interaction(hand_pos)
        
        if action == "start_hr":
            self.hr_detector.reset()
            self.measurement_started = True
            self.start_button.update_text("Restart Measurement")
            action = None
            
        if self.measurement_started:
            color_frame_surface = self.kinect_manager.get_color_frame()
            if color_frame_surface:
                frame_array = pygame.surfarray.array3d(color_frame_surface)
                frame_array = np.transpose(frame_array, (1, 0, 2))
                frame_array = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
                
                self.hr_detector.process_frame(frame_array)
        
        return action
    
    def draw(self, surface):
        self.draw_background(surface)
        
        title_surface = self.title_font.render("Heart Rate Monitor (Experimental)", True, self.text_color)
        title_rect = title_surface.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(title_surface, title_rect)
        
        if not self.measurement_started:
            instructions = [
                "Position your face in front of the camera",
                "Ensure good lighting on your forehead",
                "Stay still during measurement (30 seconds)",
                "Click 'Start Measurement' when ready"
            ]
            
            for i, instruction in enumerate(instructions):
                inst_surface = self.font.render(instruction, True, self.text_color)
                inst_rect = inst_surface.get_rect(center=(surface.get_width() // 2, 250 + i * 40))
                surface.blit(inst_surface, inst_rect)
        else:
            status = self.hr_detector.get_status_info()
            
            roi = status['roi']
            if roi:
                x, y, w, h = roi
                pygame.draw.rect(surface, (0, 255, 0), (x, y, w, h), 2)
                
                roi_label = self.small_font.render("Forehead Detection", True, (0, 255, 0))
                surface.blit(roi_label, (x, y - 25))
            
            if status['is_counting_down']:
                countdown_remaining = status['countdown_remaining']
                if countdown_remaining > 0:
                    countdown_text = "Get ready! Starting in: {:.0f}".format(countdown_remaining)
                    countdown_surface = self.title_font.render(countdown_text, True, (255, 255, 0))
                    countdown_rect = countdown_surface.get_rect(center=(surface.get_width() // 2, 400))
                    surface.blit(countdown_surface, countdown_rect)
                    
                    instructions_text = "Position yourself in front of the camera"
                    inst_surface = self.font.render(instructions_text, True, self.text_color)
                    inst_rect = inst_surface.get_rect(center=(surface.get_width() // 2, 500))
                    surface.blit(inst_surface, inst_rect)
                else:
                    start_text = "Starting measurement now!"
                    start_surface = self.title_font.render(start_text, True, (0, 255, 0))
                    start_rect = start_surface.get_rect(center=(surface.get_width() // 2, 400))
                    surface.blit(start_surface, start_rect)
            else:
                y_pos = 200
                
                time_text = "Time: {:.1f}s / {}s".format(status['elapsed_time'], status['recording_time'])
                time_surface = self.font.render(time_text, True, self.text_color)
                surface.blit(time_surface, (50, y_pos))
                y_pos += 50
                
                progress = min(status['elapsed_time'] / status['recording_time'], 1.0)
                bar_width = 400
                bar_height = 20
                bar_x = 50
                bar_y = y_pos
                
                pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, int(bar_width * progress), bar_height))
                pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
                y_pos += 50
                
                samples_text = "Samples: {}".format(status['samples_collected'])
                samples_surface = self.font.render(samples_text, True, self.text_color)
                surface.blit(samples_surface, (50, y_pos))
                y_pos += 40
                
                quality = status['signal_quality']
                if quality == "GOOD":
                    quality_color = (0, 255, 0)
                elif quality == "FAIR":
                    quality_color = (255, 255, 0)
                else:
                    quality_color = (255, 0, 0)
                    
                quality_text = "Signal Quality: {}".format(quality)
                quality_surface = self.font.render(quality_text, True, quality_color)
                surface.blit(quality_surface, (50, y_pos))
                y_pos += 60
                
                if status['processing_done']:
                    result_surface = self.font.render(status['final_hr_text'], True, (0, 255, 255))
                    result_rect = result_surface.get_rect(center=(surface.get_width() // 2, y_pos))
                    surface.blit(result_surface, result_rect)
                    
                    complete_text = "Measurement Complete! You can restart or go back."
                    complete_surface = self.small_font.render(complete_text, True, (255, 255, 255))
                    complete_rect = complete_surface.get_rect(center=(surface.get_width() // 2, y_pos + 50))
                    surface.blit(complete_surface, complete_rect)
                elif status['is_recording']:
                    recording_text = "Recording... Stay still and look at the camera"
                    recording_surface = self.small_font.render(recording_text, True, (255, 255, 0))
                    recording_rect = recording_surface.get_rect(center=(surface.get_width() // 2, 840))
                    surface.blit(recording_surface, recording_rect)
        
        for button in self.buttons:
            button.draw(surface)
            
        self.draw_hold_indicator(surface)