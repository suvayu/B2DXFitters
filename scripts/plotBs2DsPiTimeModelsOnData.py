
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
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from os.path  import exists

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------
def in_gdb():
    import os
    proclist = dict(
        (l[0], l[1:]) for l in (lraw.replace('\n', '').replace('\r','').split()
                                for lraw in os.popen('ps -o pid= -o ppid= -o comm=').readlines()
                                )
        )
    pid = os.getpid()
    while pid in proclist:
        if 'gdb' in proclist[pid][1]: return True
        pid = proclist[pid][0]
        return False
    
    
if in_gdb():
    # when running in a debugger, we want to make sure that we do not
    # handle any signals, so the debugger can catch SIGSEGV and friends,
    # and we can poke around
    ROOT.SetSignalPolicy(ROOT.kSignalFast)
    ROOT.gEnv.SetValue('Root.Stacktrace', '0')

import GaudiPython
GaudiPython.loaddict( 'B2DXFittersDict' )
from ROOT import *
from ROOT import RooCruijff

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
pdfToPlot = 'time_signal' #signal_TimeTimeerrPdf'
#fileToWriteOut = 'time_DsPi_BDTG123.pdf' 
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
    terr                                = wksp.var('lab0_LifetimeFit_ctauErr')
    dataset                             = w.data(dataSetToPlot)
    obs = dataset.get()
    obs.Print("v")
    cat2 = obs.find('qf')
    cat3 = obs.find('qt')
                

    # plot model itself
    fr = model.plotOn(frame,
                      RooFit.ProjWData(RooArgSet(cat2,cat3),dataset),
                      RooFit.LineColor(kBlue+3))

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

    from ROOT import TFile, TCanvas, gROOT, TLegend
    import GaudiPython
    GaudiPython.loaddict('B2DXFittersDict')

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
    from ROOT import PowLawAcceptance, Inverse,DecRateCoeff, RooHistPdf, RooUniform, MistagCalibration
    from ROOT import RooBinnedPdf, PowLawAcceptance
        

    gROOT.SetStyle('Plain')
    #gROOT.SetBatch(False)

    
    f = TFile(FILENAME)

    w = f.Get(options.wsname)
    if not w :
        parser.error('Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      (options.wsname, FILENAME))

    f.Close()
    time = w.var('lab0_LifetimeFit_ctau')
    #time.setRange(timeDown,timeUp)   
 
    modelPDF = w.pdf(pdfToPlot) 
    if modelPDF:
        print modelPDF.GetName()
    dataset  = w.data(dataSetToPlot) 
    if dataset:
        print dataset.GetName()
        
    print gROOT.GetVersion()
    
    if not (modelPDF and dataset) :
        w.Print('v')
        exit(1)

    
    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    canvas.cd()
       
    frame_t = time.frame()
    frame_t.SetTitle('')
 
    frame_t.GetXaxis().SetLabelSize(0.05)
    frame_t.GetYaxis().SetLabelSize(0.05)
    frame_t.GetXaxis().SetTitle('#font[12]{#tau (B_{s} #rightarrow D_{s} #pi) [ps]}')
    frame_t.GetXaxis().SetTitleSize(0.05)
    frame_t.GetYaxis().SetTitleSize(0.05)
    frame_t.GetXaxis().SetTitleOffset(0.95)
    frame_t.GetYaxis().SetTitleOffset(0.85)
    frame_t.GetXaxis().SetLabelFont( 132 )
    frame_t.GetYaxis().SetLabelFont( 132 )
        

    plotDataSet(dataset, frame_t)
    
    print '##### modelPDF is'
    print modelPDF
    if plotModel :
        plotFitModel(modelPDF, frame_t, w)

    frame_t.GetYaxis().SetRangeUser(0.001,5000)

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
    
    
    padgraphics =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    padpull =  TPad("pad2","pad2",0.01,0.01,0.99,0.21)
    padgraphics.Draw()
    padpull.Draw()
                
    
    #padgraphics.SetLogy(1)
    padgraphics.cd()
    #gStyle.SetOptLogy(1)
            
    frame_t.Draw()
    legend.Draw("same")
    
    padgraphics.Update()
    
    padpull.SetLogy(0)
    padpull.cd()
    gStyle.SetOptLogy(0)
      
    pullHist = frame_t.pullHist()
    pullHist.SetMaximum(4.00)
    pullHist.SetMinimum(-4.00)
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
    
    padpull.Update()
    canvas.Update()
    
    chi2 = frame_t.chiSquare() 
    chi22 = frame_t.chiSquare(1)
      
    print "chi2: %f"%(chi2)
    print "chi22: %f"%(chi22)
    
    frame_t.GetYaxis().SetRangeUser(0.001,3000)
    #padgraphics.SetLogy()

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
