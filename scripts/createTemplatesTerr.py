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
# -----------------------------------------------------------------------------
from B2DXFitters import *
from ROOT import *

from optparse import OptionParser
from math     import pi, log
import os, sys, gc

gROOT.SetBatch()

#------------------------------------------------------------------------------
def runComparePDF( debug, file1, work1, obs, mode ) :

    work = GeneralUtils.LoadWorkspace(TString(file1),TString(work1),debug)
    bin = 20

    if mode == "BsDsPi":
        workSig = GeneralUtils.LoadWorkspace(TString("/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"), TString(work1),debug)
    else:
        workSig = GeneralUtils.LoadWorkspace(TString("/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsK.root"), TString(work1),debug)
        
    obs   = GeneralUtils.GetObservable(work,TString(obs), debug)
    
    
    if mode == "BsDsPi":
        workSigMC = GeneralUtils.LoadWorkspace(TString("template_MC_Terr_BsDsPi.root"),
                                               TString(work1),debug)
        terrSigMC = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workSigMC, TString("sigTimeErrorPdf_BsDsPi"), debug)
        terrSigName = "TimeErrorPdf_Bs2DsPi"
        dataSig   = GeneralUtils.GetDataSet(workSig,TString("dataSet_time_Bs2DsPi_BDTGA"),  debug)
        workComb = GeneralUtils.LoadWorkspace(TString("work_dspi_combbkg.root"), TString(work1),debug)
        workComb.Print("v")
        #exit(0)
        dataComb = GeneralUtils.GetDataSet(workComb,TString("dataSetBsDsPi_up_"),  debug)
        modes =["Bs2DsstPi","Lb2LcPi","Bs2DsK"]

        workBDPi = GeneralUtils.LoadWorkspace(TString("work_dspi_pid_53005800_PIDK0_5M_BDTGA.root"),TString(work1),debug)
        workBDPi.Print("v")
        dataBDPi =  GeneralUtils.GetDataSet(workBDPi,TString("dataSet_Miss_down_kpipi"),  debug)
        dataBDPi2 =  GeneralUtils.GetDataSet(workBDPi,TString("dataSet_Miss_up_kpipi"),  debug)
        dataBDPi.append(dataBDPi2)
        terrSpec = GeneralUtils.CreateHistPDF(dataBDPi, obs, TString("TimeErrorPdf_Bd2DPi"), bin, debug)
                
    else:
        workSigMC = GeneralUtils.LoadWorkspace(TString("template_MC_Terr_BsDsK.root"),
                                               TString(work1),debug)
        terrSigMC = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workSigMC, TString("sigTimeErrorPdf_BsDsK"), debug)
        terrSigName = "TimeErrorPdf_Bs2DsK"
        dataSig   = GeneralUtils.GetDataSet(workSig,TString("dataSet_time_Bs2DsK_BDTGA"),  debug)
        workComb = GeneralUtils.LoadWorkspace(TString("work_dsk_combbkg.root"), TString(work1),debug)
        workComb.Print("v")
        #exit(0)
        dataComb = GeneralUtils.GetDataSet(workComb,TString("dataSetBsDsK_up_"),  debug)
        modes = ["Bs2DsRho","Bs2DsstPi", "Lb2Dsp","Lb2Dsstp", "Bd2DK", "Bd2DPi", "Lb2LcK", "Lb2LcPi"]
        
        workSpec = GeneralUtils.LoadWorkspace(TString("work_dspi_pid_53005800_PIDK0_5M_BDTGA.root"),TString(work1),debug)
        workSpec.Print("v")
        dataSpec =  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_down_nonres"),  debug)
        dataSpec1 =  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_up_nonres"),  debug)
        dataSpec2 =  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_down_phipi"),  debug)
        dataSpec3 =  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_up_phipi"),  debug)
        dataSpec4 =  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_down_kstk"),  debug)
        dataSpec5 =  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_up_kstk"),  debug)
        dataSpec6=  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_down_kpipi"),  debug)
        dataSpec7=  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_up_kpipi"),  debug)
        dataSpec8=  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_down_pipipi"),  debug)
        dataSpec9 =  GeneralUtils.GetDataSet(workSpec,TString("dataSetMC_BsDsPi_up_pipipi"),  debug)
        
        dataSpec.append(dataSpec1)
        dataSpec.append(dataSpec2)
        dataSpec.append(dataSpec3)
        dataSpec.append(dataSpec4)
        dataSpec.append(dataSpec5)
        dataSpec.append(dataSpec6)
        dataSpec.append(dataSpec7)
        dataSpec.append(dataSpec8)
        dataSpec.append(dataSpec9)
        
        terrSpec = GeneralUtils.CreateHistPDF(dataSpec, obs, TString("TimeErrorPdf_Bs2DsPi"), bin, debug)
        
        
    terrSig = GeneralUtils.CreateHistPDF(dataSig, obs, TString(terrSigName), bin, debug)    
    dataSigMC = GeneralUtils.GetDataSet(workSigMC,TString("data_fit"),  debug)
    terrComb = GeneralUtils.CreateHistPDF(dataComb, obs, TString("combBkgTimeErrorPdf"), bin, debug)
    terrComb.SetName("TimeErrorPdf_CombBkg")
    #exit(0)
    
    
    '''
    workCombBin = []
    dataCombBin = []
    for i in range (0,6):
        fileName  = "work_dsk_combbkg_"+str(i+1)+".root"
        workCombBin.append(GeneralUtils.LoadWorkspace(TString(fileName), TString(work1),debug))
        dataCombBin.append(GeneralUtils.GetDataSet(workCombBin[i],TString("dataSetBsDsK_up_"),  debug))
    
    terrCombBin = []
    for i in range(0,6):
         terrCombBin.append(GeneralUtils.CreateHistPDF(dataCombBin[i], obs, TString("combBkgTimeErrorPdf"), bin, debug))
    '''    

    pre = "dataSetMC_"
    pol = ["down","up"]
        
    dataW = []
    terrpdf = []
    for m in modes:
        nameD = pre+m+"_"+pol[0]
        dataD = GeneralUtils.GetDataSet(work,TString(nameD),  debug)
        nameU = pre+m+"_"+pol[1]
        dataU = GeneralUtils.GetDataSet(work,TString(nameU),  debug)
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
        histRatio.append(WeightingUtils.GetHistRatio(dataW[i],dataSigMC, obs, histRatioName, bin, debug))
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
    
    '''
    color = [kBlue+2, kRed, kOrange, kMagenta+3, kGreen+3, kBlue-10]
    bins = [5800,6000,6200,6400,6600,6800,7000]
    l = []
    for i in range(0,terrpdf.__len__()):
        terrCombBin[i].plotOn(frame, RooFit.LineColor(color[i]))
        
        l.append(TLine())
        l[i].SetLineColor(color[i])
        l[i].SetLineWidth(4)
        l[i].SetLineStyle(kSolid)
        nl = "comb in ["+str(bins[i])+","+str(bins[i+1])+"]"
        legend.AddEntry(l[i], nl , "L")
                                              
        
    terrComb.plotOn(frame, RooFit.LineColor(kCyan+3), RooFit.LineWidth(7))
    lC = TLine()
    lC.SetLineColor(kCyan+3)
    lC.SetLineWidth(4)
    lC.SetLineStyle(kSolid)
    legend.AddEntry(lC,"combBkg", "L")
    '''
    
    frame.Draw()
    legend.Draw("same")
    #frame.GetYaxis().SetRangeUser(0.1,250.)
    #canv.GetPad(0).SetLogy()
    if mode == "BsDsPi":
        canv.Print("comparison_MC_BsDsPi.pdf")
    else:
        canv.Print("comparison_MC_BsDsK.pdf")
                            


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
    #frame.GetYaxis().SetRangeUser(0.1,250.)
    #canv.GetPad(0).SetLogy()
    if mode == "BsDsPi":
        canv2.Print("comparison_Data_BsDsPi.pdf")
    else:
        canv2.Print("comparison_Data_BsDsK.pdf")
        
    workTem = RooWorkspace("workspace","workspace")
    getattr(workTem,'import')(terrSig)
    getattr(workTem,'import')(terrComb)
    getattr(workTem,'import')(terrSpec)
    for i in range(0,terrpdf.__len__()):
        getattr(workTem,'import')(pdfW[i])
    workTem.Print("v")
    if mode == "BsDsPi":
        workTem.SaveAs("template_Data_Terr_BsDsPi.root")
    else:
        workTem.SaveAs("template_Data_Terr_BsDsK.root")

    plot_components = true
    
    if plot_components:
        if mode == "BsDsPi":
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
            
            nameSave = ["template_Terr_MC_DsPi_SpecBkg.pdf",
                        "template_Terr_Data_DsPi_SpecBkg.pdf",
                        "template_Terr_Data_DsPi_CombBkg.pdf",
                        "template_Terr_Data_DsPi_Signal.pdf"]

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
                        
            nameSave = [ "template_Terr_MC_DsK_Bs2DsDsstPiRho.pdf",
                         "template_Terr_MC_DsK_Lb2DsDsstp.pdf",
                         "template_Terr_MC_DsK_Bd2DKPi.pdf",
                         "template_Terr_MC_DsK_Lb2LcKPi.pdf",
                         "template_Terr_Data_DsK_Bs2DsDsstPiRho.pdf",
                         "template_Terr_Data_DsK_Lb2DsDsstp.pdf",
                         "template_Terr_Data_DsK_Bd2DKPi.pdf",
                         "template_Terr_Data_DsK_Lb2LcKPi.pdf",
                         "template_Terr_Data_DsK_Signal.pdf",
                         "template_Terr_Data_DsK_CombBkg.pdf"]
            
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

parser.add_option( '--file1',
                   dest = 'file1',
                   default = 'work_dspi_pid_53005800_PIDK0_5M_BDTGA.root')

parser.add_option( '--work1',
                   dest = 'work1',
                   default = 'workspace')

parser.add_option( '--obs',
                   dest = 'obs',
                   default = 'lab0_LifetimeFit_ctauErr')

parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   default = 'BsDsPi',
                   help = 'set observable '
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
                   options.file1, options.work1,
                   options.obs, options.mode
                   )                                
# -----------------------------------------------------------------------------
                                
