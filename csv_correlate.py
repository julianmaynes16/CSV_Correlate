from glob import glob
import os
import pandas as pd
import csv
import matplotlib.pyplot as plt


force_file = None 
mocap_file = None
r = None

frequency_interval = 1

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
                # The check covers for if the mocap starts late
                if ((float(column_value) - float(start_height))  > 50) or ((float(column_value) - float(start_height))  < -50):
                    return mocap_index
                    print("Done.")
                    break
            mocap_index += 1
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
                #mocap_height.append(mocap_element * 1000)
                mocap_height.append(float(row[7]))
                mocap_array_index +=1
            mocap_iterator +=1
        #mocap_array_index = 0
        #for item in mocap_height:
        #    mocap_height[mocap_array_index] = item * 1000
        #    mocap_array_index += 1
        print("Done.")
        return mocap_height
# converts to mm and the origin is in M
def copyForceForces():
    force_height = []
    with open(force_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        force_force_iterator = 0
        print("Copying force data for visualization...")
        for row in reader:
            if (force_force_iterator > 0) and not(force_force_iterator % frequency_interval):
                force_height.append(abs(float(row[47])) * 1000)
            force_force_iterator += 1
        print("Done.")
        return force_height
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

def shiftMocapTime(mocap_time_array, force_time_array, force_start_index, mocap_start_index, error_offset):
    mocap_og_start_time = mocap_time_array[mocap_start_index]
    #Sets the starting time of the mocap array to the start time of the force
    mocap_time_array[mocap_start_index] = force_time_array[force_start_index]
    print(mocap_time_array)
    for i in range(len(mocap_time_array)):
        # if actual start is 5 and first index is 1, 4 second difference. 
        #take the 4 second difference from 
        if(i != mocap_start_index):
            time_offset = mocap_time_array[i] - mocap_og_start_time + error_offset
            print(f"Offset:{time_offset}")
            mocap_time_array[i] = force_time_array[force_start_index] + time_offset 

    #print(mocap_time_array)
def verifyPlot(force_start, mocap_start):
    mocap_height = copyMocapHeights()
    force_height = copyForceForces()
    force_time = copyForceTime()
    mocap_time = copyMocapTime()
    print("first item of mocap time before:")
    print(mocap_time[0])
    shiftMocapTime(mocap_time, force_time, force_start, mocap_start, 17)
    print("first item of mocap time after:")
    print(mocap_time[0])
    plt.plot(force_time, force_height, label="Knee(force)")
    plt.plot(mocap_time, mocap_height, label ="SPIRIT(mocap)")
    plt.xlabel('Time (s)')
    plt.ylabel('Height()')
    plt.legend(loc='best')
    plt.title("Mocap-force SPIRIT height to knee height over time")
    print('Writing new data to mocap file...')
    appendColumn(mocap_time)
    print("Done. Showing...")
    plt.show()

def appendColumn(mocap_time):
    with open(mocap_file,'r') as csv_file:
        reader = csv.reader(csv_file)
        data = list(reader)
    
    data[6].insert(2, 'Adjusted Time (seconds)')  
    for i in range(1, len(mocap_time)):
        print(i)
        data[i].append(mocap_time[i-1])

    with open(mocap_file, 'w', newline='') as write_file:
        writer = csv.writer(write_file)
        writer.writerows(data)
