import cv2
import zmq
import yaml
import time
import logging

from time import sleep
from datetime import datetime
from imutils.video import VideoStream

logging.basicConfig(format="%(asctime)s %(threadName)-9s [%(levelname)s] - %(message)s", level=logging.DEBUG)


def add_name(frame, name):
    cv2.putText(frame, name, org=(10, 30),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)


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

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{ip}:{port}")

    logging.info(f"Streaming to --> {ip}:{port}")

    vs = VideoStream(src=0).start()

    while True:
        start_time = time.time()

        vid_frame = vs.read()

        add_datetime_to(vid_frame)
        add_name(vid_frame, camName)

        _, buffer = cv2.imencode('.jpg', vid_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])

        socket.send(buffer)

        # # Display the resulting frame
        # cv2.imshow('Process Frame', vid_frame)
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     break

        logging.info(f"Process Frame: {(time.time() - start_time)} seconds")

        sleep(0.0005)


