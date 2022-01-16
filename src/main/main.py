import time

import cv2
import zmq
import yaml
import logging
import multiprocessing

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


def load_config(config_file_path):
    try:
        with open(config_file_path, 'r') as file:
            configuration = yaml.safe_load(file)

    except IOError as e:
        logging.error(f"Exception encountered, {e}")

    return configuration


def read_from_camera(cam_id, q):
    capture = cv2.VideoCapture(cam_id)

    while True:
        start_time = time.time()
        _, frame = capture.read()

        q.put(frame)

        # sleep(Streamer.THREAD_SLEEP)
        print("--- %s seconds ---" % (time.time() - start_time))


def process_frame(q):
    while True:
        frame = q.get()
        # Display the resulting frame
        cv2.imshow('Frame', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        # _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        # socket.send(buffer)


if __name__ == '__main__':
    config = load_config("C:/Users/meti-nati/PycharmProjects/HomeSecuritySource/src/resources/application.yml")
    ip = config.get('ip')
    port = config.get('port')
    camId = config.get('camera-id')

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{ip}:{port}")

    print(f"Streaming to --> {ip}:{port}")

    q = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=read_from_camera, args=(camId, q))

    p1.start()

    p1.join()


