import json
from app import KinectApp

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    app = KinectApp(config)
    app.run()
