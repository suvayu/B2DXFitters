#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a signal fit on MC for B->DPi, Bs->DsPi, Bs->DsK     #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python fitSignal.py --mode BDPi -s WS.root --debug --veto              #
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

GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------


# INITIAL PARAMETERS
mean  = 5367.51
sigma1 = 10.00
sigma2 = 15.00
alpha1 = 2.0
alpha2 = -2.0
n1 = 0.01
n2 = 5.0
frac = 0.50
                        
Pcut_down = 0.0
Pcut_up = 650000000.0
Time_down = 0.0
Time_up = 15.0
PT_down  = 500.0
PT_up = 45000.0
nTr_down = 1.0
nTr_up = 1000.0

dataName      = '../data/config_fitSignal.txt'

# DATA FILES
# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def fitSignal( debug, var , mode, modeDs,  reweight, veto, merge, BDTG) :

    
    dataTS = TString(dataName)
    mVarTS = TString("lab0_MassFitConsD_M")
    mdVarTS = TString("lab2_MM")
    tVarTS = TString("lab0_LifetimeFit_ctau")
    terrVarTS = TString("lab0_LifetimeFit_ctauErr")
    tagVarTS = TString("lab0_BsTaggingTool_TAGDECISION_OS")
    tagOmegaVarTS = TString("lab0_BsTaggingTool_TAGOMEGA_OS")
    idVarTS = TString("lab1_ID")
    modeTS = TString(mode)
    mProbVarTS = TString("lab1_PIDK")
    if modeTS  == "BsDsK":
        PIDcut = 5
    else:
        PIDcut = 0
    obsTS = TString(var)    
    if modeTS == "BDPi":
        modeDsTS = TString("KPiPi")
        tagVarTS = TString("lab0_BdTaggingTool_TAGDECISION_OS")
        tagOmegaVarTS = TString("lab0_BdTaggingTool_TAGOMEGA_OS")
        Dmass_down = 1770 #1830 #1930
        Dmass_up = 1920 #2015
        Bmass_down = 5000
        Bmass_up = 5500
        if ( obsTS == "lab2_MM"):
            mean  =  1869 #1968.49
        else:
            mean  = 5279 #367.51
                                
    else:
        modeDsTS=TString(modeDs)
        Dmass_down = 1930
        Dmass_up = 2015
        Bmass_down = 5000
        Bmass_up = 5600
        if ( obsTS == "lab2_MM"):
            mean  =  1968.49
        else:
            mean  = 5367.51

    BDTGTS = TString(BDTG)
    if  BDTGTS == "BDTGA":
        BDTG_down = 0.3
        BDTG_up = 1.0
    elif BDTGTS == "BDTGC":
        BDTG_down = 0.5
        BDTG_up= 1.0
    elif BDTGTS== "BDTG1":
        BDTG_down = 0.3
        BDTG_up= 0.7
    elif BDTGTS== "BDTG2":
        BDTG_down = 0.7
        BDTG_up= 0.9
    elif BDTGTS== "BDTG3":
        BDTG_down = 0.9
        BDTG_up= 1.0
        
    print "BDTG Range: (%f,%f)"%(BDTG_down,BDTG_up)

    if ( modeDsTS == "NonRes" or modeDsTS == "KstK" or modeDsTS == "PhiPi" or modeDsTS == "All"):
        if modeDsTS == "NonRes" :
            modeDsTS2 = "nonres"
        elif modeDsTS == "KstK":
            modeDsTS2 = "kstk"
        elif modeDsTS == "PhiPi":
            modeDsTS2 = "phipi"
        else:
            modeDsTS2 = "kkpi"
    else:
        if modeDsTS == "KPiPi" :
            modeDsTS2 = "kpipi"
        elif modeDsTS == "PiPiPi":
            modeDsTS2 = "pipipi"
        else:
            modeDsTS2 = "kkpi"
                                                                                                                                
    
                                
    nameTS = TString("#Signal ")+modeTS+TString(" ")+modeDsTS
    print nameTS
    workspace = MassFitUtils.ObtainSignal(dataTS, nameTS,
                                          PIDcut,
                                          Pcut_down, Pcut_up,
                                          BDTG_down, BDTG_up,
                                          Dmass_down, Dmass_up,
                                          Bmass_down, Bmass_up,
                                          Time_down, Time_up,
                                          PT_down, PT_up,
                                          nTr_down, nTr_up,
                                          mVarTS, mdVarTS, tVarTS, terrVarTS, tagVarTS,
                                          tagOmegaVarTS, idVarTS, mProbVarTS,
                                          modeTS,
                                          reweight, veto,
                                          NULL, debug)
    
                                             
       
    
    mass = GeneralUtils.GetObservable(workspace,obsTS, debug)
    observables = RooArgSet( mass )
    
             
                                                                                           
                                                                                                                    
    data= []
    nEntries = []
    if merge:
        sample = [TString("both"),TString("both")]
    else:    
        sample = [TString("up"),TString("down")]
    for i in range(0,1):
        datasetTS = TString("dataSetMC_")+modeTS+TString("_")+sample[i]+TString("_")+modeDsTS2
        data.append(GeneralUtils.GetDataSet(workspace,datasetTS, debug))
        nEntries.append(data[i].numEntries())
        print "Data set: %s with number of events: %s"%(data[i].GetName(),nEntries[i])

        
    if obsTS != "lab2_MM":
        sigma1 = 10.00
        sigma2 = 7.00
        alpha1 = 4.0
        alpha2 = -2.0
        n1 = 5.0
        n2 = 2.0
        frac = 0.50
        alpha1Var =  RooRealVar( "DblCBPDF_alpha1", "alpha1",  alpha1,  0,     6)
        alpha2Var =  RooRealVar( "DblCBPDF_alpha2", "alpha2",  alpha2,  -6,    0)
        n1Var     =  RooRealVar( "DblCBPDF_n1",     "n1",      n1,      0.001,  50)
        n2Var     =  RooRealVar( "DblCBPDF_n2",     "n2",      n2,      0.001,  50)
        fracVar   =  RooRealVar( "DblCBPDF_frac",   "frac",    frac,    0,     1)
        sigma1Var =  RooRealVar( "DblCBPDF_sigma1", "sigma1",  sigma1,  1.0,    30, "MeV/c^{2}")
        sigma2Var =  RooRealVar( "DblCBPDF_sigma2", "sigma2",  sigma2,  1.0,    20, "MeV/c^{2}")
            
    else:
        sigma1 = 15.00
        sigma2 = 10.0
        sigma3 = 1.0
        alpha1 = 5.0
        alpha2 = -3.0
        n1 = 25.0
        n2 = 40.0 
        frac = 0.50
        frac2 = 0.50
        alpha1Var =  RooRealVar( "DblCBPDF_alpha1", "alpha1",  alpha1,  0.0,  7.0)
        alpha2Var =  RooRealVar( "DblCBPDF_alpha2", "alpha2",  alpha2,  -7.0,  0.0)
        n1Var     =  RooRealVar( "DblCBPDF_n1",     "n1",      n1,      0.001,  50)
        n2Var     =  RooRealVar( "DblCBPDF_n2",     "n2",      n2,      0.001,  70)
                
        fracVar   =  RooRealVar( "DblCBPDF_frac",   "frac",    frac,    0,     1)
        frac2Var   =  RooRealVar( "DblCBPDF_frac2",   "frac2",    frac2,    0,     1)
        sigma1Var =  RooRealVar( "DblCBPDF_sigma1", "sigma1",  sigma1,  1,    20, "MeV/c^{2}")
        sigma2Var =  RooRealVar( "DblCBPDF_sigma2", "sigma2",  sigma2,  1,    20, "MeV/c^{2}")
        sigma3Var =  RooRealVar( "DblCBPDF_sigma3", "sigma3",  sigma3,  0.0001,    20, "MeV/c^{2}")
        
    meanVar   =  [RooRealVar( "DblCBPDF_mean_up" ,  "mean",    mean,    mean-50, mean+50, "MeV/c^{2}"),
                  RooRealVar( "DblCBPDF_mean_down" ,  "mean",    mean,    mean-50, mean+50, "MeV/c^{2}")]


    #sigma1Var =  RooRealVar( "DblCBPDF_sigma1", "sigma1",  sigma1,  1,    20, "MeV/c^{2}")
    #sigma2Var =  RooRealVar( "DblCBPDF_sigma2", "sigma2",  sigma2,  1,    20, "MeV/c^{2}")
                
    
    nSigEvts = []
    nSig = []
    sigPDF1 = []
    sigPDF2 = []
    sigPDF3 = []
    sigPDF = []
    sigEPDF = []
    
    for i in range(0,1):
        nSigEvts.append(0.9*nEntries[i])
        nameSig = TString("nSigEvts_")+sample[i]
        nSig.append(RooRealVar( nameSig.Data(), nameSig.Data(), nEntries[i], 0.8*nEntries[i], 1.2*nEntries[i]))
        if obsTS != "lab2_MM":
            sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVar[i], sigma1Var, alpha1Var, n1Var, sigma2Var,
                                                                      alpha2Var, n2Var, fracVar, nSig[i], sample[i].Data(), bName, debug ))
        else:
            nameSigPDF = TString("pdfSignal_")+sample[i]
            #sigPDF.append(RooCruijff(nameSigPDF.Data(), nameSigPDF.Data(),mass, meanVar[i], sigma1Var, sigma2Var,alpha1Var, alpha2Var))
            #sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleGEPDF_sim(mass, meanVar[i], sigma1Var, sigma2Var,  fracVar,
            #                                                         nSig[i], sample[i].Data(), bName, false, debug ))
            sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVar[i], sigma1Var, alpha1Var, n1Var, sigma2Var,
                                                                      alpha2Var, n2Var, fracVar, nSig[i], sample[i].Data(), bName, debug ))

            #sigPDF.append(RooCBShape( nameSigPDF.Data(), nameSigPDF.Data(), mass ,meanVar[i], sigma1Var, alpha1Var, n1Var))
            
            #name1 = TString("gauss1_")+sample[i]
            #sigPDF1.append(RooGaussian(name1.Data(), name1.Data(), mass, meanVar[i], sigma1Var))
            #name2 = TString("gauss2_")+sample[i]
            #sigPDF2.append(RooGaussian(name2.Data(), name2.Data(), mass, meanVar[i], sigma2Var))
            #name3 = TString("gauss3_")+sample[i]
            #sigPDF3.append(RooGaussian(name3.Data(), name3.Data(), mass, meanVar[i], sigma3Var))
            #sigPDF.append(RooAddPdf(nameSigPDF.Data(), nameSigPDF.Data(),
            #                        RooArgList(sigPDF1[i],sigPDF2[i],sigPDF3[i]),
            #                        RooArgList(fracVar, frac2Var), True))
            
        nameEPDF = TString("SigEPDF_")+sample[i]
        sigEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), sigPDF[i]  , nSig[i]  ))
                
                   

    sam = RooCategory("sample","sample")
    if merge:
        sam.defineType(sample[0].Data())
    else:
        sam.defineType(sample[0].Data())
        sam.defineType(sample[1].Data())

    if merge:
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sample[0].Data(),data[0]))
        
    else:
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sample[0].Data(),data[0]),
                              RooFit.Import(sample[1].Data(),data[1]))
        
    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    if merge:
        totPDF.addPdf(sigEPDF[0], sample[0].Data())
    else:
        totPDF.addPdf(sigEPDF[0], sample[0].Data())
        totPDF.addPdf(sigEPDF[1], sample[1].Data())            
                    
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
    
        fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2)) #,  RooFit.Verbose(True), RooFit.InitialHesse(True))
            
        if plot_fitted :
            fitter.saveModelPDF( options.wsname )
            fitter.saveData ( options.wsname )

        gROOT.SetStyle( 'Plain' )
    
        gStyle.SetOptLogy(1)

        result = fitter.getFitResult()
        result.Print()
        model = fitter.getModelPDF()
        
    
        integral = model.createIntegral(observables,"all")
        integralVal = integral.getVal()
        print "Integral %f"%(integralVal)

        del fitter

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

parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   default = 'BsDsPi',
                   help = 'set observable '
                   )
parser.add_option( '--modeDs',
                   dest = 'modeDs',
                   default = 'KKPi',
                   help = 'set observable '
                   )
parser.add_option( '--shape',
                   dest = 'shape',
                   default = 'dCB',
                   help = 'set shape '
                   )
parser.add_option( '--veto',
                   action = 'store_true',
                   dest = 'veto',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '--reweight',
                   action = 'store_true',
                   dest = 'reweight',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '--merge',
                   action = 'store_true',
                   dest = 'merge',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '--BDTG',
                   dest = 'BDTG',
                   default = 'BDTGA',
                   help = 'Set BDTG range '
                   )



# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
    
    fitSignal( options.debug, options.var, options.mode, options.modeDs,
               options.reweight,
               options.veto,  options.merge,
               options.BDTG)

# -----------------------------------------------------------------------------
