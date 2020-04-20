################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# function to select fractures for DFN based on peaks in intensity curve (above given threshold)
# Based on threshold approach, intensity values below set threshold
# will not be considered for visualization
def selectFracs(intnThresh, intn, zData, rNeg, rPos, rNegVert, rPosVert, rStart, rStep):
    # Consider intensities and radial extents to only those above threshold
    isGood = intn > intnThresh
    zDataAbove = zData[isGood]
    nDepthsAbove = zDataAbove.shape[0]
    intnAbove = intn[isGood]
    rNegAbove = rNeg[isGood]
    rPosAbove = rPos[isGood]
    rNegVertAbove = rNegVert[isGood]
    rPosVertAbove = rPosVert[isGood]

    # Determine curvature change for finding local maxima, which
    # will serve as locations of fractures along MD
    max = 0
    iDepth = 0
    zDataDFN = []
    intnDFN = []
    rnDFN = []
    rpDFN = []
    rnvDFN = []
    rpvDFN = []
    while iDepth <= nDepthsAbove-1:
        skip = 0
        # Ascending
        while intnAbove[iDepth + skip] >= max:
            max = intnAbove[iDepth + skip]
            skip += 1
            if iDepth + skip >= nDepthsAbove:
                break
        # Local maximum found
        intnDFN.append(max)
        zDataDFN.append(zDataAbove[iDepth + skip - 1])
        rnDFN.append(rNegAbove[iDepth + skip - 1])
        rpDFN.append(rPosAbove[iDepth + skip - 1])
        rnvDFN.append(rNegVertAbove[iDepth + skip - 1])
        rpvDFN.append(rPosVertAbove[iDepth + skip - 1])
        iDepth += skip
        skip = 0
        # Descending
        if iDepth + 1 >= nDepthsAbove:
            break
        while intnAbove[iDepth + skip + 1] <= intnAbove[iDepth + skip]:
            skip += 1
            if iDepth + skip + 1 >= nDepthsAbove:
                break
        # Skip checking when last data point is reached
        if iDepth + skip + 1 >= nDepthsAbove:
            break
        # Local minimum found
        iDepth += skip
        max = 0 # reset max

    # Convert to numpy arrays for DFN data currently in list form
    import numpy as np
    intnDFN = np.array(intnDFN)
    zDataDFN = np.array(zDataDFN)
    #--DEBUG--
    # print('{} fracs in DFN'.format(zDataDFN.shape[0]))
    rnDFN = np.array(rnDFN)
    rpDFN = np.array(rpDFN)
    rnvDFN = np.array(rnvDFN)
    rpvDFN = np.array(rpvDFN)

    # Convert radial positions (indices) to distances
    for i in range(rpDFN.shape[0]):
        rpDFN[i] = rStart+rStep*(256+rpDFN[i])
        rnDFN[i] = rStart+rStep*(256-rnDFN[i])
        rpvDFN[i] = rStart+rStep*(256+rpvDFN[i])
        rnvDFN[i] = rStart+rStep*(256-rnvDFN[i])

    return intnDFN, zDataDFN, rnDFN, rpDFN, rnvDFN, rpvDFN
