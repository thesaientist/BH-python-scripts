# ESP_shaftOrg.py
# This script organizes the SHAFT data in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

    # Import SHAFT data as an array (list of lists)
    rowShft = cF.findHeader(pmpDataSht, 'SHAFT')
    rowEnd = cF.findHeader(pmpDataSht, 'HOUSING')
    colEnd = pmpDataSht[rowShft+1,0].end('right').column
    rngShft = pmpDataSht[rowShft+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngShft[0].index("Series")
    colStgType = rngShft[0].index("Stage Type")
    colShaftSize = rngShft[0].index("Shaft Size")
    colShaftNum= rngShft[0].index("Shaft Number")
    colMat = rngShft[0].index("Material")
    colMS = rngShft[0].index("MS")
    colConn = rngShft[0].index("Connection Type")
    colItemN = rngShft[0].index("Item Notes")
    colDesc = rngShft[0].index("Description")

    # Define strings to match in description of the SHAFT group (and item notes)
    searchPattern = re.compile("(SHAFT,P.?MP) (?P<series>T.) (AR.)?(?P<remStgType>\w+) (?P<frac1>\d+)/(?P<frac2>\d+) \#(?P<shft_num>\d+)")
    shftMatList = ["INC","MNL","NIT","UHS"]
    shftMatDict = {'MS-1121-04':'NIT','MS-1131-01':'INC','MS-1131-02':'UHS','MS-1241-03':'MNL'}
    shaftSizeDict = {"5/8":0.62, "11/16":0.69, "1/2":0.5, "7/8":0.88}
    connList = ["BUT","UHP"]

    # Main loop that populates the array (list of lists) for SHAFT data
    for rowi in range(1,len(rngShft)):
        desc = rngShft[rowi][colDesc]
        itemN = rngShft[rowi][colItemN]
        shftExtDesc = desc + " " + itemN
        # Search using regular expressions
        descMatch = re.search(searchPattern, shftExtDesc)
        if descMatch:
            # Series
            rngShft[rowi][colSeries] = descMatch.group('series')
            # Type
            rngShft[rowi][colStgType] = "AR-" + descMatch.group('remStgType')
            # Shaft size
            shaftsizefrac = descMatch.group('frac1') + "/" + \
                                            descMatch.group('frac2')
            if shaftsizefrac in shaftSizeDict:
                rngShft[rowi][colShaftSize] = shaftSizeDict[shaftsizefrac]
            # Shaft number
            rngShft[rowi][colShaftNum] = descMatch.group('shft_num')
        # Material
        if rngShft[rowi][colMS] != "":
            matKey = rngShft[rowi][colMS][0:10]
            if matKey in shftMatDict:
                rngShft[rowi][colMat] = shftMatDict[matKey]
        else:
            rngShft[rowi][colMat] = ", ".join(shftMat for shftMat in shftMatList if shftMat in shftExtDesc)
        # Connection type (type of shaft)
        if any(conn in shftExtDesc for conn in connList):
            rngShft[rowi][colConn] = ", ".join(conn for conn in connList if conn in shftExtDesc)
        elif rngShft[rowi][colSeries] == "TA":
            rngShft[rowi][colConn] = "BUT"

    # Export modified SHAFT data back to worksheet
    pmpDataSht[rowShft+2,0].value = rngShft[1:]
