# ESP_cplgOrg.py
# This script is for the COUPLING BOM in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import COUPLING data as an array (list of lists)
    rowCPLG = cF.findHeader(pmpDataSht, 'COUPLING')
    rowEnd = pmpDataSht[rowCPLG+1,0].end('down').row
    colEnd = pmpDataSht[rowCPLG+1,0].end('right').column
    rngCPLG = pmpDataSht[rowCPLG+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colSeries = rngCPLG[0].index("Series")
    colStgType = rngCPLG[0].index("Stage Type")
    colSize = rngCPLG[0].index("Size")
    colMat = rngCPLG[0].index("Material")
    colMS = rngCPLG[0].index("MS")
    colItemN = rngCPLG[0].index("Item Notes")
    colDesc = rngCPLG[0].index("Description")
    colItemID = rngCPLG[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpStageType = tmpSht[1,0].value
    pmpCplgMat = tmpSht[2,0].value
    pmpShaftSize = tmpSht[3,0].value
    tmpSht[0:4,0].value = ""

    # Useful transformations and associations
    # 1. Stage type association
    if pmpStageType in ["FLT","AR-FLT","AR-MDLR","Q-PLUS"]:
        strStageType = "FLT"
    else:
        strStageType = "CMP"
    # 2. Shaft size to fraction format
    if pmpShaftSize == 0.62:
        strShaftSize = "5/8"
    elif pmpShaftSize == 0.69:
        strShaftSize = "11/16"
    elif pmpShaftSize == 0.50:
        strShaftSize = "1/2"
    elif pmpShaftSize == 0.88:
        strShaftSize = "7/8"
    # 3. Series assocation
    if pmpSeries == "TA" and strStageType == "FLT" and strShaftSize == "5/8":
        strSeries = "TA"
    elif pmpSeries == "TA":
        strSeries = "TD"
    else:
        strSeries = pmpSeries

    # Initialize BOM elements
    strCouplingItemID = "NEW"
    strCouplingDescription = "COUPLING,PMP " + strSeries + " " + strStageType + \
                            " " + strShaftSize + " S/A " + pmpCplgMat
    strCouplingItemNotes = ""

    # Find a part number matching the COUPLING (if any existing)
    for rowi in range(1,len(rngCPLG)):
        if strSeries == rngCPLG[rowi][colSeries] and \
            strStageType == rngCPLG[rowi][colStgType] and \
            strShaftSize == rngCPLG[rowi][colSize] and \
            pmpCplgMat == rngCPLG[rowi][colMat]:
            strCouplingItemID = rngCPLG[rowi][colItemID]
            break

    # Write to TempSheet
    tmpSht[0,0].value = strCouplingItemID
    tmpSht[0,1].value = strCouplingDescription
    tmpSht[0,2].value = strCouplingItemNotes
