import zmq

def main():
    context = zmq.Context()

    # Configuração do socket PUB para audio
    audio_socket = context.socket(zmq.PUB)
    audio_socket.bind("tcp://*:5555")

    # Configuração do socket PUB para voz
    voice_socket = context.socket(zmq.PUB)
    voice_socket.bind("tcp://*:5556")

    # Configuração do socket PUB para texto
    text_socket = context.socket(zmq.PUB)
    text_socket.bind("tcp://*:5557")

    print("Broker iniciado e aguardando mensagens...")

    try:
        while True:
            #TO DO:  Adicionar lógica para receber mensagens e redirecioná-las
            # por exemplo, através de sockets específicos de entrada para áudio, voz e texto
            pass
    except KeyboardInterrupt:
        print("Broker encerrado.")

if __name__ == "__main__":
    main()
