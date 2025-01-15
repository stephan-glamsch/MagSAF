# Welcome to MagSAF's documentation!

MagSAF is a GUI for fast and easy simulations of magnetic hysteresis loops of synthetic antiferromagnets (SAFs). Its target audience are reasearchers who want to get into the field of SAFs. With this software you can get familiar with the influence all of the magnetic parameters have on the hysteresis loop but also fit your experimental data to extract magnetic parameters. The simulations are currently based on a macrospin model and the software assumes an in-plane easy axis SAF. It is also possible to simulate and fit uniaxial, magnetic anisotropies.

In the future, more theoretical models, out-of-plane SAFs as well as more anisotropy options are planned.

![Screenshot of the GUI](readme_files/gui_screenshot.png)

## Getting started
1. [How to install](#how-to-install)
2. [How to use](#how-to-use)
   - [Loading experimental data](#loading-experimental-data)
3. [Theoretical Framework](#theoretical-framework)
   - [What is a synthetic antiferromagnet (SAF)?](#what-is-a-synthetic-antiferromagnet-saf)
   - [Macrospin Model](#macrospin-model)
4. [Fitting procedure](#fitting-procedure)
   - [Figure of Merit](#figure-of-merit)

## How to install
tbd

## How to use 

### Loading experimental data

The data file has to be a .txt file with two columns separated by either '\t' or whitespaces. The first column has to be the magnetic field and the second one the magnetization. For the magnetic field, supported units are 'Oe', 'mT' and 'T' and for the magnetization they are 'A/m' and 'kA/m'. Furthermore, the file is assumed to have two header lines which are being skipped on loading.

> [!IMPORTANT]
> Before loading a data file, the total, magnetic film thickness has to be specified in Step 1 of the **Simulation / Fit Procedure** section.

## Theoretical Framework

### What is a synthetic antiferromagnet (SAF)?

TODO: add some sources

A synthetic antiferromagnet (SAF) is a magnetic, thin film heterostructure. It consists of 2 ferromagnetic layers (e.g. Co, Fe, etc.) which are separated by a very thin, conductive, non-magnetic layer (e.g. Ru). In such a layer stack, an indirect, interlayer coupling arises which is usually described by the Ruderman-Kittel-Kasuya-Yosida (RKKY) model. The coupling can prefer any type of alignment between the 2 ferromagnetic layers (parallel, anti-parallel or non-collinear) depending on the material parameters - especially the thickness of the non-magnetic layer. The main focus, however, lies on the anti-parallel and non-collinear coupling.

### Macrospin Model

Currently, only a macrospin model is implemented in MagSAF. This model simplifies all magnetic moments in both of the ferromagnetic layers to one "macrospin" - just like in the Stoner-Wohlfarth model.

## Fitting procedure

First, a global minimizer is used to find good starting parameters for a subsequent local minimizer. For the global minimizer, [scipy.optimize.differential_evolution](https://docs.scipy.org/doc/scipy-1.15.0/reference/generated/scipy.optimize.differential_evolution.html) method is being used. Its *maxiter* and *popsize* parameter can be adjusted by the **fast fit**/**precise fit** option next to the fit button with **precise fit** increasing the *maxiter* and *popsize* parameter. For the subsequent local minimizer, [scipy.optimize.minimize](https://docs.scipy.org/doc/scipy-1.15.0/reference/generated/scipy.optimize.minimize.html) is being used with the *L-BFGS-B* method. Both minimizers try to minimize the Figure of Merit (FOM).

### Figure of Merit

The Figure of Merit is calculated by the following equation:

$$\large FOM = \frac{1}{N} \sum_i \frac{\Delta H_i}{\Delta H_{max}} \cdot |1 - \frac{dM^{sim}_i}{dM^{exp}_i}|$$

$N$ is the amount of data points of the full hysteresis loop, $\sum_i$ sums over all data points, $\Delta H_{i}$ is equal to $|H_{i-1} - H_i| + |H_i - H_{i+1}|$ and $\Delta H_{max}$ is the largest distance between neighboring data points in the full hysteresis loop. This first part eliminates over-weighting of specific field ranges, if the field step size changes during the hysteresis loop (e.g. smaller steps around zero field). $dM^{sim}_i$ and $dM^{exp}_i$ are the simulated and experimental $d \cdot M$ values of the respective data point, where $d \cdot M$ is the total, magnetic film thickness multiplied with the total magnetization.

> [!TIP]
> It is possible to deliberatly increase the weight of the FOM in specific field ranges. To do so, the user can set the transition fields between the antiferromagnetic (AFM) and canted (C) as well as between the canted (C) and ferromagnetic (FM) spin alignment (or any other field values) under **Fit Options**. Then, a *Fit Focus Region* can be picked (either AFM, C, FM or none). By doing so, the FOM of the picked region is multiplied by 3 to increase its weight. The regions are defined as:
> ```math
> \begin{align*}
> \text{AFM}:& 0 &< |H\;| &< H_{AFM-C} \\
> \text{C}:& H_{AFM-C} &< |H\;| &< H_{C-FM} \\
> \text{FM}:& H_{C-FM} &< |H\;|
> \end{align*}
> ```
