import cv2
import zmq
import yaml
import logging
import datetime

from time import sleep

logging.basicConfig(format="%(asctime)s %(threadName)-9s [%(levelname)s] - %(message)s", level=logging.DEBUG)


def add_datetime_to(frame):
    if len(frame.shape) == 2:
        height, width = frame.shape
    else:
        height, width, _ = frame.shape

    datetime_string = datetime.now().strftime("%b %d, %Y %H:%M:%S")

    cv2.putText(frame, datetime_string, org=(10, height - 20),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)


class Streamer:
    THREAD_SLEEP = 0.0005  # in seconds

    def __init__(self):
        self.ip = None
        self.port = None
        self.camId = None

    def load_config(self, config_file_path):
        try:
            with open(config_file_path, 'r') as file:
                config_dict = yaml.safe_load(file)

                self.ip = config_dict['ip']
                self.port = config_dict['port']
                self.camId = config_dict['camera-id']

        except IOError as e:
            logging.error(f"Exception encountered, {e}")

    def start(self):
        self.load_config("../../src/resources/application.yml")

        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.connect(f"tcp://{self.ip}:{self.port}")

        print(f"Streaming to --> {self.ip}:{self.port}")

        camera = cv2.VideoCapture(self.camId)

        while True:
            _, frame = camera.read()
            frame = cv2.resize(frame, (480, 320))

            add_datetime_to(frame)

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            socket.send(buffer)

            sleep(Streamer.THREAD_SLEEP)
