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
mean  = 5289.51
sigma1 = 22.00
sigma2 = 17.00
alpha1 = 2.0
alpha2 = -3.0
n1 = 1.0
n2 = 1.0
frac = 0.50
                        

PIDcut = 0
Pcut_down = 0.0
Pcut_up = 100000000000.0
BDTGCut = 0.50
Dmass_down = 1948
Dmass_up = 1990

dataName      = '../data/config_ExpectedEvents.txt'

# DATA FILES
# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def fitSignal( debug, var ) :

    
    dataTS = TString(dataName)
    mVarTS = TString(var)
    modeTS = TString("BdDPi") 
                
    workspace = MassFitUtils.Blabla(dataTS, TString("#BdPi"),
                                    PIDcut,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BdDPi"),false)
        

    workspace.Print()
            
    obsTS = TString(var)
    mass = GeneralUtils.GetObservable(workspace,obsTS)
    observables = RooArgSet( mass )

    
    data= []
    nEntries = []
    sample = [TString("up"),TString("down")]
    for i in range(0,2):
        datasetTS = TString("dataSetMC")+modeTS+TString("_")+sample[i]
        data.append(GeneralUtils.GetDataSet(workspace,datasetTS))
        nEntries.append(data[i].numEntries())
        print "Data set: %s with number of events: %s"%(data[i].GetName(),nEntries[i])

        
                
    meanVar   =  RooRealVar( "DblCBPDF_mean" ,  "mean",    mean,    5200., 5400., "MeV/c^{2}")
    sigma1Var =  RooRealVar( "DblCBPDF_sigma1", "sigma1",  sigma2,  10,     20, "MeV/c^{2}")
    sigma2Var =  RooRealVar( "DblCBPDF_sigma2", "sigma2",  sigma1,  20,     27, "MeV/c^{2}")
    alpha1Var =  RooRealVar( "DblCBPDF_alpha1", "alpha1",  alpha1,  1,     5)
    alpha2Var =  RooRealVar( "DblCBPDF_alpha2", "alpha2",  alpha2,  -4,    -1)
    n1Var     =  RooRealVar( "DblCBPDF_n1",     "n1",      n1,      0.1,   12)
    n2Var     =  RooRealVar( "DblCBPDF_n2",     "n2",      n2,      0.001,   5)
    fracVar   =  RooRealVar( "DblCBPDF_frac",   "frac",    frac,    0,     1);

    nSigEvts = []
    nSig = []
    sigPDF = []
    sigEPDF = []
    for i in range(0,2):
        nSigEvts.append(0.9*nEntries[i])
        nameSig = TString("nSigEvts_")+sample[i]
        nSig.append(RooRealVar( nameSig.Data(), nameSig.Data(), nSigEvts[i], 0., nEntries[i] ))
        sigEPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVar, sigma1Var, alpha1Var, n1Var, sigma2Var, alpha2Var, n2Var, fracVar, nSig[i], sample[i].Data(), bName, debug ))
        #namePDF = TString("SigPDF_")+sample[i]
        #sigPDF.append(RooGaussian(namePDF.Data(),namePDF.Data(),mass,meanVar,sigma1Var))
        #nameEPDF = TString("SigEPDF_")+sample[i]
        #sigEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), sigPDF[i]  , nSig[i]  ))
    #sigPDF = GeneralModels.buildDoubleCBEPDF( mass, mean, sigma1, alpha1, n1, sigma2, alpha2, n2, frac, nSig, 'SigMC', bName, debug )
            

    type = 1
    sam = RooCategory("sample","sample")
    sam.defineType(sample[type].Data())
    #sam.defineType(sample[0].Data())

    combData = RooDataSet("combData","combined data",RooArgSet(observables),
                          RooFit.Index(sam),
                          RooFit.Import(sample[type].Data(),data[type]))
                          #RooFit.Import(sample[1].Data(),data[1]))

    totPDFsim = RooSimultaneous("simPdf","simultaneous pdf",sam)
    bkgPDF1 = []
    bkgPDF2 = []
    bkgPDF = []
    c2 = []
    cb1 = []
    cb2 = []
    fracbkg = []
    
    totEPDF = []
    nBkgEvts = []
    nBkg = []
    bkgEPDF = []
    for i in range(0,2):
         c2.append(RooRealVar("c2","coefficient #2", -0.0055923 ,-0.006, -0.005)) 
         bkgPDF1.append(RooExponential("exp", "exp" , mass, c2[i]))

         cb1.append(RooRealVar("c0","coefficient #0", 0.9,-1.5,1.))
         cb2.append(RooRealVar("c1","coefficient #1", 0.1,-1.,1.))
        
         bkgPDF2.append(RooChebychev("cheb","cheb",mass,RooArgList(cb1[i],cb2[i])))

         nBkgEvts.append(0.4*nEntries[i])
         nameBkg = TString("nBkgEvts_")+sample[i]
         nBkg.append(RooRealVar( nameBkg.Data(), nameBkg.Data(), nBkgEvts[i], 0., nEntries[i] ))

         fracbkg.append(RooRealVar("fracbkg","fracbkg", 0.5,0.,1.))
         name = TString("BkgPDF_")+sample[i]
         bkgPDF.append(RooAddPdf(name.Data(), name.Data(), RooArgList(bkgPDF1[i],bkgPDF2[i]),RooArgList(fracbkg[i])))
         
         nameEPDF = TString("BkgEPDF_")+sample[i]
         bkgEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgPDF1[i]  , nBkg[i]  ))  
         
         name = TString("TotEPDF_m_")+sample[i]
         totEPDF.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass', RooArgList( sigEPDF[i], bkgEPDF[i] ) ))
                

    totPDFsim.addPdf(totEPDF[type], sample[type].Data())
                
                          
    # Instantiate and run the fitter
    fitter = FitMeTool( debug )
      
    fitter.setObservables( observables )

    fitter.setModelPDF( totPDFsim )
    
    fitter.setData(combData) 
      
    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    if plot_init :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )
    
    fitter.fit()
        
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

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
    
    fitSignal( options.debug, options.var)

# -----------------------------------------------------------------------------
