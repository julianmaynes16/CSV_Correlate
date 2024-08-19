from csvProcess import *
from videoGui import *
import argparse

def main():
    #make this a keyword arg
    #fileStatus()
    #csvAlter(show_plot = False)
    app = QApplication(sys.argv)

    csv_process = csvProcess("C:/Users/thela/OneDrive/Documents/CSV_Correlate/force/log00-04.csv",leg_number = 0, data_frequency = 1, subsample_rate = 60, show_plot = False)
    csv_process.copyForceForces()
    csv_process.copyForceTime()
    csv_process.stepChop()
    # 12120 is the frame of the breaking
    video_gui = videoGui(csv_process, video_fps = 15, input_frame = 0, seconds_before_loop = 5)

    main_window = video_gui.mainWindow(csv_process, video_gui)
    
    main_window.show()

    sys.exit(app.exec())
    #input_frame = 3000

if __name__ == "__main__":
    main()