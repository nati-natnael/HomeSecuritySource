import cv2
import socket
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


def send_frame(client_socket, server_addr, buffer):
    padded_buffer_size = str(buffer.size).zfill(Streamer.DIGIT_COUNT)

    msg_start = bytes(f'START,{padded_buffer_size}', 'utf-8')

    # send message
    client_socket.sendto(msg_start, server_addr)

    buffer_bytes = buffer.tobytes()
    for x in range(0, buffer.size, Streamer.MAX_MSG_SIZE):
        start = x
        end = start + Streamer.MAX_MSG_SIZE

        if end > buffer.size:
            end = buffer.size

        send_buf = buffer_bytes[start:end]
        client_socket.sendto(send_buf, server_addr)


class Streamer:
    THREAD_SLEEP = 0.0005  # in seconds
    MAX_MSG_SIZE = 60000   # in bytes
    DIGIT_COUNT = 8
    FRAME_SIZE = (480, 320)

    def __init__(self, ip, port, camera_id, camera_name):
        self.ip = ip
        self.port = port
        self.camera_id = camera_id
        self.camera_name = camera_name

    def start(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_addr = (self.ip, self.port)

        print(f'streaming to --> {server_addr}')

        vs = VideoStream(src=self.camera_id).start()

        while True:
            frame = vs.read()

            add_description(frame, self.camera_name)

            frame = cv2.resize(frame, Streamer.FRAME_SIZE)

            _, buffer = cv2.imencode('.jpg', frame)

            send_frame(client, server_addr, buffer)

            sleep(Streamer.THREAD_SLEEP)
