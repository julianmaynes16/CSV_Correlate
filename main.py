from csvProcess import *
from videoGui import *

def main():
    #make this a keyword arg
    #fileStatus()
    #csvAlter(show_plot = False)
    app = QApplication(sys.argv)

    csv_process = csvProcess(leg_number = 0, data_frequency = 1, truncated_fps = 60, show_plot = False)
    csv_process.copyForceForces()
    csv_process.copyForceTime()

    video_gui = videoGui(csv_process, video_fps = 15, input_frame = 12120, seconds_before_loop = 5)

    main_window = video_gui.mainWindow(csv_process, video_gui)
    
    main_window.show()

    sys.exit(app.exec())
    #input_frame = 3000

if __name__ == "__main__":
    main()