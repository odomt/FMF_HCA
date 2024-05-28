import nidaqmx  # library: used to interface with NI hardware
from nidaqmx.constants import TerminalConfiguration  # library: used to interface with NI hardware
import numpy as np  # library: used for working with arrays
import time  # module: provides various time-related functions


# - hardware configurations
# -- i/o name assignments
com_hca = 'Dev2/ai0:5'

# - global variables and arrays
# -- default values
hca_channels = 6  # number of active HCA channels
# com_hca = 'Dev2/ai0:' + (str(hca_channels - 1))
max_volts = 5  # volts
min_volts = -5  # volts
sample_rate_hz = 20  # 20Hz, or 20 samples per second
sample_rate_s = 0.05  # seconds, or 50 milliseconds, or 1/20Hz
sample_avg_time = 1  # seconds
sample_time = 120  # seconds
calibration_time = 20  # seconds
max_count_out = 100

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

# - assigns HCAs to NI i/o hardware ports
# 0V to 5V is the default
# task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, \
# samps_per_chan=sample_time)
hca_task = nidaqmx.Task()
hca_task.ai_channels.add_ai_voltage_chan(com_hca, terminal_config=TerminalConfiguration.DIFF,
                                         min_val=min_volts, max_val=max_volts)


# - functions
# -- reads voltage output from each HCA
def read_voltage():
    hca_task.start()
    hca_20hz_v_data = np.array(hca_task.read())
    # sample_rate_task.stop()
    # sample_rate_task.close()
    return hca_20hz_v_data


# -- sample loop for sample rate measurements
def sample_rate_loop():
    hca_1s_v_data = np.zeros((sample_rate_hz, hca_channels))
    for n in range(sample_rate_hz):
        hca_1s_v_data[n] = read_voltage()
        time.sleep(sample_rate_s)
        # TODO: update GUI/stored(?) variable
    hca_1s_data_avg = np.average(hca_1s_v_data, axis=0)
    return hca_1s_data_avg


# -- sample loop for calibration point measurements
def calibration_loop():
    # global hca_1_data_cal, hca_2_data_cal, hca_3_data_cal, hca_4_data_cal, hca_5_data_cal, hca_6_data_cal
    hca_cal_data = np.empty((0, 6))
    for n in range(calibration_time):
        iteration_reading = sample_rate_loop()
        hca_cal_data = np.append(iteration_reading)
        time.sleep(sample_avg_time)
        # TODO: update GUI/stored(?) variable
    # hca_cal_data_avg = np.average(hca_cal_data)
    return hca_cal_data


# -- sample loop for sample point measurements
def sample_loop():
    # global hca_1_data_sam, hca_2_data_sam, hca_3_data_sam, hca_4_data_sam, hca_5_data_sam, hca_6_data_sam
    hca_sam_data = np.empty((0, 6))
    for n in range(sample_time):
        iteration_reading = sample_rate_loop()
        hca_sam_data = np.append(iteration_reading)
        time.sleep(sample_avg_time)
        # TODO: update GUI/stored(?) variable
    # hca_sam_data_avg = np.average(hca_sam_data)
    return hca_sam_data


# -- converts raw voltage output to ppm (output from HCAs is +/-5V)
def array_to_concentration(hca_range, hca_array):
    # LabVIEW: C_hca = %Range * Range Factor ... Range Factor = 1, 2.5, 10, 25, 100, 250, 1000
    # Python: C_hca = (V_read / V_span) * (Range Factor) ... Range Factor = 10, 25, 100, 250, 1000, 2500, 10000
    if hca_range == 1:
        concentration_max = 10
    elif hca_range == 2:
        concentration_max = 25
    elif hca_range == 3:
        concentration_max = 100
    elif hca_range == 4:
        concentration_max = 250
    elif hca_range == 5:
        concentration_max = 1000
    elif hca_range == 6:
        concentration_max = 2500
    elif hca_range == 7:
        concentration_max = 10000
    else:
        print("Error!")
        concentration_max = 0
    hca_1_conc = (hca_array[0] * concentration_max) / max_volts
    hca_2_conc = (hca_array[1] * concentration_max) / max_volts
    hca_3_conc = (hca_array[2] * concentration_max) / max_volts
    hca_4_conc = (hca_array[3] * concentration_max) / max_volts
    hca_5_conc = (hca_array[4] * concentration_max) / max_volts
    hca_6_conc = (hca_array[5] * concentration_max) / max_volts
    hca_conc = np.array([hca_1_conc, hca_2_conc, hca_3_conc, hca_4_conc, hca_5_conc, hca_6_conc])
    return hca_conc


# -- converts raw voltage output to percent of measured range (output from HCAs is +/-5 VDC)
def array_to_pct_range(hca_array):
    # LabVIEW: C_hca = %Range * Range Factor ... Range Factor = 1, 2.5, 10, 25, 100, 250, 1000
    # Python: C_hca = (V_read / V_span) * (Range Factor) ... Range Factor = 10, 25, 100, 250, 1000, 2500, 1000
    hca_pct_range = np.zeros((1, 6))
    hca_pct_range[0, 0] = (hca_array[0] / max_volts) * 100
    hca_pct_range[0, 1] = (hca_array[1] / max_volts) * 100
    hca_pct_range[0, 2] = (hca_array[2] / max_volts) * 100
    hca_pct_range[0, 3] = (hca_array[3] / max_volts) * 100
    hca_pct_range[0, 4] = (hca_array[4] / max_volts) * 100
    hca_pct_range[0, 5] = (hca_array[5] / max_volts) * 100
    return hca_pct_range


# -- write array to data file
def write_to_file(filetype, array):
    mc_format = '%s, %.6e, %i, %i, %i, %i, %s, %.10e, %i, %.6e'
    sc_format = '%s, %s, %s, %i, %i, %.6f'
    hca_mc_columns_str = hca_mc_columns.tostring()
    hca_sc_columns_str = hca_sc_columns.tostring()
    if filetype == "mc":
        # %s for string, %e for exp, %f for float, default is %.18e - separate by comma for each column within string
        np.savetxt(".mc", array, delimiter=',', header=hca_mc_columns_str, fmt=mc_format)
    elif filetype == "sc":
        # %s for string, %e for exp, %f for float, default is %.18e - separate by comma for each column within string
        np.savetxt(".sc", array, delimiter=',', header=hca_sc_columns_str, fmt=sc_format)
    else:
        print("File type error!")


def close_task(task_name):
    task_name.stop()
    task_name.close()
