# ESP_hnb.py
# This script is for the H&B GROUP BOM in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book('ESP_config.xlsm')
    #wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import H&B GROUP data as an array (list of lists)
    rowHB = cF.findHeader(pmpDataSht, 'H&B GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'O-RING GROUP')
    colEnd = pmpDataSht[rowHB+1,0].end('right').column
    rngHB = pmpDataSht[rowHB+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngHB[0].index("Series")
    colStgType = rngHB[0].index("Stage Type")
    colShaftSize = rngHB[0].index("Shaft Size")
    colHBMaterial = rngHB[0].index("H&B Material")
    colConnectionType = rngHB[0].index("Connection Type")
    colBSMaterial = rngHB[0].index("Bearing Support Material")
    #colCoat = rngHB[0].index("Coating Type")           # NO COATING DONE ON H&B ANYMORE
    colTemp = rngHB[0].index("Temperature")
    colItemN = rngHB[0].index("Item Notes")
    colDesc = rngHB[0].index("Description")
    colItemID = rngHB[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpStageType = tmpSht[1,0].value
    pmpShaftSize = str(tmpSht[2,0].value)
    pmpHBMaterial = tmpSht[3,0].value
    pmpConnectionType = tmpSht[4,0].value
    pmpStagesMaterial = tmpSht[5,0].value
    pmpAppType = tmpSht[6,0].value
    tmpSht[0:7,0].value = ""

    # Stage type association for H&B group
    if pmpStageType in ["FLT", "AR-FLT"]:
        strHBStageType = "AR-FLT"
    elif pmpStageType in ["CMP", "AR-CMP"]:
        strHBStageType = "AR-CMP"
    else:
        strHBStageType = "AR-MDLR"

    # Temperature rating string
    if pmpAppType == "XHT":
        strTemp = "XHT"
    else:
        strTemp = ""

    # Shaft size converted to a string of the correct format for H&B group
    shaftSizeMatch = re.search("\.\d+", pmpShaftSize)
    strShaftSize = shaftSizeMatch.group(0)

    # Initialize the BOM elements
    strHBItemID = "NEW"
    strHBDescription = "GROUP,PMP " + pmpSeries + " " + strHBStageType + " " + \
                "H&B " + strShaftSize + "*"
    strHBItemNotes = pmpHBMaterial + " " + pmpConnectionType + " " + pmpStagesMaterial

    # Find a part number matching the H&B group (if any existing)
    for rowi in range(1,len(rngHB)):
        if pmpSeries == rngHB[rowi][colSeries] and \
            strHBStageType[3:] in rngHB[rowi][colStgType] and \
            strShaftSize in str(rngHB[rowi][colShaftSize]) and \
            pmpHBMaterial == rngHB[rowi][colHBMaterial] and \
            pmpConnectionType == rngHB[rowi][colConnectionType] and \
            pmpStagesMaterial == rngHB[rowi][colBSMaterial] and \
            strTemp == rngHB[rowi][colTemp]:
            strHBItemID = rngHB[rowi][colItemID]
            oldStgType = rngHB[rowi][colStgType]
            if oldStgType == "AR-CMP/FLT":
                newStgType = "AR-C/F"
            else:
                newStgType = oldStgType
            strHBDescription = "GROUP,PMP " + pmpSeries + " " + newStgType \
                                + " " + "H&B " + str(rngHB[rowi][colShaftSize]) + "*"
            break

    # Write to TempSheet
    tmpSht[0,0].value = strHBItemID
    tmpSht[0,1].value = strHBDescription
    tmpSht[0,2].value = strHBItemNotes
