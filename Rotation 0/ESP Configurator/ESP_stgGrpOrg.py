# ESP_stgGrpOrg.py
# This script organizes the STAGE GROUP data in the PumpData sheet of the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

    # Import STAGE GROUP data as an array (list of lists)
    rowSTG = cF.findHeader(pmpDataSht, 'STAGE GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'H&B GROUP')
    colEnd = pmpDataSht[rowSTG+1,0].end('right').column
    rngSTG = pmpDataSht[rowSTG+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngSTG[0].index("Series")
    colBPD = rngSTG[0].index("BPD")
    colStgType = rngSTG[0].index("Stage Type")
    colTemp = rngSTG[0].index("Temperature")
    colUPR = rngSTG[0].index("UPR")
    colOring = rngSTG[0].index("O-Ring Material")
    colMat = rngSTG[0].index("Material")
    colCoat = rngSTG[0].index("Coating Type")
    colItemN = rngSTG[0].index("Item Notes")
    colDesc = rngSTG[0].index("Description")

    # Define strings to match in description of the stage group (and item notes)
    seriesPattern = re.compile("(T.) *?(\d+)")
    StageTypes = [re.compile("AR.CMP"),re.compile("AR.FLT"),re.compile("AR.MDLR"),\
                re.compile("AR.C/F"),"CMP","FLT","C/F","C/MDLR","MDLR","MODULAR","Q PLUS"]
    noOringList = ["TA400","TA550","TA900","TA1200","TA1500"]
    OringMatList = ["AFL","HSN","VIT","CHEM","FFKM","EPDM"]
    MatList = ["N1","N2","N3","N4","DPX","SDX","3SS","CI"]
    coatType = ["NDP","FPS","CRP","SF2","DGS","BDP","GET"]
    tempInd = ["HTP","XHT"]

    # Main loop that populates the array (list of lists) for stage group data
    for rowi in range(1,len(rngSTG)):
        desc = rngSTG[rowi][colDesc]
        itemN = rngSTG[rowi][colItemN]
        stgExtDesc = desc + " " + itemN
        # Series and BPD
        seriesMatch = re.search(seriesPattern, stgExtDesc)
        if seriesMatch:
            rngSTG[rowi][colSeries] = seriesMatch.group(1)
            rngSTG[rowi][colBPD] = seriesMatch.group(2)
        # Stage type
        sTypMatch = [re.search(s, stgExtDesc) for s in StageTypes]
        if any(sTypMatch):
            firstMatchIndex = [i for i,v in enumerate(sTypMatch) if v][0]
            sTyp = sTypMatch[firstMatchIndex].group(0)
            # If AR type stages are found, make sure that there is a hyphen after the AR
            if sTyp[0:2] == "AR":
                listSType = list(sTyp)
                listSType[0:3] = ['A','R','-']
                sTyp = "".join(listSType)
            elif sTyp[0] == "Q":
                listSType = list(sTyp)
                listSType[0:3] = ['Q','-','P']
                sTyp = "".join(listSType)
            # If combo stage type found, then spell out the types
            if sTyp == "AR-C/F":
                sTyp = "AR-CMP/FLT"
            elif sTyp == "C/F":
                sTyp = "CMP/FLT"
            elif sTyp == "C/MDLR":
                sTyp = "CMP/MDLR"
            elif sTyp == "MODULAR":
                sTyp = "MDLR"
            rngSTG[rowi][colStgType] = sTyp
            # Determine if a Q PLUS stage is UPR
            if sTyp == "Q-PLUS":
                if "UPR" in stgExtDesc:
                    rngSTG[rowi][colUPR] = "UPR"
        # Oring material
        seriesBPD = rngSTG[rowi][colSeries] + rngSTG[rowi][colBPD]
        if seriesBPD in noOringList:
            rngSTG[rowi][colOring] = ""
        elif any(oMat in stgExtDesc for oMat in OringMatList):
            rngSTG[rowi][colOring] = ", ".join(oMat for oMat in OringMatList if oMat in stgExtDesc)
        elif seriesMatch.group(1) == "TA":
            rngSTG[rowi][colOring] = "HSN"  # seems to be the default if TA Stage O-Ring Material not specified
        elif seriesMatch.group(1) == "TD":
            rngSTG[rowi][colOring] = "EPDM" # all TDs by default have EPDM material quad rings in the stages
        # Stage Material
        if any(sMat in stgExtDesc for sMat in MatList):
            rngSTG[rowi][colMat] = ", ".join(sMat for sMat in MatList if sMat in stgExtDesc)
        else:
            rngSTG[rowi][colMat] = "N1"
        # Coating type
        rngSTG[rowi][colCoat] = ", ".join(cTyp for cTyp in coatType if cTyp in stgExtDesc)
        # Temperature
        if any(tInd in stgExtDesc for tInd in tempInd):
            rngSTG[rowi][colTemp] = "XHT"

    # Export modified STAGE GROUP data back to worksheet
    pmpDataSht[rowSTG+2,0].value = rngSTG[1:]
