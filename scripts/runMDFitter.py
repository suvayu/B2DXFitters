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

def getSignalPDF(myconfigfile,work,workInt, sm,merge,bound,dim,beautyMass,charmMass,debug):
   
    t = TString("_") 

    mn = WS(workInt, RooRealVar( "Signal_BeautyMass_mean", "Signal_BeautyMass_mean", myconfigfile["BsSignalShape"]["mean"]["All"],
                     myconfigfile["BsSignalShape"]["mean"]["All"]-50,    myconfigfile["BsSignalShape"]["mean"]["All"] +50, "MeV/c^{2}"))
    if dim > 1:
        mnDs = WS(workInt, RooRealVar( "Signal_CharmMass_mean", "Signal_CharmMass_mean", myconfigfile["DsSignalShape"]["mean"]["All"],
                           myconfigfile["DsSignalShape"]["mean"]["All"]-50,  myconfigfile["DsSignalShape"]["mean"]["All"]+50, "MeV/c^{2}"))
    else:
        mnDs = NULL
        
    workInt = readVariables(myconfigfile,"BsSignalShape", "Signal_BeautyMass", workInt, sm, bound, debug)
    if dim > 1:
        workInt = readVariables(myconfigfile,"DsSignalShape", "Signal_CharmMass", workInt, sm, bound, debug)


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
    
    decay =  TString(myconfigfile["Decay"])

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

        sigEPDF.append( WS ( workInt, Bs2Dsh2011TDAnaModels.build_Signal_MDFitter(beautyMass,charmMass, work, workInt,
                                                                                  sm[i], decay, types, dim, debug)))
    
    return sigEPDF, mn, workInt
#------------------------------------------------------------------------------
def getCombinatorialPDF(myconfigfile,work, workInt,sm,bound,dim,beautyMass,charmMass,debug):

    workInt = readVariables(myconfigfile,"BsCombinatorialShape", "CombBkg", workInt, sm, bound, debug)
    if dim > 1:
        workInt = readVariables(myconfigfile,"DsCombinatorialShape", "CombBkg", workInt, sm, bound, debug)
    if dim > 2:
        workInt = readVariables(myconfigfile,"PIDKCombinatorialShape", "CombBkg", workInt, sm, bound, debug)

    
    if myconfigfile["BsCombinatorialShape"].has_key("type"):
        typeBs = TString(myconfigfile["BsCombinatorialShape"]["type"])
    else:
        typeBs = TString("None")

    if myconfigfile["DsCombinatorialShape"].has_key("type"):
        typeDs = TString(myconfigfile["DsCombinatorialShape"]["type"])
    else:
        typeDs = TString("None") 

    if myconfigfile["PIDKCombinatorialShape"].has_key("type"):
        typePIDK = TString(myconfigfile["PIDKCombinatorialShape"]["type"])
    else:
        typePIDK = TString("None")
    
    types = GeneralUtils.GetList(typeBs, typeDs, typePIDK)

    if myconfigfile["PIDKCombinatorialShape"].has_key("components"):
        if myconfigfile["PIDKCombinatorialShape"]["components"]["Kaon"] == True:
            nameKaon = "true"
        else:
            nameKaon = "false"
        if myconfigfile["PIDKCombinatorialShape"]["components"]["Pion"] == True:
            namePion = "true"
        else:
            namePion = "false"
        if myconfigfile["PIDKCombinatorialShape"]["components"]["Proton"] == True:
            nameProton = "true"
        else:
            nameProton = "false"
    
    pidkNames = GeneralUtils.GetList(nameKaon, namePion, nameProton)

    combEPDF = []
    for i in range(0,bound):
        s = GeneralUtils.CheckPolarity(sm[i],debug)
        mm = GeneralUtils.GetModeCapital(sm[i],debug)
        m = GeneralUtils.CheckDMode(sm[i],debug)
        if m == "":
            m = GeneralUtils.CheckKKPiMode(sm[i],debug)

        yr = GeneralUtils.CheckDataYear(sm[i])


        if myconfigfile["BsCombinatorialShape"].has_key("name"):
            nameBs = TString(myconfigfile["BsCombinatorialShape"]["name"][yr.Data()][mm.Data()])
        else:
            nameBs = TString("None")
            
        if myconfigfile["DsCombinatorialShape"].has_key("name"):
            nameDs = TString(myconfigfile["DsCombinatorialShape"]["name"][yr.Data()][mm.Data()])
        else:
            nameDs = TString("None")

        if myconfigfile["PIDKCombinatorialShape"].has_key("name"):
            namePIDK = TString(myconfigfile["PIDKCombinatorialShape"]["name"][yr.Data()][mm.Data()])
        else:
            namePIDK = TString("None")

        pdfNames = GeneralUtils.GetList(nameBs, nameDs, namePIDK)

        EPDF = Bs2Dsh2011TDAnaModels.build_Combinatorial_MDFitter(beautyMass,charmMass, work, workInt, sm[i], types, pdfNames, pidkNames, dim, debug)
        combEPDF.append(WS(workInt,EPDF))

    return combEPDF, workInt

#------------------------------------------------------------------------------ 
def getBs2DsXPDFforBeautyMass(myconfigfile,workInt,sm,bound, mn, beautyMass,debug):

    bkgBd2DsX = []
    width1 = []
    width2 = []
    s1 = [] 
    s2 = [] 
    if myconfigfile["Bd2Ds(st)XShape"]["type"] == "ShiftedSignal":
        shift = 5369.600-5279.400
        nameMean = TString("Signal_mean")
        #mn = GeneralUtils.GetObservable(workInt, nameMean, debug)
        #mn = workInt.var(nameMean.Data())
        meanBdDsK =  RooFormulaVar("Bd2DsX_mean" , "Bd2DsX_mean",'@0-86.8', RooArgList(mn))

    for i in range(0,bound):
        s = GeneralUtils.CheckPolarity(sm[i],debug)
        mm = GeneralUtils.GetModeCapital(sm[i],debug)
        yr = GeneralUtils.CheckDataYear(sm[i],debug)
        m = GeneralUtils.CheckDMode(sm[i],debug)
        if m == "":
            m = GeneralUtils.CheckKKPiMode(sm[i],debug)
        
        if myconfigfile["Bd2Ds(st)XShape"]["type"] == "ShiftedSignal":
            
            r1 = RooRealVar( "r1", "r1", myconfigfile["Bd2Ds(st)XShape"]["scaleSigma"][yr.Data()]["frac1"] )
            r2 = RooRealVar( "r2", "r2", myconfigfile["Bd2Ds(st)XShape"]["scaleSigma"][yr.Data()]["frac2"] )

            s1Name =TString( "Signal_BeautyMass_sigma1_")+sm[i] 
            #s1 = GeneralUtils.GetObservable(workInt, s1Name, debug)
            s1.append(workInt.var(s1Name.Data()))
            s2Name = TString("Signal_BeautyMass_sigma2_")+sm[i]
            #s2 = GeneralUtils.GetObservable(workInt, s2Name, debug)
            s2.append(workInt.var(s2Name.Data())) 

            
            name = TString("Bd2DsX_sigma1_") + sm[i]
            width1.append(RooFormulaVar(name.Data(), name.Data(),'@0*@1', RooArgList(s1[i],r1)))
            name = TString("Bd2DsX_sigma2_") + sm[i]
            width2.append(RooFormulaVar(name.Data() , name.Data(),'@0*@1', RooArgList(s2[i],r2)))
            
            if myconfigfile["BsSignalShape"]["type"] == "DoubleCrystalBall": 
                name = TString("Signal_BeautyMass_alpha1_")+sm[i]
                al1 = workInt.var(name.Data())
                name = TString("Signal_BeautyMass_alpha2_")+sm[i]
                al2 = workInt.var(name.Data())

                name = TString("Signal_BeautyMass_n1_")+sm[i]
                n1 = workInt.var(name.Data())
                name = TString("Signal_BeautyMass_n2_")+sm[i]
                n2 = workInt.var(name.Data())

                name = TString("Signal_BeautyMass_frac_")+sm[i]
                frac = workInt.var(name.Data())
                bkgBd2DsX.append(WS(workInt,Bs2Dsh2011TDAnaModels.buildBdDsX(beautyMass,meanBdDsK,width1[i],al1,n1, width2[i],al2,n2,                 
                                                                             frac, sm[i], TString(myconfigfile["Bd2Ds(st)XShape"]["name"]), debug)))            
                
    #exit(0)
    return bkgBd2DsX

def getTotalBkgPDF(myconfigfile, beautyMass, charmMass, workspace, workInt, bound, Bs2DsXPDF, sm, dim, debug ):
    
    bkgPDF = [] 
    cdm = ["NonRes","PhiPi","KstK","KPiPi","PiPiPi","KKPi"]
    for i in range(0,bound):
        mm = GeneralUtils.GetModeCapital(sm[i],debug)
        if ( myconfigfile["Decay"] == "Bs2DsPi"):
            if ( mm in cdm ):
                bkgPDF.append(WS(workInt,Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_MDFitter(beautyMass,charmMass, workspace, workInt, Bs2DsXPDF[i], sm[i], dim, debug )))
        elif ( myconfigfile["Decay"] == "Bs2DsK"):
            if ( mm in cdm ):
                bkgPDF.append(WS(workInt,Bs2Dsh2011TDAnaModels.build_Bs2DsK_BKG_MDFitter(beautyMass,charmMass, workspace, workInt, Bs2DsXPDF[i], sm[i], dim, debug )))
        elif ( myconfigfile["Decay"] == "Bs2DsstPi"):
            if ( mm in cdm ):
                bkgPDF.append(WS(workInt,Bs2DssthModels.build_Bs2DsstPi_BKG(beautyMass,charmMass, workspace, workInt, sm[i], dim, debug )))
    return bkgPDF
    
#------------------------------------------------------------------------------
def runMDFitter( debug, sample, mode, sweight,  
                 fileNameAll, fileNameToys, workName,logoutputname,
                 configName, wider, merge, dim, fileDataName, year, rookeysforcombo ) :

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

    config = TString("../data/")+TString(configName)+TString(".py")
    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings")

    MDSettings = mdt.getConfig()
    MDSettings.Print("v")

    workNameTS = TString(workName)
    workspace = []
    workspace.append(GeneralUtils.LoadWorkspace(TString(fileNameAll),workNameTS,debug))
    if fileDataName == "":
        workData = workspace[0]
    else:
        workData = GeneralUtils.LoadWorkspace(TString(fileDataName),workNameTS, debug)

    
    configNameTS = TString(configName)
    if configNameTS.Contains("Toys") == False:
        toys = False
    else:
        toys = True
        workspaceToys = (GeneralUtils.LoadWorkspace(TString(fileNameToys),workNameTS, debug))
        workspaceToys.Print("v")
        workData = workspaceToys
        
    observables = getObservables(MDSettings, workData, toys, debug)

    beautyMass = observables.find(MDSettings.GetMassBVarOutName().Data())
    charmMass = NULL
    if dim>1:
        charmMass = observables.find(MDSettings.GetMassDVarOutName().Data())
    if dim>2:
        bacPIDK = observables.find(MDSettings.GetPIDKVarOutName().Data())

 ###------------------------------------------------------------------------------------------------------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------###
 ###------------------------------------------------------------------------------------------------------------------------------------###   
    dim = int(dim)
    t = TString('_')

    decayTS = myconfigfile["Decay"]
    modeTS = TString(mode)
    sampleTS = TString(sample)
    yearTS = TString(year)
    datasetTS = TString("dataSet")+decayTS+t 
    if merge:
        sampleTS = TString("both") 
    
    sam = RooCategory("sample","sample")

    sm = []
    data = []
    nEntries = []

    ### Obtain data set ###
    if toys:
        s = [TString("both")]
        m = [TString(mode)]
        sm.append(s[0]+t+m[0])
        sam.defineType(sm[0].Data())
        data.append(GeneralUtils.GetDataSet(workspaceToys,datasetTS+sm[0],debug))
        nEntries.append(data[0].numEntries())

        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sm[0].Data(),data[0]))
    else:
        combData =  GeneralUtils.GetDataSet(workData, observables, sam, datasetTS, sampleTS, modeTS, yearTS, merge, debug )
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

    lumRatio = []
    if year == "run1":
        yy = ["2011","2012"]
    else:
        yy = [year]
    for y in yy:
        lum = MDSettings.GetLumRatio(y)
        name = "lumRatio_"+y
        lumRatio.append(WS(workInt,RooRealVar(name,name, lum[1])))
    
    sigEPDF, mn, workInt = getSignalPDF(myconfigfile,workspace[0],workInt,sm,merge,bound,dim,beautyMass,charmMass,debug)

    ###------------------------------------------------------------------------------------------------------------------------------------###         
        ###-------------------------------   Create yields of backgrounds     --------------------------------------###       
    ###------------------------------------------------------------------------------------------------------------------------------------### 
    evts = TString("Evts")
    
    nYields = []
    
    for i in range(0,bound):
        print i
        print bound
        yr = GeneralUtils.CheckDataYear(sm[i])
        mm = GeneralUtils.GetModeCapital(sm[i],debug)
        print yr
        dmode = GeneralUtils.GetModeCapital(sm[i],debug)
        backgrounds = myconfigfile["Yields"]
        #print backgrounds
        
        for bkg in backgrounds:
            #print bkg 
            if bkg != "Signal":
                nameBkg = TString("n")+bkg+t+sm[i]+t+evts
                expectedYield = getExpectedYield(bkg,yr,dmode,myconfigfile)
                nYields.append(RooRealVar(nameBkg.Data() , nameBkg.Data(), expectedYield, 0.0, expectedYield*2.0))
                setConstantIfSoConfigured(nYields[nYields.__len__()-1], "Yields", bkg, mm, myconfigfile)
                getattr(workInt,'import')(nYields[nYields.__len__()-1])

    ###------------------------------------------------------------------------------------------------------------------------------------###                                
        ###-------------------------------   Create the combo PDF in Bs mass, Ds mass, PIDK --------------------------------------###                   
    ###------------------------------------------------------------------------------------------------------------------------------------###

    combEPDF, workInt = getCombinatorialPDF(myconfigfile,workspace[0],workInt,sm,bound,dim,beautyMass,charmMass,debug)

    ###------------------------------------------------------------------------------------------------------------------------------------###                                                   
        ###-------------------------------   Create the combo PDF in Bs mass, Ds mass, PIDK --------------------------------------###                                                             
    ###------------------------------------------------------------------------------------------------------------------------------------### 
    
    if myconfigfile.has_key("Bd2Ds(st)XShape"):
        Bs2DsXPDF = getBs2DsXPDFforBeautyMass(myconfigfile,workInt,sm,bound,mn,beautyMass,debug)
    else:
        Bs2DsXPDF = NULL
        
    ###------------------------------------------------------------------------------------------------------------------------------------###                                                    
        ###-------------------------------   Create the total background PDF in Bs mass, Ds mass, PIDK ------------------------------###     
    ###------------------------------------------------------------------------------------------------------------------------------------###              
    
    addVar = [] 
    if myconfigfile.has_key("AdditionalParameters"):
        add = myconfigfile["AdditionalParameters"]
        for a in add:
            if myconfigfile["AdditionalParameters"][a].has_key("Range"):
                addVar.append(RooRealVar(a,a,myconfigfile["AdditionalParameters"][a]["CentralValue"], 
                                         myconfigfile["AdditionalParameters"][a]["Range"][0], 
                                         myconfigfile["AdditionalParameters"][a]["Range"][1]))
            else:
                addVar.append(RooRealVar(a,a,myconfigfile["AdditionalParameters"][a]["CentralValue"]))
            if myconfigfile["AdditionalParameters"][a].has_key("Fixed"):
                if myconfigfile["AdditionalParameters"][a]["Fixed"] == True:
                    addVar[addVar.__len__()-1].setConstant()
                    if debug:
                        print "Parameter: %s set to be constant with value %lf"%(addVar[addVar.__len__()-1].GetName(),addVar[addVar.__len__()-1].getValV())
            getattr(workInt,'import')(addVar[addVar.__len__()-1])

    bkgPDF = getTotalBkgPDF(myconfigfile, beautyMass, charmMass, workspace[0], workInt, bound, Bs2DsXPDF, sm, dim, debug )
    ###------------------------------------------------------------------------------------------------------------------------------------### 
          ###---------------------------------   Create the total PDF in Bs mass, Ds mass, PIDK --------------------------------------###  
    ###------------------------------------------------------------------------------------------------------------------------------------###  

    N_Bkg_Tot = []

    
    totPDFp = []
    totPDFa = []
    for i in range(0,bound):
        name = TString("TotEPDF_m_")+sm[i]
        print sigEPDF[i].GetName()
        #print Bd2DsstKEPDF[i].GetName()
        print bkgPDF[i].GetName()
        totPDFp.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass', RooArgList( sigEPDF[i], combEPDF[i], bkgPDF[i]))) #Bd2DsstKEPDF[i] )))
        
    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    for i in range(0,bound):
        print totPDFp[i].GetName()
        print sm[i].Data()
        totPDF.addPdf(totPDFp[i], sm[i].Data())
    totPDF.Print("v")
    
    ###------------------------------------------------------------------------------------------------------------------------------------###    
          ###--------------------------------------------  Instantiate and run the fitter  -------------------------------------------###  
    ###------------------------------------------------------------------------------------------------------------------------------------###
    #sigEPDF[0].Print("v") 
    #sigEPDF[0].fitTo(combData) 

    fitter = FitMeTool( debug )
      
    fitter.setObservables( observables )

    fitter.setModelPDF( totPDF )
    fitter.setData(combData) 

    #fitter.setModelPDF( bkgPDF[0] ) #totPDF )

    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    if plot_init :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )
   
    import sys
    import random
    #sys.stdout = open(logoutputname, 'w')
    #exit(0) 
    fitter.fit(True, RooFit.Extended()) #,  RooFit.Verbose(False),  RooFit.ExternalConstraints(constList)) #, RooFit.InitialHesse(True))
    result = fitter.getFitResult()
    result.Print("v")
    floatpar = result.floatParsFinal()
        
    if dim == 1:
        fitter.printYieldsInRange( '*Evts', MDSettings.GetMassBVarOutName().Data() , 5320, 5420 )
    elif dim == 2:
        fitter.printYieldsInRange( '*Evts', MDSettings.GetMassBVarOutName().Data() , 5320, 5420, "SignalRegion",
                                   charmMass.GetName(), charmMass.getMin(),  charmMass.getMax() )
    else:
        fitter.printYieldsInRange( '*Evts', MDSettings.GetMassBVarOutName().Data() , 5320, 5420, "SignalRegion",
                                   charmMass.GetName(), charmMass.getMin(), charmMass.getMax(),
                                   bacPIDK.GetName(), bacPIDK.getMin(), bacPIDK.getMax())
    if plot_fitted :
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
                   default = 'WS_Mass_DsstK.root', 
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )

parser.add_option( '--sweightoutputname',
                   dest = 'sweightoutputname',
                   default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsPi_Toys_Full_sWeights_ForTimeFit_0.root', 
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )   

parser.add_option( '--logoutputname',
                   dest = 'logoutputname',
                   default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsPi_Toys_Full_MassFitResult_0.log'
                   )   

parser.add_option( '-i', '--initial-vars',
                   dest = 'initvars',
                   action = 'store_true',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '-m', '--sample',
                   dest = 'sample',
                   metavar = 'SAMPLE',
                   default = 'down',
                   help = 'Sample: choose up or down '
                   )
parser.add_option( '-o', '--mode',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'kkpi',
                   help = 'Mode: choose all, kkpi, kpipi or pipipi'
                   )
parser.add_option( '-w', '--sweight',
                   dest = 'sweight',
                   action = 'store_true',
                   default = False,
                   help = 'create and save sWeights'
                   )

parser.add_option( '--fileName',
                   dest = 'fileNameAll',
                   default = 'work_dsstk.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--fileNameToys',
                   dest = 'fileNameToys',
                   default = '../data/workspace/work_dsk.root',
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
parser.add_option( '--wider',
                   dest = 'wider',
                   action = 'store_true',
                   default = False,
                   help = 'create and save sWeights'
                   )
parser.add_option( '--merge',
                   dest = 'merge',
                   action = 'store_true',
                   default = False,
                   help = 'merge magnet polarity'
                   )
parser.add_option( '--dim',
                   dest = 'dim',
                   default = 1)

parser.add_option( '--fileData',
                   dest = 'fileData',
                   default = '',
                   help = 'you can use it if you have separate files with templates and data'
                   )
parser.add_option( '--year',
                   dest = 'year',
                   default = "")

parser.add_option( '--rookeysforcombo',
                   dest = 'rookeysforcombo',
                   action = 'store_true',
                   default = False,
                   help = 'use RooKeysPdf for combinatorial shape'
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    import sys
    sys.path.append("../data/")
        
    runMDFitter( options.debug,  options.sample, options.mode, options.sweight, 
                 options.fileNameAll, options.fileNameToys, options.workName,
                 options.logoutputname, options.configName, options.wider, 
                 options.merge, options.dim, options.fileData, options.year, options.rookeysforcombo)

# -----------------------------------------------------------------------------
