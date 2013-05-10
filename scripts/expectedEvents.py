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

PIDcut = 10
histname = "MyPionMisID_10"
PIDmisscut= 0 
pPIDcut = 5
Pcut_down = 2000.0
Pcut_up = 100000000000.0

Dmass_down =1930
Dmass_up = 2015
DDmass_down = 1830
DDmass_up = 1910

# DATA FILES
#filesDir      = '../data'
dataName      = '../data/config_ExpectedEvents.txt'
saveName      = 'work_'

# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def runBsDsPiMassFitterOnData( debug, mVar, mProbVar, save, BDTG, mode ) :

    dataTS = TString(dataName)
    mVarTS = TString(mVar)
    mProbVarTS = TString(mProbVar)
    modeTS = TString(mode)

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

    if modeTS == "BDPi":
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BdDPi BsHypo PhiPi"), TString("#BdDPi BdHypo"),
                                            TString("#PID2m2"), TString("MyPionMisID_m2"),
                                            TString("#PID2m2"), TString("MyKaonEff_m2"),
                                            #//TString("#PID2m2"), TString("MyPionMisID_m2"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BdDPi"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BdDPi BsHypo KstK"), TString("#BdDPi BdHypo"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID2m2"), TString("MyKaonEff_m2"),
                                            #//TString("#PID"), TString("MyPionMisID_5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BdDPi"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BdDPi BsHypo NonRes"), TString("#BdDPi BdHypo"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyKaonEff_5"),
                                            #TString("#PID"), TString("MyPionMisID_5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BdDPi"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BdDPi BsHypo KPiPi"), TString("#BdDPi BdHypo"),
                                            TString("#PID"), TString("MyKaonMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_10"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BdDPi"),TString("kpipi"))
        

    elif modeTS == "LbLcPi":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi"), TString("#LbLcPi"),
                                            TString("#PID"), TString("MyKaonEff_0"),
                                            TString("#PIDp"), TString("MyProtonMisID_pK5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbLcPi"),TString("kpipi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi"), TString("#LbLcPi"), TString("#PIDp"),
                                            TString("MyProtonMisID_pK5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbLcPi"),TString("pipipi"))
    elif modeTS == "BsDsPi":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsPi"), TString("#BsDsPi"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsPi"),TString("kkpi"))
        

 #   number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsPi"), TString("#BsDsPi"),
 #                                       TString("#PID"), TString("MyPionMisID_10"),
 #                                       TString("#PID"), TString("MyPionMisID_10"),
 #                                       Pcut_down, Pcut_up,
 #                                       BDTGCut,
 #                                       Dmass_down, Dmass_up,
 #                                       mVarTS, mProbVarTS,
 #                                       TString("BsDsPi"),TString("kpipi"))

    elif modeTS == "BDK":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BDK"), TString("#BDK"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            DDmass_down, DDmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BDK"),TString("kpipi"))
    elif modeTS == "BsDsK":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsK"), TString("#BsDsK"),
                                            TString("#PID"), TString("MyPionMisID_0"),
                                            TString("#PID"), TString("MyPionMisID_0"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            DDmass_down, DDmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsK"),TString("kkpi"))
        
        

  #  number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsPi"), TString("#BsDsPi"),
  #                                      TString("#PID"), TString("MyPionMisID_10"),
  #                                      TString("#PID"), TString("MyPionMisID_10"),
  #                                      Pcut_down, Pcut_up,
  #                                      BDTGCut,
  #                                      Dmass_down, Dmass_up,
  #                                      mVarTS, mProbVarTS,
  #                                      TString("BsDsPi"),TString("pipipi"))
    elif modeTS == "LbDsp":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbDsp"), TString("#LbDsp"),
                                            TString("#PIDp2"), TString("MyProtonEff_KPi10;1"),
                                            TString("#PID Dsp"),TString("MyProtonEff_p15_pK15"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbDsp"),TString("dupa"))
    elif modeTS == "LbDsstp":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbDsstp"), TString("#LbDsstp"), TString("#PID Dsp"),
                                            TString("MyProtonEff_p15_pK15"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbDsstp"),TString("dupa"))

    
    
    
                                                                                                                                                                                                                                                        
    
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
parser.add_option( '--BDTG',
                   dest = 'BDTG',
                   default = 'BDTGA',
                   help = 'Set BDTG range '
                   )
parser.add_option( '--mode',
                   dest = 'mode',
                   default = 'BDPi',
                   help = 'Set BDTG range '
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
    
    runBsDsPiMassFitterOnData( options.debug, options.var, options.ProbVar, options.save, options.BDTG, options.mode )

# -----------------------------------------------------------------------------
