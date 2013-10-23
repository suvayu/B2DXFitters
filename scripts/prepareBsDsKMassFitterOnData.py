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
# settings for running without GaudiPython
# -----------------------------------------------------------------------------
""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.

# make sure the environment is set up properly
if test -n "$CMTCONFIG" \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersDict.so \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersLib.so; then
    # all ok, software environment set up correctly, so don't need to do
    # anything
    true
else
    if test -n "$CMTCONFIG"; then
        # clean up incomplete LHCb software environment so we can run
        # standalone
        echo Cleaning up incomplete LHCb software environment.
        PYTHONPATH=`echo $PYTHONPATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export PYTHONPATH
        LD_LIBRARY_PATH=`echo $LD_LIBRARY_PATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
	export LD_LIBRARY_PATH
        exec env -u CMTCONFIG -u B2DXFITTERSROOT "$0" "$@"
    fi
    # automatic set up in standalone build mode
    if test -z "$B2DXFITTERSROOT"; then
        cwd="$(pwd)"
        if test -z "$(dirname $0)"; then
            # have to guess location of setup.sh
            cd ../standalone
            . ./setup.sh
            cd "$cwd"
        else
            # know where to look for setup.sh
            cd "$(dirname $0)"/../standalone
            . ./setup.sh
            cd "$cwd"
        fi
        unset cwd
    fi
fi
# figure out which custom allocators are available
# prefer jemalloc over tcmalloc
for i in libjemalloc libtcmalloc; do
    for j in `echo "$LD_LIBRARY_PATH" | tr ':' ' '` \
            /usr/local/lib /usr/lib /lib; do
        for k in `find "$j" -name "$i"'*.so.?' | sort -r`; do
            if test \! -e "$k"; then
                continue
            fi
            echo adding $k to LD_PRELOAD
            if test -z "$LD_PRELOAD"; then
                export LD_PRELOAD="$k"
                break 3
            else
                export LD_PRELOAD="$LD_PRELOAD":"$k"
                break 3
            fi
        done
    done
done
# set batch scheduling (if schedtool is available)
schedtool="`which schedtool 2>/dev/zero`"
if test -n "$schedtool" -a -x "$schedtool"; then
    echo "enabling batch scheduling for this job (schedtool -B)"
    schedtool="$schedtool -B -e"
else
    schedtool=""
fi

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
import B2DXFitters
import ROOT
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc
gROOT.SetBatch()


# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

saveName      = 'work_'


#------------------------------------------------------------------------------
def prepareBsDsKMassFitterOnData( debug, mVar, mdVar, tVar, tagVar, tagOmegaVar, idVar, mProbVar, save, OmegaPdf, TagTool, configName ) : 

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
                             
    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]) ,TString("#BsDsK KKPi NonRes"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS, mProbVarTS,
                                        TString("BsDsK"),tagTool,
                                        NULL,
                                        debug)

    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]) ,TString("#BsDsK KKPi KstK"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS, mProbVarTS,
                                        TString("BsDsK"),tagTool,
                                        NULL,
                                        debug)
    
    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]) ,TString("#BsDsK KKPi PhiPi"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS, mProbVarTS,
                                        TString("BsDsK"),tagTool,
                                        NULL,
                                        debug)
    
       

    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]), TString("#BsDsK KPiPi"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS, mProbVarTS,
                                        TString("BsDsK"),tagTool,
                                        workspace,
                                        debug)
    
    workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]), TString("#BsDsK PiPiPi"),
                                        myconfigfile["PIDBach"],
                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS, mProbVarTS,
                                        TString("BsDsK"),tagTool,
                                        workspace,
                                        debug)
    
    workspace = MassFitUtils.ObtainMissForBsDsK(TString(myconfigfile["dataName"]),TString("#BsDsPi KKPi NonRes"),
                                                myconfigfile["PIDChild"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsPi"), workspace, tagOmega, debug)

    workspace = MassFitUtils.ObtainMissForBsDsK(TString(myconfigfile["dataName"]),TString("#BsDsPi KKPi KstK"),
                                                myconfigfile["PIDChild"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsPi"), workspace, tagOmega, debug)

    workspace = MassFitUtils.ObtainMissForBsDsK(TString(myconfigfile["dataName"]),TString("#BsDsPi KKPi PhiPi"),
                                                myconfigfile["PIDChild"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsPi"), workspace, tagOmega, debug)
    
    
    workspace = MassFitUtils.ObtainMissForBsDsK(TString(myconfigfile["dataName"]),TString("#BsDsPi KPiPi"),
                                                myconfigfile["PIDChild"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsPi"),workspace, tagOmega, debug)
    
    workspace = MassFitUtils.ObtainMissForBsDsK(TString(myconfigfile["dataName"]),TString("#BsDsPi PiPiPi"),
                                                myconfigfile["PIDChild"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsPi"),workspace, tagOmega, debug)
    
    workspace = MassFitUtils.ObtainSpecBack(TString(myconfigfile["dataName"]), TString("#MC FileName MD"), TString("#MC TreeName"),
                                            myconfigfile["PIDBach"], myconfigfile["PIDChild"], myconfigfile["PIDProton"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                            mVarTS, mdVarTS, mProbVarTS,
                                            TString("BsDsK"),
                                            workspace, false, tagOmega, debug)


    workspace = MassFitUtils.ObtainSpecBack(TString(myconfigfile["dataName"]), TString("#MC FileName MU"), TString("#MC TreeName"),
                                            myconfigfile["PIDBach"], myconfigfile["PIDChild"], myconfigfile["PIDProton"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                            mVarTS, mdVarTS, mProbVarTS,
                                            TString("BsDsK"),
                                            workspace, false, tagOmega, debug)
    
    workspace = MassFitUtils.CreatePdfSpecBackground(TString(myconfigfile["dataName"]), TString("#MC FileName MD"),
                                                     TString(myconfigfile["dataName"]), TString("#MC FileName MU"),
                                                     mVarTS,
                                                     myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                     workspace, tagOmega, debug)
    
    
    workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), TString("#Signal BsDsK"),
                                          myconfigfile["PIDBach"],
                                          myconfigfile["PDown"], myconfigfile["PUp"],
                                          myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                          myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                          myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                          myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                          mVarTS, mdVarTS, tVarTS, tagVarTS,
                                          tagOmegaVarTS, idVarTS,
                                          mProbVarTS,
                                          TString("BsDsK"),
                                          true, false,
                                          workspace, debug)
    
#    workspace = MassFitUtils.ObtainSignal(myconfigfile["dataName"], TString("#Signal BdDsK"),
#                                          myconfigfile["PIDBach"],
#                                          myconfigfile["PDown"], myconfigfile["PUp"],
#                                          myconfigfile["BDTG"],
#                                          myconfigfile["DMassDown"], myconfigfile["DMassUp"],
#                                          myconfigfile["BMassDown"], myconfigfile["BMassUp"],
#                                          myconfigfile["TimeDown"], myconfigfile["TimeUp"],
#                                          mVarTS, tVarTS, tagVarTS,
#                                          tagOmegaVarTS, idVarTS,
#                                          mProbVarTS,
#                                          TString("BdDsK"), workspace, tagOmega, debug)

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
                   default = 'dsk',
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
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
                   help = 'set observable for PID '
                   )
parser.add_option( '--tagOmegaPdf',
                  dest = 'tagOmegaPdf',
                  default = "no",
                  help = 'create RooKeysPdf for TagOmega '
                  )
parser.add_option( '--tagTool',
                   dest = 'tagTool',
                   default = "no",
                   help = 'add to workspace a lot of tagging observables (for Matt) '
                   )
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsKConfigForNominalMassFit')


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    import sys
    sys.path.append("../data/")
        
    prepareBsDsKMassFitterOnData(  options.debug, options.mvar, options.mdvar, options.tvar, \
                                   options.tagvar, options.tagomegavar, options.idvar,\
                                   options.ProbVar, options.save, options.tagOmegaPdf,
                                   options.tagTool, options.configName)

# -----------------------------------------------------------------------------
