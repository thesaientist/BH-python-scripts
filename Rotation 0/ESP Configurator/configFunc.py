# configFunc.py
# This python module contains commonly used, user-defined functions for the
# ESP configurator

#----------------------------------FUNCTIONS-----------------------------------

# findHeader() searches for headerName in the given sht
def findHeader(sht, headerName):

    # Import all rows in first column (which contains header values e.g. 'COMMON')
    l_row = sht[0,0].end('down').row
    firstCol = sht[0:l_row,0].value

    # Find the STAGE GROUP header
    rowNum = 0
    while firstCol[rowNum] != headerName:
        rowNum += 1
        if rowNum == len(firstCol):
            raise ValueError(headerName + "header was not found!")
            break

    return rowNum
