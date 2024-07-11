import zmq
import time

def main():
    context = zmq.Context()
    audio_socket = context.socket(zmq.PUB)
    audio_socket.connect("tcp://localhost:5555")

    while True:
        # Enviando a mensagem como bytes codificados em UTF-8
        audio_socket.send("Mensagem de áudio".encode('utf-8'))
        print("Mensagem de áudio enviada")
        time.sleep(1)

if __name__ == "__main__":
    main()
