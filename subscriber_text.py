import zmq

def main():
    context = zmq.Context()
    text_socket = context.socket(zmq.SUB)
    text_socket.connect("tcp://localhost:5557")
    text_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        message = text_socket.recv_string()
        print(f"Recebido texto: {message}")

if __name__ == "__main__":
    main()
