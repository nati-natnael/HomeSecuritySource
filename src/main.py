import argparse

from streamer import Streamer

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stream video source")

    parser.add_argument("-i", "--ip", help="ip address", default="127.0.0.1")
    parser.add_argument("-p", "--port", help="port number", type=int, default=8080)
    parser.add_argument("-c", "--camera", help="camera id", type=int, default=0)

    args = parser.parse_args()

    streamer = Streamer(args.ip, args.port, args.camera)
    streamer.start()
