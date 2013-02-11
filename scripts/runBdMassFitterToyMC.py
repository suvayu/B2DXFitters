#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC mass fit for Bd -> D pi                     #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBdMassFitterToyMC.py <toy_number> [-d | --debug]             #
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
Bd2DhModels   = GaudiPython.gbl.Bd2DhModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# FIT CONFIGURATION
extendedFit =  True

# MODELS
signalModelOnly =  False

# TOY PARAMETERS
# If doing an extended likelihood fit
nSigEvts      =  6000      # signal events
nCombBkgEvts  =  9400      # combinatorial background events
nBd2DKEvts    =  420       # Bd -> D K   phys. bkg. events
nBd2DRhoEvts  =  7140      # Bd -> D rho phys. bkg. events
nBd2DstPiEvts =  1550      # Bd -> D* pi phys. bkg. events
nBd2DXEvts    =  2400      # Bd -> D X   phys. bkg. events

# DATA FILES
filesDir  = '../data'

# MISCELLANEOUS
bName = 'B_{d}'


#------------------------------------------------------------------------------
def runBdMassFitterToyMC( toy_num, debug ) :
    
    # Signal Bd mass model
    mean  = 5279.5
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
        nCombBkg  = RooRealVar( 'nCombBkgEvts'  , 'nCombBkgEvts' , nCombBkgEvts , 0. , 10000. )
        nBd2DK    = RooRealVar( 'nBd2DKEvts'    , 'nBd2DKEvts'   , nBd2DKEvts   , 0. , 10000. )
        nBd2DRho  = RooRealVar( 'nBd2DRhoEvts'  , 'nBd2DRhoEvts' , nBd2DRhoEvts , 0. , 10000. )
        nBd2DstPi = RooRealVar( 'nBd2DstPiEvts' , 'nBd2DstPiEvts', nBd2DstPiEvts, 0. , 10000. )
        nBd2DX    = RooRealVar( 'nBd2DXEvts'    , 'nBd2DXEvts'   , nBd2DXEvts   , 0. , 10000. )
        bkgPDF = Bd2DhModels.buildBdBackgroundEPDFInMass( mass,
                                                          filesDirVar,
                                                          nCombBkg,
                                                          nBd2DK,
                                                          nBd2DRho,
                                                          nBd2DstPi,
                                                          nBd2DX,
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
     
    #fitter.printModelStructure()

    fitter.printYieldsInRange( '*Evts', 'mass', 5220., 5850. )

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
        
    runBdMassFitterToyMC( TOY_NUMBER, options.debug )

# -----------------------------------------------------------------------------
