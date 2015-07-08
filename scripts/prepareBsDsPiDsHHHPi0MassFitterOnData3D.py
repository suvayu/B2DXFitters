#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to prepare a mass fit on data for Bd -> D pi                #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python prepareBdMassFitterOnData.py [-d | --debug]                     #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 08 / 06 / 2011                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 02 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# This file is used as both a shell script and as a Python script.

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
        # try to find from where script is executed, use current directory as
        # fallback
        tmp="$(dirname $0)"
        tmp=${tmp:-"$cwd"}
        # convert to absolute path
        tmp=`readlink -f "$tmp"`
        # move up until standalone/setup.sh found, or root reached
        while test \( \! -d "$tmp"/standalone \) -a -n "$tmp" -a "$tmp"\!="/"; do
            tmp=`dirname "$tmp"`
        done
        if test -d "$tmp"/standalone; then
            cd "$tmp"/standalone
            . ./setup.sh
        else
            echo `basename $0`: Unable to locate standalone/setup.sh
            exit 1
        fi
        cd "$cwd"
        unset tmp
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
from B2DXFitters import *
from ROOT import *

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
def prepareBsDsPiMassFitterOnData( debug,
                                   mVar, tVar, terrVar, tagVar, tagOmegaVar, idVar, mdVar,
                                   pidkVar, bdtgVar, pVar, ptVar, ntracksVar,
                                   TagTool, configName,
                                   Data, DPi, DPiPID, MC, MCPID, Signal, SignalPID, CombPID,
                                   save) :

    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    saveNameTS = TString(saveName)+TString(save)+TString(".root")

    #plot settings:
    plotSettings = PlotSettings("plotSettings","plotSettings", "PlotBs2DsPi3DBDTGA", "pdf", 100, true, false, true)
    plotSettings.Print("v")

    config = TString("../data/")+TString(configName)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)
            
    MDSettings.SetMassBVar(TString(mVar))
    MDSettings.SetMassDVar(TString(mdVar))
    MDSettings.SetTimeVar(TString(tVar))
    MDSettings.SetTerrVar(TString(terrVar))
    MDSettings.SetIDVar(TString(idVar))
    MDSettings.SetPIDKVar(TString(pidkVar))
    MDSettings.SetBDTGVar(TString(bdtgVar))
    MDSettings.SetMomVar(TString(pVar))
    MDSettings.SetTrMomVar(TString(ptVar))
    MDSettings.SetTracksVar(TString(ntracksVar))

    MDSettingsMC = MDFitterSettings("MDSettingsMC","MDFSettingsMC",config)
    MDSettingsMC.SetMassBVar(TString(mVar))
    MDSettingsMC.SetMassDVar(TString(mdVar))
    MDSettingsMC.SetTimeVar(TString(tVar))
    MDSettingsMC.SetTerrVar(TString(terrVar))
    MDSettingsMC.SetIDVar(TString(idVar))
    MDSettingsMC.SetPIDKVar(TString(pidkVar))
    MDSettingsMC.SetBDTGVar(TString(bdtgVar))
    MDSettingsMC.SetMomVar(TString(pVar))
    MDSettingsMC.SetTrMomVar(TString(ptVar))
    MDSettingsMC.SetTracksVar(TString(ntracksVar))
    
    
    MDRatio= 1.0-myconfigfile["lumRatio"]
    MURatio= myconfigfile["lumRatio"]

    MDSettings.Print("v")
    MDSettingsMC.Print("v")
    #exit(0)
    tagTool = TagTool
 
    dataTS  = TString(myconfigfile["dataName"])

    workspace = RooWorkspace("workspace","workspace")

    if Data:
        dataNames = [ TString("#Bs2DsPi HHHPi0")]

        for i in range(0,1):
            workspace = MassFitUtils.ObtainData(dataTS, dataNames[i],  MDSettings, TString("BsDsPi"), plotSettings, workspace, debug)
            
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)

    if MC:
        workspace = MassFitUtils.ObtainSpecBack(dataTS, TString("#MC FileName MD HHHPi0"), TString("#MC TreeName"),
                                                MDSettingsMC, TString("BsDsPi HHHPi0"), workspace, true, MDRatio, plotSettings, debug)
        
        workspace = MassFitUtils.ObtainSpecBack(dataTS, TString("#MC FileName MU HHHPi0"), TString("#MC TreeName"),
                                                MDSettingsMC, TString("BsDsPi HHHPi0"), workspace, true, MURatio, plotSettings, debug)
        
        workspace = MassFitUtils.CreatePdfSpecBackground(dataTS, TString("#MC FileName MD HHHPi0"),
                                                         dataTS, TString("#MC FileName MU HHHPi0"),
                                                         MDSettingsMC, workspace, true, plotSettings, debug)
        
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)        
                
    if Signal:
        signalNames = [ TString("#Signal BsDsPi HHHPi0")]

        for i in range(0,1):
            workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), signalNames[i],
                                                  MDSettingsMC, TString("BsDsPi"), false, false, workspace, false,
                                                  1.0, 1.0, plotSettings, debug)

    if MCPID:

        MCDownNames = [TString("MC BsDsPi Down Kaon"),
                       TString("MC BsDsPi Down Pion")]

        MCUpNames = [TString("MC BsDsPi Up Kaon"),
                     TString("MC BsDsPi Up Pion")]
        
        for i in range(0,2):
            
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MD HHHPi0"),
                                                       MDSettings, MCDownNames[i], workspace, plotSettings, debug)
            
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MU HHHPi0"),
                                                       MDSettings, MCUpNames[i], workspace, plotSettings, debug)
            
            workspace.Print()
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
            
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MD HHHPi0"),
                                                       MDSettings, MCDownNames[i], workspace, plotSettings, debug)
            
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MU HHHPi0"),
                                                       MDSettings, MCUpNames[i], workspace, plotSettings, debug)
            
            workspace.Print()
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)

            workspace.Print()
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)

            workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString("#MC FileName MD HHHPi0"),
                                                                     MDSettings, MCDownNames[i], workspace, plotSettings, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString("#MC FileName MU HHHPi0"),
                                                                     MDSettings, MCUpNames[i], workspace, plotSettings, debug)


    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    
    


    if SignalPID:

        signalPIDNames = [ TString("MC BsDsPi HHHPi0 Pion Down"),
                           TString("MC BsDsPi HHHPi0 Pion Up")]

        for i in range(0,2):
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings, signalPIDNames[i], workspace, workspace, plotSettings, debug)
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, signalPIDNames[i], workspace, plotSettings, debug)
                        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()
        
            
        
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)



    if CombPID:
        
        workspaceL = GeneralUtils.LoadWorkspace(TString("/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root"),TString("workspace"),debug)
        #workspaceL = GeneralUtils.LoadWorkspace(TString("work_dspi_dsk_sb.root"),TString("workspace"),debug)
        combNames = [TString("CombPi Pion Down"),
                     TString("CombPi Pion Up"),
                     TString("CombPi Kaon Down"),
                     TString("CombPi Kaon Up")]

        for i in range(0,4):
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings, combNames[i], workspace, workspaceL, plotSettings,  debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, combNames[i], workspace, plotSettings, debug)
            
            workspace.Print()
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)



          
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
         
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
                   default = 'Bs_MassConsDs_M',
                   help = 'set observable '
                   )
parser.add_option( '--tvar',
                   dest = 'tvar',
                   default = 'Bs_LifetimeFit_ctau',
                   help = 'set observable '
                   )
parser.add_option( '--terrvar',
                   dest = 'terrvar',
                   default = 'Bs_LifetimeFit_ctauErr',
                   help = 'set observable '
                   )

parser.add_option( '--tagvar',
                   dest = 'tagvar',
                   default = 'Bs_TAGDECISION_OS',
                   help = 'set observable '
                   )
parser.add_option( '--tagomegavar',
                   dest = 'tagomegavar',
                   default = 'Bs_TAGOMEGA_OS',
                   help = 'set observable '
                   )
parser.add_option( '--idvar',
                   dest = 'idvar',
                   default = 'Bac_ID',
                   help = 'set observable '
                   )
parser.add_option( '--mdvar',
                   dest = 'mdvar',
                   default = 'Ds_MM',
                   help = 'set observable '
                   )

parser.add_option( '--pidkvar',
                   dest = 'pidkvar',
                   default = 'Bac_PIDK',
                   help = 'set observable '
                   )

parser.add_option( '--bdtgvar',
                   dest = 'bdtgvar',
                   default = '',
                   help = 'set observable '
                   )
parser.add_option( '--momvar',
                   dest = 'pvar',
                   default = 'Bac_P',
                   help = 'set observable '
                   )
parser.add_option( '--trmomvar',
                   dest = 'ptvar',
                   default = 'Bac_PT',
                   help = 'set observable '
                   )

parser.add_option( '--ntracksvar',
                   dest = 'ntracksvar',
                   default = 'nTracks',
                   help = 'set observable '
                   )

parser.add_option( '--tagTool',
                   dest = 'tagTool',
                   action = 'store_true',
                   default = False,
                   help = 'add to workspace a lot of tagging observables '
                   )
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsPiConfigForBs2DsKst')

parser.add_option( '--Data',
                   dest = 'Data',
                   action = 'store_true',
                   default = False,
                   help = 'create data'
                   )

parser.add_option( '--DPi',
                   dest = 'DPi',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--DPiPID',
                   dest = 'DPiPID',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--MC',
                   dest = 'MC',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--MCPID',
                   dest = 'MCPID',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--Signal',
                   dest = 'Signal',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--SignalPID',
                   dest = 'SignalPID',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                                      )
parser.add_option( '--CombPID',
                   dest = 'CombPID',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    import sys
    sys.path.append("../data/")
        
    prepareBsDsPiMassFitterOnData(  options.debug, options.mvar, options.tvar, options.terrvar, \
                                    options.tagvar, options.tagomegavar, options.idvar,options.mdvar,\
                                    options.pidkvar, options.bdtgvar, options.pvar, options.ptvar, options.ntracksvar,
                                    options.tagTool, options.configName,
                                    options.Data,
                                    options.DPi, options.DPiPID,
                                    options.MC, options.MCPID,
                                    options.Signal, options.SignalPID,
                                    options.CombPID, options.save)
    

# -----------------------------------------------------------------------------
