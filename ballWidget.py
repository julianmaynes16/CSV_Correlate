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
    # Ball size
        self.ball_radius = 10
    # Ball location
        self.ball_x = 200
        self.ball_y = 200
        self.setMinimumSize(200, 200)
        #top = 10
        #middle = 200
        #bottom = 380
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # leg peak = -80
        #mid = -200
        # Floor = -270
# Draw ball
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red color
        painter.drawEllipse(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, self.ball_radius * 2, self.ball_radius * 2)
# Update ball position
    def update_ball_position(self, y):
        self.ball_y = (0.0036 * pow(float(y), 2) + 13)
        self.update()
