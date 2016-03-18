#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to obtain misID backgrounds yields                          #
#                                                                             #
#   Example usage:                                                            #
#      python expectedEvents.py --mode BDPi --BDTG BDTGA                      #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 02 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

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
print "Load necessary libraries"
import B2DXFitters
import ROOT
from B2DXFitters import *
from ROOT import *
from optparse import OptionParser
from math     import pi, log
import os, sys, gc
# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------
# MISCELLANEOUS
bName = 'B_{s}'
gROOT.SetBatch()

#------------------------------------------------------------------------------
def runExpectedYields(config, debug, mode ) :


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

    config = TString("../data/")+TString(configName)+TString(".py")
    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings",True)

    MDSettings = mdt.getConfig()
    MDSettings.Print("v")

    #plot settings:                                                                                                                                                                            
    dirPlot = "Plot"
    extPlot = "pdf"
    if myconfigfile.has_key("ControlPlots"):
        if myconfigfile["ControlPlots"].has_key("Directory"):
            dirPlot = myconfigfile["ControlPlots"]["Directory"]
            if not os.path.exists(dirPlot):
                os.makedirs(dirPlot)
        if myconfigfile["ControlPlots"].has_key("Extension"):
            extPlot = myconfigfile["ControlPlots"]["Extension"]

    plotSettings = PlotSettings("plotSettings","plotSettings", TString(dirPlot), extPlot , 100, True, False, True)
    plotSettings.Print("v")


    modeTS = TString(mode) 
    dataTS  = TString(myconfigfile["dataName"])
    decay = TString(myconfigfile["Decay"])

    if modeTS == "Bd2DPi":
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BdDPi BsHypo PhiPi"), TString("#BdDPi BdHypo"),
                                            TString("#PID2m2"), TString("MyKaonEff_m2"),
                                            TString("#PID"), TString("MyPionMisID_10"),
                                            TString("#PID2m2"), TString("MyPionMisID_10_pKm5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BdDPi"),TString("kkpi"))
        #exit(0)
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BdDPi BsHypo KstK"), TString("#BdDPi BdHypo"),
                                            TString("#PID2m2"), TString("MyKaonEff_m2"),
                                            TString("#PID"), TString("MyPionMisID_10"),
                                            TString("#PID2m2"), TString("MyPionMisID_10_pKm5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BdDPi"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BdDPi BsHypo NonRes"), TString("#BdDPi BdHypo"),
                                            TString("#PID"), TString("MyKaonEff_5"),
                                            TString("#PID"), TString("MyPionMisID_10"),
                                            TString("#PID2m2"), TString("MyPionMisID_10_pKm5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BdDPi"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BdDPi BsHypo KPiPi"), TString("#BdDPi BdHypo"),
                                            TString("#PID"), TString("MyKaonMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_10"),
                                            TString("#PID"), TString("MyPionMisID_10"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BdDPi"),TString("kpipi"))
        

    elif modeTS == "Lb2LcPi":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi PhiPi"), TString("#LbLcPi PhiPi"),
                                            TString("#PID Kaon 2012"), TString("MyKaonEff_m2"),
                                            TString("#PID Proton 2012"), TString("MyProtonMisID_pKm5"), # _KPim2"),
                                            TString("#PID Proton 2012"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            MDSettings,
                                            plotSettings,
                                            TString("Lb2LcPi, pKPi"),TString("Bs2DsPi, PhiPi"), debug)

        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi KstK"), TString("#LbLcPi KstK"),
                                            TString("#PID Kaon 2012"), TString("MyKaonEff_m2"),
                                            TString("#PID Proton 2012"), TString("MyProtonMisID_pKm5"), #_KPi5"),
                                            TString("#PID Proton 2012"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            MDSettings,
                                            plotSettings,
                                            TString("LbLcPi, pKPi"),TString("Bs2DsPi, KstK"), debug)

        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi NonRes"), TString("#LbLcPi NonRes"),
                                            TString("#PID Kaon 2012"), TString("MyKaonEff_5"),
                                            TString("#PID Proton 2012"), TString("MyProtonMisID_pKm5"), #_KPi5"),
                                            TString("#PID Proton 2012"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            MDSettings,
                                            plotSettings,
                                            TString("LbLcPi, pKPi"),TString("Bs2DsPi, NonRes"), debug)
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi KPiPi"), TString("#LbLcPi KPiPi"),
                                            TString("#PID Kaon 2012"), TString("MyKaonMisID_5_p10"),
                                            TString("#PID Proton 2012"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            TString("#PID Proton 2012"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            MDSettings,
                                            plotSettings,
                                            TString("LbLcPi, pKPi"),TString("Bs2DsPi, KPiPi"), debug)
        
        
    elif modeTS == "BsDsPi":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsPi PhiPi"), TString("#BsDsPi PhiPi"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsPi"),TString("kkpi"))

        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsPi KstK"), TString("#BsDsPi KstK"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsPi"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsPi NonRes"), TString("#BsDsPi NonRes"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsPi"),TString("kkpi"))
        

        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsPi KPiPi"), TString("#BsDsPi KPiPi"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsPi"),TString("kpipi"))
    
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsPi PiPiPi"), TString("#BsDsPi PiPiPi"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            TString("#PID"), TString("MyPionMisID_5"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsPi"),TString("pipipi"))
        
        

    elif modeTS == "BDK":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BDK"), TString("#BDK"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            DDmass_down, DDmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BDK"),TString("kpipi"))
    elif modeTS == "BsDsK":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsK PhiPi"), TString("#BsDsK PhiPi"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsK"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsK KstK"), TString("#BsDsK KstK"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsK"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsK NonRes"), TString("#BsDsK NonRes"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsK"),TString("kkpi"))
        
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsK KPiPi"), TString("#BsDsK KPiPi"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsK"),TString("kpipi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#BsDsK PiPiPi"), TString("#BsDsK PiPiPi"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            TString("#PID"), TString("MyKaonMisID_0"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("BsDsK"),TString("pipipi"))
                        
        

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
#parser.add_option( '-v', '--variable',
#                   dest = 'var',
#                   default = 'lab0_MassFitConsD_M',
#                   help = 'set observable '
#                   )
#parser.add_option( '-c', '--cutvariable',
#                   dest = 'ProbVar',
#                   default = 'lab1_PIDK',
#                   help = 'set observable '
#                   )
#parser.add_option( '--BDTG',
#                   dest = 'BDTG',
#                   default = 'BDTGA',
#                   help = 'Set BDTG range '
#                   )
parser.add_option( '--mode',
                   dest = 'mode',
                   default = 'BDPi',
                   help = 'Set BDTG range '
                   )
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsKConfigForNominalMassFitBDTGA'
                   )


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    config = options.configName
    last = config.rfind("/")
    directory = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]

    import sys
    sys.path.append(directory)

    runExpectedYields( configName , options.debug, options.mode )

# -----------------------------------------------------------------------------
