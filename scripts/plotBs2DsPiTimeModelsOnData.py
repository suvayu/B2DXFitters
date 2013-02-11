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


dataSetToPlot  = 'dataSet_time_Bs2DsK'
fileToWriteOut = 'time_DsK.pdf' 
#------------------------------------------------------------------------------
def plotDataSet(dataset, frame) :
    dataset.plotOn(frame,RooFit.Binning(74))

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
                      RooFit.LineColor(kBlue)),

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
parser.add_option( '--pull',
                   dest = 'pull',
                   action = 'store_true',
                   default = False,
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
    from ROOT import RooFit, FitMeTool, TGraph, TPad

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
    time = w.var('lab0_LifetimeFit_ctau')
    time.setRange(0.2,15.)   
 
    modelPDF = w.pdf('time_signal')
    dataset  = w.data(dataSetToPlot) 
    if dataset: print dataset.GetName()

    if not (modelPDF and dataset) :
        w.Print('v')
        exit(1)

    if ( not options.pull ):
        canvas = TCanvas('TimeCanvas', 'Propertime canvas', 800, 600)
        canvas.cd()
    else:
        canvas = TCanvas('TimeCanvas', 'Propertime canvas', 1000, 300)
    
    frame_t = time.frame()
   
    frame_t.SetTitle('')
 
    frame_t.GetXaxis().SetLabelSize(0.06)
    frame_t.GetYaxis().SetLabelSize(0.06)
    frame_t.GetXaxis().SetTitle('#tau (B_{s} #rightarrow D_{s} K) [ps]')
    frame_t.GetXaxis().SetTitleSize(0.06)
    frame_t.GetYaxis().SetTitleSize(0.06)
    frame_t.GetXaxis().SetTitleOffset(0.95)
    frame_t.GetYaxis().SetTitleOffset(0.9)

    #if plotData :
    plotDataSet(dataset, frame_t)
    
    print '##### modelPDF is'
    print modelPDF
    if plotModel :
        plotFitModel(modelPDF, frame_t, w)

    #leg, curve = legends(modelPDF, frame_t)
    #frame_t.addObject(leg)

    padgraphics = TPad("padgraphics","",0.005,0.355,0.995,0.995)
    padgraphics.Draw()
    padgraphics.cd()
    frame_t.Draw()

    from ROOT import TLatex

    myLatex = TLatex()
    myLatex.SetTextFont(132)
    myLatex.SetTextColor(1)
    myLatex.SetTextSize(0.04)
    myLatex.SetTextAlign(12)
    myLatex.SetNDC(1)
    myLatex.SetTextSize(0.065)
    myLatex.DrawLatex(0.65, 0.725, 
                 "#splitline{#splitline{LHCb}{Preliminary 1 fb^{-1}}}{}")

    if ( options.pull ):
        canvas.cd()
        padpull = TPad("padpull","",0.005,0.005,0.995,0.995)
        padpull.Draw() 
        padpull.cd()

        pullHist = frame_t.pullHist()

        #pullHist.GetXaxis().SetTitle('time [ps]')
        #pullHist.GetXaxis().SetTitleSize(0.075)

        pullHist.SetMaximum(4.00)
        pullHist.SetMinimum(-4.00)
        axisX = pullHist.GetXaxis()
        axisX.Set(100,0,15)
        axisX.SetTitle('#tau (B_{s} #rightarrow D_{s} K) [ps]')   
        axisX.SetTitleSize(0.150)
        axisX.SetTitleFont(132)
        axisX.SetLabelSize(0.150)
        axisX.SetLabelFont(132)
        axisX.SetTitle        
    
        axisY = pullHist.GetYaxis()
        max = axisY.GetXmax()
        min = axisY.GetXmin()
        axisY.SetLabelSize(0.150)
        axisY.SetLabelFont(132)
        axisY.SetNdivisions(5)        
                      
        axisX = pullHist.GetXaxis()
        maxX = axisX.GetXmax()
        minX = axisX.GetXmin()
        axisX.SetLabelSize(0.150)
        
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

        pullHist.SetTitle("");

        pullHist.Draw("AP")
        graph.Draw("same")
        graph2.Draw("same")
        graph3.Draw("same")
      

    chi2 = frame_t.chiSquare() 
    chi22 = frame_t.chiSquare(1)
      
    print "chi2: %f"%(chi2)
    print "chi22: %f"%(chi22)
    
    frame_t.GetYaxis().SetRangeUser(0.001,5000)
    padgraphics.SetLogy()
    canvas.Print(fileToWriteOut)

#------------------------------------------------------------------------------
