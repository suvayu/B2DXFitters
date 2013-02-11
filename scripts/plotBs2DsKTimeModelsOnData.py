#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot the Bd -> D pi time models                          #
#                                                                             #
#   Example usage:                                                            #
#      python -i plotBdTimeModels.py                                          #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 01 / 06 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from os.path  import exists

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
#    dataset.statOn(frame,
#                   RooFit.Layout(0.56, 0.90, 0.90),
#                   RooFit.What('N'))

#------------------------------------------------------------------------------
def plotFitModel(model, frame, wksp) :
    if debug :
        model.Print('t')
        frame.Print('v')

    '''
    model.plotOn(frame, RooFit.Cut("lab0_BsTaggingTool_TAGDECISION_OS ==1 && lab1_ID ==1 "),
	    RooFit.Components('tpdfSig'),
    	    RooFit.LineWidth(1), RooFit.LineColor(kRed))
    model.plotOn(frame, RooFit.Cut("lab0_BsTaggingTool_TAGDECISION_OS ==-1 && lab1_ID ==-1 "),
	    RooFit.Components('tpdfSig'),
    	    RooFit.LineWidth(1), RooFit.LineColor(kMagenta-2))
    model.plotOn(frame,  RooFit.Cut("lab0_BsTaggingTool_TAGDECISION_OS ==1 && lab1_ID ==-1 "),
	    RooFit.Components('tpdfSig'),
    	    RooFit.LineWidth(3), RooFit.LineColor(kRed), RooFit.LineStyle(kDashed))
    model.plotOn(frame, RooFit.Cut("lab0_BsTaggingTool_TAGDECISION_OS ==-1 && lab1_ID ==1 ") ,
	    RooFit.Components('tpdfSig'),
    	    RooFit.LineWidth(3), RooFit.LineColor(kMagenta-2), RooFit.LineStyle(kDashed))
    model.plotOn(frame, RooFit.Cut("(lab0_BsTaggingTool_TAGDECISION_OS == 0) && (lab1_ID > 0) "), 
	    RooFit.Components('tpdfSig'),
	    RooFit.LineWidth(1), RooFit.LineColor(kGreen + 1))
    model.plotOn(frame, RooFit.Cut("(lab0_BsTaggingTool_TAGDECISION_OS == 0) && (lab1_ID < 0) "),
	    RooFit.Components('tpdfSig'),
	    RooFit.LineWidth(3), RooFit.LineColor(kGreen + 1), RooFit.LineStyle(kDashed))
    '''
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Bs2Ds-K+"),
#	    RooFit.Components('Bs2DsKEPDF'),
#    	    RooFit.LineWidth(1), RooFit.LineColor(kOrange))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Bs2Ds+K-"),
#	    RooFit.Components('Bs2DsKEPDF'),
#    	    RooFit.LineWidth(1), RooFit.LineColor(kMagenta))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Bsbar2Ds+K-"),
#	    RooFit.Components('Bs2DsKEPDF'),
#    	    RooFit.LineWidth(3), RooFit.LineColor(kOrange), RooFit.LineStyle(kDashed))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Bsbar2Ds-K+"),
#	    RooFit.Components('Bs2DsKEPDF'),
#    	    RooFit.LineWidth(3), RooFit.LineColor(kMagenta), RooFit.LineStyle(kDashed))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Untagged2Ds+K-"),
#	    RooFit.Components('Bs2DsKEPDF'),
#	    RooFit.LineWidth(1), RooFit.LineColor(kCyan + 1))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Untagged2Ds-K+"),
#	    RooFit.Components('Bs2DsKEPDF'),
#	    RooFit.LineWidth(3), RooFit.LineColor(kCyan + 1), RooFit.LineStyle(kDashed))

#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Bs2Ds+K-"),
#	    RooFit.Components('CombBkgEPDF_t'),
#	    RooFit.LineWidth(1), RooFit.LineColor(kYellow))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Bs2Ds-K+"),
#	    RooFit.Components('CombBkgEPDF_t'),
#	    RooFit.LineWidth(3), RooFit.LineColor(kYellow), RooFit.LineStyle(kDashed))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Bsbar2Ds+K-"),
#	    RooFit.Components('CombBkgEPDF_t'),
#	    RooFit.LineWidth(1), RooFit.LineColor(kYellow))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Bsbar2Ds-K+"),
#	    RooFit.Components('CombBkgEPDF_t'),
#	    RooFit.LineWidth(3), RooFit.LineColor(kYellow), RooFit.LineStyle(kDashed))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Untagged2Ds+K-"),
#	    RooFit.Components('CombBkgEPDF_t'),
#	    RooFit.LineWidth(1), RooFit.LineColor(kGreen + 2))
#    model.plotOn(frame, RooFit.Slice(wksp.cat("decayPath"), "Untagged2Ds-K+"),
#	    RooFit.Components('CombBkgEPDF_t'),
#	    RooFit.LineWidth(3), RooFit.LineColor(kGreen + 2), RooFit.LineStyle(kDashed))

    if not signalModelOnly :
	# put non-signal components here
	    pass

    # plot model itself
    model.plotOn(frame,
                  RooFit.LineColor(kBlue)),
                  #RooFit.Normalization(1., RooAbsReal.RelativeExpected))

    # put model parameters on plot

    #model.paramOn(frame,
    #               RooFit.Layout(0.56, 0.90, 0.85),
    #               RooFit.Format('NEU', RooFit.AutoPrecision(2))
#)

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
                   default = 'FitMeToolWS',
                   help = 'RooWorkspace name as stored in ROOT file'
)

parser.add_option( '--pull',
                   dest = 'pull',
                   default = 'no',
                   help = 'Plot pull: choose no or yes'
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
    import GaudiPython
    GaudiPython.loaddict('B2DXFittersDict')

    from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooTruthModel, RooDecay
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooAbsReal
    from ROOT import RooFit, FitMeTool, TGraph

    from ROOT import CombBkgPTPdf
    from ROOT import BdPTAcceptance
    from ROOT import RooBlindTools

    gROOT.SetStyle('Plain')
    gROOT.SetBatch(False)

    
    f = TFile(FILENAME)

    w = f.Get(options.wsname)
    if not w :
        parser.error('Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      (options.wsname, FILENAME))

    f.Close()
#    exit(0)
    time = w.var('lab0_LifetimeFit_ctau')
   # time.setRange(-.5, 8.)
   # mass = w.var('mass')
   # mass.setRange(5.0, 6.0)

    
    modelPDF = w.pdf('TotEPDF_t')
    if not modelPDF: modelPDF = w.pdf('SigEPDF_t')
    if not modelPDF: modelPDF = w.pdf('SigEPDF') 
    if not modelPDF: modelPDF = w.pdf('tpdfSig') 
    if not modelPDF: modelPDF = w.pdf('time_signal')
    if modelPDF: print modelPDF.GetName()
    dataset = w.data('combData')
    if not dataset : dataset = w.data('TotEPDF_tData')
    if not dataset : dataset = w.data('SigEPDF_tData')
    if not dataset : dataset = w.data('TotPDF_tData')
    if not dataset : dataset = w.data('SigPDF_tData')
    if not dataset : dataset = w.data('dataSet_time_Bs2DsK') 
    if dataset: print dataset.GetName()

    if not (modelPDF and dataset) :
        w.Print('v')
        exit(1)

    if ( options.pull == "no"):
        canvas = TCanvas('TimeCanvas', 'Propertime canvas', 800, 600)
    else:
        canvas = TCanvas('TimeCanvas', 'Propertime canvas', 800, 200)
                
    canvas.SetTitle('Fit in propertime')
    canvas.cd()
    
    frame_t = time.frame()
   
#    frame_t.SetTitle('Fit in reconstructed %s propertime' % bName)
    frame_t.SetTitle("")

    frame_t.GetXaxis().SetLabelSize(0.03)
    frame_t.GetYaxis().SetLabelSize(0.03)
    frame_t.GetXaxis().SetTitle('time [ps]')

    #if plotData :
    plotDataSet(dataset, frame_t)

    print '##### modelPDF is'
    print modelPDF
    if plotModel : plotFitModel(modelPDF, frame_t, w)

    #leg, curve = legends(modelPDF, frame_t)
    #frame_t.addObject(leg)

    if ( options.pull == "no" ):
        frame_t.Draw()
    else:
        pullHist = frame_t.pullHist()
        
        pullHist.SetMaximum(4.00)
        pullHist.SetMinimum(-4.00)
        axisX = pullHist.GetXaxis()
        axisX.Set(100,0,15)
        
        axisY = pullHist.GetYaxis()
        max = axisY.GetXmax()
        min = axisY.GetXmin()
        axisY.SetLabelSize(0.10)
        axisY.SetNdivisions(5)
        
        
        axisX = pullHist.GetXaxis()
        maxX = axisX.GetXmax()
        minX = axisX.GetXmin()
        axisX.SetLabelSize(0.10)
        
        range = max-min
        zero = max/range
        print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
        print "maxX: %s, minX: %s"%(maxX,minX)
        
        graph = TGraph(2)
        graph.SetMaximum(max)
        graph.SetMinimum(min)
        graph.SetPoint(1,0,0)
        graph.SetPoint(2,15,0)
        graph2 = TGraph(2)
        graph2.SetMaximum(max)
        graph2.SetMinimum(min)
        graph2.SetPoint(1,0,-3)
        graph2.SetPoint(2,15,-3)
        graph2.SetLineColor(kRed)
        graph3 = TGraph(2)
        graph3.SetMaximum(max)
        graph3.SetMinimum(min)
        graph3.SetPoint(1,0,3)
        graph3.SetPoint(2,15,3)
        graph3.SetLineColor(kRed)

        pullHist.SetTitle("")
        
        pullHist.Draw("ap")
        graph.Draw("same")
        graph2.Draw("same")
        graph3.Draw("same")

    chi2 = frame_t.chiSquare();
       
    print "chi2: %f"%(chi2)
    
    
                                                                                                                
    canvas.Update()
    frame_t.GetYaxis().SetRangeUser(0.001,2500)
    if ( options.pull == "no" ):
        canvas.SetLogy(True)
        canvas.Print('time_DsK.pdf')
    else:
        canvas.Print('time_pull_DsK.pdf')
                

    #if plotData : plotDataSet(dataset, frame_m)
    #if plotModel : plotFitModel(modelPDF, frame_m, w)
    #frame_m.Draw()

    #canvas.Update()
    #canvas.SetLogy(False)
    #canvas.Print(FILENAME + '.mass.eps')
#------------------------------------------------------------------------------
