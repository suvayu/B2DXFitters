#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot the Bd -> D pi mass models                          #
#                                                                             #
#   Example usage:                                                            #
#      python -i plotBs2DsKMassModels.py                                      #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 02 / 2012                                                    #
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

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{s}'

#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser( _usage )

parser.add_option( '-w', '--workspace',
                                      dest = 'wsname',
                                      metavar = 'WSNAME',
                                      default = 'FitMeToolWS',
                                      help = 'RooWorkspace name as stored in ROOT file'
                                      )

parser.add_option( '-m', '--sample',
                                      dest = 'sample',
                                      metavar = 'SAMPLE',
                                      default = 'up',
                                      help = 'Sample: choose up or down '
                                      )

parser.add_option( '-v', '--variable',
                                      dest = 'var',
                                      default = 'lab0_MassFitConsD_M',
                                      help = 'set observable '
                                      )
#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, sample ) :

    bin = 100
    if sample == "both":
        dataset.plotOn( frame,
                        RooFit.Cut("sample==sample::up || sample==sample::down"),
                        RooFit.Binning( bin ) )
    elif sample == "up":
        dataset.plotOn( frame,
                        RooFit.Cut("sample==sample::up"),
                        RooFit.Binning( bin ) )
                                                
    elif sample == "down":
         dataset.plotOn( frame,
                         RooFit.Cut("sample==sample::down"),
                         RooFit.Binning( bin ) )
    else:
        print "[ERROR] Wrong sample!"
                                                                         
                
    dataset.statOn( frame,
                    RooFit.Layout( 0.10, 0.45, 0.90  ),
                    RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame, sam, var) :
    #if debug :
    
    print "model"    
    model.Print( 't' )

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    nameTot = TString("FullPdf")
    if sam == "both":
        nameSig1 = TString("DblCBPDFdown_CB1,DblCBPDFup_CB1")
        nameSig2 = TString("DblCBPDFdown_CB2,DblCBPDFup_CB2")
    elif sam == "down" :
        nameSig1 = TString("DblCBPDFdown_CB1")
        nameSig2 = TString("DblCBPDFdown_CB2")
    elif sam == "up":
        nameSig1 = TString("DblCBPDFup_CB1")
        nameSig2 = TString("DblCBPDFup_CB2")
    else:
        print "[ERROR] Wrong sample"
        exit(0)
                
    
    #model.plotOn( frame,
    #              RooFit.Components(nameTot.Data()),
    #              RooFit.LineColor(kBlue-6),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )
    
    model.plotOn( frame,
                  RooFit.Components(nameSig1.Data()),
                  RooFit.LineColor(kBlue-10),
                  RooFit.LineStyle(7),
                  RooFit.LineWidth(4),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
     
    model.plotOn( frame,
                  RooFit.Components(nameSig2.Data()),
                  RooFit.LineColor(kMagenta-10),
                  RooFit.LineStyle(kDashed),
                  RooFit.LineWidth(4),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kBlue-6),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
     
#    model.paramOn( frame,
#                   RooFit.Layout( 0.56, 0.90, 0.85 ),
#                   RooFit.Format( 'NEU', RooFit.AutoPrecision( 2 ) )
#                   )

#    decays = ["Combinatorial",
#              "B^{0}#rightarrow D^{-}_{s}K^{+}"]
#    compColor = [kBlack, kGray]                 
    #decayNameLatex="B^{0}_{s}#rightarrow D^{#pm}_{s}K^{#mp}"

    #where = [0.55,0.30,0.87,0.61]
#    legend = TLegend( 0.13, 0.57, 0.44, 0.87 )
    ## Signal
#    l1 = TLine()
#    l1.SetLineColor(kRed)
#    l1.SetLineStyle(kDashed)
#    legend.AddEntry(l1, "Signa", "L")
    #hs = []

    #for cC in xrange(len(compColor)):
    #    print 'mamma',decays[cC], compColor[cC]
    #    hs.append(TH1F("h%s"%(cC),"h%s"%(cC),10,0,1))
    #    hs[-1].SetFillColor(compColor[cC])
    #    hs[-1].SetFillStyle(1001)
    #    legend.AddEntry(hs[-1], "%s"%decays[cC], "f")
    #legend.SetTextFont(12)
#    legend.Draw()                                                                        

    
    #stat = frame.findObject( 'data_statBox' )
    #if not stat:
    #    statTS = TString("TotEPDF_m_")+sam+TString("_Data_statBox")
    #    stat = frame.findObject( statTS.Data() )
    #if stat :
    #    stat.SetTextSize( 0.025 )
    #ptTS = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    #pt = frame.findObject( ptTS.Data() )
    #if pt :
    #    pt.SetTextSize( 0.02 )
    # Legend of EPDF components

    #leg = TLegend( 0.13, 0.57, 0.44, 0.87 )
    #leg.SetFillColor( 0 )
    #leg.SetTextSize( 0.02 )

    #comps = model.getComponents()

    #pdf = comps.find(nameSig.Data())
    #pdfNameTS = TString("TotEPDF_m_")+sam+TString("_Norm[")+var+TString("]_Comp[")+nameSig.Data()+TString("]") 
    #pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bs2DsPiEPDF'

    #h=TH1F(nameSig.Data(),nameSig.Data(),10,0,1)
    #h.SetFillColor(kRed)
    #h.SetFillStyle(1001)

    #curve = frame.findObject( pdfNameTS.Data() )

    #decay = TString("Signal")
    #leg.AddEntry(curve, decay.Data(), 'l' )
    #leg.Draw()
    
    #leg.AddEntry( curve, pdf.GetTitle(), 'l' )
    #frame.addObject( leg )
    #pdf = comps.find( 'CombBkgEPDF_m' )
    #pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'CombBkgEPDF_m'
    #curve5 = frame.findObject( pdfName )
    #leg.AddEntry( curve5, pdf.GetTitle(), 'l' )
    #frame.addObject( leg )
    #pdf = comps.find( 'SigEPDF' )
    #pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'SigEPDF'
    #curve6 = frame.findObject( pdfName )
    #leg.AddEntry( curve6, pdf.GetTitle(), 'l' )
    #frame.addObject( leg )
    #pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'CombBkgEPDF_m,Bs2DsPiEPDF'
    #curve7 = frame.findObject( pdfName )
    #leg.AddEntry( curve7, 'All but %s' % pdf.GetTitle(), 'f' )
    #curve7.SetLineColor(0)

#------------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) != 1 :
        parser.print_help()
        exit( -1 )

    FILENAME = ( args[ 0 ] )
    if not exists( FILENAME ) :
        parser.error( 'ROOT file "%s" not found! Nothing plotted.' % FILENAME )
        parser.print_help()

    from ROOT import *
    #from ROOT import TFile, TCanvas, gROOT, TLegend, TString, TLine, TH1F, TBox, TPad
    #from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack, kGray, kViolet
    #from ROOT import RooFit, RooRealVar, RooAbsReal, RooCategory, RooArgSet, RooAddPdf, RooArgList
    gROOT.SetStyle( 'Plain' )    
    gROOT.SetBatch( False )
    
    
    f = TFile( FILENAME )

    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )
    
    f.Close()
    mVarTS = TString(options.var)    
    mass = w.var(mVarTS.Data())
    sam = TString(options.sample)
     
    w.Print('v')
    #exit(0)
        
       
    dataName = TString("combData")


    if sam == "up":
        print "Sample up"
        w.factory("SUM:FullPdf(nSigEvts_up*SigEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up]")
    elif sam == "down":
        print "Sample down"
        w.factory("SUM:FullPdf(nSigEvts_down*SigEPDF_down)")
        pullname2TS = TString("h_combData_Cut[sample==sample::down]")
    elif sam == "both":
        print "Sample both"
        w.factory("SUM:FullPdf(nSigEvts_down*SigEPDF_down,nSigEvts_up*SigEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up || sample==sample::down]")
    else:
        print "[ERROR] Wrong sample"
        exit(0)

    totName = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )
    dataset = w.data( dataName.Data() )
            
    if not ( modelPDF and dataset ) :
        print "Cos sie zepsulo?"
        w.Print( 'v' )
        exit( 0 )
    #w.Print('v')
    #exit(0)
#    canvas = TCanvas( 'MassCanvas', 'Mass canvas', 1200, 800 )
#    canvas.SetTitle( 'Fit in mass' )
#    canvas.cd()
    
    frame_m = mass.frame()
    
    frame_m.SetTitle( 'Fit in reconstructed %s mass' % bName )
    
    frame_m.GetXaxis().SetLabelSize( 0.03 )
    frame_m.GetYaxis().SetLabelSize( 0.03 )
           
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS )
    if plotData : plotDataSet( dataset, frame_m, sam )
    
    gStyle.SetOptLogy(1)
    canvas = TCanvas("canvas", "canvas", 600, 700)
    pad1 =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.20)
    pad1.Draw()
    pad2.Draw()
    pad1.cd()
    frame_m.Draw()
    pad1.Update()

    frame_m.Print("v")
    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[FullPdf]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())

    pad2.SetLogy(0)
    pad2.cd()
    gStyle.SetOptLogy(0)
            

    axisX = pullHist.GetXaxis()
    axisX.Set(100,5000,5500)
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
    #range = max-min
    #zero = max/range
    #print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
                                
    #max = 4
    #min = -3
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    graph.SetPoint(1,5000,0)
    graph.SetPoint(2,5500,0)
    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    graph2.SetPoint(1,5000,-3)
    graph2.SetPoint(2,5500,-3)
    graph2.SetLineColor(kRed)
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    graph3.SetPoint(1,5000,3)
    graph3.SetPoint(2,5500,3)
    graph3.SetLineColor(kRed)
                                                                 

    #pad2.SetLogy(0)
    #pad2.cd()
    #gStyle.SetOptLogy(0)
    pullHist.Draw("ap")
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
            
    pad2.Update()
    canvas.Update()
                                                                                

      
#    frame_m.Draw()
    n = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    pt = canvas.FindObject( n.Data() )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()
    canName = TString("mass_Signal_")+sam+TString(".pdf")
    canvas.Print(canName.Data())
    
#------------------------------------------------------------------------------
