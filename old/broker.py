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

    # Configuração do socket PULL para receber mensagens de publicadores
    receiver_socket = context.socket(zmq.PULL)
    receiver_socket.bind("tcp://*:5558")

    print("Broker iniciado e aguardando mensagens...")

    try:
        while True:
            # Recebe mensagem do socket PULL
            message = receiver_socket.recv_multipart()

            # Espera que a mensagem seja um par (tipo, conteúdo)
            message_type = message[0].decode('utf-8')
            content = message[1]

            # Redireciona a mensagem para o socket PUB apropriado
            if message_type == "audio":
                audio_socket.send(content)
                print("Áudio redirecionado")
            elif message_type == "voice":
                voice_socket.send(content)
                print("Voz redirecionada")
            elif message_type == "text":
                text_socket.send(content)
                print("Texto redirecionado")
    except KeyboardInterrupt:
        print("Broker encerrado.")

if __name__ == "__main__":
    main()
