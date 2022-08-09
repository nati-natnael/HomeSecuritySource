import cv2
import zmq
import logging

from time import sleep
from datetime import datetime

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

    def __init__(self, ip, port, camera_id):
        self.ip = ip
        self.port = port
        self.camId = camera_id

    def start(self):
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
