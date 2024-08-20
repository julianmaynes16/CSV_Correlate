from csvProcess import *
from videoGui import *
import easygui as eg
import argparse

def main():

    def get_csv_headers(csv_path, header_row = 0):

        """Return just the CSV headers in list Args: csv_path (str): path to a csv file header_row (int, optional): Row where header is and data starts. Allows for and ignores non-standard header rows. Defaults to 0. Returns: List(str): list of column headers in csv at header_row """ 
        with open(csv_path,'r') as f: 
            for _ in range(header_row): 
                f.readline() 
            headers = f.readline().split(',') 
            return headers
            #reader = csv.reader(f)
            #headers = next(reader)
            #return headers
    def headerToIndex(csv_path, header_string, header_row = 0):
        row_index = 0
        with open(csv_path,'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if(row_index == header_row):
                    headers = row
                row_index += 1
            #headers = next(reader)
        header_index = 0
        for header in headers:
            if(header == header_string):
                return header_index
            header_index += 1
        return header_index
        
    
    # def get_csv_num_data_rows(csv_path, header_row = 0): 
    #     """Return number of data rows in a csv file by reading whole file. May be expensive for large files. Args: csv_path (str): path to a csv file header_row (int, optional): Row where header is and data starts. Allows for and ignores non-standard header rows. Defaults to 0. Returns: int: Number of data rows after header """
    #     with open(csv_path,'r') as f:
    #         count = 0 
    #         for _ in f: 
    #             count += 1 
    #         return count - (header_row + 1)
    
    parse = argparse.ArgumentParser("Video Synchronizing GUI. Used to get the time offset in seconds between a video and a data series from a csv. USE QUOTES AROUND STRINGS.\n")
    parse.add_argument('--video_path', '-v', type=str, default=None, help='Path to video to be synced') 
    parse.add_argument('--csv_path', '-c', type=str, default=None, help='Path to CSV to be synced') 
    parse.add_argument('--sync_header', '-s', type=str, default=None, help='CSV column header for syncing signal') 
    parse.add_argument('--header_row', '-d', type=int, default=None, help = 'Row where the data headers in the CSV can be found')
    parse.add_argument('--loop_duration', '-l', type=float, default=5.0, help='Length of the video loop used for syncing') 
    parse.add_argument('--data_sub_sample_rate', '-r', type=float, default=60.0, help='Subsample rate in Hz for CSV data')
    
    args = parse.parse_args() 
    ############################################################### # This is an optional add on that allows the user to find files 
    ############################################################### 
    if args.video_path is None: 
        args.video_path = eg.fileopenbox("Find Video Path") 
    print("Video Path: ", args.video_path) 

    if args.header_row is None:
        args.header_row = eg.integerbox("Enter Header CSV Row")
    print("Header Row: ", args.header_row)

    if args.csv_path is None: 
        args.csv_path = eg.fileopenbox("Find CSV Data Path") 
    print("CSV Path: ", args.csv_path) 

    
    headers = get_csv_headers(args.csv_path, args.header_row)
    if args.sync_header is None:  
        args.sync_header = eg.choicebox("Choose Header to Sync", "Which Header?", headers)
        
    header_name = args.sync_header
    args.sync_header = headers.index(args.sync_header)

    print("CSV Sync header: ", header_name, " Column: ", args.sync_header) 
    app = QApplication(sys.argv)


    #Debug: csv_path = "C:/Users/thela/OneDrive/Documents/CSV_Correlate/force/log00-04.csv"
    #Debug: sync_header = 'Leg 0 Z'
    #Debug: data_sub_sample_rate = 60
    #Debug: video_path = "C:/Users/thela/OneDrive/Documents/CSV_Correlate/video/Rigid2sand2rigid.mp4"
    #Debug: loop_duration = 5

    #csv_process = csvProcess(args.csv_path, headerToIndex(args.csv_path, args.sync_header, args.header_row), args.data_sub_sample_rate, args.header_row)
    csv_process = csvProcess(args.csv_path, args.sync_header, args.data_sub_sample_rate, args.header_row)
    csv_process.copyForceForces()
    csv_process.copyForceTime()
    csv_process.stepChop()
    # 12120 is the frame of the breaking


    video_gui = videoGui(args.video_path, csv_process, header_name, args.loop_duration)

    main_window = video_gui.mainWindow(csv_process, video_gui)
    
    main_window.show()

    sys.exit(app.exec())
    #input_frame = 3000

if __name__ == "__main__":
    main()