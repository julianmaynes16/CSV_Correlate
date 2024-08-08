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

class GraphThread(QThread):

    def __init__(self, plot_x, plot_y):
        super().__init__()   
        self.graphWidget = pg.PlotWidget()
        #Set background to white
        self.graphWidget.setBackground('#1E1E1E')
        #Set title
        self.graphWidget.setTitle("Low-Level Data ", color="w", size="15pt")
        #Set axis labels
        styles = {"color": "#fff", "font-size": "15px"}
        self.graphWidget.setLabel("left", "Leg Height (mm)", **styles)
        self.graphWidget.setLabel("bottom", "Time (s)", **styles)
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)

        pen = pg.mkPen(color=(255, 255, 255), width = 3)
        cursor_pen = pg.mkPen(color = (255,0,0), width = 1)
        moving_pen = pg.mkPen(color = (255, 165, 0), width = 1)
        self.graphWidget.plot(plot_x, plot_y, pen=pen)

        #crosshair lines
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=moving_pen)
        self.graphWidget.addItem(self.crosshair_v, ignoreBounds=True)
        self.crosshair_cursor = pg.InfiniteLine(angle=90, movable=False, pen=cursor_pen)
        self.graphWidget.addItem(self.crosshair_cursor, ignoreBounds=True)
    
        self.proxy = pg.SignalProxy(self.graphWidget.scene().sigMouseMoved, rateLimit=30, slot=self.update_crosshair)
        #Resize graph
        self.graphWidget.setFixedSize(600, 400)  # Adjust the size as needed
        self.graphWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    def run(self):
            
            
           