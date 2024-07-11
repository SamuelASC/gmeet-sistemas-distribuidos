import zmq
import time

def main():
    context = zmq.Context()
    sender_socket = context.socket(zmq.PUSH)
    sender_socket.connect("tcp://localhost:5558")

    while True:
        # Enviando a mensagem como bytes codificados em UTF-8
        message = [b"voice", "Mensagem de voz".encode('utf-8')]
        sender_socket.send_multipart(message)
        print("Mensagem de voz enviada")
        time.sleep(1)

if __name__ == "__main__":
    main()
