#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to create mistag and time errors templates                  #
#                                                                             #
#   Example usage:                                                            #
#      python createTemplates.py --debug --mode BsDsPi --modeDs All           #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 07 / 2013                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

#------------------------------------------------------------------------------
# settings for running without GaudiPython
#------------------------------------------------------------------------------
""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.

# make sure the environment is set up properly
if test -n "$CMTCONFIG" \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersDict.so \
     -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersLib.so; then
    # all ok, software environment set up correctly, so don't need to do
    # anything
    true
else
    if test -n "$CMTCONFIG"; then
    # clean up incomplete LHCb software environment so we can run
    # standalone
        echo Cleaning up incomplete LHCb software environment.
        PYTHONPATH=`echo $PYTHONPATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export PYTHONPATH
        LD_LIBRARY_PATH=`echo $LD_LIBRARY_PATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
	export LD_LIBRARY_PATH
        exec env -u CMTCONFIG -u B2DXFITTERSROOT "$0" "$@"
    fi
    # automatic set up in standalone build mode
    if test -z "$B2DXFITTERSROOT"; then
        cwd="$(pwd)"
        if test -z "$(dirname $0)"; then
        # have to guess location of setup.sh
        cd ../standalone
        . ./setup.sh
        cd "$cwd"
        else
        # know where to look for setup.sh
        cd "$(dirname $0)"/../standalone
        . ./setup.sh
        cd "$cwd"
        fi
    unset cwd
    fi
fi

# figure out which custom allocators are available
# prefer jemalloc over tcmalloc
for i in libjemalloc libtcmalloc; do
    for j in `echo "$LD_LIBRARY_PATH" | tr ':' ' '` \
        /usr/local/lib /usr/lib /lib; do
        for k in `find "$j" -name "$i"'*.so.?' | sort -r`; do
            if test \! -e "$k"; then
            continue
        fi
        echo adding $k to LD_PRELOAD
        if test -z "$LD_PRELOAD"; then
            export LD_PRELOAD="$k"
            break 3
        else
            export LD_PRELOAD="$LD_PRELOAD":"$k"
            break 3
        fi
    done
    done
done

# set batch scheduling (if schedtool is available)
schedtool="`which schedtool 2>/dev/zero`"
if test -n "$schedtool" -a -x "$schedtool"; then
    echo "enabling batch scheduling for this job (schedtool -B)"
    schedtool="$schedtool -B -e"
else
    schedtool=""
fi

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """
 
# -----------------------------------------------------------------------------
# Load necessary libraries
#------------------------------------------------------------------------------
from B2DXFitters import *
from ROOT import *
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
import os, sys, gc
gROOT.SetBatch()        
# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

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
    workspaceNW = []

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
            fileName = ["/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTGA.root",
                        "/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTGC.root",
                        "/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTG1.root",
                        "/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTG2.root",
                        "/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTG3.root"]
        else:
            fileName = ["/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTGA.root",
                        "/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTGC.root",
                        #"/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_3modeskkpi_both_BDTG1.root",
                        "/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTG1.root",
                        "/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTG2.root",
                        "/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_"+mode+"_all_both_BDTG3.root"]

        for i in range(0,5):
            workspace.append(SFitUtils.ReadDataFromSWeights(mode2,TString(fileName[i]), TString(nameTree),
                                                            TimeDown, TimeUp,
                                                            tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS,
                                                            True, debug)
                             )
            
            workspaceNW.append(SFitUtils.ReadDataFromSWeights(mode2,TString(fileName[i]), TString(nameTree),
                                                              TimeDown, TimeUp,
                                                              tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS,
                                                              False, debug)
                               )
        nameData = TString("dataSet_time_Bs2")+mode2
        modeDsTS = TString("All") 
        
    data = []
    dataNW = []                       
    data2 = []
    data3 = []
    data4 = []
    data5 = []
    obs = []
    obsNW = []
    mistag = []
    terr = []
    sWeight = []
    
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
            if MC == false:
                dataNW.append( GeneralUtils.GetDataSet(workspaceNW[i], nameData, debug))
                dataNW[i].Print("v")
                obsNW.append( dataNW[i].get())
                sWeight.append(obsNW[i].find("sWeights"))
                        
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

    legendERR = TLegend( 0.7, 0.6, 0.88, 0.88 )

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
        pdfM.append(GeneralUtils.CreateHistPDF(data[i], mistag[0], name, 100, debug))
    
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
        pdfTERR.append(GeneralUtils.CreateHistPDF(data[i], terr[0], name, 90, debug))
        
    canvPDFT = TCanvas("canvPDFT","canv")
    framePDFT = terr[0].frame()
    for i in range(0,5):
        pdfTERR[i].plotOn(framePDFT, RooFit.LineColor(color[i]))
    framePDFT.Draw()
    legendERR.Draw("same")
    name = TString("comparison_TERR_PDF") + typeTS + TString("_")+modeTS+ TString("_") + modeDsTS +TString(".pdf")
    canvPDFT.Print(name.Data())

    
    if MC == False:
        pdfsW = []
        for i in range(0,5):
            name = TString("TimeErrorPdf_signal_")+nameBDTG[i]
            pdfsW.append(GeneralUtils.CreateHistPDF(dataNW[i], sWeight[0], name, 60, debug))
        data123 = dataNW[2]
        data123.append(dataNW[3])
        data123.append(dataNW[4])
        pdfsW123 = GeneralUtils.CreateHistPDF(data123, sWeight[0], name, 60, debug)

        canvPDFsW = TCanvas("canvPDFsW","canv")
        framePDFsW = sWeight[0].frame()
        for i in range(0,5):
            pdfsW[i].plotOn(framePDFsW, RooFit.LineColor(color[i]))
        framePDFsW.Draw()
        legend.Draw("same")
        name = TString("comparison_sW_PDF") + typeTS + TString("_")+modeTS+ TString("_") + modeDsTS +TString(".pdf")
        canvPDFsW.Print(name.Data())

        legendsW = TLegend( 0.12, 0.6, 0.3, 0.88 )
        
        legendsW.SetTextSize(0.04)
        legendsW.SetTextFont(12)
        legendsW.SetFillColor(4000)
        legendsW.SetShadowColor(0)
        legendsW.SetBorderSize(0)
        legendsW.SetTextFont(132)
        legendsW.SetHeader("BDTG bins")

        grsW1 = TGraphErrors(10)
        grsW1.SetName("grsW1")
        grsW1.SetLineColor(kBlack);
        grsW1.SetLineWidth(2);
        grsW1.SetMarkerStyle(20);
        grsW1.SetMarkerSize(1.3);
        grsW1.SetMarkerColor(color[0]);
        grsW1.Draw("P");
        legendsW.AddEntry("grsW1","BDTGA","lep");

        grsW2 = TGraphErrors(10)
        grsW2.SetName("grsW2")
        grsW2.SetLineColor(kBlack);
        grsW2.SetLineWidth(2);
        grsW2.SetMarkerStyle(20);
        grsW2.SetMarkerSize(1.3);
        grsW2.SetMarkerColor(color[1]);
        grsW2.Draw("P");
        legendsW.AddEntry("grsW2","BDTG123","lep");
                
        canvPDFsW2 = TCanvas("canvPDFsW2","canv")
        framePDFsW2 = sWeight[0].frame()
        pdfsW[0].plotOn(framePDFsW2, RooFit.LineColor(color[0]))
        pdfsW123.plotOn(framePDFsW2, RooFit.LineColor(color[1]))
        framePDFsW2.Draw()
        legendsW.Draw("same")
        name = TString("comparison2_sW_PDF") + typeTS + TString("_")+modeTS+ TString("_") + modeDsTS +TString(".pdf")
        canvPDFsW2.Print(name.Data())
                                                                                        
                                        
            

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
                                
