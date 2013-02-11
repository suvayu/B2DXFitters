#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78

""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.
# make sure the environment is set up properly

if test -z "$CMTCONFIG"; then
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
	        LD_PRELOAD="$k"
	        break 3
	    else
	        LD_PRELOAD="$LD_PRELOAD":"$k"
	        break 3
	    fi
	done
    done
done

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from math     import pi
import os, sys

if 'CMTCONFIG' in os.environ:
    import GaudiPython
import ROOT
# avoid memory leaks - will have to explicitly relinquish and acquire ownership
# if required, but PyROOT does not do what it thinks best without our knowing
# what it does
ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
if not 'CMTCONFIG' in os.environ:
    # enable ROOT to understand Reflex dictionaries
    ROOT.gSystem.Load('libCintex')
    ROOT.Cintex.Enable()
# load RooFit
ROOT.gSystem.Load('libRooFit')
from ROOT import RooFit
# load our own B2DXFitters library
if 'CMTCONFIG' in os.environ:
    GaudiPython.loaddict('B2DXFittersDict')
else:
    # running in standalone mode, we have to load things ourselves
    ROOT.gSystem.Load(os.environ['B2DXFITTERSROOT'] +                                                                                                 
            '/standalone/libB2DXFitters')

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MODELS
signalModelOnly = False

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{s}'


#------------------------------------------------------------------------------
def plotDataSet(dataset, frame) :
    dataset.plotOn(frame,
                    RooFit.Binning(70))
    dataset.statOn(frame,
                    RooFit.Layout(0.56, 0.90, 0.90),
                    RooFit.What('N'))

#------------------------------------------------------------------------------
def plotFitModel(model, frame, wksp) :
    if debug :
        model.Print('t')
        frame.Print('v')

    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "B"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('sigEPDF'),
    	    RooFit.LineWidth(1), RooFit.LineColor(kRed))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Bbar"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('sigEPDF'),
    	    RooFit.LineWidth(1), RooFit.LineColor(kBlue))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "B"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('sigEPDF'),
    	    RooFit.LineWidth(3), RooFit.LineColor(kRed), RooFit.LineStyle(kDashed))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Bbar"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('sigEPDF'),
    	    RooFit.LineWidth(3), RooFit.LineColor(kBlue), RooFit.LineStyle(kDashed))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Untagged"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('sigEPDF'),
	    RooFit.LineWidth(1), RooFit.LineColor(kGreen + 1))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Untagged"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('sigEPDF'),
	    RooFit.LineWidth(3), RooFit.LineColor(kGreen + 1), RooFit.LineStyle(kDashed))

    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "B"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('Bs2DsPiEPDF'),
    	    RooFit.LineWidth(1), RooFit.LineColor(kOrange))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Bbar"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('Bs2DsPiEPDF'),
    	    RooFit.LineWidth(1), RooFit.LineColor(kMagenta))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "B"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('Bs2DsPiEPDF'),
    	    RooFit.LineWidth(3), RooFit.LineColor(kOrange), RooFit.LineStyle(kDashed))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Bbar"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('Bs2DsPiEPDF'),
    	    RooFit.LineWidth(3), RooFit.LineColor(kMagenta), RooFit.LineStyle(kDashed))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Untagged"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('Bs2DsPiEPDF'),
	    RooFit.LineWidth(1), RooFit.LineColor(kCyan + 1))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Untagged"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('Bs2DsPiEPDF'),
	    RooFit.LineWidth(3), RooFit.LineColor(kCyan + 1), RooFit.LineStyle(kDashed))

    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "B"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('CombBkgEPDF_t'),
	    RooFit.LineWidth(1), RooFit.LineColor(kYellow))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Bbar"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('CombBkgEPDF_t'),
	    RooFit.LineWidth(3), RooFit.LineColor(kYellow), RooFit.LineStyle(kDashed))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "B"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('CombBkgEPDF_t'),
	    RooFit.LineWidth(1), RooFit.LineColor(kYellow))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Bbar"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('CombBkgEPDF_t'),
	    RooFit.LineWidth(3), RooFit.LineColor(kYellow), RooFit.LineStyle(kDashed))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Untagged"),
            RooFit.Slice(wksp.cat("qf"), "h+"),
	    RooFit.Components('CombBkgEPDF_t'),
	    RooFit.LineWidth(1), RooFit.LineColor(kGreen + 2))
    model.plotOn(frame,
            RooFit.Slice(wksp.cat("qt"), "Untagged"),
            RooFit.Slice(wksp.cat("qf"), "h-"),
	    RooFit.Components('CombBkgEPDF_t'),
	    RooFit.LineWidth(3), RooFit.LineColor(kGreen + 2), RooFit.LineStyle(kDashed))

    if not signalModelOnly :
	# put non-signal components here
	pass

    # plot model itself
    model.plotOn(frame,
                  RooFit.LineColor(kBlue),
                  RooFit.Normalization(1., RooAbsReal.RelativeExpected))

    # put model parameters on plot
    model.paramOn(frame,
                   RooFit.Layout(0.56, 0.90, 0.85),
                   RooFit.Format('NEU', RooFit.AutoPrecision(2))
)

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
        pdfName = 'sigEPDF_t'
        pdf = comps.find(pdfName)
        curve = frame.findObject(pdfName + '_Norm[time]')
        if curve : leg.AddEntry(curve, pdf.GetTitle(), 'l')
        return leg, curve
    else :
        pdf1 = comps.find('sigEPDF_t')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'sigEPDF_t'
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
                   default = 'FitMeToolWS',
                   help = 'RooWorkspace name as stored in ROOT file'
)

#------------------------------------------------------------------------------

if __name__ == '__main__' :
    (options, args) = parser.parse_args()

    if len(args) != 1 :
        parser.print_help()
        exit(-1)

    FILENAME = (args[ 0 ])
    if not os.path.exists(FILENAME) :
        parser.error('ROOT file "%s" not found! Nothing plotted.' % FILENAME)
        parser.print_help()

    import ROOT
    from ROOT import gROOT, TFile, TH1F
    ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
    gROOT.SetBatch( True )
    from ROOT import TFile, TCanvas, gROOT, TLegend

    from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooTruthModel, RooDecay
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooAbsReal
    from ROOT import RooFit, FitMeTool

    from ROOT import CombBkgPTPdf
    from ROOT import BdPTAcceptance

    gROOT.SetStyle('Plain')

    f = TFile(FILENAME)

    w = f.Get(options.wsname)
    w.Print('v')
    if not w :
        parser.error('Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      (options.wsname, FILENAME))

    f.Close()

    time = w.var('time')
    time.setRange(-.5, 8.)
    mass = w.var('mass')
    mass.setRange(5.0, 6.0)

    modelPDF = w.pdf('TotEPDF')
    if not modelPDF: modelPDF = w.pdf('TotPDF')
    dataset = w.data('agglomeration')
    if not dataset : dataset = w.data('TotEPDF_tData')
    if not dataset : dataset = w.data('sigEPDF_tData')
    if not dataset : dataset = w.data('TotPDF_tData')
    if not dataset : dataset = w.data('sigPDF_tData')
    print modelPDF
    print dataset

    if not (modelPDF and dataset) :
        w.Print('v')
        exit(1)

    canvas = TCanvas('TimeCanvas', 'Propertime canvas')
    canvas.SetTitle('Fit in propertime')
    canvas.cd()

    frame_t = time.frame()
    frame_m = mass.frame()

    frame_t.SetTitle('Fit in reconstructed %s propertime' % bName)

    frame_t.GetXaxis().SetLabelSize(0.03)
    frame_t.GetYaxis().SetLabelSize(0.03)

    if plotData : plotDataSet(dataset, frame_t)

    print '##### modelPDF is'
    print modelPDF
    if plotModel : plotFitModel(modelPDF, frame_t, w)

    #leg, curve = legends(modelPDF, frame_t)
    #frame_t.addObject(leg)

    frame_t.Draw()

    canvas.Update()
    canvas.SetLogy(True)
    canvas.Print(FILENAME + '.time.eps')

    if plotData : plotDataSet(dataset, frame_m)
    if plotModel : plotFitModel(modelPDF, frame_m, w)
    frame_m.Draw()

    canvas.Update()
    canvas.SetLogy(False)
    canvas.Print(FILENAME + '.mass.eps')
#------------------------------------------------------------------------------
