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

    def __init__(self, plot_x, plot_y, input_frame, seconds_before_loop):
        super().__init__()  

    #Type of data being parsed
        self.plot_x = plot_x
        self.plot_y = plot_y

    #Cursor movement initialization
        self.thirty_fps_begin_linemove = time.time()

    #Gif initialization
        self.loop_time = time.time()

    # Widget init
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('#1E1E1E')
        self.graphWidget.setTitle("Low-Level Data ", color="w", size="15pt")
        styles = {"color": "#fff", "font-size": "15px"}
        # labels
        self.graphWidget.setLabel("left", "Leg Height (mm)", **styles)
        self.graphWidget.setLabel("bottom", "Time (s)", **styles)
        # grid
        self.graphWidget.showGrid(x=True, y=True)
        # size
        self.graphWidget.setFixedSize(600, 400)  # Adjust the size as needed
        self.graphWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
    # Cursor Pens
        pen = pg.mkPen(color=(255, 255, 255), width = 3)
        cursor_pen = pg.mkPen(color = (255,0,0), width = 1)
        moving_pen = pg.mkPen(color = (255, 165, 0), width = 1)

    # Assign data to graph
        self.graphWidget.plot(plot_x, plot_y, pen=pen)

    # Crosshair inits
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=moving_pen)
        self.crosshair_cursor = pg.InfiniteLine(angle=90, movable=False, pen=cursor_pen)

    # Add crosshairs to widget 
        self.graphWidget.addItem(self.crosshair_v, ignoreBounds=True)
        self.graphWidget.addItem(self.crosshair_cursor, ignoreBounds=True)
    # Run when the mouse is in the graph
        self.proxy = pg.SignalProxy(self.graphWidget.scene().sigMouseMoved, rateLimit=30, slot=self.update_crosshair)
        
    # Makes other line move across like a gif
    def move_crosshair(self, e):
        line_move_index = 1
        if(time.time() - self.thirty_fps_begin_linemove) > (1/30):
            self.thirty_fps_begin_linemove = time.time()
            line_move_index = (1/30)
            if ((time.time() - self.loop_time) > seconds_before_loop):
                self.loop_time = time.time()
                #Set crosshair back to where the input_frame is
                self.crosshair_v.setPos(force_time[inputFrameToGraphXFrame("force", input_frame)])
            self.crosshair_v.setPos(self.crosshair_v.x() + line_move_index)
            self.ballWidget.update_ball_position(barXToY(self.crosshair_v.x()))
            line_move_index += (1/30)

    # Moves the main crosshair line over the graph
    def update_crosshair(self, e):
        pos = e[0]
        if self.graphWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.graphWidget.getPlotItem().vb.mapSceneToView(pos)
            self.crosshair_cursor.setPos(mousePoint.x())
            self.crosshair_v.setPos(mousePoint.x())   

    def run(self):

        

class GraphWidget(QWidget):
    def __init__(self,plot_x, plot_y):
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

    
    def update_plot(self, plot_x, plot_y):
        self.graphWidget.plot(plot_x, plot_y, pen=self.pen)
    
    def update_image(self,pixmap): 
            self.label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
    def move_crosshair(self, e):
        line_move_index = 1
        if(time.time() - self.thirty_fps_begin_linemove) > (1/30):
            self.thirty_fps_begin_linemove = time.time()
            line_move_index = (1/30)
            if ((time.time() - self.loop_time) > seconds_before_loop):
                self.loop_time = time.time()
                #Set crosshair back to where the input_frame is
                self.crosshair_v.setPos(force_time[inputFrameToGraphXFrame("force", input_frame)])
            self.crosshair_v.setPos(self.crosshair_v.x() + line_move_index)
            self.ballWidget.update_ball_position(barXToY(self.crosshair_v.x()))
            line_move_index += (1/30)

    def update_crosshair(self, e):
        pos = e[0]
        if self.graphWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.graphWidget.getPlotItem().vb.mapSceneToView(pos)
            self.crosshair_cursor.setPos(mousePoint.x())
            self.crosshair_v.setPos(mousePoint.x())            
        
        