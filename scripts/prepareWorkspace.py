#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to prepare workspace for B2DXFitter package                 #
#                                                                             #
#   Example usage:                                                            #
#      python prepareWorkspace.py [-d | --debug]                              #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 06 / 2015                                                    #
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

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc

gROOT.SetBatch()

# -----------------------------------------------------------------------------                                                                                                         
# Get signature of signal                                                                                                                                                             
# -----------------------------------------------------------------------------
def getDataNames ( myconfig ):

    decay = myconfig["Decay"]
    Dmodes = myconfig["CharmModes"]
    year = myconfig["YearOfDataTaking"]

    dataNames = []
    for y in year:
        for dmode in Dmodes:
            dataName = "#"+decay+" "+dmode+" "+y
            dataNames.append(TString(dataName))

    return dataNames

# -----------------------------------------------------------------------------                                                                                                         
# Get signature of background obtained from data                                                                                                                                
# -----------------------------------------------------------------------------
def getDataBkgNames( myconfig ):
    decay = myconfig["Decay"]
    Dmodes = myconfig["CharmModes"]

    if decay == "Bs2DsK":
        decayBkg = "Bs2DsPi"
    elif decay == "Bs2DsPi":
        decayBkg = "B2DPi"
        Dmodes = ["KPiPi"] 
    else:
        print "[ERROR] It is not possible to obtain background from data using your signal mode %s"%(decay)
        exit(0)

    dataNames = []
    year = myconfig["YearOfDataTaking"]
    for dmode in Dmodes:
        for y in year: 
            dataName = "#"+decayBkg+" "+dmode+" "+y
            dataNames.append(TString(dataName))

    decayBkg = TString(decayBkg)

    return dataNames, decayBkg

# -----------------------------------------------------------------------------                                                                                                         
# Get signature of background obtained from MC                                                                                                                                        
# -----------------------------------------------------------------------------
def getMCNames(myconfig):
    decay = myconfig["Decay"]
    
    decay2 = TString(decay)
    if decay2.Contains("Ds"):
        dsmode = "KKPi"
    elif decay2.Contains("D"):
        dsmode = "KiPiPi"

    year = myconfig["YearOfDataTaking"]
    magnet = ["MU","MD"]

    MCNames = []
    for y in year:
        for m in magnet:
            name = "#MC FileName "+dsmode+" "+m+" "+y
            #name = "#MC FileName DsPi "+m+" "+y
            MCNames.append(TString(name))

    return MCNames
            

# -----------------------------------------------------------------------------                                                                                                         
# Get signature of background obtained from data for PIDK variable                                                                                                                     
# -----------------------------------------------------------------------------
def getDataBkgPIDNames( myconfig ):
    decay = myconfig["Decay"]
    Dmodes = myconfig["CharmModes"]

    if decay == "Bs2DsK":
        decayBkg = "Bs2DsPi"
    elif decay == "Bs2DsPi":
        decayBkg = "Bd2DPi"
        Dmodes = ["KPiPi"] 
    else:
        print "[ERROR] It is not possible to obtain background from data using your signal mode %s"%(decay)
        exit(0)

    dataNames = []
    magnet = ["Up","Down"]
    year = myconfig["YearOfDataTaking"]
    for y in year:
        for mag in magnet:
            for dmode in Dmodes:
                strip = "Str"+myconfig["Stripping"][y]
                dmode2 = GeneralUtils.CheckKKPiMode(TString(dmode))
                if dmode2 == "nonres" or dmode2 == "kstk" or dmode2 == "phipi":
                    dmode2 = "KKPi"
                else:
                    dmode2 = "" 
                dataName = TString(decayBkg+" "+dmode2+" "+dmode+" Pion "+mag+" "+y+" "+strip)
                dataNames.append(TString(dataName))

    decayBkg = TString(decayBkg)
    print dataNames
    return dataNames

# -----------------------------------------------------------------------------                                                                                                         
# Get signature of background obtained from MC for PIDK variable                                                                                                                      
# ----------------------------------------------------------------------------- 
def getMCPIDNames(myconfig):
    decay = myconfig["Decay"]

    decay2 = TString(decay) 
    if decay2.Contains("K"):
        part = ["Kaon","Pion","Proton"]
    else:
        part = ["Kaon","Pion"]

    magnet = ["Up","Down"]
    year = myconfig["YearOfDataTaking"]

    dataUpNames = []
    for y in year: 
        for p in part:
            strip = "Str"+myconfig["Stripping"][y]
            name = "MC "+decay+" "+p+" Up "+y+ " "+strip
            dataUpNames.append(TString(name))
        
    dataDwNames = []
    for y in year:
        for p in part:
            strip = "Str"+myconfig["Stripping"][y]
            name = "MC "+decay+" "+p+ " Down "+y+" "+strip
            dataDwNames.append(TString(name))
        
    return dataUpNames, dataDwNames

# -----------------------------------------------------------------------------                                                                                                         
# Get signature of signal obtained from MC for PIDK variable                                                                                                                        
# -----------------------------------------------------------------------------  
def getSignalNames(myconfig):
    decay = myconfig["Decay"]
    Dmodes = myconfig["CharmModes"]
    year = myconfig["YearOfDataTaking"]

    signalNames = []
    for y in year:
        for dmode in Dmodes:
            name = "#Signal "+decay+" "+dmode+" "+y
            signalNames.append(TString(name))
        
    return signalNames


# -----------------------------------------------------------------------------                                                                                                         
# Get signature of signal obtained from MC for PIDK variable                                                                                                                         
# -----------------------------------------------------------------------------                                                                                                         
def getSignalPIDNames(myconfig):
    decay = myconfig["Decay"]
    Dmodes = myconfig["CharmModes"]

    decay2 = TString(decay)
    if decay2.Contains("K"):
        bach = "Kaon"
    elif decay2.Contains("Pi"):
        bach = "Pion"
    magnet = ["Up","Down"]
    year = myconfig["YearOfDataTaking"]

    dataNames = []
    for y in year: 
        for m in magnet:
            for dmode in Dmodes:
                strip = "Str"+myconfig["Stripping"][y]
                dmode2 = GeneralUtils.CheckKKPiMode(TString(dmode))
                if dmode2 == "nonres" or dmode2 == "kstk" or dmode2 == "phipi":
                    dmode2 = "KKPi"
                else:
                    dmode2 = ""
                name = "MC "+decay+" "+dmode2+" "+dmode+" "+bach+" "+m+" "+y+" "+strip
                dataNames.append(TString(name))

    return dataNames

def getComboNames(myconfig):
    decay = myconfig["Decay"]
    Dmodes = myconfig["CharmModes"]
    year = myconfig["YearOfDataTaking"]

    dataNames = []
    for y in year:
        for dmode in Dmodes:
            dataName = "#"+decay+" Combinatorial "+dmode+" "+y
            dataNames.append(TString(dataName))

    return dataNames


def getComboPIDNames(myconfig):
    decay = myconfig["Decay"]

    decay2 = TString(decay)
    if decay2.Contains("K"):
        com = "CombK"
    elif decay2.Contains("Pi"):
        com = "CombPi"

    magnet = ["Up","Down"]
    if decay2.Contains("K"):
        part = ["Kaon","Pion","Proton"]
    else:
        part = ["Kaon","Pion"]

    year = myconfig["YearOfDataTaking"]
    
    comboNames = []
    
    for y in year:
        for p in part:
            for m in magnet:
                strip = "Str"+myconfig["Stripping"][y]
                name = com + " " + p + " " + m + " " +y+" "+strip
                comboNames.append(TString(name))
    
    return comboNames


# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------
#------------------------------------------------------------------------------
def prepareWorkspace( debug,
                      save, configName,
                      Data, DataBkg, DataBkgPID, MC, MCPID, Signal, SignalPID, Comb, CombPID, rookeypdf, initial, workName ) : 
    
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
    saveNameTS = TString(save)

    #plot settings:
    plotSettings = PlotSettings("plotSettings","plotSettings", "Plot", "pdf", 100, True, False, True)
    plotSettings.Print("v")


    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings")

    MDSettings = mdt.getConfig()
    MDSettings.Print("v")
    

    if initial != "":
        workspace = GeneralUtils.LoadWorkspace(TString(initial),TString(workName),debug)
    else:
        workspace = RooWorkspace("workspace","workspace")

    dataTS  = TString(myconfigfile["dataName"])
    decay = TString(myconfigfile["Decay"])

    if Data:     
        dataNames = getDataNames ( myconfigfile ) 
        for i in range(0,dataNames.__len__()):
            print dataNames[i]
            workspace = MassFitUtils.ObtainData(dataTS, dataNames[i],  MDSettings, decay, plotSettings, workspace, debug)
        
        
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()


    if DataBkgPID == True:
        DataBkg = True

    if DataBkg:
        dataBkgNames, decayBkg = getDataBkgNames( myconfigfile )
        if myconfigfile["Decay"] == "Bs2DsK":
            for i in range(0,dataBkgNames.__len__()):
                workspace = MassFitUtils.ObtainMissForBsDsK(TString(myconfigfile["dataName"]), dataBkgNames[i], MDSettings, 
                                                            decayBkg, workspace, plotSettings, rookeypdf, debug)
        elif myconfigfile["Decay"] == "Bs2DsPi":
            for i in range(0,dataBkgNames.__len__()):
                workspace = MassFitUtils.ObtainMissForBsDsPi(dataTS, dataBkgNames[i], TString("nonres"),
                                                             MDSettings, decayBkg, workspace, plotSettings, rookeypdf, debug)
                
                
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()
    
    if DataBkgPID:

        dataBkgPIDNames = getDataBkgPIDNames( myconfigfile )
        for i in range(0,dataBkgPIDNames.__len__()):
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings,dataBkgPIDNames[i], workspace, workspace, plotSettings, debug)
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, dataBkgPIDNames[i], workspace, plotSettings, debug)
            
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()

    if MCPID:
        MC = True

    if MC:
        MCNames = getMCNames( myconfigfile )
        
        for i in range(0,MCNames.__len__()):
            print MCNames[i]
            year = GeneralUtils.CheckDataYear(MCNames[i],debug)
            pol = GeneralUtils.CheckPolarity(MCNames[i],debug)
            workspace = MassFitUtils.ObtainSpecBack(TString(myconfigfile["dataName"]), TString(MCNames[i]),
                                                    MDSettings, decay, workspace, True, MDSettings.GetLum(year,pol), plotSettings, debug)

        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()

        if rookeypdf:
            year = myconfigfile["YearOfDataTaking"]
            sy = year.__len__()
            for i in range(0,sy):
                workspace = MassFitUtils.CreatePdfSpecBackground(dataTS, TString(MCNames[2*i]), 
                                                                 dataTS, TString(MCNames[2*i+1]),
                                                                 MDSettings, workspace, True, plotSettings, debug)
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()

    if MCPID:
        MCPIDUpNames, MCPIDDownNames = getMCPIDNames(myconfigfile)
        for i in range(0,MCPIDUpNames.__len__()):
            print MCPIDUpNames[i]
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString(MCNames[1]),
                                                       MDSettings, MCPIDUpNames[i], workspace, plotSettings, debug)
        
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString(MCNames[1]),
                                                                     MDSettings, MCPIDUpNames[i], workspace, plotSettings, debug)
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)


        for i in range(0,MCPIDDownNames.__len__()):
            print MCPIDDownNames[i]
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString(MCNames[0]),
                                                       MDSettings, MCPIDDownNames[i], workspace, plotSettings, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString(MCNames[0]),
                                                                     MDSettings, MCPIDDownNames[i], workspace, plotSettings, debug)
            
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        

    if SignalPID:
        Signal = True

    if Signal:
        signalNames = getSignalNames(myconfigfile)
        
        for i in range(0,signalNames.__len__()):
            print signalNames[i]
            year = GeneralUtils.CheckDataYear(signalNames[i])
            workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), signalNames[i],
                                                  MDSettings, decay, False, False, workspace, False,
                                                  MDSettings.GetLum(year,"Down"), MDSettings.GetLum(year,"Up"), plotSettings, debug)

        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
           
                
    if SignalPID:
        signalPIDNames = getSignalPIDNames(myconfigfile)
        
        for i in range(0,signalPIDNames.__len__()):
            
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings, signalPIDNames[i], workspace, workspace, plotSettings, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, signalPIDNames[i], workspace, plotSettings, debug)
                        
            
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()

    if Comb and myconfigfile.has_key("CreateRooKeysPdfForCombinatorial"):
        comboNames = getComboNames(myconfigfile)
        
        mdt = Translator(myconfigfile,"MDSettingsComb")
        obs = myconfigfile["CreateRooKeysPdfForCombinatorial"]
        for o in obs:
            MDSettingsComb = mdt.getConfig()
            cut = TString(myconfigfile["CreateRooKeysPdfForCombinatorial"][o]["Cut"])
            MDSettingsComb.SetDataCuts("All", cut);
            for i in range(0,comboNames.__len__()):
                if comboNames[i].Contains("Pi"): 
                    name = TString("CombPi_")+TString(o)
                else:
                    name = TString("CombK_")+TString(o)  
                workspace = MassFitUtils.ObtainData(dataTS, comboNames[i],  MDSettingsComb, name, plotSettings, workspace, debug)
                if rookeypdf:
                    MassFitUtils.CreatePdfSpecBackground(MDSettingsComb, dataTS, comboNames[i], o, name,
                                                         myconfigfile["CreateRooKeysPdfForCombinatorial"][o]["Rho"],
                                                         myconfigfile["CreateRooKeysPdfForCombinatorial"][o]["Mirror"],
                                                         workspace, plotSettings, debug)

    if CombPID:
        if myconfigfile["Calibrations"].has_key("Combinatorial"):
            workspaceL = [GeneralUtils.LoadWorkspace(TString(myconfigfile["Calibrations"]["Combinatorial"]["FileNameUp"]),
                                                     TString(myconfigfile["Calibrations"]["Combinatorial"]["WorkName"]),debug),
                          GeneralUtils.LoadWorkspace(TString(myconfigfile["Calibrations"]["Combinatorial"]["FileNameDown"]),
                                                     TString(myconfigfile["Calibrations"]["Combinatorial"]["WorkName"]),debug)]
        combNames = getComboPIDNames(myconfigfile)

        for i in range(0,combNames.__len__()):
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings, combNames[i], workspace, workspaceL[i%2], plotSettings,  debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, combNames[i], workspace, plotSettings, debug)
            
            workspace.Print()
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)

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
                   default = 'work_dsk.root',
                   help = 'save the model PDF and generated dataset to file work_dsk.root'
                   )
parser.add_option( '-i', '--initial',
                   dest = 'initial',
                   default = '',
                   help = 'load the model PDF and generated dataset and continue obtaining shapes'
                   )
parser.add_option( '-w', '--workName',
                   dest = 'workName',
                   default = 'workspace',
                   help = 'name of initial workspace'
                   )
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsKConfigForNominalMassFitBDTGA'
                   )

parser.add_option( '--Data',
                   dest = 'Data',
                   action = 'store_true',
                   default = False,
                   help = 'create data'
                   )

parser.add_option( '--DataBkg',
                   dest = 'DataBkg',
                   action = 'store_true',
                   default = False,
                   help= 'obtain background from data'
                   )

parser.add_option( '--DataBkgPID',
                   dest = 'DataBkgPID',
                   action = 'store_true',
                   default = False,
                   help= 'obtain background from data'
                   )

parser.add_option( '--MC',
                   dest = 'MC',
                   action = 'store_true',
                   default = False,
                   help= 'obtain MC samples and PDFs'
                   )

parser.add_option( '--MCPID',
                   dest = 'MCPID',
                   action = 'store_true',
                   default = False,
                   help= 'obtain PIDK shape for MC samples'
                   )

parser.add_option( '--Signal',
                   dest = 'Signal',
                   action = 'store_true',
                   default = False,
                   help= 'obtain Signal samples'
                   )

parser.add_option( '--SignalPID',
                   dest = 'SignalPID',
                   action = 'store_true',
                   default = False,
                   help= 'obtain PIDK shape for signal'
                   )
parser.add_option( '--Comb',
                   dest = 'Comb',
                   action = 'store_true',
                   default = False,
                   help= 'obtain combinatorial background'
                   )
parser.add_option( '--CombPID',
                   dest = 'CombPID',
                   action = 'store_true',
                   default = False,
                   help= 'obtain PIDK shape for combinatorial background'
                   )

parser.add_option( '--noRooKeysPdf',
                   dest = 'rookeypdf',
                   action = 'store_false',
                   default = True,
                   help= 'don not obtain RooKeysPdf for samples'
                   )


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    import sys
    sys.path.append("../data/")
        
    prepareWorkspace(  options.debug, 
                       options.save,
                       options.configName,
                       options.Data,
                       options.DataBkg, options.DataBkgPID,
                       options.MC, options.MCPID,
                       options.Signal, options.SignalPID,
                       options.Comb, options.CombPID, options.rookeypdf,
                       options.initial, options.workName)
    
# -----------------------------------------------------------------------------
