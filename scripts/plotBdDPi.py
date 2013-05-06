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

Dmass_dw = 1830
Dmass_up = 1910

Bmass_dw = 5000
Bmass_up = 6000

bin = 200
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

    if sample == "both":
        if merge:
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
                                                                         
                
   # dataset.statOn( frame,
   #                 RooFit.Layout( 0.10, 0.45, 0.90  ),
   #                 RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame, sam, var, merge) :
    #if debug :
    
    print "model"    
    model.Print( 't' )

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    nameTot = TString("FullPdf")
    if sam == "both":
        if merge:
            nameSig = TString("SigEPDF_both")
            nameBkg = TString("BkgEPDF_both")
            nameBDK = nameBkg + TString(",BkgBDKEPDF_both")
            nameBsDsPi = nameBDK + TString(",BkgBsDsPiEPDF_both")
            nameLbLcPi = nameBsDsPi + TString(",BkgLbLcPiEPDF_both")
            nameBkgX = nameLbLcPi + TString(",BkgBkgXEPDF_both")
            nameDRho = nameLbLcPi+TString(",BkgBdDRhoEPDF_both")
            nameDstPi = nameDRho + TString(",BkgBdDstPiEPDF_both")
                                                                                                        
        else:
            nameSig1 = TString("DblCBPDFdown_CB1,DblCBPDFup_CB1")
            nameSig2 = TString("DblCBPDFdown_CB2,DblCBPDFup_CB2")
            nameSig  = TString("SigEPDF_down,SigEPDF_up") 
            nameBkg = TString("BkgEPDF_down,BkgEPDF_up")
            nameBDK = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBDKEPDF_up,BkgEPDF_up")
            nameBsDsPi = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_down,BkgBsDsPiEPDF_up")
            nameLbLcPi = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_down,BkgBsDsPiEPDF_up,BkgLbLcPiEPDF_down,BkgLbLcPiEPDF_up")
            nameBkgX = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_down,BkgBsDsPiEPDF_up,BkgLbLcPiEPDF_down,BkgLbLcPiEPDF_up,BkgBkgXEPDF_down,BkgBkgXEPDF_up")
            nameDRho = nameLbLcPi+TString(",BkgBdDRhoEPDF_down,BkgBdDRhoEPDF_up")
            nameDstPi = nameDRho + TString(",BkgBdDstPiEPDF_down,BkgBdDstPiEPDF_up")

    elif sam == "down" :
        #nameSig1 = TString("DblCBPDFdown_CB1")
        #nameSig2 = TString("DblCBPDFdown_CB2")
        nameSig1 = TString("DblGPDFdown_G1")
        nameSig2 = TString("DblGPDFdown_G2")
                
        nameSig  = TString("SigEPDF_down")
        nameBkg = TString("BkgEPDF_down")
        nameBDK = TString("BkgBDKEPDF_down,BkgEPDF_down")
        nameBsDsPi = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBsDsPiEPDF_down")
        nameLbLcPi = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBsDsPiEPDF_down,BkgLbLcPiEPDF_down")
        nameBkgX = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBsDsPiEPDF_down,BkgLbLcPiEPDF_down,BkgBkgXEPDF_down")
        
    elif sam == "up":
        #nameSig1 = TString("DblCBPDFup_CB1")
        #nameSig2 = TString("DblCBPDFup_CB2")
        #nameSig  = TString("SigEPDF_up")
        #nameBkg = TString("BkgEPDF_up")
        nameSig1 = TString("DblGPDFup_G1")
        nameSig2 = TString("DblGPDFup_G2")

        nameSig  = TString("SigEPDF_up")
        nameBkg = TString("BkgEPDF_up")
        nameBDK = TString("BkgBDKEPDF_up,BkgEPDF_up")
        nameBsDsPi = TString("BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_up")
        nameLbLcPi = TString("BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_up,BkgLbLcPiEPDF_up")
        nameBkgX =  TString("BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_up,BkgLbLcPiEPDF_up,BkgBkgXEPDF_up")
        
                                
    else:
        print "[ERROR] Wrong sample"
        exit(0)

    model.plotOn( frame,
                  RooFit.Components(nameDstPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-3),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameDRho.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kYellow-7),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
     
    model.plotOn( frame,
                  RooFit.Components(nameLbLcPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kRed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    

    model.plotOn( frame,
                  RooFit.Components(nameBsDsPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-10),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameBDK.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kOrange),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameBkg.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-6),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    
    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kMagenta-2),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame,
                  RooFit.Components(nameSig.Data()),
                  RooFit.LineColor(kRed-4),
                  RooFit.LineStyle(7),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    
    #model.plotOn( frame,
    #              RooFit.Components(nameSig.Data()),
    #              RooFit.LineColor(kMagenta-2),
    #              RooFit.LineStyle(kDashed),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )
'''     
    model.plotOn( frame,
                  RooFit.Components(nameSig2.Data()),
                  RooFit.LineColor(kBlue-10),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components(nameSig1.Data()),
                  RooFit.LineColor(kBlue-10),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame,
                  RooFit.Components(nameSig.Data()),
                  RooFit.LineColor(kBlue),
                  RooFit.LineStyle(7),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
'''                        
    #model.plotOn( frame,
    #              RooFit.Components(nameBkg.Data()),
    #              RooFit.LineColor(kRed),
    #              RooFit.LineStyle(7),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )

    #model.plotOn( frame,
    #              RooFit.Components(nameBDK.Data()),
    #              RooFit.LineColor(kOrange),
    #              RooFit.LineStyle(7),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )
    
       
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
   # gROOT.SetBatch( False )

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
    #mass.setRange(Bmass_dw,Bmass_up)
    sam = TString(options.sample)
    sufixTS = TString(options.sufix)
    merge = options.merge
    if merge and sam != "both":
        print "You cannot run option megrge with sample up or down"
        exit(0)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS
                

    
    w.Print('v')
    #exit(0)
        
       
    dataName = TString("combData")


    if sam == "up":
        print "Sample up"
        w.factory("SUM:FullPdf(nSig_up_Evts*SigEPDF_up,nBkg_up_Evts*BkgEPDF_up,nBd2DK_up_Evts*BkgBDKEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up]")
    elif sam == "down":
        print "Sample down"
        w.factory("SUM:FullPdf(nSig_down_Evts*SigEPDF_down,nBkg_down_Evts*BkgEPDF_down,nBd2DK_down_Evts*BkgBDKEPDF_down)")
        pullname2TS = TString("h_combData_Cut[sample==sample::down]")
    elif sam == "both":
        if merge:
            print "Sample both with merge"
            w.factory("SUM:FullPdf(nSig_both_Evts*SigEPDF_both,nBkg_both_Evts*BkgEPDF_both,nBd2DK_both_Evts*BkgBDKEPDF_both,nBs2DsPi_both_Evts*BkgBsDsPiEPDF_both, nLb2LcPi_both_Evts*BkgLbLcPiEPDF_both, nBd2DRho_both_Evts*BkgBdDRhoEPDF_both,nBd2DstPi_both_Evts*BkgBdDstPiEPDF_both)")
            pullname2TS = TString("h_combData_Cut[sample==sample::both]")
                        
        else:
            print "Sample both"
            w.factory("SUM:FullPdf(nSig_down_Evts*SigEPDF_down,nSig_up_Evts*SigEPDF_up,nBkg_down_Evts*BkgEPDF_down,nBkg_up_Evts*BkgEPDF_up,nBd2DK_down_Evts*BkgBDKEPDF_down,nBd2DK_up_Evts*BkgBDKEPDF_up, nBs2DsPi_down_Evts*BkgBsDsPiEPDF_down, nBs2DsPi_up_Evts*BkgBsDsPiEPDF_up, nLb2LcPi_down_Evts*BkgLbLcPiEPDF_down, nLb2LcPi_up_Evts*BkgLbLcPiEPDF_up,nBd2DRho_up_Evts*BkgBdDRhoEPDF_up,nBd2DRho_down_Evts*BkgBdDRhoEPDF_down,nBd2DstPi_up_Evts*BkgBdDstPiEPDF_up, nBd2DstPi_down_Evts*BkgBdDstPiEPDF_down)") #, nBkgX_down_Evts*BkgBkgXEPDF_down, nBkgX_up_Evts*BkgBkgXEPDF_up)")
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
        frame_m.GetXaxis().SetTitle("m(B_{d}) [MeV/c^{2}]")
    else:
        frame_m.GetXaxis().SetTitle("m(D) [MeV/c^{2}]")
    frame_m.GetYaxis().SetTitleFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 )
    frame_m.SetLabelFont(132)
    frame_m.SetTitleFont(132)
                 
           
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS, merge )
    if plotData : plotDataSet( dataset, frame_m, sam, merge )

    if ( mVarTS == "lab0_MassFitConsD_M"):
        gStyle.SetOptLogy(1)
        
    canvas = TCanvas("canvas", "canvas",1200, 1000)
    canvas.SetTitle( 'Fit in mass' )
    canvas.cd()

    pad1 =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.20)
    pad1.Draw()
    pad2.Draw()

    if ( mVarTS == "lab0_MassFitConsD_M"):
        legend = TLegend( 0.60, 0.50, 0.85, 0.85 )
    else:
        legend = TLegend( 0.12, 0.50, 0.35, 0.85 )
    legend.SetTextSize(0.03)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetHeader("LHCb L_{int}=1fb^{-1}")


    l1 = TLine()
    l1.SetLineColor(kRed-4)
    l1.SetLineWidth(4)
    l1.SetLineStyle(7)
    legend.AddEntry(l1, "Signal B^{0} #rightarrow D^{-}#pi^{+}", "L")

    h1=TH1F("Combinatorial","Combinatorial",5,0,1)
    h1.SetFillColor(kBlue-6)
    h1.SetFillStyle(1001)
    legend.AddEntry(h1, "Combinatorial", "f")
    
    h2=TH1F("B2DK","B2DK",5,0,1)
    h2.SetFillColor(kOrange)
    h2.SetFillStyle(1001)
    legend.AddEntry(h2, "B_{d}#rightarrow DK", "f")

    h3=TH1F("Bs2DsPi","Bs2DsPi",5,0,1)
    h3.SetFillColor(kBlue-10)
    h3.SetFillStyle(1001)
    legend.AddEntry(h3, "B_{s}#rightarrow D_{s}#pi", "f")

    h4=TH1F("Lb2LcPi","Lb2LcPi",5,0,1)
    h4.SetFillColor(kRed)
    h4.SetFillStyle(1001)
    legend.AddEntry(h4, "#Lambda_{b}#rightarrow #Lambda_{c}#pi", "f")

    h5=TH1F("BkgX","BkgX",5,0,1)
    h5.SetFillColor(kYellow-7)
    h5.SetFillStyle(1001)
#    legend.AddEntry(h5, "BkgX", "f")

    h6=TH1F("Bd2DRho","B2DRho",5,0,1)
    h6.SetFillColor(kYellow-7)
    h6.SetFillStyle(1001)
    legend.AddEntry(h6, "B_{d}#rightarrow D#rho", "f")

    h7=TH1F("Bd2DstPi","B2DstPi",5,0,1)
    h7.SetFillColor(kBlue-3)
    h7.SetFillStyle(1001)
    legend.AddEntry(h7, "B_{d}#rightarrow D^{*}#pi", "f")
                
    
    pad1.cd()
    frame_m.Draw()
    legend.Draw("same")
    pad1.Update()
    
    pad2.SetLogy(0)
    pad2.cd()
    gStyle.SetOptLogy(0)
            
    
    frame_m.Print("v")
    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[FullPdf]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    pullHist.SetTitle("")
    
    #pullHist.SetMaximum(5800.00)
    #pullHist.SetMinimum(5100.00)
    axisX = pullHist.GetXaxis()
    if ( mVarTS == "lab0_MassFitConsD_M"):
        axisX.Set(bin,Bmass_dw,Bmass_up)
    else:
        axisX.Set(bin,Dmass_dw,Dmass_up)
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
    canName = TString("mass_BDPi_")+mVarTS+TString("_")+sam+sufixTS+TString(".pdf")
    canvas.SaveAs(canName.Data())
    canNamePng = TString("mass_BDPi_")+mVarTS+TString("_")+sam+sufixTS+TString(".png")
    canvas.SaveAs(canNamePng.Data())
    canNameROOT = TString("mass_BDPi_")+mVarTS+TString("_")+sam+sufixTS+TString(".root")
    canvas.SaveAs(canNameROOT.Data())
        
    
        
#------------------------------------------------------------------------------
