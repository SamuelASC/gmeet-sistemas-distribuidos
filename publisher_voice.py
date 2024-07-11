import zmq
import time

def main():
    context = zmq.Context()
    voice_socket = context.socket(zmq.PUB)
    voice_socket.connect("tcp://localhost:5556")

    while True:
        voice_socket.send(b"Mensagem de voz")
        print("Mensagem de voz enviada")
        time.sleep(1)

if __name__ == "__main__":
    main()
