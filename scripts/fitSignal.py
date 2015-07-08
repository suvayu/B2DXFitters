#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a mass fit on data for B -> DX                       #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runMDFitter.py --fileName work_bsdspi.root --merge -m both      #
#                            --configName Bs2DsPiConfigForNominalMassFitBDT   #
#                            --debug --year 2011 --dim 3 --mode all           #
#                            --save WS_Mass_DsPi.root                         #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   mail: agnieszka.dziurda@cern.ch                                           #
#   date: 28.06.2015                                                          # 
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
from B2DXFitters.WS import WS as WS
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

# MISCELLANEOUS
bName = 'Bs'
dName = 'Ds'
bdName = 'Bd'
#------------------------------------------------------------------------------
def getExpectedValue(var,par,year,dsmode,myconfigfile):
    print var, par, year, dsmode
    if year != "":
        return myconfigfile[var][par][year.Data()][dsmode.Data()]
    elif year == "run1":
        return myconfigfile[var][par]["2011"][dsmode.Data()]+myconfigfile[var][par]["2012"][dsmode.Data()]
    else:
        print "[ERROR] Wrong year: %s"%(year)
        exit(0)

#------------------------------------------------------------------------------                                                             
def getExpectedYield(mode,year,dsmode, myconfigfile):
    #print mode, year, dsmode
    if year != "":
        return myconfigfile["Yields"][mode][year.Data()][dsmode.Data()]
    elif year == "run1":
        return myconfigfile["Yields"][mode]["2011"][dsmode.Data()]+myconfigfile["Yields"][mode]["2012"][dsmode.Data()]
    else:
        print "[ERROR] Wrong year: %s"%(year)
        exit(0)

#------------------------------------------------------------------------------                                                                                                   
def setConstantIfSoConfigured(var, par, mode, dmode, myconfigfile):
    if type(myconfigfile[par][mode]["Fixed"]) == bool:
        if myconfigfile[par][mode]["Fixed"] == True :
            var.setConstant()
            print "[INFO] Parameter: %s set to be constant with value %lf"%(var.GetName(),var.getValV())
        else:
            print "[INFO] Parameter: %s floats in the fit"%(var.GetName())
    elif myconfigfile[par][mode]["Fixed"].has_key(dmode.Data()):
        if myconfigfile[par][mode]["Fixed"][dmode.Data()]:
            var.setConstant()
            print "[INFO] Parameter: %s set to be constant with value %lf"%(var.GetName(),var.getValV())
        else:
            print "[INFO] Parameter: %s floats in the fit"%(var.GetName())
    else:
        print "[INFO] Parameter: %s floats in the fit"%(var.GetName())

#------------------------------------------------------------------------------ 
#get set of observables for fitter
#------------------------------------------------------------------------------ 
def getObservables (MDSettings, workData, toys, debug):
    
    if (not toys ):
        observables = MDSettings.GetObsSet(False,True,True,True,True, True)
    else:
        observables = MDSettings.GetObsSet(False,True,True,True,False, False)
        
    if MDSettings.CheckTagVar() == True:
        tagDecCombName = TString("tagDecComb")
        tagDecComb = GeneralUtils.GetCategory(workData, tagDecCombName, debug)
        tagOmegaCombName= TString("tagOmegaComb")
        tagOmegaComb = GeneralUtils.GetObservable(workData, tagOmegaCombName, debug)
        
        observables.add(tagDecComb)
        observables.add(tagOmegaComb)

    if debug:
        observables.Print("v") 

    return observables 

#------------------------------------------------------------------------------                                                                                                    
#get signal PDF                                                                                                                                                 
#------------------------------------------------------------------------------  

def readVariables(myconfigfile,label, prefix, workInt, sm, bound, debug):

    t = TString("_")
    variables = []

    names = []

    for i in range(0,bound):
        s = GeneralUtils.CheckPolarity(sm[i],debug)
        mm = GeneralUtils.GetModeCapital(sm[i],debug)
        m = GeneralUtils.CheckDMode(sm[i],debug)
        if m == "":
            m = GeneralUtils.CheckKKPiMode(sm[i],debug)

        yr = GeneralUtils.CheckDataYear(sm[i])
        y = yr
        if ( y != ""):
            y = t+y

        name = m+y
        if name in names:
            continue
        else:
            names.append(name)
        print label 
        if myconfigfile.has_key(label):
            if myconfigfile[label]["type"] != "RooKeysPdf":
                var = myconfigfile[label]
                for v in var:
                    if label == "PIDKCombinatorialShape":
                        if v == "fracPIDK":
                            if myconfigfile[label][v].has_key(yr.Data()):
                                frac = myconfigfile[label][v][yr.Data()]
                                for f in frac:
                                    if f in names:
                                        continue
                                    else:
                                        names.append(f)
                                    nameComb = TString(prefix)+t+f
                                    expectedValue = getExpectedValue(label,v,yr,TString(f),myconfigfile)
                                    variables.append(WS(workInt,RooRealVar(nameComb.Data() , nameComb.Data(), expectedValue, 0.0, 1.0)))
                                    setConstantIfSoConfigured(variables[variables.__len__()-1], label, v, mm, myconfigfile)
                        else:
                            print "[ERROR] Year not specified."

                    else:    
                        if v != "type" and v != "scaleSigma":
                            lTS = TString(label)
                            if lTS.Contains("Signal"):
                                nameVar = TString(prefix) + TString("_")+v+t+s+t+name
                            else:
                                nameVar = TString(prefix) + TString("_")+v+t+name
                            if myconfigfile[label][v].has_key("All") == False:
                                expectedValue = getExpectedValue(label,v,yr,mm,myconfigfile)
                                vTS = TString(v)
                                if vTS.Contains("frac"):
                                    boundDown = 0.0
                                    boundUp = 1.0
                                else:
                                    if expectedValue < 0.0:
                                        boundUp = 0.0
                                        boundDown = expectedValue*2.0
                                    else:
                                        boundDown = 0.0
                                        boundUp =expectedValue*2.0

                                if myconfigfile[label].has_key("scaleSigma") and ( v == "sigma1" or v == "sigma2"):
                                    f1 =  myconfigfile[label]["scaleSigma"][yr.Data()]["frac1"]
                                    f2 =  myconfigfile[label]["scaleSigma"][yr.Data()]["frac2"]

                                    if v == "sigma1": 
                                        expectedValue2 = getExpectedValue(label,"sigma2",yr,mm,myconfigfile)
                                    elif v == "sigma2": 
                                        expectedValue2 = getExpectedValue(label,"sigma1",yr,mm,myconfigfile)
                                    
                                    oldvalue = expectedValue
                                    if expectedValue>expectedValue2:
                                        f = f1
                                    else:
                                        f = f2 
                                    expectedValue = expectedValue*f
                                    print "[INFO] Change value %s to %s = %s * %s"%(str(oldvalue), str(expectedValue), str(oldvalue), str(f))

                                        
                                variables.append(WS(workInt, RooRealVar(nameVar.Data() , nameVar.Data(), expectedValue,  boundDown, boundUp)))
                                setConstantIfSoConfigured(variables[variables.__len__()-1], label, v, mm, myconfigfile)
        else:
            print "[ERROR] Cannot find the label: %s. Please specify in config file"%(label)
            exit(0)

    return workInt

def getSignalPDF(myconfigfile,work,workInt, sm, bound,dim,beautyMass,charmMass,var,decay,debug):
   
    t = TString("_") 

    if dim  ==  0:
            name = TString(var.GetName()) 
            meanName = TString("Signal_")+name + TString("_mean"); 
            mn = WS(workInt, RooRealVar( meanName.Data(), meanName.Data(), myconfigfile["BsSignalShape"]["mean"]["All"],
                                         myconfigfile["BsSignalShape"]["mean"]["All"]-50,    myconfigfile["BsSignalShape"]["mean"]["All"] +50, "MeV/c^{2}"))
    if dim > 1:
            mnDs = WS(workInt, RooRealVar( "Signal_CharmMass__mean", "Signal_CharmMass_mean", myconfigfile["DsSignalShape"]["mean"]["All"],
                                           myconfigfile["DsSignalShape"]["mean"]["All"]-50,  myconfigfile["DsSignalShape"]["mean"]["All"]+50, "MeV/c^{2}"))
    else:
            mnDs = NULL
    
    if dim == 0: 
        meanName = TString("Signal_")+TString(var.GetName())
        workInt = readVariables(myconfigfile,"SignalShape", meanName.Data(), workInt, sm, bound, debug)
    if dim > 0:
        workInt = readVariables(myconfigfile,"BsSignalShape", "Signal_BeautyMass", workInt, sm, bound, debug)
    if dim > 1:
        workInt = readVariables(myconfigfile,"DsSignalShape", "Signal_CharmMass", workInt, sm, bound, debug)


    if dim > 0: 
        if myconfigfile["BsSignalShape"].has_key("type"):
            typeBs = TString(myconfigfile["BsSignalShape"]["type"])
        else:
            typeBs = TString("None")
                    
        if myconfigfile["DsSignalShape"].has_key("type"):
            typeDs = TString(myconfigfile["DsSignalShape"]["type"])
        else:
            typeDs = TString("None")
                    
        typePIDK = TString("None")
        types = GeneralUtils.GetList(typeBs, typeDs, typePIDK)    
    else:
        if myconfigfile["SignalShape"].has_key("type"):
            types = TString(myconfigfile["SignalShape"]["type"])
                    
            

    sigEPDF = []
    nSigEvts = []
    nSig = [] 
    workInt.Print("v")
    for i in range(0,bound):
        s = GeneralUtils.CheckPolarity(sm[i],debug)
        mm = GeneralUtils.GetModeCapital(sm[i],debug)
        m = GeneralUtils.CheckDMode(sm[i],debug)
        if m == "":
            m = GeneralUtils.CheckKKPiMode(sm[i],debug)

        yr = GeneralUtils.CheckDataYear(sm[i])

        nSigEvts.append(myconfigfile["Yields"]["Signal"][yr.Data()][mm.Data()])
        name = TString("nSig")+t+sm[i]+t+TString("Evts")
        print nSigEvts[i]
        nSig.append(WS(workInt, RooRealVar( name.Data(), name.Data(), nSigEvts[i], 0.0, nSigEvts[i]+nSigEvts[i]*0.5  )))
        if dim > 0:
            sigEPDF.append( WS ( workInt, Bs2Dsh2011TDAnaModels.build_Signal_MDFitter(beautyMass,charmMass, work, workInt,
                                                                                      sm[i], decay, types, dim, debug)))
        else:
            sigEPDF.append( WS ( workInt, Bs2Dsh2011TDAnaModels.ObtainSignalMassShape(var, work, workInt,
                                                                                      sm[i], types, True, debug)))
    return sigEPDF, workInt

#------------------------------------------------------------------------------
def getSignalNames(myconfig, mode, yr):
    decay = myconfig["Decay"]
    if mode == "all":
        Dmodes = myconfig["CharmModes"]
    else:
        mode = GeneralUtils.GetModeCapital(TString(mode))
        Dmodes = [mode]
    if yr == "":
        year = myconfig["YearOfDataTaking"]
    else:
        year = [yr] 

    signalNames = []
    for y in year:
        for dmode in Dmodes:
            name = TString("#Signal ")+decay+TString(" ")+dmode+TString(" ")+y
            signalNames.append(TString(name))

    return signalNames    


#------------------------------------------------------------------------------
def runMDFitter( debug, sample, mode, decay, 
                 fileNameAll, workName,
                 configName, merge, dim, fileDataName, year, varName) :

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
                                                                    
    plotSettings = PlotSettings("plotSettings","plotSettings", "Plot", "pdf", 100, True, False, True)
    plotSettings.Print("v")


    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    config = TString("../data/")+TString(configName)+TString(".py")
    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings")

    MDSettings = mdt.getConfig()
    MDSettings.Print("v")

    mode = TString(mode) 
    decay = TString(decay) 
    workNameTS = TString(workName)
    workspace = []
    if fileDataName != "":
        workData = workspace[0]
    else:
        workData = RooWorkspace("workspace","workspace")
        signalNames = getSignalNames(myconfigfile, mode, year)
        for i in range(0,signalNames.__len__()):
            year = GeneralUtils.CheckDataYear(signalNames[i])
            workData = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), signalNames[i],
                                                 MDSettings, decay, False, False, workData, False,
                                                 MDSettings.GetLum(year,"Down"), MDSettings.GetLum(year,"Up"), plotSettings, debug)

            
    configNameTS = TString(configName)

    obs = RooArgSet()
    print dim 
    dim = int(dim)
    varName = TString(varName)
    if dim  == 0 :
        var = GeneralUtils.GetObservable(workData, varName, debug)
        obs.add(var) 
        beautyMass = NULL
        charmMass = NULL 
    if dim > 0 :     
        beautyMass = MDSettings.GetObs(MDSettings.GetMassBVarOutName(), False, False) 
        obs.add(beautyMass) 
    if dim > 1 :
        charmMass =  MDSettings.GetObs(MDSettings.GetMassDVarOutName(), False, False) 
        obs.add(charmMass)
    if dim>2:
        pidk = MDSettings.GetObs(MDSettings.GetPIDKVarOutName(), False, False) 
        obs.add(pidk) 

 ###------------------------------------------------------------------------------------------------------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------###
 ###------------------------------------------------------------------------------------------------------------------------------------###   

    t = TString('_')

    modeTS = TString(mode) 
    sampleTS = TString(sample)
    yearTS = TString(year)
    datasetTS = TString("dataSetMC_")+decay+t 
    if merge:
        sampleTS = TString("both") 
    
    sam = RooCategory("sample","sample")

    sm = []
    data = []
    nEntries = []

    workData.Print("v") 
    combData =  GeneralUtils.GetDataSet(workData, obs, sam, datasetTS, sampleTS, modeTS, yearTS, merge, debug )
    combData.Print("v")

    sm = GeneralUtils.GetSampleModeYear(sampleTS, modeTS, yearTS, merge, debug )
    s = GeneralUtils.GetSample(sampleTS, debug)
    m = GeneralUtils.GetMode(modeTS,debug)
    y = GeneralUtils.GetYear(yearTS,debug)
    nEntries = combData.numEntries()

    ran = sm.__len__()
    ranmode = m.__len__()*y.__len__()
    ransample = s.__len__()

    if merge:
        bound = ranmode
    else:
        bound = ran

    ###------------------------------------------------------------------------------------------------------------------------------------###    
          ###-------------------------   Create the signal PDF in Bs mass, Ds mass, PIDK   ------------------------------------------###          
    ###------------------------------------------------------------------------------------------------------------------------------------###        
    
    from B2DXFitters.WS import WS as WS
    workInt = RooWorkspace("workInt","workInt")    

    if dim > 0 :
        lumRatio = []
        if year == "run1": 
            yy = ["2011","2012"]
        else:
            yy = [year]
        for y in yy:
            lum = MDSettings.GetLumRatio(y)
            name = "lumRatio_"+y
            lumRatio.append(WS(workInt,RooRealVar(name,name, lum[1])))
    
    sigEPDF, workInt = getSignalPDF(myconfigfile,workData,workInt,sm,bound,dim,beautyMass,charmMass,var,decay,debug)
        
    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    for i in range(0,bound):
        print sigEPDF[i].GetName()
        print sm[i].Data()
        totPDF.addPdf(sigEPDF[i], sm[i].Data())
    totPDF.Print("v")
    
    ###------------------------------------------------------------------------------------------------------------------------------------###    
          ###--------------------------------------------  Instantiate and run the fitter  -------------------------------------------###  
    ###------------------------------------------------------------------------------------------------------------------------------------###

    fitter = FitMeTool( debug )
      
    fitter.setObservables( obs )

    fitter.setModelPDF( totPDF )
    fitter.setData(combData) 
   
    import sys
    import random
    
    fitter.fit(True, RooFit.Extended()) #,  RooFit.Verbose(False),  RooFit.ExternalConstraints(constList)) #, RooFit.InitialHesse(True))
    result = fitter.getFitResult()
    result.Print("v")
    floatpar = result.floatParsFinal()
        
    if dim == 1:
        fitter.printYieldsInRange( '*Evts', MDSettings.GetMassBVarOutName().Data() , 5320, 5420 )
    elif dim == 2:
        fitter.printYieldsInRange( '*Evts', MDSettings.GetMassBVarOutName().Data() , 5320, 5420, "SignalRegion",
                                   charmMass.GetName(), charmMass.getMin(),  charmMass.getMax() )
    elif dim == 3:
        fitter.printYieldsInRange( '*Evts', MDSettings.GetMassBVarOutName().Data() , 5320, 5420, "SignalRegion",
                                   charmMass.GetName(), charmMass.getMin(), charmMass.getMax(),
                                   bacPIDK.GetName(), bacPIDK.getMin(), bacPIDK.getMax())
    
    fitter.saveModelPDF( options.wsname )
    fitter.saveData ( options.wsname )

    del fitter

    
    
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
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   default = 'WS_MassFit_Result.root', 
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )
parser.add_option( '-m', '--sample',
                   dest = 'sample',
                   metavar = 'SAMPLE',
                   default = 'down',
                   help = 'Sample: choose up or down '
                   )
parser.add_option( '--mode','-o',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'kkpi',
                   help = 'Mode: choose all, kkpi, kpipi or pipipi'
                   )
parser.add_option( '--decay',
                   dest = 'decay',
                   metavar = 'MODE',
                   default = 'Bs2DsK',
                   help = 'decay'
                   )

parser.add_option( '--fileName',
                   dest = 'fileNameAll',
                   default = 'work_dsstk.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--variable','--var','--varName','-v',
                   dest = 'varName',
                   default = 'BeautyMass',
                   help = 'name of the inputfile'
                   )
parser.add_option( '--workName',
                   dest = 'workName',
                   default = 'workspace',
                   help = 'name of the workspace'
                   )   
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsstKConfigForNominalMassFit')
parser.add_option( '--merge',
                   dest = 'merge',
                   action = 'store_true',
                   default = False,
                   help = 'merge magnet polarity'
                   )
parser.add_option( '--dim',
                   dest = 'dim',
                   default = 0)

parser.add_option( '--fileData',
                   dest = 'fileData',
                   default = '',
                   help = 'you can use it if you have separate files with templates and data'
                   )
parser.add_option( '--year',
                   dest = 'year',
                   default = "")

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    import sys
    sys.path.append("../data/")
        
    runMDFitter( options.debug,  options.sample, options.mode, options.decay,
                 options.fileNameAll, options.workName,
                 options.configName,  
                 options.merge, options.dim, options.fileData, options.year, options.varName)

# -----------------------------------------------------------------------------
