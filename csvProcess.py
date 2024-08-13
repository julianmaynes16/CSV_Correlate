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
from videoProcessing import *
from ballWidget import *
from bisect import bisect_left

# prints out messages if able to find the files in the folders
class csvProcess():
    def __init__(self, leg_number=0, data_frequency = 1, truncated_fps=60, show_plot = True):
        self.leg_number = leg_number
        self.data_frequency = data_frequency
        self.truncated_fps = truncated_fps
        self.show_plot = show_plot
        self.mocap_height = []
        self.mocap_time = []
        self.force_height = []
        self.force_time = []
        self.step_list = []
        self.force_start_index = 0
        self.mocap_start_index = 0

    # file reference to the low level file and force file. Note: force refers to low level in every instance here
        force_file_list = os.listdir(os.path.join(os.getcwd(), 'force'))
        mocap_file_list = os.listdir(os.path.join(os.getcwd(), 'mocap'))
    # finds csv files without needing a name
        for file in force_file_list: 
            if file.endswith('.csv'):
                self.force_file = os.path.join(os.path.join(os.getcwd(), 'force'), file)
                print("Found force file!")
                
        for file in mocap_file_list:
            if(file.endswith(".csv")):
                self.mocap_file = os.path.join(os.path.join(os.getcwd(), 'mocap'), file)
                print("Found mocap file!")
        
#Uses leg force to find when SPIRIT stands up 
    def findStartForce(self):
        with open(self.force_file, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            force_index = 1
            print("Finding start force time...")
            for row in reader:
                # which leg is used shouldn't matter because its just standing up so I chose leg 0
                column_value = row['Leg 0 Z force']
                force_index +=1
                # -30 is the force threshold for saying that SPIRIT has started 
                if float(column_value) < -30:
                    self.force_start_index = force_index
                    break

# Uses Y-position to find when SPIRIT first stands up
# IMPORTANT: The Y and Z axes are flipped here in respect to their usual orientations
# Just think of mocap as using the Minecraft coordinate system
    def findStartMocap(self):
        with open(self.mocap_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            mocap_array_index = 0
            mocap_index = 1
            start_row = 8
            print("Finding start mocap time...")
            for row in reader:
                # Skips beginning texts and a few data samples. Couldn't fix the sample skip thing...
                if mocap_index == start_row:
                    start_height = row[7]
                elif mocap_index > start_row:
                    column_value = row[7]
                    mocap_array_index+=1
                    # Registers beginning of movement if SPIRIT has moved 50mm 
                    # The check covers for if the mocap starts late and has already stood up
                    if ((float(column_value) - float(start_height))  > 50) or ((float(column_value) - float(start_height))  < -50):
                        self.mocap_start_index = mocap_index
                        break
                mocap_index += 1
#Returns all mocap Y axis samples in accordance to the frequency interval
    def copyMocapHeights(self):
        with open(self.mocap_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            mocap_array_index = 0
            start_row = 8
            mocap_iterator = 0
            print("Copying mocap data for visualization...")
            for row in reader:
                if (mocap_iterator > start_row) and not (mocap_iterator % self.data_frequency):
                    self.mocap_height.append(float(row[7]))
                    mocap_array_index +=1
                mocap_iterator +=1
            print("Done.")
            
# Returns all low-level leg Z samples(converted to M) in accordance with the freq interval
    def copyForceForces(self):
        with open(self.force_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            force_force_iterator = 0
            print("Copying force data...")
            for row in reader:
                if (force_force_iterator > 0) and not(force_force_iterator % self.data_frequency):
                    # chooses Z coords depending on leg chosen 
                    self.force_height.append(float(row[47 + (3 * self.leg_number)]) * 1000)
                force_force_iterator += 1
            print("Done.")
# Returns all low level time samples in accordance with freq interval
    def copyForceTime(self):
        with open(self.force_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            force_time_iterator = 0
            print("Copying force time data...")
            for row in reader:
                if (force_time_iterator > 0) and not (force_time_iterator % self.data_frequency):
                    self.force_time.append(float(row[0]))
                force_time_iterator += 1
            
# Returns all low level mocap time samples in accordance with freq interval
    def copyMocapTime(self):
        with open(self.mocap_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            mocap_iterator = 0
            start_row = 8
            print("Copying mocap time for visualization...")
            for row in reader:
                if (mocap_iterator > start_row) and  not(mocap_iterator % self.data_frequency):
                    self.mocap_time.append(float(row[1]))
                mocap_iterator +=1
            print("Done.")
    
    def returnTruncatedData(self, input_height, input_time, datatype = "force", framerate = 60):
        print("Truncating data...")
        array_iterator = 0
        data_iterator = 0
        return_height = []
        return_time =[]
        if(datatype == "mocap"):
                data_fps = 120
        elif(datatype == "force"):
            data_fps = 1000
            for data_item in input_height:
                if (data_iterator > int(data_fps / framerate)):
                    data_iterator = 0
                    return_height.append(data_item)
                    return_time.append(input_time[array_iterator])
                    array_iterator += 1
                    
                else:
                    data_iterator +=1
                    array_iterator +=1
        self.force_height = return_height
        self.force_time = return_time
        print("Truncation Done.")

    
#Synchronizes mocap time to fit with low level data
    def shiftMocapTime(self, force_start_index, mocap_start_index, error_offset):
        # time when mocap has registered first SPIRIT movement
        mocap_og_start_time = self.mocap_time[mocap_start_index]
        # Sets the mocap time when SPIRIT first moves to be when the force first registers movement
        # the offset accounts for if the mocap is started well after SPIRIT starts moving
        # offset should be 0 when mocap is started properly, but since the data im working with wasn't started properly I set it to 17 when called
        self.mocap_time[mocap_start_index] = self.force_time[force_start_index] + error_offset
        for i in range(len(self.mocap_time)):
            # doesn't shift the already shifted start
            if(i != mocap_start_index):
                # offset is how much time before/after the current sample is from the mocap start time of movement
                time_offset = self.mocap_time[i] - mocap_og_start_time + error_offset
                # converts each mocap time sample to be the force start time shifted by the offset 
                self.mocap_time[i] = self.force_time[force_start_index] + time_offset 

    def copyData(self):
        self.copyMocapHeights()
        self.copyForceForces()
        self.copyForceTime()
        self.copyMocapTime()

    def plotInit(self):
        if(self.show_plot):
            plt.plot(self.force_time, self.force_height, label="leg0(low-level)")
            plt.plot(self.mocap_time, self.mocap_height, label ="SPIRIT(mocap)")
            plt.xlabel('Time (s)')
            plt.ylabel('Height()')
            plt.legend(loc='best')
            plt.title("Mocap-force SPIRIT height to leg height over time")

    def plotLines(self):
        if(self.show_plot):
            for item in self.step_list:
                plt.axvline(x=item, color = 'r', label = 'step')

    def showPlot(self):
        if(self.show_plot):
            print("Done. Showing...")
            plt.show()

    # Shifts the mocap times, plots the data, chops of the data based on leg movement, writes new time to original mocap csv
    def verifyPlot(self, force_start, mocap_start):

        self.copyData()
        
        # shifts the mocap stuff here
        print("Shifting Mocap time data to match low level")
        self.shiftMocapTime(force_start, mocap_start, 17)
        
        #handles plotting info
        self.plot_init()

        print("Generating leg step times...")
        # chops up leg stuff on plot
        self.stepChop()
        # writes chops to plot
        self.plotLines()
        print("Legs moved at these times:")
        print(self.step_list)
        # Writes synchronized time to the mocap file
        print('Writing new data to mocap file...')
        self.appendTimeColumn()
        print("Writing leg step data")
        self.appendLegColumn()
        self.showPlot()

# once properly aligned, find the times where a leg is put on the ground
    def stepChop(self):
        recent_high = 0
        plateu = False
        for i in range(1, len(self.force_height)):
            # Looks for plateus ever 8k frames. If plateu already detected we don't want it to cancel out of being a plateu with the else 
            if((i % 8000) == 0) and (not plateu):
                # Looks at the low level height 4k frames before, if equal, plateu detected
                if self.force_height[i] == self.force_height[i - 4000]:
                    plateu = True
                else:
                    plateu = False
            # Plateu detected subroutine
            if(plateu):
                # If the low level leg height begins to rise considerably, end of standing and sitting and beginning rising 
                if(round(self.force_height[i], 4) > (round(self.force_height[i-50] + 10, 4))):
                    plateu = False
                    recent_high = -400
            else:
                # If the height increases, a leg is moving up, updating that height to the recent highest
                if self.force_height[i] > recent_high:
                    recent_high = self.force_height[i]
                # If the leg height starts to dip
                elif self.force_height[i] < recent_high:
                    # The leg dip has to be significant enough 
                    if recent_high > (self.force_height[i] + 120):
                        # Adds time of leg movement to list. 
                        recent_high = self.force_height[i]
                        self.step_list.append(self.force_time[i])


# writes new times to the csv in mocap
    def appendTimeColumn(self):
        with open(self.mocap_file,'r') as csv_file:
            reader = csv.reader(csv_file)
            data = list(reader)
        
        for i in range(1, len(data)):
            if(i < len(self.mocap_time)):

                if i==6:
                    data[i].append('Adjusted Time (seconds)')
                elif i > 6:
                    data[i].append(self.mocap_time[i-1])

        with open(self.mocap_file, 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(data)

    def appendLegColumn(self):
        step_time_index = 0
        # 0 is no movement, 1 is leg movement
        with open(self.mocap_file,'r') as csv_file:
            reader = csv.reader(csv_file)
            data = list(reader)
        
        for i in range(1, len(data)):
            if(i < len(self.mocap_time)):
                if i==6:
                    data[i].append('Leg status')
                elif i > 6:
                    # Goes through every time of steps, if the times match, append the status
                    if(step_time_index < len(self.step_list)):
                        if round(self.mocap_time[i], 2) == round(self.step_list[step_time_index], 2):
                            data[i].append(1)
                            step_time_index += 1
                        else:
                            data[i].append(0)
                    else:
                        data[i].append(0)

        with open(self.mocap_file, 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(data)



    def barXToY(self, bar_x):
        return (bisect_left(self.force_time, bar_x))
         