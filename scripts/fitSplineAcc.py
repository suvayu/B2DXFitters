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
# Get signature of signal obtained from MC for PIDK variable                                                                                                                                        
# -----------------------------------------------------------------------------                                                                                                                      
def getSignalNames(myconfig):
    decay = myconfig["Decay"]
    Dmodes = myconfig["CharmModes"]
    year = myconfig["YearOfDataTaking"]

    hypo = ""
    if "Hypothesis" in myconfig.keys():
        hypo = " "+myconfig["Hypothesis"]+"Hypo"

    signalNames = []
    for y in year:
        for dmode in Dmodes:
            name = "#Signal "+decay+" "+dmode+" "+y+hypo
            signalNames.append(TString(name))

    return signalNames


#------------------------------------------------------------------------------
def runFitSplineAcc( debug, configName, read, fileNameIn, wsname, workName,
		     sample, mode, merge, year, binned, rel, log, plot, sufix) :
   
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "RUN MD FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="


    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    config = TString("../data/")+TString(configName)+TString(".py")
    from B2DXFitters.MDFitSettingTranslator import Translator

    mdt = Translator(myconfigfile,"MDSettings",False)

    MDSettings = mdt.getConfig()
    MDSettings.Print("v")

    dirPlot = "Plot"
    extPlot = "pdf"
    if myconfigfile.has_key("ControlPlots"):
        if myconfigfile["ControlPlots"].has_key("Directory"):
            dirPlot = myconfigfile["ControlPlots"]["Directory"]
            if not os.path.exists(dirPlot):
                os.makedirs(dirPlot)
        if myconfigfile["ControlPlots"].has_key("Extension"):
            extPlot = myconfigfile["ControlPlots"]["Extension"]

    plotSettings = PlotSettings("plotSettings","plotSettings", TString(dirPlot), extPlot , 100, True, False, True)
    plotSettings.Print("v")

    workspace = RooWorkspace("workspace","workspace")


    if not read:
        workspace = RooWorkspace("workspace","workspace")
        signalNames = getSignalNames(myconfigfile)
        for i in range(0,signalNames.__len__()):
            print signalNames[i]
            year = GeneralUtils.CheckDataYear(signalNames[i])
            workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), signalNames[i], MDSettings, decay, False, False, workspace, False, 1.0, 1.0, plotSettings, debug)	
            
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    else:
        workspace = GeneralUtils.LoadWorkspace(TString(fileNameIn),TString(workName),debug)

    t = TString("_")
    decayTS = myconfigfile["Decay"]
    modeTS = TString(mode)
    sampleTS = TString(sample)
    yearTS = TString(year)
    datasetTS = TString("dataSetMC_")+decayTS+t
    if merge == "pol" or merge == "both":
        sampleTS = TString("both")
    if merge == "year" or merge == "both":
        yearTS = TString("run1")

    sm = []
    data = []
    nEntries = []
    
    smyhs = GeneralUtils.GetSampleModeYearHypo(sampleTS, modeTS, yearTS, TString(""), merge, debug )
    s = GeneralUtils.GetSample(sampleTS, debug)
    m = GeneralUtils.GetMode(modeTS,debug)
    y = GeneralUtils.GetYear(yearTS,debug)

    data = []
    i = 0
    for smyh in smyhs:
        name = datasetTS +smyh
        data.append(GeneralUtils.GetDataSet(workspace,name,debug))
        if i != 0:
            data[0].append(data[i])
        i = i+1
    

    obs = data[0].get()
    time = obs.find(MDSettings.GetTimeVarOutName().Data())
    terr = obs.find(MDSettings.GetTerrVarOutName().Data())

    time.setBins(int(myconfigfile["Bins"]))
    dataF = RooDataSet("dataSet_time", "dataSet_time", data[0].get(), RooFit.Import(data[0]))
    dataF_binned = RooDataHist("data_fit_binned","data_fit_binned",RooArgSet(time,terr),dataF)


    print "-------------------- Data set info --------------------"
    print "[INFO] Data set unbinned: ",dataF.GetName(), dataF.numEntries(), dataF.sumEntries()
    print "[INFO] Data set binned: ", dataF_binned.GetName(), dataF_binned.numEntries(), dataF.sumEntries() 
    print "-------------------------------------------------------"
    dataF.Print("v")
    print "-------------------------------------------------------"
    dataF_binned.Print("v") 
    print "-------------------------------------------------------"
        
    print "[INFO] Acceptance model: splines"
    tMax = time.getMax()
    tMin = time.getMin()
    binName = TString("splineBinning")
    numKnots = myconfigfile["Acceptance"]["knots"].__len__()
    TimeBin = RooBinning(tMin,tMax,binName.Data())
    for i in range(0, numKnots):
        print "[INFO]   knot %s in place %s with value %s "%(str(i), str(myconfigfile["Acceptance"]["knots"][i]),
                                                            str(myconfigfile["Acceptance"]["values"][i]))
        TimeBin.addBoundary(myconfigfile["Acceptance"]["knots"][i])

    TimeBin.removeBoundary(tMin)
    TimeBin.removeBoundary(tMax)
    TimeBin.removeBoundary(tMin)
    TimeBin.removeBoundary(tMax)
    TimeBin.Print("v")
    time.setBinning(TimeBin, binName.Data())
    time.setRange(tMin, tMax)
    listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, time)

    tacc_list = RooArgList()
    tacc_var = []
    for i in range(0,numKnots):
        tacc_var.append(RooRealVar("var"+str(i+1), "var"+str(i+1), myconfigfile["Acceptance"]["values"][i], 0.0, 10.0))
        print "[INFO]  ",tacc_var[i].GetName()
        tacc_list.add(tacc_var[i])
    tacc_var.append(RooRealVar("var"+str(numKnots+1), "var"+str(numKnots+1), 1.0))
    len = tacc_var.__len__()
    tacc_list.add(tacc_var[len-1])
    print "[INFO]   n-2: ",tacc_var[len-2].GetName()
    print "[INFO]   n-1: ",tacc_var[len-1].GetName()

    #tacc_var.append(RooRealVar("var"+str(numKnots+2), "var"+str(numKnots+2), 1.0, 0.0, 10.0))
    tacc_var.append(RooAddition("var"+str(numKnots+2), "var"+str(numKnots+2),
                                RooArgList(tacc_var[len-2],tacc_var[len-1]), listCoeff))
    tacc_list.add(tacc_var[len])
    print "[INFO]   n: ",tacc_var[len].GetName()

    spl = RooCubicSplineFun("splinePdf", "splinePdf", time, "splineBinning", tacc_list)

    trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', 0.0, 'ps' )
    trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', myconfigfile["Resolution"]["scaleFactor"])
    trm = RooGaussEfficiencyModel("resmodel", "resmodel", time, spl, trm_mean, terr, trm_mean, trm_scale )
    
    #terrWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["Resolution"]["templates"]["fileName"]),
#					  TString(myconfigfile["Resolution"]["templates"]["workName"]), debug)
    terrpdf = GeneralUtils.CreateHistPDF(data[0], terr, TString("terr_template"), 20, debug)


    print " -----------------------------------"
    print "[INFO] Fixed parameters in RooBDecay"
    print "------------------------------------"
    print "[INFO] Delta Gammas : ",myconfigfile["DeltaGammas"]
    print "[INFO] Gammas: ", myconfigfile["Gammas"]
    print "[INFO] Tau: ", myconfigfile["Tau"]
    print "[INFO] 1/Tau: ",1.0/myconfigfile["Tau"]
    print "[INFO] DeltaMs: ",myconfigfile["DeltaMs"]
    print "[INFO] cosh - 1.0"
    print "[INFO] D*sinh - ", myconfigfile["sinh"]
    print "[INFO] C*cos - ", myconfigfile["cos"]
    print "[INFO] S*sin - ",myconfigfile["sin"]
    print "------------------------------------"
    timePDF = RooBDecay('Bdecay', 'Bdecay', time, RooRealConstant.value(myconfigfile["Tau"]),
			RooRealConstant.value(myconfigfile["DeltaGammas"]), 
                        RooRealConstant.value(1.0),  
                        RooRealConstant.value(myconfigfile["sinh"]),
			RooRealConstant.value(myconfigfile["cos"]),  
                        RooRealConstant.value(myconfigfile["sin"]),  
                        RooRealConstant.value(myconfigfile["DeltaMs"]),
			trm, RooBDecay.SingleSided)
        
    noncondset = RooArgSet(time)

    name_timeterr = TString("time_signal")
    totPDF = RooProdPdf(name_timeterr.Data(), name_timeterr.Data(),
			RooArgSet(terrpdf), RooFit.Conditional(RooArgSet(timePDF), noncondset))
    
    myfitresult = totPDF.fitTo(dataF_binned, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
			       RooFit.Verbose(False), 
                               RooFit.SumW2Error(True), 
                               RooFit.Extended(False))
			       #RooFit.Offset(True))


    myfitresult.Print("v")

    workout = RooWorkspace("workspace","workspace")
    getattr(workout,'import')(dataF)
    getattr(workout,'import')(totPDF)
    getattr(workout,'import')(myfitresult)
    workout.writeToFile(wsname)

    if plot:

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
    
        frame_m.GetXaxis().SetLabelSize( 0.06 )
        frame_m.GetYaxis().SetLabelSize( 0.06 )
        frame_m.GetXaxis().SetLabelFont( 132 )
        frame_m.GetYaxis().SetLabelFont( 132 )
        frame_m.GetXaxis().SetLabelOffset( 0.006 )
        frame_m.GetYaxis().SetLabelOffset( 0.006 )
        frame_m.GetXaxis().SetLabelColor( kWhite)
        
        frame_m.GetXaxis().SetTitleSize( 0.06 )
        frame_m.GetYaxis().SetTitleSize( 0.06 )
        frame_m.GetYaxis().SetNdivisions(512)
        unit = "[ps]"
        frame_m.GetXaxis().SetTitleOffset( 1.00 )
        frame_m.GetYaxis().SetTitleOffset( 1.00 )
        frame_m.GetYaxis().SetTitle((TString.Format("#font[132]{Candidates / ( " +
                                                    str(time.getBinWidth(1))+" "+
                                                    unit+")}") ).Data())

        bin = 148
        dataF.plotOn(frame_m,RooFit.Binning( bin ), RooFit.Name("dataSetCut"))
        totPDF.plotOn(frame_m, RooFit.LineColor(kBlue+3),  RooFit.Name("FullPdf"))
        
        spl.plotOn(frame_m, RooFit.LineColor(kRed), RooFit.Normalization(float(rel), RooAbsReal.Relative))
        
        canvas = TCanvas("canvas", "canvas", 1200, 800)
        canvas.cd()
        canvas.SetLeftMargin(0.01) 
        canvas.SetRightMargin(0.01)
        canvas.SetTopMargin(0.05)
        canvas.SetBottomMargin(0.05)
        pad1 = TPad("upperPad", "upperPad", .050, .22, 1.0, 1.0)
        pad1.SetBorderMode(0)
        pad1.SetBorderSize(-1)
        pad1.SetFillStyle(0)
        pad1.SetTickx(0);
        pad1.SetLeftMargin(0.115)
        pad1.SetRightMargin(0.05) 
        pad1.Draw()
        pad1.cd()
        frame_m.GetYaxis().SetRangeUser(0.1,frame_m.GetMaximum()*1.0)
        #frame_m.Draw()
        if log:
            gStyle.SetOptLogy(1)
            frame_m.GetYaxis().SetTitleOffset( 1.10 )
            frame_m.GetYaxis().SetRangeUser(1.5,frame_m.GetMaximum()*1.5)
        frame_m.Draw()
        legend.Draw("same")
        lhcbtext.DrawTextNDC(0.50,0.85,"LHCb")
        
        
        canvas.cd()
        pad2 = TPad("lowerPad", "lowerPad", .050, .005, 1.0, .3275)
        pad2.SetBorderMode(0)
        pad2.SetBorderSize(-1)
        pad2.SetFillStyle(0)
        pad2.SetBottomMargin(0.35)
        pad2.SetLeftMargin(0.115)
        pad2.SetRightMargin(0.05)
        pad2.SetTickx(0);
        pad2.Draw()
        pad2.SetLogy(0)
        pad2.cd()
        
        gStyle.SetOptLogy(0)
        frame_m.Print("v")
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
        frame_p.GetXaxis().SetTitle('#font[132]{#tau(B_{s}) [ps]}')
        
        obsTS = TString(time.GetName())
        pullnameTS = TString("FullPdf")
        pullname2TS = TString("dataSetCut")
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

        saveName = TString("time_")+decayTS+TString("_")+obsTS+TString("_")+sampleTS+TString("_")+modeTS+t+yearTS
        if sufix != "":
            saveName = saveName + TString("_") + TString(sufix)
        canName = saveName+TString(".pdf")
        canNamePng = saveName+TString(".png")
        canNameRoot = saveName+TString(".root")
        canNameC = saveName+TString(".C")
        canNameEps = saveName+TString(".eps")
        
        canvas.SaveAs(canName.Data())
        canvas.SaveAs(canNamePng.Data())
        canvas.SaveAs(canNameEps.Data())
        canvas.SaveAs(canNameC.Data())
        canvas.SaveAs(canNameRoot.Data())

                
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '-p', '--pol','--polarity',
                   dest = 'pol',
                   metavar = 'POL',
                   default = 'down',
                   help = 'Sample: choose up or down '
                   )

parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'kkpi',
                   help = 'Mode: choose all, kkpi, kpipi, pipipi, nonres, kstk, phipi, 3modeskkpi'
                   )

parser.add_option( '--merge',
                   dest = 'merge',
                   default = "",
                   help = 'for merging magnet polarities use: --merge pol, for merging years of data taking use: --merge year, for merging both use: --merge both'
                   )

parser.add_option( '--year',
		              dest = 'year',
                   default = "",
                   help = 'year of data taking can be: 2011, 2012, run1')

parser.add_option( '--binned',
                   dest = 'binned',
                   default = False,
                   action = 'store_true',
                   help = 'binned data Set'
                   )

parser.add_option( '--read',
                   dest = 'read',
                   action = 'store_true',
                   default = False,
                   )
parser.add_option( '--fileName',
                   dest = 'fileIn',
                   default = '/afs/cern.ch/work/g/gligorov//public/Bs2DsKPlotsForPaper/NominalFit/',
                   help = 'set observable '
                   )

parser.add_option( '-s','--save',
                   dest = 'save',
                   default = 'WS_Spline_Bs2DsPi.root')

parser.add_option( '--workName',
                   dest = 'work',
                   default = 'workspace',
                   help = 'set observable '
                   )
parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsPiConfigForNominalDMSFit')
parser.add_option( '--logscale', '--log',
                   dest = 'log',
                   action = 'store_true',
                   default = False,
                   help = 'log scale of plot'
                   )
parser.add_option( '--plot',
                   dest = 'plot',
                   action = 'store_true',
                   default = False,
                   help = 'plot fit result'
                   )

parser.add_option('--rel',
		  dest = "rel",
		  default = 1000) 
parser.add_option( '--sufix',
                   dest = 'sufix',
                   metavar = 'SUFIX',
                   default = '',
                   help = 'Add sufix to output'
                   )
# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    config = options.configName
    last = config.rfind("/")
    directory = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]

    import sys
    sys.path.append(directory)


    runFitSplineAcc( options.debug, configName, options.read, options.fileIn, options.save, options.work,
		     options.pol, options.mode, options.merge, options.year, options.binned, options.rel, 
                     options.log, options.plot, options.sufix)
# -----------------------------------------------------------------------------
                                
