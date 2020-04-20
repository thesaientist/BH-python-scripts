################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################

import os
import openpyxl
import openpyxl_lib as xlLib
import time
import numpy as np

path_to_source = 'C:/Users/212566876/Box Sync/Rotation 4/Ecopetrol Reserve Audit/Cashflow Fix/Annex 4 Jesus/CRFID/'


fileList = [file for file in os.listdir(path_to_source) if file.endswith('.xlsx') and os.path.isfile(os.path.join(path_to_source, file))]
fileList.sort()
numFields = len(fileList)
faulty_fields = []

# for loop to get all the data needed
for i, file in enumerate(fileList):
    startTime = time.time()                                             # start timer for loop duration (DEBUG)
    filePath = os.path.join(path_to_source, file)                  # get file path
    wb = openpyxl.load_workbook(filePath, data_only=True)       # load workbook (data-only mode, faster)
    ws_gross = wb['Gross']
    data = []
    for rowNum in range(79, 141):
        data_row = [ws_gross.cell(row=rowNum, column=colNum).value for colNum in range(xlLib.col2num('B'), xlLib.col2num('BJ'))]
        data.append(data_row)
    data = np.array(data)
    data = np.absolute(data)
    sum = np.sum(data)
    if sum!=0:
        faulty_fields.append(file)

# write fault fields list to text
with open('FID_field_list.txt', 'w') as f:
    for field in faulty_fields:
        f.write("{}\n".format(field))
