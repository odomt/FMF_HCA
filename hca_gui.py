# TODO: add calibration time to setup window?
# TODO: zsb calibration functions
# TODO: sample run function
# TODO: process data function
# TODO: change position process: verify stored positions are updated when change position function is used
# TODO: live sample and concentration data updates: verify communication, update main GUI with data values
# TODO: csv manipulation?
# TODO: throw out bad data function: discard calibration or sample run, quit in the middle and discard
# TODO: profile calibrations should not use adjusted offset and position coordinates
# TODO: create "default" study/profile configuration that can be restored on command in setup window
# TODO: execute "recall stored" button to pull in last saved setup on command in setup window
# TODO: set all digital out channels to true in remote mode
# TODO: auto-range setting changes to digital in (read)?
# TODO: [CLEANUP] use for loops to make multiple widgets
import customtkinter as ctk  # library: create modern looking user interfaces in python with tkinter
# import hca_data
import hca_ini
import hca_popups
import hca_ranges
import nidaqmx  # library: used to interface with NI hardware
# from nidaqmx.constants import LineGrouping  # library: used to interface with NI hardware
# from nidaqmx.constants import TerminalConfiguration  # library: used to interface with NI hardware
import numpy  # library: used for working with arrays
from threading import *  # module:  constructs higher-level threading interfaces on top of the lower level (tkinter)
import tkinter as tk  # library: standard Python interface to the Tcl/Tk GUI toolkit


# default themes for the program
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


COM_ranges = 'Dev1'
COM_voltages = 'Dev2'
range_init = numpy.array([True, True, True, True, True, True, True, True], dtype=bool)
range_remote = numpy.array([False, True, True, True, True, True, True, True], dtype=bool)  # necessary?
range_1 = numpy.array([True, True, True, True, True, True, True, False], dtype=bool)
range_2 = numpy.array([True, True, True, True, True, True, False, True], dtype=bool)
range_3 = numpy.array([True, True, True, True, True, False, True, True], dtype=bool)
range_4 = numpy.array([True, True, True, True, False, True, True, True], dtype=bool)
range_5 = numpy.array([True, True, True, False, True, True, True, True], dtype=bool)
range_6 = numpy.array([True, True, False, True, True, True, True, True], dtype=bool)
range_7 = numpy.array([True, False, True, True, True, True, True, True], dtype=bool)
hca_dict = hca_ini.hca_dict


def set_rake_position():
    print("Button works!")


class GUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        global hca_dict

        # - configure gui
        # -- configure window
        self.title("HCA Control")
        self.geometry(f"{877}x{852}")
        self.resizable(True, True)

        self.setup_window = None
        self.calibrating_window = None
        self.sampling_window = None
        self.process_window = None

        # - left sidebar widgets
        # -- create frame for left sidebar widgets
        self.frame_sidebar = ctk.CTkFrame(self)
        self.frame_sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")

        # -- left sidebar labels
        self.label_title_main = ctk.CTkLabel(self.frame_sidebar, text="HCA Controls",
                                             font=ctk.CTkFont(size=20, weight="bold"))
        self.label_version = ctk.CTkLabel(self.frame_sidebar, text="Version 20231222 ",
                                          font=ctk.CTkFont(slant="italic"))
        self.label_appearance = ctk.CTkLabel(self.frame_sidebar, text="Appearance Mode:")
        # self.scaling_label = ct.CTkLabel(self.frame_sidebar, text="UI Scaling:")

        # -- left sidebar buttons
        self.button_profile_setup = ctk.CTkButton(self.frame_sidebar, text='Setup',
                                                  command=lambda: self.open_setup_window())
        self.button_zero = ctk.CTkButton(self.frame_sidebar, text='Zero',
                                         hover_color="DarkSlateGrey", fg_color="cyan4",
                                         command=lambda: self.open_calibrating_window("Zero"))
        self.button_span = ctk.CTkButton(self.frame_sidebar, text='Span',
                                         hover_color="DarkSlateGrey", fg_color="cyan4",
                                         command=lambda: self.open_calibrating_window("Span"))
        self.button_background = ctk.CTkButton(self.frame_sidebar, text='Background',
                                               hover_color="DarkSlateGrey", fg_color="cyan4",
                                               command=lambda: self.open_calibrating_window("Background"))
        self.button_start_run = ctk.CTkButton(self.frame_sidebar, text='Start Sample Run',
                                              fg_color="OliveDrab4", hover_color="dark olive green",
                                              command=lambda: self.open_sampling_window())
        self.button_process_data = ctk.CTkButton(self.frame_sidebar, text='Process Data',
                                                 command=lambda: self.open_process_window())
        self.button_close_window = ctk.CTkButton(self.frame_sidebar, text='Quit Program',
                                                 hover_color="red4", fg_color="red3",
                                                 command=self.destroy)

        # -- left sidebar menus
        self.menu_appearance = ctk.CTkOptionMenu(self.frame_sidebar, values=["Light", "Dark", "System"],
                                                 command=self.change_appearance_mode_event)

        # - program theme default values
        self.menu_appearance.set("System")
        # self.menu_scaling.set("100%")

        # -- left sidebar widget positioning
        self.label_title_main.grid(row=0, column=0, padx=20, pady=(20, 0))
        self.label_version.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="n")
        self.button_profile_setup.grid(row=2, column=0, padx=20, pady=(0, 10))
        self.button_zero.grid(row=3, column=0, padx=20, pady=(0, 10))
        self.button_span.grid(row=4, column=0, padx=20, pady=(0, 10))
        self.button_background.grid(row=5, column=0, padx=20, pady=(0, 10))
        self.button_start_run.grid(row=6, column=0, padx=20, pady=(0, 10))
        self.button_process_data.grid(row=7, column=0, padx=20, pady=(0, 10))
        self.label_appearance.grid(row=8, column=0, padx=20, pady=(50, 0), sticky="s")
        self.menu_appearance.grid(row=9, column=0, padx=20, pady=(0, 75), sticky="n")
        self.button_close_window.grid(row=10, column=0, padx=20, pady=(75, 20))

        # - HCA positions
        # -- create frame for HCA positions
        self.frame_position = ctk.CTkFrame(self)
        self.frame_position.grid(row=0, column=1, columnspan=2, padx=(5, 0), pady=(5, 0), sticky="nsew")
        # -- center grid vertically and horizontally within frame by creating empty rows & columns on all sides
        self.frame_position.grid_rowconfigure(0, weight=1)
        self.frame_position.grid_rowconfigure(10, weight=1)
        self.frame_position.grid_columnconfigure(0, weight=1)
        self.frame_position.grid_columnconfigure(5, weight=1)
        self.label_title_positions = ctk.CTkLabel(self.frame_position, text="Rake Position",
                                                  font=ctk.CTkFont(size=16, weight="bold"))

        # -- HCA positions labels
        self.label_axis_profile = ctk.CTkLabel(self.frame_position, text="Profile Axis", anchor="s")
        self.label_axis_2 = ctk.CTkLabel(self.frame_position, text="Axis 2", anchor="s")
        self.label_axis_3 = ctk.CTkLabel(self.frame_position, text="Axis 3", anchor="s")
        self.label_axis_profile_pos = ctk.CTkLabel(self.frame_position, text="Profile Pos.", anchor="s")
        self.label_axis_2_posi = ctk.CTkLabel(self.frame_position, text="C1 New", anchor="s")
        self.label_axis_3_posi = ctk.CTkLabel(self.frame_position, text="C2 New", anchor="s")
        self.label_rake_origin = ctk.CTkLabel(self.frame_position, text="Rake Origin", anchor="s")
        self.label_rake_offset = ctk.CTkLabel(self.frame_position, text="Rake Offset", anchor="s")
        self.label_rake_profile_pos = ctk.CTkLabel(self.frame_position, text="Rake Positions", anchor="s")

        # -- HCA positions entry defaults
        self.axis_profile = tk.StringVar()
        self.axis_profile.set(hca_dict['Profile Axis (X, Y, Z)'])
        self.axis_2 = tk.StringVar()
        self.axis_2.set(hca_dict['Axis 2 (X, Y, Z)'])
        self.axis_3 = tk.StringVar()
        self.axis_3.set(hca_dict['Axis 3 (X, Y, Z)'])
        self.axis_profile_pos = tk.IntVar()
        self.axis_profile_pos.set(hca_dict['Rake Origin Profile Position (mm)'])
        self.axis_2_pos = tk.IntVar()
        self.axis_2_pos.set(hca_dict['Axis 2 Position (mm)'])
        self.axis_3_pos = tk.IntVar()
        self.axis_3_pos.set(hca_dict['Axis 3 Position (mm)'])
        self.rake_offset = tk.IntVar()
        self.rake_offset.set(hca_dict['Rake Offset (mm)'])
        self.rake_position_1 = tk.IntVar()
        self.rake_position_1.set(hca_dict['Rake Origin Profile Position (mm)'])
        self.rake_position_2 = tk.IntVar()
        self.rake_position_2.set(hca_dict['Rake 2 Profile Position (mm)'])
        self.rake_position_3 = tk.IntVar()
        self.rake_position_3.set(hca_dict['Rake 3 Profile Position (mm)'])
        self.rake_position_4 = tk.IntVar()
        self.rake_position_4.set(hca_dict['Rake 4 Profile Position (mm)'])
        self.rake_position_5 = tk.IntVar()
        self.rake_position_5.set(hca_dict['Rake 5 Profile Position (mm)'])
        self.rake_position_6 = tk.IntVar()
        self.rake_position_6.set(hca_dict['Rake 6 Profile Position (mm)'])

        # -- HCA positions entries
        self.entry_axis_profile = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.axis_profile)
        self.entry_axis_2 = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                         font=ctk.CTkFont(slant="italic"), textvariable=self.axis_2)
        self.entry_axis_3 = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                         font=ctk.CTkFont(slant="italic"), textvariable=self.axis_3)
        self.entry_axis_profile_posi = ctk.CTkEntry(self.frame_position, width=50,
                                                    textvariable=self.axis_profile_pos)
        self.entry_axis_2_posi = ctk.CTkEntry(self.frame_position, width=50, textvariable=self.axis_2_pos)
        self.entry_axis_3_posi = ctk.CTkEntry(self.frame_position, width=50, textvariable=self.axis_3_pos)
        self.entry_rake_offset = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.rake_offset)
        self.entry_rake_position_1 = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.rake_position_1)
        self.entry_rake_position_2 = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.rake_position_2)
        self.entry_rake_position_3 = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.rake_position_3)
        self.entry_rake_position_4 = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.rake_position_4)
        self.entry_rake_position_5 = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.rake_position_5)
        self.entry_rake_position_6 = ctk.CTkEntry(self.frame_position, width=50, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"), textvariable=self.rake_position_6)

        # -- HCA positions buttons
        self.button_change_position = ctk.CTkButton(self.frame_position, text='Change Position',
                                                    command=lambda: set_rake_position())

        # -- HCA widgets positioning
        self.label_title_positions.grid(row=1, column=1, columnspan=4, pady=(10, 0), sticky="nsew")
        self.label_axis_profile.grid(row=2, column=1, padx=(10, 0), sticky="s")
        self.label_axis_2.grid(row=2, column=2, padx=(10, 0), sticky="s")
        self.label_axis_3.grid(row=2, column=3, padx=(10, 0), sticky="s")
        self.label_rake_profile_pos.grid(row=2, column=4, padx=(10, 15), sticky="s")
        self.entry_axis_profile.grid(row=3, column=1, padx=(15, 0), pady=(10, 0), sticky="n")
        self.entry_axis_2.grid(row=3, column=2, padx=(10, 0), pady=(10, 0), sticky="n")
        self.entry_axis_3.grid(row=3, column=3, padx=(10, 0), pady=(10, 0), sticky="n")
        self.entry_rake_position_1.grid(row=3, column=4, padx=(10, 15), pady=(10, 0), sticky="n")
        self.label_axis_profile_pos.grid(row=4, column=1, padx=(15, 0), pady=(10, 0), sticky="s")
        self.label_axis_2_posi.grid(row=4, column=2, padx=(10, 0), pady=(10, 0), sticky="s")
        self.label_axis_3_posi.grid(row=4, column=3, padx=(10, 0), pady=(10, 0), sticky="s")
        self.entry_rake_position_2.grid(row=4, column=4, padx=(10, 15), pady=(10, 0), sticky="n")
        self.entry_axis_profile_posi.grid(row=5, column=1, padx=(15, 0), pady=(10, 0), sticky="n")
        self.entry_axis_2_posi.grid(row=5, column=2, padx=(10, 0), pady=(10, 0), sticky="n")
        self.entry_axis_3_posi.grid(row=5, column=3, padx=(10, 0), pady=(10, 0), sticky="n")
        self.entry_rake_position_3.grid(row=5, column=4, padx=(10, 15), pady=(10, 0), sticky="n")
        self.label_rake_offset.grid(row=6, column=1, padx=(15, 0), pady=(10, 0), sticky="s")
        self.button_change_position.grid(row=6, column=2, rowspan=3, columnspan=2, padx=(20, 10), pady=(30, 60),
                                         sticky="nsew")
        self.entry_rake_position_4.grid(row=6, column=4, padx=(10, 15), pady=(10, 0), sticky="n")
        self.entry_rake_offset.grid(row=7, column=1, padx=(15, 0), pady=(10, 0), sticky="n")
        self.entry_rake_position_5.grid(row=7, column=4, padx=(10, 15), pady=(10, 0), sticky="n")
        self.entry_rake_position_6.grid(row=8, column=4, padx=(10, 15), pady=(10, 15), sticky="n")

        # - HCA ranges
        # -- create frame for HCA ranges
        self.frame_ranges = ctk.CTkFrame(self)
        self.frame_ranges.grid(row=0, column=3, padx=5, pady=(5, 0), sticky="nsew")
        # -- center grid vertically and horizontally within frame by creating empty rows & columns on all sides
        self.frame_ranges.grid_rowconfigure(0, weight=1)
        self.frame_ranges.grid_rowconfigure(10, weight=1)
        self.frame_ranges.grid_columnconfigure(0, weight=1)
        self.frame_ranges.grid_columnconfigure(5, weight=1)
        self.label_title_ranges = ctk.CTkLabel(self.frame_ranges, text="Range Selection",
                                               font=ctk.CTkFont(size=16, weight="bold"))

        # -- HCA ranges labels
        self.label_new_ranges = ctk.CTkLabel(self.frame_ranges, text="New", anchor="s")
        self.label_ranges = ctk.CTkLabel(self.frame_ranges, text="Set", anchor="s")

        # -- HCA ranges entry defaults
        self.new_range_1 = tk.StringVar()
        self.new_range_1.set("1")
        self.new_range_2 = tk.StringVar()
        self.new_range_2.set("1")
        self.new_range_3 = tk.StringVar()
        self.new_range_3.set("1")
        self.new_range_4 = tk.StringVar()
        self.new_range_4.set("1")
        self.new_range_5 = tk.StringVar()
        self.new_range_5.set("1")
        self.new_range_6 = tk.StringVar()
        self.new_range_6.set("1")
        self.range_1_stored = tk.IntVar()
        self.range_1_stored.set(hca_dict['HCA#1 Range (#)'])
        self.range_2_stored = tk.IntVar()
        self.range_2_stored.set(hca_dict['HCA#2 Range (#)'])
        self.range_3_stored = tk.IntVar()
        self.range_3_stored.set(hca_dict['HCA#3 Range (#)'])
        self.range_4_stored = tk.IntVar()
        self.range_4_stored.set(hca_dict['HCA#4 Range (#)'])
        self.range_5_stored = tk.IntVar()
        self.range_5_stored.set(hca_dict['HCA#5 Range (#)'])
        self.range_6_stored = tk.IntVar()
        self.range_6_stored.set(hca_dict['HCA#6 Range (#)'])

        # -- HCA positions entries
        self.entry_new_range_1 = ctk.CTkEntry(self.frame_ranges, width=20, textvariable=self.new_range_1)
        self.entry_new_range_2 = ctk.CTkEntry(self.frame_ranges, width=20, textvariable=self.new_range_2)
        self.entry_new_range_3 = ctk.CTkEntry(self.frame_ranges, width=20, textvariable=self.new_range_3)
        self.entry_new_range_4 = ctk.CTkEntry(self.frame_ranges, width=20, textvariable=self.new_range_4)
        self.entry_new_range_5 = ctk.CTkEntry(self.frame_ranges, width=20, textvariable=self.new_range_5)
        self.entry_new_range_6 = ctk.CTkEntry(self.frame_ranges, width=20, textvariable=self.new_range_6)
        self.range_1 = ctk.CTkLabel(self.frame_ranges, text=str(self.range_1_stored.get()))
        self.range_2 = ctk.CTkLabel(self.frame_ranges, text=str(self.range_2_stored.get()))
        self.range_3 = ctk.CTkLabel(self.frame_ranges, text=str(self.range_3_stored.get()))
        self.range_4 = ctk.CTkLabel(self.frame_ranges, text=str(self.range_4_stored.get()))
        self.range_5 = ctk.CTkLabel(self.frame_ranges, text=str(self.range_5_stored.get()))
        self.range_6 = ctk.CTkLabel(self.frame_ranges, text=str(self.range_6_stored.get()))

        # -- HCA positions buttons and switches
        self.button_set_ranges = ctk.CTkButton(self.frame_ranges, text='Set New Ranges',
                                               command=lambda: self.update_ranges("New"))
        self.button_set_for_zero = ctk.CTkButton(self.frame_ranges, text='Set for Zero',
                                                 command=lambda: self.update_ranges("Zero"))
        self.button_set_for_span = ctk.CTkButton(self.frame_ranges, text='Set for Span',
                                                 command=lambda: self.update_ranges("Span"))
        self.switch_auto_range_state = ctk.StringVar(value="on")
        self.switch_auto_range = ctk.CTkSwitch(self.frame_ranges, text="Auto Range",
                                               command=lambda: self.switch_event_auto_range(),
                                               variable=self.switch_auto_range_state, onvalue="on", offvalue="off")

        # -- HCA widgets positioning
        self.label_title_ranges.grid(row=1, column=1, columnspan=3, pady=(10, 0), sticky="s")
        self.label_new_ranges.grid(row=2, column=2, padx=(15, 0), sticky="s")
        self.label_ranges.grid(row=2, column=3, padx=(15, 0), sticky="s")
        self.button_set_ranges.grid(row=3, column=1, pady=(10, 0), sticky="nsew")
        self.entry_new_range_1.grid(row=3, column=2, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.range_1.grid(row=3, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.button_set_for_zero.grid(row=4, column=1, pady=(10, 0), sticky="nsew")
        self.entry_new_range_2.grid(row=4, column=2, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.range_2.grid(row=4, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.button_set_for_span.grid(row=5, column=1, pady=(10, 0), sticky="nsew")
        self.entry_new_range_3.grid(row=5, column=2, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.range_3.grid(row=5, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_new_range_4.grid(row=6, column=2, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.range_4.grid(row=6, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.switch_auto_range.grid(row=7, column=1, pady=(10, 0), sticky="n")
        self.entry_new_range_5.grid(row=7, column=2, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.range_5.grid(row=7, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_new_range_6.grid(row=8, column=2, padx=(15, 0), pady=(10, 15), sticky="nsew")
        self.range_6.grid(row=8, column=3, padx=(15, 0), pady=(10, 15), sticky="nsew")

        # - HCA concentrations
        # -- create frame for HCA concentrations
        self.frame_concentrations = ctk.CTkFrame(self)
        self.frame_concentrations.grid(row=1, column=1, columnspan=3, padx=5, pady=(5, 0), sticky="nsew")
        # -- center grid vertically and horizontally within frame by creating empty rows & columns on all sides
        self.frame_concentrations.grid_rowconfigure(0, weight=1)
        self.frame_concentrations.grid_rowconfigure(10, weight=1)
        self.frame_concentrations.grid_columnconfigure(0, weight=1)
        self.frame_concentrations.grid_columnconfigure(8, weight=1)
        self.label_title_concentrations = ctk.CTkLabel(self.frame_concentrations, text="Sample and Concentration Data",
                                                       font=ctk.CTkFont(size=16, weight="bold"))

        # -- HCA concentrations labels
        self.label_hca_zero_conc = ctk.CTkLabel(self.frame_concentrations, text="HCA Zero Conc. (g/m3):")
        self.label_hca_span_conc = ctk.CTkLabel(self.frame_concentrations, text="HCA Span Conc. (g/m3):")
        self.label_zero_channel_range = ctk.CTkLabel(self.frame_concentrations, text="Zero Range by Channel (%):")
        self.label_span_channel_range = ctk.CTkLabel(self.frame_concentrations, text="Span Range by Channel (%):")
        self.label_bkg_range = ctk.CTkLabel(self.frame_concentrations, text="Background Range (%):")
        self.label_raw_conc = ctk.CTkLabel(self.frame_concentrations, text="Sample Raw Conc. (g/m3):")
        self.label_bounds_high = ctk.CTkLabel(self.frame_concentrations, text="Out of Range High (#):")
        self.label_bounds_low = ctk.CTkLabel(self.frame_concentrations, text="Out of Range Low (#):")

        # -- HCA concentrations entry defaults
        self.hca_zero_conc = tk.IntVar()
        self.hca_zero_conc.set(hca_dict['Zero Concentration (g/m3)'])
        self.hca_span_conc = tk.DoubleVar()
        self.hca_span_conc.set(hca_dict['Span Concentration (g/m3)'])
        self.hca_zero_ch_1 = tk.DoubleVar()
        self.hca_zero_ch_1.set(hca_dict['HCA#1 Zero (% range)'])
        self.hca_zero_ch_2 = tk.DoubleVar()
        self.hca_zero_ch_2.set(hca_dict['HCA#2 Zero (% range)'])
        self.hca_zero_ch_3 = tk.DoubleVar()
        self.hca_zero_ch_3.set(hca_dict['HCA#3 Zero (% range)'])
        self.hca_zero_ch_4 = tk.DoubleVar()
        self.hca_zero_ch_4.set(hca_dict['HCA#4 Zero (% range)'])
        self.hca_zero_ch_5 = tk.DoubleVar()
        self.hca_zero_ch_5.set(hca_dict['HCA#5 Zero (% range)'])
        self.hca_zero_ch_6 = tk.DoubleVar()
        self.hca_zero_ch_6.set(hca_dict['HCA#6 Zero (% range)'])
        self.hca_span_ch_1 = tk.DoubleVar()
        self.hca_span_ch_1.set(hca_dict['HCA#1 Span (% range)'])
        self.hca_span_ch_2 = tk.DoubleVar()
        self.hca_span_ch_2.set(hca_dict['HCA#2 Span (% range)'])
        self.hca_span_ch_3 = tk.DoubleVar()
        self.hca_span_ch_3.set(hca_dict['HCA#3 Span (% range)'])
        self.hca_span_ch_4 = tk.DoubleVar()
        self.hca_span_ch_4.set(hca_dict['HCA#4 Span (% range)'])
        self.hca_span_ch_5 = tk.DoubleVar()
        self.hca_span_ch_5.set(hca_dict['HCA#5 Span (% range)'])
        self.hca_span_ch_6 = tk.DoubleVar()
        self.hca_span_ch_6.set(hca_dict['HCA#6 Span (% range)'])
        self.hca_bkg_ch_1 = tk.DoubleVar()
        self.hca_bkg_ch_1.set(hca_dict['HCA#1 Background (% range)'])
        self.hca_bkg_ch_2 = tk.DoubleVar()
        self.hca_bkg_ch_2.set(hca_dict['HCA#2 Background (% range)'])
        self.hca_bkg_ch_3 = tk.DoubleVar()
        self.hca_bkg_ch_3.set(hca_dict['HCA#3 Background (% range)'])
        self.hca_bkg_ch_4 = tk.DoubleVar()
        self.hca_bkg_ch_4.set(hca_dict['HCA#4 Background (% range)'])
        self.hca_bkg_ch_5 = tk.DoubleVar()
        self.hca_bkg_ch_5.set(hca_dict['HCA#5 Background (% range)'])
        self.hca_bkg_ch_6 = tk.DoubleVar()
        self.hca_bkg_ch_6.set(hca_dict['HCA#6 Background (% range)'])
        self.raw_conc_ch_1 = tk.DoubleVar()
        self.raw_conc_ch_1.set(hca_dict['HCA#1 Sample Concentration (g/m3)'])
        self.raw_conc_ch_2 = tk.DoubleVar()
        self.raw_conc_ch_2.set(hca_dict['HCA#2 Sample Concentration (g/m3)'])
        self.raw_conc_ch_3 = tk.DoubleVar()
        self.raw_conc_ch_3.set(hca_dict['HCA#3 Sample Concentration (g/m3)'])
        self.raw_conc_ch_4 = tk.DoubleVar()
        self.raw_conc_ch_4.set(hca_dict['HCA#4 Sample Concentration (g/m3)'])
        self.raw_conc_ch_5 = tk.DoubleVar()
        self.raw_conc_ch_5.set(hca_dict['HCA#5 Sample Concentration (g/m3)'])
        self.raw_conc_ch_6 = tk.DoubleVar()
        self.raw_conc_ch_6.set(hca_dict['HCA#6 Sample Concentration (g/m3)'])
        self.bound_high_1 = tk.IntVar()
        self.bound_high_1.set(hca_dict['HCA#1 OB High (#)'])
        self.bound_high_2 = tk.IntVar()
        self.bound_high_2.set(hca_dict['HCA#2 OB High (#)'])
        self.bound_high_3 = tk.IntVar()
        self.bound_high_3.set(hca_dict['HCA#3 OB High (#)'])
        self.bound_high_4 = tk.IntVar()
        self.bound_high_4.set(hca_dict['HCA#4 OB High (#)'])
        self.bound_high_5 = tk.IntVar()
        self.bound_high_5.set(hca_dict['HCA#5 OB High (#)'])
        self.bound_high_6 = tk.IntVar()
        self.bound_high_6.set(hca_dict['HCA#6 OB High (#)'])
        self.bound_low_1 = tk.IntVar()
        self.bound_low_1.set(hca_dict['HCA#1 OB Low (#)'])
        self.bound_low_2 = tk.IntVar()
        self.bound_low_2.set(hca_dict['HCA#2 OB Low (#)'])
        self.bound_low_3 = tk.IntVar()
        self.bound_low_3.set(hca_dict['HCA#3 OB Low (#)'])
        self.bound_low_4 = tk.IntVar()
        self.bound_low_4.set(hca_dict['HCA#4 OB Low (#)'])
        self.bound_low_5 = tk.IntVar()
        self.bound_low_5.set(hca_dict['HCA#5 OB Low (#)'])
        self.bound_low_6 = tk.IntVar()
        self.bound_low_6.set(hca_dict['HCA#6 OB Low (#)'])

        # -- HCA positions entries
        self.entry_hca_zero_conc = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_zero_conc)
        self.entry_hca_span_conc = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_span_conc)
        self.entry_hca_zero_ch_1 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_zero_ch_1)
        self.entry_hca_zero_ch_2 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_zero_ch_2)
        self.entry_hca_zero_ch_3 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_zero_ch_3)
        self.entry_hca_zero_ch_4 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_zero_ch_4)
        self.entry_hca_zero_ch_5 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_zero_ch_5)
        self.entry_hca_zero_ch_6 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_zero_ch_6)
        self.entry_hca_span_ch_1 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_span_ch_1)
        self.entry_hca_span_ch_2 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_span_ch_2)
        self.entry_hca_span_ch_3 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_span_ch_3)
        self.entry_hca_span_ch_4 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_span_ch_4)
        self.entry_hca_span_ch_5 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_span_ch_5)
        self.entry_hca_span_ch_6 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.hca_span_ch_6)
        self.entry_hca_bkg_ch_1 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.hca_bkg_ch_1)
        self.entry_hca_bkg_ch_2 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.hca_bkg_ch_2)
        self.entry_hca_bkg_ch_3 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.hca_bkg_ch_3)
        self.entry_hca_bkg_ch_4 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.hca_bkg_ch_4)
        self.entry_hca_bkg_ch_5 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.hca_bkg_ch_5)
        self.entry_hca_bkg_ch_6 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.hca_bkg_ch_6)
        self.entry_raw_conc_ch_1 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.raw_conc_ch_1)
        self.entry_raw_conc_ch_2 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.raw_conc_ch_2)
        self.entry_raw_conc_ch_3 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.raw_conc_ch_3)
        self.entry_raw_conc_ch_4 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.raw_conc_ch_4)
        self.entry_raw_conc_ch_5 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.raw_conc_ch_5)
        self.entry_raw_conc_ch_6 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                                font=ctk.CTkFont(slant="italic"), textvariable=self.raw_conc_ch_6)
        self.entry_bound_low_1 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.bound_low_1)
        self.entry_bound_low_2 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.bound_low_2)
        self.entry_bound_low_3 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.bound_low_3)
        self.entry_bound_low_4 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.bound_low_4)
        self.entry_bound_low_5 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.bound_low_5)
        self.entry_bound_low_6 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                              font=ctk.CTkFont(slant="italic"), textvariable=self.bound_low_6)
        self.entry_bound_high_1 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.bound_high_1)
        self.entry_bound_high_2 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.bound_high_2)
        self.entry_bound_high_3 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.bound_high_3)
        self.entry_bound_high_4 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.bound_high_4)
        self.entry_bound_high_5 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"),  textvariable=self.bound_high_5)
        self.entry_bound_high_6 = ctk.CTkEntry(self.frame_concentrations, width=70, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.bound_high_6)

        # -- HCA widgets positioning
        self.label_title_concentrations.grid(row=1, column=1, columnspan=7, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.label_hca_zero_conc.grid(row=2, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_hca_zero_conc.grid(row=2, column=2, padx=(5, 0), pady=(10, 0), sticky="w")
        self.label_hca_span_conc.grid(row=2, column=4, columnspan=3, padx=(10, 0), pady=(10, 0), sticky="e")
        self.entry_hca_span_conc.grid(row=2, column=7, padx=(15, 0), pady=(10, 0), sticky="w")
        self.label_zero_channel_range.grid(row=3, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_hca_zero_ch_1.grid(row=3, column=2, padx=(5, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_zero_ch_2.grid(row=3, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_zero_ch_3.grid(row=3, column=4, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_zero_ch_4.grid(row=3, column=5, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_zero_ch_5.grid(row=3, column=6, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_zero_ch_6.grid(row=3, column=7, padx=15, pady=(10, 0), sticky="nsew")
        self.label_span_channel_range.grid(row=4, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_hca_span_ch_1.grid(row=4, column=2, padx=(5, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_span_ch_2.grid(row=4, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_span_ch_3.grid(row=4, column=4, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_span_ch_4.grid(row=4, column=5, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_span_ch_5.grid(row=4, column=6, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_span_ch_6.grid(row=4, column=7, padx=15, pady=(10, 0), sticky="nsew")
        self.label_bkg_range.grid(row=5, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_hca_bkg_ch_1.grid(row=5, column=2, padx=(5, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_bkg_ch_2.grid(row=5, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_bkg_ch_3.grid(row=5, column=4, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_bkg_ch_4.grid(row=5, column=5, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_bkg_ch_5.grid(row=5, column=6, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_hca_bkg_ch_6.grid(row=5, column=7, padx=15, pady=(10, 0), sticky="nsew")
        self.label_raw_conc.grid(row=6, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_raw_conc_ch_1.grid(row=6, column=2, padx=(5, 0), pady=(10, 0), sticky="nsew")
        self.entry_raw_conc_ch_2.grid(row=6, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_raw_conc_ch_3.grid(row=6, column=4, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_raw_conc_ch_4.grid(row=6, column=5, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_raw_conc_ch_5.grid(row=6, column=6, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_raw_conc_ch_6.grid(row=6, column=7, padx=15, pady=(10, 0), sticky="nsew")
        self.label_bounds_high.grid(row=7, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_bound_high_1.grid(row=7, column=2, padx=(5, 0), pady=(10, 0), sticky="nsew")
        self.entry_bound_high_2.grid(row=7, column=3, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_bound_high_3.grid(row=7, column=4, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_bound_high_4.grid(row=7, column=5, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_bound_high_5.grid(row=7, column=6, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.entry_bound_high_6.grid(row=7, column=7, padx=15, pady=(10, 0), sticky="nsew")
        self.label_bounds_low.grid(row=8, column=1, padx=(15, 0), pady=(10, 15), sticky="e")
        self.entry_bound_low_1.grid(row=8, column=2, padx=(5, 0), pady=(10, 15), sticky="nsew")
        self.entry_bound_low_2.grid(row=8, column=3, padx=(15, 0), pady=(10, 15), sticky="nsew")
        self.entry_bound_low_3.grid(row=8, column=4, padx=(15, 0), pady=(10, 15), sticky="nsew")
        self.entry_bound_low_4.grid(row=8, column=5, padx=(15, 0), pady=(10, 15), sticky="nsew")
        self.entry_bound_low_5.grid(row=8, column=6, padx=(15, 0), pady=(10, 15), sticky="nsew")
        self.entry_bound_low_6.grid(row=8, column=7, padx=15, pady=(10, 15), sticky="nsew")

        # - HCA filepaths configuration
        # -- create frame for HCA filepaths
        self.frame_filepaths = ctk.CTkFrame(self)
        self.frame_filepaths.grid(row=2, column=1, columnspan=3, padx=5, pady=(5, 0), sticky="nsew")
        # -- center grid vertically and horizontally within frame by creating empty rows & columns on all sides
        self.frame_filepaths.grid_rowconfigure(0, weight=1)
        self.frame_filepaths.grid_rowconfigure(7, weight=1)
        self.frame_filepaths.grid_columnconfigure(0, weight=1)
        self.frame_filepaths.grid_columnconfigure(4, weight=1)
        self.label_title_config = ctk.CTkLabel(self.frame_filepaths, text="Filepaths",
                                               font=ctk.CTkFont(size=16, weight="bold"))

        # -- HCA paths labels
        self.label_hca_merged = ctk.CTkLabel(self.frame_filepaths, text="Profile Raw Data File:")
        self.label_hca_streamed = ctk.CTkLabel(self.frame_filepaths, text="Profile Calibration File:")
        self.label_hca_datareport = ctk.CTkLabel(self.frame_filepaths, text="Profile Data Report File:")
        self.label_hca_calibration = ctk.CTkLabel(self.frame_filepaths, text="Full Calibration File:")

        # -- HCA paths defaults
        self.hca_merged = tk.StringVar()
        self.hca_merged.set(hca_dict['Profile Data File (Full Path)'])
        self.hca_streamed = tk.StringVar()
        self.hca_streamed.set(hca_dict['Profile Calibration File (Full Pa''th)'])
        self.hca_datareport = tk.StringVar()
        self.hca_datareport.set(hca_dict['Profile Data Report File (Full Path)'])
        self.hca_calibration = tk.StringVar()
        self.hca_calibration.set(hca_dict['Full Calibration File (Full Path)'])

        # -- HCA paths entries
        self.entry_hca_merged = ctk.CTkEntry(self.frame_filepaths, width=425, state="disabled",
                                             font=ctk.CTkFont(slant="italic"), textvariable=self.hca_merged)
        self.entry_hca_streamed = ctk.CTkEntry(self.frame_filepaths, width=425, state="disabled",
                                               font=ctk.CTkFont(slant="italic"), textvariable=self.hca_streamed)
        self.entry_hca_datareport = ctk.CTkEntry(self.frame_filepaths, width=425, state="disabled",
                                                 font=ctk.CTkFont(slant="italic"),
                                                 textvariable=self.hca_datareport)
        self.entry_hca_calibration = ctk.CTkEntry(self.frame_filepaths, width=425, state="disabled",
                                                  font=ctk.CTkFont(slant="italic"),
                                                  textvariable=self.hca_calibration)

        # -- HCA bounds positioning
        self.label_title_config.grid(row=1, column=1, columnspan=2, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.label_hca_merged.grid(row=2, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_hca_merged.grid(row=2, column=2, padx=(5, 15), pady=(10, 0), sticky="nsew")
        self.label_hca_streamed.grid(row=3, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_hca_streamed.grid(row=3, column=2, padx=(5, 15), pady=(10, 0), sticky="nsew")
        self.label_hca_datareport.grid(row=4, column=1, padx=(15, 0), pady=(10, 0), sticky="e")
        self.entry_hca_datareport.grid(row=4, column=2, padx=(5, 15), pady=(10, 0), sticky="nsew")
        self.label_hca_calibration.grid(row=5, column=1, padx=(15, 0), pady=(10, 15), sticky="e")
        self.entry_hca_calibration.grid(row=5, column=2, padx=(5, 15), pady=(10, 15), sticky="nsew")

        self.HCA_threading()

    # - change overall appearance of program to light, dark, or system
    @staticmethod
    def change_appearance_mode_event(new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    # - change overall scaling of program
    @staticmethod
    def change_scaling_event(new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    # - opens process data window
    def open_process_window(self):
        if self.process_window is None or not self.process_window.winfo_exists():
            self.process_window = hca_popups.ProcessWindow()  # create window if its None or destroyed
            # self.button_process_data.configure(text="Logging!")
        else:
            self.process_window.focus()  # if window exists focus it

    # - opens setup window
    def open_setup_window(self):
        if self.setup_window is None or not self.setup_window.winfo_exists():
            self.setup_window = hca_popups.SetupWindow()  # create window if its None or destroyed
            # self.button_setup.configure(text="Logging!")
        else:
            self.setup_window.focus()  # if window exists focus it

    # TODO: window initializes twice, once with existence check and once with mode argument
    # - opens calibrating window
    def open_calibrating_window(self, mode):
        if self.calibrating_window is None or not self.calibrating_window.winfo_exists():
            # self.calibrating_window = hca_popups.CalibratingWindow()  # create window if its None or destroyed
            # self.button_calibrating.configure(text="Logging!")
            if mode == "Zero":
                self.calibrating_window = hca_popups.CalibratingWindow().cal_mode.set("Zero")
            elif mode == "Span":
                self.calibrating_window = hca_popups.CalibratingWindow().cal_mode.set("Span")
            elif mode == "Background":
                self.calibrating_window = hca_popups.CalibratingWindow().cal_mode.set("Background")
            else:
                print("Calibration mode error!")
        else:
            self.calibrating_window.focus()  # if window exists focus it

    # - opens sample running window
    def open_sampling_window(self):
        if self.sampling_window is None or not self.sampling_window.winfo_exists():
            self.sampling_window = hca_popups.SamplingWindow()  # create window if its None or destroyed
            # self.button_sampling.configure(text="Logging!")
        else:
            self.sampling_window.focus()  # if window exists focus it

    def switch_event_auto_range(self):
        print("Switch toggled, current value:", self.switch_auto_range_state.get())

    # - placeholder function for temp purposes
    @staticmethod
    def placeholder_function():
        print("Button works!")

    # -- create thread to constantly update carriage position and stop codes
    def HCA_threading(self):
        data_thread = Thread(target=self.update_data)
        data_thread.start()

    # TODO: motion complete after target - position = 0?
    # -- update carriage positions and stop codes
    # noinspection PyTypeChecker
    def update_data(self):
        global hca_dict
        task = nidaqmx.Task()
        task.start()
        hca1_raw_conc = task.read()
        hca1_raw_conc_str = str(hca1_raw_conc)
        hca2_raw_conc = task.read()
        hca2_raw_conc_str = str(hca2_raw_conc)
        hca3_raw_conc = task.read()
        hca3_raw_conc_str = str(hca3_raw_conc)
        hca4_raw_conc = task.read()
        hca4_raw_conc_str = str(hca4_raw_conc)
        hca5_raw_conc = task.read()
        hca5_raw_conc_str = str(hca5_raw_conc)
        hca6_raw_conc = task.read()
        hca6_raw_conc_str = str(hca6_raw_conc)
        task.stop()
        task.close()
        self.raw_conc_ch_1.set(hca1_raw_conc)
        self.raw_conc_ch_2.set(hca2_raw_conc)
        self.raw_conc_ch_3.set(hca3_raw_conc)
        self.raw_conc_ch_4.set(hca4_raw_conc)
        self.raw_conc_ch_5.set(hca5_raw_conc)
        self.raw_conc_ch_6.set(hca6_raw_conc)
        hca_dict |= {'HCA#1 Sample Concentration (g/m3)': hca1_raw_conc_str}
        hca_dict |= {'HCA#2 Sample Concentration (g/m3)': hca2_raw_conc_str}
        hca_dict |= {'HCA#3 Sample Concentration (g/m3)': hca3_raw_conc_str}
        hca_dict |= {'HCA#4 Sample Concentration (g/m3)': hca4_raw_conc_str}
        hca_dict |= {'HCA#5 Sample Concentration (g/m3)': hca5_raw_conc_str}
        hca_dict |= {'HCA#6 Sample Concentration (g/m3)': hca6_raw_conc_str}
        hca_ini.ini_generate()
        self.after(10, self.update_data)

    # -- set current HCA ranges to specified ranges
    def update_ranges(self, setting):
        global hca_dict
        if setting == "New":
            self.range_1_stored.set(int(self.entry_new_range_1.get()))  # HCA1 range variable updated
            self.range_2_stored.set(int(self.entry_new_range_2.get()))  # HCA2 range variable updated
            self.range_3_stored.set(int(self.entry_new_range_3.get()))  # HCA3 range variable updated
            self.range_4_stored.set(int(self.entry_new_range_4.get()))  # HCA4 range variable updated
            self.range_5_stored.set(int(self.entry_new_range_5.get()))  # HCA5 range variable updated
            self.range_6_stored.set(int(self.entry_new_range_6.get()))  # HCA6 range variable updated
            hca_ranges.set_single_range(1, int(self.entry_new_range_1.get()))  # HCA1 to new range
            hca_ranges.set_single_range(2, int(self.entry_new_range_2.get()))  # HCA2 to new range
            hca_ranges.set_single_range(3, int(self.entry_new_range_3.get()))  # HCA3 to new range
            hca_ranges.set_single_range(4, int(self.entry_new_range_4.get()))  # HCA4 to new range
            hca_ranges.set_single_range(5, int(self.entry_new_range_5.get()))  # HCA5 to new range
            hca_ranges.set_single_range(6, int(self.entry_new_range_6.get()))  # HCA6 to new range
        elif setting == "Zero":
            self.range_1_stored.set(1)  # HCA1 range variable updated
            self.range_2_stored.set(1)  # HCA2 range variable updated
            self.range_3_stored.set(1)  # HCA3 range variable updated
            self.range_4_stored.set(1)  # HCA4 range variable updated
            self.range_5_stored.set(1)  # HCA5 range variable updated
            self.range_6_stored.set(1)  # HCA6 range variable updated
            hca_ranges.set_single_range(1, 1)  # HCA1 to zero range
            hca_ranges.set_single_range(2, 1)  # HCA2 to zero range
            hca_ranges.set_single_range(3, 1)  # HCA3 to zero range
            hca_ranges.set_single_range(4, 1)  # HCA4 to zero range
            hca_ranges.set_single_range(5, 1)  # HCA5 to zero range
            hca_ranges.set_single_range(6, 1)  # HCA6 to zero range
        elif setting == "Span":
            self.range_1_stored.set(7)  # HCA1 range variable updated
            self.range_2_stored.set(7)  # HCA2 range variable updated
            self.range_3_stored.set(7)  # HCA3 range variable updated
            self.range_4_stored.set(7)  # HCA4 range variable updated
            self.range_5_stored.set(7)  # HCA5 range variable updated
            self.range_6_stored.set(7)  # HCA6 range variable updated
            hca_ranges.set_single_range(1, 7)  # HCA1 to span range
            hca_ranges.set_single_range(2, 7)  # HCA2 to span range
            hca_ranges.set_single_range(3, 7)  # HCA3 to span range
            hca_ranges.set_single_range(4, 7)  # HCA4 to span range
            hca_ranges.set_single_range(5, 7)  # HCA5 to span range
            hca_ranges.set_single_range(6, 7)  # HCA6 to span range
        else:
            print("Range setting error!")
        hca_dict |= {'HCA#1 Range (#)': self.range_1_stored.get()}  # HCA1 range database variable updated
        hca_dict |= {'HCA#2 Range (#)': self.range_2_stored.get()}  # HCA2 range database variable updated
        hca_dict |= {'HCA#3 Range (#)': self.range_3_stored.get()}  # HCA3 range database variable updated
        hca_dict |= {'HCA#4 Range (#)': self.range_4_stored.get()}  # HCA4 range database variable updated
        hca_dict |= {'HCA#5 Range (#)': self.range_5_stored.get()}  # HCA5 range database variable updated
        hca_dict |= {'HCA#6 Range (#)': self.range_6_stored.get()}  # HCA6 range database variable updated
        self.range_1.configure(text=str(self.range_1_stored.get()))  # HCA1 displayed value updated
        self.range_2.configure(text=str(self.range_2_stored.get()))  # HCA2 displayed value updated
        self.range_3.configure(text=str(self.range_3_stored.get()))  # HCA3 displayed value updated
        self.range_4.configure(text=str(self.range_4_stored.get()))  # HCA4 displayed value updated
        self.range_5.configure(text=str(self.range_5_stored.get()))  # HCA5 displayed value updated
        self.range_6.configure(text=str(self.range_6_stored.get()))  # HCA6 displayed value updated
        hca_ini.ini_generate()  # update database

        # def quit_program(self):
        #     self.destroy


if __name__ == "__main__":
    app = GUI()
    app.mainloop()
