################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# Define a function that compares the output (standard deviation) from reflectivityStack function
# for various angles and picks the best angle
def bestAzimuth(measDepth, mdStep, zData, stepSize, dataInterp, numMDSamples):
    import numpy as np
    from reflectivityStack import reflectivityStack
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
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(stdAngles, trialAngles, 'b.')
    plt.xlabel('standard deviation')
    plt.ylabel('angle')
    plt.title('angle vs. stdev')
    plt.show()

    # Pick the angle that corresponds to the largest standard deviation
    indLowestStd = np.argmax(stdAngles)
    bestAngle = trialAngles[indLowestStd]

    return bestAngle
