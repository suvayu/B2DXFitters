#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot signals MC B->DPi, Bs->DsPi, Bs->DsK                #
#                                                                             #
#   Example usage:                                                            #
#      python plotSignal.py WS.root -m both --mode BDPi                       #
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
parser.add_option( '--mode',
                   dest = 'mode',
                   default = 'BsDsPi',
                   help = 'set observable '
                   )
parser.add_option( '--merge',
                   action = 'store_true',
                   dest = 'merge',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '-s', '--sufix',
                   dest = 'sufix',
                   metavar = 'SUFIX',
                   default = '',
                   help = 'Add sufix to output'
                   )



#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, sample, merge ) :

    bin = 100
    if sample == "both":
        if merge == True:
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::both"),
                            RooFit.Binning( bin ) )
        else:
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
                                                                         
       
#------------------------------------------------------------------------------
def plotFitModel( model, frame, sam, var, merge) :
    #if debug :
    
    print "model"    
    model.Print( 't' )
    obsTS = TString(var) 

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    nameTot = TString("FullPdf")
    if sam == "both":
        if merge == True:
            nameSig1 = TString("SigEPDF_both")
            nameSig2 = TString("SigEPDF_both")
                            
        else:
            if var == "lab2_MM":
                nameSig1 = TString("SigEPDF_down,SigEPDF_up")
                nameSig2 = TString("SigEPDF_down,SigEPDF_up")
            else:
                nameSig1 = TString("SigEPDF_down,SigEPDF_up")
                nameSig2 = TString("SigEPDF_down,SigEPDF_up")
            
    elif sam == "down" :
        if var == "lab2_MM":
            nameSig1 = TString("SigEPDF_down") #TString("DblGPDFdown_G1")
            nameSig2 = TString("SigEPDF_down") #TString("DblGPDFdown_G2")
        else:
            nameSig1 = TString("SigEPDF_down") #TString("DblCBPDFdown_CB1")
            nameSig2 = TString("SigEPDF_down") #TString("DblCBPDFdown_CB2")
    elif sam == "up":
        if var == "lab2_MM":
            nameSig1 =  TString("SigEPDF_up") #TString("DblGPDFup_G1")
            nameSig2 =  TString("SigEPDF_up") #TString("DblGPDFup_G2")
        else:    
            nameSig1 =  TString("SigEPDF_up") #TString("DblCBPDFup_CB1")
            nameSig2 =  TString("SigEPDF_up") #TString("DblCBPDFup_CB2")
    else:
        print "[ERROR] Wrong sample"
        exit(0)
                
    
        
    model.plotOn( frame,
                  RooFit.Components(nameSig1.Data()),
                  RooFit.LineColor(kBlue+2),
                  RooFit.LineWidth(4),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    ''' 
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
    '''  
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

    from ROOT import *
    #from ROOT import TFile, TCanvas, gROOT, TLegend, TString, TLine, TH1F, TBox, TPad
    #from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack, kGray, kViolet
    #from ROOT import RooFit, RooRealVar, RooAbsReal, RooCategory, RooArgSet, RooAddPdf, RooArgList
    gROOT.SetStyle( 'Plain' )    
    #gROOT.SetBatch( False )
    
    
    f = TFile( FILENAME )

    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )
    
    f.Close()
    mVarTS = TString(options.var)    
    mass = w.var(mVarTS.Data())
    sam = TString(options.sample)
    mode = TString(options.mode)
    merge = options.merge
    sufixTS = TString(options.sufix)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS
                
    
    if mode == "BDPi":
        Bmass_down = 5000
        Bmass_up = 5400
        Dmass_down = 1830 
        Dmass_up = 1920         
    else:
        Bmass_down = 5000
        Bmass_up = 5600
        Dmass_down = 1930
        Dmass_up = 2015

    if sam == "up":
        print "Sample up"
        w.factory("SUM:FullPdf(nSigEvts_up*SigEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up]")
        pullname3TS = TString("SigEPDF_up")
    elif sam == "down":
        print "Sample down"
        w.factory("SUM:FullPdf(nSigEvts_down*SigEPDF_down)")
        pullname2TS = TString("h_combData_Cut[sample==sample::down]")
        pullname3TS = TString("SigEPDF_down")
    elif sam == "both":
        print merge
        if merge == True:
            print "Sample both with merge"
            w.factory("SUM:FullPdf(nSigEvts_both*SigEPDF_both)")
            pullname2TS = TString("h_combData_Cut[sample==sample::both]")
            pullname3TS = TString("SigEPDF_both")
        else:
            print "Sample both"
            w.factory("SUM:FullPdf(nSigEvts_down*SigEPDF_down,nSigEvts_up*SigEPDF_up)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up || sample==sample::down]")
            pullname3TS = TString("SigEPDF_down,SigEPDF_up")
    else:
        print "[ERROR] Wrong sample"
        exit(0)

    dataName = TString("combData")    
    totName = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )
    dataset = w.data( dataName.Data() )
            
    if not ( modelPDF and dataset ) :
        print "Cos sie zepsulo?"
        w.Print( 'v' )
        exit( 0 )
    
    if ( mVarTS == "lab2_MM" ):
        mass.setRange(Dmass_down,Dmass_up)
    else:
        mass.setRange(Bmass_down,Bmass_up)
    frame_m = mass.frame()
    
    frame_m.SetTitle('') 
    
    frame_m.GetXaxis().SetLabelSize( 0.03 )
    frame_m.GetYaxis().SetLabelSize( 0.03 )
    if ( mVarTS == "lab2_MM" ):
        if ( mode == "BDPi" ):
            frame_m.GetXaxis().SetTitle("m(D) [MeV/c^{2}]")
        else:
            frame_m.GetXaxis().SetTitle("m(D_{s}) [MeV/c^{2}]")
    else:    
       if ( mode == "BDPi" ):
           frame_m.GetXaxis().SetTitle("m(B_{d}) [MeV/c^{2}]")
       else:
           frame_m.GetXaxis().SetTitle("m(B_{s}) [MeV/c^{2}]")
           
    frame_m.GetYaxis().SetTitleFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 ) 
    frame_m.SetLabelFont(132)
    frame_m.SetTitleFont(132)
           
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS, merge )
    if plotData : plotDataSet( dataset, frame_m, sam, merge )

    legend = TLegend( 0.15, 0.70, 0.40, 0.85 ) 
    legend.SetTextSize(0.03)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetHeader("LHCb L_{int}=1fb^{-1}")
   
    l1 = TLine()
    l1.SetLineColor(kBlue+2)
    l1.SetLineWidth(4)
    l1.SetLineStyle(kSolid)
    legend.AddEntry(l1, "Signal", "L")
        
    if ( mVarTS == "lab0_MassFitConsD_M" ):
        gStyle.SetOptLogy(1)
    canvas = TCanvas("canvas", "canvas", 600, 700)
    pad1 =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.20)
    pad1.Draw()
    pad2.Draw()
    pad1.cd()
    frame_m.Draw()
    legend.Draw("same")
    pad1.Update()

    frame_m.Print("v")
    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[")+pullname3TS+TString("]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    pullHist.SetTitle("")
    
    pad2.SetLogy(0)
    pad2.cd()

    if ( mVarTS == "lab0_MassFitConsD_M" ):
        gStyle.SetOptLogy(0)
            
    axisX = pullHist.GetXaxis()
    if ( mVarTS == "lab0_MassFitConsD_M" ):
        axisX.Set(100,Bmass_down,Bmass_up)
    else:
        axisX.Set(100,Dmass_down,Dmass_up)
    
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
                
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M" ):
        graph.SetPoint(1,Bmass_down,0)
        graph.SetPoint(2,Bmass_up,0)
    else:    
        graph.SetPoint(1,Dmass_down,0)
        graph.SetPoint(2,Dmass_up,0)
        
    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M" ):
        graph2.SetPoint(1,Bmass_down,-3)
        graph2.SetPoint(2,Bmass_up,-3)
    else:    
        graph2.SetPoint(1,Dmass_down,-3)
        graph2.SetPoint(2,Dmass_up,-3)
        
    graph2.SetLineColor(kRed)
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M" ):
        graph3.SetPoint(1,Bmass_down,3)
        graph3.SetPoint(2,Bmass_up,3)
    else:
        graph3.SetPoint(1,Dmass_down,3)
        graph3.SetPoint(2,Dmass_up,3)
        
    graph3.SetLineColor(kRed)
                                                                 

    pullHist.Draw("ap")
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
            
    pad2.Update()
    canvas.Update()
                                                                                
    n = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    pt = canvas.FindObject( n.Data() )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()
    t = TString("_")

    canName = TString("mass_Signal_")+mode+t+mVarTS+t+sam+sufixTS+TString(".pdf")
    canNameROOT = TString("mass_Signal_")+mode+t+mVarTS+t+sam+sufixTS+TString(".root")
    canNamePng = TString("mass_Signal_")+mode+t+mVarTS+t+sam+sufixTS+TString(".png")
    canvas.Print(canName.Data())
    canvas.Print(canNameROOT.Data())
    canvas.Print(canNamePng.Data())
                         
#------------------------------------------------------------------------------
