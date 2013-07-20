#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to generate toys for DsPi                                   #
#                                                                             #
#   Example usage:                                                            #
#      python comparePDF.py                                                   #
#                                                                             #
#   Author: Vava Gligorov                                                     #
#   Date  : 14 / 06 / 2012                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 06 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

from optparse import OptionParser
from os.path  import join

import GaudiPython

GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import *

GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels
SFitUtils = GaudiPython.gbl.SFitUtils

TimeDown = 0.0
TimeUp = 15.0
Time_down = 0.0
Time_up = 15.0
Pcut_down = 0.0
Pcut_up = 650000000.0
PT_down  = 500.0
PT_up = 45000.0
nTr_down = 1.0
nTr_up = 1000.0
Dmass_down = 1930
Dmass_up = 2015
Bmass_down = 5320 #5000
Bmass_up = 5420 #5600


dataName      = '../data/config_fitSignal.txt'

#------------------------------------------------------------------------------
def runCreateTemplate( debug, file, nameTree, mode, modeDs, MC) :
    
    #myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    #myconfigfile = myconfigfilegrabber()
    
    #print "=========================================================="
    #print "PREPARING WORKSPACE IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    #for option in myconfigfile :
    #    if option == "constParams" :
    #        for param in myconfigfile[option] :
    #            print param, "is constant in the fit"
    #    else :
    #        print option, " = ", myconfigfile[option]
    #print "=========================================================="
    
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
                                                                    
    mVarTS         = TString("lab0_MassFitConsD_M")
    mdVarTS        = TString("lab2_MM")
    mProbVarTS     = TString("lab1_PIDK")
    tVarTS         = TString("lab0_LifetimeFit_ctau")
    terrVarTS      = TString("lab0_LifetimeFit_ctauErr")
    tagVarTS       = TString("lab0_BsTaggingTool_TAGDECISION_OS")
    tagWeightVarTS = TString("lab0_BsTaggingTool_TAGOMEGA_OS")
    idVarTS        = TString("lab1_ID")
    modeTS         = TString(mode)
    modeDsTS         = TString(modeDs) 

    workspace = []

    nameBDTG = [TString("BDTGA"),TString("BDTGC"),TString("BDTG1"),TString("BDTG2"),TString("BDTG3")]
    BDTG_down = [ 0.3, 0.5, 0.3, 0.7, 0.9]
    BDTG_up   = [ 1.0, 1.0, 0.7, 0.9, 1.0]

    if modeTS.Contains("DsPi") == true:
        mode2 = TString("DsPi")
        PIDcut = 0
    elif modeTS.Contains("DsK") == true :
        mode2 = TString("DsK")
        PIDcut = 5

    if MC:
        typeTS = TString("MC")
    else:
        typeTS = TString("DATA")  
        
    if MC == true:
        dataTS = TString(dataName)
        if modeDsTS == "All":
            modeDsTS3 = [TString("PhiPi"), TString("KstK"), TString("NonRes"), TString("KPiPi"), TString("PiPiPi")]
            modeDsTS2 = [TString("phipi"), TString("kstk"), TString("nonres"), TString("kpipi"), TString("pipipi")]
            nameData = []
            for j in range(0,5):
                nameTS = TString("#Signal ")+modeTS+TString(" ")+modeDsTS3[j]
                nameData.append(TString("dataSetMC_")+modeTS+TString("_both_")+modeDsTS2[j])
                for i in range(0,5):
                    workspace.append( MassFitUtils.ObtainSignal(dataTS, nameTS,
                                                                PIDcut,
                                                                Pcut_down, Pcut_up,
                                                                BDTG_down[i], BDTG_up[i],
                                                                Dmass_down, Dmass_up,
                                                                Bmass_down, Bmass_up,
                                                                Time_down, Time_up,
                                                                PT_down, PT_up,
                                                                nTr_down, nTr_up,
                                                                mVarTS, mdVarTS,
                                                                tVarTS, terrVarTS,
                                                                tagVarTS, tagWeightVarTS, idVarTS, mProbVarTS,
                                                                modeTS, false, false, NULL, debug)
                                      )
            
        else:
            nameTS = TString("#Signal ")+modeTS+TString(" ")+modeDsTS
                        
            for i in range(0,5):
                workspace.append( MassFitUtils.ObtainSignal(dataTS, nameTS,
                                                            PIDcut,
                                                            Pcut_down, Pcut_up,
                                                            BDTG_down[i], BDTG_up[i],
                                                            Dmass_down, Dmass_up,
                                                            Bmass_down, Bmass_up,
                                                            Time_down, Time_up,
                                                            PT_down, PT_up,
                                                            nTr_down, nTr_up,
                                                            mVarTS, mdVarTS,
                                                            tVarTS, terrVarTS,
                                                            tagVarTS, tagWeightVarTS, idVarTS, mProbVarTS,
                                                            modeTS, false, false, NULL, debug)
                                  )
                modeDsTS2 = GeneralUtils.CheckDMode(modeDsTS, debug)
                if modeDsTS2 == "":
                    modeDsTS2 = GeneralUtils.CheckKKPiMode(modeDsTS, debug)
                    
                nameData = TString("dataSetMC_")+modeTS+TString("_both_")+modeDsTS2
        
    else:
        if modeTS.Contains("DsK") == false:
            fileName = ["sWeights_"+mode+"_all_both_BDTGA.root",
                        "sWeights_"+mode+"_all_both_BDTGC.root",
                        "sWeights_"+mode+"_all_both_BDTG1.root",
                        "sWeights_"+mode+"_all_both_BDTG2.root",
                        "sWeights_"+mode+"_all_both_BDTG3.root"]
        else:
            fileName = ["sWeights_"+mode+"_all_both_BDTGA.root",
                        "sWeights_"+mode+"_all_both_BDTGC.root",
                        "sWeights_"+mode+"_3modeskkpi_both_BDTG1.root",
                        "sWeights_"+mode+"_all_both_BDTG2.root",
                        "sWeights_"+mode+"_all_both_BDTG3.root"]
            
        workspace.append(SFitUtils.ReadDataFromSWeights(mode2,TString(fileName[i]), TString(nameTree),
                                                        TimeDown, TimeUp,
                                                        tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS,
                                                        debug)
                         )

        nameData = TString("dataSet_time_Bs2")+mode2
        modeDsTS = TString("All") 
        
    data = []
    data2 = []
    data3 = []
    data4 = []
    data5 = []
    obs = []
    mistag = []
    terr = []
    
    for i in range(0,5):
        if MC == true and modeDsTS == "All":
            data.append( GeneralUtils.GetDataSet(workspace[i], nameData[0], debug))
            data2.append( GeneralUtils.GetDataSet(workspace[i+5], nameData[1], debug))
            data3.append( GeneralUtils.GetDataSet(workspace[i+10], nameData[2], debug))
            data4.append( GeneralUtils.GetDataSet(workspace[i+15], nameData[3], debug))
            data5.append( GeneralUtils.GetDataSet(workspace[i+20], nameData[4], debug))
            data[i].append(data2[i])
            data[i].append(data3[i])
            data[i].append(data4[i])
            data[i].append(data5[i])
            data[i].Print("v")
            nameDataSave = TString("dataSetMC_all_both_") + nameBDTG[i]
            data[i].SetName(nameDataSave.Data())
            obs.append( data[i].get())
            mistag.append( obs[i].find(tagWeightVarTS.Data()))
            terr.append( obs[i].find(terrVarTS.Data()))
            
        else:    
            data.append( GeneralUtils.GetDataSet(workspace[i], nameData, debug))
            data[i].Print("v")
            nameDataSave = nameData + TString("_") + nameBDTG[i]
            data[i].SetName(nameDataSave.Data())
            obs.append( data[i].get())
            mistag.append( obs[i].find(tagWeightVarTS.Data()))
            terr.append( obs[i].find(terrVarTS.Data()))
       

    color = [kBlue+3, kRed, kOrange, kGreen+3, kMagenta+2]
    scale = []

    legend = TLegend( 0.12, 0.6, 0.3, 0.88 )

    legend.SetTextSize(0.04)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("BDTG bins")

    legendERR = TLegend( 0.65, 0.6, 0.90, 0.88 )

    legendERR.SetTextSize(0.04)
    legendERR.SetTextFont(12)
    legendERR.SetFillColor(4000)
    legendERR.SetShadowColor(0)
    legendERR.SetBorderSize(0)
    legendERR.SetTextFont(132)
    legendERR.SetHeader("BDTG bins")
                                

    gr = []
    grName = [TString("grA"), TString("grB"), TString("gr1"), TString("gr2"), TString("gr3") ]
    for i in range(0,5):
        gr.append(TGraphErrors(10))
        gr[i].SetName(grName[i].Data())
        gr[i].SetLineColor(kBlack);
        gr[i].SetLineWidth(2);
        gr[i].SetMarkerStyle(20);
        gr[i].SetMarkerSize(1.3);
        gr[i].SetMarkerColor(color[i]);
        gr[i].Draw("P");
        legend.AddEntry(grName[i].Data(),nameBDTG[i].Data(),"lep");
        legendERR.AddEntry(grName[i].Data(),nameBDTG[i].Data(),"lep");
                  
    canv = TCanvas("canv","canv")
    frame = mistag[0].frame()
    for i in range(0,5):
        scale.append(data[0].sumEntries()/data[i].sumEntries())
        data[i].plotOn(frame,RooFit.MarkerColor(color[i]),RooFit.Rescale(scale[i]), RooFit.Binning(50))
    frame.Draw()
    legend.Draw("same")
    name = TString("comparison_MISTAG_") + typeTS + TString("_")+modeTS+TString("_") + modeDsTS +TString(".pdf")
    canv.Print(name.Data())

    canvERR = TCanvas("canvERR","canvERR")
    frameERR = terr[0].frame()
    for i in range(0,5):
        data[i].plotOn(frameERR,RooFit.MarkerColor(color[i]),RooFit.Rescale(scale[i]), RooFit.Binning(50))
    frameERR.Draw()
    legendERR.Draw("same")
    name = TString("comparison_TERR_") + typeTS + TString("_")+modeTS+TString("_") + modeDsTS + TString(".pdf")
    canvERR.Print(name.Data())
    

    pdfM = []
    for i in range(0,5):
        name = TString("MistagPdf_signal_")+nameBDTG[i]
        pdfM.append(GeneralUtils.CreateHistPDF(data[i], mistag[0], name, 50, debug))
    
    canvPDFM = TCanvas("canvPDFM","canv")
    framePDFM = mistag[0].frame()
    for i in range(0,5):
        pdfM[i].plotOn(framePDFM, RooFit.LineColor(color[i])) 
    framePDFM.Draw()
    legend.Draw("same")
    name = TString("comparison_MISTAG_PDF") + typeTS + TString("_")+modeTS+TString("_") + modeDsTS +TString(".pdf")
    canvPDFM.Print(name.Data())

    pdfTERR = []
    
    for i in range(0,5):
        name = TString("TimeErrorPdf_signal_")+nameBDTG[i]
        #pdfTERR.append(GeneralUtils.CreateBinnedPDF(data[i], terr[0], name, 20, debug))
        pdfTERR.append(GeneralUtils.CreateHistPDF(data[i], terr[0], name, 50, debug))
        
    canvPDFT = TCanvas("canvPDFT","canv")
    framePDFT = terr[0].frame()
    for i in range(0,5):
        pdfTERR[i].plotOn(framePDFT, RooFit.LineColor(color[i]))
    framePDFT.Draw()
    legendERR.Draw("same")
    name = TString("comparison_TERR_PDF") + typeTS + TString("_")+modeTS+ TString("_") + modeDsTS +TString(".pdf")
    canvPDFT.Print(name.Data())

    workout = RooWorkspace("workspace","workspace")
    for i in range(0,5):
        getattr(workout,'import')(data[i])
        getattr(workout,'import')(pdfM[i])
        getattr(workout,'import')(pdfTERR[i])

    saveNameTS = TString("templates_")+typeTS+ TString("_") + modeTS +TString("_") + modeDsTS +TString(".root")
    workout.Print()
    GeneralUtils.SaveWorkspace(workout,saveNameTS, debug)
            

#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--nametree',
                   dest = 'nametree',
                   default = 'merged')

parser.add_option( '--fileA',
                   dest = 'file',
                   default = 'sWeights_BsDsPi_all_both_BDTGA.root')
parser.add_option( '--mode',
                   dest = 'mode',
                   default = 'BsDsPi')

parser.add_option( '--modeDs',
                   dest = 'modeDs',
                   default = 'PhiPi')

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsPiConfigForNominalMassFit')

parser.add_option( '--MC',
                   dest = 'MC',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    runCreateTemplate( options.debug,
                       options.file , options.nametree,
                       options.mode, options.modeDs,
                       options.MC
                       )                                
# -----------------------------------------------------------------------------
                                
