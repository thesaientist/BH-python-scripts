################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_prominences, convolve2d
from scipy import ndimage, misc

__authors__ = 'Sai Pranav Uppati'
__organization__ = 'Baker Hughes | GPE'
__date__ = '2018-10-22'
__version__ = '0.6'

__updateLog__ = """
0.6  added multiple classes and functions for approach 2 to DSWI interpretation
0.5  updated parseWellSurvey to read in inclination and azimuth data; added fracAzimuth function to get true azimuth of fracture plane
0.4  added calcSRV function to determine stimulated rock volume between the first and last selected frac in DFN
0.3  added separate ind2Dist function that converts radial indices to distances
0.2  added parseSynthetic function to handle input data that is synthetic for testing
0.1  created library with 14 functions that support read_XMAC_main.py script
"""

# function to parse XMAC input file with DSWI reflectivity data, which has
# measured depths and associated 512 reflectivity values in a certain format
def parseXMAC(fid):
    data = []
    dataRow = []
    startingDepth = -100000	# Non-sensical depth initialized for startingDepth (as a check) to prevent reassignment after initial assignment below
    for line in fid:
    	# If there is no data, then on next line there is a value
    	if line == '' or line == '\n':
    		# Store the previous row of data, if any, into the data array
    		if len(dataRow) != 0:
    			if dataRow[1] != -32767:
    				if startingDepth == -100000:
    					startingDepth = dataRow[0]	# for the first row of useful data, record the starting depth
    				data.append(dataRow)
    		dataRow = []
    	else:
    		listOfValuesInLine = [float(val) for val in line.split()]
    		dataRow.extend(listOfValuesInLine)
    # Store the last row of data, if last line of file is not empty	(also reassign ending depth)
    if len(dataRow) != 0:
    	if dataRow[1] != -32767:
    		data.append(dataRow)
    # Convert dynamic list of lists from horizontal XMAC file to numpy array
    data = np.array(data)
    endingDepth = data[-1,0]

    #--DEBUG--
    # print("Imported data...")
    # print(data)
    # print(type(data))
    # print(data.shape)

    # Make sure to close the open file
    fid.close()

    return data, startingDepth, endingDepth


# function to parse synthetic xmac input file with fake data
def parseSynthetic(fid):
    data = []
    startingDepth = -100000	# Non-sensical depth initialized for startingDepth (as a check) to prevent reassignment after initial assignment below
    next(fid)
    for line in fid:
        dataRow = line.split(',')
        dataRow2 = []
        for elem in dataRow:
        	floatelem = float(elem)
        	dataRow2.append(floatelem)
        if startingDepth == -100000:
            startingDepth = dataRow2[0]	# for the first row of useful data, record the starting depth
        data.append(dataRow2)
    # Convert dynamic list of lists from horizontal XMAC file to numpy array
    data = np.array(data)
    endingDepth = data[-1,0]

    #--DEBUG--
    # print("Imported data...")
    # print(data)
    # print(type(data))
    # print(data.shape)

    # Make sure to close the open file
    fid.close()

    return data, startingDepth, endingDepth


# function to reconcile differences between horizontal and vertical XMAC data
def reconcileXMAC(startingDepth, startingDepth_vert, \
                    endingDepth, endingDepth_vert, \
                    data, data_vert):
    # If there is discrepancy between measured depths in horizontal and vertical
    # slices of data, then fix if possible and throw an error if not
    # starting depth index
    depthStartIndex = 0
    depthStartIndex_vert = 0
    tempStartDepth = startingDepth
    if startingDepth != startingDepth_vert:
    	if startingDepth > startingDepth_vert:
    		depthStartIndex_vert = np.argwhere(data_vert[:,0] == startingDepth)[0][0]
    	else:
    		depthStartIndex = np.argwhere(data[:,0] == startingDepth_vert)[0][0]
    		tempStartDepth = startingDepth_vert
    # ending depth index
    depthEndIndex = data.shape[0]
    depthEndIndex_vert = data_vert.shape[0]
    tempEndDepth = endingDepth
    if endingDepth != endingDepth_vert:
    	if endingDepth > endingDepth_vert:
    		depthEndIndex = np.argwhere(data[:,0] == endingDepth_vert)[0][0]
    		tempEndDepth = endingDepth_vert
    	else:
    		depthEndIndex_vert = np.argwhere(data_vert[:,0] == endingDepth)[0][0]
    # eliminate depth measurements that are outside the mutually compatiable range
    data = data[depthStartIndex:depthEndIndex,:]
    data_vert = data_vert[depthStartIndex_vert:depthEndIndex_vert,:]
    # exit the program if the horizontal and vertical slices don't have the same number of samples
    if data.shape[0] == data_vert.shape[0]:
        startingDepth = tempStartDepth
        endingDepth = tempEndDepth
        isMismatch = False
    else:
        isMismatch = True

    return data, data_vert, startingDepth, endingDepth, isMismatch


# Path class to store well survey data
class Path():
    pass

# if well survey is available, parse it and get relevant attributes
def parseWellSurvey(wellSurveyFilePath):
    wellSurveyData = []
    path = Path()
    wellFID = open(wellSurveyFilePath)
    # skip 3 lines to start from 4th line
    next(wellFID)
    next(wellFID)
    next(wellFID)
    for line in wellFID:
    	listRow = line.split('\t')
    	dataRow = []
        # Columns 2, 3, 4, 7, 8, 9 (0-based index) in well survey need to be
        # Easting, Northing, TVDSS, and Measure Depth, inclination, and azimuth
    	for i in [2, 3, 4, 7, 8, 9]:
    		dataRow.append(float(listRow[i]))
    	wellSurveyData.append(dataRow)
    wellSurveyData = np.array(wellSurveyData)

    # Store data in path object
    path.x = wellSurveyData[:,0]
    path.y = wellSurveyData[:,1]
    path.z = wellSurveyData[:,2]
    path.md = wellSurveyData[:,3]
    path.inc = wellSurveyData[:,4]
    path.azi = wellSurveyData[:,5]

    # close file
    wellFID.close()

    return wellSurveyData, path


# reorganize parsed XMAC data to define useful arrays for tracking measured depth
# and reflectivity data
def organizeXMACData(data, data_vert, boolSuppress, suppressLimit):
    # Suppress values in data that are less than 8 (set to 0),
    if boolSuppress:
        data[np.absolute(data) < suppressLimit] = 0
        data_vert[np.absolute(data_vert) < suppressLimit] = 0

    # Separate into + and - (horizontal and vertical)
    zData = data[:,0]	# measured depths (MDs)
    dataNeg = np.fliplr(data[:,1:257])
    dataPos = data[:,257:]
    zDataVert = data_vert[:,0]	# these MDs should be identical to zData, otherwise there's a mismatch between horizontal and vertical data files
    dataNegVert = np.fliplr(data_vert[:,1:257])
    dataPosVert = data_vert[:,257:]

    # Convert to magnitudes
    # dataNeg = np.absolute(dataNeg)
    # dataPos = np.absolute(dataPos)
    # dataNegVert = np.absolute(dataNegVert)
    # dataPosVert = np.absolute(dataPosVert)

    #--DEBUG--
    # print(dataNeg.shape)
    # print(dataPos.shape)
    # print(dataNegVert.shape)
    # print(dataPosVert.shape)

    #--DEBUG--
    # from random import randint
    # i = randint(0, zData.shape[0]-1)
    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.subplot(2,2,1)
    # plt.plot(np.arange(1,257), dataNeg[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataNeg @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,2)
    # plt.plot(np.arange(1,257), dataPos[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataPos @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,3)
    # plt.plot(np.arange(1,257), dataNegVert[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataNegVert @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,4)
    # plt.plot(np.arange(1,257), dataPosVert[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataPosVert @ MD {}'.format(zData[i]))
    # plt.show()

    return zData, dataNeg, dataPos, dataNegVert, dataPosVert


# class to store identified features
class Fracture():
    pass


# function to smooth a 2d array/image with a moving average
def smooth2(arrayIn, nR, nC):
    kernel = np.ones((nR, nC))
    kernel = kernel/kernel.size
    arrayOut = convolve2d(arrayIn, kernel, mode='same')

    return arrayOut


# function to find the index of the brightest spot in an image/map
def findBrightest(searchMap, dataOrig, spotSize):
    smoothMap = smooth2(searchMap, spotSize, spotSize)
    intn = np.max(smoothMap)
    (xb, yb) = np.unravel_index(np.argmax(smoothMap.flatten(order='F')), smoothMap.shape, order='F')
    # center on brightest spot spotSize<window
    (xLim, yLim) = dataOrig.shape
    # tx and ty below find the square (when possible) window to be considered from overall map
    tx = np.intersect1d(range(xb-spotSize, xb+spotSize+1), range(xLim))
    ty = np.intersect1d(range(yb-spotSize, yb+spotSize+1), range(yLim))
    window = dataOrig[np.ix_(tx, ty)]
    # find relative indices of brightest spot within this window
    (xbw, ybw) = np.unravel_index(np.argmax(window.flatten(order='F')), window.shape, order='F')
    # find absolute indices within original image
    xb = tx[0] + xbw
    yb = ty[0] + ybw

    return xb, yb, intn


# function to get the lower and upper bounds of the region from the search map
# and the given maxima
def getRegion(searchMap, xb, yb, regionSize):
    # making sure the region stays in bounds
    shiftx = 1
    shifty = 1
    if xb < regionSize:
        shiftx = regionSize - xb
    elif xb + regionSize > searchMap.shape[0]:
        shiftx = searchMap.shape[0] - (xb + regionSize)

    if yb < regionSize:
        shifty = regionSize - yb
    elif yb + regionSize > searchMap.shape[1]:
        shifty = searchMap.shape[1] - (yb + regionSize)

    xl = xb - regionSize + shiftx
    yl = yb - regionSize + shifty
    xu = xb + regionSize + shiftx
    yu = yb + regionSize + shifty

    return xl, yl, xu, yu


# function to determine frac plane angle based on masking DSWI image and fitting a weighted least
# squares regression function to the reflectivity data. The regression is weighted by two factors:
# 1) proximity to the maxima
# 2) the amplitude of the arrival
# the feature angle is determined from a subset of the data and the maximum in that data range
def weightedLSR(dataFilt, dataOrig, x1, y1, width, weightParams, inputData):
    # Assign individual parameters
    distanceWeight = weightParams[0]
    renormConstant = weightParams[1]
    ainc = weightParams[2]
    meanRemove = weightParams[3]
    mStop = weightParams[4]
    xSz = inputData['mdStep']
    ySz = inputData['rStep']

    # column 0 is the x (row index, referring to MD)
    # column 1 is the y (column index, referring to radial position)
    # this designation of x and y is compatiable with angle theta, which is defined as arctan(y/x)
    # in other words slope of fracture line is tan(angle)
    indx = np.zeros((dataFilt.size, 2))
    (indx[:,0], indx[:,1]) = np.unravel_index(range(dataFilt.size), dataFilt.shape)

    # line => y-y1 = m(x-x1)
    #         m(x) - y - mx1 + y1 = 0
    #         a = m, b = -1, c = y1 - mx1
    angles = np.arange(-88, 89, ainc)
    a_coeff = np.tan(angles * np.pi / 180)  # slope m is tangent of angle
    b_coeff = -1 * np.ones(angles.shape)
    c_coeff = y1 - a_coeff * x1

    # distance of all points from each line: abs(ax0 + bx0 + c)/sqrt(a^2 + b^2)
    dist_from_line = np.zeros((angles.size, dataFilt.size))
    for i in range(angles.size):
        dist_from_line[i, :] = np.absolute(a_coeff[i] * indx[:, 0] + b_coeff[i] * indx[:, 1] + c_coeff[i]) / np.sqrt(a_coeff[i]**2 + b_coeff[i]**2)

    # distance of all points from maxima
    indx[:,0] = indx[:,0] - x1
    indx[:,1] = indx[:,1] - y1
    dist_from_max = np.sqrt((xSz * indx[:, 0])**2 + (ySz * indx[:, 1])**2)

    # reduce data to values only above background noise (mean reflectivity in this region, else 0)
    meanValue = np.mean(dataFilt)
    meanData = dataFilt - meanValue
    meanData[meanData < 0] = 0

    # determine scale factor weighted by (1) distance from max, (2) amplitude
    scale_factor = np.divide(meanData.reshape((meanData.size,)), (dist_from_max + renormConstant)**distanceWeight)
    msf = np.mean(scale_factor)
    scale_factor = scale_factor - meanRemove * msf
    scale_factor[scale_factor < 0] = 0

    # calculate weighted distances and sum for each line (minimum sum is correct line/angle)
    sum_weighted_dist = np.zeros((angles.size,))
    for i in range(angles.size):
        sum_weighted_dist[i] = np.sum(dist_from_line[i, :] * scale_factor)

    # best angle has minimum weighted distance sum
    bestIndx = np.argmin(sum_weighted_dist)
    bestAngle = angles[bestIndx]

    # convert from angle based on 1:1 dx:dy ratio to actual angle with
    # dx = mdStep or xSz and dy = rStep or ySz
    bestAngle = np.arctan(ySz / xSz * np.tan(bestAngle * np.pi / 180))
    bestAngle = bestAngle * 180 / np.pi     # convert to degrees

    # quality of angle
    qRange = np.intersect1d(range(sum_weighted_dist.size), range(bestIndx-3, bestIndx+4))
    quality = np.polyfit(angles[qRange], sum_weighted_dist[qRange], 2)
    quality = quality[0]

    #--DEBUG--
    # plot checks
    # plt.imshow(dist_from_line[bestIndx, :].reshape(dataFilt.shape)) # show distance from best fit line
    # scaled_dist = np.multiply(dist_from_line[bestIndx, :], scale_factor)
    # plt.imshow(scaled_dist.reshape(dataFilt.shape))     # show residual of best fit
    # plt.imshow(scale_factor.reshape(dataFilt.shape))    # show the data being taken into consideration
    #--

    # call for function get_length_center_and_remove() to determine the extent of the feature
    length, cxb, cyb, filtRegion, aline = get_length_center_and_remove(dataFilt, dataOrig, a_coeff[bestIndx], x1, y1, xSz, ySz, mStop, width)
    #--DEBUG--
    # plot check
    # plt.figure()
    # plt.imshow(filtRegion)
    # plt.plot(cyb, cxb, 'x')
    #--

    return bestAngle, length, cxb, cyb, quality, filtRegion, aline


# function to determine the termination points of the identified feature
def get_length_center_and_remove(dataFilt, dataOrig, a, x1, y1, xSz, ySz, mStop, width):
    # length is length of the segment that is the fracture length
    # cx1 is the center of the fracture in x
    # cy1 is the center of the fracture in y
    # x is the array of indices of the line in x-direction
    # y is the array of indices of the line in y-direction

    (xLim, yLim) = dataFilt.shape

    # determine points along the line
    xMin = 0
    yMin = y1 - (x1 - xMin) * a
    yMax = y1 - (x1 - (xLim-1)) * a

    # generate indices on the line in the range of x
    x, y = bresenham(xMin, yMin, xLim-1, yMax)

    # check that y values are in range
    inRange = np.in1d(y, np.arange(yLim))
    y = y[inRange]
    # select only x values in range
    x = x[inRange]
    # sort in increasing x
    sort_order = np.argsort(x, kind='mergesort')
    x = x[sort_order]
    y = y[sort_order]

    # determine the end point in positive x direction
    # mData = dataOrig - mStop * np.mean(dataOrig)
    # mData[mData<0] = 0
    i_term = findTermination(dataFilt, x1, y1, x, y, mStop, True)
    # determine the end point in negative x direction
    i_start = findTermination(dataFilt, x1, y1, x, y, mStop, False)

    # determine length from endpoints
    # if i_term == i_start:
    #     i_start = 1
    #     i_term = x.size
    dx = (x[i_term] - x[i_start])*xSz
    dy = (y[i_term] - y[i_start])*ySz
    length = np.sqrt(dx**2 + dy**2)

    # determine center
    cix = np.round((i_term+i_start)/2)
    cix = cix.astype('int32')
    cx1 = x[cix]
    cy1 = y[cix]

    # remove the data on the line
    x_rel = x[i_start:i_term+1]     # part of the line that overlays feature
    y_rel = y[i_start:i_term+1]     # part of the line that overlays feature

    #--DEBUG--
    # plot check
    # featureLineFig, featureLineAx = plt.subplots()
    # featureLineAx.imshow(dataOrig)
    # featureLineAx.plot(y_rel, x_rel, '-rx')
    # featureLineFig.show()

    dataFilt, aline = removeLineWidth(dataFilt, a, x_rel, y_rel, width, 0)

    return length, cx1, cy1, dataFilt, aline


# function to implement Bresenham line algorithm to approximate a straight line in 2D raster,
# such as displayed in imshow() plots
def bresenham(x1, y1, x2, y2):
    # Input:
    #   (x1, y1): Start position
    #   (x2, y2): End position
    # Output:
    #   arrays x and y, containing the line coordinates from (x1, y1) to (x2, y2)
    x1 = np.round(x1)
    x2 = np.round(x2)
    y1 = np.round(y1)
    y2 = np.round(y2)
    dx = np.absolute(x2 - x1)
    dy = np.absolute(y2 - y1)
    boolSteep = dy>dx

    if boolSteep:
        temp = dx
        dx = dy
        dy = temp

    # main bresenham algorithm
    if dy==0:
        q = np.zeros(dx + 1)
    else:
        arr = np.linspace(np.floor(dx/2), -dy*dx+np.floor(dx/2), num=dx+2)
        arr = np.remainder(arr, dx)
        q = (np.diff(arr) >= 0) * 1
        # q = np.insert(arr, 0, 0)

    # assign x and y arrays of coordinates based on boolSteep
    if boolSteep:
        if y1 <= y2:
            y = np.arange(y1, y2+1)
        else:
            y = np.arange(y1, y2-1, -1)

        if x1 <= x2:
            x = x1 + np.cumsum(q)
        else:
            x = x1 - np.cumsum(q)
    else:
        if x1 <= x2:
            x = np.arange(x1, x2+1)
        else:
            x = np.arange(x1, x2-1, -1)

        if y1 <= y2:
            y = y1 + np.cumsum(q)
        else:
            y = y1 - np.cumsum(q)

    # convert to integers
    x = x.astype('int32')
    y = y.astype('int32')

    return x, y


# function that finds where the feature line goes back to the mean of the data (background noise level)
def findTermination(data, x1, y1, x, y, mStop, isPos):
    #--DEBUG--
    # plot check
    # plt.figure()
    # plt.imshow(data)
    # plt.plot(y, x, '-rx')

    # find index of (x1, y1) with given x, y coordinate arrays
    for i in range(x.size):
        if x[i]==x1 and y[i]==y1:
            ix1 = i
            break

    # in case the actual maximum is not in bresenham-derived x,y coordinate arrays
    try:
        ix1
    except NameError:   # find a new max data point within x, y cooridinate points given
        ix1 = 0
        dataMax = data[x[ix1], y[ix1]]
        for i in range(x.size):
            if data[x[i], y[i]] > dataMax:
                dataMax = data[x[i], y[i]]
                ix1 = i

    # determine termination point in one direction (positive or negative x direction)
    termination_pt = ix1
    count_zeros = 0
    if isPos:
        for i in range(ix1, x.size):    # check in the positive x direction
            if data[x[i], y[i]] > 0:
                count_zeros = 0
                termination_pt = i
            else:
                count_zeros += 1
                if count_zeros > 20:
                    break
    else:
        for i in range(ix1, 0, -1):     # check in the negative x direction
            if data[x[i], y[i]] > 0:
                count_zeros = 0
                termination_pt = i
            else:
                count_zeros += 1
                if count_zeros > 20:
                    break

    return termination_pt


# function that removes data on identified feature line with given width
def removeLineWidth(dataFilt, a, x, y, width, whitenEdge):
    dataShape = dataFilt.shape
    remove = np.ravel_multi_index(np.array([x,y]), dataShape)
    aline = remove
    dataFilt.flat[remove] = whitenEdge

    # remove consecutive widths in either x- or y-direction based on slope of line
    if np.absolute(a) > 1:  # if the angle of feature is steep (more than 45 deg)
        # ...then take widths in x direction and whiten out those values
        sort_order = np.argsort(x, kind='mergesort')
        x = x[sort_order]
        y = y[sort_order]
        for i in range(1, width+1):
            if (x+i < dataShape[0]).all():      # make sure within boundary for selected width
                iFilt = np.ravel_multi_index(np.array([x+i, y]), dataShape)
                dataFilt.flat[iFilt] = whitenEdge
            if (x-i >= 0).all():                # make sure within boundary for selected width
                iFilt = np.ravel_multi_index(np.array([x-i, y]), dataShape)
                dataFilt.flat[iFilt] = whitenEdge

    else:                   # if the angle of feature isn't steep (less than 45 deg)
        # ...then take widths in y direction and whiten out those values
        sort_order = np.argsort(y, kind='mergesort')
        y = y[sort_order]
        x = x[sort_order]
        for i in range(1, width+1):
            if (y+i < dataShape[1]).all():      # make sure within boundary for selected width
                iFilt = np.ravel_multi_index(np.array([x, y+i]), dataShape)
                dataFilt.flat[iFilt] = whitenEdge
            if (y-i >= 0).all():
                iFilt = np.ravel_multi_index(np.array([x, y-i]), dataShape)
                dataFilt.flat[iFilt] = whitenEdge

    return dataFilt, aline


# function to smooth the reflectivity data radially over 7 points at a time
def radialXMACSmoothing(dataNeg, dataPos, dataNegVert, dataPosVert, zData):
    # Smoothing 7 points
    dataNegSmoothed = dataNeg
    dataPosSmoothed = dataPos
    dataNegVertSmoothed = dataNegVert
    dataPosVertSmoothed = dataPosVert
    for col in range(3,dataNeg.shape[1]-3):
    	dataNegSmoothed[:, col] = np.mean(dataNeg[:, col-3:col+3], axis=1)
    	dataPosSmoothed[:, col] = np.mean(dataPos[:, col-3:col+3], axis=1)
    	dataNegVertSmoothed[:, col] = np.mean(dataNegVert[:, col-3:col+3], axis=1)
    	dataPosVertSmoothed[:, col] = np.mean(dataPosVert[:, col-3:col+3], axis=1)
    dataNeg = dataNegSmoothed
    dataPos = dataPosSmoothed
    dataNegVert = dataNegVertSmoothed
    dataPosVert = dataPosVertSmoothed

    #--DEBUG--
    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.subplot(2,2,1)
    # plt.plot(np.arange(1,257), dataNeg[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataNeg @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,2)
    # plt.plot(np.arange(1,257), dataPos[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataPos @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,3)
    # plt.plot(np.arange(1,257), dataNegVert[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataNegVert @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,4)
    # plt.plot(np.arange(1,257), dataPosVert[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataPosVert @ MD {}'.format(zData[i]))
    # plt.show()

    return dataNeg, dataPos, dataNegVert, dataPosVert


# function to smooth the fracture radial extent and fracture intensity in depth
# with a weighted filter
def depthXMACSmoothing(rNeg, rPos, rNegVert, rPosVert, intn):
    # Smoothing in depth (both radial extent and intensity)
    # 1. Radii
    rNegSmoothed = rNeg
    rPosSmoothed = rPos
    rNegVertSmoothed = rNegVert
    rPosVertSmoothed = rPosVert
    filterDef = np.concatenate((np.arange(1,8), np.arange(6,0,-1))) / 49
    for i in range(6, rNeg.shape[0]-7):
    	rNegSmoothed[i] = np.dot(rNeg[i-6:i+7], filterDef)
    	rPosSmoothed[i] = np.dot(rPos[i-6:i+7], filterDef)
    	rNegVertSmoothed[i] = np.dot(rNegVert[i-6:i+7], filterDef)
    	rPosVertSmoothed[i] = np.dot(rPosVert[i-6:i+7], filterDef)
    rNeg = rNegSmoothed
    rPos = rPosSmoothed
    rNegVert = rNegVertSmoothed
    rPosVert = rPosVertSmoothed
    # 2. Intensity
    intnSmoothed = intn
    for i in range(6, intn.shape[0]-7):
        intnSmoothed[i] = np.dot(intn[i-6:i+7], filterDef)
    intn = intnSmoothed

    return rNeg, rPos, rNegVert, rPosVert, intn


# function to determine cumulative intensity and radial extent based on integral threshold
def radialExtent(inputData, dataNeg, dataPos, dataNegVert, dataPosVert, \
                    normNeg, normPos, normNegVert, normPosVert):
    # Define constants needed for calculations
    integral = inputData['cumulative intensity threshold']

    # Cumulative sum, ignoring the division by zero warnings (which will later be replaced by 1's)
    with np.errstate(invalid = 'ignore'):
    	cumSumNormNeg = np.divide(np.cumsum(dataNeg, axis=1), normNeg[:,None])
    	cumSumNormPos = np.divide(np.cumsum(dataPos, axis=1), normPos[:,None])
    	cumSumNormNegVert = np.divide(np.cumsum(dataNegVert, axis=1), normNegVert[:,None])
    	cumSumNormPosVert = np.divide(np.cumsum(dataPosVert, axis=1), normPosVert[:,None])
    cumSumNormNeg[np.where(np.isnan(cumSumNormNeg))] = 1
    cumSumNormPos[np.where(np.isnan(cumSumNormPos))] = 1
    cumSumNormNegVert[np.where(np.isnan(cumSumNormNegVert))] = 1
    cumSumNormPosVert[np.where(np.isnan(cumSumNormPosVert))] = 1
    # Radial extent based on reaching threshold integral value for cumul. frac intensity
    nDepth = dataNeg.shape[0]
    rNeg = np.zeros((nDepth,))
    rPos = np.zeros((nDepth,))
    rNegVert = np.zeros((nDepth,))
    rPosVert = np.zeros((nDepth,))
    for row in range(nDepth):
    	rNeg[row] = np.argmax(cumSumNormNeg[row,:] > integral) + 1
    	rPos[row] = np.argmax(cumSumNormPos[row,:] > integral) + 1
    	rNegVert[row] = np.argmax(cumSumNormNegVert[row,:] > integral) + 1
    	rPosVert[row] = np.argmax(cumSumNormPosVert[row,:] > integral) + 1

    # Convert radial position indices to distances
    rNeg, rPos, rNegVert, rPosVert = ind2Dist(rNeg, rPos, rNegVert, rPosVert, inputData)

    return rNeg, rPos, rNegVert, rPosVert


# function to convert radial position indices to radial distances
def ind2Dist(rNeg, rPos, rNegVert, rPosVert, inputData):
    # Define required constants
    rStart = inputData['rStart']
    rStep = inputData['rStep']
    # Calculate distances based on position indices
    rn = rStart + rStep * (256 - rNeg)
    rp = rStart + rStep * (256 + rPos)
    rnv = rStart + rStep * (256 - rNegVert)
    rpv = rStart + rStep * (256 + rPosVert)

    return rn, rp, rnv, rpv


# function to select fractures for DFN based on peaks in intensity curve (above given threshold)
# Based on threshold approach, intensity values below set threshold
# will not be considered for visualization
def selectFracs(inputData, intn, zData, rNeg, rPos, rNegVert, rPosVert):
    # Define constants
    intnThresh = inputData['intensity threshold']
    peak_distance = inputData['peak distance']
    peak_prominence = inputData['peak prominence']

    # Find peaks based on threshold, distance b/t peaks and peak prominence conditions
    peaks, _ = find_peaks(intn, distance=peak_distance, height=intnThresh, prominence=peak_prominence)
    numFractures = peaks.size

    # Store selected fracture relevant intensities, MDs, and radii
    intnDFN = intn[peaks]
    zDataDFN = zData[peaks]
    rnDFN = rNeg[peaks]
    rpDFN = rPos[peaks]
    rnvDFN = rNegVert[peaks]
    rpvDFN = rPosVert[peaks]

    return numFractures, intnDFN, zDataDFN, rnDFN, rpDFN, rnvDFN, rpvDFN


# Define function to interpolate Easting, Northing, and TVD for a given MD, if
# well survey data with Easting, Northing, TVD and MD values are provided
def wellInterp(md, wellSurveyData):
    # Define arrays
    mds = wellSurveyData[:,3]
    eastings = wellSurveyData[:,0]
    northings = wellSurveyData[:,1]
    tvds = wellSurveyData[:,2]

    # linear interpolation (point on the wellbore where the frac intersects)
    Easting = np.interp(md, mds, eastings)
    Northing = np.interp(md, mds, northings)
    TVD = np.interp(md, mds, tvds)

    return Easting, Northing, TVD

# Define function to interpolate and adjust Easting, Northing and TVD for a
# given MD, and radial offset of a feature from wellbore and the orientation of
# DSWI slice from which it was obtained
def locate_and_orient_frac(path, md, r, fracAngle, sliceDir, isPos):
    # sliceDir: 0 (Horizontal), 1 (Vertical)

    # first determine x, y, z of wellbore at given md
    x_well = np.interp(md, path.md, path.x)
    y_well = np.interp(md, path.md, path.y)
    z_well = np.interp(md, path.md, path.z)
    inc_well = np.interp(md, path.md, path.inc) * np.pi/180
    azi_well = np.interp(md, path.md, path.azi) * np.pi/180

    # dz, dl (azimuthal direction length change), dx, dy calculations
    if sliceDir == 0:   # horizontal slice
        dz = 0
        if azi_well < np.pi/2:      # quadrant 1 (azimuth less than 90deg)
            angle = np.pi/2 - azi_well
            dx = -r * np.sin(angle)
            dy = r * np.cos(angle)
        elif azi_well < np.pi:      # quadrant 2 (azimuth less than 180deg)
            angle = azi_well - np.pi/2
            dx = r * np.sin(angle)
            dy = r * np.cos(angle)
        elif azi_well < 3*np.pi/2:   # quadrant 3 (azimuth less than 270deg)
            angle = np.pi/2 - (azi_well - np.pi)
            dx = r * np.sin(angle)
            dy = -r * np.cos(angle)
        else:                       # quadrant 4
            angle = azi_well - 3*np.pi/2
            dx = -r * np.sin(angle)
            dy = -r * np.cos(angle)
    else:               # Vertical slice
        if inc_well <= 90:
            dz = r * np.sin(inc_well)
            dl = -r * np.cos(inc_well)
            dy = dl * np.cos(azi_well)
            dx = dl * np.sin(azi_well)
        else:
            dz = r * np.sin(180-inc_well)
            dl = r * np.cos(180-inc_well)
            dy = dl * np.cos(azi_well)
            dx = dl * np.sin(azi_well)

    # frac start point coordinates
    x = x_well + dx
    y = y_well + dy
    z = z_well + dz

    # azimuth and dip calc
    if sliceDir == 0:
        dip = 0
        if isPos:
            if fracAngle >= 0:
                azi = azi_well * 180/np.pi - fracAngle
            else:
                azi = azi_well * 180/np.pi - (180 + fracAngle)
        else:
            if fracAngle >= 0:
                azi = azi_well * 180/np.pi - (180 + fracAngle)
            else:
                azi = azi_well * 180/np.pi - (360 + fracAngle)
    else:
        azi = azi_well * 180/np.pi
        if isPos:
            if fracAngle >= 0:
                dip = fracAngle
            else:
                dip = 180 + fracAngle
        else:
            if fracAngle >= 0:
                dip = 180 + fracAngle
            else:
                dip = 360 + fracAngle

    return x, y, z, azi, dip


# function to write calculated frac properties to array
def frac_calcs_for_slice(slice, sliceDir, isPos, path):
    md = []
    x = []
    y = []
    z = []
    azi = []
    dip = []
    length = []

    for i in range(slice.count):
        if slice.length[i] != 0:
            depth = slice.lines[i][0][0]
            md.append(depth)
            r = slice.lines[i][1][0]
            angle = slice.angle[i]
            x_frac, y_frac, z_frac, azi_frac, dip_frac = locate_and_orient_frac(path, depth, r, angle, sliceDir, isPos)
            x.append(x_frac)
            y.append(y_frac)
            z.append(z_frac)
            azi.append(azi_frac)
            dip.append(dip_frac)
            length.append(slice.length[i])

    return md, x, y, z, azi, dip, length


# function to write frac/feature properties to text file
def fracPropWrite(writeData):
    # Define values needed for write point set text file
    md = writeData['md frac']
    x = writeData['x frac']
    y = writeData['y frac']
    z = writeData['z frac']
    azi = writeData['azi frac']
    dip = writeData['dip frac']
    length = writeData['len frac']
    sno = writeData['sno frac']
    label = writeData['label']

    # Write file
    fracOutput = open(writeData['frac filepath'], 'w')
    fracOutput.write("Easting Northing TVDSS StructureAzimuth StructureDip FracLength MD SNo Label\n")
    fracOutput.write("ft ft ft deg deg ft ft . .\n")
    for i in range(len(md)):
        fracOutput.write("{0} {1} {2} {3} {4} {5} {6} {7} {8}\n".format(x[i],
                                                                y[i],
                                                                z[i],
    															azi[i],
                                                                dip[i],
                                                                length[i],
                                                                md[i],
                                                                sno[i],
                                                                label))
    fracOutput.close()

    return


# Interpolation func to convert to n times as many samples radially at all MDs
# for example 4 times, 256 samples in each of the 4 directions becomes 1021 samples in each
def interpRadial(dataXYZ, n):
	numSamples = dataXYZ.shape[1] + (dataXYZ.shape[1] - 1) * (n - 1)
	quadDataXYZ = np.zeros((dataXYZ.shape[0], numSamples))
	origSampleArray = np.arange(1,257)
	newSampleArray = np.linspace(1.0, 256.0, num=numSamples)
	for row in range(dataXYZ.shape[0]):
		quadDataXYZ[row, :] = np.interp(newSampleArray, origSampleArray, dataXYZ[row, :])

	return quadDataXYZ


# Define function to determine stacking of reflectivity signal traces at a given angle
# for the fracture selected at a certain MD in DFN Selection and return
# the metric for how good the traces stack (standard deviation: high - good stacking,
# low - poor stacking)
def reflectivityStack(angle, measDepth, mdStep, zData, stepSize, dataInterp, numMDSamples):
    # Define vertical shift array (numMDSamples samples on either side) for trace shift as empty list
    vsArray = []
    for i in range(1, numMDSamples+1):
        hs = i*mdStep
        vs = np.absolute(np.tan(angle*np.pi/180) * hs)
        vs = np.rint(vs / stepSize)	# vertical shift by this many radial samples
        vsArray.append(vs)
    # DEBUG:--
    # print(vsArray)
    # --
    # Find the index of current measured depth in zData
    depthRow = np.argwhere(zData == measDepth)[0][0]
    # Obtain the reflectivity data, apply vertical shift (circularly), at relevant measured depths
    reflData = np.zeros((numMDSamples*2+1, dataInterp.shape[1]))
    for i in range(-numMDSamples, numMDSamples+1):
        if i<0:
            if angle>=0:
                reflData[i+numMDSamples, :] = np.roll(dataInterp[depthRow + i, :], int(vsArray[-i-1]))
            else:
                reflData[i+numMDSamples, :] = np.roll(dataInterp[depthRow + i, :], int(-1*vsArray[-i-1]))
        elif i>0:
            if angle>=0:
                reflData[i+numMDSamples, :] = np.roll(dataInterp[depthRow + i, :], int(-1*vsArray[i-1]))
            else:
                reflData[i+numMDSamples, :] = np.roll(dataInterp[depthRow + i, :], int(vsArray[i-1]))
        else:
            reflData[i+numMDSamples, :] = dataInterp[depthRow + i, :]
    # Sum all the shifted traces at the 31 MDs to get a resultant stacked trace
    sumReflData = np.sum(reflData, axis=0)
    # DEBUG:--
    # plt.figure()
    # plt.plot(range(dataInterp.shape[1]), sumReflData)
    # plt.xlabel("radial space")
    # plt.ylabel("reflectivity")
    # plt.title("Stacked reflectivity with angle = {} @ MD = {}".format(angle, measDepth))
    # plt.show()
    #--
    # Get standard deviation of resultant trace
    stdReflData = np.std(sumReflData)

    return stdReflData, sumReflData


# Define a function that compares the output (standard deviation) from reflectivityStack function
# for various angles and picks the best angle
def bestAzimuth(measDepth, mdStep, zData, stepSize, dataInterp, numMDSamples):
    trialAnglesPos = np.linspace(1, 89, 89)
    trialAnglesNeg = np.linspace(-1, -89, 89)
    trialAngles = np.concatenate((trialAnglesPos, trialAnglesNeg))
    stdAngles = np.zeros(trialAngles.shape)
    # Compute standard deviation of stacked reflectivity trace for all trial angles
    #DEBUG:--
    # plt.figure()
    for i in range(trialAngles.shape[0]):
    	# Below couple of lines are to make sure that there are at least numMDSamples more
    	# measured depth samples after the current MD being considered; if not,
    	# break out of the loop; same for before the current MD
    	depthRow = np.argwhere(zData == measDepth)[0][0]
    	if depthRow + numMDSamples > zData.shape[0]-1 or depthRow - numMDSamples < 0:
    		break
    	stdAngles[i], sumReflData = reflectivityStack(trialAngles[i], measDepth, mdStep, zData, stepSize, dataInterp, numMDSamples)
    	#DEBUG: --
    	# plt.cla()
    	# plt.plot(range(2042), sumReflData)
    	# plt.xlabel("radial space")
    	# plt.ylabel("reflectivity")
    	# plt.title("Stacked reflectivity with angle = {} @ MD = {}".format(trialAngles[i], measDepth))
    	# plt.pause(0.3)
    	#--
    # plt.show()
    #--
    # DEBUG: plot standard deviation vs angle
    # plt.figure()
    # plt.plot(stdAngles, trialAngles, 'b.')
    # plt.xlabel('standard deviation')
    # plt.ylabel('angle')
    # plt.title('angle vs. stdev')
    # plt.show()

    # Pick the angle that corresponds to the largest standard deviation
    indLowestStd = np.argmax(stdAngles)
    bestAngle = trialAngles[indLowestStd]

    return bestAngle


# function to calculate azimuth of frac plane, based on relative angle given w.r.t. wellbore
def fracAzimuth(angle, md, wellSurveyData):
    mds = wellSurveyData[:,3]
    azimuths = wellSurveyData[:,5]

    azimuth = np.interp(md, mds, azimuths)
    fracAbsoluteAzimuth = azimuth - angle

    return fracAbsoluteAzimuth


# function to calculate stimulated rock volume (SRV) based on radial extents
def calcSRV(wellSurveyData, zData, zDataDFN, rn, rp, rnv, rpv):
    # Bound the measured depths with first and last selected MD in DFN frac selection
    lowerBound = np.argwhere(zData == zDataDFN[0])[0][0]
    upperBound = np.argwhere(zData == zDataDFN[-1])[0][0]

    # Change lowerBound based on inclination of well (focus on horizontal portion, >=85 deg)
    inclinations = wellSurveyData[:,4]
    horizontal_incl_index = np.argmax(inclinations > 85)
    if horizontal_incl_index > lowerBound:
        lowerBound = horizontal_incl_index

    # Summation/integral to find volume (each volume is calculated based on a frustum shape)
    srv = 0
    for i in range(lowerBound + 1, upperBound + 1):
        area_i = (rp[i] - rn[i]) * (rpv[i] - rnv[i])
        area_im1 = (rp[i-1] - rn[i-1]) * (rpv[i-1] - rnv[i-1])
        h = zData[i] - zData[i-1]
        vol = 1.0/3.0 * h * (area_i + area_im1 + np.sqrt(area_i * area_im1))
        srv += vol

    return srv


# function to write a text file with calculated physical quantities
def quantityWrite(inputData, writeData, quantities):
    # Define paramaters
    filePath = writeData['quant file']
    qFID = open(filePath, 'w')
    companyName = inputData['company']
    wellName = inputData['well']

    # Write file
    qFID.write('Company: {}\n'.format(companyName))
    qFID.write('Well: {}\n'.format(wellName))
    qFID.write('\n')
    for key in quantities:
        qFID.write(key + '\n')
        qFID.write('\t' + str(quantities[key]))

    # close file
    qFID.close()

    return


# function to write LAS file for radial extents and fracture intensity
def lasWrite(inputData, writeData):
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    # outputFileName = 'logOutput_' + timestr +'.txt'
    logOutputID = open(inputData['log filepath'], 'w')

    # Define values needed for writing file
    companyName = inputData['company']
    wellName = inputData['well']
    fieldName = inputData['field']
    locationName = inputData['location']
    countyName = inputData['county']
    stateName = inputData['state']
    countryName = inputData['country']
    serviceCompanyName = inputData['service company']
    logDate = inputData['log date']
    apiNumber = inputData['api']
    wellID = inputData['well id']
    apiCode = inputData['api code']
    mdStep = inputData['mdStep']
    startingDepth = writeData['starting depth']
    endingDepth = writeData['ending depth']
    zData = writeData['zData']
    nDepth = zData.shape[0]
    rNeg = writeData['rNeg']
    rPos = writeData['rPos']
    rNegVert = writeData['rNegVert']
    rPosVert = writeData['rPosVert']
    intn = writeData['intn']

    # Writing out header lines of LAS file
    logOutputID.write('~Version Information\n')
    logOutputID.write(' VERS.                2.00:   CWLS log ASCII Standard -VERSION 2.00\n')
    logOutputID.write(' WRAP.                  NO:   One line per frame      \n')
    logOutputID.write('~Well Information Block\n')
    logOutputID.write('#MNEM.UNIT                  Well Data                   Data Description\n')
    logOutputID.write('#----.----   ----------------------------------------   -------------------------------\n')
    logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STRT.FT', startingDepth, 'Starting Depth'))
    logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STOP.FT', endingDepth, 'Ending Depth'))
    logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STEP.FT', mdStep, 'Level Spacing'))
    logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('NULL.', -9999, 'Absent Value'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('COMP.', companyName, 'Company'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('WELL.', wellName, 'Well'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('FLD .', fieldName, 'Field'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('LOC .', locationName, 'Location'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('CNTY.', countyName, 'County'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('STAT.', stateName, 'State'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('CTRY.', countryName, 'Country'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('SRVC.', serviceCompanyName, 'Service Company'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('DATE.', logDate, 'Log Date'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('API .', apiNumber, 'API Number'))
    logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('UWI .', wellID, 'Unique Well ID'))
    logOutputID.write('~Curve Information Block\n')
    logOutputID.write('#MNEM    .UNIT        API Codes     Curve Description\n')
    logOutputID.write('#--------.--------   ------------   ---------------------------------------------------\n')
    logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('DEPT', 'FT', apiCode, 'DEPTH'))
    logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('HZUP', 'FT', apiCode, 'DSWI_HZ_Contour_+'))
    logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('HZDN', 'FT', apiCode, 'DSWI_HZ_Contour_-'))
    logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('VTDN', 'FT', apiCode, 'DSWI_VT_Contour_+'))
    logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('VTUP', 'FT', apiCode, 'DSWI_VT_Contour_-'))
    logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('INTN', '', apiCode, 'DSWI_TotalFractureIntensity'))

    # Writing out log data
    logOutputID.write('#  Curve Data\n')
    logOutputID.write('~A   DEPT       HZUP      HZDN      VTDN      VTUP      INTN\n')
    # All the depths with null intensity values at the beginning until the first MD with usable values
    if zData[0] != startingDepth:
    	depthIncrementCount = 0
    	while startingDepth + 0.5*depthIncrementCount < zData[0]:
    		logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(startingDepth + 0.5*depthIncrementCount,
    																							-9999,
    																							-9999,
    																							-9999,
    																							-9999,
    																							-9999))
    		depthIncrementCount += 1
    # First MD with usable values
    logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(zData[0],
    																							rPos[0],
    																							rNeg[0],
    																							rPosVert[0],
    																							rNegVert[0],
    																							intn[0]))
    # Loop through MDs, adding MDs with null intensity values where MD increment(s) are missing
    for iDepth in range(1, nDepth):
    	# Recording the missing MDs with null intensity
    	if zData[iDepth] - zData[iDepth-1] != 0.5:
    		depthIncrementCount = 1
    		while zData[iDepth-1] + 0.5*depthIncrementCount < zData[iDepth]:
    			logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(zData[iDepth-1] + 0.5*depthIncrementCount,
    																							-9999,
    																							-9999,
    																							-9999,
    																							-9999,
    																							-9999))
    			depthIncrementCount += 1
    	# Recording the accounted for MDs with calculated intensity values
    	logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(zData[iDepth],
    																							rPos[iDepth],
    																							rNeg[iDepth],
    																							rPosVert[iDepth],
    																							rNegVert[iDepth],
    																							intn[iDepth]))
    # All the depths (if any) with null values after the final MD through the above loop, until the ending depth is reached
    if zData[-1] != endingDepth:
    	depthIncrementCount = 1
    	while zData[-1] + 0.5*depthIncrementCount <= endingDepth:
    		logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(zData[-1] + 0.5*depthIncrementCount,
    																							-9999,
    																							-9999,
    																							-9999,
    																							-9999,
    																							-9999))
    		depthIncrementCount += 1
    # Close log write file
    logOutputID.close()

    return


# function to write the DFN text file with a point set of all the selected fracture planes,
# their respective coordinates and properties
def dfnWrite(inputData, writeData):
    # Define values needed for write point set text file
    zDataDFN = writeData['zDataDFN']
    eastingDFN = writeData['eastingDFN']
    northingDFN = writeData['northingDFN']
    tvdDFN = writeData['tvdDFN']
    azimuthDFN = writeData['azimuthDFN']
    rpDFN = writeData['rpDFN']
    rnDFN = writeData['rnDFN']
    rpvDFN = writeData['rpvDFN']
    rnvDFN = writeData['rnvDFN']
    plane_angle = writeData['pointset']
    angle = writeData['angleDFN']

    # Write file
    dfnOutput = open(inputData['text filepath'], 'w')
    dfnOutput.write("MD Easting Northing TVDSS StructureAzimuth Angle_with_Wellbore Plane_Angle StructureDip FracLength FracHeight Area\n")
    dfnOutput.write("ft ft ft ft deg deg deg deg ft ft sqft\n")
    for i in range(zDataDFN.shape[0]):
        dfnOutput.write("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}\n".format(zDataDFN[i],
                                                                eastingDFN[i],
                                                                northingDFN[i],
                                                                tvdDFN[i],
    															azimuthDFN[i],
                                                                angle[i],
                                                                plane_angle[i],
                                                                90,
    															rpDFN[i]-rnDFN[i],
    															rpvDFN[i]-rnvDFN[i],
                                                                (rpDFN[i]-rnDFN[i])*(rpvDFN[i]-rnvDFN[i])))
    dfnOutput.close()

    return
