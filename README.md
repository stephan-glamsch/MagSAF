# Welcome to MagSAF's documentation!

MagSAF is a GUI for fast and easy simulations of magnetic hysteresis loops of synthetic antiferromagnets (SAFs). Its target audience are reasearchers who want to get into the field of SAFs. With this software you can get familiar with the influence all of the magnetic parameters have on the hysteresis loop but also fit your experimental data to extract magnetic parameters. The simulations are currently based on a macrospin model and the software assumes an in-plane easy axis SAF. It is also possible to simulate and fit uniaxial, magnetic anisotropies.

In the future, more theoretical models, out-of-plane SAFs as well as more anisotropy options are planned.

## Getting started
tbd: add list of contents

## How to install
tbd

## How to use
tbd

## Theoretical Framework

### What is a synthetic antiferromagnet (SAF)?

TODO: add some sources

A synthetic antiferromagnet (SAF) is a magnetic, thin film heterostructure. It consists of 2 ferromagnetic layers (e.g. Co, Fe, etc.) which are separated by a very thin, conductive, non-magnetic layer (e.g. Ru). In such a layer stack, an indirect, interlayer coupling arises which is usually described by the Ruderman-Kittel-Kasuya-Yosida (RKKY) model. The coupling can prefer any type of alignment between the 2 ferromagnetic layers (parallel, anti-parallel or non-collinear) depending on the material parameters - especially the thickness of the non-magnetic layer. The main focus, however, lies on the anti-parallel and non-collinear coupling.

### Macrospin Model

Currently, only a macrospin model is implemented in MagSAF. This model simplifies all magnetic moments in both of the ferromagnetic layers to one "macrospin" - just like in the Stoner-Wohlfarth model.
