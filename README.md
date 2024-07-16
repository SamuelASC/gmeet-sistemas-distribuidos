Claro! Aqui está o README traduzido para o português:

---

# Aplicação de Videoconferência

Esta é uma aplicação de videoconferência que simula um ambiente semelhante ao Google Meet para comunicação local entre usuários. A aplicação suporta funcionalidades de vídeo, áudio e chat de texto.

## Autores

- Samuel Abel Said Corrêa (RA: 800209)
- Juliano Eleno Silva Pádua (RA: 800812)
- Anderson Antônio de Melo (RA: 795231)

## Funcionalidades

- Transmissão de vídeo
- Transmissão de áudio
- Chat de texto
- Interface gráfica para interação do usuário
- Alternar vídeo e áudio
- Funcionalidade de sair

## Pré-requisitos

- Python 3.x

## Bibliotecas Necessárias

Certifique-se de ter as seguintes bibliotecas instaladas:

```bash
pip install pyzmq opencv-python numpy pyaudio
```

## Como Executar

1. Clone o repositório ou faça o download do código-fonte.
2. Navegue até o diretório contendo o código-fonte.
3. Execute a aplicação com o seguinte comando:

```bash
python main.py -node <IP_ADDRESS_1> -node <IP_ADDRESS_2> ...
```

Substitua  `<IP_ADDRESS_1>`, `<IP_ADDRESS_2>`, etc., pelos endereços IP dos nós que você deseja conectar.

Exemplo:

```bash
python video_conference.py -node 192.168.0.2 -node 192.168.0.3
```

## Uso

- **Chat de Texto:** Digite sua mensagem na caixa de entrada e pressione Enter ou clique no botão "Enviar".
- **Alternar Vídeo:** Clique no botão "Desligar Vídeo" para desligar o vídeo. O texto do botão mudará para "Ligar Vídeo" quando o vídeo estiver desligado.
- **Alternar Áudio:** Clique no botão "Desligar Áudio" para desligar o áudio. O texto do botão mudará para "Ligar Áudio" quando o áudio estiver desligado.
- **Sair:** Clique no botão "Sair" para sair da aplicação.

## Visão Geral do Código

- `pub_text`: Publica mensagens de texto.
- `sub_text`: Inscreve-se para receber mensagens de texto.
- `pub_video`: Publica quadros de vídeo.
- `sub_video`: Inscreve-se para receber quadros de vídeo.
- `pub_audio`: Publica dados de áudio.
- `sub_audio`: Inscreve-se para receber dados de áudio.
- `start_gui`: Inicializa e inicia a interface gráfica do usuário.

## Licença

Este projeto é licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## Agradecimentos

Este projeto utiliza as seguintes bibliotecas:
- ZeroMQ para mensagens
- OpenCV para processamento de vídeo
- PyAudio para processamento de áudio
- Tkinter para a interface gráfica do usuário

---

Você pode copiar e colar este texto em um arquivo `README.md` no diretório do seu projeto.
