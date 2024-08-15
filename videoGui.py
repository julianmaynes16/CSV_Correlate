import os
import pandas as pd
import csv
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
import pyqtgraph as pg
import sys
import cv2
import time
import matplotlib.pyplot as plt
from videoThread import *
from ballWidget import *
from csvProcess import *
from bisect import bisect_left


class videoGui():
    def __init__(self, csv_process, video_fps = 30, input_frame = 0, seconds_before_loop = 5):
        self.csv_process = csv_process
        self.video_fps = video_fps
        self.input_frame = input_frame
        self.seconds_before_loop = seconds_before_loop
        self.data_fps = self.csv_process.truncated_fps

        video_file_list = os.listdir(os.path.join(os.getcwd(), 'video'))
        for file in video_file_list: 
            if ((file.endswith('.mp4')) or (file.endswith('.MOV'))):
                self.video_file = os.path.join(os.path.join(os.getcwd(), 'video'), file)
                print("Found video file!")


    def inputFrameToGraphXFrame(self, data_type, input_frame):
    
    # turn frame 3000 into an x coordinate

    # we know the first x by the first index of time
    # The camera fps should be calculated
    # The Video is 30 frames
    # So we need to get a starting value
        if(data_type == "mocap"):
            data_fps = 120
            graph_x_start = self.csv_process.mocap_time[0]
        elif(data_type == "force"):
            data_fps = 1000
            graph_x_start = self.csv_process.force_time[0]
            #should be like 442.19
        return(int(((1/self.video_fps) * input_frame) * data_fps)) # returns the frame where the input frame    

# Write something that gives you an array of times that the leg has moved, SAVE THE TIMES SOMEWHERE (json maybe) (want video offset, file names of all files connected, list of all starting step times in each csv) press for next step (start of steptimes), go to step 100. use a video player that reads frames like open cv 
    def playVideo(self):
        video_frame = 0
        cap = cv2.VideoCapture(self)
        if (cap.isOpened()== False):
            print("Error playing video...")
        else:
            print("Playing...")
        last_imshow_time = time.time()
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        print(f"fps: {frame_rate}")
        while(cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()

            while (time.time() - last_imshow_time)< (1/frame_rate):
                pass
            
            video_frame+=1
            if ret == True:
                # Display the resulting frame
                last_imshow_time = time.time()
                cv2.imshow('Frame', frame)
                # Press Q on keyboard to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            # Break the loop
            else:
                break

        # When everything done, release
        # the video capture object
        cap.release()

        # Closes all the frames
        cv2.destroyAllWindows()

    def playVideoGif(self):
        video_frame = 0
        cap = cv2.VideoCapture(self.video_file)
        cap.set(1, self.input_frame)
        if (cap.isOpened()== False):
            print("Error playing video...")
        else:
            print("Playing...")
        last_imshow_time = time.time()
        loop_begin = time.time()
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        print(f"fps: {frame_rate}")
        while(cap.isOpened()):
            # Capture frame-by-frame
            
            if ((time.time() - loop_begin) > self.seconds_before_loop):
                print(f"frame: {self.input_frame}")
                cap.set(1, self.input_frame)
                loop_begin = time.time()
            ret, frame = cap.read()

            while (time.time() - last_imshow_time)< (1/frame_rate):
                pass
            
            video_frame+=1
            if ret == True:
                # Display the resulting frame
                
                last_imshow_time = time.time()
                cv2.imshow('Frame', frame)
                #show_diff = show_time_begin - show_time_end
                # Press Q on keyboard to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            # Break the loop
            else:
                break
            
        # When everything done, release
        # the video capture object
        cap.release()

        # Closes all the frames
        cv2.destroyAllWindows()

    class mainWindow(QMainWindow):
        def __init__(self, csv_process, video_gui):
            super().__init__()
            print("Initializing Window...")
        #Setup csv and video objects
            self.csv_process = csv_process
            self.video_gui = video_gui
        # Truncate input values
            self.csv_process.returnTruncatedData(self.csv_process.force_height, self.csv_process.force_time, datatype = "force", framerate = 60)

            self.thirty_fps_begin_linemove = time.time()
            self.loop_time = time.time()
        #Line moving 
            self.line_move_index = 0

            #Main setup
            #self.setStyleSheet("background-color: white;")
            self.setWindowTitle("RoboCorrelate")
            self.setMinimumSize(QSize(800,700))
            
        #Plot
            
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
            cursor_pen = pg.mkPen(color = (255,0,0), width = 2)
            moving_pen = pg.mkPen(color = (255, 165, 0), width = 1)
            self.graphWidget.plot(self.csv_process.force_time, self.csv_process.force_height, pen=pen)
        #crosshair lines
            self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=moving_pen)
            self.graphWidget.addItem(self.crosshair_v, ignoreBounds=True)
            self.crosshair_cursor = pg.InfiniteLine(pos = 500, angle=90, movable=True, pen=cursor_pen)
            self.graphWidget.setMouseEnabled(y=False)
            self.graphWidget.addItem(self.crosshair_cursor, ignoreBounds=True)
            
            

            #self.proxy = pg.SignalProxy(self.graphWidget.scene().sigMouseMoved, rateLimit=30, slot=self.update_crosshair)
        #Resize graph
            self.graphWidget.setFixedSize(600, 400)  # Adjust the size as needed
            self.graphWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            
        #ball widget
            self.ballWidget = BallWidget()

            self.label = QLabel(self)
        #video Control toolbar
            self.video_toolbar = QToolBar()
            style = self.style()
            pause_icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause, style.standardIcon(QStyle.SP_MediaPause))
            self._pause_action = self.video_toolbar.addAction(pause_icon, "Pause")
            link_icon = QIcon.fromTheme(QIcon.ThemeIcon.InsertLink)
            self._link_action = self.video_toolbar.addAction(link_icon, "Link")

        # Video Slider
            #make a box under it for the orange line path
            self.video_slider = QSlider(Qt.Horizontal)
        #layout
            #controls
            control_layout = QHBoxLayout()
            control_layout.addWidget(self.video_slider)
            control_layout.addWidget(self.video_toolbar)
            
            video_controls = QVBoxLayout()
            video_controls.addWidget(self.label)
            video_controls.addLayout(control_layout)

            video_ball = QHBoxLayout()
            video_ball.addLayout(video_controls)
            video_ball.addWidget(self.ballWidget)

            layout_v = QVBoxLayout()
            layout_v.addLayout(video_ball)
            layout_v.addWidget(self.graphWidget)
            

            central_widget = QWidget()
            central_widget.setLayout(layout_v)
            self.setCentralWidget(central_widget)

            self.thread = VideoThread(self.video_gui.video_file, self.video_gui.input_frame, self.video_gui.seconds_before_loop, playback_rate = 15)
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.thread.change_pixmap_signal.connect(self.move_crosshair)
            self.thread.start()
            print("Finished Initialization.")

        def update_image(self, gif_state): 
            #print(time.time())
            self.label.setPixmap(gif_state.pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            
        # Line goes for 7 seconds whent the video goes for 5. If the data is at 60 fps(0, 0.016,...)
        def move_crosshair(self, gif_state):
            # Move crosshair
            self.crosshair_v.setPos(self.crosshair_cursor.x() + gif_state.time)
            # Update Ball Position
            self.ballWidget.update_ball_position(self.csv_process.barXToY(self.crosshair_v.x()))
    
        def closeEvent(self,event):
            self.thread.stop()
            event.accept()

    
    #if __name__ == "__main__":
    #    main()