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
from bisect import bisect_left

class csvProcess():
    """Processes CSV and returns useful data
    """
    def __init__(self, csv_path, data_header, subsample_rate=60, header_row = 0):
        self.force_file = csv_path
        self.data_header = data_header

        self.subsample_rate = subsample_rate

        self.header_row = header_row

        self.force_height = []
        self.force_time = []
        self.step_list = []
        self.force_start_index = 0
        self.detection_offset = 5

    def copyForceForces(self):
        """ Returns all low-level leg Z samples(converted to M) in accordance with the freq interval
        """
        with open(self.force_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            data_iterator = 0
            force_height_iterator = 0
            reading_nums = False
            print("Copying data...")
            for row in reader:
                if (force_height_iterator > self.header_row) and (data_iterator > int(1000 / self.subsample_rate)):
                    if not reading_nums:
                        self.highest_height = float(row[self.data_header])
                        self.lowest_height = float(row[self.data_header])
                        reading_nums = True
                    data_iterator = 0 
                    self.force_height.append(float(row[self.data_header]))
                    if(float(row[self.data_header]) > self.highest_height):
                        self.highest_height = float(row[self.data_header])
                    if(float(row[self.data_header]) < self.lowest_height):
                        self.lowest_height = float(row[self.data_header])
                data_iterator += 1
                force_height_iterator += 1
            print("Done.")
            #print("Max height: " + str(self.highest_height))
            #print("Low height: " + str(self.lowest_height))

            
    def copyForceTime(self):
        """ Returns all low level time samples in accordance with freq interval
        """
        with open(self.force_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            force_time_iterator = 0
            data_iterator = 0
            print("Copying time data...")
            for row in reader:
                if (force_time_iterator > 0) and (data_iterator > int(1000 / self.subsample_rate)):
                    data_iterator = 0
                    self.force_time.append(float(row[0]))
                data_iterator += 1
                force_time_iterator += 1

    def stepChop(self):
        """Returns list of times where data spikes (steps) occur
        """
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
                #if(round(self.force_height[i], 4) > (round(self.force_height[i-50] + 10, 4))):
                if(round(self.force_height[i], 4) > (round(self.force_height[i-0.050] + 0.010, 4))):
                    plateu = False
                    recent_high = -0.400
            else:
                # If the height increases, a leg is moving up, updating that height to the recent highest
                if self.force_height[i] > recent_high:
                    recent_high = self.force_height[i]
                # If the leg height starts to dip
                elif self.force_height[i] < recent_high:
                    # The leg dip has to be significant enough 
                    if recent_high > (self.force_height[i] + 0.120):
                        # Adds time of leg movement to list. 
                        recent_high = self.force_height[i]
                        self.step_list.append(round(self.force_time[i] - self.detection_offset))
                
    def barXToY(self, bar_x):
        """Converts a graph time to its corresponding height 

        Args:
            bar_x (float): Time(x) in the graph  

        Returns:
            float: current graph y
        """
        return (self.force_height[bisect_left(self.force_time, bar_x)])
