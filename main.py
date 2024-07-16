#Grupo 1
#Nome e RA dos participantes:
#Samuel Abel said Corrêa 800209
#Juliano Eleno Silva Pádua 800812
#Anderson Antônio de Melo 795231

import sys
import zmq
import time
import threading
import cv2
import base64
import numpy as np
import socket
import pyaudio
import tkinter as tk

text_port = 1000
video_port = 1001
audio_port = 1002

EXIT = 0

message_history = []

RECEIVE_SLEEP_TIME = 0.01

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    return local_ip

def quit_socket(socket):
    topic = "quit-" + get_local_ip()
    to_send = b"%s %s" % (topic.encode(), b"Nothing")
    socket.send(to_send)

def pub_text(port_pub, zmq_context, chat_input):
    socket = zmq_context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port_pub)

    topic = "*" + get_local_ip()
    while True:
        message = chat_input.get()
        if message == "#quit":
            quit_socket(socket)
            global EXIT
            EXIT = 1
            break
        socket.send(b"%s %s" % (topic.encode(), message.encode()))
        chat_input.set("")

    socket.close()

def sub_text(ips_to_connect, zmq_context, chat_box):
    socket = zmq_context.socket(zmq.SUB)
    for ip in ips_to_connect:
        socket.connect("tcp://%s:%s" % (ip, int(text_port)))
        socket.subscribe("*" + ip)
        socket.subscribe("quit-" + ip)

    while True:
        try:
            string = socket.recv(flags=zmq.NOBLOCK)
            topic, messagedata = string.split(b" ", 1)

            if topic.decode().startswith("quit"):
                ip_user_quitting = topic.decode().split("-")[1]
                message = "Usuário %s saiu do canal de texto.\n" % (ip_user_quitting)
                chat_box.insert(tk.END, message)
                chat_box.yview(tk.END)
                if EXIT:
                    break
                continue

            message = "%s: %s\n" % (topic.decode(), messagedata.decode())
            message_history.append(message)
            chat_box.insert(tk.END, message)
            chat_box.yview(tk.END)

        except zmq.Again:
            pass

        time.sleep(RECEIVE_SLEEP_TIME)

    socket.close()

def pub_video(port_pub, zmq_context, video_flag):
    socket = zmq_context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port_pub)

    camera = cv2.VideoCapture(0)
    quitting_key_q = 0

    while not EXIT:
        if video_flag[0]:
            (grabbed, frame) = camera.read()
            frame = cv2.resize(frame, (320, 240))
            encoded, buffer = cv2.imencode(".jpg", frame)

            topic = "*" + get_local_ip()

            to_send = b"%s " % (topic.encode())
            buffer_encoded = base64.b64encode(buffer)
            to_send += buffer_encoded
            socket.send(to_send)

            cv2.imshow("Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                quitting_key_q = 1
                quit_socket(socket)
                break

    camera.release()
    
    if not quitting_key_q:
        quit_socket(socket)

    cv2.destroyWindow("Webcam")
    socket.close()

def sub_video(ips_to_connect, zmq_context):
    socket = zmq_context.socket(zmq.SUB)
    for ip in ips_to_connect:
        socket.connect("tcp://%s:%d" % (ip, video_port))
        topic = "*" + ip
        socket.subscribe(topic)
        quit_topic = "quit-" + ip
        socket.subscribe(quit_topic)

    while True:
        try:
            string = socket.recv(flags=zmq.NOBLOCK)
            topic, frame_encoded = string.split()

            if topic.decode().startswith("quit"):
                ip_user_quitting = topic.decode().split("-")[1]
                cv2.destroyWindow(ip_user_quitting)
                if EXIT:
                    break
                continue
            
            img = base64.b64decode(frame_encoded)
            npimg = np.frombuffer(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            
            cv2.imshow(str(topic.decode()[1:]), source)
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        except zmq.Again:
            pass

        time.sleep(RECEIVE_SLEEP_TIME)
    
    socket.close()

def pub_audio(port_pub, zmq_context, audio_flag):
    socket = zmq_context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port_pub)

    my_audio = pyaudio.PyAudio()
    sample_rate = 44100
    format = pyaudio.paInt16
    channels = 1
    frames_per_buffer = 1024

    stream = my_audio.open(
        format=format,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frames_per_buffer,
    )

    while not EXIT:
        if audio_flag[0]:
            data = stream.read(frames_per_buffer)
            to_send = b"%s %s" % (b"*", data)
            socket.send(to_send)

    quit_socket(socket)
    socket.close()

def sub_audio(ips_to_connect, zmq_context):
    socket = zmq_context.socket(zmq.SUB)
    for ip in ips_to_connect:
        socket.connect("tcp://%s:%s" % (ip, audio_port))
        socket.subscribe("quit-" + ip)

    socket.subscribe("*")

    my_audio = pyaudio.PyAudio()
    sample_rate = 44100
    format = pyaudio.paInt16
    channels = 1
    frames_per_buffer = 1024

    stream = my_audio.open(
        format=format,
        channels=channels,
        rate=sample_rate,
        output=True,
        frames_per_buffer=frames_per_buffer,
    )

    while True:
        try:
            string = socket.recv(flags=zmq.NOBLOCK)
            topic, data = string.split(b" ", 1)

            if topic.decode().startswith("quit"):
                ip_user_quitting = topic.decode().split("-")[1]
                if EXIT:
                    break
                continue

            stream.write(data)

        except zmq.Again:
            pass

        time.sleep(RECEIVE_SLEEP_TIME)
    
    socket.close()

def start_gui(nodes):
    global EXIT
    root = tk.Tk()
    root.title("Video conferencia")
    root.geometry("800x600")

    chat_frame = tk.Frame(root)
    chat_frame.pack(pady=10)

    chat_box = tk.Text(chat_frame, height=15, width=50)
    chat_box.pack(side=tk.LEFT, padx=10)

    scrollbar = tk.Scrollbar(chat_frame, command=chat_box.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_box['yscrollcommand'] = scrollbar.set

    chat_input = tk.StringVar()
    input_entry = tk.Entry(root, textvariable=chat_input, width=50)
    input_entry.pack(pady=10)

    video_flag = [True]
    audio_flag = [True]

    def send_message(event=None):
        message = chat_input.get()
        if message:
            chat_input.set("")
            message_text = "%s: %s\n" % (get_local_ip(), message)
            chat_box.insert(tk.END, message_text)
            chat_box.yview(tk.END)
            pub_text(text_port, context, chat_input)
        message_history.append(message_text)
    

    input_entry.bind("<Return>", send_message)
    send_m_button = tk.Button(root, text="Enviar", command=send_message)
    send_m_button.pack(pady=5)

    def toggle_video():
        video_flag[0] = not video_flag[0]
        video_button.config(text="Ligar Vídeo" if not video_flag[0] else "Desligar Vídeo")

    def toggle_audio():
        audio_flag[0] = not audio_flag[0]
        audio_button.config(text="Ligar Áudio" if not audio_flag[0] else "Desligar Áudio")

    video_button = tk.Button(root, text="Desligar Vídeo", command=toggle_video)
    video_button.pack(pady=5)

    audio_button = tk.Button(root, text="Desligar Áudio", command=toggle_audio)
    audio_button.pack(pady=5)

    def quit_program():
        global EXIT
        EXIT = 1
        root.destroy()

    quit_button = tk.Button(root, text="Sair", command=quit_program)
    quit_button.pack(pady=5)

    chat_box.insert(tk.END, "Bem-vindo ao chat!\n")

    for message in message_history:
        chat_box.insert(tk.END, message)
    chat_box.yview(tk.END)

    context = zmq.Context()

    thread_pub = threading.Thread(target=pub_text, args=(text_port, context, chat_input))
    thread_pub.start()

    thread_sub = threading.Thread(target=sub_text, args=(nodes, context, chat_box))
    thread_sub.start()

    thread_pub_video = threading.Thread(target=pub_video, args=(video_port, context, video_flag))
    thread_pub_video.start()

    thread_sub_video = threading.Thread(target=sub_video, args=(nodes, context))
    thread_sub_video.start()

    thread_pub_audio = threading.Thread(target=pub_audio, args=(audio_port, context, audio_flag))
    thread_pub_audio.start()
    time.sleep(1)

    thread_sub_audio = threading.Thread(target=sub_audio, args=(nodes, context))
    thread_sub_audio.start()

    root.mainloop()

if __name__ == "__main__":
    strArgv = ""
    for element in sys.argv[1:]:
        strArgv += str(element) + " "
    strArgv = strArgv.strip()

    nodes = strArgv.split("-node ")
    for i in range(1, len(nodes)):
        nodes[i] = nodes[i].strip()
    nodes = nodes[1:]

    start_gui(nodes)
