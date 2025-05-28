import pygame

class Button:
    def __init__(self, config):
        self.rect = pygame.Rect(config.get("rect", (0, 0, 100, 50)))
        self.text = config.get("text", "Button")
        font_name = config.get("font_name", "Arial")
        font_size = config.get("font_size", 24)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text_color = tuple(config.get("text_color", (255, 255, 255)))
        self.bg_color = tuple(config.get("bg_color", (0, 0, 0)))
        self.border_color = tuple(config.get("border_color", (255, 255, 255)))
        self.border_width = config.get("border_width", 2)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.action = None

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)
        surface.blit(self.text_surface, self.text_rect)