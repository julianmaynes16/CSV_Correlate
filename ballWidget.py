import sys
import time
import cv2
import pyqtgraph as pg
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class BallWidget(QWidget):
    #TODO FILL IN DOCSTRING
    """_summary_
    """
    def __init__(self, width, height, highest_height, lowest_height):
        super().__init__()
        self.ball_radius = 10
        self.ball_x = 50
        self.ball_y = 250
        self.setMinimumSize(200, 200)
        self.width = width
        self.height = height

        self.highest_height = highest_height
        self.lowest_height = lowest_height
        self.ball_top = 30
        self.ball_bottom = 250

        #top = 30
        #middle = 140
        #bottom = 250
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def paintEvent(self, event):
        #TODO FILL IN DOCSTRING
        """_summary_

        Args:
            event (_type_): _description_
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #draw border
        
        border_thickness = 1
        painter.setPen(QPen(Qt.white, 2))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red color
        painter.drawEllipse(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, self.ball_radius * 2, self.ball_radius * 2)


    def update_ball_position(self, y):
        #TODO FILL IN DOCSTRING
        """_summary_

        Args:
            y (_type_): _description_
        """
        #self.ball_y = (((-44000.0/93)* (y-0.04)) + 30) #TODO Replace MAGIC NUMBERS
        self.ball_y = ((self.ball_bottom - self.ball_top) / (self.lowest_height - self.highest_height)) * (y - self.highest_height)
        self.update()
