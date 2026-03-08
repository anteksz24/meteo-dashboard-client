import time
import requests
import sys
import os
import re
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

file_path = sys.argv[1]
endpoint = sys.argv[2]

class DataParser:
    def parse_data(self, data):
        data_split = (re.split(r':|;', data[1:-1]))
        data_dict = {}
        for i in range(0, len(data_split), 2):
            key = data_split[i]
            value = data_split[i+1]
            data_dict[key] = value
        return data_dict
    
class DataSender:
    def send_request(self, data):
        print(f"Sending data to: {endpoint}")
        try:
            response = requests.post(endpoint, json = data)
            print(f"Status: {response.status_code}")
        except Exception as e:
            print(f"Error while sending data: {e}")

class FileModificationHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_data = ""
        self.sender = DataSender()
        self.parser = DataParser()

    def on_modified(self, event):
        if event.event_type == "modified" and event.src_path == file_path:
            with open(file_path, "r") as file:
                data = {
                    "content": self.parser.parse_data(file.read()),
                    "password": os.getenv("METEO_PASSWORD")
                }
                if data["content"] != self.last_data:
                    self.last_data = data["content"]
                    self.sender.send_request(data)

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