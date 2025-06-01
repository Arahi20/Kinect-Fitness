import json
import os
from datetime import datetime

class LeaderboardManager:
    def __init__(self, data_file="leaderboard_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self.create_default_data()
    
    def create_default_data(self):
        return {
            "exercises": {
                "squats": {
                    "best_session": {"reps": 0, "form_score": 0, "date": None},
                    "total_reps": 0,
                    "total_sessions": 0,
                    "form_scores": [],
                    "session_history": []
                },
                "jumping_jacks": {
                    "best_session": {"reps": 0, "form_score": 0, "date": None},
                    "total_reps": 0,
                    "total_sessions": 0,
                    "form_scores": [],
                    "session_history": []
                },
                "bicep_curls": {
                    "best_session": {"reps": 0, "form_score": 0, "date": None},
                    "total_reps": 0,
                    "total_sessions": 0,
                    "form_scores": [],
                    "session_history": []
                },
                "arm_raises": {
                    "best_session": {"reps": 0, "form_score": 0, "date": None},
                    "total_reps": 0,
                    "total_sessions": 0,
                    "form_scores": [],
                    "session_history": []
                }
            },
            "overall_stats": {
                "total_workouts": 0,
                "total_lifetime_reps": 0,
                "avg_form_quality": 0,
                "first_workout_date": None,
                "last_workout_date": None
            }
        }
    
    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except:
            return False
    
    def calculate_form_score(self, exercise_detector, total_reps):
        if total_reps == 0:
            return 0
            
        progress = exercise_detector.get_progress_info()
        
        form_penalties = 0
        max_penalties = total_reps * 2
        
        if hasattr(exercise_detector, 'min_confirm_frames'):
            unstable_transitions = max(0, exercise_detector.min_confirm_frames - 3)
            form_penalties += unstable_transitions * 0.1
        
        if 'avg_hip_knee_distance' in progress:
            if progress.get('avg_hip_knee_distance', 0) > progress.get('standing_threshold', 0.3) * 1.5:
                form_penalties += 0.2
        
        if 'avg_hand_shoulder_distance' in progress or 'avg_hand_shoulder_height' in progress:
            if exercise_detector.current_state in ['extending', 'lowering', 'going_up', 'going_down']:
                form_penalties += 0.1
        
        form_score = max(0, min(100, 100 - (form_penalties / max_penalties * 100)))
        return round(form_score, 1)
    
    def record_session(self, exercise_type, reps, exercise_detector):
        if exercise_type not in self.data["exercises"]:
            return False
            
        form_score = self.calculate_form_score(exercise_detector, reps)
        current_date = datetime.now().isoformat()
        
        exercise_data = self.data["exercises"][exercise_type]
        
        session_record = {
            "reps": reps,
            "form_score": form_score,
            "date": current_date
        }
        
        exercise_data["session_history"].append(session_record)
        if len(exercise_data["session_history"]) > 10:
            exercise_data["session_history"] = exercise_data["session_history"][-10:]
        
        exercise_data["total_reps"] += reps
        exercise_data["total_sessions"] += 1
        exercise_data["form_scores"].append(form_score)
        if len(exercise_data["form_scores"]) > 20:
            exercise_data["form_scores"] = exercise_data["form_scores"][-20:]
        
        if reps > exercise_data["best_session"]["reps"]:
            exercise_data["best_session"] = session_record.copy()
        
        self.data["overall_stats"]["total_workouts"] += 1
        self.data["overall_stats"]["total_lifetime_reps"] += reps
        self.data["overall_stats"]["last_workout_date"] = current_date
        
        if not self.data["overall_stats"]["first_workout_date"]:
            self.data["overall_stats"]["first_workout_date"] = current_date
        
        all_form_scores = []
        for ex_data in self.data["exercises"].values():
            all_form_scores.extend(ex_data["form_scores"])
        
        if all_form_scores:
            self.data["overall_stats"]["avg_form_quality"] = round(
                sum(all_form_scores) / len(all_form_scores), 1
            )
        
        self.save_data()
        return True
    
    def get_form_quality_text(self, score):
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Poor"
    
    def get_exercise_stats(self, exercise_type):
        if exercise_type not in self.data["exercises"]:
            return None
            
        exercise_data = self.data["exercises"][exercise_type]
        
        avg_form = 0
        if exercise_data["form_scores"]:
            avg_form = sum(exercise_data["form_scores"]) / len(exercise_data["form_scores"])
        
        good_sessions = sum(1 for score in exercise_data["form_scores"] if score >= 70)
        consistency = (good_sessions / len(exercise_data["form_scores"]) * 100) if exercise_data["form_scores"] else 0
        
        return {
            "best_reps": exercise_data["best_session"]["reps"],
            "best_form_score": exercise_data["best_session"]["form_score"],
            "best_date": exercise_data["best_session"]["date"],
            "total_reps": exercise_data["total_reps"],
            "total_sessions": exercise_data["total_sessions"],
            "avg_form_score": round(avg_form, 1),
            "consistency_percent": round(consistency, 1),
            "recent_sessions": exercise_data["session_history"][-5:]
        }
    
    def get_overall_stats(self):
        return self.data["overall_stats"].copy()