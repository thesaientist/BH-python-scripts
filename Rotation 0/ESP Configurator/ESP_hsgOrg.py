# ESP_hsgOrg.py
# This script organizes the HOUSING data in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

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

    # Define strings to match in description of the HOUSING group (and item notes)
    searchPattern = re.compile("(HOUSING,P.?MP) (?P<series>T.) (?P<typ>\w+)? ?\#(?P<hsg_num>\d+)")
    hsgMatList = ["T-9","13cr","STL","DPX"]
    hsgMatDict = {'MS-1111-03':'STL','MS-1122-02':'T9'}
    connList = ["BUT","UHP"]

    # Main loop that populates the array (list of lists) for HOUSING data
    for rowi in range(1,len(rngHSG)):
        desc = rngHSG[rowi][colDesc]
        itemN = rngHSG[rowi][colItemN]
        if itemN is None:
            itemN = ""
        hsgExtDesc = desc + " " + itemN
        # Search using regular expressions
        descMatch = re.search(searchPattern, hsgExtDesc)
        if descMatch:
            # Series
            rngHSG[rowi][colSeries] = descMatch.group('series')
            # Type association
            if descMatch.group('typ') is not None:
                rngHSG[rowi][colType] = descMatch.group('typ')
            else:
                rngHSG[rowi][colType] = "FLT"
            # Housing number
            rngHSG[rowi][colHsgNum] = descMatch.group('hsg_num')
        # Material
        if rngHSG[rowi][colMS] != "":
            matKey = rngHSG[rowi][colMS][0:10]
            rngHSG[rowi][colMat] = hsgMatDict[matKey]
        else:
            rngHSG[rowi][colMat] = ", ".join(hsgMat for hsgMat in hsgMatList if hsgMat in hsgExtDesc)
        # Connection type (type of housing)
        if any(conn in hsgExtDesc for conn in connList):
            rngHSG[rowi][colConn] = ", ".join(conn for conn in connList if conn in hsgExtDesc)

    # Export modified HOUSING data back to worksheet
    pmpDataSht[rowHSG+2,0].value = rngHSG[1:]
