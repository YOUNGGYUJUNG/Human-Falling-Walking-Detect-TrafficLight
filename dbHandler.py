import pyrebase
import json

class DBModule:
    def __init__(self):
        with open("C:/python/yolov5-master/static/dbData.json") as f:
            config = json.load(f)

        self.firebase = pyrebase.initialize_app(config)
    
    def login(self, id, pwd):
        pass

    def signin(self, id, pwd, name, id_num, birth, address, position):
        pass

    def graph(self, num, date, location):
        pass