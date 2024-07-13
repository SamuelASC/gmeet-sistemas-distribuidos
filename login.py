import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
import zmq
import socket
import base64
import cv2
import numpy as np
import pyaudio

# Usuários pré-criados
USERS = {
    "user1": "password1",
    "user2": "password2"
}

# Portas para comunicação
text_port = 6000
video_port = 6001
audio_port = 6002

EXIT = 0

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    return local_ip

def quit_socket(socket):
    topic = "quit-" + get_local_ip()
    to_send = b"%s %s" % (topic.encode(), b"Nothing")
    socket.send(to_send)

class ChatApp:
    def __init__(self, root, username):
        self.root = root
        self.root.title(f"Simulador Google Meet - {username}")

        self.mainframe = ttk.Frame(root, padding="10")
        self.mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.video_label = tk.Label(self.mainframe, bg="black")
        self.video_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.chat_box = tk.Text(self.mainframe, width=50, height=10, state='disabled')
        self.chat_box.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.chat_entry = ttk.Entry(self.mainframe, width=50)
        self.chat_entry.grid(row=2, column=0, padx=5, pady=5)

        self.send_button = ttk.Button(self.mainframe, text="Enviar", command=self.send_message)
        self.send_button.grid(row=2, column=1, padx=5, pady=5)

        self.context = zmq.Context()
        self.chat_pub = self.context.socket(zmq.PUB)
        self.chat_pub.bind("tcp://*:%s" % text_port)
        self.chat_sub = self.context.socket(zmq.SUB)
        self.chat_sub.setsockopt_string(zmq.SUBSCRIBE, "*")

        self.nodes = ["127.0.0.1"]
        self.init_video_audio_streams()
        
        self.thread_chat_sub = threading.Thread(target=self.receive_messages)
        self.thread_chat_sub.start()
        
        self.thread_video_sub = threading.Thread(target=self.sub_video)
        self.thread_video_sub.start()
        
        self.thread_audio_sub = threading.Thread(target=self.sub_audio)
        self.thread_audio_sub.start()

        self.video_stream = cv2.VideoCapture(0)
        self.audio_stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )
        
        self.video_running = True
        self.audio_running = True

        self.thread_video_pub = threading.Thread(target=self.pub_video)
        self.thread_video_pub.start()
        
        self.thread_audio_pub = threading.Thread(target=self.pub_audio)
        self.thread_audio_pub.start()

    def init_video_audio_streams(self):
        for ip in self.nodes:
            self.chat_sub.connect("tcp://%s:%s" % (ip, text_port))
            self.chat_sub.setsockopt_string(zmq.SUBSCRIBE, "*")
            
            self.chat_sub.connect("tcp://%s:%d" % (ip, video_port))
            self.chat_sub.setsockopt_string(zmq.SUBSCRIBE, "*")
            
            self.chat_sub.connect("tcp://%s:%s" % (ip, audio_port))
            self.chat_sub.setsockopt_string(zmq.SUBSCRIBE, "*")

    def send_message(self):
        message = self.chat_entry.get()
        self.chat_box.config(state='normal')
        self.chat_box.insert(tk.END, f"Você: {message}\n")
        self.chat_box.config(state='disabled')
        self.chat_entry.delete(0, tk.END)
        self.chat_pub.send(b"%s %s" % (f"*{get_local_ip()}".encode(), message.encode()))

    def receive_messages(self):
        while not EXIT:
            message = self.chat_sub.recv()
            try:
                topic, messagedata = message.split(b" ", 1)
                if topic.decode().startswith("quit"):
                    continue
                self.chat_box.config(state='normal')
                self.chat_box.insert(tk.END, f"{topic.decode()}: {messagedata.decode(errors='ignore')}\n")
                self.chat_box.config(state='disabled')
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")

    def pub_video(self):
        socket = self.context.socket(zmq.PUB)
        socket.bind("tcp://*:%d" % video_port)
        while self.video_running:
            ret, frame = self.video_stream.read()
            frame = cv2.resize(frame, (320, 240))
            encoded, buffer = cv2.imencode(".jpg", frame)
            to_send = b"%s " % f"*{get_local_ip()}".encode()
            buffer_encoded = base64.b64encode(buffer)
            to_send += buffer_encoded
            socket.send(to_send)
            cv2.imshow("Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.video_running = False
                quit_socket(socket)
                break
        socket.close()
        cv2.destroyWindow("Webcam")

    def sub_video(self):
        socket = self.context.socket(zmq.SUB)
        for ip in self.nodes:
            socket.connect("tcp://%s:%d" % (ip, video_port))
            socket.setsockopt_string(zmq.SUBSCRIBE, f"*{ip}")
            socket.setsockopt_string(zmq.SUBSCRIBE, f"quit-{ip}")
        while not EXIT:
            message = socket.recv()
            try:
                topic, frame_encoded = message.split()
                if topic.decode().startswith("quit"):
                    cv2.destroyWindow(topic.decode().split("-")[1])
                    continue
                img = base64.b64decode(frame_encoded)
                npimg = np.frombuffer(img, dtype=np.uint8)
                frame = cv2.imdecode(npimg, 1)
                cv2.imshow(topic.decode()[1:], frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            except Exception as e:
                print(f"Erro ao processar vídeo: {e}")
        socket.close()

    def pub_audio(self):
        socket = self.context.socket(zmq.PUB)
        socket.bind("tcp://*:%d" % audio_port)
        while self.audio_running:
            data = self.audio_stream.read(1024)
            socket.send(b"%s %s" % (b"*", data))
        quit_socket(socket)
        socket.close()

    def sub_audio(self):
        socket = self.context.socket(zmq.SUB)
        for ip in self.nodes:
            socket.connect("tcp://%s:%d" % (ip, audio_port))
            socket.setsockopt_string(zmq.SUBSCRIBE, f"*")
            socket.setsockopt_string(zmq.SUBSCRIBE, f"quit-{ip}")
        audio = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            output=True,
            frames_per_buffer=1024,
        )
        while not EXIT:
            message = socket.recv()
            try:
                topic, data = message.split(b" ", 1)
                if topic.decode().startswith("quit"):
                    continue
                audio.write(data)
            except Exception as e:
                print(f"Erro ao processar áudio: {e}")
        socket.close()

    def stop(self):
        global EXIT
        EXIT = 1
        self.video_running = False
        self.audio_running = False
        self.video_stream.release()
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        cv2.destroyAllWindows()
        self.context.term()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.mainframe = ttk.Frame(root, padding="10")
        self.mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.label_user = ttk.Label(self.mainframe, text="Usuário")
        self.label_user.grid(row=0, column=0, padx=5, pady=5)

        self.entry_user = ttk.Entry(self.mainframe)
        self.entry_user.grid(row=0, column=1, padx=5, pady=5)

        self.label_password = ttk.Label(self.mainframe, text="Senha")
        self.label_password.grid(row=1, column=0, padx=5, pady=5)

        self.entry_password = ttk.Entry(self.mainframe, show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ttk.Button(self.mainframe, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.entry_user.get()
        password = self.entry_password.get()
        if username in USERS and USERS[username] == password:
            self.root.destroy()
            root = tk.Tk()
            app = ChatApp(root, username)
            root.protocol("WM_DELETE_WINDOW", app.stop)
            root.mainloop()
        else:
            messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
