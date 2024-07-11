import zmq
import time

def main():
    context = zmq.Context()
    text_socket = context.socket(zmq.PUB)
    text_socket.connect("tcp://localhost:5557")

    while True:
        text_socket.send_string("Mensagem de texto")
        print("Mensagem de texto enviada")
        time.sleep(1)

if __name__ == "__main__":
    main()
