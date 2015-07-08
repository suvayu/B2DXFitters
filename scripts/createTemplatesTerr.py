# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to compare datas or pdfs                                    #
#                                                                             #
#   Example usage:                                                            #
#      python comparePDF.py                                                   #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 06 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
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
        # try to find from where script is executed, use current directory as
        # fallback
        tmp="$(dirname $0)"
        tmp=${tmp:-"$cwd"}
        # convert to absolute path
        tmp=`readlink -f "$tmp"`
        # move up until standalone/setup.sh found, or root reached
        while test \( \! -d "$tmp"/standalone \) -a -n "$tmp" -a "$tmp"\!="/"; do
            tmp=`dirname "$tmp"`
        done
        if test -d "$tmp"/standalone; then
            cd "$tmp"/standalone
            . ./setup.sh
        else
            echo `basename $0`: Unable to locate standalone/setup.sh
            exit 1
        fi
            cd "$cwd"
        unset tmp
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
# -----------------------------------------------------------------------------
from B2DXFitters import *
from ROOT import *

from optparse import OptionParser
from math     import pi, log
import os, sys, gc

gROOT.SetBatch()

#------------------------------------------------------------------------------
def runComparePDF( debug, pathName, treeName, obs, mode, configName, sufix, bin ) :

    # Get the configuration file                                                                                                                                                             
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="

    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    plotSettings = PlotSettings("plotSettings","plotSettings", "PlotSignal", "pdf", 100, true, false, true)
    plotSettings.Print("v")

    config = TString("../data/")+TString(configName)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettings.SetMassBVar(TString("lab0_MassFitConsD_M"))
    MDSettings.SetMassDVar(TString("lab2_MM"))
    MDSettings.SetTimeVar(TString("lab0_LifetimeFit_ctau"))
    MDSettings.SetTerrVar(TString(obs))
    MDSettings.SetIDVar(TString("lab1_ID"))
    MDSettings.SetPIDKVar(TString("lab1_PIDK"))
    MDSettings.SetBDTGVar(TString("BDTGResponse_1"))
    MDSettings.SetMomVar(TString("lab1_P"))
    MDSettings.SetTrMomVar(TString("lab1_PT"))
    MDSettings.SetTracksVar(TString("nTracks"))
    MDSettings.Print("v") 

    config = TString("../data/")+TString(configName)+TString(".py")
    MDSettingsSig = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettingsSig.SetMassBVar(TString("lab0_MassFitConsD_M"))
    MDSettingsSig.SetMassDVar(TString("lab2_MM"))
    MDSettingsSig.SetTimeVar(TString("lab0_LifetimeFit_ctau"))
    MDSettingsSig.SetTerrVar(TString(obs))
    MDSettingsSig.SetIDVar(TString("lab1_ID"))
    MDSettingsSig.SetPIDKVar(TString("lab1_PIDK"))
    MDSettingsSig.SetBDTGVar(TString("BDTGResponse_1"))
    MDSettingsSig.SetMomVar(TString("lab1_P"))
    MDSettingsSig.SetTrMomVar(TString("lab1_PT"))
    MDSettingsSig.SetTracksVar(TString("nTracks"))
    MDSettingsSig.SetMassBRange(5000, 5600)
    MDSettingsSig.Print("v")

    config = TString("../data/")+TString(configName)+TString(".py")
    MDSettingsCombo = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettingsCombo.SetMassBVar(TString("lab0_MassFitConsD_M"))
    MDSettingsCombo.SetMassDVar(TString("lab2_MM"))
    MDSettingsCombo.SetTimeVar(TString("lab0_LifetimeFit_ctau"))
    MDSettingsCombo.SetTerrVar(TString(obs))
    MDSettingsCombo.SetIDVar(TString("lab1_ID"))
    MDSettingsCombo.SetPIDKVar(TString("lab1_PIDK"))
    MDSettingsCombo.SetBDTGVar(TString("BDTGResponse_1"))
    MDSettingsCombo.SetMomVar(TString("lab1_P"))
    MDSettingsCombo.SetTrMomVar(TString("lab1_PT"))
    MDSettingsCombo.SetTracksVar(TString("nTracks"))
    MDSettingsCombo.SetMassBRange(5700, 7000)
    MDSettingsCombo.Print("v")

    dataTS  = TString(myconfigfile["dataName"])
    modeTS = TString(mode) 
    if sufix != "":
        sufix = "_"+sufix

    if modeTS == "Bs2DsPi":
        modeTS2 = "BsDsPi"
    else:
        modeTS2 = "BsDsK"

    workspace =[]
    
    #obtain combo samples
    workCombo = RooWorkspace("workCombo","workCombo") 
    dataNames = [ TString("#") + modeTS + TString(" NonRes"),
                  TString("#") + modeTS + TString(" PhiPi"),
                  TString("#") + modeTS + TString(" KstK"),
                  TString("#") + modeTS + TString(" KPiPi"),
                  TString("#") + modeTS + TString(" PiPiPi")]

    for i in range(0,5):
        workCombo = MassFitUtils.ObtainData(dataTS, dataNames[i],  MDSettingsCombo, TString(mode), plotSettings, workCombo, debug)
    
    dataCombo = []    
    mDs = ["nonres","phipi","kstk","kpipi","pipipi"]
    MDs = ["NonRes", "PhiPi", "KstK", "KPiPi", "PiPiPi"]
    sample = [TString("up"),TString("down")]
    nEntriesCombo = []
    for m in mDs:
        for i in range(0,2):
            datasetTS = TString("dataSet")+modeTS+TString("_")+sample[i]+TString("_")+TString(m)
            dataCombo.append(GeneralUtils.GetDataSet(workCombo,datasetTS, debug))
            size = dataCombo.__len__()
            nEntriesCombo.append(dataCombo[size-1].numEntries())
            print "Data set: %s with number of events: %s"%(dataCombo[size-1].GetName(),nEntriesCombo[size-1])

    sample = [TString("both"),TString("both")]
    for i in range(1,10):
        print "Add data set: %s"%(dataCombo[i].GetName())
        dataCombo[0].append(dataCombo[i])

    obs = GeneralUtils.GetObservable(workCombo,TString(obs), debug)
    terrComb = GeneralUtils.CreateHistPDF(dataCombo[0], obs, TString("combBkgTimeErrorPdf"), bin, debug)
    terrComb.SetName("TimeErrorPdf_CombBkg")
    
        
    #obtain sWeighted data set
    workData = SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, TString(mode), true, false, false, debug)
    nameData = TString("dataSet_time_")+TString(mode)
    dataSig = GeneralUtils.GetDataSet(workData,  nameData, debug)
    terrSigName = TString("TimeErrorPdf_")+TString(mode)
    terrSig = GeneralUtils.CreateHistPDF(dataSig, obs, terrSigName, bin, debug)
    

    #obtain signal MC samples
    wD = (0.59)/(0.59+0.44)
    wU = (0.44)/(0.59+0.44)
    wGD = [0.9918, 0.9918, 0.9918, 1.5, 0.9322]
    wGU = [0.9918, 0.9918, 0.9918, 1.5, 0.9322]
    
    dataNameSig = "../data/config_fitSignal.txt"
    dataSigMC = []
    workSigMC = RooWorkspace("workSig","workSig")
    i = 0 
    for m in MDs:
        nameTS = TString("#Signal ")+modeTS2+TString(" ")+TString(m)
        print nameTS
        print "global weight for down = %lf, global weight for up = %lf"%(wD*wGD[i],wU*wGU[i])
        workSigMC = MassFitUtils.ObtainSignal(TString(dataNameSig), nameTS,
                                              MDSettings, modeTS, false, false, workSigMC, false,
                                              wD*wGD[i], wU*wGU[i], plotSettings, debug)
        i=i+1

    nEntriesSig = []    
    sample = [TString("down"),TString("up")]
    for m in mDs:
        for i in range(0,2):
            datasetTS = TString("dataSetMC_")+modeTS+TString("_")+sample[i]+TString("_")+TString(m)
            dataSigMC.append(GeneralUtils.GetDataSet(workSigMC,datasetTS, debug))
            size = dataSigMC.__len__()
            nEntriesSig.append(dataSigMC[size-1].numEntries())
            print "Data set: %s with number of events: %s"%(dataSigMC[size-1].GetName(),nEntriesSig[size-1])

    sample = [TString("both"),TString("both")]
    for i in range(1,10):
        print "Add data set: %s"%(dataSigMC[i].GetName())
        dataSigMC[0].append(dataSigMC[i])

    terrSigMC = GeneralUtils.CreateHistPDF(dataSigMC[0], obs, TString("sigMCTimeErrorPdf"), bin, debug)
                                    
    #obtain specific background from data
    workMiss = RooWorkspace("workMiss","workMiss")
    if mode == "Bs2DsPi":
        workMiss = MassFitUtils.ObtainMissForBsDsPi(dataTS, TString("#BdPi"), TString("nonres"), MDSettings, TString("Bd2DPi"), workMiss, plotSettings, false, debug)
        dataSpec = GeneralUtils.GetDataSet(workMiss,TString("dataSet_Miss_down_kpipi"),  debug)
        dataSpec2 = GeneralUtils.GetDataSet(workMiss,TString("dataSet_Miss_up_kpipi"),  debug)
        dataSpec.append(dataSpec2)
        terrSpec = GeneralUtils.CreateHistPDF(dataSpec, obs, TString("TimeErrorPdf_Bd2DPi"), bin, debug)
    else:
        DsPiNames = [TString("#Bs2DsPi NonRes"),
                     TString("#Bs2DsPi PhiPi"),
                     TString("#Bs2DsPi KstK"),
                     TString("#Bs2DsPi KPiPi"),
                     TString("#Bs2DsPi PiPiPi")]

        DsPiDataName = [TString("dataSet_Miss_down_nonres"), 
                        TString("dataSet_Miss_down_phipi"), 
                        TString("dataSet_Miss_down_kstk"),
                        TString("dataSet_Miss_down_kpipi"),
                        TString("dataSet_Miss_down_pipipi"),
                        TString("dataSet_Miss_up_nonres"),
                        TString("dataSet_Miss_up_phipi"),
                        TString("dataSet_Miss_up_kstk"),
                        TString("dataSet_Miss_up_kpipi"),
                        TString("dataSet_Miss_up_pipipi")]
        dataMiss = []
        for i in range(0,5):
            workMiss = MassFitUtils.ObtainMissForBsDsK(TString(myconfigfile["dataName"]), DsPiNames[i], MDSettings, TString("BsDsPi"), workMiss, plotSettings, false, debug)
        
        for i in range(0,10):    
            dataMiss.append(GeneralUtils.GetDataSet(workMiss,DsPiDataName[i],  debug))
            
        dataSpec = dataMiss[0]   
        for i in range(0,9):
            dataSpec.append(dataMiss[0])
        terrSpec = GeneralUtils.CreateHistPDF(dataSpec, obs, TString("TimeErrorPdf_Bs2DsPi"), bin, debug)    
            
            
    #obtain data sets for MC bkg                                    
    if mode == "Bs2DsPi":
        modes =["Bs2DsstPi","Lb2LcPi","Bs2DsK"]
    else:
        modes = ["Bs2DsRho","Bs2DsstPi", "Lb2Dsp","Lb2Dsstp", "Bd2DK", "Bd2DPi", "Lb2LcK", "Lb2LcPi"]

    MDRatio= 1.0-myconfigfile["lumRatio"]
    MURatio= myconfigfile["lumRatio"]

    workSpecBkg = RooWorkspace("workSpecBkg","workSpecBkg")

    workSpecBkg = MassFitUtils.ObtainSpecBack(dataTS, TString("#MC FileName MD"), TString("#MC TreeName"),MDSettings, TString(mode), workSpecBkg, true, MDRatio, plotSettings, debug)
    workSpecBkg = MassFitUtils.ObtainSpecBack(dataTS, TString("#MC FileName MU"), TString("#MC TreeName"), MDSettings, TString(mode), workSpecBkg, true, MURatio, plotSettings, debug)      

    pre = "dataSetMC_"
    pol = ["down","up"]
        
    dataW = []
    terrpdf = []
    for m in modes:
        nameD = pre+m+"_"+pol[0]
        dataD = GeneralUtils.GetDataSet(workSpecBkg,TString(nameD),  debug)
        nameU = pre+m+"_"+pol[1]
        dataU = GeneralUtils.GetDataSet(workSpecBkg,TString(nameU),  debug)
        dataU.append(dataD)
        #dataW.append(dataU)
        dataW.append(RooDataSet(dataU.GetName(), dataU.GetName(),
                                dataU.get(), RooFit.Import(dataU), RooFit.WeightVar("weights")))
        
    for i in range(0,dataW.__len__()):
        nameTerrPDF = "TimeErrorPdf_"+modes[i]
        terrpdf.append(GeneralUtils.CreateHistPDF(dataW[i], obs, TString(nameTerrPDF), bin, debug))
      

    histRatio = []
    histSig = WeightingUtils.GetHist(dataSig, obs, bin, debug) 
    histW = []
    pdfW = []
    for i in range(0,dataW.__len__()):
        histRatioName = "histRatio_"+modes[i]
        print histRatioName
        histRatio.append(WeightingUtils.GetHistRatio(dataW[i],dataSigMC[0], obs, histRatioName, bin, debug))
        histWeightName = "histWeight_"+modes[i]
        print histWeightName
        histW.append(WeightingUtils.MultiplyHist(histSig, histRatio[i], obs, histWeightName, debug))
        nameTerrPDF = "TimeErrorPdf_"+modes[i]
        print "name: %s, num: %s, sum: %s"%(histW[i].GetName(), str(histW[i].GetEntries()), str(histW[i].GetSumOfWeights()))
        savename = histWeightName+".root" 
        histW[i].SaveAs(savename)
        pdfW.append(GeneralUtils.CreateHistPDF(histW[i],obs, TString(nameTerrPDF), bin, debug))
                    
    canv = TCanvas("canv","canv", 1200,1000)
    frame = obs.frame()
    frame.SetTitle("")
    frame.GetXaxis().SetTitle("time errors [ps]")
    frame.GetYaxis().SetTitle(' ')
    frame.GetXaxis().SetLabelFont( 132 );
    frame.GetYaxis().SetLabelFont( 132 );
    frame.GetXaxis().SetLabelSize( 0.04 );
    frame.GetYaxis().SetLabelSize( 0.04 );
    frame.GetXaxis().SetTitleFont( 132 );
    frame.GetYaxis().SetTitleFont( 132 );
    frame.GetXaxis().SetTitleSize( 0.04 );
    frame.GetYaxis().SetTitleSize( 0.04 );
                                                            
    
    legend = TLegend( 0.60, 0.50, 0.88, 0.88 )

    legend.SetTextSize(0.03)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("LHCb")

    terrSigMC.plotOn(frame, RooFit.LineColor(kBlack), RooFit.LineWidth(7))
    lS = TLine()
    lS.SetLineColor(kBlack)
    lS.SetLineWidth(4)
    lS.SetLineStyle(kSolid)
    legend.AddEntry(lS,"signal BsDsPi", "L")
    
    color = [kBlue+2, kRed, kOrange, kMagenta+3, kGreen+3, kBlue-10, kYellow, kRed-7]                                                      
    l = []
    for i in range(0,terrpdf.__len__()):
        terrpdf[i].plotOn(frame, RooFit.LineColor(color[i]))
    
        l.append(TLine())
        l[i].SetLineColor(color[i])
        l[i].SetLineWidth(4)
        l[i].SetLineStyle(kSolid)
        legend.AddEntry(l[i], modes[i] , "L")
    
    frame.Draw()
    legend.Draw("same")
    #frame.GetYaxis().SetRangeUser(0.1,250.)
    #canv.GetPad(0).SetLogy()
    canv.Print(Form("comparison_MC_%s%s.pdf"%(mode,sufix)))  

    canv2 = TCanvas("canv2","canv2", 1200,1000)
    frame2 = obs.frame()
    frame2.SetTitle("")
    frame2.GetXaxis().SetTitle("time errors [ps]")
    frame2.GetYaxis().SetTitle(' ')
    frame2.GetXaxis().SetLabelFont( 132 );
    frame2.GetYaxis().SetLabelFont( 132 );
    frame2.GetXaxis().SetLabelSize( 0.04 );
    frame2.GetYaxis().SetLabelSize( 0.04 );
    frame2.GetXaxis().SetTitleFont( 132 );
    frame2.GetYaxis().SetTitleFont( 132 );
    frame2.GetXaxis().SetTitleSize( 0.04 );
    frame2.GetYaxis().SetTitleSize( 0.04 );

    terrSig.plotOn(frame2, RooFit.LineColor(kBlack), RooFit.LineWidth(7))
    terrSpec.plotOn(frame2, RooFit.LineColor(kMagenta-7))

    lSpec = TLine()
    lSpec.SetLineColor(kMagenta-7)
    lSpec.SetLineWidth(4)
    lSpec.SetLineStyle(kSolid)
    if mode == "BsDsPi":
        legend.AddEntry(lSpec, "Bd2DPi" , "L")
    else:
        legend.AddEntry(lSpec, "Bs2DsPi" , "L")

    terrComb.plotOn(frame2, RooFit.LineColor(kCyan+3))
    lC = TLine()
    lC.SetLineColor(kCyan+3)
    lC.SetLineWidth(4)
    lC.SetLineStyle(kSolid)
    legend.AddEntry(lC,"combBkg", "L")

                        
    for i in range(0,terrpdf.__len__()):
        pdfW[i].plotOn(frame2, RooFit.LineColor(color[i]))
                
    frame2.Draw()
    legend.Draw("same")
    canv2.Print(Form("comparison_Data_%s%s.pdf"%(mode,sufix)))
        
    workTem = RooWorkspace("workspace","workspace")
    getattr(workTem,'import')(terrSig)
    getattr(workTem,'import')(terrComb)
    getattr(workTem,'import')(terrSpec)
    for i in range(0,terrpdf.__len__()):
        getattr(workTem,'import')(pdfW[i])
    workTem.Print("v")
    workTem.SaveAs(Form("template_Data_Terr_%s%s.root"%(mode,sufix)))

    plot_components = true
    
    if plot_components:
        if mode == "Bs2DsPi":
            print "BsDsPi"
            colorPC = [kBlue-8, kRed, kGreen+3, kOrange-3 ]
            stylePC = [1,2,3,6]
            
            canPC = []
            framePC = []
            legendPC = []
            lhcbtextPC = []
            
            for i in range(0,4):
                nameCanv = "canPC_"+str(i)
                canPC.append(TCanvas(nameCanv,nameCanv, 1600,1200))

                framePC.append(obs.frame())
                framePC[i].SetTitle("")
                framePC[i].GetXaxis().SetTitle("time errors [ps]")
                framePC[i].GetYaxis().SetTitle(' ')
                framePC[i].GetXaxis().SetLabelFont( 132 );
                framePC[i].GetYaxis().SetLabelFont( 132 );
                framePC[i].GetXaxis().SetLabelSize( 0.045);
                framePC[i].GetYaxis().SetLabelSize( 0.045 );
                framePC[i].GetXaxis().SetTitleFont( 132 );
                framePC[i].GetYaxis().SetTitleFont( 132 );
                framePC[i].GetXaxis().SetTitleSize( 0.05 );
                framePC[i].GetYaxis().SetTitleSize( 0.05 );

                if i > 1:
                    legendPC.append(TLegend( 0.55, 0.72, 0.88, 0.78 ))
                else:
                    legendPC.append(TLegend( 0.62, 0.58, 0.88, 0.88 ))
                legendPC[i].SetTextSize(0.06)
                legendPC[i].SetTextFont(12)
                legendPC[i].SetFillColor(4000)
                legendPC[i].SetShadowColor(0)
                legendPC[i].SetBorderSize(0)
                legendPC[i].SetTextFont(132)
                
                lhcbtextPC.append(TLatex())
                lhcbtextPC[i].SetTextFont(132)
                lhcbtextPC[i].SetTextColor(1)
                lhcbtextPC[i].SetTextSize(0.06)
                lhcbtextPC[i].SetTextAlign(12)

            linePC = []
            for i in range(0, 4):
                linePC.append(TLine())
                linePC[i].SetLineColor(colorPC[i])
                linePC[i].SetLineWidth(4)
                linePC[i].SetLineStyle(stylePC[i])

            for i in range(0,3):
                terrpdf[i].plotOn(framePC[0], RooFit.LineColor(colorPC[i]), RooFit.LineStyle(stylePC[i]))
                pdfW[i].plotOn(framePC[1], RooFit.LineColor(colorPC[i]), RooFit.LineStyle(stylePC[i]))
           
            legendPC[0].AddEntry(linePC[0], "B_{s} #rightarrow D_{s}^{*}#pi" , "L")
            legendPC[0].AddEntry(linePC[1], "#Lambda_{b} #rightarrow #Lambda_{c}#pi" , "L")
            legendPC[0].AddEntry(linePC[2], "B_{s} #rightarrow D_{s}K" , "L")
            
            legendPC[1].AddEntry(linePC[0], "B_{s} #rightarrow D_{s}^{*}#pi" , "L")
            legendPC[1].AddEntry(linePC[1], "#Lambda_{b} #rightarrow #Lambda_{c}#pi" , "L")
            legendPC[1].AddEntry(linePC[2], "B_{s} #rightarrow D_{s}K" , "L")

            terrSpec.plotOn(framePC[1], RooFit.LineColor(colorPC[3]), RooFit.LineStyle(stylePC[3]))
            legendPC[1].AddEntry(linePC[3], "B #rightarrow D#pi" , "L")
            
            terrComb.plotOn(framePC[2], RooFit.LineColor(kCyan+3), RooFit.LineStyle(1))
            legendPC[2].AddEntry(lC, "Combinatorial" , "L")
            
            terrSig.plotOn(framePC[3], RooFit.LineColor(kBlack), RooFit.LineStyle(1))
            legendPC[3].AddEntry(lS, "B_{s} #rightarrow D_{s}#pi" , "L")
            
            nameSave = [Form("template_Terr_MC_DsPi_SpecBkg%s.pdf"%(sufix)),
                        Form("template_Terr_Data_DsPi_SpecBkg%s.pdf"%(sufix)),
                        Form("template_Terr_Data_DsPi_CombBkg%s.pdf"%(sufix)),
                        Form("template_Terr_Data_DsPi_Signal%s.pdf"%(sufix))]

            for i in range(0,4):
                canPC[i].cd()
                framePC[i].Draw()
                legendPC[i].Draw()
                if i>1:
                    lhcbtextPC[i].DrawTextNDC( 0.55 , 0.84, "LHCb")
                else:
                    lhcbtextPC[i].DrawTextNDC( 0.50 , 0.84, "LHCb")
                canPC[i].Update()
                canPC[i].SaveAs(nameSave[i])

        else:
            print "BsDsK"
            colorPC = [kBlue-2, kBlue-2, kYellow+1, kYellow+1, kRed, kRed, kGreen+3, kGreen+3]
            stylePC = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2,1]

            canPC = []
            framePC = []
            legendPC = []
            lhcbtextPC = []

                            
            for i in range(0,10):
                nameCanv = "canPC_"+str(i)
                canPC.append(TCanvas(nameCanv,nameCanv, 1600,1200))

                framePC.append(obs.frame())
                framePC[i].SetTitle("")
                framePC[i].GetXaxis().SetTitle("time errors [ps]")
                framePC[i].GetYaxis().SetTitle(' ')
                framePC[i].GetXaxis().SetLabelFont( 132 );
                framePC[i].GetYaxis().SetLabelFont( 132 );
                framePC[i].GetXaxis().SetLabelSize( 0.045);
                framePC[i].GetYaxis().SetLabelSize( 0.045 );
                framePC[i].GetXaxis().SetTitleFont( 132 );
                framePC[i].GetYaxis().SetTitleFont( 132 );
                framePC[i].GetXaxis().SetTitleSize( 0.05 );
                framePC[i].GetYaxis().SetTitleSize( 0.05 );
                if i > 7:
                    legendPC.append(TLegend( 0.55, 0.72, 0.88, 0.78 ))
                else:
                    legendPC.append(TLegend( 0.62, 0.65, 0.88, 0.88 ))
                legendPC[i].SetTextSize(0.06)
                legendPC[i].SetTextFont(12)
                legendPC[i].SetFillColor(4000)
                legendPC[i].SetShadowColor(0)
                legendPC[i].SetBorderSize(0)
                legendPC[i].SetTextFont(132)
                                        
                lhcbtextPC.append(TLatex())
                lhcbtextPC[i].SetTextFont(132)
                lhcbtextPC[i].SetTextColor(1)
                lhcbtextPC[i].SetTextSize(0.06)
                lhcbtextPC[i].SetTextAlign(12)

                
            linePC = []
            for i in range(0, 8):
                linePC.append(TLine())
                linePC[i].SetLineColor(colorPC[i])
                linePC[i].SetLineWidth(4)
                linePC[i].SetLineStyle(stylePC[i])

            lineDsPi = TLine()
            lineDsPi.SetLineColor(color[0])
            lineDsPi.SetLineWidth(4)
            lineDsPi.SetLineStyle(3)

            terrpdf[0].plotOn(framePC[0], RooFit.LineColor(colorPC[0]), RooFit.LineStyle(stylePC[0]))
            terrpdf[1].plotOn(framePC[0], RooFit.LineColor(colorPC[1]), RooFit.LineStyle(stylePC[1]))
            legendPC[0].AddEntry(linePC[0], "B_{s} #rightarrow D_{s} #rho" , "L")
            legendPC[0].AddEntry(linePC[1], "B_{s} #rightarrow D_{s}^{*}#pi" , "L")
            
            terrpdf[2].plotOn(framePC[1], RooFit.LineColor(colorPC[2]), RooFit.LineStyle(stylePC[2]))
            terrpdf[3].plotOn(framePC[1], RooFit.LineColor(colorPC[3]), RooFit.LineStyle(stylePC[3]))
            legendPC[1].AddEntry(linePC[2], "#Lambda_{b} #rightarrow D_{s} p" , "L")
            legendPC[1].AddEntry(linePC[3], "#Lambda_{b} #rightarrow D_{s}^{*}p" , "L")
            
            terrpdf[4].plotOn(framePC[2], RooFit.LineColor(colorPC[4]), RooFit.LineStyle(stylePC[4]))
            terrpdf[5].plotOn(framePC[2], RooFit.LineColor(colorPC[5]), RooFit.LineStyle(stylePC[5]))
            legendPC[2].AddEntry(linePC[4], "B #rightarrow DK" , "L")
            legendPC[2].AddEntry(linePC[5], "B #rightarrow D#pi" , "L")
            
            terrpdf[6].plotOn(framePC[3], RooFit.LineColor(colorPC[6]), RooFit.LineStyle(stylePC[6]))
            terrpdf[7].plotOn(framePC[3], RooFit.LineColor(colorPC[7]), RooFit.LineStyle(stylePC[7]))
            legendPC[3].AddEntry(linePC[6], "#Lambda_{b} #rightarrow #Lambda_{c}K" , "L")
            legendPC[3].AddEntry(linePC[7], "#Lambda_{b} #rightarrow #Lambda_{c}#pi" , "L")

            pdfW[0].plotOn(framePC[4], RooFit.LineColor(colorPC[0]), RooFit.LineStyle(stylePC[0]))
            pdfW[1].plotOn(framePC[4], RooFit.LineColor(colorPC[1]), RooFit.LineStyle(stylePC[1]))
            terrSpec.plotOn(framePC[4], RooFit.LineColor(colorPC[0]), RooFit.LineStyle(3))
            legendPC[4].AddEntry(linePC[0], "B_{s} #rightarrow D_{s} #rho" , "L")
            legendPC[4].AddEntry(linePC[1], "B_{s} #rightarrow D_{s}^{*}#pi" , "L")
            legendPC[4].AddEntry(lineDsPi, "B_{s} #rightarrow D_{s}#pi" , "L")
            
            pdfW[2].plotOn(framePC[5], RooFit.LineColor(colorPC[2]), RooFit.LineStyle(stylePC[2]))
            pdfW[3].plotOn(framePC[5], RooFit.LineColor(colorPC[3]), RooFit.LineStyle(stylePC[3]))
            legendPC[5].AddEntry(linePC[2], "#Lambda_{b} #rightarrow D_{s} p" , "L")
            legendPC[5].AddEntry(linePC[3], "#Lambda_{b} #rightarrow D_{s}^{*}p" , "L")
            
            pdfW[4].plotOn(framePC[6], RooFit.LineColor(colorPC[4]), RooFit.LineStyle(stylePC[4]))
            pdfW[5].plotOn(framePC[6], RooFit.LineColor(colorPC[5]), RooFit.LineStyle(stylePC[5]))
            legendPC[6].AddEntry(linePC[4], "B #rightarrow DK" , "L")
            legendPC[6].AddEntry(linePC[5], "B #rightarrow D#pi" , "L")

            pdfW[6].plotOn(framePC[7], RooFit.LineColor(colorPC[6]), RooFit.LineStyle(stylePC[6]))
            pdfW[7].plotOn(framePC[7], RooFit.LineColor(colorPC[7]), RooFit.LineStyle(stylePC[7]))
            legendPC[7].AddEntry(linePC[6], "#Lambda_{b} #rightarrow #Lambda_{c}K" , "L")
            legendPC[7].AddEntry(linePC[7], "#Lambda_{b} #rightarrow #Lambda_{c}#pi" , "L")

            terrSig.plotOn(framePC[8], RooFit.LineColor(kBlack), RooFit.LineStyle(1))
            legendPC[8].AddEntry(lS, "B_{s} #rightarrow D_{s}K" , "L")

            terrComb.plotOn(framePC[9], RooFit.LineColor(kCyan+3), RooFit.LineStyle(1))
            legendPC[9].AddEntry(lC, "Combinatorial" , "L")
                        
            nameSave = [ Form("template_Terr_MC_DsK_Bs2DsDsstPiRho%s.pdf"%(sufix)),
                         Form("template_Terr_MC_DsK_Lb2DsDsstp%s.pdf"%(sufix)),
                         Form("template_Terr_MC_DsK_Bd2DKPi%s.pdf"%(sufix)),
                         Form("template_Terr_MC_DsK_Lb2LcKPi%s.pdf"%(sufix)),
                         Form("template_Terr_Data_DsK_Bs2DsDsstPiRho%s.pdf"%(sufix)),
                         Form("template_Terr_Data_DsK_Lb2DsDsstp%s.pdf"%(sufix)),
                         Form("template_Terr_Data_DsK_Bd2DKPi%s.pdf"%(sufix)),
                         Form("template_Terr_Data_DsK_Lb2LcKPi%s.pdf"%(sufix)),
                         Form("template_Terr_Data_DsK_Signal%s.pdf"%(sufix)),
                         Form("template_Terr_Data_DsK_CombBkg%s.pdf"%(sufix))]
            
            for i in range(0,10):             
                canPC[i].cd()
                framePC[i].Draw()
                legendPC[i].Draw()
                if i>7:
                    lhcbtextPC[i].DrawTextNDC( 0.55 , 0.84, "LHCb")
                else:
                    lhcbtextPC[i].DrawTextNDC( 0.50 , 0.84, "LHCb")
                canPC[i].Update()
                canPC[i].SaveAs(nameSave[i])
                 
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--pathName',
                   dest = 'pathName',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights-PAPER-1fb/sWeights_BsDsK_all_both_BDTGA.root')

parser.add_option( '--treeName',
                   dest = 'treeName',
                   default = 'merged',
                   help = 'name of the workspace'
                   )

parser.add_option( '--obs',
                   dest = 'obs',
                   default = 'lab0_LifetimeFit_ctauErr')

parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   default = 'BsDsPi',
                   help = 'set observable '
                   )
parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsKConfigForNominalMassFitBDTGA')

parser.add_option( '-s', '--sufix',
                   dest = 'sufix',
                   metavar = 'SUFIX',
                   default = '',
                   help = 'Add sufix to output'
                   )
parser.add_option( '--bin',
                   dest = 'bin',
                   action = 'store_true',
                   default = 20,
                   help = 'set number of bins'
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    runComparePDF( options.debug,
                   options.pathName, options.treeName,
                   options.obs, options.mode,
                   options.configName,
                   options.sufix,
                   options.bin
                   )                                
# -----------------------------------------------------------------------------
                                
