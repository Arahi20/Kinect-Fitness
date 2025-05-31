import pygame
import sys
from kinect_manager import KinectManager
from gui.main_menu import MainMenu
from gui.exercise_menu import ExerciseMenu
from gui.exercise_runner import ExerciseRunner
import pygame
import sys
from kinect_manager import KinectManager
from gui.main_menu import MainMenu
from gui.exercise_menu import ExerciseMenu
from gui.exercise_runner import ExerciseRunner
from heartrate.heart_rate_monitor import HeartRateMonitor

class KinectApp:
    def __init__(self, config):
        pygame.init()
        self.config = config
        self.kinect_manager = KinectManager()
        window_cfg = config.get("window", {})
        self.screen = pygame.display.set_mode(
            (window_cfg.get("width", 1920), window_cfg.get("height", 1080)),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption(window_cfg.get("title", "Kinect App"))
        timing_cfg = config.get("timing", {})
        self.fps = timing_cfg.get("fps", 30)
        self.clock = pygame.time.Clock()
        self.current_menu = None
        self.menu_stack = []
        self.switch_to_menu("main")

    def switch_to_menu(self, menu_type, **kwargs):
        if menu_type == "main":
            self.current_menu = MainMenu(self.kinect_manager, self.config)
        elif menu_type == "exercise_select":
            self.current_menu = ExerciseMenu(self.kinect_manager, self.config)
        elif menu_type == "exercise_run":
            exercise_type = kwargs.get("exercise_type", "free_mode")
            self.current_menu = ExerciseRunner(self.kinect_manager, self.config, exercise_type)
        elif menu_type == "heart_rate":
            self.current_menu = HeartRateMonitor(self.kinect_manager, self.config)
        else:
            print("Unknown menu type: {}".format(menu_type))
            return
        
        # Update menu stack for navigation
        if menu_type != "main" and len(self.menu_stack) == 0:
            self.menu_stack.append(menu_type)

    def go_back(self):
        if self.menu_stack:
            self.menu_stack.pop()
        if len(self.menu_stack) == 0:
            self.switch_to_menu("main")
        else:
            # For now, just go back to exercise select or main
            # You could enhance this for deeper navigation if needed
            self.switch_to_menu("exercise_select")

    def handle_menu_action(self, action):
        if action == "quit":
            return False
        elif action == "start":
            self.switch_to_menu("exercise_select")
        elif action == "heart_rate":
            self.switch_to_menu("heart_rate")
        elif action == "back":
            self.go_back()
        elif action in ["squats", "pushups", "jumping_jacks", "free_mode"]:
            self.switch_to_menu("exercise_run", exercise_type=action)
        elif action == "leaderboard":
            print("Leaderboard not implemented yet!")
        return True

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if self.current_menu:
                action = self.current_menu.update(self.screen)
                if action:
                    running = self.handle_menu_action(action)
            
            if self.current_menu:
                self.current_menu.draw(self.screen)
            
            pygame.display.update()
            self.clock.tick(self.fps)
        
        self.kinect_manager.close()
        pygame.quit()
        sys.exit()

class KinectApp:
    def __init__(self, config):
        pygame.init()
        self.config = config
        self.kinect_manager = KinectManager()
        window_cfg = config.get("window", {})
        self.screen = pygame.display.set_mode(
            (window_cfg.get("width", 1920), window_cfg.get("height", 1080)),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption(window_cfg.get("title", "Kinect App"))
        timing_cfg = config.get("timing", {})
        self.fps = timing_cfg.get("fps", 30)
        self.clock = pygame.time.Clock()
        self.current_menu = None
        self.menu_stack = []
        self.switch_to_menu("main")

    def switch_to_menu(self, menu_type, **kwargs):
        if menu_type == "main":
            self.current_menu = MainMenu(self.kinect_manager, self.config)
        elif menu_type == "exercise_select":
            self.current_menu = ExerciseMenu(self.kinect_manager, self.config)
        elif menu_type == "exercise_run":
            exercise_type = kwargs.get("exercise_type", "free_mode")
            self.current_menu = ExerciseRunner(self.kinect_manager, self.config, exercise_type)
        elif menu_type == "heart_rate":
            self.current_menu = HeartRateMonitor(self.kinect_manager, self.config)
        else:
            print("Unknown menu type: {}".format(menu_type))
            return
        
        # Update menu stack for navigation
        if menu_type != "main" and len(self.menu_stack) == 0:
            self.menu_stack.append(menu_type)

    def go_back(self):
        if self.menu_stack:
            self.menu_stack.pop()
        if len(self.menu_stack) == 0:
            self.switch_to_menu("main")
        else:
            # For now, just go back to exercise select or main
            # You could enhance this for deeper navigation if needed
            self.switch_to_menu("exercise_select")

    def handle_menu_action(self, action):
        if action == "quit":
            return False
        elif action == "start":
            self.switch_to_menu("exercise_select")
        elif action == "heart_rate":
            self.switch_to_menu("heart_rate")
        elif action == "back":
            self.go_back()
        elif action in ["squats", "pushups", "jumping_jacks", "free_mode"]:
            self.switch_to_menu("exercise_run", exercise_type=action)
        elif action == "leaderboard":
            print("Leaderboard not implemented yet!")
        return True

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if self.current_menu:
                action = self.current_menu.update(self.screen)
                if action:
                    running = self.handle_menu_action(action)
            
            if self.current_menu:
                self.current_menu.draw(self.screen)
            
            pygame.display.update()
            self.clock.tick(self.fps)
        
        self.kinect_manager.close()
        pygame.quit()
        sys.exit()