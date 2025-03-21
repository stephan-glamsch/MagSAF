'''
This Model is adapted from Elliot Wadge:
https://zenodo.org/records/13958482
https://github.com/Elliot-Wadge/Modeling-magnetization-reversal-in-multilayers-with-interlayer-exchange-coupling/tree/v1.0.0

This model class is still under construction.
'''

import numpy as np
import scipy.optimize as o


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

class WadgeDiscreteEnergyModel():
    def __init__(self, gui, h_sweep, param_values, exp_M=None, fit_paras=None, fit_para_ind=[], fit_type=None, bnds=None, full_hyst="off"):
        '''
        param_values = [dA, MsA, AexA, J1, J2, dB, MsB, AexB, d]
        dA: m
        MsA: MA/m
        AexA: 1E-11 J/m
        J1: J/m^2
        J2: J/m^2
        dB: m
        MsB: MA/m
        AexB: 1E-11 J/m
        d: Angström
        '''
        
        # convert my param_values units to E. Wadge's units
        self.h_sweep = h_sweep
        self.dA, self.MsA, self.AexA, self.J1, self.J2, self.dB, self.MsB, self.AexB, self.d, self.phiH = param_values

        self.dA *= 1e9  # nm
        self.dB *= 1e9  # nm
        self.J1 *= 1e3  # mJ/m^2
        self.J2 *= 1e3  # mJ/m^2
        htA = self.dA / 2   # half thickness in nm
        htB = self.dB / 2   # half thickness in nm
        self.NA = int(htA*10/self.d)
        self.NB = int(htB*10/self.d)        

        self.AexA *= np.ones(self.NA-1)
        self.AexB *= np.ones(self.NB-1)
        self.MsA *= np.ones(self.NA)
        self.MsB *= np.ones(self.NB)

        #self.gui = gui
        #if self.gui is not None: self.gui.prog_bar.set(0)
        self.h_sweep = list(h_sweep)
        #self.param_values = param_values
        self.exp_M = exp_M
        #self.fit_paras = fit_paras
        #self.fit_para_ind = fit_para_ind
        #self.fit_type = fit_type
        #self.para_scale = [5e-3, 1e-3, 1, 1e-4, 1e-4, 5e-3, 1e-3, 1]
        #self.para_scale = [self.para_scale[i] for i in fit_para_ind]
        #self.fitting = False
        #self.bnds = bnds
        #self.full_hyst = full_hyst
        #if len(self.h_sweep) > 0: self.half_sweep_ind = self.h_sweep.index(min(self.h_sweep))
        #self.best_FOM = 100000
        #self.linkedParas = False


    def calculateMH(self, tol=1e-4):
        '''
        This is the function 'energy_M' from E. Wadge
        '''
        ret = np.ones(len(self.h_sweep))
        phiA0 = np.ones(len(self.h_sweep))
        phiB0 = np.ones(len(self.h_sweep))
        # unit conversions to match the continuous model
        dMsA = 2*self.MsA*self.d*0.1     # mA
        dMsB = 2*self.MsB*self.d*0.1     # mA
        dAexA = 100*self.AexA/self.d    # mJ/m^2
        dAexB = 100*self.AexB/self.d    # mJ/m^2
        ini_thetas = np.concatenate((np.arange(1,self.NA+1,1), np.arange(1,self.NB+1,1)))
        for i, H in enumerate(self.h_sweep):
            thetas_opt = o.minimize(self.energy_asymmetric, ini_thetas, args=(H, dAexA, dAexB, dMsA, dMsB), tol=tol).x

            for j, theta in enumerate(thetas_opt):
                thetas_opt[j] = normalizeRadian(theta)
            ini_thetas = thetas_opt

            if hasattr(self.MsA, "__iter__"):
                MsA_sum = np.sum(self.MsA)
            else:
                MsA_sum = self.NA*self.MsA

            if hasattr(self.MsB, "__iter__"):
                MsB_sum = np.sum(self.MsB)
            else:
                MsB_sum = self.NB*self.MsB

            mag = 1/(MsA_sum + MsB_sum) * (np.sum(self.MsA*np.cos(thetas_opt[:self.NA])) + np.sum(self.MsB*np.cos(thetas_opt[self.NA:])))
            if abs(1-mag) < 0.001:
                phiA0[i:] = thetas_opt[self.NA-1]
                phiB0[i:] = thetas_opt[self.NA]
                break

            ret[i] = mag
            phiA0[i] = np.mean(thetas_opt[:self.NA-1])
            phiB0[i] = np.mean(thetas_opt[self.NA:])
            
        ret *= 1e-3 * (self.dA * self.MsA[0] + self.dB * self.MsB[0])
        phiA0 *= 180/np.pi
        phiB0 *= 180/np.pi
        return ret, phiA0, phiB0
    

    def energy_asymmetric(self, thetas, H, dAexA, dAexB, dMsA, dMsB):
        '''
        This is the function 'energy_asymmetric' from E. Wadge
        '''
        E_RKKY = -self.J1 * np.cos(thetas[self.NA-1] - thetas[self.NA]) - self.J2*np.cos(thetas[self.NA-1] - thetas[self.NA])**2
        E_ex = -2*(np.sum(dAexA*np.cos(thetas[:self.NA-1] - thetas[1:self.NA])) + np.sum(dAexB*np.cos(thetas[self.NA:-1] - thetas[self.NA+1:])))
        E_ZCo = -H*np.sum(dMsA*np.cos(thetas[:self.NA])) - H*np.sum(dMsB*np.cos(thetas[self.NA:]))
        # print(f"E_RKKY = {E_RKKY}\nE_ex = {E_ex}\nE_Z = {E_ZCo}\ntotal={E_RKKY + E_ex + E_ZCo}")
        return E_RKKY + E_ex + E_ZCo