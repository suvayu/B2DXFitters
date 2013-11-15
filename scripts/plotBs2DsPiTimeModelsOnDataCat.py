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

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc
gROOT.SetBatch()


# MODELS
signalModelOnly = False

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{s}'

timeDown = 0.2
timeUp = 15.0

dataSetToPlot  = 'dataSet_time_Bs2DsPi'
pdfToPlot = 'sigTotPDF'
#fileToWriteOut = 'time_DsPi_BDTG123.pdf' 
#------------------------------------------------------------------------------
def plotDataSet(dataset, frame, BDTGbins) :
    if BDTGbins:
        dataset.plotOn(frame,
                       RooFit.Cut("bdtgbin==bdtgbin::BDTG1 || bdtgbin==bdtgbin::BDTG2 || bdtgbin==bdtgbin::BDTG3"),
                       RooFit.Binning(74))
    else:
        dataset.plotOn(frame,
                       RooFit.Cut("bdtgbin==bdtgbin::BDTGA"),
                       RooFit.Binning(74))
        

#------------------------------------------------------------------------------
def plotFitModel(model, frame, wksp, combData) :
    if debug :
        model.Print('t')
        frame.Print('v')

    mistag                              = wksp.var('lab0_BsTaggingTool_TAGOMEGA_OS')
    time                                = wksp.var('lab0_LifetimeFit_ctau')
    terr                                = wksp.var('lab0_LifetimeFit_ctauErr')
    dataset                             = wksp.data("combData") #dataSetToPlot)
    obs = dataset.get()
    obs.Print("v")
    cat = obs.find('bdtgbin')
    qf = obs.find('qf')
    qt = obs.find('qt')

   
    #for i in range(0,dataset.numEntries()) :
    #    obs = dataset.get(i)
    #    obs.Print("v")
    #exit(0)

    # plot model itself
    frame.Print("v")
    
    model.plotOn(frame,
                 RooFit.Slice(RooArgSet(qf,qt,cat)),
                 RooFit.ProjWData(RooArgSet(qf,qt,cat), dataset), #obs, dataset),
                 RooFit.LineColor(kBlue+3))
    
    #fr = model.plotOn(frame,
    #                  RooFit.Slice(BdtgBin,"bdtg2"),
    #                  RooFit.ProjWData(combData),
    #                  RooFit.LineColor(kRed))

    #fr = model.plotOn(frame,
    #                  RooFit.Slice(BdtgBin,"bdtg3"),
    #                  RooFit.ProjWData(combData),
    #                  RooFit.LineColor(kMagenta+2))
    
    '''
    qt.setIndex(0)
    qt.Print("v")
    print "1"
    pdf = model.createProjection(RooArgSet(qf,qt,time,cat,mistag))
    pdf.plotOn(frame,
               #RooFit.Slice(RooArgSet(qf,qt,cat)),
               #RooFit.ProjWData(obs, dataset),
               RooFit.LineColor(kRed))

    print "2"
    '''
    #model.createProjection(RooArgSet(qf,qt))    
    '''
    sliceData_1 = dataset.reduce(RooArgSet(obs),"((qt == 1 && qf == -1) || ( qt == -1 && qf == 1))")
    sliceData_1.plotOn(frame,RooFit.MarkerColor(kOrange))

    obs1 = sliceData_1.get()
    obs1.Print("v")
    
    model.plotOn(frame,
                 RooFit.Slice(obs1),
                 RooFit.ProjWData(obs1, sliceData_1),
                 RooFit.LineColor(kOrange))
    
    
    sliceData_2 = dataset.reduce(RooArgSet(obs),"(qt == -1 && qf == -1) || ( qt == 1 && qf == 1)")
    sliceData_2.plotOn(frame,RooFit.MarkerColor(kBlue+2))

    obs2 = sliceData_2.get()
    obs2.Print("v")
    
    model.plotOn(frame,
                 RooFit.Slice(obs2),
                 RooFit.ProjWData(obs2, sliceData_2),
                 RooFit.LineColor(kBlue+2))
    
                 
    sliceData_3 = dataset.reduce(RooArgSet(obs),"qt == 0")
    sliceData_3.plotOn(frame,RooFit.MarkerColor(kRed))

    obs3 = sliceData_3.get()
    obs3.Print("v")
    
    #qt.setLabel("Untagged")
    #qt.Print("v")
    
    model.plotOn(frame,
                 RooFit.Slice(obs3),
                 RooFit.ProjWData(obs3, sliceData_3),
                 RooFit.LineColor(kRed))
    '''
    
    

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
parser.add_option( '--BDTGbins',
                   dest = 'BDTGbins',
                   default = False,
                   action = 'store_true'
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

    from ROOT import TFile, TCanvas, gROOT, TLegend
    
    from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooTruthModel, RooDecay
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooAbsReal
    from ROOT import RooFit, FitMeTool, TGraph, TPad, gStyle
    from ROOT import CombBkgPTPdf
    from ROOT import BdPTAcceptance
    from ROOT import RooBlindTools
    from ROOT import RooSimultaneous, RooBDecay, RooEffResModel, RooAddModel, RooGaussModel, RooBinnedPdf
    from ROOT import PowLawAcceptance, Inverse, DecRateCoeff, RooHistPdf, RooUniform, MistagCalibration
    from ROOT import RooBinnedPdf, PowLawAcceptance  

    gROOT.SetStyle('Plain')
    #gROOT.SetBatch(False)

    
    f = TFile(FILENAME)

    w = f.Get(options.wsname)
    if not w :
        parser.error('Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      (options.wsname, FILENAME))

    f.Close()
    BDTGbins = options.BDTGbins
    
    time = w.var('lab0_LifetimeFit_ctau')
    #time.setRange(timeDown,timeUp)   
 
    #modelPDF = w.pdf(pdfToPlot) 
    #if modelPDF:
    #    print modelPDF.GetName()
    w.Print("v")
    
    totName = TString("simPdf")
    #totName  = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )
    if modelPDF:
        print modelPDF.GetName()
            
    dataset = w.data("combData")    
    #dataset  = w.data(dataSetToPlot) 
    if dataset:
        print dataset.GetName()

    if not (modelPDF and dataset) :
        w.Print('v')
        exit(1)

    
    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    canvas.cd()
       
    frame_t = time.frame()
    frame_t.SetTitle('')
 
    frame_t.SetTitle('')

    frame_t.GetXaxis().SetLabelSize( 0.05 )
    frame_t.GetYaxis().SetLabelSize( 0.05 )
    frame_t.GetXaxis().SetLabelFont( 132 )
    frame_t.GetYaxis().SetLabelFont( 132 )
    frame_t.GetXaxis().SetLabelOffset( 0.006 )
    frame_t.GetYaxis().SetLabelOffset( 0.006 )
    frame_t.GetXaxis().SetLabelColor( kWhite)
    
    frame_t.GetXaxis().SetTitleSize( 0.05 )
    frame_t.GetYaxis().SetTitleSize( 0.05 )
    frame_t.GetYaxis().SetNdivisions(512)
    
    frame_t.GetXaxis().SetTitleOffset( 1.00 )
    frame_t.GetYaxis().SetTitleOffset( 1.00 )
                                                    
    frame_t.GetXaxis().SetTitle('#font[12]{#tau (B_{s} #rightarrow D_{s} #pi) [ps]}')
    frame_t.GetYaxis().SetTitle((TString.Format("#font[12]{Candidates / ( " +
                                                str(time.getBinWidth(1))+" [ps])}") ).Data())
    

    plotDataSet(dataset, frame_t, BDTGbins)
    
    print '##### modelPDF is'
    print modelPDF
    if plotModel :
        plotFitModel(modelPDF, frame_t, w, dataset)

    gStyle.SetOptLogy(1)    
    frame_t.GetYaxis().SetRangeUser(0.05,5000)

    legend = TLegend( 0.12, 0.12, 0.3, 0.3 )
    legend.SetTextSize(0.06)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("LHCb Preliminary") # L_{int}=1.0 fb^{-1}")

    gr = TGraphErrors(10);
    gr.SetName("gr");
    gr.SetLineColor(kBlack);
    gr.SetLineWidth(2);
    gr.SetMarkerStyle(20);
    gr.SetMarkerSize(1.3);
    gr.SetMarkerColor(kBlack);
    gr.Draw("P");
    legend.AddEntry("gr","Data","lep");

    l1 = TLine()
    l1.SetLineColor(kBlue+3)
    l1.SetLineWidth(4)
    legend.AddEntry(l1, "Signal B_{s}#rightarrow D_{s}#pi", "L")
    
    
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
    frame_p.GetYaxis().SetTitleFont(62)
    frame_p.GetYaxis().SetNdivisions(106)
    frame_p.GetYaxis().SetLabelSize(0.18)
    frame_p.GetYaxis().SetLabelOffset(0.006)
    frame_p.GetXaxis().SetTitleSize(0.12)
    frame_p.GetXaxis().SetTitleFont(132)
    frame_p.GetXaxis().SetTitleOffset(0.85)
    frame_p.GetXaxis().SetNdivisions(5)
    frame_p.GetYaxis().SetNdivisions(5)
    frame_p.GetXaxis().SetLabelSize(0.09)
    frame_p.GetXaxis().SetLabelFont( 132 )
    frame_p.GetYaxis().SetLabelFont( 132 )
    frame_p.GetXaxis().SetTitle('#font[12]{#tau (B_{s} #rightarrow D_{s} #pi) [ps]}')
                                            
    pullHist = frame_t.pullHist()
    pullHist.SetMaximum(4.00)
    pullHist.SetMinimum(-4.00)

    frame_p.addPlotable(pullHist,"P")
    frame_p.Draw()
        
    
    axisX = pullHist.GetXaxis()
    axisX.Set(100, timeDown, timeUp )
    axisX.SetTitle('#font[12]{#tau (B_{s} #rightarrow D_{s} #pi) [ps]}')   
    axisX.SetTitleSize(0.150)
    axisX.SetTitleFont(132)
    axisX.SetLabelSize(0.150)
    axisX.SetLabelFont(132)
    axisX.SetTitle        
    
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
    axisY.SetLabelSize(0.100)
    axisY.SetLabelFont(132)
    axisY.SetNdivisions(5)        
    
    axisX = pullHist.GetXaxis()
    maxX = axisX.GetXmax()
    minX = axisX.GetXmin()
    axisX.SetLabelSize(0.100)
    
    range = max-min
    zero = max/range
    print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
    print "maxX: %s, minX: %s"%(maxX,minX)
    
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    graph.SetPoint(1,timeDown,0)
    graph.SetPoint(2,timeUp,0)
    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    graph2.SetPoint(1,timeDown,-3)
    graph2.SetPoint(2,timeUp,-3)
    graph2.SetLineColor(kRed)
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    graph3.SetPoint(1,timeDown,3)
    graph3.SetPoint(2,timeUp,3)
    graph3.SetLineColor(kRed)
    
    pullHist.SetTitle("");
    
    pullHist.Draw("AP")
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
    
    pad2.Update()
    canvas.Update()
    
    chi2 = frame_t.chiSquare() 
    chi22 = frame_t.chiSquare(1)
      
    print "chi2: %f"%(chi2)
    print "chi22: %f"%(chi22)
    
    sufixTS = TString(options.sufix)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS

    nameCanPdf = TString("time_DsPi")+sufixTS+TString(".pdf")
    nameCanPng = TString("time_DsPi")+sufixTS+TString(".png")
    nameCanRoot = TString("time_DsPi")+sufixTS+TString(".root")

    canvas.Print(nameCanPdf.Data())
    canvas.Print(nameCanPng.Data())
    canvas.Print(nameCanRoot.Data())

#------------------------------------------------------------------------------
