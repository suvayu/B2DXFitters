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
#import os, sys, gc

import GaudiPython
GaudiPython.loaddict( 'B2DXFittersDict' )
from ROOT import *
from ROOT import RooCruijff

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{d}'

Dmass_dw = 2200
Dmass_up = 2380

Bmass_dw = 5400
Bmass_up = 5800
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

    if sample == "both":
        dataset.plotOn( frame,
                        RooFit.Cut("sample==sample::up || sample==sample::down"),
                        RooFit.Binning( 70 ) )
    elif sample == "up":
        dataset.plotOn( frame,
                        RooFit.Cut("sample==sample::up"),
                        RooFit.Binning( 70 ) )
                                                
    elif sample == "down":
         dataset.plotOn( frame,
                         RooFit.Cut("sample==sample::down"),
                         RooFit.Binning( 70 ) )
    else:
        print "[ERROR] Wrong sample!"
                                                                         
                
   # dataset.statOn( frame,
   #                 RooFit.Layout( 0.10, 0.45, 0.90  ),
   #                 RooFit.What('N') )

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
        nameSig  = TString("SigEPDF_down,SigEPDF_up") 
        nameBkg = TString("BkgEPDF_down,BkgEPDF_up")
                        
    elif sam == "down" :
        nameSig  = TString("SigEPDF_down")
        nameBkg = TString("BkgEPDF_down")
         
    elif sam == "up":
        nameSig  = TString("SigEPDF_up")
        nameBkg = TString("BkgEPDF_up")
                                        
    else:
        print "[ERROR] Wrong sample"
        exit(0)

       
    model.plotOn( frame,
                  RooFit.Components(nameBkg.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kRed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    
    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kMagenta-2),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame,
                  RooFit.Components(nameSig.Data()),
                  RooFit.LineColor(kBlue),
                  RooFit.LineStyle(7),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
          
#    model.paramOn( frame,
#                   RooFit.Layout( 0.56, 0.90, 0.85 ),
#                   RooFit.Format( 'NEU', RooFit.AutoPrecision( 2 ) )
#                   )

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

    #from ROOT import *
    #from ROOT import RooCruijff, TCanvas, TPad
    
    #from ROOT import TFile, TCanvas, gROOT, TLegend, TString, TLine, TH1F, TBox, TPad
    #from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack, kGray, kViolet
    #from ROOT import RooFit, RooRealVar, RooAbsReal, RooCategory, RooArgSet, RooAddPdf, RooArgList
    gROOT.SetStyle( 'Plain' )    
   
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    
    pdf = RooCruijff()
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
        w.factory("SUM:FullPdf(nSig_up_Evts*SigEPDF_up,nBkg_up_Evts*BkgEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up]")
    elif sam == "down":
        print "Sample down"
        w.factory("SUM:FullPdf(nSig_down_Evts*SigEPDF_down,nBkg_down_Evts*BkgEPDF_down)")
        pullname2TS = TString("h_combData_Cut[sample==sample::down]")
    elif sam == "both":
        print "Sample both"
        w.factory("SUM:FullPdf(nSig_down_Evts*SigEPDF_down,nSig_up_Evts*SigEPDF_up,nBkg_down_Evts*BkgEPDF_down,nBkg_up_Evts*BkgEPDF_up)")
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
   
    frame_m = mass.frame()
       
    frame_m.SetTitle("") #'Fit in reconstructed %s mass' % bName )
    
    frame_m.GetXaxis().SetLabelSize( 0.03 )
    frame_m.GetYaxis().SetLabelSize( 0.03 )
    if ( mVarTS == "lab0_MassFitConsD_M"):
        frame_m.GetXaxis().SetTitle("m(#Lambda_{b}) [MeV/c^{2}]")
    else:
        frame_m.GetXaxis().SetTitle("m(#Lambda_{c}) [MeV/c^{2}]")
    frame_m.GetYaxis().SetTitleFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 )
    frame_m.SetLabelFont(132)
    frame_m.SetTitleFont(132)
                 
           
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS )
    if plotData : plotDataSet( dataset, frame_m, sam )
    
    canvas = TCanvas("canvas", "canvas",700, 700)
    canvas.SetTitle( 'Fit in mass' )
    canvas.cd()

    pad1 =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.20)
    pad1.Draw()
    pad2.Draw()

    if ( mVarTS == "lab0_MassFitConsD_M"):
        legend = TLegend( 0.60, 0.50, 0.85, 0.85 )
    else:
        legend = TLegend( 0.12, 0.60, 0.35, 0.85 )
    legend.SetTextSize(0.03)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetHeader("LHCb L_{int}=1fb^{-1}")


    l1 = TLine()
    l1.SetLineColor(kBlue)
    l1.SetLineWidth(4)
    l1.SetLineStyle(7)
    legend.AddEntry(l1, "Signal #Lambda_{B} #rightarrow #Lambda_{c}#pi", "L")


    h1=TH1F("Combinatorial","Combinatorial",5,0,1)
    h1.SetFillColor(kRed)
    h1.SetFillStyle(1001)
    legend.AddEntry(h1, "Combinatorial", "f")
    
    
    pad1.cd()
    frame_m.Draw()
    legend.Draw("same")
    pad1.Update()
    
    frame_m.Print("v")
    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[FullPdf]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    pullHist.SetTitle("")
    
    #pullHist.SetMaximum(5800.00)
    #pullHist.SetMinimum(5100.00)
    axisX = pullHist.GetXaxis()
    if ( mVarTS == "lab0_MassFitConsD_M"):
        axisX.Set(70,Bmass_dw,Bmass_up)
    else:
        axisX.Set(70,Dmass_dw,Dmass_up)
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
    range = max-min
    zero = max/range
    print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
    #line = TLine(0.11,0.31,0.99,0.20)
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M"):
        graph.SetPoint(1,Bmass_dw,0)
        graph.SetPoint(2,Bmass_up,0)
    else:
        graph.SetPoint(1,Dmass_dw,0)
        graph.SetPoint(2,Dmass_up,0)
    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M"):
        graph2.SetPoint(1,Bmass_dw,-3)
        graph2.SetPoint(2,Bmass_up,-3)
    else:
        graph2.SetPoint(1,Dmass_dw,-3)
        graph2.SetPoint(2,Dmass_up,-3)
    graph2.SetLineColor(kRed)
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M"):
        graph3.SetPoint(1,Bmass_dw,3)
        graph3.SetPoint(2,Bmass_up,3)
    else:
        graph3.SetPoint(1,Dmass_dw,3)
        graph3.SetPoint(2,Dmass_up,3)
    graph3.SetLineColor(kRed)
                                            
    
    pad2.SetLogy(0)
    pad2.cd()
    gStyle.SetOptLogy(0)
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
    canName = TString("mass_LbLcPi_")+mVarTS+TString("_")+sam+TString(".pdf")
    canvas.SaveAs(canName.Data())
    canNamePng = TString("mass_LbLcPi_")+mVarTS+TString("_")+sam+TString(".png")
    canvas.SaveAs(canNamePng.Data())
    canNameROOT = TString("mass_LbLcPi_")+mVarTS+TString("_")+sam+TString(".root")
    canvas.SaveAs(canNameROOT.Data())
        
    
        
#------------------------------------------------------------------------------
