import pygame
import numpy as np
from pykinect2 import PyKinectV2, PyKinectRuntime

class KinectManager:
    def __init__(self):
        self.kinect = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body
        )
        self.width = self.kinect.color_frame_desc.Width
        self.height = self.kinect.color_frame_desc.Height

    def get_color_frame(self):
        if self.kinect.has_new_color_frame():
            frame = self.kinect.get_last_color_frame()
            frame = frame.reshape((self.height, self.width, 4))  # BGRA
            frame_rgb = frame[:, :, :3][:, :, ::-1]  # to RGB
            return pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        return None

    def get_bodies(self):
        if self.kinect.has_new_body_frame():
            return self.kinect.get_last_body_frame()
        return None

    def close(self):
        self.kinect.close()
