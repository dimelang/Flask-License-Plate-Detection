import cv2
import numpy as np
import time
from .proccess import preprocessing


class Video():
    def __init__(self, url):
        self.url = url
        # url = 'D:/Belajar/belajar-flask/app/uploads/IP Camera1_Nvr Penelitian_Nvr Penelitian_20191209071102_20191209071122_219588.mp4'
        self.cap = cv2.VideoCapture(url)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        while self.cap.isOpened():
            success, frame = self.cap.read()
            ori = frame
            if success:
                if any(f in str(self.url)for f in ['mp4', 'avi', '3gp']):
                    framePre, ori = preprocessing(frame)
                time.sleep(.03)
            return success, framePre, ori
