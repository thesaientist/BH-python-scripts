################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################

import os
import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd
import Frac_ML_Library as fracmlLib

path_to_folder = 'C:/Users/212566876/Box Sync/Rotation 3/DSWI/Marathon_Challenger_C_AC_1H_XMAC_POST/AC-1H Stages/'
stageFiles= []
stageNums = []
wellNames = []

for i in os.listdir(path_to_folder):
    if i.endswith('.txt'):
        filePath = os.path.join(path_to_folder, i)
        stageFiles.append(open(filePath,'r'))
        wellNames.append(i[:i.find('Stage')])
        stageNums.append(i[i.find('Stage')+6:i.find('.txt')])

# read in data from files and close them
stages = {}
for index, fileID in enumerate(stageFiles):
    stageData = []
    for line in fileID:
        stageData.append(line.rstrip('\n').split('\t'))
    stages[stageNums[index]] = pd.DataFrame(data=np.array(stageData[1:], dtype=float), columns=stageData[0])
    fileID.close()

# assign quantities for a particular stage
stage_i = 27


# -------------------------
# plot stage data
# -------------------------
plot_data = {}
plot_data['stages'] = stages
plot_data['well names'] = wellNames
plot_data['stage numbers'] = stageNums
fracmlLib.plot_stage_data(stage_i, plot_data)
