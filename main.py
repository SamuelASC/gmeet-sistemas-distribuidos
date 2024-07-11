import tkinter as tk
from tkinter import scrolledtext
import zmq
import threading
import time
import cv2
import pyaudio
import numpy as np

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
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Google Meet")
        
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

    def send_message(self):
        self.chat_box.insert(tk.END, f"Você: {message}\n")
        message = self.chat_entry.get()
        # self.chat_box.insert(tk.END, f"Você: {message}\n")
        self.chat_entry.delete(0, tk.END)
        # Aqui você pode enviar a mensagem via ZeroMQ

    def stop(self):
        self.video_stream.stop()
        self.voice_stream.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()
