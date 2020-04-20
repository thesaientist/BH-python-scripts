# ESP_hnbOrg.py
# This script organizes the H&B GROUP data in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

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
    #colCoat = rngHB[0].index("Coating Type")           NO COATING DONE ON H&B anymore
    colTemp = rngHB[0].index("Temperature")
    colItemN = rngHB[0].index("Item Notes")
    colDesc = rngHB[0].index("Description")

    # Define strings to match in description of the H&B group (and item notes)
    searchPattern1 = re.compile("(GROUP,P.*?MP) (?P<series>T.) (AR).(?P<stgtyp>[a-zA-Z/]+)")
    searchPattern2 = re.compile("\.\d+")
    HBMatList = ["4SS","STL","17-4","DPX"]
    BSM = ["N1","N2","N3","N4","DPX"]
    coatType = ["NDP","FPS","CRP","SF2"]

    # Main loop that populates the array (list of lists) for H&B group data
    for rowi in range(1,len(rngHB)):
        desc = rngHB[rowi][colDesc]
        itemN = rngHB[rowi][colItemN]
        hbExtDesc = desc + " " + itemN
        # Search using regular expressions
        descMatch = re.search(searchPattern1, hbExtDesc)
        if descMatch:
            # Series
            rngHB[rowi][colSeries] = descMatch.group('series')
            # Stage type
            sTyp = "AR-" + descMatch.group('stgtyp')
            if sTyp == "AR-C/F":
                sTyp = "AR-CMP/FLT"
            rngHB[rowi][colStgType] = sTyp
        # Shaft size
        rngHB[rowi][colShaftSize] = "/".join(re.findall(searchPattern2, hbExtDesc))
        # H&B material
        rngHB[rowi][colHBMaterial] = ", ".join(hbMat for hbMat in HBMatList if hbMat in hbExtDesc)
        # Connection type
        if "UHP" in hbExtDesc:
            connTyp = "UHP"
        elif "BUT" in hbExtDesc:
            connTyp = "BUT"
        else:
            connTyp = ""
        rngHB[rowi][colConnectionType] = connTyp
        # Bearing support material
        rngHB[rowi][colBSMaterial] = ", ".join(bsType for bsType in BSM if bsType in hbExtDesc)
        # Temperature rating
        if "XHT" in  hbExtDesc:
            rngHB[rowi][colTemp] = "XHT"

    # Export modified H&B GROUP data back to worksheet
    pmpDataSht[rowHB+2,0].value = rngHB[1:]
