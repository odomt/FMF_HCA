import csv  # module: implements classes to read and write tabular data in CSV format
import numpy as np  # library: used for working with arrays
from numpy import genfromtxt as gft

# -- data file array setup
hca_mc_columns = np.array(["TYPE", "SPAN", "XPOS", "YPOS", "ZPOS", "HCAPOS", "DATE", "TIME", "RANGE", "RAW", "CORR"])
hca_mc_log = np.zeros((6, 12))  # creates empty array to be used for each data log iteration
hca_mc_data = np.empty((0, 12))  # creates empty array to be used for entire mc data file
hca_sc_columns = np.array(["TYPE", "DATE", "TIME", "HCAPOS", "RANGE", "%RANGE"])
hca_sc_log = np.zeros((6, 6))  # creates empty array to be used for each cal log iteration
hca_sc_data = np.empty((0, 6))  # creates empty array to be used for entire sc data file
hca_dr_header = np.array(["Study Name: ", "Profile Name: ", "Sample Rate (Hz): ", "Sample Time (s): ",
                          "Active Channels: ", "HCA IDs: ", "Profile Axis: ", "Coord. Axis 1: ", "Coord. Axis 2: ",
                          "Length Scale 1 (mm): ", "Length Scale 2 (mm): ", "Norm. Wind Speed (m/s): ",
                          "Source Rate (g/min): ", "Char. Height (mm): ", "WT Tach. (m/s): ", "Scale (ratio): ",
                          "Merged File: ", "Stream File: ", "Calibration File: ", "Comment: "])
np.vstack(hca_dr_header)  # TODO: or create row array and add to empty array?
hca_dr_columns = np.array(["TYPE", "SPAN", "XPOS", "YPOS", "ZPOS", "HCAPOS", "DATE", "TIME", "RANGE", "RAW", "CORR",
                           "XPOS/H", "YPOS/H", "ZPOS/H", "CHI"])
hca_dr_log = np.zeros((6, 15))  # creates empty array to be used for each cal log iteration
hca_dr_data = np.empty((0, 15))  # creates empty array to be used for entire sc data file
profile_name = ""
mc_filename = profile_name + ".mc"
sc_filename = profile_name + ".sc"
dr_filename = profile_name = ".dr"

# - sample data files
data_sam_full = gft('hca_sam_full.csv', delimiter=',')
data_cal_full = gft('hca_cal_full.csv', delimiter=',')
data_20hz_full = gft('hca_20hz_full.csv', delimiter=',')
data_20hz_single = gft('hca_20hz_single.csv', delimiter=',')
mc_format = '%s, %.6e, %i, %i, %i, %i, %s, %.10e, %i, %.6e'
sc_format = '%s, %s, %s, %i, %i, %.6f'
hca_mc_columns_str = hca_mc_columns.tostring()
hca_sc_columns_str = hca_sc_columns.tostring()

# ini writing setup
hca_storage_reader = csv.reader(open('hca.ini', 'r'))
hca_dict = {}
for hca_storage_row in hca_storage_reader:
    k, v = hca_storage_row
    hca_dict[k] = v


# -- updates hca ini file
def ini_generate():
    with open('hca.ini', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in hca_dict.items():
            writer.writerow([key, value])


# -- recalls saved hca ini settings from file
def ini_recall():
    with open("hca.ini", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            print(','.join(row))


# -- write array to data file
def write_to_file(filetype, array):
    global mc_format, sc_format, hca_mc_columns_str, hca_sc_columns_str
    if filetype == "mc":
        # %s for string, %e for exp, %f for float, default is %.18e - separate by comma for each column within string
        np.savetxt(".mc", array, delimiter=',', header=hca_mc_columns_str, fmt=mc_format)
    elif filetype == "sc":
        # %s for string, %e for exp, %f for float, default is %.18e - separate by comma for each column within string
        np.savetxt(".sc", array, delimiter=',', header=hca_sc_columns_str, fmt=sc_format)
    else:
        print("File type error!")
