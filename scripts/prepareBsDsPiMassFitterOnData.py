#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to prepare a mass fit on data for Bd -> D pi                    #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python prepareBdMassFitterOnData.py [-d | --debug]                         #
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

saveName      = 'work_'



#------------------------------------------------------------------------------
def prepareBsDsPiMassFitterOnData( debug, mVar, mdVar, tVar, tagVar, tagOmegaVar, idVar, mProbVar, save, OmegaPdf, TagTool, configName ) :

    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()
    
    print "=========================================================="
    print "PREPARING WORKSPACE IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="
                                                                    

    #dataTS = TString(dataName)
    mVarTS = TString(mVar)
    mdVarTS = TString(mdVar)
    tVarTS = TString(tVar)
    tagVarTS = TString(tagVar)
    tagOmegaVarTS = TString(tagOmegaVar)
    idVarTS = TString(idVar)
    mProbVarTS = TString(mProbVar)

    if ( OmegaPdf == "no" ):
        tagOmega = false
    else:
        tagOmega = true

    if ( TagTool == "no"):
        tagTool = false
    else:
        tagTool = true
                           
    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]),TString("#BsDsPi KKPi NonRes"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS, 
                                        mProbVarTS,
                                        TString("BsDsPi"), tagTool, NULL, debug)
    
    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]),TString("#BsDsPi KKPi PhiPi"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS,
                                        mProbVarTS,
                                        TString("BsDsPi"), tagTool, workspace, debug)

    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]),TString("#BsDsPi KKPi KstK"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS,
                                        mProbVarTS,
                                        TString("BsDsPi"),tagTool, workspace, debug)

    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]),TString("#BsDsPi KPiPi"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS,
                                        mProbVarTS,
                                        TString("BsDsPi"),tagTool, workspace, debug)

    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]),TString("#BsDsPi PiPiPi"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS,
                                        mProbVarTS,
                                        TString("BsDsPi"),tagTool, workspace, debug)
    
                                        
    workspace = MassFitUtils.ObtainMissForBsDsPi(TString(myconfigfile["dataName"]),TString("#BdPi"),
                                                 myconfigfile["PIDChild"], 
                                                 myconfigfile["PDown"], myconfigfile["PUp"],
                                                 myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                 myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                 myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                 mVarTS, mdVarTS, mProbVarTS,
                                                 TString("Bd2DPi"),workspace, tagOmega, debug)

    workspace = MassFitUtils.ObtainSpecBack(TString(myconfigfile["dataName"]), TString("#MC FileName MD"), TString("#MC TreeName"),
                                            myconfigfile["PIDBach"], myconfigfile["PIDChild"], myconfigfile["PIDProton"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                            mVarTS, mdVarTS, mProbVarTS,
                                            TString("BsDsPi"),
                                            workspace, false, tagOmega, debug)
    
    workspace = MassFitUtils.ObtainSpecBack(TString(myconfigfile["dataName"]), TString("#MC FileName MU"), TString("#MC TreeName"),
                                            myconfigfile["PIDBach"], myconfigfile["PIDChild"], myconfigfile["PIDProton"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                            mVarTS, mdVarTS, mProbVarTS,
                                            TString("BsDsPi"),
                                            workspace, false, tagOmega, debug)

    workspace = MassFitUtils.CreatePdfSpecBackground(myconfigfile["dataName"], TString("#MC FileName MD"),
                                                     myconfigfile["dataName"], TString("#MC FileName MU"),
                                                     mVarTS, mdVarTS,
                                                     myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                     workspace, tagOmega, debug)
    
    
    #workspace = RooWorkspace("workspace","workspace")
    workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), TString("#Signal BsDsPi"),
                                          myconfigfile["PIDBach"],
                                          myconfigfile["PDown"], myconfigfile["PUp"],
                                          myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                          myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                          myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                          myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                          mVarTS, mdVarTS, tVarTS, tagVarTS,
                                          tagOmegaVarTS, idVarTS, mProbVarTS,
                                          TString("BsDsPi"),
                                          true, false,
                                          workspace, debug)

    
  #  workspace = MassFitUtils.ObtainSignal(myconfigfile["dataName"], TString("#Signal BdDsPi"),
  #                                        myconfigfile["PIDBach"],
  #                                        myconfigfile["PDown"], myconfigfile["PUp"],
  #                                        myconfigfile["BDTG"],
  #                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
  #                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
  #                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
  #                                        mVarTS, tVarTS, tagVarTS,
  #                                        tagOmegaVarTS, idVarTS,
  #                                        mProbVarTS, TString("BdDsPi"), workspace, xsdebug)
        

    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()
    
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
parser.add_option( '--mvar',
                   dest = 'mvar',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
                   )
parser.add_option( '--mdvar',
                   dest = 'mdvar',
                   default = 'lab2_MM',
                   help = 'set observable '
                   )
parser.add_option( '--tvar',
                   dest = 'tvar',
                   default = 'lab0_LifetimeFit_ctau',
                   help = 'set observable '
                   )
parser.add_option( '--tagvar',
                   dest = 'tagvar',
                   default = 'lab0_BsTaggingTool_TAGDECISION_OS',
                   help = 'set observable '
                   )
parser.add_option( '--tagomegavar',
                   dest = 'tagomegavar',
                   default = 'lab0_BsTaggingTool_TAGOMEGA_OS',
                   help = 'set observable '
                   )
parser.add_option( '--idvar',
                   dest = 'idvar',
                   default = 'lab1_ID',
                   help = 'set observable '
                   )
parser.add_option( '-c', '--cutvariable',
                   dest = 'ProbVar',
                   default = 'lab1_PIDK',
                   help = 'set observable '
                   )
parser.add_option( '--tagOmegaPdf',
                   dest = 'tagOmegaPdf',
                   default = "no",
                   help = 'create RooKeysPdf for TagOmega '
                   )
parser.add_option( '--tagTool',
                   dest = 'tagTool',
                   default = "no",
                   help = 'add to workspace a lot of tagging observables '
                   )
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsPiConfigForNominalMassFit')


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    import sys
    sys.path.append("../data/")
        
    prepareBsDsPiMassFitterOnData(  options.debug, options.mvar, options.mdvar, options.tvar, \
                                options.tagvar, options.tagomegavar, options.idvar,\
                                options.ProbVar, options.save, options.tagOmegaPdf, options.tagTool, options.configName )

# -----------------------------------------------------------------------------
