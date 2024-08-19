from csvProcess import *
from videoGui import *
import argparse

def main():
    
    parse = argparse.ArgumentParser("Video Synchronizing GUI. Used to get the time offset in seconds between a video and a data series from a csv. USE QUOTES AROUND STRINGS.\n")
    parse.add_argument('--video_path', '-v', type=str, default=None, help='Path to video to be synced') 
    parse.add_argument('--csv_path', '-c', type=str, default=None, help='Path to CSV to be synced') 
    parse.add_argument('--sync_header', '-s', type=str, default=None, help='CSV column header for syncing signal') 
    parse.add_argument('--loop_duration', '-l', type=float, default=5.0, help='Length of the video loop used for syncing') 
    parse.add_argument('--data_sub_sample_rate', '-r', type=float, default=60.0, help='Subsample rate in Hz for CSV data') 
    args = parse.parse_args() 
    ############################################################### # This is an optional add on that allows the user to find files 
    ############################################################### 
    # if args.video_path is None: 
    #     args.video_path = eg.fileopenbox("Find Video Path") 
    # print("Video Path: ", args.video_path) 
    # if args.csv_path is None: 
    #     args.csv_path = eg.fileopenbox("Find CSV Data Path") 
    # print("CSV Path: ", args.csv_path) 
    # if args.sync_header is None: 
    #     headers = get_csv_headers(args.csv_path) 
    #     args.sync_header = eg.choicebox("Choose Header to Sync", "Which Header?", headers) 
    # print("CSV Sync header: ", args.sync_header) 

    app = QApplication(sys.argv)

    #Debug: csv_path = "C:/Users/thela/OneDrive/Documents/CSV_Correlate/force/log00-04.csv"
    #Debug: sync_header = 'Leg 0 Z'
    #Debug: data_sub_sample_rate = 60
    #Debug: video_path = "C:/Users/thela/OneDrive/Documents/CSV_Correlate/video/Rigid2sand2rigid.mp4"
    #Debug: loop_duration = 5

    csv_process = csvProcess(args.csv_path, args.sync_header, args.data_sub_sample_rate)
    csv_process.copyForceForces()
    csv_process.copyForceTime()
    csv_process.stepChop()
    # 12120 is the frame of the breaking


    video_gui = videoGui(args.video_path, csv_process, args.loop_duration)

    main_window = video_gui.mainWindow(csv_process, video_gui)
    
    main_window.show()

    sys.exit(app.exec())
    #input_frame = 3000

if __name__ == "__main__":
    main()