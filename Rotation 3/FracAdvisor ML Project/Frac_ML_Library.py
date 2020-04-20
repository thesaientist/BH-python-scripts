################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
import cv2
import numpy as np
import scipy
from scipy.misc import imread
# import cPickle as pickle
import random
import os
import matplotlib.pyplot as plt

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

def plot_stage_data(stage_i, plot_data):
    # Define needed arrays
    stages = plot_data['stages']
    wellNames = plot_data['well names']
    stageNums = plot_data['stage numbers']
    stage_i = str(stage_i)  # convert to string to use a key for stages dictionary
    time = stages[stage_i][:,0]
    pressure = stages[stage_i][:,1]
    slurry_rate = stages[stage_i][:,2]
    density = stages[stage_i][:,3]
    
    fig, host = plt.subplots()
    fig.subplots_adjust(right=0.75)
    
    par1 = host.twinx()
    par2 = host.twinx()
    
    # Offset the right spine of par2.  The ticks and label have already been
    # placed on the right by twinx above.
    par2.spines["right"].set_position(("axes", 1.2))
    # Having been created by twinx, par2 has its frame off, so the line of its
    # detached spine is invisible.  First, activate the frame but make the patch
    # and spines invisible.
    make_patch_spines_invisible(par2)
    # Second, show the right spine.
    par2.spines["right"].set_visible(True)
    
    p1, = host.plot(time, pressure, label="Pressure")
    p2, = par1.plot(time, slurry_rate, 'r-', label="Slurry Rate")
    p3, = par2.plot(time, density, color='turquoise',label="Density")
    
    # host.set_xlim(0, 2)
    # host.set_ylim(0, 2)
    # par1.set_ylim(0, 4)
    # par2.set_ylim(1, 65)
    
    host.set_xlabel("Time (min)")
    host.set_ylabel("Pressure (psi)")
    par1.set_ylabel("Slurry Rate (bpm)")
    par2.set_ylabel("Density (ppm)")
    fig.suptitle(wellNames[stageNums.index(stage_i)] + 'Stage ' + stage_i)
    
    host.yaxis.label.set_color(p1.get_color())
    par1.yaxis.label.set_color(p2.get_color())
    par2.yaxis.label.set_color(p3.get_color())
    
    tkw = dict(size=4, width=1.5)
    host.tick_params(axis='y', colors=p1.get_color(), **tkw)
    par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
    par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
    host.tick_params(axis='x', **tkw)
    
    lines = [p1, p2, p3]
    
    host.legend(lines, [l.get_label() for l in lines])
    
    plt.show()


def extract_features(image, vector_size=32):
    # image = imread(image_path, mode="RGB")
    try:
        # Using KAZE, cause SIFT, ORB and other was moved to additional module
        # which is adding addtional pain during install
        alg = cv2.KAZE_create()
        # Dinding image keypoints
        kps = alg.detect(image)
        # Getting first 32 of them. 
        # Number of keypoints is varies depend on image size and color pallet
        # Sorting them based on keypoint response value(bigger is better)
        kps = sorted(kps, key=lambda x: -x.response)[:vector_size]
        # computing descriptors vector
        kps, dsc = alg.compute(image, kps)
        # Flatten all of them in one big vector - our feature vector
        dsc = dsc.flatten()
        # Making descriptor of same size
        # Descriptor vector size is 64
        needed_size = (vector_size * 64)
        if dsc.size < needed_size:
            # if we have less the 32 descriptors then just adding zeros at the
            # end of our feature vector
            dsc = np.concatenate([dsc, np.zeros(needed_size - dsc.size)])
    except cv2.error as e:
        print('Error: ', e)
        return None

    return dsc
