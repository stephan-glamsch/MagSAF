import os
import signal
from datetime import datetime
import customtkinter as ctk
import tkinter as tk
import pyautogui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.axes_grid1 import make_axes_locatable
import threading
import numpy as np

from GUI_elements import Parameter, ThicknessMsCalculator
from MacrospinModel import MacrospinModel

plt.style.use('dark_background')
ctk.set_appearance_mode("Dark")
screen_size = pyautogui.size()
GUI_scale = screen_size.width/2560
ctk.set_widget_scaling(GUI_scale)
ctk.set_window_scaling(GUI_scale)

pads = 10
entry_w = 90
slider_w = 200
tk_text_subscript = int(11*GUI_scale)
tk_text_font_size = int(14*GUI_scale)
small_font_size = 15
medium_font_size = 17
large_font_size = 20
font_name = "Space Grotesk"
exp_color = "#0087c1"
sim_color = "#d4002d"
phiA_color = "#ad007c"
phiB_color = "#eb690b"


def normalizeRadian(phi):      # reduce angles to (-pi < phi < pi)
    sign = np.sign(phi)
    phi_mod = (sign*phi) % (2*np.pi)    # reduce it below 2 pi
    if phi_mod >= np.pi:
        phi_mod = phi_mod - (2*np.pi)   # reduce it to (-pi < phi_mod < pi)
    p = sign*phi_mod
    try:
        return p[0]
    except:
        return p

def closeApp():
    os.kill(os.getpid(), signal.SIGTERM)


class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.title("MagSAF - Simulating and Fitting of Magnetic Hystersis Loops of SAFs")

        # all frames
        self.scroll_parent = ctk.CTkScrollableFrame(self, height=1150, width=1920, fg_color="#0B2538", scrollbar_fg_color="#2B2B2B", corner_radius=0)
        self.scroll_parent.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.scroll_parent.grid_columnconfigure(2, weight=1)
        self.scroll_parent.grid_rowconfigure(2, weight=1)
        self.param_frame = ctk.CTkFrame(self.scroll_parent)
        self.param_frame.grid(row=0, column=0, columnspan=2, padx=(pads, 0), pady=(pads, 0), sticky="nsew")
        self.sim_fit_opt_frame = ctk.CTkFrame(self.scroll_parent)
        self.sim_fit_opt_frame.grid(row=1, rowspan=2, column=0, padx=(pads, 0), pady=(pads, 0), sticky="nsew")
        self.sim_fit_opt_frame.grid_columnconfigure((0,4), weight=1)
        self.sim_fit_opt_frame.grid_rowconfigure(4, weight=1)
        self.bnds_frame = ctk.CTkFrame(self.sim_fit_opt_frame, fg_color="transparent")
        self.bnds_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")
        self.bnds_frame.grid_columnconfigure((0, 1), weight=1)
        self.fit_focus_frame = ctk.CTkFrame(self.sim_fit_opt_frame, fg_color="transparent")
        self.fit_focus_frame.grid(row=5, column=0, columnspan=4, sticky="nsew")
        self.fit_focus_frame.grid_columnconfigure((0, 1), weight=1)
        self.procedure_frame = ctk.CTkFrame(self.scroll_parent)
        self.procedure_frame.grid(row=1, rowspan=2, column=1, padx=(pads, 0), pady=(pads, 0), sticky="nsew")
        self.prog_bar_frame = ctk.CTkFrame(self.scroll_parent)
        self.prog_bar_frame.grid(row=3, column=0, columnspan=2, padx=(pads, 0), pady=pads, sticky="nsew")
        self.prog_bar_frame.grid_columnconfigure((0, 1), weight=1)
        self.plot_adult_frame = ctk.CTkFrame(self.scroll_parent)
        self.plot_adult_frame.grid(row=0, column=2, rowspan=2, padx=pads, pady=(pads, 0), sticky="nsew")
        self.plot_adult_frame.grid_rowconfigure(0, weight=0)
        self.plot_adult_frame.grid_rowconfigure(1, weight=1)
        self.plot_adult_frame.grid_columnconfigure(0, weight=1)
        self.plot_options_frame = ctk.CTkFrame(self.plot_adult_frame, corner_radius=10, fg_color="transparent")
        self.plot_options_frame.grid(row=0, column=0, padx=pads/2, pady=(pads/2, 0), sticky="nsew")
        self.plot_options_frame.grid_columnconfigure((1, 6, 7), weight=1)
        self.plot_frame = ctk.CTkFrame(self.plot_adult_frame, fg_color="transparent")
        self.plot_frame.grid(row=1, column=0, sticky="nsew")
        self.console_frame = ctk.CTkFrame(self.scroll_parent)
        self.console_frame.grid(row=2, rowspan=2, column=2, padx=pads, pady=pads, sticky="nsew")
        self.console_frame.grid_columnconfigure(0, weight=1)


        # PARAMETER FRAME
        ctk.CTkLabel(self.param_frame, text="Fit?", font=(font_name, large_font_size)).grid(row=0, column=0, padx=(1.5*pads,pads), pady=pads, sticky="n")
        ctk.CTkLabel(self.param_frame, text="Link?", font=(font_name, large_font_size)).grid(row=0, column=1, padx=0, pady=pads, sticky="n")
        ctk.CTkLabel(self.param_frame, text="Top Ferromagnetic Layer", font=(font_name, large_font_size)).grid(row=0, column=2, columnspan=6, padx=pads, pady=pads, sticky="n")
        self.FM2_dMs = Parameter(self, self.param_frame, 1, "d*M\u209B", 6.25, 1, 40)
        self.FM2_dMs_calc = ThicknessMsCalculator(self.param_frame, 2, self.FM2_dMs)
        self.FM2_Hani_ip = Parameter(self, self.param_frame, 3, "Hani", 0, 0, 10)
        self.FM2_PhiAni_ip = Parameter(self, self.param_frame, 4, "\u03C6ani", 90, 0, 180)

        ctk.CTkLabel(self.param_frame, text="Non-magnetic Spacer Layer", font=(font_name, large_font_size)).grid(row=5, column=2, columnspan=6, padx=pads, pady=pads, sticky="n")
        self.J1 = Parameter(self, self.param_frame, 6, "J\u2081", -0.75, 0, -1.5, fit=True)
        self.J2 = Parameter(self, self.param_frame, 7, "J\u2082", -0.25, 0, -0.5, fit=True)
        
        ctk.CTkLabel(self.param_frame, text="Bottom Ferromagnetic Layer", font=(font_name, large_font_size)).grid(row=8, column=2, columnspan=6, padx=pads, pady=pads, sticky="n")
        self.FM1_dMs = Parameter(self, self.param_frame, 9, "d*M\u209B", 6.25, 1, 40)
        self.FM1_dMs_calc = ThicknessMsCalculator(self.param_frame, 10, self.FM1_dMs)
        self.FM1_Hani_ip = Parameter(self, self.param_frame, 11, "Hani", 0, 0, 10)
        self.FM1_PhiAni_ip = Parameter(self, self.param_frame, 12, "\u03C6ani", 90, 0, 180)


        # SIMULATION AND FIT PARAMETERS TABVIEW
        self.sim_fit_seg_but = ctk.CTkSegmentedButton(self.sim_fit_opt_frame, values=("Sim Options", "Fit Options"), command=self.sim_fit_opt_cb, font=(font_name, medium_font_size))
        self.sim_fit_seg_but.grid(row=0, column=0, columnspan=4, padx=pads, pady=pads, sticky="nsew")
        self.sim_fit_seg_but.set("Sim Options")

        # field direction in deg
        self.sim_phiH_label = tk.Text(self.sim_fit_opt_frame, width=5, height=1, borderwidth=0, foreground="#DCE4EE", background="#2B2B2B", font=(font_name, tk_text_font_size))
        self.sim_phiH_label.tag_configure("subscript", offset=-4, font=(font_name, tk_text_subscript))
        self.sim_phiH_label.insert("insert", u"\u03C6", "", "H", "subscript", " =")
        self.sim_phiH_label.configure(state="disabled")
        self.sim_phiH_label.grid(row=1, column=0, padx=(pads,0), pady=pads, sticky="e")

        self.sim_phiH = ctk.CTkEntry(self.sim_fit_opt_frame, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.sim_phiH.grid(row=1, column=1, padx=pads/2, pady=pads, sticky="w")
        self.sim_phiH.insert(0, 0)
        ctk.CTkLabel(self.sim_fit_opt_frame, text="°", font=(font_name, medium_font_size)).grid(row=1, column=2, padx=(0, 3*pads), pady=pads, sticky="w")

        # field steps in mT
        self.sim_dH_label = tk.Text(self.sim_fit_opt_frame, width=7, height=1, borderwidth=0, foreground="#DCE4EE", background="#2B2B2B", font=(font_name, tk_text_font_size))
        self.sim_dH_label.tag_configure("subscript", offset=-4, font=(font_name, tk_text_subscript))
        self.sim_dH_label.insert("insert", u"\u0394", "", u"\u03BC", "", "0", "subscript", "H =")
        self.sim_dH_label.configure(state="disabled")
        self.sim_dH_label.grid(row=2, column=0, padx=(pads,0), pady=pads, sticky="e")
        self.sim_dH = ctk.CTkEntry(self.sim_fit_opt_frame, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.sim_dH.grid(row=2, column=1, padx=pads/2, pady=pads, sticky="w")
        self.sim_dH.insert(0, 2.5)

        self.AFM_C_H_label = tk.Text(self.sim_fit_opt_frame, width=10, height=1, borderwidth=0, foreground="#DCE4EE", background="#2B2B2B", font=(font_name, tk_text_font_size))
        self.AFM_C_H_label.tag_configure("subscript", offset=-4, font=(font_name, tk_text_subscript))
        self.AFM_C_H_label.insert("insert", u"\u03BC", "", "0", "subscript", "H", "", "AFM-C", "subscript", " =")
        self.AFM_C_H_label.configure(state="disabled")
        self.AFM_C_H_label.grid(row=2, column=0, padx=(pads,0), pady=pads, sticky="e")
        self.AFM_C_H = ctk.CTkEntry(self.sim_fit_opt_frame, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.AFM_C_H.grid(row=2, column=1, padx=pads/2, pady=pads, sticky="w")
        self.AFM_C_H.insert(0, 0)
        self.AFM_C_H_label.grid_remove()
        self.AFM_C_H.grid_remove()

        ctk.CTkLabel(self.sim_fit_opt_frame, text="mT", font=(font_name, medium_font_size)).grid(row=2, column=2, padx=(0, 3*pads), pady=pads, sticky="w")
        
        # saturation field in mT
        self.sim_H_max_label = tk.Text(self.sim_fit_opt_frame, width=9, height=1, borderwidth=0, foreground="#DCE4EE", background="#2B2B2B", font=(font_name, tk_text_font_size))
        self.sim_H_max_label.tag_configure("subscript", offset=-4, font=(font_name, tk_text_subscript))
        self.sim_H_max_label.insert("insert", u"\u03BC", "", "0", "subscript", "H", "", "max", "subscript", " =")
        self.sim_H_max_label.configure(state="disabled")
        self.sim_H_max_label.grid(row=3, column=0, padx=(pads,0), pady=pads, sticky="e")
        self.sim_H_max = ctk.CTkEntry(self.sim_fit_opt_frame, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.sim_H_max.grid(row=3, column=1, padx=pads/2, pady=pads, sticky="w")
        self.sim_H_max.insert(0, 1000)

        self.C_FM_H_label = tk.Text(self.sim_fit_opt_frame, width=9, height=1, borderwidth=0, foreground="#DCE4EE", background="#2B2B2B", font=(font_name, tk_text_font_size))
        self.C_FM_H_label.tag_configure("subscript", offset=-4, font=(font_name, tk_text_subscript))
        self.C_FM_H_label.insert("insert", u"\u03BC", "", "0", "subscript", "H", "", "C-FM", "subscript", " =")
        self.C_FM_H_label.configure(state="disabled")
        self.C_FM_H_label.grid(row=3, column=0, padx=(pads,0), pady=pads, sticky="e")
        self.C_FM_H = ctk.CTkEntry(self.sim_fit_opt_frame, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.C_FM_H.grid(row=3, column=1, padx=pads/2, pady=pads, sticky="w")
        self.C_FM_H.insert(0, 500)
        self.C_FM_H_label.grid_remove()
        self.C_FM_H.grid_remove()

        ctk.CTkLabel(self.sim_fit_opt_frame, text="mT", font=(font_name, medium_font_size)).grid(row=3, column=2, padx=(0, 3*pads), pady=pads, sticky="w")

        # BOUNDARIES CHECKBOX FRAME
        self.full_hyst_check = ctk.CTkCheckBox(self.bnds_frame, text="", width=pads, onvalue="on", offvalue="off")
        self.full_hyst_check.grid(row=0, column=0, padx=(2*pads, 0), pady=pads, sticky="e")
        self.full_hyst_check_txt = ctk.CTkLabel(self.bnds_frame, text="Calculate Full Hysteresis?", font=(font_name, medium_font_size), anchor=tk.CENTER)
        self.full_hyst_check_txt.grid(row=0, column=1, padx=pads, pady=pads, sticky="w")

        self.use_bnds_check = ctk.CTkCheckBox(self.bnds_frame, text="", width=pads, onvalue="on", offvalue="off")
        self.use_bnds_check.grid(row=1, column=0, padx=(2*pads, 0), pady=pads, sticky="e")
        self.use_bnds_check.select()
        self.use_bnds_check.configure(state="disabled") # TODO: allow disabling of boundaries in the future (need to adjust fit function accordingly)
        self.use_bnds_check_txt = ctk.CTkLabel(self.bnds_frame, text="Use Boundaries for Fit?", font=(font_name, medium_font_size), anchor=tk.CENTER)
        self.use_bnds_check_txt.grid(row=1, column=1, padx=pads, pady=pads, sticky="w")
        self.use_bnds_check.grid_remove()
        self.use_bnds_check_txt.grid_remove()

        self.fit_focus_txt = ctk.CTkLabel(self.fit_focus_frame, text="Focus Fit on region", font=(font_name, medium_font_size))
        self.fit_focus_txt.grid(row=0, column=0, padx=(2*pads, 0), pady=pads, sticky="w")
        self.fit_focus = ctk.CTkComboBox(self.fit_focus_frame, values=["none", "AFM", "C", "FM"], width=80, state="readonly")
        self.fit_focus.grid(row=0, column=1, padx=(0, pads), pady=pads, sticky="w")
        self.fit_focus.set("none")
        self.fit_focus_frame.grid_remove()

        # FIT PROCEDURE
        ctk.CTkLabel(self.procedure_frame, text="Simulation / Fit Procedure", font=(font_name, large_font_size), anchor=tk.CENTER).grid(row=0, column=0, columnspan=3, padx=pads, pady=pads, sticky="n")
        
        ctk.CTkLabel(self.procedure_frame, text="0. Load previous Parameters", font=(font_name, medium_font_size), anchor=tk.CENTER).grid(row=1, column=0, padx=(2*pads,pads), pady=pads, sticky="nw")
        self.load_paras_but = ctk.CTkButton(self.procedure_frame, text="Load Parameters", font=(font_name, small_font_size), command=self.loadParameters)
        self.load_paras_but.grid(row=1, column=1, padx=pads, pady=pads, sticky="n")

        # Enter nominell, total film thickness
        self.more_frames = ctk.CTkFrame(self.procedure_frame, fg_color="transparent")
        self.more_frames.grid(row=2, column=0, columnspan=3, sticky="nsew")
        ctk.CTkLabel(self.more_frames, text="1. Enter total Ms =", font=(font_name, medium_font_size), anchor=tk.CENTER).grid(row=0, column=0, padx=(2*pads,0), pady=pads, sticky="nw")
        self.Ms_tot_nom = ctk.CTkEntry(self.more_frames, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.Ms_tot_nom.grid(row=0, column=1, padx=pads/2, pady=pads, sticky="e")
        ctk.CTkLabel(self.more_frames, text="kA/m and total d =", font=(font_name, medium_font_size), anchor=tk.CENTER).grid(row=0, column=2, padx=0, pady=pads, sticky="w")
        self.d_tot_nom = ctk.CTkEntry(self.more_frames, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.d_tot_nom.grid(row=0, column=3, padx=pads/2, pady=pads, sticky="e")
        ctk.CTkLabel(self.more_frames, text="nm", font=(font_name, medium_font_size)).grid(row=0, column=4, padx=(0, pads), pady=pads, sticky="w")

        # Load exp. data
        ctk.CTkLabel(self.procedure_frame, text="2. Load exp. M(H) data", font=(font_name, medium_font_size), anchor=tk.CENTER).grid(row=3, column=0, padx=(2*pads,pads), pady=pads, sticky="nw")
        self.load_data_button = ctk.CTkButton(self.procedure_frame, text="Load exp. Data", font=(font_name, small_font_size), command=self.loadData)
        self.load_data_button.grid(row=3, column=1, padx=pads, pady=pads, sticky="n")
        self.remove_data_button = ctk.CTkButton(self.procedure_frame, text="Remove exp. Data", font=(font_name, small_font_size), command=self.removeData)
        self.remove_data_button.grid(row=3, column=2, padx=(pads, 2*pads), pady=pads, sticky="n")

        # Simulate hysteresis
        ctk.CTkLabel(self.procedure_frame, text="3. Simulate hysteresis", font=(font_name, medium_font_size), anchor=tk.CENTER).grid(row=4, column=0, padx=(2*pads,pads), pady=pads, sticky="nw")
        self.sim_but = ctk.CTkButton(self.procedure_frame, text="Simulate", font=(font_name, small_font_size), command=self.newThreadMHsim)
        self.sim_but.grid(row=4, column=1, padx=pads, pady=pads, sticky="n")
        self.remove_sim_but = ctk.CTkButton(self.procedure_frame, text="Remove Sim", font=(font_name, small_font_size), command=self.removeSim)
        self.remove_sim_but.grid(row=4, column=2, padx=(pads, 2*pads), pady=pads, sticky="n")
        
        # Fit hysteresis
        ctk.CTkLabel(self.procedure_frame, text="4. Fit selected parameters", font=(font_name, medium_font_size), anchor=tk.CENTER).grid(row=5, column=0, padx=(2*pads,pads), pady=pads, sticky="nw")
        self.fit_prec = ctk.CTkComboBox(self.procedure_frame, width=135, values=("fast fit", "precise fit"), state="readonly")
        self.fit_prec.grid(row=5, column=1, padx=pads, pady=pads, sticky="n")
        self.fit_prec.set("fast fit")      
        self.fit_button = ctk.CTkButton(self.procedure_frame, text="Run Fit", font=(font_name, small_font_size), command=self.newThreadMHfit)
        self.fit_button.grid(row=5, column=2, padx=(pads, 2*pads), pady=pads, sticky="n")
        
        # Export data
        ctk.CTkLabel(self.procedure_frame, text="5. Save the result", font=(font_name, medium_font_size), anchor=tk.CENTER).grid(row=6, column=0, padx=(2*pads,pads), pady=(pads, 2*pads), sticky="nw")
        self.export_MH_curve = ctk.CTkButton(self.procedure_frame, text="Export Plot", font=(font_name, small_font_size), command=self.exportPlotData)
        self.export_MH_curve.grid(row=6, column=1, padx=pads, pady=(pads, 2*pads), sticky="n")
        self.export_parameters = ctk.CTkButton(self.procedure_frame, text="Export Parameters", font=(font_name, small_font_size), command=self.exportParameters)
        self.export_parameters.grid(row=6, column=2, padx=(pads, 2*pads), pady=(pads, 2*pads), sticky="n")

        self.disable_buttons = [self.load_paras_but, self.load_data_button, self.remove_data_button, self.sim_but, self.remove_sim_but, self.fit_button, self.export_MH_curve, self.export_parameters]

        # PROGRESS BAR
        self.kill_thread_but = ctk.CTkButton(self.prog_bar_frame, text="Stop Sim / Fit", font=(font_name, small_font_size), command=self.stopDaemon)
        self.kill_thread_but.grid(row=0, column=1, padx=(pads, 2*pads), pady=pads, sticky="n")
        self.prog_bar_label = ctk.CTkLabel(self.prog_bar_frame, text="Simulation Progress Bar", width=200, font=(font_name, medium_font_size), anchor=tk.CENTER)
        self.prog_bar_label.grid(row=0, column=2, padx=pads, pady=pads, sticky="e")
        self.prog_bar = ctk.CTkProgressBar(self.prog_bar_frame, height=15, width=500)
        self.prog_bar.grid(row=0, column=3, padx=pads, pady=pads, sticky="w")
        self.prog_bar.set(0)

        # PLOT OPTIONS FRAME
        self.plot_seg_but = ctk.CTkSegmentedButton(self.plot_options_frame, values=("Hysteresis", "Macrospin Rotation", "Energy Landscape"), command=self.drawPlot, font=(font_name, medium_font_size))
        self.plot_seg_but.grid(row=0, column=0, columnspan=4, padx=pads, pady=(2*pads,0), sticky="w")
        self.plot_seg_but.set("Hysteresis")

        ctk.CTkLabel(self.plot_options_frame, text="FOM: ", font=(font_name, medium_font_size), anchor=tk.CENTER).grid(row=0, column=6, padx=pads, pady=(pads, 0), sticky="e")
        self.FOM_label = ctk.CTkLabel(self.plot_options_frame, text="-------", font=(font_name, medium_font_size), anchor=tk.CENTER)
        self.FOM_label.grid(row=0, column=7, padx=pads, pady=(pads, 0), sticky="w")

        ctk.CTkLabel(self.plot_options_frame, text="Choose Field Value:", font=(font_name, medium_font_size)).grid(row=1, column=0, padx=(2*pads, 0), pady=(pads, 0), sticky="e")
        ctk.CTkButton(self.plot_options_frame, width=15, text="-", font=(font_name, large_font_size), corner_radius=50, command=self.slider_decrease).grid(row=1, column=1, padx=pads, pady=(pads, 0), sticky="e")
        self.EnergyFieldSlider = ctk.CTkSlider(self.plot_options_frame, from_=100, to=0, number_of_steps=3, width=333, command=self.calcEnergyLandscape)
        self.EnergyFieldSlider.grid(row=1, column=2, padx=0, pady=(pads, 0), sticky="e")
        self.EnergyFieldSlider.set(0)
        ctk.CTkButton(self.plot_options_frame, width=15, text="+", font=(font_name, large_font_size), corner_radius=50, command=self.slider_increase).grid(row=1, column=3, padx=pads, pady=(pads, 0), sticky="w")
        self.EnergyFieldEntry = ctk.CTkEntry(self.plot_options_frame, font=(font_name, medium_font_size), width=entry_w, state="disabled")
        self.EnergyFieldEntry.grid(row=1, column=4, padx=(pads, pads/2), pady=(pads, 0), sticky="e")
        ctk.CTkLabel(self.plot_options_frame, text="mT", font=(font_name, medium_font_size)).grid(row=1, column=5, padx=(0, pads), pady=(pads, 0), sticky="w")
        self.EnergyFieldValue = 0
        self.cover_frame = ctk.CTkFrame(self.plot_options_frame, height=0)
        self.cover_frame.grid(row=1, column=0, columnspan=7, padx=pads, pady=(pads, 0), sticky="nsew")

        self.loaded_file_label = ctk.CTkLabel(self.plot_options_frame, text="Loaded data file:", font=(font_name, medium_font_size))
        self.loaded_file_label.grid(row=2, column=0, columnspan=7, padx=(2*pads, pads), pady=(pads, 0), sticky="w")


        # PLOT FRAME
        self.fig = plt.figure(figsize=(GUI_scale*8, GUI_scale*7.5))
        self.fig_ax = self.fig.add_subplot(111)
        self.fig_ax.set_ylabel("d*M (mA)", fontsize=12)
        self.fig_ax.set_xlabel("µ{0}H (T)".format(chr(0x2080)), fontsize=12)
        self.fig_ax.set_title("Magnetic Hysteresis", fontsize=13)
        self.fig.set_facecolor("#2B2B2B")
        self.fig_ax.set_facecolor("#2B2B2B")
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.config(background="#828282")
        self.toolbar._message_label.config(background="#828282")
        self.toolbar.update()

        self.canvas._tkcanvas.pack(expand=True)
        self.axhline = self.fig_ax.axhline(0, color="#D3D3D3", linestyle="--", linewidth=1)
        self.axvline = self.fig_ax.axvline(0, color="#D3D3D3", linestyle="--", linewidth=1)


        # CONSOLE FRAME
        self.console = ctk.CTkTextbox(self.console_frame, font=(font_name, medium_font_size), border_spacing=7, wrap="word", fg_color="transparent")
        self.console.grid(row=0, column=0, sticky="nsew")
        self.console.insert("0.0", "Console output:")
        self.console.configure(state="disabled")


        # initialize some self parameters
        self.param_list = [self.FM2_dMs, self.FM2_Hani_ip, self.FM2_PhiAni_ip, 
                           self.J1, self.J2, 
                           self.FM1_dMs, self.FM1_Hani_ip, self.FM1_PhiAni_ip,
                           self.sim_phiH, self.sim_H_max, self.sim_dH]
        self.dMs_linked = {"master": -1,
                           "follower": -1}
        self.param_values = [0] * len(self.param_list)
        self.param_l_bnds = [param.getLowerBound() for param in self.param_list if type(param) == Parameter]
        self.param_u_bnds = [param.getUpperBound() for param in self.param_list if type(param) == Parameter]
        self.exp_H, self.sim_H = [], []
        self.phiA, self.phiB = [], []
        self.cur_plot = "M(H)"
        self.stopDaemon_bool = False

        if screen_size.height > 1080:
            self.eval("tk::PlaceWindow . center")


    def writeConsole(self, input):
        cur_time = datetime.now()
        cur_time = cur_time.strftime("%H:%M:%S")
        cur_txt = self.console.get("0.0", "end")
        new_txt = cur_txt + str(cur_time) + "\t" + input
        self.console.configure(state="normal")
        self.console.delete("0.0", "end")
        self.console.insert("0.0", new_txt)
        self.console.configure(state="disabled")
        self.console.see("end")


    def sim_fit_opt_cb(self, value):
        if value == "Fit Options":
            self.sim_dH_label.grid_remove()
            self.sim_dH.grid_remove()
            self.AFM_C_H_label.grid()
            self.AFM_C_H.grid()
            self.sim_H_max_label.grid_remove()
            self.sim_H_max.grid_remove()
            self.C_FM_H_label.grid()
            self.C_FM_H.grid()
            self.use_bnds_check.grid()
            self.use_bnds_check_txt.grid()
            self.fit_focus_frame.grid()
        elif value == "Sim Options":
            self.sim_dH_label.grid()
            self.sim_dH.grid()
            self.AFM_C_H_label.grid_remove()
            self.AFM_C_H.grid_remove()
            self.sim_H_max_label.grid()
            self.sim_H_max.grid()
            self.C_FM_H_label.grid_remove()
            self.C_FM_H.grid_remove()
            self.use_bnds_check.grid_remove()
            self.use_bnds_check_txt.grid_remove()
            self.fit_focus_frame.grid_remove()


    def updateCheckboxes(self, row, type):
        if row == 1:    (clicked, linked_to) = (0, 5)
        elif row == 9:  (clicked, linked_to) = (5, 0)
        else:           return

        if type == "link":
            if self.param_list[clicked].getLinkCheckbox() == "on":
                self.param_list[clicked].setLinkFollower()
                self.param_list[linked_to].setLinkMaster()
                self.dMs_linked["master"] = linked_to
                self.dMs_linked["follower"] = clicked
            elif self.param_list[clicked].getLinkCheckbox() == "off":
                self.removeLinks()
        elif type == "fit":
            if self.param_list[clicked].getFitCheckbox() == "on" and self.param_list[clicked].getLinkCheckbox() == "on":
                self.removeLinks()


    def removeLinks(self):
        self.param_list[0].resetLinkBox()
        self.param_list[5].resetLinkBox()
        self.dMs_linked["master"] = -1
        self.dMs_linked["follower"] = -1


    def drawPlot(self, plot_type, rescale=True):
        if plot_type == "Hysteresis":
            self.plot_seg_but.set("Hysteresis")
            self.cover_frame.grid()
            self.drawMHplots(rescale)
        elif plot_type == "Macrospin Rotation":
            self.plot_seg_but.set("Macrospin Rotation")
            self.cover_frame.grid()
            self.drawMacrospinRotPlot()
        elif plot_type == "Energy Landscape":
            self.plot_seg_but.set("Energy Landscape")
            self.cover_frame.grid_remove()
            self.drawEnergyPlot()


    def drawMHplots(self, rescale=True):
        cur_xlim = self.fig_ax.get_xlim()
        cur_ylim = self.fig_ax.get_ylim()
        if cur_xlim == cur_ylim == (0, 1):
            rescale = True
        self.cur_plot = "M(H)"
        self.fig_ax.clear()
        self.axhline = self.fig_ax.axhline(0, color="#D3D3D3", linestyle="--", linewidth=1)
        self.axvline = self.fig_ax.axvline(0, color="#D3D3D3", linestyle="--", linewidth=1)
        try:
            self.g_colorbar.ax.clear()
            self.g_colorbar.ax.remove()
        except:
            pass
        self.fig_ax.set_title("Magnetic Hysteresis", fontsize=13)
        self.fig_ax.set_ylabel("d*M (mA)", fontsize=12)
        self.fig_ax.set_xlabel("µ{0}H (T)".format(chr(0x2080)), fontsize=12)
        if len(self.exp_H) > 0:
            x_max = max(self.exp_H) * 1.1
            xlim = (-x_max, x_max) if rescale == True else cur_xlim
            self.fig_ax.set_xlim(xlim)
        elif len(self.sim_H) > 0:
            x_max = max(self.sim_H) * 1.1
            xlim = (-x_max, x_max) if rescale == True else cur_xlim
            self.fig_ax.set_xlim(xlim)

        # exp. data
        try:
            self.exp_plot = self.fig_ax.plot(self.exp_H, self.exp_M_plot, color=exp_color, marker="o", markersize=4, label="exp")
            ylim = (1.1 * min(self.exp_M_plot), 1.1 * max(self.exp_M_plot)) if rescale == True else cur_ylim
            self.fig_ax.set_ylim(ylim)
        except:
            pass

        # simulation with analytical model
        try:
            self.sim_plot = self.fig_ax.plot(self.sim_H, self.sim_M_plot, color=sim_color, marker="o", markersize=4, label="sim")
            ylim = (1.1 * min(self.sim_M_plot), 1.1 * max(self.sim_M_plot)) if rescale == True else cur_ylim
            self.fig_ax.set_ylim(ylim)
        except:
            pass
        
        legend = self.fig_ax.legend()
        if len(legend.legend_handles) == 0:
            legend.remove()
        self.fig.canvas.draw()

    
    def drawMacrospinRotPlot(self):
        self.fig_ax.clear()
        try:
            self.g_colorbar.ax.clear()
            self.g_colorbar.ax.remove()
        except:
            pass
        self.axhline = self.fig_ax.axhline(0, color="#D3D3D3", linestyle="--", linewidth=1)
        self.axvline = self.fig_ax.axvline(0, color="#D3D3D3", linestyle="--", linewidth=1)
        self.cur_plot = "macrospins"

        self.fig_ax.set_title("Macrospin Angles", fontsize=13)
        self.fig_ax.set_ylabel("phi (°)", fontsize=12)
        self.fig_ax.set_ylim(-200, 200)
        self.fig_ax.set_xlabel("µ{0}H (T)".format(chr(0x2080)), fontsize=12)
        if len(self.exp_H) > 0:
            x_max = max(self.exp_H) * 1.1
            self.fig_ax.set_xlim(-x_max, x_max)
        elif len(self.sim_H) > 0:
            x_max = max(self.sim_H) * 1.1
            self.fig_ax.set_xlim(-x_max, x_max)

        # if only down sweep was calculated, lets just display down sweep
        try:
            if len(self.sim_H) != len(self.phiA) and len(self.sim_H) != len(self.phiB):
                sim_H_plot = self.sim_H[:len(self.phiA)]
            else:
                sim_H_plot = self.sim_H
        except:
            pass

        if len(self.phiA) > 0:
            self.phiA_plot = self.fig_ax.plot(sim_H_plot, self.phiA, color=phiA_color, marker="o", markersize=5, label="Top FM")
            self.phiB_plot = self.fig_ax.plot(sim_H_plot, self.phiB, color=phiB_color, marker="x", markersize=5, label="Bottom FM")
        
        legend = self.fig_ax.legend()
        if len(legend.legend_handles) == 0:
            legend.remove()
        self.fig.canvas.draw()


    def drawEnergyPlot(self):
        self.updateParamValues()
        if len(self.phiA) > 0:
            steps = len(self.phiA)
        else:
            steps = 100
        self.EnergyFieldSlider.configure(number_of_steps=steps-1, from_=steps-1)

        self.fig_ax.set_title("Energy Landscape", fontsize=13)
        self.fig_ax.set_ylabel("phi top (°)", fontsize=12)
        self.fig_ax.set_ylim(-180, 180)
        self.fig_ax.set_xlabel("phi bot (°)", fontsize=12)
        self.fig_ax.set_xlim(-180, 180)

        self.calcEnergyLandscape(self.EnergyFieldSlider.get())


    def calcEnergyLandscape(self, index):
        self.fig_ax.clear()
        self.fig_ax.set_title("Energy Landscape", fontsize=13)
        self.fig_ax.set_ylabel("phi top (°)", fontsize=12)
        self.fig_ax.set_ylim(-180, 180)
        self.fig_ax.set_xlabel("phi bot (°)", fontsize=12)
        self.fig_ax.set_xlim(-180, 180)
        try:
            self.g_colorbar.ax.clear()
            self.g_colorbar.ax.remove()
        except:
            pass

        i = int(index)
        if len(self.sim_H) == 0 or self.sim_H[i] == self.EnergyFieldValue:
            self.fig.canvas.draw()
            return
        self.EnergyFieldValue = round(self.sim_H[i] * 1e3, 2)   # mT
        self.EnergyFieldEntry.configure(state="normal")
        self.EnergyFieldEntry.delete(0, "end")
        self.EnergyFieldEntry.insert(0, str(self.EnergyFieldValue))
        self.EnergyFieldEntry.configure(state="disabled")
        title = "Energy Landscape at " + str(self.EnergyFieldValue) + " mT"
        self.fig_ax.set_title(title, fontsize=13)
        
        g_calc = MacrospinModel(gui=root, h_sweep=[], param_values=self.param_values)
        g = []
        phi = np.linspace(-np.pi, np.pi, num=120)
        for phi_k in phi:
            gi, dg = g_calc.get_G(phis=(phi_k, phi), h=1e-3*self.EnergyFieldValue)
            g.append(gi)
        x, y = np.meshgrid(np.arange(-180, 180, 3), np.arange(-180, 180, 3))
        g_min, g_max = np.array(g).min(), np.array(g).max()
        self.g_plot = self.fig_ax.pcolormesh(x, y, g, cmap='RdBu', vmin=g_min, vmax=g_min/1.5)
        divider = make_axes_locatable(self.fig_ax)
        cax = divider.append_axes("right", size="5%", pad=0.3)
        self.g_colorbar = plt.colorbar(self.g_plot, cax=cax)
        self.g_colorbar.ax.set_ylabel("normed energy", rotation=270, labelpad=2*pads, size=0.8*small_font_size)
        self.g_plot_marker = self.fig_ax.plot(self.phiB[i], self.phiA[i], "o")

        legend = self.fig_ax.legend()
        if len(legend.legend_handles) == 0:
            legend.remove()
        self.fig.canvas.draw()


    def slider_decrease(self):
        new_Slider_value = int(self.EnergyFieldSlider.get()) + 1
        self.EnergyFieldSlider.set(new_Slider_value)
        self.calcEnergyLandscape(new_Slider_value)


    def slider_increase(self):
        new_Slider_value = int(self.EnergyFieldSlider.get()) - 1
        self.EnergyFieldSlider.set(new_Slider_value)
        self.calcEnergyLandscape(new_Slider_value)


    def loadData(self):
        try:
            self.d_tot_nom_val = float(self.d_tot_nom.get()) * 1e-9 # total FM thickness in m
        except:
            self.writeConsole("You can't load experimental data until you entered the total thickness of the sample in Step 1. in Simulation/Fit Procedure.")
            return
        exp_data_filename = tk.filedialog.askopenfilename(parent=self, initialdir=os.getcwd())
        if exp_data_filename == "": return
        try:
            self.exp_H, self.exp_M = np.loadtxt(exp_data_filename, dtype=np.float64, usecols=(0,1), unpack=True, skiprows=2)
            with open(exp_data_filename, "r") as f:
                lines = f.readlines()
                if " " not in lines[1]:
                    units = lines[1].split("\t")
                else:
                    units = lines[1].split(" ")
                    units = [unit.replace("\n", "") for unit in units]

            units = [x for x in units if x != ""]   # remove all "" entries from units
            self.exp_H_unit = units[0]
            self.exp_M_unit = units[1]

            # want exp_H in T
            if "Oe" in self.exp_H_unit:
                self.exp_H = [x/1e4 for x in self.exp_H]
            elif "mT" in self.exp_H_unit:
                self.exp_H = [x/1e3 for x in self.exp_H]
            elif "T" not in self.exp_H_unit:
                self.writeConsole("Magnetic field values H of loaded data are neither in units of Oe, mT nor T. Loading data aborted.")
                self.exp_H, self.exp_M = [], []
                return
            
            # want exp_M in A unit (d*M)
            if "kA/m" in self.exp_M_unit:
                self.exp_M = [1e3 * m * self.d_tot_nom_val for m in self.exp_M]
                self.exp_M_unit = "A"
            elif "A/m" in self.exp_M_unit:
                self.exp_M = [m * self.d_tot_nom_val for m in self.exp_M]
                self.exp_M_unit = "A"
            else:
                self.writeConsole("Magnetization values M of loaded data are neither in units of kA/m nor A/m. Loading data aborted.")
                self.exp_H, self.exp_M = [], []
                return
            self.exp_M_plot = [1e3 * m for m in self.exp_M] # plot d*M in mA units

            # I want a list of the H step density for FOM weighting later on
            self.exp_H_steps = []
            for i in range(len(self.exp_H)):
                if i == 0:
                    dH = 2 * np.abs(self.exp_H[i] - self.exp_H[i+1])
                elif i == len(self.exp_H)-1:
                    dH = 2 * np.abs(self.exp_H[i-1] - self.exp_H[i])
                else:
                    dH = np.abs(self.exp_H[i-1] - self.exp_H[i]) + np.abs(self.exp_H[i] - self.exp_H[i+1])
                self.exp_H_steps.append(dH)

            self.drawPlot("Hysteresis")
            filename = exp_data_filename.split("/")
            filename = filename[-1]
            self.loaded_file_label.configure(text="Loaded data file: " + filename)
        except Exception as err:
            self.writeConsole("Error: Exp. data could not be loaded. Make sure you chose the correct file and it is structured correctly (see documentation).")      


    def removeData(self):
        self.exp_H = []
        self.exp_M = []
        self.loaded_file_label.configure(text="Loaded data file: ")
        try:
            self.exp_plot.pop(0).remove()
            self.fig_ax.legend().remove()
            self.fig.canvas.draw()
        except:
            pass


    def removeSim(self):
        self.sim_H, self.sim_M, self.phiA, self.phiB = [], [], [], []
        self.drawPlot(self.plot_seg_but.get())

            
    def getSim_H_sweep(self):
        try:
            max_H = float(self.sim_H_max.get()) / 1e3
            H_steps = float(self.sim_dH.get()) / 1e3
            nmr_of_steps = int(2*max_H/H_steps)
            if self.full_hyst_check.get() == "off":
                sim_H_sweep = np.linspace(max_H, -max_H, nmr_of_steps)
            elif self.full_hyst_check.get() == "on":
                sim_H_down_sweep = np.linspace(max_H, -max_H, nmr_of_steps)
                sim_H_up_sweep = np.linspace(-max_H, max_H, nmr_of_steps)
                sim_H_sweep = np.append(sim_H_down_sweep, sim_H_up_sweep)
            return sim_H_sweep
        except:
            pass


    def updateParamValues(self):
        # update total, nominal values of Ms and d of the whole layerstack
        try:    self.Ms_tot_nom_val = round(float(self.Ms_tot_nom.get()) * 1e3, 13)     # total, nominal Ms in A/m
        except: self.Ms_tot_nom_val = 0
        try:    self.d_tot_nom_val = round(float(self.d_tot_nom.get()) * 1e-9, 13)     # total, nominal FM thickness in m
        except: self.d_tot_nom_val = 0
        self.exp_dMs = self.Ms_tot_nom_val * self.d_tot_nom_val * 1e3   # in mA
        if self.exp_dMs == 0: self.removeLinks()


        # if both d*Ms parameters are linked to each other, we need to update them accordingly
        if -1 not in self.dMs_linked.values():
            m_id = self.dMs_linked["master"]
            f_id = self.dMs_linked["follower"]
            value_diff = self.exp_dMs - self.param_list[m_id].getValue()
            self.param_list[f_id].param_value.configure(state="normal")
            self.param_list[f_id].setValue(value_diff)
            self.param_list[f_id].param_value.configure(state="disabled")

        for i, param in enumerate(self.param_list):
            if type(param) == Parameter:
                param.updateSliderRange()
                self.param_values[i] = param.getValue()
                self.param_l_bnds[i] = param.getLowerBound()
                self.param_u_bnds[i] = param.getUpperBound()
                if self.param_values[i] == None:
                    continue
                if i in (0, 5):     
                    self.param_values[i] *= 1e-3     # d*Ms from mA to A
                    self.param_l_bnds[i] *= 1e-3
                    self.param_u_bnds[i] *= 1e-3
                elif i in (1, 3, 4, 6):     
                    self.param_values[i] *= 1e-3    # Hani from mT to T and J1 or J2 from mJ/m^2 to J/m^2
                    self.param_l_bnds[i] *= 1e-3
                    self.param_u_bnds[i] *= 1e-3
                elif i in (2, 7):
                    self.param_values[i] *= (np.pi/180) # phiani from deg to rad
                    self.param_l_bnds[i] *= (np.pi/180)
                    self.param_u_bnds[i] *= (np.pi/180)
            else:
                self.param_values[i] = float(param.get())
                if i == 8:
                    self.param_values[i] *= (np.pi/180) # phiH from deg to rad
                elif i in (9, 10):
                    self.param_values[i] *= 1e-3    # sim µ0H and dµ0H from mT to T
             

    def updateFOM(self):
        if len(self.exp_H) == 0:
            self.FOM_label.configure(text="-------")
            return
        
        # updates FOM in the GUI
        try:
            FOM = self.getFOM(self.sim_M)
            FOM = str(FOM.round(8))
            self.FOM_label.configure(text=FOM)
        except Exception as err:
            self.writeConsole("Update FOM Error: " + str(err))
            self.FOM_label.configure(text="-------")


    def getFOM(self, sim_M):
        # calculates the Figure of Merit (FOM) of the Simulations / Fits
        try:
            # try/except to check if H1 and H2 is given
            H1 = float(self.AFM_C_H.get()) / 1e3    # T
            H2 = float(self.C_FM_H.get()) / 1e3     # T
            FM, C, AFM = [], [], []
            for i, h in enumerate(self.exp_H):
                if H2 <= np.abs(h):
                    # Ferromagnetic (FM) region
                    FM.append(i)
                elif H1 < np.abs(h) < H2:
                    # Canted (C) region
                    C.append(i)
                elif np.abs(h) <= H1:
                    # Antiferromagnetic (AFM) region
                    AFM.append(i)
            
            max_H_steps = max(self.exp_H_steps)
            FM_M_dif = [np.abs((self.exp_H_steps[i]/max_H_steps) * (1 - sim_M[i]/self.exp_M[i])) for i in FM]
            C_M_dif = [np.abs((self.exp_H_steps[i]/max_H_steps) * (1 - sim_M[i]/self.exp_M[i])) for i in C]
            AFM_M_dif = [np.abs((self.exp_H_steps[i]/max_H_steps) * (1 - sim_M[i]/self.exp_M[i])) for i in AFM]

            # if we want to focus on a region, we just put some weight on their FOM
            if self.fit_focus.get() == "FM": FM_M_dif *= 3
            if self.fit_focus.get() == "C": C_M_dif *= 3
            if self.fit_focus.get() == "AFM": AFM_M_dif *= 3

            FOM = (sum(FM_M_dif) + sum(C_M_dif) + sum(AFM_M_dif))/len(self.exp_H)
        except:
            M_dif = [(self.exp_H_steps[i]/max(self.exp_H_steps)) * np.abs(1 - sim_M[i]/self.exp_M[i]) for i in range(len(self.exp_M))]
            FOM = sum(M_dif)/len(self.exp_M)
                
        return FOM


    def stopDaemon(self):
        self.stopDaemon_bool = True
        
        for button in self.disable_buttons:
            button.configure(state="normal")


    def newThreadMHsim(self):
        self.stopDaemon_bool = False
        threading.Thread(target=self.MHsim, daemon=True).start()
    def MHsim(self):
        for button in self.disable_buttons:
            button.configure(state="disabled")
        self.updateParamValues()

        if None in self.param_values or (self.param_values[4] == 0 and self.param_values[5] == 0):
            # None is in self.param_values if some parameter value cannot be floated
            # If both J1 and J2 are zero the simulation doesnt work
            return
        
        # get correct field sweep to simulate
        if len(self.exp_H) == 0:
            self.sim_H = self.getSim_H_sweep()
        elif self.full_hyst_check.get() == "off":
            i = np.where(self.exp_H == min(self.exp_H)) if isinstance(self.exp_H, np.ndarray) else self.exp_H.index(min(self.exp_H))
            self.sim_H = self.exp_H[:i+1] if isinstance(i, int) else self.exp_H[:min(i[0])+1]
        else:
            self.sim_H = self.exp_H
        
        MH_sim = MacrospinModel(gui=root, h_sweep=self.sim_H, param_values=self.param_values)
        self.sim_M, self.phiA, self.phiB = MH_sim.calculateMH()   # simulate M(H)

        # check if only down field sweep was simulated
        # if so, get up field sweep by mirroring down sweep (this is only gives the correct hysteresis if it is symmetric)
        if self.full_hyst_check.get() == "off":
            H_up_sweep = [-h for h in self.sim_H]
            self.sim_H = np.append(self.sim_H, H_up_sweep)
            M_up_sweep = [-m for m in self.sim_M]
            self.sim_M = np.append(self.sim_M, M_up_sweep)

        # i dont even know what this if clause is for
        if len(self.sim_M) > 0:
            self.sim_M_plot = [1e3 * m for m in self.sim_M] # plot d*M in mA units
            self.updateFOM()
            self.drawPlot("Hysteresis", rescale=False)

        for button in self.disable_buttons:
            button.configure(state="normal")


    def newThreadMHfit(self):
        self.stopDaemon_bool = False
        threading.Thread(target=self.MHfit, daemon=True).start()
    def MHfit(self):
        self.updateParamValues()

        if len(self.exp_H) == 0 or None in self.param_values or (self.param_values[3] == 0 and self.param_values[4] == 0):
            # If there is no exp data, nothing can be fitted
            # None is in self.param_values if some parameter value cannot be floated
            # If both J1 and J2 are zero the simulation doesnt work
            return

        # get parameters, which should be fitted, and also their boundaries
        fit_paras, fit_para_ind, bnds = [], [], []
        for i, param in enumerate(self.param_list):
            if i == 8:
                break
            if param.getFitCheckbox() == "on":
                fit_paras.append(self.param_values[i])
                self.param_values[i] = None     # remove parameters which should be fitted from self.param_values
                fit_para_ind.append(i)
                bnds.append([self.param_l_bnds[i], self.param_u_bnds[i]])
        if self.use_bnds_check.get() == "on":
            bnds = bnds
        else:
            bnds = None

        if None not in self.param_values:   
            # if no fit parameter is checked on to be fitted, there is nothing to fit
            self.MHsim()
            return
        
        for button in self.disable_buttons:
            button.configure(state="disabled")

        self.sim_H = self.exp_H.copy()     # needed for plotting purposes
        MH_fit = MacrospinModel(gui=root, h_sweep=self.exp_H, param_values=self.param_values, exp_M=self.exp_M, fit_paras=fit_paras,
                                fit_para_ind=fit_para_ind, fit_type=self.fit_prec.get(), bnds=bnds, full_hyst=self.full_hyst_check.get())
        
        # if both d*Ms parameters are linked to each other AND we want to fit one of them, we need to update the other one accordingly during the fitting process
        # please ignore the ugly hard coding :)
        if -1 not in self.dMs_linked.values() and (0 in fit_para_ind or 5 in fit_para_ind):
            m_id = self.dMs_linked["master"]
            f_id = self.dMs_linked["follower"]
            MH_fit.addLinkedParas(sum=self.exp_dMs*1e-3, master=m_id, follower=f_id)

        fitted_paras = MH_fit.fit()    # fit M(H) to exp data
        if len(fitted_paras) == 0:
            for button in self.disable_buttons:
                button.configure(state="normal")
            return

        # do final simulation with final fit parameters
        for i in fit_para_ind:
            if i in (2, 7):
                fitted_paras[0] *= (180/np.pi) # phiani from pi values to deg
            else:   
                fitted_paras[0] *= 1e3    # d*Ms from A to mA, Hani from T to mT and J/m^2 to mJ/m^2
            self.param_list[i].setValue(fitted_paras[0])
            fitted_paras.pop(0)

        self.MHsim()


    def exportPlotData(self):
        self.updateParamValues()
        try:
            if self.cur_plot == "M(H)":
                sim_M = 1e-3 * self.sim_M / self.d_tot_nom_val # sim_M in kA/m
                sim_data = list(np.stack((self.sim_H, sim_M)).T)
                save_data = "H\tM\n[T]\t[kA/m]\n"
                for i in range(len(sim_data)):
                    save_data += str(sim_data[i][0]) + "\t" + str(sim_data[i][1]) + "\n"
            elif self.cur_plot == "macrospins":
                phiA_local = self.phiA.copy()
                phiB_local = self.phiB.copy()
                for i in range(len(self.phiA)):
                    phiA_local.append(normalizeRadian(phiA_local[i]*np.pi/180 + np.pi)*180/np.pi)
                    phiB_local.append(normalizeRadian(phiB_local[i]*np.pi/180 + np.pi)*180/np.pi)
                sim_data = list(np.stack((self.sim_H, phiA_local, phiB_local)).T)
                save_data = "H\tphi_top_FM\tphi_bot_FM\n[T]\t[deg]\t[deg]\n"
                for i in range(len(sim_data)):
                    save_data += str(sim_data[i][0]) + "\t" + str(sim_data[i][1]) + "\t" + str(sim_data[i][2]) + "\n"
            save_data = save_data[:-1]
        except:
            return
        save_filename = tk.filedialog.asksaveasfilename(parent=self, initialdir=os.getcwd(), filetypes=[("Text File", ".txt")], defaultextension=".txt")
        if save_filename != "":
            with open(save_filename, "w") as f:
                f.write(save_data)


    def exportParameters(self):
        param_names = ["Ms_A * d_A", "Ms_A", "d_A", "Hani_A", "phiAni_A", "J1", "J2", "Ms_B * d_B", "Ms_B", "d_B", "Hani_B", "phiAni_B", "phiH", "H_afm-c", "H_c-fm", "Ms_tot", "d_tot"]
        units = ["[mA]", "[kA/m]", "[nm]", "[mT]", "[deg]", "[mJ/m^2]", "[mJ/m^2]", "[mA]", "[kA/m]", "[nm]", "[mT]", "[deg]", "[deg]", "[mT]", "[mT]", "[kA/m]", "[nm]"]
        self.updateParamValues()
        param_values = []
        for i in range(0, 9):
            if i in (0, 1, 3, 4, 5, 6):
                val = round(self.param_values[i] * 1e3, 13)
            elif i in (2, 7, 8):
                val = round(self.param_values[i] * 180/np.pi, 3)
            else:
                val = self.param_values[i]
            param_values.append(str(val))

        Ms_A = self.FM2_dMs_calc.getMs()
        if Ms_A == "": Ms_A = "unknown"
        param_values.insert(1, Ms_A)
        d_A = self.FM2_dMs_calc.getd()
        if d_A == "": d_A = "unknown"
        param_values.insert(2, d_A)
        Ms_B = self.FM1_dMs_calc.getMs()
        if Ms_B == "": Ms_B = "unknown"
        param_values.insert(8, Ms_B)
        d_B = self.FM1_dMs_calc.getd()
        if d_B == "": d_B = "unknown"
        param_values.insert(9, d_B)
        param_values.append(self.AFM_C_H.get())
        param_values.append(self.C_FM_H.get())
        param_values.append(self.Ms_tot_nom_val * 1e-3)
        param_values.append(self.d_tot_nom_val * 1e9)
        param_values_table = np.stack((param_names, units, param_values), dtype=str)
        save_filename = tk.filedialog.asksaveasfilename(parent=self, initialdir=os.getcwd(), filetypes=[("Text File", ".txt")], defaultextension=".txt")
        if save_filename != "": np.savetxt(save_filename, param_values_table, fmt='%s', delimiter="\t")


    def loadParameters(self):
        openFilename = tk.filedialog.askopenfilename(parent=self, initialdir=os.getcwd())
        if openFilename == "": return
        try:
            with open(openFilename, "r") as f:
                lines = f.readlines()
                new_params = lines[2].split("\t")
                for i in range(len(new_params)):
                    if "\n" in new_params[i]:
                        new_params[i] = new_params[i].replace("\n", "")
                    if i == 0: self.param_list[0].setValue(float(new_params[i]))
                    elif i == 1: self.FM2_dMs_calc.setMs(new_params[i])
                    elif i == 2: self.FM2_dMs_calc.setd(new_params[i])
                    elif i in (3, 4, 5, 6, 7): self.param_list[i-2].setValue(float(new_params[i]))     # hani_A, phiani_A, J1, J2 and d_B * Ms_B
                    elif i == 8: self.FM1_dMs_calc.setMs(new_params[i])
                    elif i == 9: self.FM1_dMs_calc.setd(new_params[i])
                    elif i in (10, 11): self.param_list[i-4].setValue(float(new_params[i]))     # hani_B, phiani_B
                    elif i in (12, 13, 14, 15, 16):
                        entry_list = [self.sim_phiH, self.AFM_C_H, self.C_FM_H, self.Ms_tot_nom, self.d_tot_nom]
                        entry_field = entry_list[i-12]
                        entry_field.delete(0, "end")
                        entry_field.insert(0, new_params[i])
                self.updateParamValues()
        except:
            self.writeConsole("Error: Parameter file could not be loaded. Make sure you chose the correct file.")


if __name__ == "__main__":
    root = GUI()
    root.tk_setPalette(background="#828282", selectColor="#1F6AA5", foreground="black")
    root.protocol("WM_DELETE_WINDOW", closeApp)
    if screen_size.height <= 1080:
        root.after(0, lambda: root.wm_state('zoomed'))
    root.mainloop()