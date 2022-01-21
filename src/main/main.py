import cv2
import zmq
import yaml
import time
import logging
import threading

from time import sleep
from queue import Queue
from datetime import datetime

logging.basicConfig(format="%(asctime)s %(threadName)-9s [%(levelname)s] - %(message)s", level=logging.DEBUG)


queue = Queue(maxsize=20)


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


def read_from_camera(cam_id):
    capture = cv2.VideoCapture(cam_id)

    while True:
        # start_time = time.time()
        _, _frame = capture.read()

        # # Display the resulting frame
        # cv2.imshow('Read Frame', frame)
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     breakd

        queue.put(_frame)

        # sleep(Streamer.THREAD_SLEEP)
        # print("--- Read Frame: %s seconds ---" % (time.time() - start_time))

        # sleep(0.0005)


if __name__ == '__main__':
    config = load_config("C:/Users/meti-nati/PycharmProjects/HomeSecuritySource/src/resources/application.yml")
    ip = config.get('ip')
    port = config.get('port')
    camId = config.get('camera_id')
    camName = config.get('camera_name')

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{ip}:{port}")

    print(f"Streaming to --> {ip}:{port}")

    t1 = threading.Thread(target=read_from_camera, args=(camId, ))
    t1.start()

    while True:
        start_time = time.time()
        size = 0

        if not queue.empty():
            size = queue.qsize()

            vid_frame = queue.get()

            add_datetime_to(vid_frame)
            add_name(vid_frame, camName)

            _, buffer = cv2.imencode('.jpg', vid_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            socket.send(buffer)

            # # Display the resulting frame
            # cv2.imshow('Process Frame', frame)
            # if cv2.waitKey(25) & 0xFF == ord('q'):
            #     break

        print(f"--- Process Frame: Queue Size: {size}: {(time.time() - start_time)} seconds ---")

        sleep(0.0005)


