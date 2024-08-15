import sys
import time
import cv2
import pyqtgraph as pg
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class BallWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ball_radius = 10
        self.ball_x = 190
        self.ball_y = 250
        self.setMinimumSize(200, 200)
        #top = 30
        #middle = 140
        #bottom = 250
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # leg peak = -80
        #mid = -200
        # Floor = -270
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #draw border
        
        border_thickness = 1
        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(0,2,0,250)
        painter.drawLine(0,250,375,250)
        painter.drawLine(375,250,375,2)
        painter.drawLine(375,2,0,2)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red color
        painter.drawEllipse(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, self.ball_radius * 2, self.ball_radius * 2)

    def update_ball_position(self, y):
        self.ball_y = ((-(44.0/91) * (y-40)) + 30)
        self.update()
