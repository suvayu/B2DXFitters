#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot the Bd -> D pi time models                          #
#                                                                             #
#   Example usage:                                                            #
#      python plotBs2DsPiTimeModelsOnData.py WS_Time_DsPi.root                #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 01 / 06 / 2011                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Author: Vladimir Vava Gligorov                                            #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# settings for running without GaudiPython
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

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc
gROOT.SetBatch()
gROOT.ProcessLine(".x ../root/.rootlogon.C")

# MODELS
signalModelOnly = False

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{s}'

#timeDown = 0.2
#timeUp = 15.0

dataSetToPlot  = 'dataSet_time_BsDsK'
pdfToPlot = 'time_signal_BDTGA'
bin = 146
#fileToWriteOut = 'time_DsPi_BDTG123.pdf' 
#------------------------------------------------------------------------------
def plotDataSet(dataset, frame) :
    dataset.plotOn(frame,RooFit.Binning(bin),RooFit.DataError(RooAbsData.SumW2),
                   RooFit.Name("dataSetCut"))

#------------------------------------------------------------------------------
def plotFitModel(model, frame, wksp) :
    if debug :
        model.Print('t')
        frame.Print('v')

    lab0_BsTaggingTool_TAGDECISION_OS   = wksp.var('lab0_BsTaggingTool_TAGDECISION_OS')
    lab1_ID                             = wksp.var('lab1_ID')
    time                                = wksp.var('lab0_LifetimeFit_ctau')
    dataset                             = w.data(dataSetToPlot)

    # plot model itself
    fr = model.plotOn(frame,
                      RooFit.LineColor(kBlue+3),RooFit.Name("FullPdf"))

    #model.createProjection(RooArgSet(lab0_BsTaggingTool_TAGDECISION_OS,lab1_ID))    

    #sliceData = dataset.reduce(RooArgSet(time,lab0_BsTaggingTool_TAGDECISION_OS,lab1_ID),"lab0_BsTaggingTool_TAGDECISION_OS > 0")

    #sliceData.plotOn(frame,RooFit.Color(kRed))

#------------------------------------------------------------------------------
def legends(model, frame):
    stat = frame.findObject('data_statBox')
    prefix = 'Sig' if signalModelOnly else 'Tot'
    if not stat: stat = frame.findObject('%sEPDF_tData_statBox' % prefix)
    if stat :
        stat.SetTextSize(0.025)
    pt = frame.findObject('%sEPDF_t_paramBox' % prefix)
    if pt :
        pt.SetTextSize(0.02)
    # Legend of EPDF components
    leg = TLegend(0.56, 0.42, 0.87, 0.62)
    leg.SetFillColor(0)
    leg.SetTextSize(0.02)
    comps = model.getComponents()

    if signalModelOnly :
        pdfName = 'SigEPDF_t'
        pdf = comps.find(pdfName)
        curve = frame.findObject(pdfName + '_Norm[time]')
        if curve : leg.AddEntry(curve, pdf.GetTitle(), 'l')
        return leg, curve
    else :
        pdf1 = comps.find('SigEPDF_t')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'SigEPDF_t'
        curve1 = frame.findObject(pdfName)
        if curve1 : leg.AddEntry(curve1, pdf1.GetTitle(), 'l')
        pdf = comps.find('Bd2DKEPDF_t')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'Bd2DKEPDF_t'
        curve2 = frame.findObject(pdfName)
        if curve2 : leg.AddEntry(curve2, pdf.GetTitle(), 'l')
        pdf = comps.find('CombBkgEPDF_t')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'CombBkgEPDF_t'
        curve3 = frame.findObject(pdfName)
        if curve3 : leg.AddEntry(curve3, pdf.GetTitle(), 'l')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'CombBkgEPDF_t,Bd2DKEPDF_t'
        curve4 = frame.findObject(pdfName)
        if curve4 :
            leg.AddEntry(curve4, 'All but %s' % pdf1.GetTitle(), 'f')
            curve4.SetLineColor(0)
        pdfName = 'TotEPDF_t_Norm[time]'
        pdf = comps.find('TotEPDF_t')
        curve5 = frame.findObject(pdfName)
        #if curve5 : leg.AddEntry(curve5, pdf.GetTitle(), 'l')
        if curve5 : leg.AddEntry(curve5, 'Model (signal & background) EPDF', 'l')
        return leg, curve4

#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser(_usage)

parser.add_option('-w', '--workspace',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   default = 'workspace',
                   help = 'RooWorkspace name as stored in ROOT file'
)

parser.add_option( '-s', '--sufix',
                   dest = 'sufix',
                   metavar = 'SUFIX',
                   default = '',
                   help = 'Add sufix to output'
                   )

#------------------------------------------------------------------------------

if __name__ == '__main__' :
    (options, args) = parser.parse_args()

    if len(args) != 1 :
        parser.print_help()
        exit(-1)

    FILENAME = (args[ 0 ])
    if not exists(FILENAME) :
        parser.error('ROOT file "%s" not found! Nothing plotted.' % FILENAME)
        parser.print_help()

    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-13)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-13)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    # since we have finite ranges, the RooIntegrator1D is best suited to the job
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    
    from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooTruthModel, RooDecay
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooAbsReal
    from ROOT import RooFit, FitMeTool, TGraph, TPad, gStyle
    from ROOT import CombBkgPTPdf
    from ROOT import BdPTAcceptance
    from ROOT import RooBlindTools

    gROOT.SetStyle('Plain')
    #gROOT.SetBatch(False)

    
    f = TFile(FILENAME)

    w = f.Get(options.wsname)
    if not w :
        parser.error('Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      (options.wsname, FILENAME))

    f.Close()
    time = w.var('lab0_LifetimeFit_ctau')
    time.setBins(bin)
    #time.setRange(0.4,15)
    timeDown = time.getMin()
    timeUp = time.getMax()
    #time.setRange(timeDown,timeUp)   
 
    modelPDF = w.pdf(pdfToPlot) 
    if modelPDF:
        print modelPDF.GetName()
    dataset  = w.data(dataSetToPlot) 
    if dataset:
        print dataset.GetName()

    if not (modelPDF and dataset) :
        w.Print('v')
        exit(1)

    
    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    canvas.cd()
       
    frame_t = time.frame()
    frame_t.SetTitle('')
 
    frame_t.GetXaxis().SetLabelSize( 0.06 )
    frame_t.GetYaxis().SetLabelSize( 0.06 )
    frame_t.GetXaxis().SetLabelFont( 132 )
    frame_t.GetYaxis().SetLabelFont( 132 )
    frame_t.GetXaxis().SetLabelOffset( 0.006 )
    frame_t.GetYaxis().SetLabelOffset( 0.006 )
    frame_t.GetXaxis().SetLabelColor( kWhite)
    
    frame_t.GetXaxis().SetTitleSize( 0.06 )
    frame_t.GetYaxis().SetTitleSize( 0.06 )
    frame_t.GetYaxis().SetNdivisions(512)
    
    frame_t.GetXaxis().SetTitleOffset( 1.00 )
    frame_t.GetYaxis().SetTitleOffset( 0.85 )
    
    #frame_t.GetXaxis().SetTitle('#font[132]{#tau (B_{s} #rightarrow D_{s} #pi) [ps]}')
    frame_t.GetYaxis().SetTitle((TString.Format("#font[132]{Candidates / ( " +
                                                str(time.getBinWidth(1))+" ps)}") ).Data())
    
        

    plotDataSet(dataset, frame_t)
    
    print '##### modelPDF is'
    print modelPDF
    if plotModel :
        plotFitModel(modelPDF, frame_t, w)

    gStyle.SetOptLogy(1)
    frame_t.GetYaxis().SetRangeUser(0.4,250)

    legend = TLegend( 0.50, 0.6, 0.73, 0.88 )
    legend.SetTextSize(0.06)
    legend.SetTextFont(12)
    legend.SetFillColor(0)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("LHCb") # L_{int}=1.0 fb^{-1}")

    gr = TGraphErrors(1);
    gr.SetName("gr");
    gr.SetLineColor(kBlack);
    gr.SetLineWidth(2);
    gr.SetMarkerStyle(20);
    gr.SetMarkerSize(1.3);
    gr.SetMarkerColor(kBlack);
    #gr.Draw("P");
    legend.AddEntry(gr,"Data","lep");

    l1 = TLine()
    l1.SetLineColor(kBlue+3)
    l1.SetLineWidth(4)
    happypm   = "#lower[-0.95]{#scale[0.6]{#pm}}"
    happymp   = "#lower[-0.95]{#scale[0.6]{#mp}}"
    happy0   = "#lower[-0.95]{#scale[0.6]{0}}"
    decayDescriptor = "B_{s}#kern[-0.7]{"+happy0+"}#rightarrow D_{s}"+happypm+"#kern[0.1]{K"+happymp+"}"
    legend.AddEntry(l1, decayDescriptor, "L")
    
    
    pad1 = TPad("upperPad", "upperPad", .050, .22, 1.0, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0);
    pad1.Draw()
    pad1.cd()
               
    frame_t.Draw()
    legend.Draw("same")
    
    pad1.Update()
    
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
    
    frame_p = time.frame(RooFit.Title("pull_frame"))
    frame_p.Print("v")
    frame_p.SetTitle("")
    frame_p.GetYaxis().SetTitle("")
    frame_p.GetYaxis().SetTitleSize(0.09)
    frame_p.GetYaxis().SetTitleOffset(0.26)
    frame_p.GetYaxis().SetTitleFont(132)
    frame_p.GetYaxis().SetNdivisions(106)
    frame_p.GetYaxis().SetLabelSize(0.20)
    frame_p.GetYaxis().SetLabelOffset(0.006)
    frame_p.GetXaxis().SetTitleSize(0.20)
    frame_p.GetXaxis().SetTitleFont(132)
    frame_p.GetXaxis().SetTitleOffset(0.85)
    frame_p.GetXaxis().SetNdivisions(5)
    frame_p.GetYaxis().SetNdivisions(5)
    frame_p.GetXaxis().SetLabelSize(0.20)
    frame_p.GetXaxis().SetLabelFont( 132 )
    frame_p.GetYaxis().SetLabelFont( 132 )
    frame_p.GetXaxis().SetTitle('#font[132]{#tau('+decayDescriptor+') [ps]}')
    
    pullHist = frame_t.pullHist()
    pullHist.SetName("pullHist")
    pullHist.SetMaximum(3.5)
    pullHist.SetMinimum(-3.5)

    frame_p.addPlotable(pullHist,"P")
    frame_p.Draw()

    axisX = pullHist.GetXaxis()
    axisX.Set(100, timeDown, timeUp )
    axisX.SetTitle('#font[132]{#tau('+decayDescriptor+') [ps]}')   
    axisX.SetTitleSize(0.150)
    axisX.SetTitleFont(132)
    axisX.SetLabelSize(0.150)
    axisX.SetLabelFont(132)
    maxX = axisX.GetXmax()
    minX = axisX.GetXmin()  
 
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
    axisY.SetLabelSize(0.150)
    axisY.SetLabelFont(132)
    axisY.SetNdivisions(5)        
    
    range = max-min
    zero = max/range
    print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
    print "maxX: %s, minX: %s"%(maxX,minX)
    
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    graph.SetName("graph1")
    graph.SetTitle("")
    graph.SetPoint(1,timeDown,0)
    graph.SetPoint(2,timeUp,0)

    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    graph2.SetName("graph2")
    graph2.SetTitle("")
    graph2.SetPoint(1,timeDown,-3)
    graph2.SetPoint(2,timeUp,-3)
    graph2.SetLineColor(kRed)

    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    graph3.SetName("graph3")
    graph3.SetTitle("")
    graph3.SetPoint(1,timeDown,3)
    graph3.SetPoint(2,timeUp,3)
    graph3.SetLineColor(kRed)
    
    pullHist.SetTitle("");
    
    pullHist.Draw("AP")
    graph.Draw("L SAME")
    graph2.Draw("L SAME")
    graph3.Draw("L SAME")

    pad2.Update()
    canvas.Update()
    
    chi2 = frame_t.chiSquare() 
    chi22 = frame_t.chiSquare(1)
      
    print "chi2: %f"%(chi2)
    print "chi22: %f"%(chi22)
    
    sufixTS = TString(options.sufix)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS

    nameCanPdf = TString("time_DsK")+sufixTS+TString(".pdf")
    nameCanPng = TString("time_DsK")+sufixTS+TString(".png")
    nameCanRoot = TString("time_DsK")+sufixTS+TString(".root")
    nameCanC = TString("time_DsK")+sufixTS+TString(".C")
    nameCanEps = TString("time_DsK")+sufixTS+TString(".eps")


    canvas.Print(nameCanPdf.Data())
    canvas.Print(nameCanPng.Data())
    canvas.Print(nameCanRoot.Data())
    canvas.Print(nameCanC.Data())
    canvas.Print(nameCanEps.Data())


#------------------------------------------------------------------------------
