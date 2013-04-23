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
from ROOT import RooCruijff

GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# FIT CONFIGURATION
extendedFit =  True

# INITIAL PARAMETERS

n1 = 1.0
n2 = 1.0
frac = 0.50

PIDcut = 10
Pcut_down = 0.0
Pcut_up = 650000.0
PT_down = 100
PT_up = 45000 
nTr_down = 15
nTr_up = 1000

dataName      = '../data/config_ExpectedEvents.txt'

# DATA FILES
# MISCELLANEOUS
bName = '#Lambda_{b}'

#------------------------------------------------------------------------------

def fitLbLcPi( debug, sweight ) :

    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    
    dataTS = TString(dataName)
    mVarTS = TString("lab0_MassFitConsD_M")
    mDVarTS = TString("lab2_MM")
    modeTS = TString("BdDPi")
    t = TString('_')
    '''
    workspace = MassFitUtils.ObtainLbLcPi(dataTS, TString("#LbLcPi data"),
                                          PIDcut,
                                          Pcut_down, Pcut_up,
                                          PT_down, PT_up,
                                          nTr_down, nTr_up,
                                          mVarTS, mDVarTS,
                                          TString("LbLcPi"),
                                          NULL,
                                          debug)
    
    workspace.Print()
    saveNameTS = TString("work_lblcpi_10.root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    exit(0)
    '''
    workspace = GeneralUtils.LoadWorkspace(TString("work_lblcpi_10.root"),TString("workspace"),debug)
    
    
    massB = GeneralUtils.GetObservable(workspace,mVarTS, debug)
    massD = GeneralUtils.GetObservable(workspace,mDVarTS,debug)
    mom = GeneralUtils.GetObservable(workspace,TString("lab1_P"), debug)
    pt = GeneralUtils.GetObservable(workspace,TString("lab1_PT"), debug)
    nTr = GeneralUtils.GetObservable(workspace,TString("nTracks"), debug)
    pid = GeneralUtils.GetObservable(workspace,TString("lab1_PIDK"), debug)

    observables = RooArgSet( massB, massD, mom, pt, nTr, pid )

    data= []
    nEntries = []
    sample = [TString("up"),TString("down")]
    for i in range(0,2):
        datasetTS = TString("dataSetLb2LcPi_")+sample[i]
        data.append(GeneralUtils.GetDataSet(workspace,datasetTS))
        nEntries.append(data[i].numEntries())
        print "Data set: %s with number of events: %s"%(data[i].GetName(),nEntries[i])
        

    meanD  = 2290
    alpha1D = 0.16167
    alpha2D = 0.10289
    sigma1D = 0.50
    sigma2D = 0.50
    fracD = 0.5
    
    alpha1DVar =  RooRealVar( "alpha1D", "alpha1D",  alpha1D, 0.0, 0.5 )
    alpha2DVar =  RooRealVar( "alpha2D", "alpha2D",  alpha2D, 0.0, 0.5 )
    fracDVar   =  RooRealVar( "fracD",   "fracD",    fracD, 0.0, 1.0)
    
    meanDVar   =  [RooRealVar( "meanD_up" ,  "mean",    meanD,    meanD-150, meanD+150, "MeV/c^{2}"),
                   RooRealVar( "meanD_down" ,  "mean",    meanD,    meanD-150, meanD+150, "MeV/c^{2}")]
    sigma1DVar =  RooRealVar( "sigma1D", "sigma1",  sigma2D,  0.10, 15.0)
    sigma2DVar =  RooRealVar( "sigma2D", "sigma2",  sigma1D,  0.10, 15.0)

    nSigEvts = []
    nSig = []
    sigPDF = []
    sigDPDF = []
    sigProdPDF = []
    sigEPDF = []

    for i in range(0,2):
        nSigEvts.append(0.5*nEntries[i])
        nameSig = TString("nSig_")+sample[i]+TString("_Evts")
        nSig.append(RooRealVar( nameSig.Data(), nameSig.Data(), nSigEvts[i], 0., nEntries[i] ))

        nameSigPDF = TString("pdfDsSignal_")+sample[i]
        sigDPDF.append(RooCruijff(nameSigPDF.Data(), nameSigPDF.Data(),massD, meanDVar[i], sigma1DVar, sigma2DVar,alpha1DVar, alpha2DVar))
        #sigDPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleGEPDF_sim(massD, meanDVar[i], sigma1DVar, sigma2DVar,  fracDVar,
        #                                                          nSig[i], sample[i].Data(), bName, false, debug ))
                                                                  

        nameEPDF = TString("SigEPDF_")+sample[i]
        sigEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), sigDPDF[i]  , nSig[i]  ))

    sam = RooCategory("sample","sample")
    sam.defineType(sample[0].Data())
    sam.defineType(sample[1].Data())
    
    combData = RooDataSet("combData","combined data",RooArgSet(observables),
                          RooFit.Index(sam),
                          #RooFit.Import(sample[type].Data(),data[type]))
                          RooFit.Import(sample[0].Data(),data[0]),
                          RooFit.Import(sample[1].Data(),data[1]))

    totPDFsim = RooSimultaneous("simPdf","simultaneous pdf",sam)

    totEPDF = []
    nBkgEvts = []
    nBkg = []

    cD = []
    bkgDPDF = []
    bkgEPDF = []
    totEPDF = []
    
    for i in range(0,2):
        cD.append(RooRealVar("cD","coefficient #2", -0.1 ,-0.5, -0.000001))
        bkgDPDF.append(RooExponential("expD", "expB" , massD, cD[i]))

        nBkgEvts.append(0.4*nEntries[i])
        nameBkg = TString("nBkg_")+sample[i]+TString("_Evts")
        nBkg.append(RooRealVar( nameBkg.Data(), nameBkg.Data(), nBkgEvts[i], 0., nEntries[i] ))
               
        nameEPDF = TString("BkgEPDF_")+sample[i]
        bkgEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgDPDF[i]  , nBkg[i]  ))

        name = TString("TotEPDF_m_")+sample[i]
        totEPDF.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass', RooArgList( sigEPDF[i], bkgEPDF[i]) ))
                
                
    totPDFsim.addPdf(totEPDF[0], sample[0].Data())
    totPDFsim.addPdf(totEPDF[1], sample[1].Data())
    
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

    name = TString("./sWeights_LbLcPi_both_PIDK10.root")
    #Now includes setting things constant
    if sweight:
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(RooFit.Eval)
        fitter.savesWeights(mDVarTS.Data(), combData, name)
        RooMsgService.instance().reset()
        
    if plot_fitted :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )
        
    gROOT.SetStyle( 'Plain' )
    #gROOT.SetBatch( False )
    gStyle.SetOptLogy(1)

    result = fitter.getFitResult()
    result.Print()
    model = fitter.getModelPDF()
    
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
parser.add_option( '--sweight',
                   action = 'store_true',
                   dest = 'sweight',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )



# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    fitLbLcPi( options.debug, options.sweight)
        
# -----------------------------------------------------------------------------
                                


        
