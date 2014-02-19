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

# FIT CONFIGURATION

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
def runExpectedYields( debug, mVar, mProbVar, save, BDTG, mode ) :

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

    plotSettings = PlotSettings("plotSettings","plotSettings", "PlotBs2DsPi3DBDTGA", "pdf", 100, true, false, true)
    plotSettings.Print("v")

    if modeTS == "BDPi":
        
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
        

    elif modeTS == "LbLcPi":
        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi PhiPi"), TString("#LbLcPi PhiPi"),
                                            TString("#PID2m2"), TString("MyKaonEff_m2"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPim2"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbLcPi"),TString("kkpi"))

        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi KstK"), TString("#LbLcPi KstK"),
                                            TString("#PID2m2"), TString("MyKaonEff_m2"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi5"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbLcPi"),TString("kkpi"))

        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi NonRes"), TString("#LbLcPi NonRes"),
                                            TString("#PID"), TString("MyKaonEff_5"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi5"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbLcPi"),TString("kkpi"))
        
        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi KPiPi"), TString("#LbLcPi KPiPi"),
                                            TString("#PID2m2"), TString("MyKaonMisID_5_p10"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbLcPi"),TString("kpipi"))

        number = MassFitUtils.ExpectedYield(dataTS, TString("#LbLcPi PiPiPi"), TString("#LbLcPi PiPiPi"),
                                            TString("#PID"), TString("MyKaonEff_5"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            TString("#PIDp3"), TString("MyProtonMisID_pKm5"), #_KPi10"),
                                            Pcut_down, Pcut_up,
                                            BDTG_down, BDTG_up,
                                            Dmass_down, Dmass_up,
                                            mVarTS, mProbVarTS,
                                            TString("LbLcPi"),TString("pipipi"))
        
        
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
    
    runExpectedYields( options.debug, options.var, options.ProbVar, options.save, options.BDTG, options.mode )

# -----------------------------------------------------------------------------
