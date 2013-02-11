#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC mass fit for Bs -> Ds pi                    #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBsMassFitterToyMC.py <toy_number> [-d | --debug]             #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 24 / 05 / 2011                                                    #
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

GeneralModels = GaudiPython.gbl.GeneralModels
Bs2DshModels  = GaudiPython.gbl.Bs2DshModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# FIT CONFIGURATION
extendedFit =  True

# MODELS
signalModelOnly =  False

# TOY PARAMETERS
# If doing an extended likelihood fit
nSigEvts       =  6000    # signal events
nCombBkgEvts   =  13500   # combinatorial background events
nBd2DPiEvts    =  1000    # Bd -> D pi   phys. bkg. events
nBs2DsRhoEvts  =  2400    # Bs -> Ds rho phys. bkg. events
nBs2DsstPiEvts =  3200    # Bs -> Ds* pi phys. bkg. events
nBs2DsXEvts    =  2300    # Bs -> Ds X   phys. bkg. events
nLb2LcPiEvts   =  1100    # Lb -> Lc pi  phys. bkg. events

# DATA FILES
filesDir  = '../data'

# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def runBsMassFitterToyMC( toy_num, debug ) :
    
    # Signal Bs mass model
    mean  = 5366
    sigma = 19
    
    mass = RooRealVar( "mass", "%s mass" % bName, mean, 4800, 5850, "MeV/c^{2}" )
    
    observables = RooArgSet( mass )    
    
    if extendedFit :
        nSig = RooRealVar( 'nSigEvts', 'nSigEvts', nSigEvts, 0., 10000. )
        sigPDF = GeneralModels.buildGaussianEPDF( mass, mean, sigma,
                                                  nSig,
                                                  'Sig', bName, debug )
    else :
        sigPDF = GeneralModels.buildGaussianPDF( mass, mean, sigma,
                                                 'Sig', bName, debug )
    
    # Create the background PDF in mass
    filesDirVar = RooStringVar( 'filesDir', 'filesDir', filesDir );
    if extendedFit :
        nCombBkg   = RooRealVar( 'nCombBkgEvts'  , 'nCombBkgEvts'  , nCombBkgEvts  , 0., 10000. )
        nBd2DPi    = RooRealVar( 'nBd2DPiEvts'   , 'nBd2DPiEvts'   , nBd2DPiEvts   , 0., 10000. )
        nBs2DsRho  = RooRealVar( 'nBs2DsRhoEvts' , 'nBs2DsRhoEvts' , nBs2DsRhoEvts , 0., 10000. )
        nBs2DsstPi = RooRealVar( 'nBs2DsstPiEvts', 'nBs2DsstPiEvts', nBs2DsstPiEvts, 0., 10000. )
        nBs2DsX    = RooRealVar( 'nBs2DsXEvts'   , 'nBs2DsXEvts'   , nBs2DsXEvts   , 0., 10000. )
        nLb2LcPi   = RooRealVar( 'nLb2LcPiEvts'  , 'nLb2LcPiEvts'  , nLb2LcPiEvts  , 0., 10000. )
        bkgPDF = Bs2DshModels.buildBsBackgroundEPDFInMass( mass,
                                                           filesDirVar,
                                                           nCombBkg,
                                                           nBd2DPi,
                                                           nBs2DsRho,
                                                           nBs2DsstPi,
                                                           nBs2DsX,
                                                           nLb2LcPi,
                                                           debug )
        
    # Create the model PDF in mass
    if extendedFit :
        totPDF = RooAddPdf( 'TotEPDF_m', 'Model (signal & background) EPDF in mass',
                            RooArgList( sigPDF, bkgPDF ) )
    
    # Instantiate and run the fitter in toy MC mode
    fitter = FitMeTool( toy_num, debug )
    
    fitter.setObservables( observables )
    
    if signalModelOnly :
        fitter.setModelPDF( sigPDF )
    else :
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

    runBsMassFitterToyMC( TOY_NUMBER, options.debug )

# -----------------------------------------------------------------------------
