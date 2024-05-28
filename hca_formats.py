from datetime import datetime

date_format = '%Y/%m/%d'
time_format = '%.1f'
study_name = "Vehicle_Wakes"
profile_name = "WD30_S2_x=235_y=-480--420"
filename_directory = "C:\\Users\\FMF\\Documents\\Studies\\" + study_name + "\\HCA\\"
filename_mc = str(profile_name) + ".mc"
filename_sc = str(profile_name) + ".sc"
filename_dr = str(profile_name) + ".dr"


# -- returns current epoch time as a formatted string
def get_time():
    epoch_time = time_format % datetime.timestamp(datetime.now())
    return epoch_time


# -- returns current date as a formatted string
def get_date():
    log_date = datetime.today().strftime(date_format)
    return log_date
