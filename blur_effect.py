import pygame
from PIL import Image, ImageFilter
import numpy as np

class BlurEffect:
    def __init__(self, config):
        visual_effects_cfg = config.get("visual_effects", {})
        self.enabled = visual_effects_cfg.get("blur_enabled", False)
        self.radius = visual_effects_cfg.get("blur_radius", 15)
        
    def apply_blur(self, surface):
        """Apply blur effect to camera feed for privacy"""
        if not self.enabled:
            return surface
        
        try:

            width, height = surface.get_size()

            raw_data = pygame.image.tostring(surface, 'RGB')

            pil_image = Image.frombytes('RGB', (width, height), raw_data)
            
            blurred_image = pil_image.filter(ImageFilter.GaussianBlur(radius=self.radius))
            

            raw_blurred = blurred_image.tobytes()
            blurred_surface = pygame.image.fromstring(raw_blurred, (width, height), 'RGB')
            
            return blurred_surface
            
        except Exception as e:
            print("Blur effect error: {}".format(e))
            privacy_surface = pygame.Surface(surface.get_size())
            privacy_surface.fill((50, 50, 50))  
            return privacy_surface
    
    def update_settings(self, enabled=None, radius=None):
        """Update blur settings at runtime"""
        if enabled is not None:
            self.enabled = enabled
        if radius is not None:
            self.radius = max(5, min(50, radius))  