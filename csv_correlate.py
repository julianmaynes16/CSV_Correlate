from glob import glob
import os
import pandas as pd
import csv
import matplotlib.pyplot as plt


force_file = None 
mocap_file = None
r = None


def fileStatus():
    global force_file
    global mocap_file
    force_file_list = os.listdir(os.path.join(os.getcwd(), 'force'))
    mocap_file_list = os.listdir(os.path.join(os.getcwd(), 'mocap'))
    for file in force_file_list: 
        if file.endswith('.csv'):
            force_file = os.path.join(os.path.join(os.getcwd(), 'force'), file)
            print("Found force file!")
            
    for file in mocap_file_list:
        if(file.endswith(".csv")):
            mocap_file = os.path.join(os.path.join(os.getcwd(), 'mocap'), file)
            print("Found mocap file!")
def findStartForce():
    with open(force_file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        global force_index
        force_index = 1
        print("Finding start force time...")
        for row in reader:
            column_value = row['Leg 0 Z force']
            force_index +=1
            if float(column_value) < -30:
                return force_index
                print("Done.")
                break
def findStartMocap():
    with open(mocap_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        global mocap_index
        mocap_array_index = 0
        mocap_index = 1
        start_row = 8
        print("Finding start mocap time...")
        for row in reader:
            if mocap_index == start_row:
                global start_height
                start_height = row[7]
                #print(f"start height: {start_height}")
            elif mocap_index > start_row:
                column_value = row[7]
                mocap_array_index+=1
                if (float(column_value) - float(start_height))  > 50:
                    return mocap_index
                    print("Done.")
                    break
            mocap_index += 1
# converts to mm and the origin is in M
def copyMocapHeights():
    mocap_height = []
    with open(mocap_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        mocap_array_index = 0
        start_row = 8
        mocap_iterator = 0
        print("Copying mocap data for visualization...")
        for row in reader:
            if mocap_iterator > 8:
                mocap_height.append(row[7] * 1000)
                mocap_array_index +=1
            mocap_iterator +=1
        print("Done.")
        return mocap_height
# converts to mm and the origin is in M
def copyForceForces():
    force_height = []
    with open(force_file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        print("Copying force data for visualization...")
        for row in reader:
            force_height.append(row['Leg 0 Z force'])
        print("Done.")
        return force_height
def copyForceTime():
    force_time = []
    with open(force_file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        print("Copying force time data for visualization...")
        for row in reader:
            force_time.append(row['Leg 0 Z force'])
        return force_time
def copyMocapTime():
    mocap_time = []
    with open(mocap_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        mocap_iterator = 0
        start_row = 8
        print("Copying mocap time for visualization...")
        for row in reader:
            if mocap_iterator > start_row:
                mocap_time.append(row[1])
            mocap_iterator +=1
        print("Done.")
        return mocap_time
# use mocap's spirit height and knee height and graph the two
def verifyPlot(force_start, mocap_start):
    mocap_height = copyMocapHeights()
    force_height = copyForceForces()
    force_time = copyForceTime()
    mocap_time = copyMocapTime()


    plt.plot(force_height, force_time, label="Knee(mocap)")
    plt.plot(mocap_height, mocap_time, label ="SPIRIT(mocap)")
    plt.xlabel('Time (s)')
    plt.ylabel('Height()')
    plt.title("Mocap-force SPIRIT height to knee height over time")
    print("Showing...")
    plt.show()



def changeMocaptimes():
    pass
            
