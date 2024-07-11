from glob import glob
import os
import pandas as pd
import csv

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
            print("Found force!")
            
    for file in mocap_file_list:
        if(file.endswith(".csv")):
            mocap_file = os.path.join(os.path.join(os.getcwd(), 'mocap'), file)
            print("Found mocap!")
def findStartForce():
    with open(force_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        df = pd.read_csv(csv_file)
        global r
        r = 1
        for index, row in df.iterrows():
            r+=1
            if float(row["Leg 0 Z force"]) < -1:
                print(r)
                break
fileStatus()
findStartForce()