import tkinter as tk
from tkinter import messagebox, scrolledtext
import zmq
import threading
import time
import cv2
import pyaudio
import numpy as np

# Usuários pré-criados
USERS = {
    "user1": "password1",
    "user2": "password2"
}

class VideoStream:
    def __init__(self, label):
        self.label = label
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.thread = threading.Thread(target=self.update)
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = np.array(frame)
                img = cv2.resize(img, (640, 480))
                img = np.flip(img, axis=1)
                self.photo = tk.PhotoImage(master=self.label, image=tk.PhotoImage.fromarray(img))
                self.label.config(image=self.photo)
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.cap.release()
        self.thread.join()

class VoiceStream:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        self.running = True
        self.thread = threading.Thread(target=self.update)
        self.thread.start()

    def update(self):
        while self.running:
            data = self.stream.read(1024)
            # Aqui você pode enviar os dados de áudio via ZeroMQ

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.thread.join()

class ChatApp:
    def __init__(self, root, username):
        self.root = root
        self.root.title(f"Simulador Google Meet - {username}")
        
        self.video_label = tk.Label(root)
        self.video_label.pack()

        self.chat_box = scrolledtext.ScrolledText(root, width=50, height=10)
        self.chat_box.pack()
        
        self.chat_entry = tk.Entry(root, width=50)
        self.chat_entry.pack()
        
        self.send_button = tk.Button(root, text="Enviar", command=self.send_message)
        self.send_button.pack()

        self.video_stream = VideoStream(self.video_label)
        self.voice_stream = VoiceStream()

        self.context = zmq.Context()
        self.chat_pub = self.context.socket(zmq.PUB)
        self.chat_pub.connect("tcp://localhost:5557")
        self.chat_sub = self.context.socket(zmq.SUB)
        self.chat_sub.connect("tcp://localhost:5557")
        self.chat_sub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.thread = threading.Thread(target=self.receive_messages)
        self.thread.start()

    def send_message(self):
        message = self.chat_entry.get()
        self.chat_box.insert(tk.END, f"Você: {message}\n")
        self.chat_entry.delete(0, tk.END)
        self.chat_pub.send_string(message)

    def receive_messages(self):
        while True:
            message = self.chat_sub.recv_string()
            self.chat_box.insert(tk.END, f"Outro: {message}\n")

    def stop(self):
        self.video_stream.stop()
        self.voice_stream.stop()
        self.context.term()
        self.thread.join()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        
        self.label_user = tk.Label(root, text="Usuário")
        self.label_user.pack()
        
        self.entry_user = tk.Entry(root)
        self.entry_user.pack()
        
        self.label_password = tk.Label(root, text="Senha")
        self.label_password.pack()
        
        self.entry_password = tk.Entry(root, show="*")
        self.entry_password.pack()
        
        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        user = self.entry_user.get()
        password = self.entry_password.get()
        
        if user in USERS and USERS[user] == password:
            self.root.destroy()
            main_app(user)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos")

def main_app(username):
    root = tk.Tk()
    app = ChatApp(root, username)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
