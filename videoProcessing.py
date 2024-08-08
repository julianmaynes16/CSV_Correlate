import os
import pandas as pd
import csv
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import cv2
import time


class VideoThread(QThread):
    change_pixmap_signal = Signal(QPixmap)

    def __init__(self, video_file, input_frame, seconds_before_loop):
        super().__init__()
        self._run_flag = True
        self.input_frame = input_frame
        self.cap = cv2.VideoCapture(video_file)
        self.cap.set(1, input_frame)
        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        self.seconds_before_loop = seconds_before_loop
        self.loop_begin = time.time()
        self.thirtyfps_begin = time.time()

    def run(self):
        while self._run_flag:
            if (time.time() - self.loop_begin) > self.seconds_before_loop:
                self.cap.set(1, self.input_frame)
                self.loop_begin = time.time()
            if(time.time() - self.thirtyfps_begin) > (1/self.frame_rate):
                self.thirtyfps_begin = time.time()
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height, width, channel = frame.shape
                    img = QImage(frame, width, height, QImage.Format_RGB888)
                    pix = QPixmap.fromImage(img)
                    self.change_pixmap_signal.emit(pix)
            

    def stop(self):
        self._run_flag = False
        self.wait()