import cv2
import numpy as np
import time
from collections import deque
from scipy import signal as scipy_signal

class HeartRateDetector:
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        hr_config = config.get("heart_rate", {})
        
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        self.max_samples = hr_config.get("max_samples", 900)
        self.red_signal = deque(maxlen=self.max_samples)
        self.green_signal = deque(maxlen=self.max_samples)
        self.blue_signal = deque(maxlen=self.max_samples)
        self.timestamps = deque(maxlen=self.max_samples)
        
        self.fps = hr_config.get("fps", 30)
        self.recording_time = hr_config.get("recording_time", 30)
        self.countdown_time = hr_config.get("countdown_time", 5)
        self.no_detection_timeout = hr_config.get("no_detection_timeout", 15)
        self.min_hr = hr_config.get("min_hr", 50)
        self.max_hr = hr_config.get("max_hr", 180)
        
        self.last_roi = None
        self.start_time = None
        self.countdown_start_time = None
        self.last_detection_time = None
        self.is_counting_down = False
        self.is_recording = False
        self.processing_done = False
        self.final_hr_text = "Preparing..."
        self.current_quality = "INSUFFICIENT"
        
    def reset(self):
        self.red_signal.clear()
        self.green_signal.clear()
        self.blue_signal.clear()
        self.timestamps.clear()
        self.countdown_start_time = time.time()
        self.start_time = None
        self.last_detection_time = None
        self.is_counting_down = True
        self.is_recording = False
        self.processing_done = False
        self.final_hr_text = "Get ready..."
        self.current_quality = "INSUFFICIENT"
        
    def detect_forehead_roi(self, gray_frame):
        faces = self.face_cascade.detectMultiScale(
            gray_frame, 
            scaleFactor=1.1, 
            minNeighbors=8, 
            minSize=(80, 80),
            maxSize=(400, 400),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        if len(faces) == 0:
            self.last_roi = None
            return None
            
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        
        face_area = w * h
        if face_area < 6400:
            self.last_roi = None
            return None
            
        roi_x = x + w // 4
        roi_y = y + int(h * 0.15)
        roi_width = w // 2
        roi_height = h // 5
        
        if roi_width < 40 or roi_height < 20:
            self.last_roi = None
            return None
        
        self.last_roi = (roi_x, roi_y, roi_width, roi_height)
        self.last_detection_time = time.time()
        return self.last_roi
        
    def extract_roi_signal(self, frame, roi):
        if roi is None:
            return None, None, None
            
        x, y, w, h = roi
        
        if x < 0 or y < 0 or x + w >= frame.shape[1] or y + h >= frame.shape[0]:
            return None, None, None
            
        roi_region = frame[y:y + h, x:x + w]
        if roi_region.size == 0:
            return None, None, None
            
        red_mean = np.mean(roi_region[:, :, 2])
        green_mean = np.mean(roi_region[:, :, 1])
        blue_mean = np.mean(roi_region[:, :, 0])
        
        return red_mean, green_mean, blue_mean
        
    def simple_bandpass_filter(self, data, fs, lowcut=0.8, highcut=3.0, order=4):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        
        if low >= 1.0 or high >= 1.0:
            return data
            
        try:
            b, a = scipy_signal.butter(order, [low, high], btype='band')
            return scipy_signal.filtfilt(b, a, data)
        except:
            return data
            
    def estimate_heart_rate_fft(self, signal_data, fs):
        if len(signal_data) < 100:
            return None
            
        signal_array = np.array(signal_data)
        
        if np.std(signal_array) == 0:
            return None
            
        signal_normalized = (signal_array - np.mean(signal_array)) / np.std(signal_array)
        
        filtered_signal = self.simple_bandpass_filter(signal_normalized, fs)
        
        fft = np.abs(np.fft.fft(filtered_signal))
        freqs = np.fft.fftfreq(len(filtered_signal), 1.0/fs)
        
        min_freq = self.min_hr / 60.0
        max_freq = self.max_hr / 60.0
        valid_indices = np.where((freqs >= min_freq) & (freqs <= max_freq))[0]
        
        if len(valid_indices) == 0:
            return None
            
        valid_fft = fft[valid_indices]
        valid_freqs = freqs[valid_indices]
        peak_idx = np.argmax(valid_fft)
        peak_freq = valid_freqs[peak_idx]
        
        heart_rate = peak_freq * 60
        
        return heart_rate if self.min_hr <= heart_rate <= self.max_hr else None
        
    def get_signal_quality(self, signal_data):
        if len(signal_data) < 30:
            return "INSUFFICIENT"
            
        std_dev = np.std(np.array(signal_data))
        if std_dev < 0.5:
            return "POOR"
        elif std_dev < 2.0:
            return "FAIR"
        else:
            return "GOOD"
            
    def process_frame(self, frame):
        if self.processing_done:
            return
            
        if self.is_counting_down:
            elapsed_countdown = time.time() - self.countdown_start_time
            if elapsed_countdown >= self.countdown_time:
                self.is_counting_down = False
                self.is_recording = True
                self.start_time = time.time()
                self.last_detection_time = time.time()
                self.final_hr_text = "Recording..."
            return
            
        if not self.is_recording:
            return
            
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        roi = self.detect_forehead_roi(gray)
        
        if self.last_detection_time and time.time() - self.last_detection_time > self.no_detection_timeout:
            self.processing_done = True
            self.is_recording = False
            self.final_hr_text = "Insufficient data - no face detected"
            return
        
        red_val, green_val, blue_val = self.extract_roi_signal(frame, roi)
        
        if green_val is not None:
            self.red_signal.append(red_val)
            self.green_signal.append(green_val)
            self.blue_signal.append(blue_val)
            self.timestamps.append(time.time())
            
            if len(self.green_signal) > 30:
                self.current_quality = self.get_signal_quality(list(self.green_signal)[-30:])
        
        if self.start_time and time.time() - self.start_time >= self.recording_time:
            self._process_final_heart_rate()
            
    def _process_final_heart_rate(self):
        if self.processing_done:
            return
            
        self.processing_done = True
        self.is_recording = False
        self.final_hr_text = "Unable to detect HR"
        
        if len(self.green_signal) > 300:
            hr_results = {}
            
            for name, data in [('Red', self.red_signal), ('Green', self.green_signal), ('Blue', self.blue_signal)]:
                hr = self.estimate_heart_rate_fft(list(data), self.fps)
                if hr:
                    hr_results[name] = hr
                    
            if hr_results:
                if 'Green' in hr_results:
                    final_hr = hr_results['Green']
                    method = "Green"
                else:
                    final_hr = np.median(list(hr_results.values()))
                    method = "Multi"
                    
                hr_std = np.std(list(hr_results.values()))
                if hr_std < 5:
                    confidence = "High"
                elif hr_std < 10:
                    confidence = "Med"
                else:
                    confidence = "Low"
                    
                self.final_hr_text = "HR: {:.1f} BPM ({}, {})".format(final_hr, method, confidence)
            else:
                self.final_hr_text = "No valid HR detected"
        else:
            self.final_hr_text = "Insufficient data"
            
    def get_roi_for_display(self):
        return self.last_roi
        
    def get_elapsed_time(self):
        if self.is_counting_down:
            return 0
        if not self.start_time:
            return 0
        if self.processing_done:
            return self.recording_time
        return time.time() - self.start_time
        
    def get_countdown_remaining(self):
        if not self.is_counting_down or not self.countdown_start_time:
            return 0
        elapsed = time.time() - self.countdown_start_time
        return max(0, self.countdown_time - elapsed)
        
    def get_samples_collected(self):
        return len(self.green_signal)
        
    def get_status_info(self):
        return {
            'is_counting_down': self.is_counting_down,
            'countdown_remaining': self.get_countdown_remaining(),
            'is_recording': self.is_recording,
            'processing_done': self.processing_done,
            'elapsed_time': self.get_elapsed_time(),
            'recording_time': self.recording_time,
            'samples_collected': self.get_samples_collected(),
            'signal_quality': self.current_quality,
            'final_hr_text': self.final_hr_text,
            'roi': self.get_roi_for_display()
        }