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

P_down = 0.0
P_up = 650000000.0
Time_down = 0.2
Time_up = 15.0
PT_down  = 500.0
PT_up = 45000.0
nTr_down = 1.0
nTr_up = 1000.0
Terr_down = 0.01
Terr_up = 0.1
BDTG_down = 0.3
BDTG_up = 1.0

tauH = 1.536875
tauL = 1.407125
gammaH = 1.0/tauH
gammaL = 1.0/tauL
gamma = (gammaH + gammaL) / 2.0
tau = 1.0 / gamma
dgamma = gammaH - gammaL

dataName      = '../data/config_fitSignal.txt'


#------------------------------------------------------------------------------
def runFitSplineAcc( debug, var , mode, modeDs, spline ) :

    
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    
    plotSettings = PlotSettings("plotSettings","plotSettings", "PlotLbLcPi", "pdf", 100, true, false, true)
    plotSettings.Print("v")
    
    MDSettings = MDFitterSettings("MDSettings","MDFSettings")
    
    MDSettings.SetMassBVar(TString("lab0_MassFitConsD_M"))
    MDSettings.SetMassDVar(TString("lab2_MM"))
    MDSettings.SetTimeVar(TString("lab0_LifetimeFit_ctau"))
    MDSettings.SetTerrVar(TString("lab0_LifetimeFit_ctauErr"))
    MDSettings.SetTagVar(TString("lab0_BsTaggingTool_TAGDECISION_OS"))
    MDSettings.SetTagOmegaVar(TString("lab0_BsTaggingTool_TAGOMEGA_OS"))
    MDSettings.SetIDVar(TString("lab1_ID"))
    MDSettings.SetPIDKVar(TString("lab1_PIDK"))
    MDSettings.SetBDTGVar(TString("BDTGResponse_1"))
    MDSettings.SetMomVar(TString("lab1_P"))
    MDSettings.SetTrMomVar(TString("lab1_PT"))
    MDSettings.SetTracksVar(TString("nTracks"))

    dataTS = TString(dataName)
    modeTS = TString(mode)
    if modeTS  == "BsDsK":
        PIDcut = 5
        MDSettings.SetPIDKRange(log(PIDcut),log(150))
    else:
        PIDcut = 0
        MDSettings.SetPIDKRange(PIDcut,150)
    obsTS = TString(var)
    if modeTS == "BDPi":
        modeDsTS = TString("KPiPi")
        MDSettings.SetTagVar(TString("lab0_BdTaggingTool_TAGDECISION_OS"))
        MDSettings.SetTagOmegaVar(TString("lab0_BdTaggingTool_TAGOMEGA_OS"))
        Dmass_down = 1770 #1830 #1930
        Dmass_up = 1920 #2015
        Bmass_down = 5000
        Bmass_up = 5500
        if ( obsTS == "lab2_MM"):
            mean  =  1869 #1968.49
        else:
            mean  = 5279 #367.51

    else:
        modeDsTS=TString(modeDs)
        Dmass_down = 1930
        Dmass_up = 2015
        Bmass_down = 5000
        Bmass_up = 5600
        if ( obsTS == "lab2_MM"):
            mean  =  1968.49
        else:
            mean  = 5367.51
            
                                                                
    MDSettings.SetMassBRange(Bmass_down, Bmass_up)
    MDSettings.SetMassDRange(Dmass_down, Dmass_up)
    MDSettings.SetTimeRange(Time_down,  Time_up )
    MDSettings.SetMomRange(P_down, P_up  )
    MDSettings.SetTrMomRange(PT_down, PT_up  )
    MDSettings.SetTracksRange(nTr_down, nTr_up  )
    MDSettings.SetBDTGRange( BDTG_down, BDTG_up  )
    MDSettings.SetPIDBach(PIDcut)
    MDSettings.SetTerrRange(Terr_down, Terr_up  )
    MDSettings.SetTagRange(-2.0, 2.0  )
    MDSettings.SetTagOmegaRange(0.0, 1.0  )
    MDSettings.SetIDRange( -1000.0, 1000.0 )
    
    MDSettings.SetLumDown(0.59)
    MDSettings.SetLumUp(0.44)
    MDSettings.SetLumRatio()
    
    MDSettings.Print("v")
    workspace = RooWorkspace("workspace","workspace")

    if modeDsTS == "All":
        mDs = ["NonRes", "PhiPi", "KstK", "KPiPi", "PiPiPi"]
    else:
        mDs = [modeDsTS]
    
    #for m in mDs:
    #    nameTS = TString("#Signal ")+modeTS+TString(" ")+TString(m)
    #    print nameTS
    #    workspace = MassFitUtils.ObtainSignal(dataTS, nameTS,
    #                                          MDSettings, modeTS, false, false, workspace, false,
    #                                          MDSettings.GetLumDown(), MDSettings.GetLumUp(), plotSettings, debug)
    
    #GeneralUtils.SaveWorkspace(workspace,TString("data_acceptance_BsDsK.root"), debug)
    #exit(0)

    
    workName = "data_acceptance_"+mode+".root"
    workspace = GeneralUtils.LoadWorkspace(TString(workName), TString("workspace"),debug)
    workspace.Print("v")
    time = GeneralUtils.GetObservable(workspace,obsTS, debug)
    weight = GeneralUtils.GetObservable(workspace,TString("weights"), debug)
    observables = RooArgSet( time, weight )
    
    if modeDsTS == "All":
        mDs2 = ["nonres","phipi","kstk","kpipi","pipipi"]
    else:
        temp = GeneralUtils.CheckDMode(modeDsTS)
        if temp == "kkpi" or temp == "":
            temp = GeneralUtils.CheckKKPiMode(modeDsTS)
        mDs2 = [ temp ]    

    data= []
    nEntries = []
    sample = [TString("up"),TString("down")]

    for m in mDs2:
        for i in range(0,2):
            datasetTS = TString("dataSetMC_")+modeTS+TString("_")+sample[i]+TString("_")+TString(m)
            data.append(GeneralUtils.GetDataSet(workspace,datasetTS, debug))
            size = data.__len__()
            nEntries.append(data[size-1].numEntries())
            print "Data set: %s with number of events: %s"%(data[size-1].GetName(),nEntries[size-1])
        
    sample = [TString("both"),TString("both")]
    if modeDsTS == "All":
        for i in range(1,10):
            print "Add data set: %s"%(data[i].GetName())
            data[0].append(data[i])
    else:
        data[0].append(data[1])
        data[0].Print()

    dataF = RooDataSet("data_fit", "data_fit", data[0].get(), RooFit.Import(data[0]), RooFit.WeightVar("weights")) 
    '''
    terr = GeneralUtils.GetObservable(workspace,TString("lab0_LifetimeFit_ctauErr"), debug)
    nameTerrPDF = "sigTimeErrorPdf_"+mode
    terrpdf = GeneralUtils.CreateHistPDF(dataF, terr, TString(nameTerrPDF), 40, debug)
    workout = RooWorkspace("workspace","workspace")
    getattr(workout,'import')(terrpdf)
    saveName = "template_MC_Terr_"+mode+".root"
    workout.Print()
    GeneralUtils.SaveWorkspace(workout,TString(saveName), debug)
    '''
    nEntriesF  = dataF.numEntries()
    print "Data set: %s with number of events: %s"%(dataF.GetName(),nEntriesF)
    #exit(0)
    
    if spline:
        binName = TString("splineBinning")
        TimeBin = RooBinning(0.2,15,binName.Data())
        TimeBin.addBoundary(0.25)
        TimeBin.addBoundary(0.5)
        TimeBin.addBoundary(1.0)
        TimeBin.addBoundary(2.0)
        TimeBin.addBoundary(3.0)
        #TimeBin.addBoundary(7.0) #(was 8) 
        TimeBin.addBoundary(12.0) #(was 10)
        #TimeBin.addBoundary(12.5)
        TimeBin.removeBoundary(0.2)
        TimeBin.removeBoundary(15.0)
        TimeBin.removeBoundary(0.2)
        TimeBin.removeBoundary(15.0)
        TimeBin.Print("v")
        time.setBinning(TimeBin, binName.Data())
        time.setRange(0.2, 15.0)
        listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, time)
        
        var1 = RooRealVar("var1", "var1", 1.0, 0.0, 3.0) 
        var2 = RooRealVar("var2", "var2", 1.0, 0.0, 3.0)  
        var3 = RooRealVar("var3", "var3", 1.0, 0.0, 3.0)  
        var4 = RooRealVar("var4", "var4", 1.0, 0.0, 3.0) 
        var5 = RooRealVar("var5", "var5", 1.0, 0.0, 3.0) 
        var6 = RooRealVar("var6", "var6", 1.0, 0.0, 3.0) 
        var7 = RooRealVar("var7", "var7", 1.0, 0.0, 3.0)
        var8 = RooRealVar("var8", "var8", 1.0)  
        var9 = RooAddition("var9","var9", RooArgList(var7,var8), listCoeff)
        #var9 = RooRealVar("var9","var9",1.0, 0.0, 3.0)
        
        Var = RooArgList(var1,var2,var3,var4,var5,var7,var8,var9)
        
        spl = RooCubicSplineFun("spline", "spline", time, "splineBinning", Var)
        
        if modeTS  == "BsDsPi":
            trm = PTResModels.tripleGausEffModel( time,
                                                  spl,
                                                  1.195,
                                                  0.0,
                                                  2.15934e-02,
                                                  3.71992e-02,
                                                  6.50957e-02,
                                                  3.88398e-01,
                                                  5.55078e-01,
                                                  debug)
        else:
            trm = PTResModels.tripleGausEffModel( time,
                                                  spl,
                                                  1.195,
                                                  0.0,
                                                  2.14295e-02,
                                                  3.68152e-02,
                                                  6.25371e-02,
                                                  3.71673e-01,
                                                  5.57606e-01,
                                                  debug)
            
        
        pdf = RooBDecay('Bdecay', 'Bdecay', time, RooRealConstant.value(tau),
                        RooRealConstant.value(dgamma), RooRealConstant.value(1.0),  RooRealConstant.value(0.0),
                        RooRealConstant.value(0.0),  RooRealConstant.value(0.0),  RooRealConstant.value(0.0),
                        trm, RooBDecay.SingleSided)
    else:
        tacc_beta       = RooRealVar('tacc_beta'    , 'tacc_beta',      0.03,   0.0,  0.50  )
        tacc_exponent   = RooRealVar('tacc_exponent', 'tacc_exponent',  1.9,    0.0,  10.0 )
        tacc_offset     = RooRealVar('tacc_offset'  , 'tacc_offset',    0.008,   -1.0,  10.0 )
        tacc_turnon     = RooRealVar('tacc_turnon'  , 'tacc_turnon',    1.45,    0.0,  10.0 )
        tacc            = PowLawAcceptance('tacc', 'tacc', tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta)

        
        if modeTS  == "BsDsPi":
            trm = PTResModels.tripleGausResolutionModel( time,
                                                         1.195,
                                                         0.0,
                                                         2.15934e-02,
                                                         3.71992e-02,
                                                         6.50957e-02,
                                                         3.88398e-01,
                                                         5.55078e-01,
                                                         debug)
        else:
            trm = PTResModels.tripleGausResolutionModel( time,
                                                         1.195,
                                                         0.0,
                                                         2.14295e-02,
                                                         3.68152e-02,
                                                         6.25371e-02,
                                                         3.71673e-01,
                                                         5.57606e-01,
                                                         debug)
            
                                                     

        pdfD = RooBDecay('Bdecay_noacc', 'Bdecay_noacc', time, RooRealConstant.value(tau),
                         RooRealConstant.value(dgamma), RooRealConstant.value(1.0),  RooRealConstant.value(0.0),
                         RooRealConstant.value(0.0),  RooRealConstant.value(0.0),  RooRealConstant.value(0.0),
                         trm, RooBDecay.SingleSided)

        pdf = RooEffProd('Bdecay','Bdecay',pdfD,tacc)

        
    myfitresult = pdf.fitTo(dataF, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                            RooFit.Verbose(True), RooFit.SumW2Error(True), RooFit.Extended(False),
                            RooFit.Offset(True))


    range_dw = time.getMin()
    range_up = time.getMax()

    lhcbtext = TLatex()
    lhcbtext.SetTextFont(132)
    lhcbtext.SetTextColor(1)
    lhcbtext.SetTextSize(0.07)
    lhcbtext.SetTextAlign(12)

    legend = TLegend( 0.62, 0.70, 0.88, 0.88 )

    legend.SetTextSize(0.05)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)

    l1 = TLine()
    l1.SetLineColor(kBlue+3)
    l1.SetLineWidth(4)
    l1.SetLineStyle(kSolid)
    legend.AddEntry(l1, "decay", "L")

    l2 = TLine()
    l2.SetLineColor(kRed)
    l2.SetLineWidth(4)
    l2.SetLineStyle(kSolid)
    legend.AddEntry(l2, "acceptance", "L")
                    
        
    frame_m = time.frame()
    frame_m.SetTitle('')
    
    frame_m.GetXaxis().SetLabelSize( 0.05 )
    frame_m.GetYaxis().SetLabelSize( 0.05 )
    frame_m.GetXaxis().SetLabelFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 )
    frame_m.GetXaxis().SetLabelOffset( 0.006 )
    frame_m.GetYaxis().SetLabelOffset( 0.006 )
    frame_m.GetXaxis().SetLabelColor( kWhite)
    
    frame_m.GetXaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetNdivisions(512)
    unit = "[ps]"
    frame_m.GetXaxis().SetTitleOffset( 1.00 )
    frame_m.GetYaxis().SetTitleOffset( 1.10 )
    #frame_m.GetYaxis().SetTitle((TString.Format("#font[12]{Candidates / ( " +
    #                                            str(time.getBinWidth(1))+" "+
    #                                            unit+")}") ).Data())
                                                        
    bin = 100
    dataF.plotOn(frame_m,RooFit.Binning( bin ))
    pdf.plotOn(frame_m, RooFit.LineColor(kBlue+3))
    if spline:
        spl.plotOn(frame_m, RooFit.LineColor(kRed), RooFit.Normalization(800, RooAbsReal.Relative))
    else:
        tacc.plotOn(frame_m, RooFit.LineColor(kRed), RooFit.Normalization(800, RooAbsReal.Relative))
    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    canvas.cd()
    pad1 = TPad("upperPad", "upperPad", .050, .22, 1.0, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0);
    pad1.Draw()
    pad1.cd()
    frame_m.GetYaxis().SetRangeUser(0.1,frame_m.GetMaximum()*1.0)
    frame_m.Draw()
    legend.Draw("same")
    lhcbtext.DrawTextNDC(0.50,0.85,"LHCb")
        
        
    canvas.cd()
    pad2 = TPad("lowerPad", "lowerPad", .050, .005, 1.0, .3275)
    pad2.SetBorderMode(0)
    pad2.SetBorderSize(-1)
    pad2.SetFillStyle(0)
    pad2.SetBottomMargin(0.35)
    pad2.SetTickx(0);
    pad2.Draw()
    pad2.SetLogy(0)
    pad2.cd()
    
    gStyle.SetOptLogy(0)
    frame_m.Print("v")
    #exit(0)
    frame_p = time.frame(RooFit.Title("pull_frame"))
    frame_p.Print("v")
    frame_p.SetTitle("")
    frame_p.GetYaxis().SetTitle("")
    frame_p.GetYaxis().SetTitleSize(0.09)
    frame_p.GetYaxis().SetTitleOffset(0.26)
    frame_p.GetYaxis().SetTitleFont(62)
    frame_p.GetYaxis().SetNdivisions(106)
    frame_p.GetYaxis().SetLabelSize(0.12)
    frame_p.GetYaxis().SetLabelOffset(0.006)
    frame_p.GetXaxis().SetTitleSize(0.15)
    frame_p.GetXaxis().SetTitleFont(132)
    frame_p.GetXaxis().SetTitleOffset(0.85)
    frame_p.GetXaxis().SetNdivisions(515)
    frame_p.GetYaxis().SetNdivisions(5)
    frame_p.GetXaxis().SetLabelSize(0.12)
    frame_p.GetXaxis().SetLabelFont( 132 )
    frame_p.GetYaxis().SetLabelFont( 132 )
    frame_p.GetXaxis().SetTitle('#font[12]{#tau(B_{s}) [ps]}')

    pullnameTS = TString("Bdecay_Norm[lab0_LifetimeFit_ctau]")
    pullname2TS = TString("h_data_fit")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    frame_p.addPlotable(pullHist,"P")

    chi2 = frame_m.chiSquare();
    chi22 = frame_m.chiSquare(pullnameTS.Data(),pullname2TS.Data());
    
    print "chi2: %f"%(chi2)
    print "chi22: %f"%(chi22)
    
    
    axisX = pullHist.GetXaxis()
    Bin = RooBinning(range_dw,range_up,'P')
    Bin.addUniform(bin, range_dw, range_up)
    axisX.Set(Bin.numBins(), Bin.array())
    
    axisY = pullHist.GetYaxis()
    max = 5.0 #axisY.GetXmax()
    min = -5.0 #axisY.GetXmin()
    axisY.SetLabelSize(0.12)
    axisY.SetNdivisions(5)
    axisX.SetLabelSize(0.12)
    
    rangeX = max-min
    zero = max/rangeX
    print "max: %s, min: %s, range: %s, zero:%s"%(max,min,rangeX,zero)
    
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    graph.SetPoint(1,range_dw,0)
    graph.SetPoint(2,range_up,0)
    
    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    graph2.SetPoint(1,range_dw,-3)
    graph2.SetPoint(2,range_up,-3)
    graph2.SetLineColor(kRed)
    
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    graph3.SetPoint(1,range_dw,3)
    graph3.SetPoint(2,range_up,3)
    graph3.SetLineColor(kRed)
    
    pullHist.GetXaxis().SetLabelFont( 132 )
    pullHist.GetYaxis().SetLabelFont( 132 )
    pullHist.SetTitle("")
                                                             
    frame_p.GetYaxis().SetRangeUser(-5.0,5.0)
    frame_p.Draw()
        
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
    #tex.DrawLatex(0.50,0.30,"m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]")
    
    pad2.Update()
    canvas.Update()
    if spline:
        suf = "spline"
    else:
        suf = "powlaw"

    namePDF = "data_sPline_"+mode+"_"+suf+".pdf"    
    nameROOT = "data_sPline_"+mode+"_"+suf+".root"
    canvas.SaveAs(namePDF)
    canvas.SaveAs(nameROOT)
    
                
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_LifetimeFit_ctau',
                   help = 'set observable '
                   )

parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   default = 'BsDsPi',
                   help = 'set observable '
                   )

parser.add_option( '--modeDs',
                   dest = 'modeDs',
                   default = 'KKPi',
                   help = 'set observable '
                   )
parser.add_option( '--spline',
                   dest = 'spline',
                   action = 'store_true',
                   default = False,
                   )


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    runFitSplineAcc( options.debug, options.var, options.mode, options.modeDs, options.spline )                                
# -----------------------------------------------------------------------------
                                
