import time
import requests
import sys
import os
import re
import json
import datetime
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

file_path = sys.argv[1]
endpoint = sys.argv[2]

class ConfigLoader:
    def load_config(self):
        with open("config.json", "r") as config:
            return json.load(config)

class DataParser:
    def __init__(self):
        config = ConfigLoader().load_config()
        self.replacements = config["replacements"]
        self.use_computer_datetime = config["use-computer-datetime"]
    
    def get_datetime_value(self, date, time):
        if self.use_computer_datetime:
            date_and_time = str(datetime.datetime.now(datetime.timezone.utc))
            return date_and_time[:-13]
        else:
            date_and_time = datetime.datetime.fromisoformat("20" + date[:2] + "-" + date[2:4] + "-" + date[4:6] + " " + time[:2] + ":" + time[2:4] + ":" + time[4:6])
            return str(date_and_time.astimezone(datetime.timezone.utc))[:-6]

    def parse_data(self, data):
        data_split = (re.split(r':|;', data[1:-1]))
        data_dict = {}
        for i in range(0, len(data_split), 2):
            key = data_split[i]
            value = data_split[i+1]
            if key not in self.replacements:
                data_dict[key] = value
            else:
                data_dict[key] = self.replacements[key]
        data_dict["DT"] = self.get_datetime_value(data_dict["D"], data_dict["T"])
        data_dict.pop("D")
        data_dict.pop("T")
        return data_dict
    
class DataSender:
    def send_request(self, data):
        print(f"Sending data to: {endpoint}")
        response = requests.post(endpoint, json = data)
        print(f"Status: {response.status_code}")

class FileModificationHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_data = ""
        self.sender = DataSender()
        self.parser = DataParser()
        config = ConfigLoader().load_config()
        self.encoding = config["file-encoding"]

    def on_modified(self, event):
        if event.src_path == file_path:
            try:
                with open(file_path, "r", encoding = self.encoding) as file:
                    data = {
                        "content": self.parser.parse_data(file.read()),
                        "password": os.getenv("METEO_PASSWORD")
                    }
                    if data["content"] != self.last_data:
                        self.last_data = data["content"]
                        self.sender.send_request(data)
            except Exception as e:
                print(f"Error while parsing or sending data: {e}")

if __name__ == "__main__":
    file_modification_handler = FileModificationHandler()
    observer = Observer()
    observer.schedule(file_modification_handler, os.path.dirname(file_path), recursive = False)
    observer.start()

    print(f"Ready, data from {file_path} will be sent to {endpoint}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()