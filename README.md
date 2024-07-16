## README.md

# Video Conferencing Application

This is a video conferencing application that simulates a Google Meet-like environment for local communication between two or more users. The application supports video, audio, and text chat functionalities.

## Authors

- Samuel Abel Said Corrêa (RA: 800209)
- Juliano Eleno Silva Pádua (RA: 800812)
- Anderson Antônio de Melo (RA: 795231)

## Features

- Video streaming
- Audio streaming
- Text chat
- GUI for user interaction
- Toggle video and audio
- Exit functionality

## Prerequisites

- Python 3.x

## Required Libraries

Ensure you have the following libraries installed:

```bash
pip install pyzmq opencv-python numpy pyaudio
```

## How to Run

1. Clone the repository or download the source code.
2. Navigate to the directory containing the source code.
3. Run the application with the following command:

```bash
python <script_name>.py -node <IP_ADDRESS_1> -node <IP_ADDRESS_2> ...
```

Replace `<script_name>` with the name of the Python script and `<IP_ADDRESS_1>`, `<IP_ADDRESS_2>`, etc., with the IP addresses of the nodes you want to connect.

Example:

```bash
python video_conference.py -node 192.168.0.2 -node 192.168.0.3
```

## Usage

- **Text Chat:** Type your message in the input box and press Enter or click the "Enviar" button.
- **Toggle Video:** Click the "Desligar Vídeo" button to turn off the video. The button text will change to "Ligar Vídeo" when the video is off.
- **Toggle Audio:** Click the "Desligar Áudio" button to turn off the audio. The button text will change to "Ligar Áudio" when the audio is off.
- **Exit:** Click the "Sair" button to exit the application.

## Code Overview

- `pub_text`: Publishes text messages.
- `sub_text`: Subscribes to text messages.
- `pub_video`: Publishes video frames.
- `sub_video`: Subscribes to video frames.
- `pub_audio`: Publishes audio data.
- `sub_audio`: Subscribes to audio data.
- `start_gui`: Initializes and starts the GUI.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project uses the following libraries:
- ZeroMQ for messaging
- OpenCV for video processing
- PyAudio for audio processing
- Tkinter for the graphical user interface