################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# if well survey is available, parse it and get relevant attributes
def parseWellSurvey(wellSurveyFilePath):
	wellSurveyData = []
	wellFID = open(wellSurveyFilePath)
	# skip 3 lines to start from 4th line
	next(wellFID)
	next(wellFID)
	next(wellFID)
	for line in wellFID:
		listRow = line.split('\t')
		dataRow = []
        # Columns 2, 3, 4, 7 (0-based index) in well survey need to be
        # Easting, Northing, TVDSS, and Measure Depth
		for i in [2, 3, 4, 7]:
			dataRow.append(float(listRow[i]))
		wellSurveyData.append(dataRow)
	import numpy as np
	wellSurveyData = np.array(wellSurveyData)

    # close file
	wellFID.close()

	return wellSurveyData
