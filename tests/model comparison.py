import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(1, os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
from MacrospinModel import MacrospinModel, EffectiveMacrospinModel
from WadgeDiscreteEnergyModel import WadgeDiscreteEnergyModel

# initialize some parameters
dA = 8e-9           # m
MsA = 1.25          # MA/m
dMsA = dA*MsA*1e6   # A
HaniA = 0.0         # T
phianiA = 0.0       # rad
AexA = 2          # 10^-11 J/m
J1 = -1.5e-3        # J/m2
J2 = -0.25e-3        # J/m2
dB = 8e-9           # m
MsB = 1.25          # MA/m
dMsB = dB*MsB*1e6   # A
HaniB = 0.0         # T
phianiB = 0.0       # rad
AexB = 2          # 10^-11 J/m

d = 4               # Angström
phiH = 0            # rad
Hmax = 2000         # mT
H_steps = 5        # mT
gui = None
h_sweep = np.arange(1, Hmax, H_steps, dtype=np.float64) / 1e3  # T

def run_sims(gui, h_sweep, param_values, discE_param_values):
    # get M(H) from different models to compare
    MacroModel = MacrospinModel(gui=gui, h_sweep=h_sweep, param_values=param_values)
    sim_macro = MacroModel.calculateMH()  # returns sim_M_macro, phiA_macro, phiB_macro

    EffMacroModel = EffectiveMacrospinModel(gui=gui, h_sweep=h_sweep, param_values=param_values, Aex=AexB)
    sim_effMacro = EffMacroModel.calculateMH() # returns sim_M_effMacro, phiA_effMacro, phiB_effMacro

    DiscEnModel = WadgeDiscreteEnergyModel(gui=gui, h_sweep=h_sweep, param_values=discE_param_values)
    sim_discE = DiscEnModel.calculateMH()   # returns sim_M_discE, phiA0_discE, phiB0_discE

    phis_dif = sim_discE[1][2:] - sim_macro[2][2:]

    #return sim_macro, sim_discE
    return sim_macro, sim_effMacro, sim_discE, phis_dif


'''
simulate parameter studies and save them accordingly

for j2 in np.arange(0, 1.1, 0.1):
    J2 = j2*1e-3
    param_values = [dMsA, HaniA, phianiA, J1, J2, dMsB, HaniB, phianiB, phiH, Hmax, H_steps]
    discE_param_values = [dA, MsA, AexA, J1, J2, dB, MsB, AexB, d, phiH]
    sim_macro, sim_discE, phis_dif = run_sims(gui, h_sweep, param_values, discE_param_values)
    save_data = np.asarray([h_sweep[2:], sim_macro[0][2:], sim_macro[1][2:], sim_macro[2][2:], sim_discE[0][2:],  sim_discE[1][2:], sim_discE[2][2:], phis_dif]).T
    np.savetxt(os.path.join(os.getcwd(), "dMs={0} Aex={1} J1={2} J2={3} d={4}.txt".format(round(dMsA*1e3, 4), AexA, round(J1*1e3, 4), round(J2*1e3, 4), d)), save_data, header="H\tM_macro\tphiA_macro\tphiB_macro\tM_discE\tphiA_discE\tphiB_discE\tdiff", comments="")
'''



param_values = [dMsA, HaniA, phianiA, J1, J2, dMsB, HaniB, phianiB, phiH, Hmax, H_steps]
#discE_param_values = [dA, MsA, AexA, J1*5/6, J2-J1/12, dB, MsB, AexB, d, phiH]
discE_param_values = [dA, MsA, AexA, J1, J2, dB, MsB, AexB, d, phiH]

(sim_M_macro, phiA_macro, phiB_macro), (sim_M_effMacro, phiA_effMacro, phiB_effMacro), (sim_M_discE, phiA_discE, phiB_discE), _ = run_sims(gui, h_sweep, param_values, discE_param_values)


# plot everything
fig, axes = plt.subplots(1, 2, figsize=(14,6))
axes[0].set_title("M(H)")
axes[0].set_ylabel("d*M [A]")
axes[0].set_xlabel("H [T]")
axes[0].plot(h_sweep, sim_M_macro, "r", label="Macrospin")
axes[0].plot(h_sweep, sim_M_effMacro, "b", label="EffMacrospin")
axes[0].plot(h_sweep, sim_M_discE, "g", label="DiscreteEnergy")
axes[0].legend()

axes[1].set_title("Macrospin rotation")
axes[1].set_ylabel("phi [°]")
axes[1].set_xlabel("H [T]")
axes[1].plot(h_sweep, phiA_macro, color="r", marker="o", label="phiA Macro")
axes[1].plot(h_sweep, phiB_macro, color="r", marker="x", label="phiB Macro")
axes[1].plot(h_sweep, phiA_effMacro, color="b", marker="o", label="phiA EffMacro")
axes[1].plot(h_sweep, phiB_effMacro, color="b", marker="x", label="phiB EffMacro")
axes[1].plot(h_sweep, phiA_discE, color="g", marker="o", label="phiA DiscEnergy")
axes[1].plot(h_sweep, phiB_discE, color="g", marker="x", label="phiB DiscEnergy")
#axes[1].plot(h_sweep[2:], phis_dif, marker="+")
axes[1].legend()

plt.show()