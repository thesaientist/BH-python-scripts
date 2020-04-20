# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 09:33:43 2018

@author: 212566876
"""

import Frac_ML_Library as fracmlLib
import numpy as np
import os
import matplotlib.pyplot as plt

# assign arrays from image data (horizontal MRO Challenger AC1H slice pre-frac)
path_to_image = os.path.normpath('C:\\Users\\212566876\\Box Sync\\Rotation 3\\DSWI\\Marathon_Challenger_C_AC_1H_XMAC_PRE\\WIMGHH_wavelet.txt')
z_data = np.loadtxt(path_to_image, delimiter=',', dtype=np.float, skiprows=1, usecols=[0])
image = np.loadtxt(path_to_image, delimiter=',', dtype=np.uint8, skiprows=1, usecols=range(1,513))

# plot image
#fig = plt.figure()
#plt.imshow(image)

# Get features using openCV feature extraction algorithms
dsc = fracmlLib.extract_features(image)