################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# Define function to determine stacking of reflectivity signal traces at a given angle
# for the fracture selected at a certain MD in DFN Selection and return
# the metric for how good the traces stack (standard deviation: high - good stacking,
# low - poor stacking)
def reflectivityStack(angle, measDepth, mdStep, zData, stepSize, dataInterp, numMDSamples):
    # Define vertical shift array (numMDSamples samples on either side) for trace shift as empty list
    import numpy as np
    from math import pi
    vsArray = []
    for i in range(1, numMDSamples+1):
        hs = i*mdStep
        vs = np.absolute(np.tan(angle*pi/180) * hs)
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
                reflData[i+numMDSamples, :] = np.roll(dataInterp[depthRow + i, :], int(-1*vsArray[-i-1]))
            else:
                reflData[i+numMDSamples, :] = np.roll(dataInterp[depthRow + i, :], int(vsArray[-i-1]))
        elif i>0:
            if angle>=0:
                reflData[i+numMDSamples, :] = np.roll(dataInterp[depthRow + i, :], int(vsArray[i-1]))
            else:
                reflData[i+numMDSamples, :] = np.roll(dataInterp[depthRow + i, :], int(-1*vsArray[i-1]))
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
