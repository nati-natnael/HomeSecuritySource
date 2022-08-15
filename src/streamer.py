import cv2
import socket
import logging

from time import sleep
from datetime import datetime
from imutils.video import VideoStream

logging.basicConfig(format="%(asctime)s %(threadName)-9s [%(levelname)s] - %(message)s", level=logging.DEBUG)


def add_datetime(frame, camera_name="N/A"):
    if len(frame.shape) == 2:
        height, width = frame.shape
    else:
        height, width, _ = frame.shape

    text_color = (0, 0, 255)

    cv2.putText(frame, f"Cam {camera_name}", org=(10, 30),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                color=text_color, thickness=2, lineType=cv2.LINE_AA)

    datetime_string = datetime.now().strftime("%b %d, %Y %H:%M:%S")

    cv2.putText(frame, datetime_string, org=(10, height - 20),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                color=text_color, thickness=2, lineType=cv2.LINE_AA)


class Streamer:
    THREAD_SLEEP = 0.0005  # in seconds
    MAX_MSG_SIZE = 60000   # in bytes
    DIGIT_COUNT = 8
    FRAME_SIZE = (480, 320)

    def __init__(self, ip, port, camera_id):
        self.ip = ip
        self.port = port
        self.camera_id = camera_id

    def start(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_addr = (self.ip, self.port)

        print(f"streaming to --> {server_addr}")

        vs = VideoStream(src=self.camera_id).start()

        while True:
            frame = vs.read()

            add_datetime(frame)

            frame = cv2.resize(frame, Streamer.FRAME_SIZE)

            _, buffer = cv2.imencode('.jpg', frame)

            padded_buffer_size = str(buffer.size).zfill(8)

            msg_start = bytes(f"START,{padded_buffer_size}", "utf-8")

            # send message
            client.sendto(msg_start, server_addr)

            buffer_bytes = buffer.tobytes()
            for x in range(0, buffer.size, Streamer.MAX_MSG_SIZE):
                start = x
                end = start + Streamer.MAX_MSG_SIZE

                if end > buffer.size:
                    end = buffer.size

                send_buf = buffer_bytes[start:end]
                client.sendto(send_buf, server_addr)

            sleep(Streamer.THREAD_SLEEP)
