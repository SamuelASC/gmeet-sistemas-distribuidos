import tkinter as tk
from tkinter import ttk
import zmq
import threading
import pyaudio
import cv2
import base64
import numpy as np
import sys
import time
from PIL import Image, ImageTk

# Definição das portas base
text_port_base = 6000
video_port_base = 6001
audio_port_base = 6002

EXIT = False

class ChatApp:
    def __init__(self, root, username, nodes, text_port, video_port, audio_port):
        self.root = root
        self.username = username
        self.nodes = nodes
        self.context = zmq.Context()
        self.text_port = text_port
        self.video_port = video_port
        self.audio_port = audio_port

        self.camera_enabled = True
        self.audio_enabled = True

        self.root.title(f"Chat - {self.username}")
        self.root.geometry("800x600")
        self.root.configure(bg="#202124")

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para as câmeras
        self.camera_frame = ttk.Frame(self.main_frame)
        self.camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas para exibir a câmera local
        self.local_camera_canvas = tk.Canvas(self.camera_frame, width=320, height=240, bg="#000000")
        self.local_camera_canvas.pack(side=tk.TOP, padx=10, pady=10)

        # Canvas para exibir a câmera remota
        self.remote_camera_canvas = tk.Canvas(self.camera_frame, width=320, height=240, bg="#000000")
        self.remote_camera_canvas.pack(side=tk.TOP, padx=10, pady=10)

        # Frame para o chat e os botões
        self.chat_control_frame = ttk.Frame(self.main_frame)
        self.chat_control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.chat_frame = ttk.Frame(self.chat_control_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_box = tk.Text(self.chat_frame, wrap=tk.WORD, bg="#202124", fg="#ffffff")
        self.chat_box.pack(fill=tk.BOTH, expand=True)

        self.entry_frame = ttk.Frame(self.chat_control_frame)
        self.entry_frame.pack(fill=tk.X)

        self.message_entry = ttk.Entry(self.entry_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        self.create_control_buttons()

        self.setup_zmq()
        self.start_threads()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        global EXIT
        EXIT = True
        self.root.destroy()

    def setup_zmq(self):
        self.pub_socket = self.context.socket(zmq.PUB)
        self.bind_socket(self.pub_socket, self.text_port)
        print(f"ZMQ Publisher socket bound to port {self.text_port}")

    def bind_socket(self, socket, port):
        while True:
            try:
                socket.bind(f"tcp://*:{port}")
                break
            except zmq.ZMQError as e:
                if e.errno == zmq.EADDRINUSE:
                    print(f"A porta {port} está em uso. Tentando próxima porta.")
                    port += 1
                    time.sleep(1)
                else:
                    raise

    def start_threads(self):
        self.sub_thread = threading.Thread(target=self.sub_text)
        self.sub_thread.start()
        print("Text subscription thread started")

        self.pub_video_thread = threading.Thread(target=self.pub_video)
        self.pub_video_thread.start()
        print("Video publication thread started")

        self.sub_video_thread = threading.Thread(target=self.sub_video)
        self.sub_video_thread.start()
        print("Video subscription thread started")

        self.pub_audio_thread = threading.Thread(target=self.pub_audio)
        self.pub_audio_thread.start()
        print("Audio publication thread started")

        self.sub_audio_thread = threading.Thread(target=self.sub_audio)
        self.sub_audio_thread.start()
        print("Audio subscription thread started")

    def create_control_buttons(self):
        control_frame = ttk.Frame(self.chat_control_frame)
        control_frame.pack(fill=tk.X)

        self.camera_button = ttk.Button(control_frame, text="Disable Camera", command=self.toggle_camera)
        self.camera_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.audio_button = ttk.Button(control_frame, text="Disable Audio", command=self.toggle_audio)
        self.audio_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.end_call_button = ttk.Button(control_frame, text="End Call", command=self.on_close)
        self.end_call_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def toggle_camera(self):
        self.camera_enabled = not self.camera_enabled
        self.camera_button.configure(text="Disable Camera" if self.camera_enabled else "Enable Camera")

    def toggle_audio(self):
        self.audio_enabled = not self.audio_enabled
        self.audio_button.configure(text="Disable Audio" if self.audio_enabled else "Enable Audio")

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            self.message_entry.delete(0, tk.END)
            topic = f"*{self.username}"
            self.pub_socket.send_string(f"{topic} {message}")
            self.chat_box.insert(tk.END, f"{self.username}: {message}\n")

    def sub_text(self):
        socket = self.context.socket(zmq.SUB)
        for ip in self.nodes:
            socket.connect(f"tcp://{ip}:{self.text_port}")
            socket.setsockopt_string(zmq.SUBSCRIBE, "*")
            socket.setsockopt_string(zmq.SUBSCRIBE, f"quit-{ip}")

        while not EXIT:
            try:
                message = socket.recv()
                topic, messagedata = message.split(b" ", 1)
                if topic.decode().startswith("quit"):
                    continue
                self.chat_box.insert(tk.END, f"{topic.decode()}: {messagedata.decode()}\n")
            except zmq.error.ZMQError as e:
                print(f"ZMQ Error in sub_text: {e}")
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
        socket.close()
        print("Saindo sub_text")

    def pub_video(self):
        socket = self.context.socket(zmq.PUB)
        self.bind_socket(socket, self.video_port)
        print(f"Video publisher socket bound to port {self.video_port}")

        camera = cv2.VideoCapture(0)
        while not EXIT:
            if self.camera_enabled:
                try:
                    ret, frame = camera.read()
                    if not ret:
                        break
                    frame = cv2.resize(frame, (320, 240))
                    _, buffer = cv2.imencode('.jpg', frame)
                    topic = f"*{self.username}"
                    socket.send(topic.encode() + b" " + base64.b64encode(buffer))
                    self.update_local_camera(frame)
                except Exception as e:
                    print(f"Error in pub_video: {e}")
        camera.release()
        socket.close()
        print("Saindo pub_video")

    def update_local_camera(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.local_camera_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.local_camera_canvas.image = imgtk

    def sub_video(self):
        socket = self.context.socket(zmq.SUB)
        for ip in self.nodes:
            socket.connect(f"tcp://{ip}:{self.video_port}")
            socket.setsockopt_string(zmq.SUBSCRIBE, "*")
            socket.setsockopt_string(zmq.SUBSCRIBE, f"quit-{ip}")

        while not EXIT:
            try:
                message = socket.recv()
                topic, frame_encoded = message.split(b" ", 1)
                if topic.decode().startswith("quit"):
                    continue
                frame = base64.b64decode(frame_encoded)
                np_frame = np.frombuffer(frame, dtype=np.uint8)
                img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
                self.update_remote_camera(img)
            except zmq.error.ZMQError as e:
                print(f"ZMQ Error in sub_video: {e}")
            except Exception as e:
                print(f"Erro ao processar vídeo: {e}")
        socket.close()
        print("Saindo sub_video")

    def update_remote_camera(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.remote_camera_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.remote_camera_canvas.image = imgtk

    def pub_audio(self):
        socket = self.context.socket(zmq.PUB)
        self.bind_socket(socket, self.audio_port)
        print(f"Audio publisher socket bound to port {self.audio_port}")

        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

        while not EXIT:
            if self.audio_enabled:
                try:
                    data = stream.read(1024)
                    socket.send(b"*" + data)
                except Exception as e:
                    print(f"Error in pub_audio: {e}")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        socket.close()
        print("Saindo pub_audio")

    def sub_audio(self):
        socket = self.context.socket(zmq.SUB)
        for ip in self.nodes:
            socket.connect(f"tcp://{ip}:{self.audio_port}")
            socket.setsockopt_string(zmq.SUBSCRIBE, "*")
            socket.setsockopt_string(zmq.SUBSCRIBE, f"quit-{ip}")

        p = pyaudio.PyAudio()
        audio = p
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            output=True,
            frames_per_buffer=1024,
        )

        while not EXIT:
            try:
                message = socket.recv()
                topic, data = message.split(b" ", 1)
                if topic.decode().startswith("quit"):
                    continue
                stream.write(data)
            except zmq.error.ZMQError as e:
                print(f"ZMQ Error in sub_audio: {e}")
            except Exception as e:
                print(f"Erro ao processar áudio: {e}")
        stream.stop_stream()
        stream.close()
        p.terminate()
        socket.close()
        print("Saindo sub_audio")

def login():
    global login_window
    username = username_entry.get()
    password = password_entry.get()

    if username in users and users[username] == password:
        login_window.destroy()
        text_port, video_port, audio_port = get_available_ports()
        root = tk.Tk()
        app = ChatApp(root, username, nodes, text_port, video_port, audio_port)
    else:
        error_label.config(text="Invalid username or password")

def get_available_ports():
    global text_port_base, video_port_base, audio_port_base
    text_port = text_port_base
    video_port = video_port_base
    audio_port = audio_port_base
    text_port_base += 3
    video_port_base += 3
    audio_port_base += 3
    return text_port, video_port, audio_port

users = {
    "user1": "password1",
    "user2": "password2",
}

if __name__ == "__main__":
    nodes = sys.argv[2:] if len(sys.argv) > 2 else []

    login_window = tk.Tk()
    login_window.title("Login")

    tk.Label(login_window, text="Username").pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    tk.Label(login_window, text="Password").pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    error_label = tk.Label(login_window, text="", fg="red")
    error_label.pack()

    login_button = tk.Button(login_window, text="Login", command=login)
    login_button.pack()

    login_window.mainloop()
