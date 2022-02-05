import cv2
import yaml
import socket
import logging

from time import sleep
from datetime import datetime
from imutils.video import VideoStream

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


def load_config(config_file_path):
    try:
        with open(config_file_path, 'r') as file:
            configuration = yaml.safe_load(file)

    except IOError as e:
        logging.error(f"Exception encountered, {e}")

    return configuration


if __name__ == '__main__':
    config = load_config("C:/Users/meti-nati/PycharmProjects/HomeSecuritySource/src/resources/application.yml")
    ip = config.get('ip')
    port = config.get('port')
    camId = config.get('camera_id')
    camName = config.get('camera_name')

    socket_conn = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)

    logging.info(f"Streaming to --> {ip}:{port}")

    vs = VideoStream(src=0).start()

    while True:
        vid_frame = vs.read()

        vid_frame = cv2.resize(vid_frame, (640, 420))

        add_datetime_to(vid_frame)

        _, buffer = cv2.imencode('.jpg', vid_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

        try:
            socket_conn.sendto(buffer, (ip, port))
        except:
            continue

        sleep(0.0005)
