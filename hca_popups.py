# TODO: Change all entry fields to pull from hca_storage file (entry_stored)
# TODO: Use last calibration toggles
# TODO: Automatically assign C1 Axis and C2 Axis based on Profile Axis input (always XYZ, YZX, or ZXY)
# TODO: [CLEANUP] Use for loops to make multiple widgets
import csv

import customtkinter as ctk  # library: create modern looking user interfaces in python with tkinter
# from hca_gui import GUI
import hca_formats
import hca_ini
import numpy as np
import os  # module: portable way of using operating system dependent functionality
import random
from threading import *
import tkinter as tk  # library: standard Python interface to the Tcl/Tk GUI toolkit
from tkinter import filedialog  # module: provides classes and functions for creating file/directory selection windows


# default themes for the program
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# - global variables and arrays
# -- hca.ini file for variable storage
hca_dict = hca_ini.hca_dict
# print(hca_dict)

# -- default values
hca_channels = 6  # number of active HCA channels
# com_hca = 'Dev2/ai0:' + (str(hca_channels - 1))
max_volts = 5  # volts
min_volts = -5  # volts
sample_rate_hz = 20  # 20Hz, or 20 samples per second
sample_rate_s = 0.05  # 20Hz in seconds (1/20Hz)
sample_rate_ms = 50  # 20Hz in milliseconds (1/20Hz * 1000)
sample_avg_time = 1  # seconds
sample_time = 120  # seconds
calibration_time = 20  # seconds
max_count_out = 100


# - Create popup window for profile setup
class SetupWindow(ctk.CTkToplevel):
    switch_change_profile_state = None

    def __init__(self):
        super().__init__()

        self.title("Profile Setup")
        self.geometry("698x696")
        self.resizable(False, False)

        global hca_dict

        # -- create frame for "Profile Setup" window
        self.frame_setup = ctk.CTkFrame(self)
        self.frame_setup.grid(row=16, column=6, padx=5, pady=(0, 5), sticky="nsew")

        # -- create widgets for "Setup Profile" window
        self.label_title_study_name = ctk.CTkLabel(self.frame_setup, text="Study & Profile Names",
                                                   font=ctk.CTkFont(weight="bold"))
        self.label_study_name = ctk.CTkLabel(self.frame_setup, text="Study Name:")
        self.study_name = tk.StringVar()
        self.study_name.set(hca_dict['Study Name'])
        self.entry_study_name = ctk.CTkEntry(self.frame_setup, width=200, textvariable=self.study_name)
        self.label_profile_name = ctk.CTkLabel(self.frame_setup, text="Profile Name:")
        self.profile_name = tk.StringVar()
        self.profile_name.set(hca_dict['Profile Name'])
        self.entry_profile_name = ctk.CTkEntry(self.frame_setup, width=200, textvariable=self.profile_name)

        self.label_title_study_config = ctk.CTkLabel(self.frame_setup, text="Study & Profile Configurations",
                                                     font=ctk.CTkFont(weight="bold"))
        self.label_sample_rate = ctk.CTkLabel(self.frame_setup, text="Sample Rate (Hz):")
        self.sample_rate = tk.IntVar()
        self.sample_rate.set(hca_dict['Sample Rate (Hz)'])
        self.entry_sample_rate = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.sample_rate)
        self.label_sample_duration = ctk.CTkLabel(self.frame_setup, text="Sample Duration (s):")
        self.sample_duration = tk.IntVar()
        self.sample_duration.set(hca_dict['Sample Duration (s)'])
        self.entry_sample_duration = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.sample_duration)
        self.label_sample_channels = ctk.CTkLabel(self.frame_setup, text="Sample Channels (#):")
        self.sample_channels = tk.IntVar()
        self.sample_channels.set(hca_dict['Sample Channels (#)'])
        self.entry_sample_channels = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.sample_channels)
        self.label_profile_axis = ctk.CTkLabel(self.frame_setup, text="Profile Axis:")
        self.profile_axis = tk.StringVar()
        self.profile_axis.set(hca_dict['Profile Axis (X/Y/Z)'])
        self.entry_profile_axis = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.profile_axis)
        self.label_axis_2 = ctk.CTkLabel(self.frame_setup, text="Coordinate Axis 2:")
        self.axis_2 = tk.StringVar()
        self.axis_2.set(hca_dict['Axis 2 (X/Y/Z)'])
        self.entry_axis_2 = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.axis_2)
        self.label_axis_3 = ctk.CTkLabel(self.frame_setup, text="Coordinate Axis 3:")
        self.axis_3 = tk.StringVar()
        self.axis_3.set(hca_dict['Axis 3 (X/Y/Z)'])
        self.entry_axis_3 = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.axis_3)
        self.label_rake_origin_pos = ctk.CTkLabel(self.frame_setup, text="Rake Origin Position (mm):")
        self.rake_origin_pos = tk.IntVar()
        self.rake_origin_pos.set(hca_dict['Rake Origin Position (mm)'])
        self.entry_rake_origin_pos = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.rake_origin_pos)
        self.label_rake_offset = ctk.CTkLabel(self.frame_setup, text="Rake Offset (mm):")
        self.rake_offset = tk.IntVar()
        self.rake_offset.set(hca_dict['Rake Offset (mm)'])
        self.entry_rake_offset = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.rake_offset)
        self.label_model_scale = ctk.CTkLabel(self.frame_setup, text="Model Scale (ratio, #:1):")
        self.model_scale = tk.IntVar()
        self.model_scale.set(hca_dict['Model Scale (#:1)'])
        self.entry_model_scale = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.model_scale)
        self.label_length_scale_1 = ctk.CTkLabel(self.frame_setup, text="Length Scale 1 (mm):")
        self.length_scale_1 = tk.IntVar()
        self.length_scale_1.set(hca_dict['Length Scale 1 (mm)'])
        self.entry_length_scale_1 = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.length_scale_1)
        self.label_length_scale_2 = ctk.CTkLabel(self.frame_setup, text="Length Scale 2 (mm):")
        self.length_scale_2 = tk.IntVar()
        self.length_scale_2.set(hca_dict['Length Scale 2 (mm)'])
        self.entry_length_scale_2 = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.length_scale_2)
        self.label_height_scale = ctk.CTkLabel(self.frame_setup, text="Characteristic H (mm):")
        self.height_scale = tk.IntVar()
        self.height_scale.set(hca_dict['Characteristic Height H (mm)'])
        self.entry_height_scale = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.height_scale)
        self.label_wind_speed = ctk.CTkLabel(self.frame_setup, text="Target Wind Speed (m/s):")
        self.wind_speed = tk.DoubleVar()
        self.wind_speed.set(hca_dict['WT Target Wind Speed (m/s)'])
        self.entry_wind_speed = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.wind_speed)
        self.label_norm_wind_speed = ctk.CTkLabel(self.frame_setup, text="Norm. Wind Speed (m/s):")
        self.norm_wind_speed = tk.DoubleVar()
        self.norm_wind_speed.set(hca_dict['Normalized Wind Speed (m/s)'])
        self.entry_norm_wind_speed = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.norm_wind_speed)
        self.label_source_rate = ctk.CTkLabel(self.frame_setup, text="Source Rate (g/min):")
        self.source_rate = tk.DoubleVar()
        self.source_rate.set(hca_dict['Source Rate (g/min)'])
        self.entry_source_rate = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.source_rate)
        self.label_zero_conc = ctk.CTkLabel(self.frame_setup, text="Zero Conc. (g/m3):")
        self.zero_conc = tk.DoubleVar()
        self.zero_conc.set(hca_dict['Zero Concentration (g/m3)'])
        self.entry_zero_conc = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.zero_conc)
        self.label_span_conc = ctk.CTkLabel(self.frame_setup, text="Span Conc. (g/m3):")
        self.span_conc = tk.DoubleVar()
        self.span_conc.set(hca_dict['Span Concentration (g/m3)'])
        self.entry_span_conc = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.span_conc)
        self.label_title_hca_config = ctk.CTkLabel(self.frame_setup, text="HCA Assignments",
                                                   font=ctk.CTkFont(weight="bold"))
        self.label_hca_1_id = ctk.CTkLabel(self.frame_setup, text="HCA #1 ID (#):")
        self.hca_1_id = tk.IntVar()
        self.hca_1_id.set(hca_dict['HCA#1 ID (#)'])
        self.entry_hca_1_id = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.hca_1_id)
        self.label_hca_2_id = ctk.CTkLabel(self.frame_setup, text="HCA #2 ID (#):")
        self.hca_2_id = tk.IntVar()
        self.hca_2_id.set(hca_dict['HCA#2 ID (#)'])
        self.entry_hca_2_id = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.hca_2_id)
        self.label_hca_3_id = ctk.CTkLabel(self.frame_setup, text="HCA #3 ID (#):")
        self.hca_3_id = tk.IntVar()
        self.hca_3_id.set(hca_dict['HCA#3 ID (#)'])
        self.entry_hca_3_id = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.hca_3_id)
        self.label_hca_4_id = ctk.CTkLabel(self.frame_setup, text="HCA #4 ID (#):")
        self.hca_4_id = tk.IntVar()
        self.hca_4_id.set(hca_dict['HCA#4 ID (#)'])
        self.entry_hca_4_id = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.hca_4_id)
        self.label_hca_5_id = ctk.CTkLabel(self.frame_setup, text="HCA #5 ID (#):")
        self.hca_5_id = tk.IntVar()
        self.hca_5_id.set(hca_dict['HCA#5 ID (#)'])
        self.entry_hca_5_id = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.hca_5_id)
        self.label_hca_6_id = ctk.CTkLabel(self.frame_setup, text="HCA #6 ID (#):")
        self.hca_6_id = tk.IntVar()
        self.hca_6_id.set(hca_dict['HCA#6 ID (#)'])
        self.entry_hca_6_id = ctk.CTkEntry(self.frame_setup, width=50, textvariable=self.hca_6_id)
        self.label_title_file_config = ctk.CTkLabel(self.frame_setup, text="File Configurations",
                                                    font=ctk.CTkFont(weight="bold"))
        self.label_data_filepath = ctk.CTkLabel(self.frame_setup, text="Data Filepath:")
        self.data_filepath = tk.StringVar()
        self.data_filepath.set(hca_dict['Profile Data Filepath (Full Path)'])
        self.entry_data_filepath = ctk.CTkEntry(self.frame_setup, width=300, state='disabled',
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.data_filepath)
        self.label_profile_filenames = ctk.CTkLabel(self.frame_setup, text="Profile Filenames:")
        self.mc_filename = tk.StringVar()
        self.mc_filename.set(hca_dict['Profile Raw Data File (Filename)'])
        self.sc_filename = tk.StringVar()
        self.sc_filename.set(hca_dict['Profile Calibration File (Filename)'])
        self.dr_filename = tk.StringVar()
        self.dr_filename.set(hca_dict['Profile Data Report File (Filename)'])
        self.profile_filenames = tk.StringVar()
        self.profile_filenames.set(self.mc_filename.get() + ", " + self.sc_filename.get() + ", " +
                                   self.dr_filename.get())
        self.entry_profile_filenames = ctk.CTkEntry(self.frame_setup, width=300, state='disabled',
                                                    font=ctk.CTkFont(slant="italic"),
                                                    textvariable=self.profile_filenames)
        self.label_cal_file = ctk.CTkLabel(self.frame_setup, text="Calibration File (.txt):")
        self.cal_file = tk.StringVar()
        self.cal_file.set(hca_dict['Full Calibration File (Filename)'])
        self.entry_cal_file = ctk.CTkEntry(self.frame_setup, width=300, state='disabled',
                                           font=ctk.CTkFont(slant="italic"), textvariable=self.cal_file)

        self.button_accept_profile = ctk.CTkButton(self.frame_setup, text='Accept Changes', fg_color="OliveDrab4",
                                                   hover_color="dark olive green",
                                                   command=lambda: accept_setup())
        self.button_recall_profile = ctk.CTkButton(self.frame_setup, text='Recall Stored',
                                                   command=lambda: recall_setup())
        self.button_close_profile = ctk.CTkButton(self.frame_setup, text='Close Window',
                                                  fg_color="red3", hover_color="red4",
                                                  command=lambda: discard_setup())
        self.button_update_filepath = ctk.CTkButton(self.frame_setup, text='Select', width=25,
                                                    command=lambda: choose_file_directory(self.data_filepath))
        self.button_update_profile = ctk.CTkButton(self.frame_setup, text='Update', width=25,
                                                   command=lambda: update_filenames(self.profile_name, self.mc_filename,
                                                                                    self.sc_filename, self.dr_filename,
                                                                                    self.profile_filenames))
        self.button_select_cal = ctk.CTkButton(self.frame_setup, text='Select', width=25,
                                               command=lambda: choose_file(self.cal_file))

        # positions
        self.label_title_study_name.grid(row=0, column=0, columnspan=7, padx=(10, 0), pady=(10, 0), sticky="s")
        self.label_study_name.grid(row=1, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_study_name.grid(row=1, column=1, columnspan=2, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_profile_name.grid(row=1, column=3, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_profile_name.grid(row=1, column=4, columnspan=2, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_title_study_config.grid(row=2, column=0, columnspan=7, padx=(10, 0), pady=(15, 0), sticky="s")
        self.label_sample_rate.grid(row=3, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sample_rate.grid(row=3, column=1, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_sample_duration.grid(row=3, column=2, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sample_duration.grid(row=3, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_sample_channels.grid(row=3, column=4, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sample_channels.grid(row=3, column=5, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_profile_axis.grid(row=4, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_profile_axis.grid(row=4, column=1, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_axis_2.grid(row=4, column=2, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_axis_2.grid(row=4, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_axis_3.grid(row=4, column=4, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_axis_3.grid(row=4, column=5, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_rake_origin_pos.grid(row=5, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_rake_origin_pos.grid(row=5, column=1, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_rake_offset.grid(row=5, column=2, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_rake_offset.grid(row=5, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_model_scale.grid(row=5, column=4, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_model_scale.grid(row=5, column=5, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_length_scale_1.grid(row=6, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_length_scale_1.grid(row=6, column=1, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_length_scale_2.grid(row=6, column=2, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_length_scale_2.grid(row=6, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_height_scale.grid(row=6, column=4, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_height_scale.grid(row=6, column=5, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_wind_speed.grid(row=7, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_wind_speed.grid(row=7, column=1, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_norm_wind_speed.grid(row=7, column=2, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_norm_wind_speed.grid(row=7, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_source_rate.grid(row=8, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_source_rate.grid(row=8, column=1, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_zero_conc.grid(row=8, column=2, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_zero_conc.grid(row=8, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_span_conc.grid(row=8, column=4, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_span_conc.grid(row=8, column=5, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_title_hca_config.grid(row=9, column=0, columnspan=7, padx=(10, 0), pady=(15, 0), sticky="s")
        self.label_hca_1_id.grid(row=10, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_hca_1_id.grid(row=10, column=1, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_hca_2_id.grid(row=10, column=2, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_hca_2_id.grid(row=10, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_hca_3_id.grid(row=10, column=4, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_hca_3_id.grid(row=10, column=5, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_hca_4_id.grid(row=11, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_hca_4_id.grid(row=11, column=1, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_hca_5_id.grid(row=11, column=2, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_hca_5_id.grid(row=11, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_hca_6_id.grid(row=11, column=4, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_hca_6_id.grid(row=11, column=5, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.label_title_file_config.grid(row=12, column=0, columnspan=7, padx=(10, 0), pady=(15, 0), sticky="s")
        self.label_data_filepath.grid(row=13, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_data_filepath.grid(row=13, column=1, columnspan=4, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.button_update_filepath.grid(row=13, column=5, padx=(0, 25), pady=(10, 0), sticky="nsew")
        self.label_profile_filenames.grid(row=14, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_profile_filenames.grid(row=14, column=1, columnspan=4, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.button_update_profile.grid(row=14, column=5, padx=(0, 25), pady=(10, 0), sticky="nsew")
        self.label_cal_file.grid(row=15, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_cal_file.grid(row=15, column=1, columnspan=4, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.button_select_cal.grid(row=15, column=5, padx=(0, 25), pady=(10, 0), sticky="nsew")
        self.button_accept_profile.grid(row=16, column=0, columnspan=2, padx=10, pady=20, sticky="e")
        self.button_recall_profile.grid(row=16, column=2, columnspan=2, padx=50, pady=20, sticky="nsew")
        self.button_close_profile.grid(row=16, column=4, columnspan=2, padx=10, pady=20, sticky="w")

        # saves current user entries to hca.ini file
        def accept_setup():
            global hca_dict
            hca_dict |= {'Study Name': self.entry_study_name.get()}
            hca_dict |= {'Profile Name': self.entry_profile_name.get()}
            hca_dict |= {'Sample Rate (Hz) Name': self.entry_sample_rate.get()}
            hca_dict |= {'Sample Duration (s)': self.entry_sample_duration.get()}
            hca_dict |= {'Sample Channels (#)': self.entry_sample_channels.get()}
            hca_dict |= {'Profile Axis (X, Y, Z)': self.entry_profile_axis.get()}
            hca_dict |= {'Axis 2 (X, Y, Z)': self.entry_axis_2.get()}
            hca_dict |= {'Axis 3 (X, Y, Z)': self.entry_axis_3.get()}
            hca_dict |= {'Rake Origin Position (mm)': self.entry_rake_origin_pos.get()}
            hca_dict |= {'Rake Offset (mm)': self.entry_rake_offset.get()}
            hca_dict |= {'Model Scale (#:1)': self.entry_model_scale.get()}
            hca_dict |= {'Length Scale 1 (mm)': self.entry_length_scale_1.get()}
            hca_dict |= {'Length Scale 2 (mm)': self.entry_length_scale_2.get()}
            hca_dict |= {'Characteristic Height H (mm)': self.entry_height_scale.get()}
            hca_dict |= {'WT Target Wind Speed (m/s)': self.entry_wind_speed.get()}
            hca_dict |= {'Normalized Wind Speed (m/s)': self.entry_norm_wind_speed.get()}
            hca_dict |= {'Source Rate (g/min)': self.entry_source_rate.get()}
            hca_dict |= {'Zero Concentration (g/m3)': self.entry_zero_conc.get()}
            hca_dict |= {'Span Concentration (g/m3)': self.entry_span_conc.get()}
            hca_dict |= {'HCA#1 ID (#)': self.entry_hca_1_id.get()}
            hca_dict |= {'HCA#2 ID (#)': self.entry_hca_2_id.get()}
            hca_dict |= {'HCA#3 ID (#)': self.entry_hca_3_id.get()}
            hca_dict |= {'HCA#4 ID (#)': self.entry_hca_4_id.get()}
            hca_dict |= {'HCA#5 ID (#)': self.entry_hca_5_id.get()}
            hca_dict |= {'HCA#6 ID (#)': self.entry_hca_6_id.get()}
            hca_dict |= {'Profile Data Filepath (Full Path)': self.entry_data_filepath.get()}
            hca_dict |= {'Profile Raw Data File (Filename)': self.mc_filename.get()}
            hca_dict |= {'Profile Calibration File (Filename)': self.sc_filename.get()}
            hca_dict |= {'Profile Data Report File (Filename)': self.dr_filename.get()}
            hca_dict |= {'Full Calibration File (Filename)': self.entry_cal_file.get()}
            hca_ini.ini_generate()
            print("Setup saved!")

        # used to recall last saved settings from hca.ini file
        def recall_setup():
            global hca_dict
            self.study_name.set(hca_dict['Study Name'])
            self.profile_name.set(hca_dict['Profile Name'])
            self.sample_rate.set(hca_dict['Sample Rate (Hz)'])
            self.sample_duration.set(hca_dict['Sample Duration (s)'])
            self.sample_channels.set(hca_dict['Sample Channels (#)'])
            self.profile_axis.set(hca_dict['Profile Axis (X, Y, Z)'])
            self.axis_2.set(hca_dict['Axis 2 (X, Y, Z)'])
            self.axis_3.set(hca_dict['Axis 3 (X, Y, Z)'])
            self.rake_origin_pos.set(hca_dict['Rake Origin Position (mm)'])
            self.rake_offset.set(hca_dict['Rake Offset (mm)'])
            self.model_scale.set(hca_dict['Model Scale (#:1)'])
            self.length_scale_1.set(hca_dict['Length Scale 1 (mm)'])
            self.length_scale_2.set(hca_dict['Length Scale 2 (mm)'])
            self.height_scale.set(hca_dict['Characteristic Height H (mm)'])
            self.wind_speed.set(hca_dict['WT Target Wind Speed (m/s)'])
            self.norm_wind_speed.set(hca_dict['Normalized Wind Speed (m/s)'])
            self.source_rate.set(hca_dict['Source Rate (g/min)'])
            self.zero_conc.set(hca_dict['Zero Concentration (g/m3)'])
            self.span_conc.set(hca_dict['Span Concentration (g/m3)'])
            self.hca_1_id.set(hca_dict['HCA#1 ID (#)'])
            self.hca_2_id.set(hca_dict['HCA#2 ID (#)'])
            self.hca_3_id.set(hca_dict['HCA#3 ID (#)'])
            self.hca_4_id.set(hca_dict['HCA#4 ID (#)'])
            self.hca_5_id.set(hca_dict['HCA#5 ID (#)'])
            self.hca_6_id.set(hca_dict['HCA#6 ID (#)'])
            self.data_filepath.set(hca_dict['Profile Data Filepath (Full Path)'])
            self.mc_filename.set(hca_dict['Profile Raw Data File (Filename)'])
            self.sc_filename.set(hca_dict['Profile Calibration File (Filename)'])
            self.dr_filename.set(hca_dict['Profile Data Report File (Filename)'])
            self.cal_file.set(hca_dict['Full Calibration File (Filename)'])
            hca_ini.ini_generate()
            print("Setup saved!")

        # used to recall last saved settings from hca.ini file
        def discard_setup():
            print("Exiting window!")
            self.destroy()

        # -- used to update .mc, .sc, or .dr data filename
        def update_filenames(profile_name, mc, sc, dr, profile_filenames):
            mc.set(profile_name.get() + ".mc")
            sc.set(profile_name.get() + ".sc")
            dr.set(profile_name.get() + ".dr")
            profile_filenames.set(mc.get() + ", " + sc.get() + ", " + dr.get())

        # used to browse Windows Explorer for file
        def choose_file(selected_file):
            filename = filedialog.askopenfilename(initialdir="C:/", title="Select a File",
                                                  filetypes=(("Text files", "*.txt*"), ("all files", "*.*")))
            selected_file.set(os.path.basename(filename))
            print("Calibration File:", selected_file.get())

        # used to browse Windows Explorer for directory
        def choose_file_directory(selected_directory):
            directory = filedialog.askdirectory(title="Select a Directory")
            selected_directory.set(directory + "/")
            print("File Directory:", selected_directory.get())


# - Create popup window for processing data
class ProcessWindow(ctk.CTkToplevel):
    switch_change_profile_state = None

    def __init__(self):
        super().__init__()

        self.title("Process Data")
        self.geometry("592x253")
        self.resizable(False, False)

        global hca_dict

        # -- create frame for "Process Data" window
        self.frame_process = ctk.CTkFrame(self)
        self.frame_process.grid(row=6, column=4, padx=5, pady=5, sticky="nsew")

        # -- create modules for "Process Data" window
        self.label_hca_ini_file = ctk.CTkLabel(self.frame_process, text="HCA .ini Filename:", anchor="e")
        self.hca_ini_file = tk.StringVar()
        self.hca_ini_file.set("hca.ini")
        self.entry_hca_ini_file = ctk.CTkEntry(self.frame_process, width=200, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.hca_ini_file)
        self.label_mc_filepath = ctk.CTkLabel(self.frame_process, text="Raw Data Filepath (.mc):", anchor="e")
        self.mc_filepath = tk.StringVar()
        self.mc_filepath.set(str(hca_dict['Profile Data Filepath (Full Path)'] +
                                 hca_dict['Profile Raw Data File (Filename)']))
        self.entry_mc_filepath = ctk.CTkEntry(self.frame_process, width=400, textvariable=self.mc_filepath)
        self.label_dr_filepath = ctk.CTkLabel(self.frame_process, text="Data Report Filepath (.dr):",  anchor="e")
        self.dr_filepath = tk.StringVar()
        self.dr_filepath.set(str(hca_dict['Profile Data Filepath (Full Path)'] +
                                 hca_dict['Profile Data Report File (Filename)']))
        self.entry_dr_filepath = ctk.CTkEntry(self.frame_process, width=400, textvariable=self.dr_filepath)
        self.label_process_comment = ctk.CTkLabel(self.frame_process, text="Comment(s):", anchor="e")
        self.process_comment = tk.StringVar()
        self.entry_process_comment = ctk.CTkEntry(self.frame_process, width=400,
                                                  textvariable=self.process_comment)
        self.label_process_axis = ctk.CTkLabel(self.frame_process, text="Profile Axis:", anchor="e")
        self.process_axis = tk.StringVar()
        self.process_axis.set(hca_dict['Profile Axis (X/Y/Z)'])
        self.entry_process_axis = ctk.CTkEntry(self.frame_process, width=30, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.process_axis)

        self.button_accept_process = ctk.CTkButton(self.frame_process, text='Process', fg_color="OliveDrab4",
                                                   hover_color="dark olive green",
                                                   command=lambda: self.process_data())
        self.button_cancel_process = ctk.CTkButton(self.frame_process, text='Cancel and Return', fg_color="red3",
                                                   hover_color="red4", command=self.destroy)

        self.label_hca_ini_file.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_hca_ini_file.grid(row=0, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.label_process_axis.grid(row=0, column=2, padx=(25, 0), pady=(10, 0), sticky="e")
        self.entry_process_axis.grid(row=0, column=3, padx=(10, 25), pady=(10, 0), sticky="w")
        self.label_mc_filepath.grid(row=1, column=0, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_mc_filepath.grid(row=1, column=1, columnspan=3, padx=(15, 10), pady=(10, 0), sticky="nsew")
        self.label_dr_filepath.grid(row=2, column=0, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_dr_filepath.grid(row=2, column=1, columnspan=3, padx=(15, 10), pady=(10, 0), sticky="nsew")
        self.label_process_comment.grid(row=3, column=0, padx=(10, 0), pady=(5, 0), sticky="nsew")
        self.entry_process_comment.grid(row=3, column=1, columnspan=3, padx=(15, 10), pady=(10, 0), sticky="nsew")
        self.button_accept_process.grid(row=4, column=0, columnspan=4, padx=200, pady=(15, 0), sticky="nsew")
        self.button_cancel_process.grid(row=5, column=0, columnspan=4, padx=200, pady=10, sticky="nsew")

    # used to browse Windows Explorer for directory
    @staticmethod
    def process_data():
        print("Data processed!")
        # TODO: take mc file
        # mock_mc_file = ""
        # directory = self.dr_filepath
        # selected_directory.set(directory + "/")
        # print("File Directory:", selected_directory.get())


# - Create popup window to save sample data
class SaveSampleDataWindow(ctk.CTkToplevel):
    switch_change_profile_state = None

    def __init__(self):
        super().__init__()

        self.title("Save Sample Data File")
        self.geometry("410x176")
        self.resizable(False, False)

        # -- create frame for "Save Sample Data to File" window
        self.frame_save_sample_data = ctk.CTkFrame(self)
        self.frame_save_sample_data.grid(row=4, column=2, padx=5, pady=5, sticky="nsew")

        # -- create modules for "Save Sample Data to File" window
        self.label_save_sample_data = ctk.CTkLabel(self.frame_save_sample_data, text="Save Sample Data to File",
                                                   anchor="center")
        self.sample_data_filename = tk.StringVar()
        self.sample_data_filename.set("C:\\Documents\\UWT-Detroit_NU\\HCA\\WD00_S1\\x=235_z=0.mc")
        self.entry_sample_data_filename = ctk.CTkEntry(self.frame_save_sample_data, width=375, state="disabled",
                                                       font=ctk.CTkFont(slant="italic"),
                                                       textvariable=self.sample_data_filename)
        self.button_accept_sample_data = ctk.CTkButton(self.frame_save_sample_data, text='Accept',
                                                       fg_color="OliveDrab4", hover_color="dark olive green",
                                                       command=lambda: self.write_logged_data())
        self.button_discard_sample_data = ctk.CTkButton(self.frame_save_sample_data, text='Discard', fg_color="red3",
                                                        hover_color="red4",
                                                        command=lambda: placeholder_function())

        self.label_save_sample_data.grid(row=0, column=0, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_sample_data_filename.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nsew")
        self.button_accept_sample_data.grid(row=2, column=0, columnspan=2, padx=130, pady=(15, 0), sticky="nsew")
        self.button_discard_sample_data.grid(row=3, column=0, columnspan=2, padx=130, pady=(10, 10), sticky="nsew")

    # write logged data to file
    @staticmethod
    def write_logged_data():
        global hca_channels
        mode = "ZERO"
        span = "1.160000E+1"
        xpos = "235"
        ypos = "-480"
        zpos = "0"
        log_date = str(hca_formats.get_date())
        log_time = str(hca_formats.get_time())
        hca_range = "1"
        raw = "4.169742E-3"
        corr = "4.169742E-3"

        print("Date is: " + log_date + ", Time is: " + log_time)

        list_columns = ["TYPE", "SPAN", "XPOS", "YPOS", "ZPOS", "HCAPOS", "DATE", "TIME", "RANGE", "RAW", "CORR"]
        # hca_mc_columns = np.array(["TYPE", "SPAN", "XPOS", "YPOS", "ZPOS",
        #                            "HCAPOS", "DATE", "TIME", "RANGE", "RAW", "CORR"])
        # hca_mc_log = np.empty((6, 11), dtype=str)  # creates empty array to be used for each data log iteration
        # hca_mc_data = np.empty((0, 12))  # creates empty array to be used for entire mc data file
        # hca_sc_columns = np.array(["TYPE", "DATE", "TIME", "HCAPOS", "RANGE", "%RANGE"])
        # hca_sc_log = np.zeros((6, 6))  # creates empty array to be used for each cal log iteration
        # hca_sc_data = np.empty((0, 6))  # creates empty array to be used for entire sc data file
        print(list_columns)
        for n in range(hca_channels):
            new_list = [mode, span, xpos, ypos, zpos, n+1, log_date, log_time, hca_range, raw, corr]
            list_columns.extend(new_list)
        print(list_columns)
        with open("test_mc_data.mc", 'w', newline='\n') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(list_columns)
        # np.savetxt("test_mc_file", hca_mc_log, fmt='%s', delimiter=',')
        # HCA_1_log = np.array(["ZERO", 0.000000E+0, 235, -480, 0, 1, 9/20/2023,
        # 3.7780756693E+9, 1, 1.352224E-1, 0.000000E+0])


# - Create popup window to save HCA data
# TODO: Is this necessary? Seems like it just chops up flow for no consistently valid reason.
class SaveHCADataWindow(ctk.CTkToplevel):
    switch_change_profile_state = None

    def __init__(self):
        super().__init__()

        self.title("Save HCA Data File")
        self.geometry("410x176")
        self.resizable(False, False)

        # -- create frame for "Save HCA Data to File" window
        self.frame_save_hca_data = ctk.CTkFrame(self)
        self.frame_save_hca_data.grid(row=4, column=2, padx=5, pady=5, sticky="nsew")

        # -- create modules for "Save Sample HCA to File" window
        self.label_save_hca_data = ctk.CTkLabel(self.frame_save_hca_data, text="Save HCA Data to File", anchor="center")
        self.hca_data_filename = tk.StringVar()
        self.hca_data_filename.set("C:\\HCA\\HCAFile.ini")
        self.entry_hca_data_filename = ctk.CTkEntry(self.frame_save_hca_data, width=300, state="disabled",
                                                    font=ctk.CTkFont(slant="italic"),
                                                    textvariable=self.hca_data_filename)
        self.button_accept_hca_data = ctk.CTkButton(self.frame_save_hca_data, text='Accept', fg_color="OliveDrab4",
                                                    hover_color="dark olive green",
                                                    command=lambda: placeholder_function())
        self.button_discard_hca_data = ctk.CTkButton(self.frame_save_hca_data, text='Discard', fg_color="red3",
                                                     hover_color="red4",
                                                     command=lambda: placeholder_function())

        self.label_save_hca_data.grid(row=0, column=0, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_data_filename.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="nsew")
        self.button_accept_hca_data.grid(row=2, column=0, columnspan=2, padx=130, pady=(15, 0), sticky="nsew")
        self.button_discard_hca_data.grid(row=3, column=0, columnspan=2, padx=130, pady=(10, 10), sticky="nsew")


# - Create popup window for confirming sample pressures
# TODO: unnecessary since sample pressures should never change in current config?
class PressuresWindow(ctk.CTkToplevel):

    def __init__(self):
        super().__init__()

        self.title("Confirm Reg. Pressures")
        self.geometry("300x135")
        self.resizable(False, False)

        # -- create frame for "Confirm Regulator Pressures" window
        self.frame_pressure_check = ctk.CTkFrame(self)
        self.frame_pressure_check.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        # -- create modules for "Confirm Regulator Pressures" window
        self.label_pressure_check = ctk.CTkLabel(self.frame_pressure_check,
                                                 text="Did you confirm HCA sample pressures?", anchor="center")
        self.button_pressure_check = ctk.CTkButton(self.frame_pressure_check, text='Acknowledge', fg_color="OliveDrab4",
                                                   hover_color="dark olive green",
                                                   command=lambda: placeholder_function())
        self.button_fix_pressures = ctk.CTkButton(self.frame_pressure_check, text='Cancel and Return', fg_color="red3",
                                                  hover_color="red4", command=self.destroy)

        self.label_pressure_check.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="nsew")
        self.button_pressure_check.grid(row=1, column=0, padx=75, pady=(10, 0), sticky="nsew")
        self.button_fix_pressures.grid(row=2, column=0, padx=75, pady=(10, 10), sticky="nsew")


# - Create popup window for confirming HCA ranges
# TODO: unnecessary since ranges will automatically adjust for calibration modes?
class RangesWindow(ctk.CTkToplevel):

    def __init__(self):
        super().__init__()

        self.title("Confirm HCA Ranges")
        self.geometry("300x135")
        self.resizable(False, False)

        # -- create frame for "Confirm Regulator Pressures" window
        self.frame_check_ranges = ctk.CTkFrame(self)
        self.frame_check_ranges.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

        # -- create modules for "Confirm Regulator Pressures" window
        self.label_check_ranges = ctk.CTkLabel(self.frame_check_ranges, text="Did you confirm HCA ranges?",
                                               anchor="center")
        self.button_acknowledge_ranges = ctk.CTkButton(self.frame_check_ranges, text='Acknowledge',
                                                       fg_color="OliveDrab4", hover_color="dark olive green",
                                                       command=lambda: placeholder_function())
        self.button_fix_ranges = ctk.CTkButton(self.frame_check_ranges, text='Cancel and Return', fg_color="red3",
                                               hover_color="red4", command=self.destroy)

        self.label_check_ranges.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="nsew")
        self.button_acknowledge_ranges.grid(row=1, column=0, padx=75, pady=(10, 0), sticky="nsew")
        self.button_fix_ranges.grid(row=2, column=0, padx=75, pady=(10, 10), sticky="nsew")


# - Create popup window for calibrating
class CalibratingWindow(ctk.CTkToplevel):

    def __init__(self):
        super().__init__()

        self.title("Calibrating...")
        self.geometry("636x323")
        self.resizable(False, False)

        global hca_dict

        # -- create frame for "Calibrating" window
        self.frame_calibrating = ctk.CTkFrame(self)
        self.frame_calibrating.grid(row=15, column=9, padx=5, pady=5, sticky="nsew")

        # -- create modules for "Calibrating" window
        self.label_cal_mode = ctk.CTkLabel(self.frame_calibrating, text="Mode", anchor="e")
        self.cal_mode = tk.StringVar()
        self.cal_mode.set(hca_dict['Acquisition Mode (Zero/Span/Background/Sample)'])
        self.entry_cal_mode = ctk.CTkEntry(self.frame_calibrating, width=85, state="disabled",
                                           font=ctk.CTkFont(slant="italic"), textvariable=self.cal_mode)
        self.label_cal_hca_1 = ctk.CTkLabel(self.frame_calibrating, text="HCA1", anchor="e")
        self.label_cal_hca_2 = ctk.CTkLabel(self.frame_calibrating, text="HCA2", anchor="e")
        self.label_cal_hca_3 = ctk.CTkLabel(self.frame_calibrating, text="HCA3", anchor="e")
        self.label_cal_hca_4 = ctk.CTkLabel(self.frame_calibrating, text="HCA4", anchor="e")
        self.label_cal_hca_5 = ctk.CTkLabel(self.frame_calibrating, text="HCA5", anchor="e")
        self.label_cal_hca_6 = ctk.CTkLabel(self.frame_calibrating, text="HCA6", anchor="e")
        self.label_cal_hca_ranges = ctk.CTkLabel(self.frame_calibrating, text="Range", anchor="e")
        self.cal_hca_1_range = tk.StringVar()
        self.cal_hca_1_range.set(hca_dict['HCA#1 Range (#)'])
        self.entry_cal_hca_1_range = ctk.CTkEntry(self.frame_calibrating, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_1_range)
        self.cal_hca_2_range = tk.StringVar()
        self.cal_hca_2_range.set(hca_dict['HCA#2 Range (#)'])
        self.entry_cal_hca_2_range = ctk.CTkEntry(self.frame_calibrating, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_2_range)
        self.cal_hca_3_range = tk.StringVar()
        self.cal_hca_3_range.set(hca_dict['HCA#3 Range (#)'])
        self.entry_cal_hca_3_range = ctk.CTkEntry(self.frame_calibrating, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_3_range)
        self.cal_hca_4_range = tk.StringVar()
        self.cal_hca_4_range.set(hca_dict['HCA#4 Range (#)'])
        self.entry_cal_hca_4_range = ctk.CTkEntry(self.frame_calibrating, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_4_range)
        self.cal_hca_5_range = tk.StringVar()
        self.cal_hca_5_range.set(hca_dict['HCA#5 Range (#)'])
        self.entry_cal_hca_5_range = ctk.CTkEntry(self.frame_calibrating, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_5_range)
        self.cal_hca_6_range = tk.StringVar()
        self.cal_hca_6_range.set(hca_dict['HCA#6 Range (#)'])
        self.entry_cal_hca_6_range = ctk.CTkEntry(self.frame_calibrating, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_6_range)
        self.label_1_sec_array = ctk.CTkLabel(self.frame_calibrating, text="1 sec. array", anchor="e")
        self.cal_hca_1_1s = tk.StringVar()
        self.cal_hca_1_1s.set(hca_dict['HCA#1 1s Data (% range)'])
        self.entry_cal_hca_1_1s = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_1_1s)
        self.cal_hca_2_1s = tk.StringVar()
        self.cal_hca_2_1s.set(hca_dict['HCA#2 1s Data (% range)'])
        self.entry_cal_hca_2_1s = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_2_1s)
        self.cal_hca_3_1s = tk.StringVar()
        self.cal_hca_3_1s.set(hca_dict['HCA#3 1s Data (% range)'])
        self.entry_cal_hca_3_1s = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_3_1s)
        self.cal_hca_4_1s = tk.StringVar()
        self.cal_hca_4_1s.set(hca_dict['HCA#4 1s Data (% range)'])
        self.entry_cal_hca_4_1s = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_4_1s)
        self.cal_hca_5_1s = tk.StringVar()
        self.cal_hca_5_1s.set(hca_dict['HCA#5 1s Data (% range)'])
        self.entry_cal_hca_5_1s = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_5_1s)
        self.cal_hca_6_1s = tk.StringVar()
        self.cal_hca_6_1s.set(hca_dict['HCA#6 1s Data (% range)'])
        self.entry_cal_hca_6_1s = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_6_1s)
        self.cal_hca_1s_array = np.array([self.cal_hca_1_1s, self.cal_hca_2_1s, self.cal_hca_3_1s,
                                          self.cal_hca_4_1s, self.cal_hca_5_1s, self.cal_hca_6_1s])
        self.label_n_sec_array = ctk.CTkLabel(self.frame_calibrating, text="n sec. array", anchor="e")
        self.cal_hca_1_ns = tk.StringVar()
        self.cal_hca_1_ns.set(hca_dict['HCA#1 ns Data (% range)'])
        self.entry_cal_hca_1_ns = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"),  textvariable=self.cal_hca_1_ns)
        self.cal_hca_2_ns = tk.StringVar()
        self.cal_hca_2_ns.set(hca_dict['HCA#2 ns Data (% range)'])
        self.entry_cal_hca_2_ns = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_2_ns)
        self.cal_hca_3_ns = tk.StringVar()
        self.cal_hca_3_ns.set(hca_dict['HCA#3 ns Data (% range)'])
        self.entry_cal_hca_3_ns = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_3_ns)
        self.cal_hca_4_ns = tk.StringVar()
        self.cal_hca_4_ns.set(hca_dict['HCA#4 ns Data (% range)'])
        self.entry_cal_hca_4_ns = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_4_ns)
        self.cal_hca_5_ns = tk.StringVar()
        self.cal_hca_5_ns.set(hca_dict['HCA#5 ns Data (% range)'])
        self.entry_cal_hca_5_ns = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_5_ns)
        self.cal_hca_6_ns = tk.StringVar()
        self.cal_hca_6_ns.set(hca_dict['HCA#6 ns Data (% range)'])
        self.entry_cal_hca_6_ns = ctk.CTkEntry(self.frame_calibrating, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.cal_hca_6_ns)
        self.cal_hca_ns_array = np.array([self.cal_hca_1_ns, self.cal_hca_2_ns, self.cal_hca_3_ns,
                                          self.cal_hca_4_ns, self.cal_hca_5_ns, self.cal_hca_6_ns])
        self.label_target_time = ctk.CTkLabel(self.frame_calibrating, text="Sample Run # sec.", anchor="e")
        self.target_time = tk.StringVar()
        self.target_time.set(hca_dict['Calibration Duration (s)'])
        self.entry_target_time = ctk.CTkEntry(self.frame_calibrating, width=30, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.target_time)
        self.label_elapsed_time = ctk.CTkLabel(self.frame_calibrating, text="Elapsed Time # sec.", anchor="e")
        self.elapsed_time = tk.StringVar()
        self.elapsed_time.set(hca_dict['Calibration Elapsed (s)'])
        self.entry_elapsed_time = ctk.CTkEntry(self.frame_calibrating, width=30, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.elapsed_time)
        self.label_cal_filepath = ctk.CTkLabel(self.frame_calibrating, text="Filepath", anchor="ne")
        self.textbox_cal_filepath = ctk.CTkTextbox(self.frame_calibrating, width=495, height=65)
        # self.textbox_cal_filepath.configure(state="disabled")
        self.textbox_cal_filepath.insert("0.0", str(hca_dict['Profile Data Filepath (Full Path)'] +
                                                    hca_dict['Profile Calibration File (Filename)']))
        self.button_quit_cal = ctk.CTkButton(self.frame_calibrating, text='Quit', fg_color="red3", hover_color="red4",
                                             command=lambda: self.quit_calibration())

        self.label_cal_mode.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_cal_mode.grid(row=0, column=1, columnspan=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.button_quit_cal.grid(row=0, column=4, columnspan=4, padx=(30, 0), pady=(10, 0), sticky="w")
        self.label_cal_hca_1.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_cal_hca_2.grid(row=1, column=2, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_cal_hca_3.grid(row=1, column=3, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_cal_hca_4.grid(row=1, column=4, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_cal_hca_5.grid(row=1, column=5, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_cal_hca_6.grid(row=1, column=6, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_cal_hca_ranges.grid(row=2, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_cal_hca_1_range.grid(row=2, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_2_range.grid(row=2, column=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_3_range.grid(row=2, column=3, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_4_range.grid(row=2, column=4, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_5_range.grid(row=2, column=5, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_6_range.grid(row=2, column=6, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_1_sec_array.grid(row=3, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_cal_hca_1_1s.grid(row=3, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_2_1s.grid(row=3, column=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_3_1s.grid(row=3, column=3, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_4_1s.grid(row=3, column=4, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_5_1s.grid(row=3, column=5, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_6_1s.grid(row=3, column=6, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_n_sec_array.grid(row=4, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_cal_hca_1_ns.grid(row=4, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_2_ns.grid(row=4, column=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_3_ns.grid(row=4, column=3, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_4_ns.grid(row=4, column=4, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_5_ns.grid(row=4, column=5, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_cal_hca_6_ns.grid(row=4, column=6, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_target_time.grid(row=5, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_target_time.grid(row=5, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.label_elapsed_time.grid(row=5, column=2, columnspan=3, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_elapsed_time.grid(row=5, column=5, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_cal_filepath.grid(row=6, column=0, padx=(10, 0), pady=(10, 10), sticky="e")
        self.textbox_cal_filepath.grid(row=6, column=1, columnspan=6, padx=(10, 5), pady=(10, 10), sticky="w")

    # - functions
    # -- reads voltage output from each HCA
    @staticmethod
    def read_voltage():
        return np.array([random.random(), random.random(), random.random(),
                         random.random(), random.random(), random.random()])

    # -- sample loop for sample rate measurements
    def sample_rate_loop(self):
        global sample_rate_hz, sample_rate_ms
        for n in range(sample_rate_hz):
            if n < 1:
                self.cal_hca_ns_array = np.array([1., 1., 1., 1., 1., 1.])  # set up new rolling average array baseline
            else:
                self.cal_hca_1s_array = np.array(self.read_voltage())  # update 1s array
                # update rolling average array
                self.cal_hca_ns_array = np.mean(np.array([self.cal_hca_1s_array, self.cal_hca_ns_array]), axis=0)
                # hca_ini.ini_generate()
        app.after(sample_rate_ms, self.sample_rate_loop)
        hca_1s_v = self.cal_hca_1s_array
        hca_ns_rolling_v = self.cal_hca_ns_array
        return hca_1s_v, hca_ns_rolling_v

    # calibration loop
    def calibration_loop(self):
        global hca_dict
        # populate fields when window opens with last saved values
        time_elapsed = int(hca_dict['Calibration Elapsed (s)'])
        target_time = int(hca_dict['Calibration Duration (s)'])
        hca_1_range = int(hca_dict['HCA#1 Range (#)'])
        hca_2_range = int(hca_dict['HCA#2 Range (#)'])
        hca_3_range = int(hca_dict['HCA#3 Range (#)'])
        hca_4_range = int(hca_dict['HCA#4 Range (#)'])
        hca_5_range = int(hca_dict['HCA#5 Range (#)'])
        hca_6_range = int(hca_dict['HCA#6 Range (#)'])
        hca_1_1s = float(hca_dict['HCA#1 1s Data (% range)'])  # or 0.000000
        hca_2_1s = float(hca_dict['HCA#2 1s Data (% range)'])  # or 0.000000
        hca_3_1s = float(hca_dict['HCA#3 1s Data (% range)'])  # or 0.000000
        hca_4_1s = float(hca_dict['HCA#4 1s Data (% range)'])  # or 0.000000
        hca_5_1s = float(hca_dict['HCA#5 1s Data (% range)'])  # or 0.000000
        hca_6_1s = float(hca_dict['HCA#6 1s Data (% range)'])  # or 0.000000
        hca_1_ns = float(hca_dict['HCA#1 ns Data (% range)'])  # or 0.000000
        hca_2_ns = float(hca_dict['HCA#2 ns Data (% range)'])  # or 0.000000
        hca_3_ns = float(hca_dict['HCA#3 ns Data (% range)'])  # or 0.000000
        hca_4_ns = float(hca_dict['HCA#4 ns Data (% range)'])  # or 0.000000
        hca_5_ns = float(hca_dict['HCA#5 ns Data (% range)'])  # or 0.000000
        hca_6_ns = float(hca_dict['HCA#6 ns Data (% range)'])  # or 0.000000
        if time_elapsed < target_time:
            time_elapsed += 1
            hca_1s_v, hca_ns_rolling_v = self.sample_rate_loop()
            hca_dict |= {'Calibration Elapsed (s)': time_elapsed}
            hca_dict |= {'HCA#1 1s Data (% range)': hca_1s_v[0]}
            hca_dict |= {'HCA#2 1s Data (% range)': hca_1s_v[1]}
            hca_dict |= {'HCA#3 1s Data (% range)': hca_1s_v[2]}
            hca_dict |= {'HCA#4 1s Data (% range)': hca_1s_v[3]}
            hca_dict |= {'HCA#5 1s Data (% range)': hca_1s_v[4]}
            hca_dict |= {'HCA#6 1s Data (% range)': hca_1s_v[5]}
            hca_dict |= {'HCA#1 ns Data (% range)': hca_ns_rolling_v[0]}
            hca_dict |= {'HCA#2 ns Data (% range)': hca_ns_rolling_v[1]}
            hca_dict |= {'HCA#3 ns Data (% range)': hca_ns_rolling_v[2]}
            hca_dict |= {'HCA#4 ns Data (% range)': hca_ns_rolling_v[3]}
            hca_dict |= {'HCA#5 ns Data (% range)': hca_ns_rolling_v[4]}
            hca_dict |= {'HCA#6 ns Data (% range)': hca_ns_rolling_v[5]}
            self.elapsed_time.set(str(time_elapsed))
            self.cal_hca_1_1s.set(str("%.5f" % hca_1_1s))
            self.cal_hca_2_1s.set(str("%.5f" % hca_2_1s))
            self.cal_hca_3_1s.set(str("%.5f" % hca_3_1s))
            self.cal_hca_4_1s.set(str("%.5f" % hca_4_1s))
            self.cal_hca_5_1s.set(str("%.5f" % hca_5_1s))
            self.cal_hca_6_1s.set(str("%.5f" % hca_6_1s))
            self.cal_hca_1_ns.set(str("%.5f" % hca_1_ns))
            self.cal_hca_2_ns.set(str("%.5f" % hca_2_ns))
            self.cal_hca_3_ns.set(str("%.5f" % hca_3_ns))
            self.cal_hca_4_ns.set(str("%.5f" % hca_4_ns))
            self.cal_hca_5_ns.set(str("%.5f" % hca_5_ns))
            self.cal_hca_6_ns.set(str("%.5f" % hca_6_ns))
            self.cal_hca_1_range.set(str(hca_1_range))
            self.cal_hca_2_range.set(str(hca_2_range))
            self.cal_hca_3_range.set(str(hca_3_range))
            self.cal_hca_4_range.set(str(hca_4_range))
            self.cal_hca_5_range.set(str(hca_5_range))
            self.cal_hca_6_range.set(str(hca_6_range))
            hca_ini.ini_generate()
            self.after(1000, self.calibration_loop)
        else:
            self.quit_calibration()

    # -- converts raw voltage output to ppm (output from HCAs is +/-5V)
    @staticmethod
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
    @staticmethod
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

    def quit_calibration(self):
        global hca_dict
        hca_dict |= {'Calibration Elapsed (s)': 0}
        hca_ini.ini_generate()
        # print("Done!")
        self.destroy()

    def calibration_threading(self):
        cal_loop_thread = Thread(target=self.calibration_loop)
        cal_loop_thread.start()


# - Create popup window for sampling
class SamplingWindow(ctk.CTkToplevel):
    switch_change_profile_state = None

    def __init__(self):
        super().__init__()

        self.title("Sampling...")
        self.geometry("638x398")
        self.resizable(False, False)

        global hca_dict

        # -- create frame for "Sampling" window
        self.frame_sampling = ctk.CTkFrame(self)
        self.frame_sampling.grid(row=15, column=9, padx=5, pady=5, sticky="nsew")

        # -- create modules for "Sampling" window
        self.label_sam_mode = ctk.CTkLabel(self.frame_sampling, text="Mode", anchor="e")
        self.sam_mode = tk.StringVar()
        self.sam_mode.set(hca_dict['Acquisition Mode (Zero/Span/Background/Sample)'])
        self.entry_sam_mode = ctk.CTkEntry(self.frame_sampling, width=85, state="disabled",
                                           font=ctk.CTkFont(slant="italic"), textvariable=self.sam_mode)
        self.label_hca_1 = ctk.CTkLabel(self.frame_sampling, text="HCA1", anchor="e")
        self.label_hca_2 = ctk.CTkLabel(self.frame_sampling, text="HCA2", anchor="e")
        self.label_hca_3 = ctk.CTkLabel(self.frame_sampling, text="HCA3", anchor="e")
        self.label_hca_4 = ctk.CTkLabel(self.frame_sampling, text="HCA4", anchor="e")
        self.label_hca_5 = ctk.CTkLabel(self.frame_sampling, text="HCA5", anchor="e")
        self.label_hca_6 = ctk.CTkLabel(self.frame_sampling, text="HCA6", anchor="e")
        self.label_sam_hca_ranges = ctk.CTkLabel(self.frame_sampling, text="Range", anchor="e")
        self.sam_hca_1_range = tk.StringVar()
        self.sam_hca_1_range.set(hca_dict['HCA#1 Range (#)'])
        self.entry_sam_hca_1_range = ctk.CTkEntry(self.frame_sampling, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_1_range)
        self.sam_hca_2_range = tk.StringVar()
        self.sam_hca_2_range.set(hca_dict['HCA#2 Range (#)'])
        self.entry_sam_hca_2_range = ctk.CTkEntry(self.frame_sampling, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_2_range)
        self.sam_hca_3_range = tk.StringVar()
        self.sam_hca_3_range.set(hca_dict['HCA#3 Range (#)'])
        self.entry_sam_hca_3_range = ctk.CTkEntry(self.frame_sampling, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_3_range)
        self.sam_hca_4_range = tk.StringVar()
        self.sam_hca_4_range.set(hca_dict['HCA#4 Range (#)'])
        self.entry_sam_hca_4_range = ctk.CTkEntry(self.frame_sampling, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_4_range)
        self.sam_hca_5_range = tk.StringVar()
        self.sam_hca_5_range.set(hca_dict['HCA#5 Range (#)'])
        self.entry_sam_hca_5_range = ctk.CTkEntry(self.frame_sampling, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_5_range)
        self.sam_hca_6_range = tk.StringVar()
        self.sam_hca_6_range.set(hca_dict['HCA#6 Range (#)'])
        self.entry_sam_hca_6_range = ctk.CTkEntry(self.frame_sampling, width=30, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_6_range)
        self.label_1_sec_array = ctk.CTkLabel(self.frame_sampling, text="1 sec. array", anchor="e")
        self.sam_hca_1_1s = tk.StringVar()
        self.sam_hca_1_1s.set(hca_dict['HCA#1 1s Data (% range)'])
        self.entry_sam_hca_1_1s = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_1_1s)
        self.sam_hca_2_1s = tk.StringVar()
        self.sam_hca_2_1s.set(hca_dict['HCA#2 1s Data (% range)'])
        self.entry_sam_hca_2_1s = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_2_1s)
        self.sam_hca_3_1s = tk.StringVar()
        self.sam_hca_3_1s.set(hca_dict['HCA#3 1s Data (% range)'])
        self.entry_sam_hca_3_1s = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_3_1s)
        self.sam_hca_4_1s = tk.StringVar()
        self.sam_hca_4_1s.set(hca_dict['HCA#4 1s Data (% range)'])
        self.entry_sam_hca_4_1s = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_4_1s)
        self.sam_hca_5_1s = tk.StringVar()
        self.sam_hca_5_1s.set(hca_dict['HCA#5 1s Data (% range)'])
        self.entry_sam_hca_5_1s = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_5_1s)
        self.sam_hca_6_1s = tk.StringVar()
        self.sam_hca_6_1s.set(hca_dict['HCA#6 1s Data (% range)'])
        self.entry_cal_hca_6_1s = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_6_1s)
        self.sam_hca_1s_array = np.array([self.sam_hca_1_1s, self.sam_hca_2_1s, self.sam_hca_3_1s,
                                          self.sam_hca_4_1s, self.sam_hca_5_1s, self.sam_hca_6_1s])
        self.label_n_sec_array = ctk.CTkLabel(self.frame_sampling, text="n sec. array", anchor="e")
        self.sam_hca_1_ns = tk.StringVar()
        self.sam_hca_1_ns.set(hca_dict['HCA#1 ns Data (% range)'])
        self.entry_sam_hca_1_ns = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"),  textvariable=self.sam_hca_1_ns)
        self.sam_hca_2_ns = tk.StringVar()
        self.sam_hca_2_ns.set(hca_dict['HCA#2 ns Data (% range)'])
        self.entry_sam_hca_2_ns = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_2_ns)
        self.sam_hca_3_ns = tk.StringVar()
        self.sam_hca_3_ns.set(hca_dict['HCA#3 ns Data (% range)'])
        self.entry_sam_hca_3_ns = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_3_ns)
        self.sam_hca_4_ns = tk.StringVar()
        self.sam_hca_4_ns.set(hca_dict['HCA#4 ns Data (% range)'])
        self.entry_sam_hca_4_ns = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_4_ns)
        self.sam_hca_5_ns = tk.StringVar()
        self.sam_hca_5_ns.set(hca_dict['HCA#5 ns Data (% range)'])
        self.entry_sam_hca_5_ns = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_5_ns)
        self.sam_hca_6_ns = tk.StringVar()
        self.sam_hca_6_ns.set(hca_dict['HCA#6 ns Data (% range)'])
        self.entry_sam_hca_6_ns = ctk.CTkEntry(self.frame_sampling, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_6_ns)
        self.sam_hca_ns_array = np.array([self.sam_hca_1_ns, self.sam_hca_2_ns, self.sam_hca_3_ns,
                                          self.sam_hca_4_ns, self.sam_hca_5_ns, self.sam_hca_6_ns])
        self.label_sam_count_high = ctk.CTkLabel(self.frame_sampling, text="Out High", anchor="e")
        self.sam_hca_1_high = tk.IntVar()
        self.sam_hca_1_high.set(hca_dict['HCA#1 OB High (#)'])
        self.entry_sam_hca_1_high = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                 font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_1_high)
        self.sam_hca_2_high = tk.IntVar()
        self.sam_hca_2_high.set(hca_dict['HCA#2 OB High (#)'])
        self.entry_sam_hca_2_high = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                 font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_2_high)
        self.sam_hca_3_high = tk.IntVar()
        self.sam_hca_3_high.set(hca_dict['HCA#3 OB High (#)'])
        self.entry_sam_hca_3_high = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                 font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_3_high)
        self.sam_hca_4_high = tk.IntVar()
        self.sam_hca_4_high.set(hca_dict['HCA#4 OB High (#)'])
        self.entry_sam_hca_4_high = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                 font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_4_high)
        self.sam_hca_5_high = tk.IntVar()
        self.sam_hca_5_high.set(hca_dict['HCA#5 OB High (#)'])
        self.entry_sam_hca_5_high = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                 font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_5_high)
        self.sam_hca_6_high = tk.IntVar()
        self.sam_hca_6_high.set(hca_dict['HCA#6 OB High (#)'])
        self.entry_sam_hca_6_high = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                 font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_6_high)
        self.label_sam_count_low = ctk.CTkLabel(self.frame_sampling, text="Out Low", anchor="e")
        self.sam_hca_1_low = tk.IntVar()
        self.sam_hca_1_low.set(hca_dict['HCA#1 OB Low (#)'])
        self.entry_sam_hca_1_low = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_1_low)
        self.sam_hca_2_low = tk.IntVar()
        self.sam_hca_2_low.set(hca_dict['HCA#2 OB Low (#)'])
        self.entry_sam_hca_2_low = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_2_low)
        self.sam_hca_3_low = tk.IntVar()
        self.sam_hca_3_low.set(hca_dict['HCA#3 OB Low (#)'])
        self.entry_sam_hca_3_low = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_3_low)
        self.sam_hca_4_low = tk.IntVar()
        self.sam_hca_4_low.set(hca_dict['HCA#4 OB Low (#)'])
        self.entry_sam_hca_4_low = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_4_low)
        self.sam_hca_5_low = tk.IntVar()
        self.sam_hca_5_low.set(hca_dict['HCA#5 OB Low (#)'])
        self.entry_sam_hca_5_low = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_5_low)
        self.sam_hca_6_low = tk.IntVar()
        self.sam_hca_6_low.set(hca_dict['HCA#6 OB Low (#)'])
        self.entry_sam_hca_6_low = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.sam_hca_6_low)
        self.label_target_time = ctk.CTkLabel(self.frame_sampling, text="Sample Run # sec.:", anchor="e")
        self.target_time = tk.IntVar()
        self.target_time.set(hca_dict['Sample Duration (s)'])
        self.entry_target_time = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.target_time)
        self.label_elapsed_time = ctk.CTkLabel(self.frame_sampling, text="Elapsed Time # sec.:", anchor="e")
        self.elapsed_time = tk.StringVar()
        self.elapsed_time.set(hca_dict['Sample Elapsed (s)'])
        self.entry_elapsed_time = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.elapsed_time)
        self.label_sample_rate = ctk.CTkLabel(self.frame_sampling, text="Sample Rate (Hz):", anchor="e")
        self.sample_rate = tk.IntVar()
        self.sample_rate.set(hca_dict['Sample Rate (Hz)'])
        self.entry_sample_rate = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.sample_rate)
        self.label_span_conc = ctk.CTkLabel(self.frame_sampling, text="Span Conc. (g/m3):", anchor="e")
        self.span_conc = tk.DoubleVar()
        self.span_conc.set(hca_dict['Span Concentration (g/m3)'])
        self.entry_span_conc = ctk.CTkEntry(self.frame_sampling, width=50, state="disabled",
                                            font=ctk.CTkFont(slant="italic"), textvariable=self.span_conc)
        self.label_mc_filepath = ctk.CTkLabel(self.frame_sampling, text="Filepath:", anchor="ne")
        self.textbox_mc_filepath = ctk.CTkTextbox(self.frame_sampling, width=495, height=65)
        # self.textbox_mc_filepath.configure(state="disabled")
        self.textbox_mc_filepath.insert("0.0", str(hca_dict['Profile Data Filepath (Full Path)'] +
                                                   hca_dict['Profile Raw Data File (Filename)']))
        self.button_quit_sam = ctk.CTkButton(self.frame_sampling, text='Quit', fg_color="red3", hover_color="red4",
                                             command=lambda: self.quit_sample())

        self.label_sam_mode.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sam_mode.grid(row=0, column=1, columnspan=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.button_quit_sam.grid(row=0, column=4, columnspan=4, padx=(30, 0), pady=(10, 0), sticky="w")
        self.label_hca_1.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_hca_2.grid(row=1, column=2, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_hca_3.grid(row=1, column=3, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_hca_4.grid(row=1, column=4, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_hca_5.grid(row=1, column=5, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_hca_6.grid(row=1, column=6, padx=(10, 0), pady=(10, 0), sticky="w")
        self.label_sam_hca_ranges.grid(row=2, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sam_hca_1_range.grid(row=2, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_2_range.grid(row=2, column=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_3_range.grid(row=2, column=3, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_4_range.grid(row=2, column=4, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_5_range.grid(row=2, column=5, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_6_range.grid(row=2, column=6, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_n_sec_array.grid(row=3, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sam_hca_1_ns.grid(row=3, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_2_ns.grid(row=3, column=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_3_ns.grid(row=3, column=3, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_4_ns.grid(row=3, column=4, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_5_ns.grid(row=3, column=5, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_6_ns.grid(row=3, column=6, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_sam_count_high.grid(row=4, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sam_hca_1_high.grid(row=4, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_2_high.grid(row=4, column=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_3_high.grid(row=4, column=3, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_4_high.grid(row=4, column=4, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_5_high.grid(row=4, column=5, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_6_high.grid(row=4, column=6, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_sam_count_low.grid(row=5, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sam_hca_1_low.grid(row=5, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_2_low.grid(row=5, column=2, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_3_low.grid(row=5, column=3, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_4_low.grid(row=5, column=4, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_5_low.grid(row=5, column=5, padx=(15, 0), pady=(10, 0), sticky="w")
        self.entry_sam_hca_6_low.grid(row=5, column=6, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_target_time.grid(row=6, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_target_time.grid(row=6, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.label_elapsed_time.grid(row=6, column=2, columnspan=3, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_elapsed_time.grid(row=6, column=5, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_sample_rate.grid(row=7, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_sample_rate.grid(row=7, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.label_span_conc.grid(row=7, column=2, columnspan=3, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_span_conc.grid(row=7, column=5, padx=(10, 5), pady=(10, 0), sticky="w")
        self.label_mc_filepath.grid(row=8, column=0, padx=(10, 0), pady=(10, 10), sticky="e")
        self.textbox_mc_filepath.grid(row=8, column=1, columnspan=6, padx=(10, 5), pady=(10, 10), sticky="w")

    # - functions
    # -- reads voltage output from each HCA
    @staticmethod
    def read_voltage():
        return np.array([random.random(), random.random(), random.random(),
                         random.random(), random.random(), random.random()])

    # -- sample loop for sample rate measurements
    def sample_rate_loop(self):
        global sample_rate_hz, sample_rate_ms
        for n in range(sample_rate_hz):
            if n < 1:
                self.sam_hca_ns_array = np.array([1., 1., 1., 1., 1., 1.])  # set up new rolling average array baseline
            else:
                self.sam_hca_1s_array = np.array(self.read_voltage())  # update 1s array
                # update rolling average array
                self.sam_hca_ns_array = np.mean(np.array([self.sam_hca_1s_array, self.sam_hca_ns_array]), axis=0)
                # hca_ini.ini_generate()
        app.after(sample_rate_ms, self.sample_rate_loop)
        hca_1s_v = self.sam_hca_1s_array
        hca_ns_rolling_v = self.sam_hca_ns_array
        return hca_1s_v, hca_ns_rolling_v

    # sample loop
    def sample_loop(self):
        global hca_dict
        # populate fields when window opens with last saved values
        time_elapsed = int(hca_dict['Sample Elapsed (s)'])
        target_time = int(hca_dict['Sample Duration (s)'])
        hca_1_range = int(hca_dict['HCA#1 Range (#)'])
        hca_2_range = int(hca_dict['HCA#2 Range (#)'])
        hca_3_range = int(hca_dict['HCA#3 Range (#)'])
        hca_4_range = int(hca_dict['HCA#4 Range (#)'])
        hca_5_range = int(hca_dict['HCA#5 Range (#)'])
        hca_6_range = int(hca_dict['HCA#6 Range (#)'])
        hca_1_1s = float(hca_dict['HCA#1 1s Data (% range)'])  # or 0.000000
        hca_2_1s = float(hca_dict['HCA#2 1s Data (% range)'])  # or 0.000000
        hca_3_1s = float(hca_dict['HCA#3 1s Data (% range)'])  # or 0.000000
        hca_4_1s = float(hca_dict['HCA#4 1s Data (% range)'])  # or 0.000000
        hca_5_1s = float(hca_dict['HCA#5 1s Data (% range)'])  # or 0.000000
        hca_6_1s = float(hca_dict['HCA#6 1s Data (% range)'])  # or 0.000000
        hca_1_ns = float(hca_dict['HCA#1 ns Data (% range)'])  # or 0.000000
        hca_2_ns = float(hca_dict['HCA#2 ns Data (% range)'])  # or 0.000000
        hca_3_ns = float(hca_dict['HCA#3 ns Data (% range)'])  # or 0.000000
        hca_4_ns = float(hca_dict['HCA#4 ns Data (% range)'])  # or 0.000000
        hca_5_ns = float(hca_dict['HCA#5 ns Data (% range)'])  # or 0.000000
        hca_6_ns = float(hca_dict['HCA#6 ns Data (% range)'])  # or 0.000000

        if time_elapsed < target_time:
            time_elapsed += 1
            hca_1s_v, hca_ns_rolling_v = self.sample_rate_loop()
            hca_dict |= {'Sample Elapsed (s)': time_elapsed}
            hca_dict |= {'HCA#1 1s Data (% range)': hca_1s_v[0]}
            hca_dict |= {'HCA#2 1s Data (% range)': hca_1s_v[1]}
            hca_dict |= {'HCA#3 1s Data (% range)': hca_1s_v[2]}
            hca_dict |= {'HCA#4 1s Data (% range)': hca_1s_v[3]}
            hca_dict |= {'HCA#5 1s Data (% range)': hca_1s_v[4]}
            hca_dict |= {'HCA#6 1s Data (% range)': hca_1s_v[5]}
            hca_dict |= {'HCA#1 ns Data (% range)': hca_ns_rolling_v[0]}
            hca_dict |= {'HCA#2 ns Data (% range)': hca_ns_rolling_v[1]}
            hca_dict |= {'HCA#3 ns Data (% range)': hca_ns_rolling_v[2]}
            hca_dict |= {'HCA#4 ns Data (% range)': hca_ns_rolling_v[3]}
            hca_dict |= {'HCA#5 ns Data (% range)': hca_ns_rolling_v[4]}
            hca_dict |= {'HCA#6 ns Data (% range)': hca_ns_rolling_v[5]}
            self.elapsed_time.set(str(time_elapsed))
            self.sam_hca_1_1s.set(str("%.5f" % hca_1_1s))
            self.sam_hca_2_1s.set(str("%.5f" % hca_2_1s))
            self.sam_hca_3_1s.set(str("%.5f" % hca_3_1s))
            self.sam_hca_4_1s.set(str("%.5f" % hca_4_1s))
            self.sam_hca_5_1s.set(str("%.5f" % hca_5_1s))
            self.sam_hca_6_1s.set(str("%.5f" % hca_6_1s))
            self.sam_hca_1_ns.set(str("%.5f" % hca_1_ns))
            self.sam_hca_2_ns.set(str("%.5f" % hca_2_ns))
            self.sam_hca_3_ns.set(str("%.5f" % hca_3_ns))
            self.sam_hca_4_ns.set(str("%.5f" % hca_4_ns))
            self.sam_hca_5_ns.set(str("%.5f" % hca_5_ns))
            self.sam_hca_6_ns.set(str("%.5f" % hca_6_ns))
            self.sam_hca_1_range.set(str(hca_1_range))
            self.sam_hca_2_range.set(str(hca_2_range))
            self.sam_hca_3_range.set(str(hca_3_range))
            self.sam_hca_4_range.set(str(hca_4_range))
            self.sam_hca_5_range.set(str(hca_5_range))
            self.sam_hca_6_range.set(str(hca_6_range))
            hca_ini.ini_generate()
            self.after(1000, self.sample_loop)
        else:
            self.quit_sample()

    # -- converts raw voltage output to ppm (output from HCAs is +/-5V)
    @staticmethod
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
    @staticmethod
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

    def quit_sample(self):
        global hca_dict
        hca_dict |= {'Sample Elapsed (s)': 0}
        hca_ini.ini_generate()
        # print("Done!")
        self.destroy()

    def sample_threading(self):
        sam_loop_thread = Thread(target=self.sample_loop)
        sam_loop_thread.start()


# - Create popup window for sample summary/graph
class SummaryWindow(ctk.CTkToplevel):
    switch_change_profile_state = None

    def __init__(self):
        super().__init__()

        self.title("Profile Setup")
        self.geometry("1042x185")
        self.resizable(False, False)

        # -- create frame for "Setup Profile" window
        self.frame_setup = ctk.CTkFrame(self)
        self.frame_setup.grid(row=4, column=4, padx=5, pady=5, sticky="nsew")

        # -- create modules for "Setup Profile" window
        self.label_ini_file = ctk.CTkLabel(self.frame_setup, text="HCA .ini Filename:", anchor="e")
        self.ini_file = tk.StringVar()
        self.ini_file.set("HCAFILE.ini")
        self.entry_ini_file = ctk.CTkEntry(self.frame_setup, width=200, state="disabled",
                                           font=ctk.CTkFont(slant="italic"), textvariable=self.ini_file)
        self.label_mc_filepath = ctk.CTkLabel(self.frame_setup, text="Merged File Path (.mc):", anchor="e")
        self.mc_filepath = tk.StringVar()
        self.mc_filepath.set("C:\\Documents\\UWT-Detroit_NU\\HCA\\WD00_S1\\x=235_z=0.mc")
        self.entry_mc_filepath = ctk.CTkEntry(self.frame_setup, width=850, textvariable=self.mc_filepath)
        self.label_dr_filepath = ctk.CTkLabel(self.frame_setup, text="Data Report File Path (.dr):", anchor="e")
        self.dr_filepath = tk.StringVar()
        self.dr_filepath.set("C:\\Documents\\UWT-Detroit_NU\\HCA\\WD00_S1\\x=235_z=0.dr")
        self.entry_dr_filepath = ctk.CTkEntry(self.frame_setup, width=850, textvariable=self.dr_filepath)
        self.label_process_comment = ctk.CTkLabel(self.frame_setup, text="Comment(s):", anchor="e")
        self.process_comment = tk.StringVar()
        self.entry_process_comment = ctk.CTkEntry(self.frame_setup, width=850, textvariable=self.process_comment)
        self.label_process_axis = ctk.CTkLabel(self.frame_setup, text="Profile Axis:", anchor="e")
        self.process_axis = tk.StringVar()
        self.process_axis.set("Y")
        self.entry_process_axis = ctk.CTkEntry(self.frame_setup, width=30, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.process_axis)
        self.button_accept_profile = ctk.CTkButton(self.frame_setup, text='Process', fg_color="OliveDrab4",
                                                   hover_color="dark olive green",
                                                   command=lambda: placeholder_function())

        self.label_ini_file.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_ini_file.grid(row=0, column=1, padx=(15, 0), pady=(10, 0), sticky="w")
        self.label_process_axis.grid(row=0, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_process_axis.grid(row=0, column=2, padx=(10, 25), pady=(10, 0), sticky="w")
        self.button_accept_profile.grid(row=0, column=2, columnspan=2, padx=100, pady=10, sticky="e")
        self.label_mc_filepath.grid(row=1, column=0, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_mc_filepath.grid(row=1, column=1, columnspan=2, padx=(15, 10), pady=(10, 0), sticky="nsew")
        self.label_dr_filepath.grid(row=2, column=0, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_dr_filepath.grid(row=2, column=1, columnspan=2, padx=(15, 10), pady=(10, 0), sticky="nsew")
        self.label_process_comment.grid(row=3, column=0, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_process_comment.grid(row=3, column=1, columnspan=2, padx=(15, 10), pady=(10, 10), sticky="nsew")


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        # - configure gui
        # -- configure window
        self.title("HCA Controls Popup Windows")
        self.geometry(f"{550}x{248}")
        self.resizable(False, False)

        # default variable configurations
        self.cal_mode = tk.StringVar()
        self.cal_mode.set("-")
        self.setup_window = None
        self.calibrating_window = None
        self.sampling_window = None
        self.process_window = None
        self.save_sample_data_window = None
        self.save_hca_data_window = None
        self.pressure_check_window = None
        self.range_check_window = None
        self.summary_window = None

        # - test widgets
        # -- create frame for test widgets
        self.frame_gui_popup_windows = ctk.CTkFrame(self)
        self.frame_gui_popup_windows.grid(row=0, column=0, rowspan=3, padx=5, pady=5, sticky="nsew")

        # -- test labels
        self.label_logo = ctk.CTkLabel(self.frame_gui_popup_windows, text="Green = Done Yellow = Need? Black = WIP",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.label_appearance = ctk.CTkLabel(self.frame_gui_popup_windows, text="Appearance Mode:", anchor="w")

        # -- test buttons
        self.button_profile_setup = ctk.CTkButton(self.frame_gui_popup_windows, text='Setup',
                                                  # TODO: fix colors when complete
                                                  fg_color="OliveDrab4", hover_color="dark olive green",
                                                  command=lambda: self.open_setup_window())
        # TODO: delete this extra argument being passed?
        # self.button_zero = ctk.CTkButton(self.frame_gui_popup_windows, text='Zero',
        #                                  # hover_color="DarkSlateGrey", fg_color="cyan4",
        #                                  fg_color="black",
        #                                  command=lambda: (self.open_calibrating_window("Zero"),
        #                                                   CalibratingWindow.calibration_threading))
        self.button_zero = ctk.CTkButton(self.frame_gui_popup_windows, text='Zero',
                                         # hover_color="DarkSlateGrey", fg_color="cyan4",
                                         fg_color="black",  # TODO: fix colors when complete
                                         command=lambda: (self.open_calibrating_window("Zero")))
        self.button_span = ctk.CTkButton(self.frame_gui_popup_windows, text='Span',
                                         # hover_color="DarkSlateGrey", fg_color="cyan4",
                                         fg_color="black",  # TODO: fix colors when complete
                                         command=lambda: (self.open_calibrating_window("Span")))
        self.button_background = ctk.CTkButton(self.frame_gui_popup_windows, text='Background',
                                               # fg_color="cyan4", hover_color="DarkSlateGrey",
                                               fg_color="black",  # TODO: fix colors when complete
                                               command=lambda: (self.open_calibrating_window("Background")))
        self.button_start_run = ctk.CTkButton(self.frame_gui_popup_windows, text='Start Sample Run',
                                              # fg_color="OliveDrab4", hover_color="dark olive green",
                                              fg_color="black",  # TODO: fix colors when complete
                                              command=lambda: self.open_sampling_window())
        self.button_process_data = ctk.CTkButton(self.frame_gui_popup_windows, text='Process Data',
                                                 fg_color="black",  # TODO: fix colors when complete
                                                 command=lambda: self.open_process_window())
        # TODO: Buttons below are temporary button access, part of process in another window
        self.button_save_sample_data = ctk.CTkButton(self.frame_gui_popup_windows, text='Save Sample Data',
                                                     fg_color="black",  # TODO: fix colors when complete
                                                     command=lambda: self.open_save_sample_data_window())
        self.button_save_hca_data = ctk.CTkButton(self.frame_gui_popup_windows, text='Save HCA Data',
                                                  fg_color="goldenrod3", hover_color="goldenrod4",
                                                  command=lambda: self.open_save_hca_data_window())
        self.button_check_pressures = ctk.CTkButton(self.frame_gui_popup_windows, text='Check Pressures',
                                                    fg_color="goldenrod3", hover_color="goldenrod4",
                                                    command=lambda: self.open_pressure_check_window())
        self.button_check_ranges = ctk.CTkButton(self.frame_gui_popup_windows, text='Check Ranges',
                                                 fg_color="goldenrod3", hover_color="goldenrod4",
                                                 command=lambda: self.open_range_check_window())
        self.button_summary = ctk.CTkButton(self.frame_gui_popup_windows, text='Sample Summary',
                                            # fg_color="goldenrod3", hover_color="goldenrod4",
                                            fg_color="black",  # TODO: fix colors when complete
                                            command=lambda: self.open_summary_window())
        self.button_close_window = ctk.CTkButton(self.frame_gui_popup_windows, text='Close',
                                                 # hover_color="red4", fg_color="red3",
                                                 fg_color="OliveDrab4", hover_color="dark olive green",
                                                 command=self.destroy)
        self.button_main_window = ctk.CTkButton(self.frame_gui_popup_windows, text='Main GUI',
                                                # fg_color="OliveDrab4", hover_color="dark olive green",
                                                fg_color="black",  # TODO: fix colors when complete
                                                command=lambda: placeholder_function())

        # -- test menus
        self.menu_appearance = ctk.CTkOptionMenu(self.frame_gui_popup_windows, values=["Light", "Dark", "System"],
                                                 command=self.change_appearance_mode_event)

        # -- test widget positioning
        self.label_logo.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # --- column 0 positioning
        self.button_profile_setup.grid(row=1, column=0, padx=20, pady=(0, 10))
        self.button_zero.grid(row=2, column=0, padx=20, pady=(0, 10))
        self.button_span.grid(row=3, column=0, padx=20, pady=(0, 10))
        self.button_background.grid(row=4, column=0, padx=20, pady=(0, 10))
        self.button_start_run.grid(row=5, column=0, padx=20, pady=(0, 10))

        # --- column 1 positioning
        self.button_process_data.grid(row=1, column=1, padx=20, pady=(0, 10))
        self.button_save_sample_data.grid(row=2, column=1, padx=20, pady=(0, 10))
        self.button_save_hca_data.grid(row=3, column=1, padx=20, pady=(0, 10))
        self.button_check_pressures.grid(row=4, column=1, padx=20, pady=(0, 10))
        self.button_check_ranges.grid(row=5, column=1, padx=20, pady=(0, 10))

        # --- column 2 positioning
        self.button_summary.grid(row=1, column=2, padx=20, pady=(0, 10))
        self.button_close_window.grid(row=2, column=2, padx=20, pady=(0, 10))
        self.label_appearance.grid(row=3, column=2, padx=20, pady=(0, 10))
        self.menu_appearance.grid(row=4, column=2, padx=20, pady=(0, 10))
        self.button_main_window.grid(row=5, column=2, padx=20, pady=(0, 10))

        # - program theme default values
        self.menu_appearance.set("System")
        # self.menu_scaling.set("100%")

    # - functions
    # -- change overall appearance of program to light, dark, or system (default)
    @staticmethod
    def change_appearance_mode_event(new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    # -- change overall scaling of program
    @staticmethod
    def change_scaling_event(new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    # -- opens setup window
    def open_setup_window(self):
        if self.setup_window is None or not self.setup_window.winfo_exists():
            self.setup_window = SetupWindow()  # create window if its None or destroyed
            # self.button_setup.configure(text="Logging!")
        else:
            self.setup_window.focus()  # if window exists focus it

    # -- opens calibrating window
    def open_calibrating_window(self, mode):
        global hca_dict
        if self.calibrating_window is None or not self.calibrating_window.winfo_exists():
            hca_dict |= {'Acquisition Mode (Zero/Span/Background/Sample)': mode}
            # GUI.update_ranges(self, mode)  # TODO: auto assign range based on mode
            self.calibrating_window = CalibratingWindow()  # create window if its None or destroyed
            self.calibrating_window.calibration_loop()
            # self.button_calibrating.configure(text="Logging!")
        else:
            self.calibrating_window.focus()  # if window exists focus it

    # -- opens sample running window
    def open_sampling_window(self):
        global hca_dict
        if self.sampling_window is None or not self.sampling_window.winfo_exists():
            hca_dict |= {'Acquisition Mode (Zero/Span/Background/Sample)': "Sampling"}
            self.sampling_window = SamplingWindow()  # create window if its None or destroyed
            self.sampling_window.sample_loop()
            # self.button_sampling.configure(text="Logging!")
        else:
            self.sampling_window.focus()  # if window exists focus it

    # -- opens process data window
    def open_process_window(self):
        if self.process_window is None or not self.process_window.winfo_exists():
            self.process_window = ProcessWindow()  # create window if its None or destroyed
            # self.button_process_data.configure(text="Logging!")
        else:
            self.process_window.focus()  # if window exists focus it

    # -- opens save data window
    def open_save_sample_data_window(self):
        if self.save_sample_data_window is None or not self.save_sample_data_window.winfo_exists():
            self.save_sample_data_window = SaveSampleDataWindow()  # create window if its None or destroyed
            # self.button_save_sample_data.configure(text="Logging!")
        else:
            self.save_sample_data_window.focus()  # if window exists focus it

    # -- opens save HCA window
    def open_save_hca_data_window(self):
        if self.save_hca_data_window is None or not self.save_hca_data_window.winfo_exists():
            self.save_hca_data_window = SaveHCADataWindow()  # create window if its None or destroyed
            # self.button_save_hca_data.configure(text="Logging!")
        else:
            self.save_hca_data_window.focus()  # if window exists focus it

    # -- opens pressure check window
    def open_pressure_check_window(self):
        if self.pressure_check_window is None or not self.pressure_check_window.winfo_exists():
            self.pressure_check_window = PressuresWindow()  # create window if its None or destroyed
            # self.button_pressure_check.configure(text="Logging!")
        else:
            self.pressure_check_window.focus()  # if window exists focus it

    # -- opens range check window
    def open_range_check_window(self):
        if self.range_check_window is None or not self.range_check_window.winfo_exists():
            self.range_check_window = RangesWindow()  # create window if its None or destroyed
            # self.button_check_ranges.configure(text="Logging!")
        else:
            self.range_check_window.focus()  # if window exists focus it

    # -- opens sample summary window
    def open_summary_window(self):
        if self.summary_window is None or not self.summary_window.winfo_exists():
            self.summary_window = SummaryWindow()  # create window if its None or destroyed
            # self.button_calibrating.configure(text="Logging!")
        else:
            self.summary_window.focus()  # if window exists focus it


# - placeholder function for temp purposes
def placeholder_function():
    print("Button works!")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
