#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC mass fit for Bs -> Ds K                     #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBs2DsKMassFitterToyMC.py <toy_number> [-d | --debug]         #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser

import GaudiPython

GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import RooRealVar, RooFormulaVar
from ROOT import RooArgSet, RooArgList
from ROOT import RooAddPdf, RooExponential, RooExtendPdf
from ROOT import RooFit
from ROOT import FitMeTool

GeneralModels = GaudiPython.gbl.GeneralModels
Bd2DhModels   = GaudiPython.gbl.Bd2DhModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# FIT CONFIGURATION
extendedFit =  True

# MODELS
signalModelOnly = False

# TOY PARAMETERS
# If doing an extended likelihood fit
nSigEvts      =  300      # signal events
nCombBkgEvts  =  2000      # combinatorial background events
nBs2DsPiEvts  =  200       # Bs -> Ds pi phys. bkg. events
# Bs mass offset for DsPi under the K-bachelor hypothesis
OffsetDsPi = 50

# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def runBs2DsKMassFitterToyMC( toy_num, debug ) :
    
    # Signal Bd mass model
    mean  = 5366.
    sigma = 19
    
    mass = RooRealVar( "mass", "%s mass" % bName, mean, 5000, 5800, "MeV/c^{2}" )
    
    observables = RooArgSet( mass )
    
    if extendedFit :
        nSig = RooRealVar( 'nSigEvts', 'nSigEvts', nSigEvts, 0., 50000. )
        sigPDF = GeneralModels.buildGaussianEPDF( mass, mean, sigma,
                                                  nSig,
                                                  'Sig', bName, debug )
    else :
        sigPDF = GeneralModels.buildGaussianPDF( mass, mean, sigma,
                                                 'Sig', bName, debug )
    
    # Create the background PDFs in mass
    if not signalModelOnly :
        if extendedFit :
            nCombBkg  = RooRealVar( 'nCombBkgEvts'  , 'nCombBkgEvts' , nCombBkgEvts , 0. , 100000. )
            combBkgPDF_slope = RooRealVar( 'CombBkgPDF_slope',
                                           'Combinatorial background PDF in mass - exponential slope',
                                           -0.002, -0.01, 0., '[MeV/c^{2}]^{-1}' )
            combBkgPDF = RooExponential( 'CombBkgPDF_m', 'Combinatorial background PDF in mass',
                                         mass, combBkgPDF_slope )
            combBkgEPDF = RooExtendPdf( 'CombBkgEPDF_m', combBkgPDF.GetTitle(), combBkgPDF, nCombBkg )
            
            nBs2DsPi  = RooRealVar( 'nBs2DsPiEvts'  , 'nBs2DsPiEvts' , nBs2DsPiEvts , 0. , 100000. )
            #offsetDsPi = RooRealVar( 'offsetDsPi', 'offsetDsPi', OffsetDsPi, 0., 200, 'MeV/c^{2}' )
            #meanDsPi = RooFormulaVar( "meanDsPi", "@0+@1", RooArgList( mean, offsetDsPi ) )
            meanDsPi = mean + OffsetDsPi
            Bs2DsPiEPDF = GeneralModels.buildGaussianEPDF( mass, meanDsPi, sigma,
                                                           nBs2DsPi,
                                                           'Bs2DsPi', bName, debug )
            
            bkgPDF = RooAddPdf( 'BkgEPDF_m', 'BkgEPDF_m',
                                RooArgList( combBkgEPDF, Bs2DsPiEPDF ) )
        
        # Create the model PDF in mass
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
    
    fitter.fit( True, RooFit.NumCPU( 6 ), RooFit.Strategy( 2 ), RooFit.Timer() )
    
    if plot_fitted :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData( options.wsname )
    
    #fitter.printModelStructure()
    
    fitter.printYieldsInRange( '*Evts', 'mass', 5220., 5800. )
    
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
        
    runBs2DsKMassFitterToyMC( TOY_NUMBER, options.debug )

# -----------------------------------------------------------------------------
