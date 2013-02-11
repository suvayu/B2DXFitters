#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to test running a toy MC mass fit for Bd -> D pi            #
#   defining the model PDF from the one stored on a RooWorkspace              #
#                                                                             #
#   Example usage:                                                            #
#      ./testToyFitFromWorkspace.py                                           #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 27 / 05 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

import GaudiPython

GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import RooRealVar, RooArgSet
from ROOT import FitMeTool


debug = True
toy_num = 7

mass = RooRealVar( "mass", "B_{d} mass", 5279, 4800, 5850, "MeV/c^{2}" )
observables = RooArgSet( mass )

fitter = FitMeTool( toy_num, debug )

fitter.setObservables( observables )

fitter.setModelPDF( 'testToyFitFromWorkspace.root', 'FitterWS', 'TotEPDF_m' )

fitter.generate()

fitter.fit()

del fitter
