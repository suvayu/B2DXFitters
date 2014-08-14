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
from B2DXFitters import *
from ROOT import *

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
def prepareBsDsKMassFitterOnData( debug,
                                  mVar, tVar, terrVar, tagVar, tagOmegaVar, idVar,
                                  mdVar, pidkVar, bdtgVar, pVar, ptVar, ntracksVar,
                                  save, OmegaPdf, TagTool, configName,
                                  Data, DsPi, DsPiPID, MC, MCPID, Signal, SignalPID, CombPID ) : 

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

    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    saveNameTS = TString(saveName)+TString(save)+TString(".root")

    #plot settings:
    plotSettings = PlotSettings("plotSettings","plotSettings", "PlotBs2DsK3DBDTGA", "pdf", 100, true, false, true)
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
        
    if ( OmegaPdf == "no" ):
        tagOmega = false
    else:
        tagOmega = true

    if ( TagTool == "no"):
        tagTool = false
    else:
        tagTool = true

    workspace = RooWorkspace("workspace","workspace")
    dataTS  = TString(myconfigfile["dataName"])
    
    
    if Data:     
    	workspace = MassFitUtils.ObtainData(dataTS, TString("#Bs2DsK HHHPi0"),  MDSettings, TString("BsDsK"), plotSettings, workspace, debug)
        
        
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()


                
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()


    if MC:
        workspace = MassFitUtils.ObtainSpecBack(dataTS, 
                                                TString("#MC FileName MD HHHPi0"), TString("#MC TreeName"),MDSettingsMC, 
                                                TString("BsDsK"), workspace, true, MDRatio, plotSettings, debug)

        workspace = MassFitUtils.ObtainSpecBack(dataTS, 
                                                TString("#MC FileName MU HHHPi0"), TString("#MC TreeName"),MDSettingsMC, 
                                                TString("BsDsK"), workspace, true, MURatio, plotSettings, debug)
  
        workspace = MassFitUtils.CreatePdfSpecBackground(dataTS, TString("#MC FileName MD HHHPi0"),
                                                         dataTS, TString("#MC FileName MU HHHPi0"),
                                                         MDSettingsMC, workspace, true, plotSettings, debug)
       
        
    workspace.Print()

    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)


    if MCPID:

        MCDownNames = [TString("MC BsDsK Kaon Down Str20"),
                       TString("MC BsDsK Pion Down Str20")]

        MCUpNames = [TString("MC BsDsK Kaon Up Str20"),
                     TString("MC BsDsK Pion Up Str20")]
        
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
    
    if Signal:
   	workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), TString("#Signal BsDsK HHHPi0"),
                                                  MDSettings, TString("BsDsK"), false, false, workspace, false,
                                                  MDSettings.GetLumDown(), MDSettings.GetLumUp(), plotSettings, debug)

        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)



    if SignalPID:

        signalPIDNames = [ TString("MC BsDsK HHHPi0 Kaon Down Str20"),
                           TString("MC BsDsK HHHPi0 Kaon Up Str20")]

        for i in range(0,2):
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings, signalPIDNames[i], workspace, workspace, plotSettings, debug)
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, signalPIDNames[i], workspace, plotSettings, debug)
                        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()

    if CombPID:
        
        workspaceL = GeneralUtils.LoadWorkspace(TString("/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsK_5358.root"),TString("workspace"),debug)
        combNames = [TString("CombK Pion Down Str20"),
                     TString("CombK Pion Up Str20"),
                     TString("CombK Kaon Down Str20"),
                     TString("CombK Kaon Up Str20")]

        for i in range(0,4):
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings, combNames[i], workspace, workspaceL, plotSettings,  debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, combNames[i], workspace, plotSettings, debug)
            
            workspace.Print()
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)


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
                   default = 'BDTGResponse_1',
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
                   default = 'Bs2DsKConfigForBs2DsKst'
                   )

parser.add_option( '--Data',
                   dest = 'Data',
                   action = 'store_true',
                   default = False,
                   help = 'create data'
                   )

parser.add_option( '--DsPi',
                   dest = 'DsPi',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--DsPiPID',
                   dest = 'DsPiPID',
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
        
    prepareBsDsKMassFitterOnData(  options.debug, options.mvar, options.tvar, options.terrvar, \
                                   options.tagvar, options.tagomegavar, options.idvar, options.mdvar,\
                                   options.pidkvar, options.bdtgvar, options.pvar, options.ptvar, options.ntracksvar,
                                   options.save, options.tagOmegaPdf,
                                   options.tagTool, options.configName,
                                   options.Data,
                                   options.DsPi, options.DsPiPID,
                                   options.MC, options.MCPID,
                                   options.Signal, options.SignalPID,
                                   options.CombPID)

# -----------------------------------------------------------------------------

