#!/usr/bin/env python    
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC fit for the CP asymmetry observables        #
#   in Bs -> Ds K                                                             #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBs2DsKCPAsymmObsFitterOnData.py [-d -s]                      #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#   Author: Manuel Schiller                                                   #
#   Author: Agnieszka Dziurda                                                 #
#   Author: Vladimir Vava Gligorov                                            #
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
import B2DXFitters
import ROOT
from B2DXFitters import *
from ROOT import *

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc

gROOT.SetBatch()

AcceptanceFunction       =  'PowLawAcceptance'#BdPTAcceptance'  # None/BdPTAcceptance/DTAcceptanceLHCbNote2007041

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------
              
#------------------------------------------------------------------------------
def setConstantIfSoConfigured(var,myconfigfile) :
    if var.GetName() in myconfigfile["constParams"] : var.setConstant()

#------------------------------------------------------------------------------
def runBdGammaFitterOnData(debug, wsname,
                           tVar, terrVar, idVar, mVar,
                           pathName, treeName,
                           configName, configNameMD, mode, combo) :
    
    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option] 
    print "=========================================================="
 

    myconfigfilegrabber2 = __import__(configNameMD,fromlist=['getconfig']).getconfig
    myconfigfileMD = myconfigfilegrabber2()

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfileMD :
        if option == "constParams" :
            for param in myconfigfileMD[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfileMD[option]
    print "=========================================================="

    # tune integrator configuration
                            
    plotSettings = PlotSettings("plotSettings","plotSettings", "Plot", "pdf", 100, true, false, true)
    plotSettings.Print("v")

    config = TString("../data/")+TString(configNameMD)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettings.SetTimeVar(TString(tVar))
    MDSettings.SetTerrVar(TString(terrVar))
    MDSettings.SetIDVar(TString(idVar))
    MDSettings.SetMassBVar(TString(mVar))
    
    config = TString("../data/")+TString(configNameMD)+TString(".py")
    MDSettingsCombo = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettingsCombo.SetMassBVar(TString(mVar))
    MDSettingsCombo.SetMassDVar(TString("lab2_MM"))
    MDSettingsCombo.SetTimeVar(TString(tVar))
    MDSettingsCombo.SetTerrVar(TString(terrVar))
    MDSettingsCombo.SetIDVar(TString(idVar))
    MDSettingsCombo.SetPIDKVar(TString("lab1_PIDK"))
    MDSettingsCombo.SetBDTGVar(TString("BDTGResponse_1"))
    MDSettingsCombo.SetMomVar(TString("lab1_P"))
    MDSettingsCombo.SetTrMomVar(TString("lab1_PT"))
    MDSettingsCombo.SetTracksVar(TString("nTracks"))
    MDSettingsCombo.SetMassBRange(5700, 7000)

    MDSettings.Print("v")
    workspaceW = [] 
    namePart = TString(mode)
    if mode == "BsDsPi":
        modeTS = TString("Bs2DsPi")
    if mode == "BsDsK":
        modeTS = TString("Bs2DsK") 
    
    if combo:
        dataTS  = TString(myconfigfileMD["dataName"])
        workCombo = RooWorkspace("workCombo","workCombo")
        dataNames = [ TString("#") + modeTS + TString(" NonRes"),
                      TString("#") + modeTS + TString(" PhiPi"),
                      TString("#") + modeTS + TString(" KstK"),
                      TString("#") + modeTS + TString(" KPiPi"),
                      TString("#") + modeTS + TString(" PiPiPi")]

        for i in range(0,5):
            workCombo = MassFitUtils.ObtainData(dataTS, dataNames[i],  MDSettingsCombo, TString(mode), plotSettings, workCombo, debug)
            
        dataCombo = []
        mDs = ["nonres","phipi","kstk","kpipi","pipipi"]
        MDs = ["NonRes", "PhiPi", "KstK", "KPiPi", "PiPiPi"]
        sample = [TString("up"),TString("down")]
        nEntriesCombo = []
        for m in mDs:
            for i in range(0,2):
                datasetTS = TString("dataSet")+namePart+TString("_")+sample[i]+TString("_")+TString(m)
                dataCombo.append(GeneralUtils.GetDataSet(workCombo,datasetTS, debug))
                size = dataCombo.__len__()
                nEntriesCombo.append(dataCombo[size-1].numEntries())
                print "Data set: %s with number of events: %s"%(dataCombo[size-1].GetName(),nEntriesCombo[size-1])
                
        sample = [TString("both"),TString("both")]
        for i in range(1,10):
            print "Add data set: %s"%(dataCombo[i].GetName())
            dataCombo[0].append(dataCombo[i])

        mistagPDF = SFitUtils.CreateMistagTemplates(dataCombo[0],MDSettingsCombo,40,true, debug)    
                
    else:    
        workspaceW.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, namePart,
                                                         true, false, false, debug))
        
        workspaceW[0].Print()
          
        # Data set
        #-----------------------
        nameData = TString("dataSet_time_")+namePart
        dataWA = GeneralUtils.GetDataSet(workspaceW[0],   nameData, debug)
        nEntries = dataWA.numEntries()                               
        dataWA.Print("v")
        mistagPDF = SFitUtils.CreateMistagTemplates(dataWA,MDSettings,40,true, debug)


       
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser(_usage)

parser.add_option('-d', '--debug',
                  dest    = 'debug',
                  default = False,
                  action  = 'store_true',
                  help    = 'print debug information while processing'
                  )
parser.add_option('-s', '--save',
                  dest    = 'wsname',
                  metavar = 'WSNAME',
                  default = 'WS_Time_DsPi.root',  
                  help    = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                  )
parser.add_option( '--tvar',
                   dest = 'tvar',
                   default = 'lab0_LifetimeFit_ctau',
                   help = 'set observable '
                   )
parser.add_option( '--terrvar',
                   dest = 'terrvar',
                   default = 'lab0_LifetimeFit_ctauErr',
                   help = 'set observable '
                   )

parser.add_option( '--idvar',
                   dest = 'idvar',
                   default = 'lab1_ID',
                   help = 'set observable '
                   )

parser.add_option( '--mvar',
                   dest = 'mvar',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
                   )

parser.add_option( '--pathName',
                   dest = 'pathName',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsPi_all_both.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--treeName',
                   dest = 'treeName',
                   default = 'merged',
                   help = 'name of the workspace'
                   )
parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsPiConfigForNominalDMSFit')

parser.add_option( '--configNameMDFitter',
                   dest = 'configNameMD',
                   default = 'Bs2DsPiConfigForNominalMassFitBDTGA')

parser.add_option( '--mode',
                   dest = 'mode',
                   default = 'BsDsPi')

parser.add_option('--combo',
                  dest    = 'combo',
                  default = False,
                  action  = 'store_true',
                  help    = 'obtain mistag template for combinatorial'
                  )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    (options, args) = parser.parse_args()

    if len(args) > 0 :
        parser.print_help()
        exit(-1)

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    print options
    print "=========================================================="

    import sys
    sys.path.append("../data/")  
 
    runBdGammaFitterOnData( options.debug,
                            options.wsname,
                            options.tvar,
                            options.terrvar,
                            options.idvar,
                            options.mvar,
                            options.pathName,
                            options.treeName,
                            options.configName,
                            options.configNameMD,
                            options.mode,
                            options.combo)

# -----------------------------------------------------------------------------
