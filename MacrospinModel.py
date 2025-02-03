import numpy as np
import scipy.optimize as o
import math


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


class MacrospinModel():
    def __init__(self, gui, h_sweep, param_values, exp_M=None, fit_paras=None, fit_para_ind=[], fit_type=None, bnds=None, full_hyst="off"):
        self.gui = gui
        self.h_sweep = list(h_sweep)
        self.param_values = param_values
        self.exp_M = exp_M
        self.fit_paras = fit_paras
        self.fit_para_ind = fit_para_ind
        self.fit_type = fit_type
        self.para_scale = [5e-3, 1e-3, 1, 1e-4, 1e-4, 5e-3, 1e-3, 1]
        self.para_scale = [self.para_scale[i] for i in fit_para_ind]
        self.gui.prog_bar.set(0)
        self.fitting = False
        self.bnds = bnds
        self.full_hyst = full_hyst
        if len(self.h_sweep) > 0: self.half_sweep_ind = self.h_sweep.index(min(self.h_sweep))
        self.best_FOM = 100000
        self.linkedParas = False

        # if d * Ms as well as Hani and phiani of both FM are identical, the simulation is buggy
        # to circumvent this, we check on class creation if this is the case and adjust one anisotropy angle by 0.01°
        # this has a negligible influence on the hystersis but drastically improves the quality by fixing the otherwise occurring bug
        check_Zeeman = bool(param_values[0] == param_values[5]) if None not in (param_values[0], param_values[5]) else False
        check_Hani = bool(param_values[1] == param_values[6] and param_values[1] != 0) if None not in (param_values[1], param_values[6]) else False
        check_phiani_phiH = bool(param_values[2] == param_values[7]) if None not in (param_values[2], param_values[7]) else False
        if check_Zeeman and check_Hani and check_phiani_phiH:
            self.param_values[2] += 0.01 * np.pi / 180


    def addLinkedParas(self, sum, master, follower):
        self.linkedParas = True
        self.linkedParaSum = sum
        self.masterParaID = master
        self.followerParaID = follower


    def updateLinkedParas(self):
        self.param_values[self.followerParaID] = self.linkedParaSum - self.param_values[self.masterParaID]


    def fit(self):
        self.fitting = True
        self.fit_iteration = 1
        self.cur_fit_type = "Global"

        if self.fit_type == "fast fit":
            maxiter = 5
            popsize = 3
        elif self.fit_type == "precise fit":
            maxiter = 15
            popsize = 8

        try:
            global_fitted_paras = o.differential_evolution(self.fit_cost, bounds=self.bnds, x0=self.fit_paras, maxiter=maxiter, popsize=popsize, polish=False)
            self.gui.writeConsole("Global Fit success: " + str(global_fitted_paras.success))
            self.gui.writeConsole("Global Fit message: " + str(global_fitted_paras.message))
            self.cur_fit_type = "Polish"
            polished_fit_paras = o.minimize(self.fit_cost, global_fitted_paras.x, method='L-BFGS-B', bounds=self.bnds, options={"ftol": 1e-4})
            self.gui.writeConsole("Polish Fit success: " + str(polished_fit_paras.success))
            self.gui.writeConsole("Polish Fit message: " + str(polished_fit_paras.message))
            return list(polished_fit_paras.x)
        except Exception as err:
            if len(err.args) == 0:
                self.gui.writeConsole("Fit aborted.")
            else:
                self.gui.writeConsole("Fit Error: " + str(err))
            return []
        

    def fit_cost(self, paras, *args):
        M, phiA, phiB = self.calculateMH(self.h_sweep, paras)
        if len(M) == 0: raise Exception # if we pressed the stop button, we raise an Exception to stop fitting
        FOM = self.gui.getFOM(sim_M=M)
        return FOM
    

    def calculateMH(self, h_sweep=[], *paras):
        # First we setup some things for the Progress Bar
        # Also if we fit, h_sweep is given by o.curve_fit to this function, 
        # otherwise if we just simulate we need to get it from the class initialization
        if self.fitting == True:
            txt = self.cur_fit_type + " Fit (iteration " + str(self.fit_iteration) + ")"
            self.gui.prog_bar_label.configure(text=txt)
            self.fit_iteration += 1
        elif self.fitting == False:
            h_sweep = self.h_sweep
            self.gui.prog_bar_label.configure(text="Simulation Progress Bar")
        last_progbar_update = 0
        update_interval = int(len(h_sweep) * 20 / 800)

        # here we put the parameters, which are being fitted and being given by o.curve_fit, back into self.param_values
        if len(paras) > 0 and len(self.fit_para_ind) > 0:
            if isinstance(paras[0], np.ndarray): paras = paras[0]
            fit_paras_copy = list(paras).copy()
            for i in self.fit_para_ind:
                self.param_values[i] = fit_paras_copy[0]
                fit_paras_copy.pop(0)
            if self.linkedParas == True: self.updateLinkedParas()

        M, phiA, phiB = [], [], []
        phiH = self.param_values[8]
        phiA_i, phiB_i = phiH, phiH   # we start from saturation so the first macrospin angles are identical to phiH

        for i, h in enumerate(h_sweep):
            # check if progress bar should be update
            if i - last_progbar_update == update_interval:
                if self.gui.stopDaemon_bool == True:
                    self.gui.stopDaemon_bool = False
                    self.gui.prog_bar.set(0)
                    return []
                if self.full_hyst == "off":
                    self.gui.prog_bar.set(2*i/len(h_sweep))
                elif self.full_hyst == "on":
                    self.gui.prog_bar.set(i/len(h_sweep))
                last_progbar_update = i
            elif i == len(h_sweep) - 1:
                self.gui.prog_bar.set(1)

            # flip phiH by 180° if we go to negative field values
            phiH_at_h = normalizeRadian(phiH + np.pi) if h < 0 else phiH

            # find local minimum in G(phiA, phiB) for new external field value, using the previous macrospin angles (phiA, phiB) as initial parameters
            phiAB_new = o.minimize(self.get_G, (phiA_i, phiB_i), args=(h, phiH_at_h), method="newton-cg", jac=True, hess=self.get_G_hess, options={"xtol": 1e-12})

            # check whether we are stuck on a terrace point / local maxima
            if math.isclose(phiAB_new.x[0], phiA_i, abs_tol=1e-2) and math.isclose(phiAB_new.x[1], phiB_i, abs_tol=1e-2):   # absolute tolerance is 0.6°
                inc = np.pi/180     # 1° in radians
                guesses = [(phiA_i+inc, phiB_i), (phiA_i, phiB_i+inc), (phiA_i-inc, phiB_i), (phiA_i, phiB_i-inc), 
                           (phiA_i+inc, phiB_i+inc), (phiA_i+inc, phiB_i-inc), (phiA_i-inc, phiB_i-inc), (phiA_i-inc, phiB_i+inc)]
                g, dg = self.get_G((phiA_i, phiB_i), h, phiH_at_h)
                d2g, det = self.get_G_hess((phiA_i, phiB_i), h, phiH_at_h, type="det")
                best_guess = [(phiA_i, phiB_i), dg, d2g, det]
                while det < 0 or det == 0 or (abs(dg[0]) < 1E-7 and abs(dg[1]) < 1E-7 and det > 0 and d2g[0,0] < 0):
                    # we are not in a minimum
                    for i, guess in enumerate(guesses):
                        g, dg = self.get_G(guess, h, phiH_at_h)
                        d2g, det = self.get_G_hess(guess, h, phiH_at_h, type="det")
                        if sum(dg) < sum(best_guess[1]) and det > 0:
                            best_guess = [guess, dg, d2g, det]
                            break
                    phiAB_new = o.minimize(self.get_G, best_guess[0], args=(h, phiH_at_h), method="newton-cg", jac=True, hess=self.get_G_hess, options={"xtol": 1e-12})
                    dg, d2g, det = best_guess[1:]
                    inc += np.pi/180
                    guesses = [(phiA_i+inc, phiB_i), (phiA_i, phiB_i+inc), (phiA_i-inc, phiB_i), (phiA_i, phiB_i-inc),
                               (phiA_i+inc, phiB_i+inc), (phiA_i+inc, phiB_i-inc), (phiA_i-inc, phiB_i-inc), (phiA_i-inc, phiB_i+inc)]

            M_at_H = self.get_MvH(phiAB_new.x, phiH_at_h)
            M.append(M_at_H)
            phiA_i = normalizeRadian(phiAB_new.x[0])       # set the current phiA value as the next starting guess for phiA
            phiB_i = normalizeRadian(phiAB_new.x[1])       # set the current phiB value as the next starting guess for phiB
            phiA.append(phiA_i)
            phiB.append(phiB_i)

            if self.fitting == True and self.full_hyst == "off" and i == self.half_sweep_ind:
                # we wanna fit to exp data which should be a full hysteresis but we only simulate the down sweep
                # so we break after the down sweep is done and mirror & interpolate it to get the theo. up sweep data points
                H_down_sweep = [-h for h in self.h_sweep[:i+1]]
                M_down_sweep = [-m for m in M]
                H_up_sweep = list(self.h_sweep[i+1:])               
                # First we mirrored the MH down sweep to an up sweep but due to some effects like remanent field correction of 
                # SQUID-VSMs the H fields at the up and down sweep don't have to be identical. That's why we have to interpolate 
                # the M values for the up sweep.
                M = np.append(M, np.interp(H_up_sweep, H_down_sweep, M_down_sweep))
                break
        
        # M(H) simulation is done

        # convert from radians to deg for plotting purposes
        phiA = [p * 180 / np.pi for p in phiA]
        phiB = [p * 180 / np.pi for p in phiB]

        # if we are currently fitting, we want to check the FOM of the newly simulated M(H) curve and compare it to the currently best FOM
        # if the new simulation is a better fit, we want to update the GUI live (update parameters, plot and FOM)
        if self.fitting == True:
            FOM = self.gui.getFOM(sim_M=M)
            if FOM < self.best_FOM:
                self.best_FOM = FOM
                self.gui.sim_M = M
                self.gui.sim_M_plot = M * 1e3
                self.gui.drawPlot("Hysteresis", rescale=False)

                fitted_paras = list(paras).copy()
                self.gui.writeConsole("------------------------------------------------")
                for i in self.fit_para_ind:
                    if i in (2, 7):
                        fitted_paras[0] *= (180/np.pi) # phiani from pi values to deg
                    else:   
                        fitted_paras[0] *= 1e3    # d*Ms from A to mA, Hani from T to mT and J/m^2 to mJ/m^2
                    self.gui.param_list[i].setValue(fitted_paras[0])
                    self.gui.writeConsole(self.gui.param_list[i].param_name + " = " + str(fitted_paras[0]) + " " + self.gui.param_list[i].unit)
                    fitted_paras.pop(0)
                FOM = str(FOM.round(8))
                self.gui.FOM_label.configure(text=FOM)
                self.gui.writeConsole("New FOM: " + FOM)
        
        return M, phiA, phiB


    def get_G(self, phis, h, phiH=None):
        if phiH == None:
            phiH = normalizeRadian(self.param_values[8] + np.pi) if h < 0 else self.param_values[8]
        phiA, phiB = phis
        d_Ms_A, hani_A, phiani_A, J1, J2, d_Ms_B, hani_B, phiani_B = self.param_values[:8]

        # calculate energy
        g_A = - d_Ms_A * (abs(h) * np.cos(phiA - phiH) + 0.5 * hani_A * (np.cos(phiA - phiani_A))**2)
        g_B = - d_Ms_B * (abs(h) * np.cos(phiB - phiH) + 0.5 * hani_B * (np.cos(phiB - phiani_B))**2)
        g_RKKY = - (J1 * np.cos(phiA - phiB) + J2 * (np.cos(phiA - phiB))**2)
        g = g_A + g_B + g_RKKY

        # normalize energy to max values
        g /= d_Ms_A * (abs(h) + hani_A/2) + d_Ms_B * (abs(h) + hani_B/2) + abs(J1) + abs(J2)

        # calculate gradients along phiA and phiB
        dg_phiA = d_Ms_A * (abs(h) * np.sin(phiA - phiH) + 0.5 * hani_A * np.sin(2*(phiA - phiani_A))) + J1 * np.sin(phiA-phiB) + J2 * np.sin(2*phiA-2*phiB)
        dg_phiB = d_Ms_B * (abs(h) * np.sin(phiB - phiH) + 0.5 * hani_B * np.sin(2*(phiB - phiani_B))) - J1 * np.sin(phiA-phiB) - J2 * np.sin(2*phiA-2*phiB)
        
        # normalize gradients to max values
        dg_phiA /= d_Ms_A * (abs(h) + 0.5 * hani_A) + abs(J1) + abs(J2)
        dg_phiB /= d_Ms_B * (abs(h) + 0.5 * hani_B) + abs(J1) + abs(J2)

        return g, (dg_phiA, dg_phiB)
    

    def get_G_hess(self, phis, h, phiH=None, type=None):
        if phiH == None:
            phiH = normalizeRadian(self.param_values[8] + np.pi) if h < 0 else self.param_values[8]
        phiA, phiB = phis
        d_Ms_A, hani_A, phiani_A, J1, J2, d_Ms_B, hani_B, phiani_B = self.param_values[:8]

        # calculate hessian
        G_hess = np.zeros((2,2))
        G_hess[0,0] = d_Ms_A * (abs(h) * np.cos(phiA - phiH) + hani_A * np.cos(2*(phiA - phiani_A))) + J1 * np.cos(phiA - phiB) + 2 * J2 * np.cos(2*phiA-2*phiB)    # d2G_dphiA2
        G_hess[1,0] = - J1 * np.cos(phiA - phiB) - 2 * J2 * np.cos(2*phiA - 2*phiB)
        G_hess[1,1] = d_Ms_B * (abs(h) * np.cos(phiB - phiH) + hani_B * np.cos(2*(phiB - phiani_B))) + J1 * np.cos(phiA - phiB) + 2 * J2 * np.cos(2*phiA-2*phiB)    # d2G_dphiB2
        G_hess[0,1] = - J1 * np.cos(phiA - phiB) - 2 * J2 * np.cos(2*phiA - 2*phiB)

        if type == "det":
            det = G_hess[0,0] * G_hess[1,1] - G_hess[1,0] * G_hess[0,1]
            return G_hess, det
        else:
            return G_hess


    def get_MvH(self, phis, phiH):
        phiA, phiB = phis
        sign = math.copysign(1, phiH)
        d_Ms_A = self.param_values[0]
        d_Ms_B = self.param_values[5]

        M = sign * (d_Ms_A * np.cos(phiA - phiH) + d_Ms_B * np.cos(phiB - phiH))

        return M