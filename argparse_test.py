import argparse 
# Used to parse args import easygui as eg # Used to get files if not specified ############################################################# 
# # Helper functions ############################################################# 

def get_csv_headers(csv_path, header_row = 0): 
    """Return just the CSV headers in list Args: csv_path (str): path to a csv file header_row (int, optional): Row where header is and data starts. Allows for and ignores non-standard header rows. Defaults to 0. Returns: List(str): list of column headers in csv at header_row """ 
    with open(csv_path,'r') as f: 
        for _ in range(header_row): 
            f.readline() 
            headers = f.readline().split(',') 
            return headers 
def get_csv_num_data_rows(csv_path, header_row = 0): 
    """Return number of data rows in a csv file by reading whole file. May be expensive for large files. Args: csv_path (str): path to a csv file header_row (int, optional): Row where header is and data starts. Allows for and ignores non-standard header rows. Defaults to 0. Returns: int: Number of data rows after header  """ 
    with open(csv_path,'r') as f: 
        count = 0 
        for _ in f: 
            count += 1 
            return count - (header_row + 1) 
        ############################################################### # This should go in your main function or in a argument parsing
        #  # function that then goes in your main function ############################################################### 
parse = argparse.ArgumentParser("Video Synchronizing GUI. Used to get the time offset in seconds between a video and a data series from a csv. USE QUOTES AROUND STRINGS.\n")
parse.add_argument('--video_path', '-v', type=str, default=None, help='Path to video to be synced') 
parse.add_argument('--csv_path', '-c', type=str, default=None, help='Path to CSV to be synced') 
parse.add_argument('--sync_header', '-s', type=str, default=None, help='CSV column header for syncing signal') 
parse.add_argument('--loop_duration', '-l', type=float, default=5.0, help='Length of the video loop used for syncing') 
parse.add_argument('--data_sub_sample_rate', '-r', type=float, default=60.0, help='Subsample rate in Hz for CSV data') 
args = parse.parse_args() 
############################################################### # This is an optional add on that allows the user to find files 
############################################################### 
if args.video_path is None: 
    args.video_path = eg.fileopenbox("Find Video Path") 
print("Video Path: ", args.video_path) 
if args.csv_path is None: 
    args.csv_path = eg.fileopenbox("Find CSV Data Path") 
print("CSV Path: ", args.csv_path) 
if args.sync_header is None: 
    headers = get_csv_headers(args.csv_path) 
    args.sync_header = eg.choicebox("Choose Header to Sync", "Which Header?", headers) 
print("CSV Sync header: ", args.sync_header) 
                    
###############################################################
