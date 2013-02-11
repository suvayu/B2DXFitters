#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a mass fit on data for Bd -> D pi                    #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBdMassFitterOnData.py [-d | --debug]                         #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 08 / 06 / 2011                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 02 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from os.path  import join

import GaudiPython

GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import *
#from ROOT import RooRealVar, RooStringVar
#from ROOT import RooArgSet, RooArgList
#from ROOT import RooAddPdf
#from ROOT import FitMeTool

GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils

Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# FIT CONFIGURATION
extendedFit =  True

# INITIAL PARAMETERS
#mean  = 5367.51
#sigma1 = 10.00
#sigma2 = 15.00
#alpha1 = 2.0
#alpha2 = -2.0
#n1 = 0.01
#n2 = 5.0
#frac = 0.50
                        

PIDcut = 0
Pcut_down = 0.0
Pcut_up = 100000000000.0
BDTGCut = 0.30
Dmass_down = 1948
Dmass_up = 1990
dataName      = '../data/config_fitSignal.txt'

# DATA FILES
# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def fitSignal( debug, var ) :

    
    dataTS = TString(dataName)
    mVarTS = TString(var)
    modeTS = TString("BsDsPi")
    mProbVarTS = TString("lab1_PIDK") 
                
    workspace = MassFitUtils.ObtainSignal(dataTS, TString("#Signal BsDsPi"),
                                          PIDcut,
                                          Pcut_down, Pcut_up,
                                          BDTGCut,
                                          Dmass_down, Dmass_up,
                                          mVarTS, mProbVarTS,
                                          modeTS, NULL)
    

    
            
    obsTS = TString(var)
    mass = GeneralUtils.GetObservable(workspace,obsTS, debug)
    observables = RooArgSet( mass )

    
    data= []
    nEntries = []
    sample = [TString("up"),TString("down")]
    for i in range(0,2):
        datasetTS = TString("dataSetMC")+modeTS+TString("_")+sample[i]
        data.append(GeneralUtils.GetDataSet(workspace,datasetTS), debug)
        nEntries.append(data[i].numEntries())
        print "Data set: %s with number of events: %s"%(data[i].GetName(),nEntries[i])


    mean  = 5367.51
    sigma1 = 10.77
    sigma2 = 16.0
    alpha1 = 2.0
    alpha2 = -2.0
    n1 = 1.33
    n2 = 5.0
    frac = 0.30
            
                
    meanVar   =  [RooRealVar( "DblCBPDF_mean_up" ,  "mean",    mean,    5000., 5500., "MeV/c^{2}"),
                  RooRealVar( "DblCBPDF_mean_down" ,  "mean",    mean,    5000., 5500., "MeV/c^{2}")]
    sigma1Var =  RooRealVar( "DblCBPDF_sigma1", "sigma1",  12.691 )#sigma1,  8,    20, "MeV/c^{2}")
    sigma2Var =  RooRealVar( "DblCBPDF_sigma2", "sigma2",  20.486 ) #sigma2,  10,    30, "MeV/c^{2}")
    alpha1Var =  RooRealVar( "DblCBPDF_alpha1", "alpha1",  2.1260) #alpha1,  0,     5)
    alpha2Var =  RooRealVar( "DblCBPDF_alpha2", "alpha2",  -2.0649) #alpha2,  -5,    0)
    n1Var     =  RooRealVar( "DblCBPDF_n1",     "n1",      1.1019) #,      0.0001,   10)
    n2Var     =  RooRealVar( "DblCBPDF_n2",     "n2",      5.8097) #n2,      0.001,   10)
    fracVar   =  RooRealVar( "DblCBPDF_frac",   "frac",    0.7844) #frac,    0,     1);

    nSigEvts = []
    nSig = []
    sigPDF = []
    for i in range(0,2):
        nSigEvts.append(0.9*nEntries[i])
        nameSig = TString("nSigEvts_")+sample[i]
        nSig.append(RooRealVar( nameSig.Data(), nameSig.Data(), nEntries[i], 0.8*nEntries[i], 1.2*nEntries[i]))
        sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVar[i], sigma1Var, alpha1Var, n1Var, sigma2Var, alpha2Var, n2Var, fracVar, nSig[i], sample[i].Data(), bName, debug ))
        
    #sigPDF = GeneralModels.buildDoubleCBEPDF( mass, mean, sigma1, alpha1, n1, sigma1, alpha2, n2, frac, nSig, 'SigMC', bName, debug )
            

    sam = RooCategory("sample","sample")
    sam.defineType(sample[0].Data())
    sam.defineType(sample[1].Data())

    combData = RooDataSet("combData","combined data",RooArgSet(observables),
                          RooFit.Index(sam),
                          RooFit.Import(sample[0].Data(),data[0]),
                          RooFit.Import(sample[1].Data(),data[1]))

    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    totPDF.addPdf(sigPDF[0], sample[0].Data())
    totPDF.addPdf(sigPDF[1], sample[1].Data())            
                          
    # Instantiate and run the fitter
    c = TString("no")
    if( c == "yes"):
        nll= RooNLLVar("nll","-log(sig)",totPDF,combData, RooFit.NumCPU(4));

        pll  = RooProfileLL("pll",  "",  nll, RooArgSet(sigma1Var));
        pll1 = RooProfileLL("pll1", "",  nll, RooArgSet(sigma2Var));
        pll2 = RooProfileLL("pll2", "",  nll, RooArgSet(alpha1Var));
        pll3 = RooProfileLL("pll3", "",  nll, RooArgSet(alpha2Var));
        pll4 = RooProfileLL("pll4", "",  nll, RooArgSet(n1Var));
        pll5 = RooProfileLL("pll5", "",  nll, RooArgSet(n2Var));
    #pll6 = RooProfileLL("pll6", "",  nll, RooArgSet(*cbmean1));
        pll7 = RooProfileLL("pll7", "",  nll, RooArgSet(fracVar));
    

        hsigma1 = pll.createHistogram("hsigma1",sigma1Var,RooFit.Binning(40));
        hsigma1.SetLineColor(kBlue);
        hsigma1.SetLineWidth(2);
        hsigma1.SetTitle("Likelihood Function - Sigma1");

        hsigma2 = pll1.createHistogram("hsigma2",sigma2Var,RooFit.Binning(40));
        hsigma2.SetLineColor(kBlue);
        hsigma2.SetLineWidth(2);
        hsigma2.SetTitle("Likelihood Function - Sigma2");


        halpha1 = pll2.createHistogram("halpha1",alpha1Var,RooFit.Binning(40));
        halpha1.SetLineColor(kRed);
        halpha1.SetLineWidth(2);
        halpha1.SetTitle("Likelihood Function - Alpha1");
    
        halpha2 = pll3.createHistogram("halpha2",alpha2Var,RooFit.Binning(40));
        halpha2.SetLineColor(kRed);
        halpha2.SetLineWidth(2);
        halpha2.SetTitle("Likelihood Function - Alpha2");


        hn1 = pll4.createHistogram("hn1",n1Var,RooFit.Binning(40));
        hn1.SetLineColor(kGreen);
        hn1.SetLineWidth(2);
        hn1.SetTitle("Likelihood Function - N1");

        hn2 = pll5.createHistogram("hn2",n2Var,RooFit.Binning(40));
        hn2.SetLineColor(kGreen);
        hn2.SetLineWidth(2);
        hn2.SetTitle("Likelihood Function - N2");
        
        hfrac = pll7.createHistogram("hfrac",fracVar,RooFit.Binning(40));
        hfrac.SetLineColor(42);
        hfrac.SetLineWidth(2);
        hfrac.SetTitle("Likelihood Function - Fraction");
    
        m1 = RooMinuit(nll);
        
        m1.setVerbose(kFALSE);
        m1.setLogFile("out.log");
        
        m1.setStrategy(2);
        m1.simplex();
        m1.migrad();
    
        m1.minos();
        m1.hesse();
        
        result=m1.save("result","result");
        result.Print();

        like = TCanvas("like", "like", 1200, 800);
        like.Divide(4,2)
        like.cd(1)
        hsigma1.Draw()
        like.cd(5)
        hsigma2.Draw()
        like.cd(2)
        halpha1.Draw()
        like.cd(6)
        halpha2.Draw()
        like.cd(3)
        hn1.Draw()
        like.cd(7)
        hn2.Draw()
        like.cd(8)
        hfrac.Draw()
        like.Update()
        n = TString("likelihood_BsDsPi.pdf")
        like.SaveAs(n.Data())
    

    else:    
   
        fitter = FitMeTool( debug )
        
        fitter.setObservables( observables )
        
        fitter.setModelPDF( totPDF )
        
        fitter.setData(combData) 
        
        plot_init   = options.initvars         and ( options.wsname != None )
        plot_fitted = ( not options.initvars ) and ( options.wsname != None )
        
        if plot_init :
            fitter.saveModelPDF( options.wsname )
            fitter.saveData ( options.wsname )
    
        fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2),  RooFit.Verbose(True), RooFit.InitialHesse(True))
            
        if plot_fitted :
            fitter.saveModelPDF( options.wsname )
            fitter.saveData ( options.wsname )

        gROOT.SetStyle( 'Plain' )
    #gROOT.SetBatch( False )
        gStyle.SetOptLogy(1)

        result = fitter.getFitResult()
        result.Print()
        model = fitter.getModelPDF()
        
    
        integral = model.createIntegral(observables,"all")
        integralVal = integral.getVal()
        print "Integral %f"%(integralVal)

        del fitter
    
#    exit(0)
#    canvas = TCanvas( 'MassCanvas', 'Mass canvas', 1200, 800 )
#    canvas.SetTitle( 'Fit in mass' )
#    canvas.cd()
#    gStyle.SetOptLogy(1)
    
#    frame_m = mass.frame()

#    frame_m.SetTitle( 'Fit in reconstructed %s mass' % bName )

#    frame_m.GetXaxis().SetLabelSize( 0.03 )
#    frame_m.GetYaxis().SetLabelSize( 0.03 )

#    model.plotOn( frame_m,
#                   RooFit.Components("mpdfSigMC"),
#                   RooFit.LineColor(kRed),
#                   RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
#                  )
#    model.plotOn( frame_m,
#                   RooFit.Components("mpdfSigMC_CB1"),
#                   RooFit.LineColor(kBlue),
#                   RooFit.LineStyle(kDashed),
#                   RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
#                   )
#    model.plotOn( frame_m,
#                   RooFit.Components("mpdfSigMC_CB2"),
#                   RooFit.LineColor(kGreen),
#                   RooFit.LineStyle(kDashed),
#                   RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
#                   )
#    
#    
    #model.paramOn( frame_m,
    #               RooFit.Layout( 0.56, 0.90, 0.85 ),
    #               RooFit.Format( 'NEU', RooFit.AutoPrecision( 2 ) )
    #               )
                   
                           
#    data.plotOn( frame_m, RooFit.Binning( 70 ) )
#    data.statOn( frame_m, RooFit.Layout( 0.10, 0.35, 0.90 ), RooFit.What('N') )#
#
#    canvas = TCanvas("canvas", "canvas", 600, 700)
#    pad1 =  TPad("pad1","pad1",0.01,0.31,0.99,0.99)
#    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.30)
#    pad1.Draw()
#    pad2.Draw()
#    pad1.cd()
#    frame_m.Draw()
#    pad1.Update()#
#
#    gStyle.SetOptLogy(0)#
#
#    frame_m.Print("v")
    
    #pullnameTS = TString("mpdfSigMC_CB1+mpdfSigMC_CB2_Norm[")+mVarTS+TString("]")
#    pullnameTS = TString("mepdfSigMC_Norm[")+mVarTS+TString("]_Comp[mpdfSigMC]")
#    pullHist  = frame_m.pullHist("h_dataSetMC",pullnameTS.Data())
    #residHist = mframe->residHist("h_dh",Form("mpdfSigMC_CB1+mpdfSigMC_CB2_Norm[%s]",mVarTS.Data()))
#    pad2.SetLogy(0)
#    pad2.cd()
#    gStyle.SetOptLogy(0)
#    pullHist.Draw("ap")
#    pad2.Update()
#    canvas.Update()

    
    #frame_m.Draw()
#    n = TString("SigPDF_paramBox")
#    pt = canvas.FindObject( n.Data() )
#    if pt :
#        print ''
#        pt.SetY1NDC( 0.40 )
#                            
#    canvas.Modified()
#    canvas.Update()
#    canName = TString("mass_Signal.pdf")
#    canvas.Print(canName.Data())
                
    
#del fitter

#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )
parser.add_option( '-s', '--save',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )
parser.add_option( '-i', '--initial-vars',
                   dest = 'initvars',
                   action = 'store_true',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
    
    fitSignal( options.debug, options.var)

# -----------------------------------------------------------------------------
