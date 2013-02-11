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


PIDcut_dsk = 10
PIDcut_dspi = 0
histname = "MyPionMisID_10"
PIDmisscut= 0 
pPIDcut = 5
Pcut_down = 0.0
Pcut_up = 100000000000.0
BDTGCut = 0.50
Dmass_down =1948
Dmass_up = 1990

# DATA FILES
#filesDir      = '../data'
dataName      = '../data/config_dsdsstpirho.txt'
saveName      = 'work_'

# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def runBsDsPiMassFitterOnData( debug, mVar, mProbVar, save ) :

    dataTS = TString(dataName)
    mVarTS = TString(mVar)
    mProbVarTS = TString(mProbVar)
    
    workspace = MassFitUtils.Blabla(dataTS, TString("#BsDsPi"),
                                    PIDcut_dsk,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BsDsPi"),true, TString("DsK"))

    workspace = MassFitUtils.Blabla(dataTS, TString("#BsDsRho"),
                                    PIDcut_dsk,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BsDsRho"),true, TString("DsK"))
     
    workspace = MassFitUtils.Blabla(dataTS, TString("#BsDsstPi"),
                                    PIDcut_dsk,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BsDsstPi"),true, TString("DsK"))
     
    workspace = MassFitUtils.Blabla(dataTS, TString("#BsDsstRho"),
                                    PIDcut_dsk,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BsDsstRho"),true, TString("DsK"))

    workspace = MassFitUtils.Blabla(dataTS, TString("#BsDsPi"),
                                    PIDcut_dspi,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BsDsPi"),true, TString("DsPi"))
    
    workspace = MassFitUtils.Blabla(dataTS, TString("#BsDsRho"),
                                    PIDcut_dspi,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BsDsRho"),true, TString("DsPi"))
    
    workspace = MassFitUtils.Blabla(dataTS, TString("#BsDsstPi"),
                                    PIDcut_dspi,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BsDsstPi"),true, TString("DsPi"))
    
    workspace = MassFitUtils.Blabla(dataTS, TString("#BsDsstRho"),
                                    PIDcut_dspi,
                                    Pcut_down, Pcut_up,
                                    BDTGCut,
                                    Dmass_down, Dmass_up,
                                    mVarTS, TString("lab1_PIDK"),
                                    TString("BsDsstRho"),true, TString("DsPi"))
    
     
     
    
   # print" Expected number of events: "%(number)

   # saveNameTS = TString(saveName)+TString(save)+TString(".root")
   # GeneralUtils.SaveWorkspace(workspace,saveNameTS)
   # workspace.Print()
    
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
                   dest = 'save',
                   default = 'dspi',
                   help = 'save workspace to file work_dspi.root'
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
parser.add_option( '-c', '--cutvariable',
                   dest = 'ProbVar',
                   default = 'lab1_PIDK',
                   help = 'set observable '
                   )


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
    
    runBsDsPiMassFitterOnData( options.debug, options.var, options.ProbVar, options.save )

# -----------------------------------------------------------------------------
