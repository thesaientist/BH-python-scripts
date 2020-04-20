################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
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
    import numpy as np
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
