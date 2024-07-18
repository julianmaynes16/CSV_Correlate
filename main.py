from csv_correlate import *

def main():
    fileStatus()
    force_start = findStartForce()
    print(force_start)
    mocap_start = findStartMocap()
    print(mocap_start)
    verifyPlot(0,0)

if __name__ == "__main__":
    main()