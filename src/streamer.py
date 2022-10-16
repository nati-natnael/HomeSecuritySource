import cv2
import zmq
import logging

from time import sleep
from datetime import datetime
from imutils.video import VideoStream

logging.basicConfig(format='%(asctime)s %(threadName)-9s [%(levelname)s] - %(message)s', level=logging.DEBUG)


def write_text_with_dark_outline(frame, text, text_color, position):
    text_outline_color = (0, 0, 0)

    cv2.putText(frame, f'{text}', org=position,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                color=text_outline_color, thickness=5, lineType=cv2.LINE_AA)
    cv2.putText(frame, f'{text}', org=position,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                color=text_color, thickness=2, lineType=cv2.LINE_AA)


def add_description(frame, camera_name='N/A'):
    if len(frame.shape) == 2:
        height, width = frame.shape
    else:
        height, width, _ = frame.shape

    text_color = (255, 255, 255)
    camera_name_position = (10, 30)
    datetime_position = (10, height - 20)

    write_text_with_dark_outline(frame, camera_name, text_color, camera_name_position)

    datetime_string = datetime.now().strftime('%b %d, %Y %H:%M:%S')

    write_text_with_dark_outline(frame, datetime_string, text_color, datetime_position)


class Streamer:
    THREAD_SLEEP = 0.0005  # in seconds
    FRAME_SIZE = (480, 320)

    def __init__(self, ip, port, camera_id, camera_name):
        self.ip = ip
        self.port = port
        self.camera_id = camera_id
        self.camera_name = camera_name

    def start(self):
        context = zmq.Context()
        client = context.socket(zmq.PUB)
        client.connect(f"tcp://{self.ip}:{self.port}")

        logging.info(f"Streaming to --> {self.ip}:{self.port}")

        vs = VideoStream(src=self.camera_id).start()

        while True:
            frame = vs.read()

            add_description(frame, self.camera_name)

            frame = cv2.resize(frame, Streamer.FRAME_SIZE)

            _, buffer = cv2.imencode('.jpg', frame)

            client.send(buffer)

            sleep(Streamer.THREAD_SLEEP)
