import pygame

class Button:
    def __init__(self, config):
        self.rect = pygame.Rect(config.get("rect", (0, 0, 100, 50)))
        self.text = config.get("text", "Button")
        font_name = config.get("font_name", "Arial")
        initial_font_size = config.get("font_size", 24)
        self.text_color = tuple(config.get("text_color", (255, 255, 255)))
        self.bg_color = tuple(config.get("bg_color", (0, 0, 0)))
        self.border_color = tuple(config.get("border_color", (255, 255, 255)))
        self.border_width = config.get("border_width", 2)
        
        self.font_name = font_name
        self.max_font_size = initial_font_size
        self.min_font_size = config.get("min_font_size", 12)
        
        self.font, self.font_size = self._fit_text_to_rect()
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.action = None

    def _fit_text_to_rect(self):
        padding = 10
        available_width = self.rect.width - (padding * 2)
        available_height = self.rect.height - (padding * 2)
        
        font_size = self.max_font_size
        
        while font_size >= self.min_font_size:
            test_font = pygame.font.SysFont(self.font_name, font_size)
            text_surface = test_font.render(self.text, True, self.text_color)
            text_width, text_height = text_surface.get_size()
            
            if text_width <= available_width and text_height <= available_height:
                return test_font, font_size
                
            font_size -= 1
        
        return pygame.font.SysFont(self.font_name, self.min_font_size), self.min_font_size

    def update_text(self, new_text):
        self.text = new_text
        self.font, self.font_size = self._fit_text_to_rect()
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)
        surface.blit(self.text_surface, self.text_rect)