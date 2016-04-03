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
#"
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
    
    hypo = ""
    if "Hypothesis" in myconfig.keys():
        hypo = " "+myconfig["Hypothesis"]+"Hypo"
    
    decay2 = TString(decay)
    if decay2.Contains("Ds"):
        dsmode = "KKPi"
    elif decay2.Contains("D"):
        dsmode = "KPiPi"

    year = myconfig["YearOfDataTaking"]
    magnet = ["MU","MD"]

    MCNames = []
    for y in year:
        for m in magnet:
            name = "#MC FileName "+dsmode+" "+m+" "+y+hypo
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
    if decay2.Contains("DsK"):
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

    hypo = ""
    if "Hypothesis" in myconfig.keys():
        hypo = " "+myconfig["Hypothesis"]+"Hypo"
    
    signalNames = []
    for y in year:
        for dmode in Dmodes:
            name = "#Signal "+decay+" "+dmode+" "+y+hypo
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


def getComboPIDNames(myconfig, DsModes):
    decay = myconfig["Decay"]

    decay2 = TString(decay)
    if decay2.Contains("K"):
        com = "CombK"
    elif decay2.Contains("Pi"):
        com = "CombPi"

    magnet = ["Up","Down"]
    if decay2.Contains("DsK"):
        part = ["Kaon","Pion","Proton"]
    else:
        part = ["Kaon","Pion"]
    year = myconfig["YearOfDataTaking"]
    
    if DsModes:
        Dmodes = myconfig["CharmModes"]
    else:
        Dmodes = [""] 
    comboNames = []
    
    for y in year:
        for p in part:
            for m in magnet:
                for d in Dmodes:
                    strip = "Str"+myconfig["Stripping"][y]
                    name = com + " " + p + " " + m + " " +y+" "+strip+ " " +d
                    comboNames.append(TString(name))
    
    return comboNames


def getCombPar(mode, o,  myconfig):
    if type(mode) == TString:
        mode = mode.Data()

    if myconfig["CreateCombinatorial"][o].has_key(mode):
        if myconfig["CreateCombinatorial"][o][mode].has_key("Cut"):
            cut = TString(myconfig["CreateCombinatorial"][o][mode]["Cut"])
        else:
            cut = TString("")
        if myconfig["CreateCombinatorial"][o][mode].has_key("Rho"):
            rho = myconfig["CreateCombinatorial"][o][mode]["Rho"]
        else:
            rho = -1.0
        if myconfig["CreateCombinatorial"][o][mode].has_key("Mirror"):
            mirror = TString(myconfig["CreateCombinatorial"][o][mode]["Mirror"])
        else:
            mirror = TString("None")
    else:
        cut = TString("")
        rho = -1.0
        mirror = TString("None")
    return cut, rho, mirror

def getCombProperties(rho, mirror, rhoD, mirrorD):
    print rho, rhoD, mirror, mirrorD
    if rhoD != -1.0:
        rhoF = rhoD
    elif rho != -1.0:
        rhoF = rho
    else:
        rhoF = 3.5

    if mirrorD != TString("None"):
        mirrorF = mirrorD
    elif mirror != TString("None"):
        mirrorF = mirror
    else:
        mirrorF = TString("Both")

    return rhoF, mirrorF

def matchMCName(MCNames,MCPIDUpName):

    MC = TString(MCPIDUpName)
    year = GeneralUtils.CheckDataYear(MC)
    pol = GeneralUtils.CheckPolarity(MC, False)

    for m in MCNames:
        mc = TString(m)
        y = GeneralUtils.CheckDataYear(mc)
        p = GeneralUtils.CheckPolarity(mc, False)

        if y == year and p == pol:
            MCName = m
            break;

    return MCName

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
    #exit(0) 

    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings",True)

    MDSettings = mdt.getConfig()
    MDSettings.Print("v")
    #exit(0)

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


 #   if DataBkgPID == True:
 #       DataBkg = True

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
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings,dataBkgPIDNames[i], workspace, plotSettings, debug)
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, dataBkgPIDNames[i], workspace, plotSettings, debug)
            
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()

#    if MCPID:
#        MC = True

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
                print MCNames[2*i]
                print MCNames[2*i+1]
                workspace = MassFitUtils.CreatePdfSpecBackground(dataTS, TString(MCNames[2*i]), 
                                                                 dataTS, TString(MCNames[2*i+1]),
                                                                 MDSettings, workspace, False, plotSettings, debug)
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()

    if MCPID:
        MCPIDUpNames, MCPIDDownNames = getMCPIDNames(myconfigfile)
        MCNames = getMCNames( myconfigfile )
        for i in range(0,MCPIDUpNames.__len__()):
            print MCPIDUpNames[i]
            MCName = matchMCName(MCNames,MCPIDUpNames[i])
            print MCName
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString(MCName),
                                                       MDSettings, MCPIDUpNames[i], workspace, plotSettings, debug)
        
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString(MCName),
                                                                     MDSettings, MCPIDUpNames[i], workspace, plotSettings, debug)
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)


        for i in range(0,MCPIDDownNames.__len__()):
            print MCPIDDownNames[i]
            MCName = matchMCName(MCNames,MCPIDDownNames[i])
            print MCName
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString(MCName),
                                                       MDSettings, MCPIDDownNames[i], workspace, plotSettings, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString(MCName),
                                                                     MDSettings, MCPIDDownNames[i], workspace, plotSettings, debug)
            
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        

#    if SignalPID:
#        Signal = True

    if Signal:
        signalNames = getSignalNames(myconfigfile)
        
        for i in range(0,signalNames.__len__()):
            print signalNames[i]
            year = GeneralUtils.CheckDataYear(signalNames[i])
            workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), signalNames[i],
                                                  MDSettings, decay, False, False, workspace, False,
                                                  1.0, 1.0, plotSettings, debug)

        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
           
                
    if SignalPID:
        signalPIDNames = getSignalPIDNames(myconfigfile)
        
        for i in range(0,signalPIDNames.__len__()):
            
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings, signalPIDNames[i], workspace, plotSettings, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(MDSettings, signalPIDNames[i], workspace, plotSettings, debug)
                        
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
            workspace.Print()

    if CombPID:
        if MDSettings.CheckPIDComboShapeForDsModes():
            check = myconfigfile.has_key("CreateCombinatorial")
            if check == False:
                print "[ERROR] You want to take PID Calib samples from recent workspace, please specify 'CreateRooKeysPdfForCombinatorial' in your config file"
            else:
                Comb = True 

    if Comb and myconfigfile.has_key("CreateCombinatorial"):
        comboNames = getComboNames(myconfigfile)

        mdt = Translator(myconfigfile,"MDSettingsComb",True)
        obs = myconfigfile["CreateCombinatorial"]
        for o in obs:
            MDSettingsComb = mdt.getConfig()
            cuts = myconfigfile["CreateCombinatorial"][o]

            cut, rho, mirror = getCombPar("All", o, myconfigfile)
            MDSettingsComb.SetDataCuts("All", cut);

            print cut, rho, mirror

            for i in range(0,comboNames.__len__()):
                dmode = GeneralUtils.CheckDMode(TString(comboNames[i]))
                if dmode == "kkpi" or dmode == "":
                    dmode = GeneralUtils.CheckKKPiMode(TString(comboNames[i]))
                Dmode = GeneralUtils.GetModeCapital(dmode)
                cutD, rhoD, mirrorD = getCombPar(Dmode, o, myconfigfile)
                MDSettingsComb.SetDataCuts(Dmode, cutD)
                print dmode, cutD, rhoD, mirrorD

                if decay.Contains("Pi"):
                    name = TString("CombPi_")+TString(o)
                else:
                    name = TString("CombK_")+TString(o)
                workspace = MassFitUtils.ObtainData(dataTS, comboNames[i],  MDSettingsComb, name, plotSettings, workspace, debug)
                if rookeypdf:
                    rhoF, mirrorF = getCombProperties(rho, mirror, rhoD, mirrorD)
                    MassFitUtils.CreatePdfSpecBackground(MDSettingsComb, dataTS, comboNames[i], o, name, rhoF, mirrorF, workspace, plotSettings, debug)


    if CombPID:
        combNames = getComboPIDNames(myconfigfile, MDSettings.CheckPIDComboShapeForDsModes())
        print combNames 
        for i in range(0,combNames.__len__()):
            workspace = WeightingUtils.ObtainHistRatioOneSample(MDSettings, combNames[i], workspace, plotSettings,  debug)
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

parser.add_option( '--noRooKeysPdf','--nRKP',
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


    config = options.configName
    last = config.rfind("/")
    directory = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]
    
    import sys
    sys.path.append(directory)
        
    prepareWorkspace(  options.debug, 
                       options.save,
                       configName,
                       options.Data,
                       options.DataBkg, options.DataBkgPID,
                       options.MC, options.MCPID,
                       options.Signal, options.SignalPID,
                       options.Comb, options.CombPID, options.rookeypdf,
                       options.initial, options.workName)
    
# -----------------------------------------------------------------------------
