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
from graphProcessing import *
from videoProcessing import *
from ballWidget import *


force_file = None 
mocap_file = None
video_file = None
r = None

force_height = None
force_time = None
mocap_height = None
mocap_time = None

step_list = None

# dictates how many samples should be registered every x steps. Lower = more samples
frequency_interval = 1
# prints out messages if able to find the files in the folders
def fileStatus():
    # file reference to the low level file. Note: force refers to low level in every instance here
    global force_file
    # file reference to the mocap file
    global mocap_file
    force_file_list = os.listdir(os.path.join(os.getcwd(), 'force'))
    mocap_file_list = os.listdir(os.path.join(os.getcwd(), 'mocap'))
    # finds csv files without needing a name
    for file in force_file_list: 
        if file.endswith('.csv'):
            force_file = os.path.join(os.path.join(os.getcwd(), 'force'), file)
            print("Found force file!")
            
    for file in mocap_file_list:
        if(file.endswith(".csv")):
            mocap_file = os.path.join(os.path.join(os.getcwd(), 'mocap'), file)
            print("Found mocap file!")
#Uses leg force to find when SPIRIT stands up 
def findStartForce():
    with open(force_file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        global force_index
        force_index = 1
        print("Finding start force time...")
        for row in reader:
            # which leg is used shouldn't matter because its just standing up so I chose leg 0
            column_value = row['Leg 0 Z force']
            force_index +=1
            # -30 is the force threshold for saying that SPIRIT has started 
            if float(column_value) < -30:
                return force_index
                print("Done.")
                break
# Uses Y-position to find when SPIRIT first stands up
# IMPORTANT: The Y and Z axes are flipped here in respect to their usual orientations
# Just think of mocap as using the Minecraft coordinate system
def findStartMocap():
    with open(mocap_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        global mocap_index
        mocap_array_index = 0
        mocap_index = 1
        start_row = 8
        print("Finding start mocap time...")
        for row in reader:
            # Skips beginning texts and a few data samples. Couldn't fix the sample skip thing...
            if mocap_index == start_row:
                global start_height
                start_height = row[7]
            elif mocap_index > start_row:
                column_value = row[7]
                mocap_array_index+=1
                # Registers beginning of movement if SPIRIT has moved 50mm 
                # The check covers for if the mocap starts late and has already stood up
                if ((float(column_value) - float(start_height))  > 50) or ((float(column_value) - float(start_height))  < -50):
                    return mocap_index
                    print("Done.")
                    break
            mocap_index += 1
#Returns all mocap Y axis samples in accordance to the frequency interval
def copyMocapHeights():
    mocap_height = []
    with open(mocap_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        mocap_array_index = 0
        start_row = 8
        mocap_iterator = 0
        print("Copying mocap data for visualization...")
        for row in reader:
            if (mocap_iterator > start_row) and not (mocap_iterator % frequency_interval):
                mocap_height.append(float(row[7]))
                mocap_array_index +=1
            mocap_iterator +=1
        print("Done.")
        return mocap_height
# Returns all low-level leg Z samples(converted to M) in accordance with the freq interval
def copyForceForces(leg_number):
    force_height = []
    with open(force_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        force_force_iterator = 0
        print("Copying force data for visualization...")
        for row in reader:
            if (force_force_iterator > 0) and not(force_force_iterator % frequency_interval):
                # chooses Z coords depending on leg chosen 
                force_height.append(float(row[47 + (3 * leg_number)]) * 1000)
            force_force_iterator += 1
        print("Done.")
        return force_height
# Returns all low level time samples in accordance with freq interval
def copyForceTime():
    force_time = []
    with open(force_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        force_time_iterator = 0
        print("Copying force time data for visualization...")
        for row in reader:
            if (force_time_iterator > 0) and not (force_time_iterator % frequency_interval):
                force_time.append(float(row[0]))
            force_time_iterator += 1
        return force_time
# Returns all low level mocap time samples in accordance with freq interval
def copyMocapTime():
    mocap_time = []
    with open(mocap_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        mocap_iterator = 0
        start_row = 8
        print("Copying mocap time for visualization...")
        for row in reader:
            if (mocap_iterator > start_row) and  not(mocap_iterator % frequency_interval):
                mocap_time.append(float(row[1]))
            mocap_iterator +=1
        print("Done.")
        return mocap_time
#Synchronizes mocap time to fit with low level data
def shiftMocapTime(mocap_time_array, force_time_array, force_start_index, mocap_start_index, error_offset):
    # time when mocap has registered first SPIRIT movement
    mocap_og_start_time = mocap_time_array[mocap_start_index]
    # Sets the mocap time when SPIRIT first moves to be when the force first registers movement
    # the offset accounts for if the mocap is started well after SPIRIT starts moving
    # offset should be 0 when mocap is started properly, but since the data im working with wasn't started properly I set it to 17 when called
    mocap_time_array[mocap_start_index] = force_time_array[force_start_index] + error_offset
    for i in range(len(mocap_time_array)):
        # doesn't shift the already shifted start
        if(i != mocap_start_index):
            # offset is how much time before/after the current sample is from the mocap start time of movement
            time_offset = mocap_time_array[i] - mocap_og_start_time + error_offset
            # converts each mocap time sample to be the force start time shifted by the offset 
            mocap_time_array[i] = force_time_array[force_start_index] + time_offset 
# Shifts the mocap times, plots the data, chops of the data based on leg movement, writes new time to original mocap csv
# a lot of things happen here becase the copy commands take so much time 
def verifyPlot(force_start, mocap_start, show_plot):

    global force_height
    global force_time
    global mocap_height
    global mocap_time
    global step_list

    mocap_height = copyMocapHeights()
    #Custom leg input
    force_height = copyForceForces(0)
    force_time = copyForceTime()
    mocap_time = copyMocapTime()
    
    # shifts the mocap stuff here
    print("Shifting Mocap time data to match low level")
    shiftMocapTime(mocap_time, force_time, force_start, mocap_start, 17)
    
    #handles plotting info
    if(show_plot):
        plt.plot(force_time, force_height, label="leg0(low-level)")
        plt.plot(mocap_time, mocap_height, label ="SPIRIT(mocap)")
        plt.xlabel('Time (s)')
        plt.ylabel('Height()')
        plt.legend(loc='best')
        plt.title("Mocap-force SPIRIT height to leg height over time")

    print("Generating leg step times...")
    # chops up leg stuff on plot
    step_list = stepChop(force_height, force_time)
    # writes chops to plot
    if(show_plot):
        for item in step_list:
            plt.axvline(x=item, color = 'r', label = 'step')
    print("Legs moved at these times:")
    print(step_list)
    # Writes synchronized time to the mocap file
    print('Writing new data to mocap file...')
    appendTimeColumn(mocap_time)
    print("Writing leg step data")
    appendLegColumn(mocap_time, step_list)
    if(show_plot):
        print("Done. Showing...")
        plt.show()

# once properly aligned, find the times where a leg is put on the ground
def stepChop(force_height, force_time):
    recent_high = 0
    step_array = []
    plateu = False
    skip_this_spike = False
    for i in range(1, len(force_height)):
        # Looks for plateus ever 8k frames. If plateu already detected we don't want it to cancel out of being a plateu with the else 
        if((i % 8000) == 0) and (not plateu):
            # Looks at the low level height 4k frames before, if equal, plateu detected
            if force_height[i] == force_height[i - 4000]:
                plateu = True
            else:
                plateu = False
        # Plateu detected subroutine
        if(plateu):
            # If the low level leg height begins to rise considerably, end of standing and sitting and beginning rising 
            if(round(force_height[i], 4) > (round(force_height[i-50] + 10, 4))):
                plateu = False
                recent_high = -400
        else:
            # If the height increases, a leg is moving up, updating that height to the recent highest
            if force_height[i] > recent_high:
                recent_high = force_height[i]
            # If the leg height starts to dip
            elif force_height[i] < recent_high:
                # The leg dip has to be significant enough 
                if recent_high > (force_height[i] + 120):
                    # Adds time of leg movement to list. 
                    recent_high = force_height[i]
                    step_array.append(force_time[i])
    return step_array


# writes new times to the csv in mocap
def appendTimeColumn(mocap_time):
    with open(mocap_file,'r') as csv_file:
        reader = csv.reader(csv_file)
        data = list(reader)
    
    for i in range(1, len(data)):
        if(i < len(mocap_time)):

            if i==6:
                data[i].append('Adjusted Time (seconds)')
            elif i > 6:
                data[i].append(mocap_time[i-1])

    with open(mocap_file, 'w', newline='') as write_file:
        writer = csv.writer(write_file)
        writer.writerows(data)

def appendLegColumn(mocap_time, step_list):
    step_time_index = 0
    # 0 is no movement, 1 is leg movement
    with open(mocap_file,'r') as csv_file:
        reader = csv.reader(csv_file)
        data = list(reader)
    
    for i in range(1, len(data)):
        if(i < len(mocap_time)):
            if i==6:
                data[i].append('Leg status')
            elif i > 6:
                # Goes through every time of steps, if the times match, append the status
                if(step_time_index < len(step_list)):
                    if round(mocap_time[i], 2) == round(step_list[step_time_index], 2):
                        data[i].append(1)
                        step_time_index += 1
                    else:
                        data[i].append(0)
                else:
                    data[i].append(0)

    with open(mocap_file, 'w', newline='') as write_file:
        writer = csv.writer(write_file)
        writer.writerows(data)


    
    



def csvAlter(show_plot):
    fileStatus()
    force_start = findStartForce()
    print(force_start)
    mocap_start = findStartMocap()
    print(mocap_start)
    verifyPlot(force_start, mocap_start, show_plot)


def videoSync(input_frame, seconds_before_loop):
    videoStatus()
    openWindow(input_frame, seconds_before_loop)

# Write something that gives you an array of times that the leg has moved, SAVE THE TIMES SOMEWHERE (json maybe) (want video offset, file names of all files connected, list of all starting step times in each csv) press for next step (start of steptimes), go to step 100. use a video player that reads frames like open cv 
def videoStatus():
    global video_file
    video_file_list = os.listdir(os.path.join(os.getcwd(), 'video'))
    for file in video_file_list: 
        if ((file.endswith('.mp4')) or (file.endswith('.MOV'))):
            video_file = os.path.join(os.path.join(os.getcwd(), 'video'), file)
            print("Found video file!")
    
def playVideo():
    video_frame = 0
    cap = cv2.VideoCapture(video_file)
    if (cap.isOpened()== False):
        print("Error playing video...")
    else:
        print("Playing...")
    last_imshow_time = time.time()
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    print(f"fps: {frame_rate}")
    while(cap.isOpened()):
        # Capture frame-by-frame
        #read_time_begin = time.time()
        ret, frame = cap.read()

        #print(thirty_fps_diff)
        while (time.time() - last_imshow_time)< (1/frame_rate):
            pass
        #read_time_end = time.time()
        #read_diff = read_time_begin-read_time_end
        #print(f"Read time difference: {read_diff}")
        #print(f"Video frame: {video_frame}")
        
        video_frame+=1
        if ret == True:
            # Display the resulting frame
            #show_time_begin = time.time()
            last_imshow_time = time.time()
            cv2.imshow('Frame', frame)
            #show_time_end = time.time()
            #show_diff = show_time_begin - show_time_end
            #print(f"Show time difference: {show_diff}")
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

def playVideoGif(input_frame, seconds_before_loop):
    video_frame = 0
    cap = cv2.VideoCapture(video_file)
    cap.set(1, input_frame)
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
        
        if ((time.time() - loop_begin) > seconds_before_loop):
            print(f"frame: {input_frame}")
            cap.set(1, input_frame)
            loop_begin = time.time()
        ret, frame = cap.read()

        #print(thirty_fps_diff)
        while (time.time() - last_imshow_time)< (1/frame_rate):
            pass
        #read_time_end = time.time()
        #read_diff = read_time_begin-read_time_end
        #print(f"Read time difference: {read_diff}")
        #print(f"Video frame: {video_frame}")
        
        video_frame+=1
        if ret == True:
            # Display the resulting frame
            #show_time_begin = time.time()
            last_imshow_time = time.time()
            cv2.imshow('Frame', frame)
            #show_time_end = time.time()
            #show_diff = show_time_begin - show_time_end
            #print(f"Show time difference: {show_diff}")
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

def openWindow(input_frame, seconds_before_loop):
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            #self.thirty_fps_begin_linemove = time.time()
            #self.loop_time = time.time()

        # Main window setup
            self.setWindowTitle("RoboCorrelate")
            self.setMinimumSize(QSize(800,700))
            
        # Ball widget
            #self.ballWidget = BallWidget()

        # Video
            self.label = QLabel(self)

        # Establish video thread
            self.video_thread = VideoThread(video_file, input_frame, seconds_before_loop)
            self.video_thread.change_pixmap_signal.connect(self.update_image)
            #self.video_thread.change_pixmap_signal.connect(self.move_crosshair)
            self.video_thread.start()


            self.graphic_thread = GraphThread(force_time, force_height, input_frame, seconds_before_loop)
            
            self.graphic_thread.start()

        #Lay the ball widget to the right of the video
            layout_h = QHBoxLayout()
            layout_h.addWidget(self.label)
            #layout_h.addWidget(self.ballWidget)
        # Lay the graph under everything
            layout_v = QVBoxLayout()
            layout_v.addLayout(layout_h)
            layout_v.addWidget(self.graphic_thread.graphWidget)
            
        #Center everything
            central_widget = QWidget()
            central_widget.setLayout(layout_v)
            self.setCentralWidget(central_widget)


        def update_image(self,pixmap): 
            self.label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        #def closeEvent(self,event):
        #    self.thread.stop()
        #    event.accept()
        
# Make everything execute
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    #window 
    window = MainWindow()
    window.show()

    app.exec()

def playVideoInWindow():
    pass 