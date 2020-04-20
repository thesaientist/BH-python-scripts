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
    wellSurveyData = xmacLib.parseWellSurvey(inputData['well survey filepath'])

# ---------------
# MAIN ALGORITHM
# ---------------

# 1. Organize parsed XMAC data into useful arrays
zData, dataNeg, dataPos, dataNegVert, dataPosVert = xmacLib.organizeXMACData(data, data_vert, \
                                                                        boolSuppress, \
                                                                        inputData['suppress limit'])
writeData['zData'] = zData

# 2. Radial smoothing
dataNeg, dataPos, dataNegVert, dataPosVert = xmacLib.radialXMACSmoothing(dataNeg, dataPos, \
                                                                    dataNegVert, \
                                                                    dataPosVert, zData)

# 3. Determine directional norms and total fracture intensity at each MD
normNeg = np.sum(dataNeg, axis=1)
normPos = np.sum(dataPos, axis=1)
normNegVert = np.sum(dataNegVert, axis=1)
normPosVert = np.sum(dataPosVert, axis=1)
intn = normNeg + normPos + normNegVert + normPosVert

# 4. Determine radial extent of fracs based on integral threshold (radial distances)
rNeg, rPos, rNegVert, rPosVert = xmacLib.radialExtent(inputData, dataNeg, dataPos, \
                                                dataNegVert, dataPosVert, \
                                                normNeg, normPos, normNegVert, \
                                                normPosVert)

# 5. Smoothing in depth (frac radii and intensity)
rNeg, rPos, rNegVert, rPosVert, intn = xmacLib.depthXMACSmoothing(rNeg, rPos, rNegVert, \
                                                            rPosVert, intn)
writeData['rNeg'] = rNeg
writeData['rPos'] = rPos
writeData['rNegVert'] = rNegVert
writeData['rPosVert'] = rPosVert
writeData['intn'] = intn

# 6. Select peaks in frac intensity as fractures for discrete network (DFN)
numFractures, intnDFN, zDataDFN, rnDFN, rpDFN, rnvDFN, rpvDFN = xmacLib.selectFracs(inputData, intn, \
                                                                zData, rNeg, rPos, \
                                                                rNegVert, rPosVert)
writeData['numFractures'] = numFractures
writeData['zDataDFN'] = zDataDFN
writeData['rnDFN'] = rnDFN
writeData['rpDFN'] = rpDFN
writeData['rnvDFN'] = rnvDFN
writeData['rpvDFN'] = rpvDFN

# 7. Calculated stimulated rock volume (between the first and last frac in DFN)
srv = xmacLib.calcSRV(wellSurveyData, zData, zDataDFN, rNeg, rPos, rNegVert, rPosVert)
quantities = {} # data struction (python dict) to store calculated physical quantities
quantities['Stimulated Rock Volume'] = srv

# 8. Calculate Easting, Northing and TVD for DFN measured depths for writing to file
# if well survey file is not provided, then assign null values -9999
eastingDFN = np.zeros(zDataDFN.shape)
northingDFN = np.zeros(zDataDFN.shape)
tvdDFN = np.zeros(zDataDFN.shape)
for i in range(zDataDFN.shape[0]):
	if inputData['well survey?'] == 'True':
		eastingDFN[i], northingDFN[i], tvdDFN[i] = xmacLib.wellInterp(zDataDFN[i], wellSurveyData)
	else:
		eastingDFN[i] = -9999
		northingDFN[i] = -9999
		tvdDFN[i] = -9999
writeData['eastingDFN'] = eastingDFN
writeData['northingDFN'] = northingDFN
writeData['tvdDFN'] = tvdDFN

# 9. Interpolate to obtain 4 times as many points radially for azimuth algorithm
dataNInterp = xmacLib.interpRadial(dataNeg, 4)
dataPInterp = xmacLib.interpRadial(dataPos, 4)
dataHorizInterp = np.concatenate((np.fliplr(dataNInterp), dataPInterp), axis=1)
dataNVInterp = xmacLib.interpRadial(dataNegVert, 4)
dataPVInterp = xmacLib.interpRadial(dataPosVert, 4)

# 10. Azimuth calculations for selected fracs in DFN (15 MD samples used on either side
# for reflectivity trace shifting and stacking)
angleDFN = np.ones(zDataDFN.shape)*100
azimuthDFN = np.ones(zDataDFN.shape)*100
pointset_plane_angle = np.ones(zDataDFN.shape)*100
for i in range(zDataDFN.shape[0]):
    angleDFN[i] = xmacLib.bestAzimuth(zDataDFN[i], inputData['mdStep'], zData, inputData['rStep']/4, dataHorizInterp, 15)
    if inputData['well survey?'] == 'True':
        azimuthDFN[i] = xmacLib.fracAzimuth(angleDFN[i], zDataDFN[i], wellSurveyData)
    else:
        azimuthDFN[i] = angleDFN[i]
    pointset_plane_angle[i] = azimuthDFN[i] + 90  # the addition of 90 here allows the planes to be displayed in the direction of the frac instead of normal to it when imported as a pointset in jewelsuite
    if azimuthDFN[i] >= 360:
        azimuthDFN[i] = azimuthDFN[i]-360
    if pointset_plane_angle[i] >= 360:
        pointset_plane_angle[i] = pointset_plane_angle[i] - 360
# azimuthDFN[0] = xmacLib.bestAzimuth(zDataDFN[0], inputData['mdStep'], zData, inputData['rStep']/4, dataHorizInterp, 15)
writeData['angleDFN'] = angleDFN
writeData['azimuthDFN'] = azimuthDFN
writeData['pointset'] = pointset_plane_angle

# ---------------
# PLOTTING
# ---------------
# plt.figure(1)
# plt.subplot(1,2,2)
# plt.plot(angleDFN, np.arange(1, zDataDFN.shape[0]+1),'r.')
# plt.plot(angleDFN, zDataDFN,'rx')
# plt.ylim(zData[-1], zData[0])
# plt.ylim(zDataDFN[-1], zDataDFN[0])
# plt.ylabel('MD (ft)')
# plt.xlabel('Fracture Angle (deg)')
# plt.title('Frac Plane Angles in DFN')
# plt.show()

# # plt.figure(2)
# plt.subplot(1,2,1)
# plt.plot(intn, zData)
# plt.plot(intnDFN, zDataDFN,'rx')
# plt.vlines(inputData['intensity threshold'], ymin=zData[0], ymax=zData[-1], colors='g')
# # plt.ylim(zDataAbove[-1], zDataAbove[0])   # invert MD axis for standard log type presentation
# plt.ylim(zData[-1], zData[0])
# # plt.ylim(zDataDFN[-1], zDataDFN[0])
# # plt.ylabel('Fracture Index')
# # plt.xlabel('Fracture Angle')
# plt.ylabel('MD (ft)')
# plt.xlabel('Intensity')
# plt.title('DSWI Frac Intensity')
# plt.show()

# plt.figure()
# plt.subplot(1,2,1)
# plt.plot(intn, zData)
# plt.vlines(inputData['intensity threshold'], ymin=zData[0], ymax=zData[-1], colors='g')
# plt.plot(intnDFN, zDataDFN, 'rx')
# plt.ylim(zDataAbove[-1], zDataAbove[0])   # invert MD axis for standard log type presentation
# plt.ylim(zData[-1], zData[0])
# plt.ylim(zDataDFN[-1], zDataDFN[0])
# plt.ylabel('Fracture Index')
# plt.xlabel('Fracture Angle')
# plt.ylabel('MD (ft)')
# plt.xlabel('Intensity')
# plt.title(inputData['well'] + ': Selection of fractures - ' + str(numFractures) + ' fractures')
# plt.show()

# plt.subplot(1,2,2)
# # plt.plot(angleDFN, np.arange(1, zDataDFN.shape[0]+1),'r.')
# plt.plot(angleDFN, zDataDFN,'rx')
# plt.ylim(zData[-1], zData[0])
# # plt.ylim(zDataDFN[-1], zDataDFN[0])
# plt.ylabel('MD (ft)')
# plt.xlabel('Fracture Angle (deg)')
# plt.title('Frac Plane Angles in DFN')
# plt.show()

# ----------------------------------
# I/O (1. LAS file with frac extent and intensity; 2. text file w DFN planes)
# ----------------------------------
# 1. LOG
xmacLib.lasWrite(inputData, writeData)

# 2. TXT output for DFN
xmacLib.dfnWrite(inputData, writeData)

# 3. Calculated physical quantities
quantFilename = inputData['well'] + '_calcQuants.txt'
quantFilepath = os.path.normpath(os.path.join(os.getcwd(), quantFilename))
writeData['quant file'] = quantFilepath
xmacLib.quantityWrite(inputData, writeData, quantities)
