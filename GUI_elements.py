import customtkinter as ctk
import tkinter as tk
import pyautogui
import numpy as np

pads = 10
entry_w = 90
slider_w = 200
font_name = "Space Grotesk"

small_font_size = 15
medium_font_size = 17
large_font_size = 20
screen_size = pyautogui.size()
GUI_scale = screen_size.width/2560
tk_text_subscript = int(11*GUI_scale)
tk_text_font_size = int(14*GUI_scale)


class ThicknessMsCalculator():
    def __init__(self, parent, row, dMs_Parameter):
        self.dMs = dMs_Parameter
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid(row=row, column=2, columnspan=6, sticky="nsew")
        self.dropdown = ctk.CTkComboBox(self.frame, values=["Calculate d from Ms", "Calculate Ms from d", "Calculate d*Ms"], width=entry_w*2, state="readonly")
        self.dropdown.grid(row=0, column=0, padx=(pads, 0), pady=pads, sticky="w")
        self.dropdown.set("Calculate d*Ms")
        ctk.CTkLabel(self.frame, text="M\u209B =", font=(font_name, medium_font_size)).grid(row=0, column=1, padx=(pads, 0), pady=pads, sticky="w")
        self.Ms = ctk.CTkEntry(self.frame, font=(font_name, medium_font_size), width=entry_w*3/4, validate="key")
        self.Ms.grid(row=0, column=2, padx=(pads/2,0), pady=pads, sticky="w")
        ctk.CTkLabel(self.frame, text="kA/m and d =", font=(font_name, medium_font_size)).grid(row=0, column=3, padx=(pads/2, 0), pady=pads, sticky="w")
        self.d = ctk.CTkEntry(self.frame, font=(font_name, medium_font_size), width=entry_w*3/4)
        self.d.grid(row=0, column=4, padx=(pads/2,0), pady=pads, sticky="w")
        ctk.CTkLabel(self.frame, text="nm", font=(font_name, medium_font_size)).grid(row=0, column=5, padx=(pads/2, 0), pady=pads, sticky="w")
        self.calc_but = ctk.CTkButton(self.frame, text="Calculate", font=(font_name, small_font_size), command=self.calculate)
        self.calc_but.grid(row=0, column=6, padx=(3*pads, pads), pady=pads, sticky="e")

    def calculate(self):
        try:
            calc_type = self.dropdown.get()
            dMs = self.dMs.getValue() * 1e-6    # d*Ms in kA unit
            if calc_type == "Calculate d from Ms":
                Ms = float(self.Ms.get())
                d = 1e9 * dMs / Ms
                self.d.delete(0, "end")
                self.d.insert(0, str(round(d, 4)))
            elif calc_type == "Calculate Ms from d":
                d = float(self.d.get()) * 1e-9
                Ms = dMs / d
                self.Ms.delete(0, "end")
                self.Ms.insert(0, str(round(Ms, 4)))
            elif calc_type == "Calculate d*Ms":
                d = float(self.d.get()) * 1e-9
                Ms = float(self.Ms.get())
                dMs = d * Ms * 1e6  # d*Ms in mA
                self.dMs.setValue(dMs)
        except:
            pass

    def getMs(self):
        return self.Ms.get()
    
    def setMs(self, value):
        self.Ms.delete(0, "end")
        self.Ms.insert(0, str(value))
    
    def getd(self):
        return self.d.get()
    
    def setd(self, value):
        self.d.delete(0, "end")
        self.d.insert(0, str(value))


class Parameter():
    def __init__(self, gui, parent, row, param, start_value, lower, upper, fit=False):
        self.gui = gui
        self.row = row
        self.param = param

        param_to_unit = {
            "d*M\u209B": "mA",
            "J\u2081": u"mJ/m\u00B2",
            "J\u2082": u"mJ/m\u00B2",
            "Hani" : "mT",
            "\u03C6ani": "°"}
        self.unit = param_to_unit[param]
        
        if row in (1, 3, 4):
            self.param_name = param + "_top"
        elif row in (9, 11, 12):
            self.param_name = param + "_bot"
        else:
            self.param_name = param
        
        self.fit_checkbox = ctk.CTkCheckBox(parent, text="", width=3*pads, onvalue="on", offvalue="off", command=self.fitCheckboxCallback)
        self.fit_checkbox.grid(row=row, column=0, padx=(2*pads,pads), pady=pads, sticky="n")
        self.fit_checkbox.select() if fit == True else self.fit_checkbox.deselect()

        self.link_checkbox = ctk.CTkCheckBox(parent, text="", width=3*pads, onvalue="on", offvalue="off", command=self.linkCheckboxCallback)
        self.link_checkbox.grid(row=row, column=1, padx=0, pady=pads, sticky="n")
        if row not in (1, 9):   self.link_checkbox.configure(state=tk.DISABLED, border_color="#4F5254")

        if param in ("Hani", "\u03C6ani"):
            txt = param.replace("ani", "")
            txt = u"%s" % (txt)
            self.label = tk.Text(parent, width=5, height=1, borderwidth=0, foreground="#DCE4EE", background="#2B2B2B", font=(font_name, tk_text_font_size))
            self.label.tag_configure("subscript", offset=-4, font=(font_name, tk_text_subscript))
            self.label.insert("insert", txt, "", "ani", "subscript", " =")
            self.label.configure(state="disabled")
            self.label.grid(row=row, column=2, padx=(pads,0), pady=pads, sticky="e")
        else:
            txt = u"%s =" % (param)
            ctk.CTkLabel(parent, text=txt, font=(font_name, large_font_size)).grid(row=row, column=2, padx=(pads,0), pady=pads, sticky="e")

        self.param_value = ctk.CTkEntry(parent, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.param_value.grid(row=row, column=3, padx=pads/2, pady=pads, sticky="w")
        self.param_value.insert(0, start_value)

        ctk.CTkLabel(parent, text=self.unit, font=(font_name, medium_font_size)).grid(row=row, column=4, padx=(0, 4*pads), pady=pads, sticky="w")

        self.param_lower = ctk.CTkEntry(parent, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.param_lower.grid(row=row, column=5, padx=(pads,0), pady=pads, sticky="e")
        self.param_lower.insert(0, lower)

        self.param_slider = ctk.CTkSlider(parent, from_=lower, to=upper, width=slider_w, command=self.setValue)
        self.param_slider.grid(row=row, column=6, padx=pads, pady=pads, sticky="e")

        self.param_upper = ctk.CTkEntry(parent, font=(font_name, medium_font_size), width=entry_w, validate="key")
        self.param_upper.grid(row=row, column=7, pady=pads, sticky="w")
        self.param_upper.insert(0, upper)

        ctk.CTkLabel(parent, text=self.unit, font=(font_name, medium_font_size)).grid(row=row, column=8, padx=(pads/2, 2*pads), pady=pads, sticky="w")

        self.updateSliderRange()

    def updateSliderRange(self, value=None, init_state="normal"):
        if init_state == "disabled":
            self.param_lower.configure(state="normal")
            self.param_slider.configure(state="normal")
            self.param_upper.configure(state="normal")

        # validate and update lower and upper boundaries
        try:
            lower = float(self.param_lower.get())
            upper = float(self.param_upper.get())
            if lower != upper: self.param_slider.configure(from_=lower, to=upper)

            # update value position on slider
            if value is not None:
                self.param_slider.set(value)
            else:
                self.param_slider.set(self.getValue())
        except:
            if "lower" not in locals():
                self.param_lower.delete(0, "end")
                self.param_lower.insert(0, "Error")
            elif "upper" not in locals():
                self.param_upper.delete(0, "end")
                self.param_upper.insert(0, "Error")
        
        if init_state == "disabled":
            self.param_lower.configure(state="disabled")
            self.param_slider.configure(state="disabled")
            self.param_upper.configure(state="disabled")

    def setValue(self, value):
        if self.param_value._state == "disabled":
            init_state = "disabled"
            self.param_value.configure(state="normal")
        else:
            init_state = "normal"
        self.param_value.delete(0, "end")
        self.param_value.insert(0, str(round(float(value), 4)))
        if init_state == "disabled": self.param_value.configure(state="disabled")

        self.updateSliderRange(value=float(value), init_state=init_state)

    def getValue(self):
        if self.param_value.get() == "":
            return None
        else:
            try:
                value = round(np.float64(self.param_value.get()), 13)
                return value
            except:
                return None
            
    def getLowerBound(self):
        param_lower = float(self.param_lower.get())
        param_upper = float(self.param_upper.get())
        if param_lower < param_upper:
            return param_lower
        else:
            return param_upper
    
    def getUpperBound(self):
        param_lower = float(self.param_lower.get())
        param_upper = float(self.param_upper.get())
        if param_upper > param_lower:
            return param_upper
        else:
            return param_lower

    def getFitCheckbox(self):
        return self.fit_checkbox.get()
    
    def getLinkCheckbox(self):
        return self.link_checkbox.get()
    
    def fitCheckboxCallback(self):
        self.gui.updateCheckboxes(self.row, "fit")
    
    def linkCheckboxCallback(self):
        self.gui.updateCheckboxes(self.row, "link")

    def setLinkMaster(self):
        self.link_checkbox.deselect()
        self.link_checkbox.configure(border_color="#1F6AA5")
        self.param_value.configure(state="normal")
        self.param_lower.configure(state="normal")
        self.param_slider.configure(state="normal")
        self.param_upper.configure(state="normal")
    
    def setLinkFollower(self):
        self.fit_checkbox.deselect()
        self.param_value.configure(state="disabled")
        self.param_lower.configure(state="disabled")
        self.param_slider.configure(state="disabled")
        self.param_upper.configure(state="disabled")

    def resetLinkBox(self):
        self.setLinkMaster()
        self.link_checkbox.configure(border_color="#949A9F")