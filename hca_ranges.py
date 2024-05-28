import nidaqmx  # library: used to interface with NI hardware
from nidaqmx.constants import LineGrouping  # library: used to interface with NI hardware
import numpy as np  # library: used for working with arrays
import hca_data


# - hardware configurations
# -- i/o name assignments
com_ranges = 'Dev1/port'
hca_1_port = 'port0'
hca_2_port = 'port1'
hca_3_port = 'port2'
hca_4_port = 'port3'
hca_5_port = 'port4'
hca_6_port = 'port5'

# -- range NI i/o hardware line arrays
range_1 = np.array([False, True, True, True, True, True, True, True], dtype=bool)  # line 0
range_2 = np.array([True, False, True, True, True, True, True, True], dtype=bool)  # line 1
range_3 = np.array([True, True, False, True, True, True, True, True], dtype=bool)  # line 2
range_4 = np.array([True, True, True, False, True, True, True, True], dtype=bool)  # line 3
range_5 = np.array([True, True, True, True, False, True, True, True], dtype=bool)  # line 4
range_6 = np.array([True, True, True, True, True, False, True, True], dtype=bool)  # line 5
range_7 = np.array([True, True, True, True, True, True, False, True], dtype=bool)  # line 6
range_remote = np.array([True, True, True, True, True, True, True, False], dtype=bool)  # line 7 (necessary?)
# range_1 = [False, True, True, True, True, True, True, True]  # line 0
# range_2 = [True, False, True, True, True, True, True, True]  # line 1
# range_3 = [True, True, False, True, True, True, True, True]  # line 2
# range_4 = [True, True, True, False, True, True, True, True]  # line 3
# range_5 = [True, True, True, True, False, True, True, True]  # line 4
# range_6 = [True, True, True, True, True, False, True, True]  # line 5
# range_7 = [True, True, True, True, True, True, False, True]  # line 6
# range_remote = [True, True, True, True, True, True, True, False]  # line 7 (necessary?)


# - functions
# -- toggles on/off auto ranging based on concentration
def switch_event_auto_range(self):
    print("Switch toggled, current value:", self.switch_auto_range_state.get())


# -- initialize HCAs to "Range 0" for remote control
def init_remote_ranges():
    for i in range(5):
        task = nidaqmx.Task()
        port = str(i)
        task.do_channels.add_do_chan(com_ranges + port + '/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
        task.start()
        task.write(range_1)
        task.stop()
        task.close()


# -- assign port arrays to HCAs
def select_range_port(hca):
    if hca == 1:
        return hca_1_port
    elif hca == 2:
        return hca_2_port
    elif hca == 3:
        return hca_3_port
    elif hca == 4:
        return hca_4_port
    elif hca == 5:
        return hca_5_port
    elif hca == 6:
        return hca_6_port
    else:
        print("HCA error!")


# -- assign range arrays to HCAs
def select_range_setting(setting):
    if setting == 1:
        return range_1  # binary bit value 254
    elif setting == 2:
        return range_2  # binary bit value 253
    elif setting == 3:
        return range_3  # binary bit value 251
    elif setting == 4:
        return range_4  # binary bit value 247
    elif setting == 5:
        return range_5  # binary bit value 239
    elif setting == 6:
        return range_6  # binary bit value 223
    elif setting == 7:
        return range_7  # binary bit value 191
    # elif setting == 0:
    #     return range_remote  # binary bit value 127
    else:
        print("Range setting error!")


# -- set range for each HCA
def set_single_range(hca, setting):
    task = nidaqmx.Task()  # create task
    port = select_range_port(hca)  # assign port to task
    range_setting = select_range_setting(setting)  # assign range to task
    task.do_channels.add_do_chan('Dev1/' + port + '/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
    task.start()
    task.write(range_setting)
    task.stop()
    task.close()

# # -- set current HCA ranges to specified ranges
# def update_ranges(setting):
#     global hca_dict
#     if setting == "New":
#         self.range_1_stored.set(int(self.entry_new_range_1.get()))  # HCA1 range variable updated
#         self.range_2_stored.set(int(self.entry_new_range_2.get()))  # HCA2 range variable updated
#         self.range_3_stored.set(int(self.entry_new_range_3.get()))  # HCA3 range variable updated
#         self.range_4_stored.set(int(self.entry_new_range_4.get()))  # HCA4 range variable updated
#         self.range_5_stored.set(int(self.entry_new_range_5.get()))  # HCA5 range variable updated
#         self.range_6_stored.set(int(self.entry_new_range_6.get()))  # HCA6 range variable updated
#         hca_ranges.set_single_range(1, int(self.entry_new_range_1.get()))  # HCA1 to new range
#         hca_ranges.set_single_range(2, int(self.entry_new_range_2.get()))  # HCA2 to new range
#         hca_ranges.set_single_range(3, int(self.entry_new_range_3.get()))  # HCA3 to new range
#         hca_ranges.set_single_range(4, int(self.entry_new_range_4.get()))  # HCA4 to new range
#         hca_ranges.set_single_range(5, int(self.entry_new_range_5.get()))  # HCA5 to new range
#         hca_ranges.set_single_range(6, int(self.entry_new_range_6.get()))  # HCA6 to new range
#     elif setting == "Zero":
#         self.range_1_stored.set(1)  # HCA1 range variable updated
#         self.range_2_stored.set(1)  # HCA2 range variable updated
#         self.range_3_stored.set(1)  # HCA3 range variable updated
#         self.range_4_stored.set(1)  # HCA4 range variable updated
#         self.range_5_stored.set(1)  # HCA5 range variable updated
#         self.range_6_stored.set(1)  # HCA6 range variable updated
#         hca_ranges.set_single_range(1, 1)  # HCA1 to zero range
#         hca_ranges.set_single_range(2, 1)  # HCA2 to zero range
#         hca_ranges.set_single_range(3, 1)  # HCA3 to zero range
#         hca_ranges.set_single_range(4, 1)  # HCA4 to zero range
#         hca_ranges.set_single_range(5, 1)  # HCA5 to zero range
#         hca_ranges.set_single_range(6, 1)  # HCA6 to zero range
#     elif setting == "Span":
#         self.range_1_stored.set(7)  # HCA1 range variable updated
#         self.range_2_stored.set(7)  # HCA2 range variable updated
#         self.range_3_stored.set(7)  # HCA3 range variable updated
#         self.range_4_stored.set(7)  # HCA4 range variable updated
#         self.range_5_stored.set(7)  # HCA5 range variable updated
#         self.range_6_stored.set(7)  # HCA6 range variable updated
#         hca_ranges.set_single_range(1, 7)  # HCA1 to span range
#         hca_ranges.set_single_range(2, 7)  # HCA2 to span range
#         hca_ranges.set_single_range(3, 7)  # HCA3 to span range
#         hca_ranges.set_single_range(4, 7)  # HCA4 to span range
#         hca_ranges.set_single_range(5, 7)  # HCA5 to span range
#         hca_ranges.set_single_range(6, 7)  # HCA6 to span range
#     else:
#         print("Range setting error!")
#     hca_dict |= {'HCA#1 Range (#)': self.range_1_stored.get()}  # HCA1 range database variable updated
#     hca_dict |= {'HCA#2 Range (#)': self.range_2_stored.get()}  # HCA2 range database variable updated
#     hca_dict |= {'HCA#3 Range (#)': self.range_3_stored.get()}  # HCA3 range database variable updated
#     hca_dict |= {'HCA#4 Range (#)': self.range_4_stored.get()}  # HCA4 range database variable updated
#     hca_dict |= {'HCA#5 Range (#)': self.range_5_stored.get()}  # HCA5 range database variable updated
#     hca_dict |= {'HCA#6 Range (#)': self.range_6_stored.get()}  # HCA6 range database variable updated
#     self.range_1.configure(text=str(self.range_1_stored.get()))  # HCA1 displayed value updated
#     self.range_2.configure(text=str(self.range_2_stored.get()))  # HCA2 displayed value updated
#     self.range_3.configure(text=str(self.range_3_stored.get()))  # HCA3 displayed value updated
#     self.range_4.configure(text=str(self.range_4_stored.get()))  # HCA4 displayed value updated
#     self.range_5.configure(text=str(self.range_5_stored.get()))  # HCA5 displayed value updated
#     self.range_6.configure(text=str(self.range_6_stored.get()))  # HCA6 displayed value updated
#     hca_ini.ini_generate()  # update database


# TODO: set provision to not switch ranges down when on Range 1 or up when on Range 7
# -- switch range to higher or lower setting when readings are outside of range for consecutive counts
def range_reset():
    if hca_data.max_count_out > 100:
        print("Resetting range!")
        # switch range
        # reset count
