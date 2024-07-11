import zmq

def main():
    context = zmq.Context()
    voice_socket = context.socket(zmq.SUB)
    voice_socket.connect("tcp://localhost:5556")
    voice_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        message = voice_socket.recv()
        print(f"Recebido voz: {message}")

if __name__ == "__main__":
    main()
