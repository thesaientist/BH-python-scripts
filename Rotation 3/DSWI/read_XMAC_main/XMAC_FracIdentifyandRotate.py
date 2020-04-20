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
inputFID =  open('inputXMAC_challenger_wavelet_pre.txt','r')
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

# TODO: see if these values maybe set elsewhere
boolPlots = False
width = 8   # size of 0.5*wavelength
weightParams = [2.5, 2, 2, 16, 3]
mStop = 5   # decreasing makes more fractures+

# 3. Other parameters to be set for module usage

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
# define writeData dictionary for storing values/arrays of values to pass to write file functions
writeData = {}
writeData['starting depth'] = startingDepth
writeData['ending depth'] = endingDepth
# throw an error is there is a mismatch
if isMismatch:
    print('There was an issue! The number of measured depth samples are NOT the \
		same in the horizontal and vertical slices of provided XMAC data. \
		The program will now terminate. ')
    exit()

# -----------------------------
# Read in well survey, if available
# -----------------------------
if inputData['well survey?'] == 'True':
    wellSurveyData, path = xmacLib.parseWellSurvey(inputData['well survey filepath'])

# ---------------
# MAIN ALGORITHM
# ---------------
# Summary of main routine
#   1. Organize data into horizontal and vertical as well as positive and negative slices
#   2. Search for a maximum brightness/reflectivity
#   3. Determine the location of this max spot, and identify the direction of the feature
#   4. Remove feature from the original image
#   5. Continue searching for max brightness/reflectivity features (from what remains in the image)
#   6. Stop when things are not so bright (below set threshold)

# 1. Organize parsed XMAC data into useful arrays
zData, dataNeg, dataPos, dataNegVert, dataPosVert = xmacLib.organizeXMACData(data, data_vert, \
                                                                        boolSuppress, \
                                                                        inputData['suppress limit'])
writeData['zData'] = zData

# define values to provide plot extents
rStart = inputData['rStart']
rStep = inputData['rStep']
rEnd = rStart + 512 * rStep

#-------------------------------------------------------------------------------
# CODE BELOW WAS INTRODUCED TO LOOK AT A SPECIFIC SECTION OF MARATHON AC1H WELL
# MAYBE SAFELY REMOVED, ONLY PART THAT WILL BE AFFECTED IS THE FINAL PLOTTING CODE
#-------------------------------------------------------------------------------
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

# slice being considered
stage_start_idx = np.argmin(np.absolute(zData_stages[:,1]-16))
stage_end_idx = np.argmin(np.absolute(zData_stages[:,1]-13))
start_depth = zData_stages[stage_start_idx,0]    # depth of stage closer to heel - e.g. depth of stage 17
end_depth = zData_stages[stage_end_idx,0]      # depth of stage (+1) closer to heel (i.e. end of stage is depth of stage+1) - e.g. depth of stage 12
start_index = np.argmin(np.absolute(zData-start_depth))
end_index = np.argmin(np.absolute(zData-end_depth))
perf_start_idx = np.argmin(np.absolute(zData_perfs-start_depth))
perf_end_idx = np.argmin(np.absolute(zData_perfs-end_depth))

data_closer = data[start_index:end_index, :]
data_vert_closer = data_vert[start_index:end_index, :]

zData, dataNeg, dataPos, dataNegVert, dataPosVert = xmacLib.organizeXMACData(data_closer, data_vert_closer, \
                                                                        boolSuppress, \
                                                                        inputData['suppress limit'])
data = data_closer[:,1:]
data_vert = data_vert_closer[:,1:]
#-------------------------------------------------------------------------------

# show image section being considered (on which extracted features will be plotted in the loop)
if boolPlots:
    fracFig, (fracAx1, fracAx2) = plt.subplots(1, 2, sharey=True)  # figure, axes object handles
    fracFig.suptitle('Challenger AC1H Pre-Frac Horizontal')
    origIm = fracAx1.imshow(data, aspect='equal', cmap='gist_heat_r', vmin=0, vmax=15, extent = [rStart, rEnd, zData[-1], zData[0]])
    fracAx1.set_title('Original Image (with extracted feature lines)')
    fracAx1.set_xlabel('Radius (ft)')
    fracAx1.set_ylabel('Measured depth (ft)')
    plt.tight_layout()
    fracFig.show()

def find_features(data, isPos):
    # Initialize for main routine
    spotSize = 5        # determines size of spot to search for bright zone
    regionSize = 128    # determines seize of the region to use least squares regression (LSR) 2 x region = range
    numFeatures = 100  # keeps the routine from running too long potentially
    data[data < 0] = 0
    meanI = np.mean(data)
    intnLimit = meanI * mStop   # lower threshold of limit, below which fractures/features will not be identified:
    print('Intensity threshold: {0}'.format(intnLimit))
    (xLim, yLim) = data.shape
    searchMap = np.copy(data)

    # plot check (dynamic search map image)
    if boolPlots:
        if isPos:
            imExt1 = 0
            imExt2 = rEnd
            searchMap_plot = np.copy(searchMap)
        else:
            imExt1 = rStart
            imExt2 = 0
            searchMap_plot = np.fliplr(searchMap)
        fracAx2.clear()
        searchMapIm = fracAx2.imshow(searchMap_plot, aspect='equal', cmap='gist_heat_r', vmin=0, vmax=15, extent = [imExt1, imExt2, zData[-1], zData[0]])
        fracAx2.set_title('Dynamic Search Map Image (with bright spots marked)')
        fracAx2.set_xlabel('Radius (ft)')

    fractures = xmacLib.Fracture()  # Fracture class to store extracted feature properties
    fractures.count = 0  # number of fractures/features detected
    fractures.sno = []  # fracture serial number
    fractures.iX = []    # locations of center of features in X direction
    fractures.iY = []    # locations of center of features in Y direction
    fractures.lines = []    # coordinates indices of fracture/feature lines
    fractures.length = []    # lengths of features
    fractures.angle = []     # angles that features make with the wellbore axis
    fractures.intensity = []    # reflectivity around the maximum of the feature
    fractures.quality = []      # relative quality of the angular measure based on curvature of the LSR

    # 2-6 of the main routine, as mentioned in the summary above
    stopSearch = False
    while not stopSearch:
        # find the brightest spot
        xb, yb, intn = xmacLib.findBrightest(searchMap, searchMap, spotSize)
        # always find new bright spot (after finding the bright feature above)
        # which requires removal of above feature
        xs = np.intersect1d(range(xb-spotSize*2, xb+spotSize*2+1), range(xLim))
        ys = np.intersect1d(range(yb-spotSize*2, yb+spotSize*2+1), range(yLim))
        # searchMap[np.ix_(xs, ys)] = 0   # remove the spot

        # plot check (show current bright spot on dynamic search map image)
        if boolPlots:
            xb_plot = zData[xb]
            yb_plot = rStart + rStep * (256 + (-1)**(isPos*1+1) * yb + 1)
            fracAx2.plot(yb_plot, xb_plot, 'ro')
            fracLabel = '{featurenum}'.format(featurenum=str(fractures.count+1))
            # fracAx2.text(yb_plot, xb_plot, fracLabel)

        # test whether or not this is the last fracture to be taken into account
        if intn <= meanI * mStop or fractures.count >= numFeatures-1:
            stopSearch = True
            # break

        # get region to analyze (based on bright spot identified above in this iteration)
        xl, yl, xu, yu = xmacLib.getRegion(searchMap, xb, yb, regionSize)
        region = searchMap[xl:xu, yl:yu]        # searchMap will be modified whenever region is modified because region is a view (reference)
        dataRegion = data[xl:xu, yl:yu]

        # search for the direction and location of maximum within the region
        # it also provides the indices of the fracture within the region
        bestAngle, length, x_center_idx, y_center_idx, quality, filtRegion, aline = xmacLib.weightedLSR(region, dataRegion, xb-xl, yb-yl, width, weightParams, inputData)

        # Convert angle based on isPos
        if not isPos:
            bestAngle = -bestAngle

        # Do not record if length is greater than 100 ft?
        # if length >= 100:
        #     continue

        # convert relative center coordinates of fracture to actual ones in searchMap
        xc = zData[xl + x_center_idx]
        yc = rStart + rStep * (256 + (-1)**(isPos*1+1) * (yl + y_center_idx) + 1)

        # points along fracture line to be converted from flat to coordinate indices
        # then converted from relative to absolute coordinates
        (alnx, alny) = np.unravel_index(aline, filtRegion.shape)
        alnx = xl + alnx
        alny = yl + alny
        sort_order = np.argsort(alny, kind='mergesort') # sort from closest to farthest from wellbore
        alnx = alnx[sort_order]
        alny = alny[sort_order]
        line_depths = zData[alnx]
        if isPos:
            line_radii = rStart + rStep * (256 + alny + 1)
        else:
            line_radii = rStart + rStep * (256 - alny + 1)
        fractures.lines.append((line_depths, line_radii))

        # increment the fracture count
        fractures.count += 1
        fractures.sno.append(fractures.count)
        print('Frac/feature count: {0}'.format(fractures.count))
        if np.remainder(fractures.count, 22) == 0:
            print('Intensity: {0}'.format(intn))

        # store identified fracture/feature characteristics
        fractures.iX.append(xc)
        fractures.iY.append(yc)
        fractures.length.append(length)
        fractures.angle.append(bestAngle)
        fractures.intensity.append(intn)
        fractures.quality.append(quality)

        # plot check (plot extracted feature line in this iteration, update searchMap image plot)
        if boolPlots:
            fracAx1.plot(line_radii, line_depths, 'r-')
            # fracAx1.text(yc, xc, fracLabel)
            if isPos:
                searchMapIm.set_data(searchMap)
            else:
                searchMapIm.set_data(np.fliplr(searchMap))
            fracFig.canvas.draw()
            plt.pause(0.05)

    return fractures

fracturesPos = find_features(dataPos, True)
fracturesNeg = find_features(dataNeg, False)
fracturesPosVert = find_features(dataPosVert, True)
fracturesNegVert = find_features(dataNegVert, False)

# write frac/feature properties to file (to import into JewelSuite)
writeData['frac filepath'] = inputData['well'] + '_fracs.txt'
md_p, x_p, y_p, z_p, azi_p, dip_p, len_p = xmacLib.frac_calcs_for_slice(fracturesPos, 0, True, path)
md_n, x_n, y_n, z_n, azi_n, dip_n, len_n = xmacLib.frac_calcs_for_slice(fracturesNeg, 0, False, path)
md_pv, x_pv, y_pv, z_pv, azi_pv, dip_pv, len_pv = xmacLib.frac_calcs_for_slice(fracturesPosVert, 1, True, path)
md_nv, x_nv, y_nv, z_nv, azi_nv, dip_nv, len_nv = xmacLib.frac_calcs_for_slice(fracturesNegVert, 1, False, path)
md = md_p + md_n + md_pv + md_nv                # MD array of fracs
x = x_p + x_n + x_pv + x_nv                     # Easting array of fracs
y = y_p + y_n + y_pv + y_nv                     # Northing array of fracs
z = z_p + z_n + z_pv + z_nv                     # TVD array of fracs
azi = azi_p + azi_n + azi_pv + azi_nv           # Azimuth array of fracs
dip = dip_p + dip_n + dip_pv + dip_nv           # Dip array of fracs
length = len_p + len_n + len_pv + len_nv        # Length array of fracs
sno = fracturesPos.sno + fracturesNeg.sno + fracturesPosVert.sno + fracturesNegVert.sno # Serial number array of fracs
writeData['md frac'] = md
writeData['x frac'] = x
writeData['y frac'] = y
writeData['z frac'] = z
writeData['azi frac'] = azi
writeData['dip frac'] = dip
writeData['len frac'] = length
writeData['sno frac'] = sno
wellstr = inputData['well']
writeData['label'] = (wellstr[wellstr.find('-Frac')-4:wellstr.find('-Frac')]).lstrip()
xmacLib.fracPropWrite(writeData)

# Plot horizontal and vertical slice of AC1H well
fig, (ax1, ax2)  = plt.subplots(nrows = 1, ncols = 2, sharex=True, sharey=True)
ax1.imshow(data, aspect='equal', cmap='gist_heat_r', vmin=0, vmax=15, extent = [rStart, rEnd, zData[-1], zData[0]])
for depth in zData_perfs[perf_start_idx:perf_end_idx]:
    ax1.hlines(depth, xmin=-4, xmax=4, colors='g',linewidths=3)
for i, depth in enumerate(zData_stages[stage_start_idx:stage_end_idx,0]):
    s = 'Stage {stagenum:3.0f}'.format(stagenum=zData_stages[i + stage_start_idx,1])
    ax1.text(-5, depth, s, fontsize=7)
ax1.set_title('Horizontal Cross-Section (Map View)')
ax1.set_xlabel('Radius (ft)')
ax1.set_ylabel('Measured Depth (ft)')
for i in range(fracturesPos.count):
    ax1.plot(fracturesPos.lines[i][1], fracturesPos.lines[i][0], 'r-')
for i in range(fracturesNeg.count):
    ax1.plot(fracturesNeg.lines[i][1], fracturesNeg.lines[i][0], 'r-')
ax2.imshow(data_vert, aspect='equal', cmap='gist_heat_r', vmin=0, vmax=15, extent = [rStart, rEnd, zData[-1], zData[0]])
for depth in zData_perfs[perf_start_idx:perf_end_idx]:
    ax2.hlines(depth, xmin=-4, xmax=4, colors='g',linewidths=3)
for i, depth in enumerate(zData_stages[stage_start_idx:stage_end_idx,0]):
    s = 'Stage {stagenum:3.0f}'.format(stagenum=zData_stages[i + stage_start_idx,1])
    ax2.text(-5, depth, s, fontsize=7)
ax2.set_title('Vertical Cross-Section (Side View)')
ax2.set_xlabel('Radius (ft)')
ax2.set_ylabel('Measured Depth (ft)')
for i in range(fracturesPosVert.count):
    ax2.plot(fracturesPosVert.lines[i][1], fracturesPosVert.lines[i][0], 'r-')
for i in range(fracturesNegVert.count):
    ax2.plot(fracturesNegVert.lines[i][1], fracturesNegVert.lines[i][0], 'r-')
plt.tight_layout()
fig.suptitle('Challenger AC1H Pre-Frac Stages 14-16')

# End
print ('End of program...')
