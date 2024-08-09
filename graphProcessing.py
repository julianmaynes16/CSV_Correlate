import os
import pandas as pd
import csv
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
from pyqtgraph import PlotWidget, plot
from ballWidget import * 
import pyqtgraph as pg
import sys
import cv2
import time

class GraphThread(QThread):
    
    crosshair_update_signal = Signal()

    def __init__(self, plot_x, plot_y, input_frame, seconds_before_loop):
        QThread.__init__(self)  

    # Type of data being parsed
        self.plot_x = plot_x
        self.plot_y = plot_y
        self.input_frame = input_frame
        self.seconds_before_loop = seconds_before_loop

    # Run loop
        self.run_flag = True
    # Fps variable
        self.frame_rate = 30

    #Cursor movement initialization
        self.thirty_fps_begin = time.time()
    
    #Line movement info
        self.line_move_index = 1 / self.frame_rate

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
        
    # Connect Graph Widget to update crosshair
        #self.crosshair_update_signal.connect(self.update_crosshair)
        #self.graphWidget.scene().sigMouseMoved.connect()
        #self.graphWidget.sigSceneMouseMoved.connect(self.update_crosshair)

    # Initialize ball to enable updating
        self.ballWidget = BallWidget()

    def barXToY(self, bar_x):
        for i in range(len(self.plot_x)):
            if self.plot_x[i] >= bar_x:
                return self.plot_y[i]
        
    def inputFrameToGraphXFrame(self, data_type, input_frame):
        
        video_fps = 30
        if(data_type == "mocap"):
            data_fps = 120
            graph_x_start = self.plot_x[0]
        elif(data_type == "force"):
            data_fps = 1000
            graph_x_start = self.plot_x[0]
            #should be like 442.19
        return(int(((1/video_fps) * input_frame) * data_fps)) # returns the frame where the input frame
    
    # Makes other line move across like a gif
    def move_crosshair(self):
    #If the line has moved past the max gif time, reset it back to the cursos line
        if(line_move_index > self.seconds_before_loop):
            self.self.crosshair_v.setPos(self.crosshair_cursor.x())
            line_move_index = (1/self.frame_rate)
    # Move the orange line and make it move one more frame next time
        self.crosshair_v.setPos(self.crosshair_v.x() + line_move_index)
        line_move_index += (1/self.frame_rate)
    # Update the ball location
        self.ballWidget.update_ball_position(self.barXToY(self.crosshair_v.x()))
        
    #If the line hasn't reached the end yet
        if((time.time() - self.loop_time) > self.seconds_before_loop):
        # Update the time
            self.loop_time = time.time()
        #Set crosshair back to where the input_frame is
            self.crosshair_v.setPos(self.force_time[self.inputFrameToGraphXFrame("force", self.input_frame)])
        
        

    # Moves the main crosshair line over the graph
    def update_crosshair(self):
        pos = QCursor.pos()
    # If the mouse cursor is in the graph
        if self.graphWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.graphWidget.getPlotItem().vb.mapSceneToView(pos)
        # Set the red line and orange line to the mouse cursor 
            self.crosshair_cursor.setPos(mousePoint.x())
            self.crosshair_v.setPos(mousePoint.x())
        # Move the orange line
            self.move_crosshair()   

    #def run(self):
    #    while self.run_flag:
    #        if(time.time() - self.thirty_fps_begin) > (1/self.frame_rate):
    #            self.crosshair_update_signal.emit()