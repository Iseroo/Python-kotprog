import json


class Config:
    data = None

    def load(path: str):
        with open(path, 'r') as f:
            Config.data = json.load(f)
