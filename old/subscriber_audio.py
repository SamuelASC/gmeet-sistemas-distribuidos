import zmq

def main():
    context = zmq.Context()
    audio_socket = context.socket(zmq.SUB)
    audio_socket.connect("tcp://localhost:5555")
    audio_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        message = audio_socket.recv()
        print(f"Recebido áudio: {message}")

if __name__ == "__main__":
    main()
