# ESP_shaft.py
# This script is for the SHAFT BOM in the ESP configurator
import xlwings as xw
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import Shaft data as an array (list of lists)
    rowShft = cF.findHeader(pmpDataSht, 'SHAFT')
    rowEnd = cF.findHeader(pmpDataSht, 'HOUSING')
    colEnd = pmpDataSht[rowShft+1,0].end('right').column
    rngShft = pmpDataSht[rowShft+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colSeries = rngShft[0].index("Series")
    colStgType = rngShft[0].index("Stage Type")
    colShaftSize = rngShft[0].index("Shaft Size")
    colShaftNum= rngShft[0].index("Shaft Number")
    colMat = rngShft[0].index("Material")
    colConn = rngShft[0].index("Connection Type")
    colItemN = rngShft[0].index("Item Notes")
    colDesc = rngShft[0].index("Description")
    colItemID = rngShft[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpStageType = tmpSht[1,0].value
    pmpShaftSize = tmpSht[2,0].value
    pmpShaftNum = tmpSht[3,0].options(numbers=int).value
    pmpShaftMat = tmpSht[4,0].value
    pmpConn = tmpSht[5,0].value
    tmpSht[0:6,0].value = ""

    # Useful transformations and associations
    # 1. Stage type association
    if pmpStageType in ["FLT","AR-FLT","AR-MDLR","Q-PLUS"]:
        strStageType = "AR-FLT"
    else:
        strStageType = "AR-CMP"
    # 2. Shaft size to fraction format
    if pmpShaftSize == 0.62:
        strShaftSize = "5/8"
    elif pmpShaftSize == 0.69:
        strShaftSize = "11/16"
    elif pmpShaftSize == 0.50:
        strShaftSize = "1/2"
    elif pmpShaftSize == 0.88:
        strShaftSize = "7/8"
    # 3. Shaft number to correct format
    if pmpShaftNum < 10:
        strShaftNum = "0" + str(pmpShaftNum)
    else:
        strShaftNum = str(pmpShaftNum)

    # Initialize BOM elements
    strShaftItemID = "NEW"
    strShaftDescription = "SHAFT,PMP " + pmpSeries + " " + strStageType + " " + \
                            strShaftSize + " #" + strShaftNum + " " + pmpShaftMat + "*"
    strShaftItemNotes = pmpConn

    # Find a part number matching the SHAFT (if any existing)
    for rowi in range(1,len(rngShft)):
        if pmpSeries == rngShft[rowi][colSeries] and \
            strStageType == rngShft[rowi][colStgType] and \
            pmpShaftSize == rngShft[rowi][colShaftSize] and \
            pmpShaftNum == rngShft[rowi][colShaftNum] and \
            pmpShaftMat == rngShft[rowi][colMat] and \
            pmpConn == rngShft[rowi][colConn]:
            strShaftItemID = rngShft[rowi][colItemID]
            break

    # Write to TempSheet
    tmpSht[0,0].value = strShaftItemID
    tmpSht[0,1].value = strShaftDescription
    tmpSht[0,2].value = strShaftItemNotes
