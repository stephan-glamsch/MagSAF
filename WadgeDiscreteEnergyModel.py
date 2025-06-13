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
        self.dA, self.MsA, self.AexA, self.HaniA, self.phianiA, self.J1, self.J2, self.dB, self.MsB, self.AexB, self.HaniB, self.phianiB, self.d, self.phiH = param_values

        self.dA *= 1e9  # nm
        self.dB *= 1e9  # nm
        self.NA = int(self.dA*10/self.d)
        self.NB = int(self.dB*10/self.d) 
        self.J1 *= 1e3  # mJ/m^2
        self.J2 *= 1e3  # mJ/m^2

        self.AexA *= np.ones(self.NA-1)
        self.AexB *= np.ones(self.NB-1)
        self.MsA *= np.ones(self.NA)
        self.MsB *= np.ones(self.NB)

        # unit conversions to match the continuous model
        self.dMsA = self.MsA*self.d*0.1     # mA
        self.dMsB = self.MsB*self.d*0.1     # mA
        self.dAexA = 100*self.AexA/self.d    # mJ/m^2
        self.dAexB = 100*self.AexB/self.d    # mJ/m^2

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

        
        # I want a list of the H step density for FOM weighting later on
        self.exp_H_steps = []
        for i in range(len(self.h_sweep)):
            if i == 0:
                dH = 2 * np.abs(self.h_sweep[i] - self.h_sweep[i+1])
            elif i == len(self.h_sweep)-1:
                dH = 2 * np.abs(self.h_sweep[i-1] - self.h_sweep[i])
            else:
                dH = np.abs(self.h_sweep[i-1] - self.h_sweep[i]) + np.abs(self.h_sweep[i] - self.h_sweep[i+1])
            self.exp_H_steps.append(dH)


    def curve_fitMH(self, H, J1, J2, Aex):

        #print("New Fit with J1={j1}, J2={j2}, Aex={aex}".format(j1=J1, j2=J2, aex=Aex))
        #print("New Fit with J1={j1}, J2={j2}".format(j1=J1*1e3, j2=J2*1e3))

        self.J1 = J1    # mJ/m^2
        self.J2 = J2    # mJ/m^2

        self.dAexA = 100 * Aex * np.ones(self.NA-1) / self.d    # mJ/m^2
        self.dAexB = 100 * Aex * np.ones(self.NB-1) / self.d    # mJ/m^2

        m, phiA, phiB, Hs, FOM = self.calculateMH()
        return m
    

    def diff_evo_fitMH(self, J1, J2, Aex, bnds):
        global_fitted_paras = o.differential_evolution(self.fit_cost, bounds=bnds, x0=[J1, J2, Aex], maxiter=5, popsize=5, polish=False, disp=True)
        print("global fit done")
        polished_fit_paras = o.minimize(self.fit_cost, global_fitted_paras.x, method='L-BFGS-B', bounds=bnds, options={"ftol": 1e-4})
        print("local fit done")
        return list(polished_fit_paras.x)


    def fit_cost(self, paras, *args):
        self.J1, self.J2, Aex = paras

        self.dAexA = 100 * Aex * np.ones(self.NA-1) / self.d
        self.dAexB = 100 * Aex * np.ones(self.NB-1) / self.d
        
        m, phiA, phiB, Hs, FOM = self.calculateMH()
        #if len(M) == 0: raise Exception # if we pressed the stop button, we raise an Exception to stop fitting
        #FOM = self.getFOM(sim_M=m)
        print("FOM = " + str(FOM))
        return FOM
    

    def getFOM(self, sim_M):
        # calculates the Figure of Merit (FOM) of the Simulations / Fits
        M_dif = [(self.exp_H_steps[i]/max(self.exp_H_steps)) * np.abs(1 - sim_M[i]/self.exp_M[i]) for i in range(len(self.exp_M))]
        FOM = sum(M_dif)/len(self.exp_M)
        return FOM


    def calculateMH(self, tol=1e-6):
        '''
        This is the function 'energy_M' from E. Wadge
        '''
        ret = np.ones(len(self.h_sweep))
        phiA0, phiB0 = [], []
        ini_thetas = np.concatenate((np.arange(1,self.NA+1,1), np.arange(1,self.NB+1,1)))
        for i, H in enumerate(self.h_sweep):
            thetas_opt = o.minimize(self.energy_asymmetric, ini_thetas, args=(H,), tol=tol).x

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

            ret[i] = mag
            phiA0.append(thetas_opt[:self.NA])
            phiB0.append(thetas_opt[self.NA:])
            Hs_i = i

            if abs(1-mag) < 0.0005:
                break
        
        #ret *= (self.dA * self.MsA[0] + self.dB * self.MsB[0])
        phiA0 = np.asarray(phiA0)
        phiA0 *= 180/np.pi
        phiB0 = np.asarray(phiB0)
        phiB0 *= 180/np.pi
        #FOM = self.getFOM(ret)
        return ret, phiA0, phiB0, Hs_i
    

    def energy_asymmetric(self, thetas, H):
        '''
        This is the function 'energy_asymmetric' from E. Wadge
        '''
        E_RKKY = -self.J1 * np.cos(thetas[self.NA-1] - thetas[self.NA]) - self.J2*np.cos(thetas[self.NA-1] - thetas[self.NA])**2
        E_ex = -2*(np.sum(self.dAexA*np.cos(thetas[:self.NA-1] - thetas[1:self.NA])) + np.sum(self.dAexB*np.cos(thetas[self.NA:-1] - thetas[self.NA+1:])))
        E_ZCo = -H*np.sum(self.dMsA*np.cos(thetas[:self.NA])) - H*np.sum(self.dMsB*np.cos(thetas[self.NA:]))
        #E_UMA = -0.5*self.HaniA*np.sum(self.dMsA*np.cos(thetas[:self.NA] - self.phianiA)**2) - 0.5*self.HaniB*np.sum(self.dMsB*np.cos(thetas[self.NA:] - self.phianiB)**2)
        # print(f"E_RKKY = {E_RKKY}\nE_ex = {E_ex}\nE_Z = {E_ZCo}\ntotal={E_RKKY + E_ex + E_ZCo}")
        return E_RKKY + E_ex + E_ZCo