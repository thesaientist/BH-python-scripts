# ESP_oringOrg.py
# This script organizes the O-RING GROUP data in the ESP configurator
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
    rowOR = cF.findHeader(pmpDataSht, 'O-RING GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'SPACER GROUP')
    colEnd = pmpDataSht[rowOR+1,0].end('right').column
    rngOR = pmpDataSht[rowOR+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngOR[0].index("Series")
    colMat = rngOR[0].index("Material")
    colDuro = rngOR[0].index("Durometer")
    colTyp = rngOR[0].index("Type Designation")
    colApp = rngOR[0].index("Application")
    colItemN = rngOR[0].index("Item Notes")
    colDesc = rngOR[0].index("Description")

    # Define strings to match in description & item notes of Oring group
    searchPattern = re.compile("(GROUP,P.*?MP) (T.)")
    matList = ["AFL","HSN","VIT","CHEM","FFKM"]
    duroList = ["75","80","90"]
    typeList = ["CMP","FLT"]
    appList = ["UHP","XHT"]

    # Main loop that populates the array (list of lists) for oring group data
    for rowi in range(1,len(rngOR)):
        desc = rngOR[rowi][colDesc]
        itemN = rngOR[rowi][colItemN]
        orExtDesc = desc + " " + itemN
        # Search using regular expressions
        descMatch = re.search(searchPattern, orExtDesc)
        if descMatch:
            # Series
            rngOR[rowi][colSeries] = descMatch.group(2)
        # Material
        rngOR[rowi][colMat] = ", ".join(orMat for orMat in matList if orMat in orExtDesc)
        # Durometer
        rngOR[rowi][colDuro] = ", ".join(dur for dur in duroList if dur in orExtDesc)
        # Type designation
        rngOR[rowi][colTyp] = ", ".join(typ for typ in typeList if typ in orExtDesc)
        # Application
        rngOR[rowi][colApp] = ", ".join(app for app in appList if app in orExtDesc)

    # Export modified O-RING GROUP data back to worksheet
    pmpDataSht[rowOR+2,0].value = rngOR[1:]
