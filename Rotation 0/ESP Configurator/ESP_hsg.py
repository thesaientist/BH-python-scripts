# ESP_hsgOrg.py
# This script is for the HOUSING BOM in the ESP configurator
import xlwings as xw
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import HOUSING data as an array (list of lists)
    rowHSG = cF.findHeader(pmpDataSht, 'HOUSING')
    rowEnd = cF.findHeader(pmpDataSht, 'LOWER DIFFUSER')
    colEnd = pmpDataSht[rowHSG+1,0].end('right').column
    rngHSG = pmpDataSht[rowHSG+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colSeries = rngHSG[0].index("Series")
    colType = rngHSG[0].index("Type Association")
    colHsgNum= rngHSG[0].index("Housing Number")
    colMat = rngHSG[0].index("Material")
    colMS = rngHSG[0].index("MS")
    colConn = rngHSG[0].index("Connection Type")
    colItemN = rngHSG[0].index("Item Notes")
    colDesc = rngHSG[0].index("Description")
    colItemID = rngHSG[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpStageType = tmpSht[1,0].value
    pmpHousingNum = tmpSht[2,0].options(numbers=int).value
    pmpHousingMat = tmpSht[3,0].value
    pmpConn = tmpSht[4,0].value
    tmpSht[0:5,0].value = ""

    # Useful transformations and associations
    # 1. Type association
    if pmpStageType in ["FLT","AR-FLT","AR-MDLR"]:
        strType = "FLT"
    else:
        strType = "CMP"
    # 2. Housing number to correct format
    if pmpHousingNum < 10:
        strHousingNum = "0" + str(pmpHousingNum)
    else:
        strHousingNum = str(pmpHousingNum)

    # Initialize BOM elements
    strHousingItemID = "NEW"
    strHousingDescription = "HOUSING,PMP " + pmpSeries + " " + strType + " #" + \
                            strHousingNum + " " + pmpHousingMat + "*"
    strHousingItemNotes = pmpConn

    # Find a part number matching the HOUSING (if any existing)
    for rowi in range(1,len(rngHSG)):
        if pmpSeries == rngHSG[rowi][colSeries] and \
            strType == rngHSG[rowi][colType] and \
            pmpHousingNum == rngHSG[rowi][colHsgNum] and \
            pmpHousingMat == rngHSG[rowi][colMat] and \
            pmpConn == rngHSG[rowi][colConn]:
            strHousingItemID = rngHSG[rowi][colItemID]
            break

    # Write to TempSheet
    tmpSht[0,0].value = strHousingItemID
    tmpSht[0,1].value = strHousingDescription
    tmpSht[0,2].value = strHousingItemNotes
