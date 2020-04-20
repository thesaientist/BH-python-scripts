################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# Import required built-in modules and user-defined libraries
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import XMAClib2018 as xmacLib

# ----------------------------------------
# INPUTS
# ----------------------------------------
# Define input data dictionary
inputData = {}
# 1. I/O of input data
inputFID =  open('inputXMAC_challenger_wavelet_post.txt','r')
next(inputFID)
next(inputFID)
for line in inputFID:
    if line != '\n' or line != '':
        # get value from next line and assign as float when possible, otherwise as string
        val = next(inputFID).rstrip('\n').lstrip()
        try:
            inputData[line.rstrip(':\n')] = float(val)
        except ValueError:
            inputData[line.rstrip(':\n')] = val

# 2. Other parameters to be set based on inputs
# TODO: revert to above working_dir definition for executable-convertable python code
# working_dir = os.path.dirname(sys.executable) #<-- absolute dir the script/executable is in
fid = open(inputData['xmac horizontal filepath'])  # file identifier for reading (horizontal XMAC)
fid_vert = open(inputData['xmac vertical filepath']) # file identifier for reading (vertical XMAC)
boolSuppress = inputData['suppress?']=='True' # NOTE: should some low magnitude data be suppressed?
logFilePath = os.path.normpath(os.path.join(os.getcwd(), inputData['log name']))
inputData['log filepath'] = logFilePath
txtFilePath = os.path.normpath(os.path.join(os.getcwd(), inputData['text filename']))
inputData['text filepath'] = txtFilePath

# -----------------------------
# Read in XMAC data
# -----------------------------
# use parseXMAC or parseSynthetic function to read in data
if inputData['type'] == 'xmac':
    data, startingDepth, endingDepth = xmacLib.parseXMAC(fid)
    data_vert, startingDepth_vert, endingDepth_vert = xmacLib.parseXMAC(fid_vert)
else:
    data, startingDepth, endingDepth = xmacLib.parseSynthetic(fid)
    data_vert, startingDepth_vert, endingDepth_vert = xmacLib.parseSynthetic(fid_vert)
# reconcile differences between horizontal and vertical XMAC data
data, data_vert, startingDepth, endingDepth, isMismatch = xmacLib.reconcileXMAC(startingDepth, \
                                                                        startingDepth_vert, \
                                                                        endingDepth, \
                                                                        endingDepth_vert, \
                                                                        data, data_vert)

zData, dataNeg, dataPos, dataNegVert, dataPosVert = xmacLib.organizeXMACData(data, data_vert, \
                                                                        boolSuppress, \
                                                                        inputData['suppress limit'])

# calculate plot extents
rStart = inputData['rStart']
rStep = inputData['rStep']
rEnd = rStart + 512 * rStep

# read in perfs data
perfs = np.loadtxt('AC1H_perfs_md.txt', usecols=[0, 1])
zData_perfs = perfs[:,0]
stage_perfs = perfs[:,1]
sort_order = np.argsort(zData_perfs)
zData_perfs = zData_perfs[sort_order]
stage_perfs = stage_perfs[sort_order]
zData_stages = []
for i, stageVal in enumerate(stage_perfs):
    if i==0:
        currentVal = stageVal
        zData_stages.append([zData_perfs[i], currentVal])
        continue
    if stageVal==currentVal:
        continue
    else:
        currentVal = stageVal
        zData_stages.append([zData_perfs[i], currentVal])
zData_stages = np.array(zData_stages)

# make sure perf/stage depths are in range of DSWI image data
if zData_perfs[-1] > zData[-1]:
    last_idx_perf = np.argmax(np.absolute(zData_perfs>zData[-1]))
    last_idx_stage = np.argmax(np.absolute(zData_stages[:,0]>zData[-1]))
else:
    last_idx_perf = zData_perfs.shape[0]
    last_idx_stage = zData_stages.shape[0]
if zData_perfs[0] < zData[0]:
    first_idx_perf = np.argmax(np.absolute(zData_perfs>=zData[0]))
    first_idx_stage = np.argmax(np.absolute(zData_stages[:,0]>=zData[0]))
else:
    first_idx_perf = 0
    first_idx_stage = 0
zData_perfs = zData_perfs[first_idx_perf:last_idx_perf]
zData_stages = zData_stages[first_idx_stage:last_idx_stage]
#zData_perfs_idx = np.zeros(zData_perfs.shape, dtype=int)
#for i, depth in enumerate(zData_perfs):
#    zData_perfs_idx[i] = np.argmin(np.absolute(zData-depth))


# plot different slices of data (whole DSWI image)
#fig, (ax1, ax2)  = plt.subplots(nrows = 1, ncols = 2)
#ax1.imshow(data[:,1:], aspect='auto', cmap='gist_heat_r', vmin=0, vmax=15, extent = [rStart, rEnd, zData[-1], zData[0]])
#for depth in zData_perfs:
#    ax1.hlines(depth, xmin=-1, xmax=1, colors='g')
#for i, depth in enumerate(zData_stages[:,0]):
#    s = 'Stage {stagenum:3.0f}'.format(stagenum=zData_stages[i,1])
#    ax1.text(-5, depth, s, fontsize=6)
#ax1.set_title('Horizontal Cross-Section (Map View)')
#ax1.set_xlabel('Radius (ft)')
#ax1.set_ylabel('Measured Depth (ft)')
#ax2.imshow(data_vert[:,1:], aspect='auto', cmap='gist_heat_r', vmin=0, vmax=15, extent = [rStart, rEnd, zData[-1], zData[0]])
#for depth in zData_perfs:
#    ax2.hlines(depth, xmin=-1, xmax=1, colors='g')
#for i, depth in enumerate(zData_stages[:,0]):
#    s = 'Stage {stagenum:3.0f}'.format(stagenum=zData_stages[i,1])
#    ax2.text(-5, depth, s, fontsize=6)
#ax2.set_title('Vertical Cross-Section (Side View)')
#ax2.set_xlabel('Radius (ft)')
#ax2.set_ylabel('Measured Depth (ft)')
#plt.tight_layout()
#fig.suptitle('Challenger AC1H Pre-Frac')

# plot different slices of data (STAGES 13-17)
stage_start_idx = np.argmin(np.absolute(zData_stages[:,1]-16))
stage_end_idx = np.argmin(np.absolute(zData_stages[:,1]-13))
start_depth = zData_stages[stage_start_idx,0]    # depth of stage closer to heel - e.g. depth of stage 17
end_depth = zData_stages[stage_end_idx,0]      # depth of stage (+1) closer to heel (i.e. end of stage is depth of stage+1) - e.g. depth of stage 12
start_index = np.argmin(np.absolute(zData-start_depth))
end_index = np.argmin(np.absolute(zData-end_depth))
perf_start_idx = np.argmin(np.absolute(zData_perfs-start_depth))
perf_end_idx = np.argmin(np.absolute(zData_perfs-end_depth))

data_closer = data[start_index:end_index, 1:]
data_vert_closer = data_vert[start_index:end_index, 1:]

fig, (ax1, ax2)  = plt.subplots(nrows = 1, ncols = 2)
ax1.imshow(data_closer, aspect='auto', cmap='gist_heat_r', vmin=0, vmax=15, extent = [rStart, rEnd, zData[end_index], zData[start_index]])
for depth in zData_perfs[perf_start_idx:perf_end_idx]:
    ax1.hlines(depth, xmin=-2, xmax=2, colors='g',linewidths=2)
for i, depth in enumerate(zData_stages[stage_start_idx:stage_end_idx,0]):
    s = 'Stage {stagenum:3.0f}'.format(stagenum=zData_stages[i + stage_start_idx,1])
    ax1.text(-5, depth, s, fontsize=6)
ax1.set_title('Horizontal Cross-Section (Map View)')
ax1.set_xlabel('Radius (ft)')
ax1.set_ylabel('Measured Depth (ft)')
ax2.imshow(data_vert_closer, aspect='auto', cmap='gist_heat_r', vmin=0, vmax=15, extent = [rStart, rEnd, zData[end_index], zData[start_index]])
for depth in zData_perfs[perf_start_idx:perf_end_idx]:
    ax2.hlines(depth, xmin=-2, xmax=2, colors='g',linewidths=2)
for i, depth in enumerate(zData_stages[stage_start_idx:stage_end_idx,0]):
    s = 'Stage {stagenum:3.0f}'.format(stagenum=zData_stages[i + stage_start_idx,1])
    ax2.text(-5, depth, s, fontsize=6)
ax2.set_title('Vertical Cross-Section (Side View)')
ax2.set_xlabel('Radius (ft)')
ax2.set_ylabel('Measured Depth (ft)')
plt.tight_layout()
fig.suptitle('Challenger AC1H Post-Frac Stages 14-16')