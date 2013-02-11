#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC Gamma_d fit for Bd -> D pi                  #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBdGammaFitterToyMC.py <toy_number> [-d | --debug]            #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 25 / 05 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser

import GaudiPython

GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import RooRealVar, RooStringVar
from ROOT import RooArgSet, RooArgList
from ROOT import RooAddPdf
from ROOT import FitMeTool
from ROOT import BdPTAcceptance

GeneralModels = GaudiPython.gbl.GeneralModels
Bd2DhModels   = GaudiPython.gbl.Bd2DhModels
PTResModels   = GaudiPython.gbl.PTResModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MODELS
signalModelOnly =  False
propertimeResolutionModel  =  'Gaussian'         # truth/Gaussian/DoubleGaussian/GaussianWithScaleAndPEPTE
acceptanceFunction         =  'BdPTAcceptance'   # None/BdPTAcceptance/RooAcceptance

# PHYSICAL PARAMETERS
Gamma =  0.656    # in ps^{-1}

# TOY PARAMETERS
# Extended likelihood fit
nSigEvts      =  5980      # signal events
nCombBkgEvts  =  3625      # combinatorial background events
nBd2DKEvts    =  198       # Bd -> D K   phys. bkg. events
# Parameters for the combinatorial background PDF in time
CombBkgPdf_a      =  0.1209
CombBkgPdf_f      =  0.996
CombBkgPdf_alpha  =  4.149
CombBkgPdf_beta   =  1.139

# MISCELLANEOUS
bName = 'B_{d}'


#------------------------------------------------------------------------------
def runBdGammaFitterToyMC( toy_num, debug ) :
    
    time = RooRealVar( "time", "%s propertime" % bName, 0., 0., 8., 'ps' )
    
    gamma = RooRealVar( "Gamma", "%s average lifetime" % bName, Gamma, 0., 5., 'ps^{-1}' )
    
    observables = RooArgSet( time )
    
    BdPTRM = PTResModels.getPTResolutionModel( propertimeResolutionModel,
                                               time, 'Bd', debug )

    if acceptanceFunction :
        #sigPTAcc = getSignalPTAcceptanceFunction( acceptanceFunction )
        slope = RooRealVar( "BdPTAcceptance_slope_sig" , "BdPTAcceptance_slope_sig" , 2.36 )
        offset = RooRealVar( "BdPTAcceptance_offset_sig", "BdPTAcceptance_offset_sig", 0.2 )
        BdPTAcc = BdPTAcceptance( "BdPTAccFunction", "Bd propertime acceptance function",
                                  time, slope, offset )
    else :
        BdPTAcc = None
    
    nSig = RooRealVar( 'nSigEvts', 'nSigEvts', nSigEvts )
    sigPDF = GeneralModels.buildRooDecayEPDF( time, gamma,
                                              BdPTRM, BdPTAcc,
                                              nSig,
                                              'Sig', bName, debug )
    
    # Create the background PDF in time
    nCombBkg  = RooRealVar( 'nCombBkgEvts'  , 'nCombBkgEvts' , nCombBkgEvts )
    nBd2DK    = RooRealVar( 'nBd2DKEvts'    , 'nBd2DKEvts'   , nBd2DKEvts   )
    combBkgPdf_a     = RooRealVar( "CombBkgPdf_a"    , "CombBkgPdf_a"    , CombBkgPdf_a     )
    combBkgPdf_f     = RooRealVar( "CombBkgPdf_f"    , "CombBkgPdf_f"    , CombBkgPdf_f     )
    combBkgPdf_alpha = RooRealVar( "CombBkgPdf_alpha", "CombBkgPdf_alpha", CombBkgPdf_alpha )
    combBkgPdf_beta  = RooRealVar( "CombBkgPdf_beta" , "CombBkgPdf_beta" , CombBkgPdf_beta  )
    bkgPDF = Bd2DhModels.buildBdBackgroundNoTagEPDFInTime( time, gamma,
                                                           nCombBkg,
                                                           combBkgPdf_a,
                                                           combBkgPdf_f,
                                                           combBkgPdf_alpha,
                                                           combBkgPdf_beta,
                                                           nBd2DK,
                                                           BdPTRM, BdPTAcc,
                                                           debug
                                                           )
    
    # Instantiate and run the fitter in toy MC mode
    fitter = FitMeTool( toy_num, debug )
    
    fitter.setObservables( observables )
    
    if signalModelOnly :
        fitter.setModelPDF( sigPDF )
    else :
        # Create the total model PDF in time
        totPDF = RooAddPdf( 'TotEPDF_t', 'Model (signal & background) EPDF in propertime',
                            RooArgList( sigPDF, bkgPDF) )
        fitter.setModelPDF( totPDF )
    
    fitter.generate()
    
    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    if plot_init :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData( options.wsname )
    
    fitter.fit()
    
    if plot_fitted :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData( options.wsname )
    
    del fitter

#------------------------------------------------------------------------------
_usage = '%prog [options] <toy_number>'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
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

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) != 1 :
        parser.print_help()
        exit( -1 )
    
    try:
        TOY_NUMBER = int( args[ 0 ] )
    except ValueError:
        parser.error( 'The toy number is meant to be an integer ;-)!' )

    DEBUG = True if options.debug else False

    runBdGammaFitterToyMC( TOY_NUMBER, DEBUG )

# -----------------------------------------------------------------------------
