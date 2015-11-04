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
#-----------------------------------------------------------------------------

def getTotalBkgPDF(myconfigfile, beautyMass, charmMass, workspace, workInt, merge, bound, sm, dim, debug ):
    
    bkgPDF = [] 
    cdm = ["NonRes","PhiPi","KstK","KPiPi","PiPiPi","KKPi"]
    for i in range(0,bound):
        mm = GeneralUtils.GetModeCapital(sm[i],debug)
        if ( myconfigfile["Decay"] == "Bs2DsPi"):
            if ( mm in cdm ):
                bkgPDF.append(WS(workInt,Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_MDFitter(beautyMass,charmMass, workspace, workInt, sm[i], merge, dim, debug )))
        elif ( myconfigfile["Decay"] == "Bs2DsK"):
            if ( mm in cdm ):
                bkgPDF.append(WS(workInt,Bs2Dsh2011TDAnaModels.build_Bs2DsK_BKG_MDFitter(beautyMass,charmMass, workspace, workInt, sm[i], merge, dim, debug )))
        elif ( myconfigfile["Decay"] == "Bs2DsstPi"):
            if ( mm in cdm ):
                bkgPDF.append(WS(workInt,Bs2DssthModels.build_Bs2DsstPi_BKG(beautyMass,charmMass, workspace, workInt, sm[i], merge, dim, debug )))
        elif ( myconfigfile["Decay"] == "Bs2DsstK"):
            if ( mm in cdm ):
                bkgPDF.append(WS(workInt,Bs2DssthModels.build_Bs2DsstK_BKG(beautyMass,charmMass, workspace, workInt, sm[i], merge, dim, debug )))

    return bkgPDF
    
#------------------------------------------------------------------------------
def runMDFitter( debug, sample, mode, sweight,  
                 fileNameAll, fileNameToys, workName, sweightName,
                 configName, wider, merge, dim, fileDataName, year) :

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
    

    from B2DXFitters.mdfitutils import getExpectedValue as getExpectedValue
    from B2DXFitters.mdfitutils import getExpectedYield as getExpectedYield
    from B2DXFitters.mdfitutils import setConstantIfSoConfigured as setConstantIfSoConfigured
    from B2DXFitters.mdfitutils import getObservables  as getObservables 
    from B2DXFitters.mdfitutils import readVariables as readVariables
    from B2DXFitters.mdfitutils import getSigOrCombPDF as getSigOrCombPDF
    from B2DXFitters.mdfitutils import getType as getType
    from B2DXFitters.mdfitutils import getPDFNameFromConfig as getPDFNameFromConfig
    from B2DXFitters.mdfitutils import getPIDKComponents as getPIDKComponents
    from B2DXFitters.mdfitutils import setBs2DsXParameters as setBs2DsXParameters
    

    mdt = Translator(myconfigfile,"MDSettings",False)

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
    charmMass = observables.find(MDSettings.GetMassDVarOutName().Data())
    bacPIDK = observables.find(MDSettings.GetPIDKVarOutName().Data())
    obs = [beautyMass, charmMass, bacPIDK]
        
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
    if merge == "pol" or merge == "both":
        sampleTS = TString("both") 
    if merge == "year" or merge == "both":
        yearTS = TString("run1") 

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

    bound = sm.__len__()
    ranmode = m.__len__()*y.__len__()
    ransample = s.__len__()

    

    #exit(0) 
    ###------------------------------------------------------------------------------------------------------------------------------------###    
          ###-------------------------   Create the signal PDF in Bs mass, Ds mass, PIDK   ------------------------------------------###          
    ###------------------------------------------------------------------------------------------------------------------------------------###        
    
    from B2DXFitters.WS import WS as WS
    workInt = RooWorkspace("workInt","workInt")    

    lumRatio = []
    if year == "run1":
        yy = ["2011","2012", "run1", "down", "up"]
    else:
        yy = [year]
    for y in yy:
        lum = MDSettings.GetLumRatio(y)
        print lum[0],  lum[1] 
        name = "lumRatio_"+y
        lumRatio.append(WS(workInt,RooRealVar(name,name, lum[1])))


    workInt.Print("v")

    #exit(0) 
    ###------------------------------------------------------------------------------------------------------------------------------------###         
        ###-------------------------------   Create yields of backgrounds     --------------------------------------###       
    ###------------------------------------------------------------------------------------------------------------------------------------### 
    evts = TString("Evts")
    
    nYields = []
    other = False
    signal = False 
    combo = False 

    for i in range(0,bound):
        print i
        print bound
        yr = GeneralUtils.CheckDataYear(sm[i])
        mm = GeneralUtils.GetModeCapital(sm[i],debug)
        print yr
        dmode = GeneralUtils.GetModeCapital(sm[i],debug)
        backgrounds = myconfigfile["Yields"]
        pol = GeneralUtils.CheckPolarityCapital(sm[i],debug)
        #print backgrounds
        
        for bkg in backgrounds:
            if bkg != "Signal":
                nameBkg = TString("n")+bkg+t+sm[i]+t+evts
            else:
                nameBkg = TString("nSig")+t+sm[i]+t+evts
                signal = True
            if bkg == "CombBkg" or bkg == "Combinatorial":
                combo = True
            if bkg != "Signal" and bkg != "Combinatorial" and bkg != "CombBkg":
                other = True

            expectedYield = getExpectedYield(bkg,yr,dmode,pol,merge,myconfigfile)
            nYields.append(RooRealVar(nameBkg.Data() , nameBkg.Data(), expectedYield, 0.0, expectedYield*2.0))
            setConstantIfSoConfigured(nYields[nYields.__len__()-1], "Yields", bkg, mm, pol, myconfigfile)
            getattr(workInt,'import')(nYields[nYields.__len__()-1])

    ###------------------------------------------------------------------------------------------------------------------------------------###                                
        ###-------------------------------   Create the combo and signal PDF in Bs mass, Ds mass, PIDK --------------------------------------###                   
    ###------------------------------------------------------------------------------------------------------------------------------------###

    keysSig = ["BsSignalShape","DsSignalShape","PIDKSignalShape"]
    if signal:
        sigEPDF, workInt = getSigOrCombPDF(myconfigfile,keysSig,TString("Signal"),
                                           workspace[0],workInt,sm,merge,bound,dim,obs, debug)

    keysComb = ["BsCombinatorialShape","DsCombinatorialShape","PIDKCombinatorialShape"]
    if combo:
        combEPDF, workInt = getSigOrCombPDF(myconfigfile,keysComb,TString("CombBkg"),
                                            workspace[0],workInt,sm,merge,bound,dim,obs, debug)
    
    workInt = setBs2DsXParameters(myconfigfile, workInt, sm, merge,bound, beautyMass,debug)
    
    ###------------------------------------------------------------------------------------------------------------------------------------###     
        ###-------------------------------   Create the total background PDF in Bs mass, Ds mass, PIDK ------------------------------###     
    ###------------------------------------------------------------------------------------------------------------------------------------###              
    
    addVar = [] 
    if myconfigfile.has_key("AdditionalParameters"):
        add = myconfigfile["AdditionalParameters"]
        for a in add:
            year = myconfigfile["AdditionalParameters"][a]
            for y in year:
                if y != "Fixed": 
                    mode = myconfigfile["AdditionalParameters"][a][y]
                    for m in mode:
                        pol = myconfigfile["AdditionalParameters"][a][y][m]
                        for p in pol:
                            pp = GeneralUtils.CheckPolarity(TString(p),False)
                            yy = GeneralUtils.CheckDataYear(TString(y),False)
                            mm = GeneralUtils.CheckDMode(TString(m),False)
                            if mm == "":
                                mm = GeneralUtils.CheckKKPiMode(TString(m),debug)
                            if m == "All":
                                mm = "all"
                            t = TString("_")
                            ssmm = t + pp + t + mm + t + yy
                            name = TString(a) + ssmm 
                            if myconfigfile["AdditionalParameters"][a][y][m][p].has_key("Range"):
                                addVar.append(RooRealVar(name.Data(),name.Data(),myconfigfile["AdditionalParameters"][a][y][m][p]["CentralValue"], 
                                                         myconfigfile["AdditionalParameters"][a][y][m][p]["Range"][0], 
                                                         myconfigfile["AdditionalParameters"][a][y][m][p]["Range"][1]))
                            else:
                                addVar.append(RooRealVar(name.Data(),name.Data(),myconfigfile["AdditionalParameters"][a][y][m][p]["CentralValue"]))
                            if myconfigfile["AdditionalParameters"][a].has_key("Fixed"):
                                if myconfigfile["AdditionalParameters"][a]["Fixed"] == True:
                                    addVar[addVar.__len__()-1].setConstant()
                                    if debug:
                                        print "Parameter: %s set to be constant with value %lf"%(addVar[addVar.__len__()-1].GetName(),addVar[addVar.__len__()-1].getValV())
                            getattr(workInt,'import')(addVar[addVar.__len__()-1])

    
    if other == True:
        bkgPDF = getTotalBkgPDF(myconfigfile, beautyMass, charmMass, workspace[0], workInt, merge, bound, sm, dim, debug )
    ###------------------------------------------------------------------------------------------------------------------------------------### 
          ###---------------------------------   Create the total PDF in Bs mass, Ds mass, PIDK --------------------------------------###  
    ###------------------------------------------------------------------------------------------------------------------------------------###  
    #exit(0)    
    
    N_Bkg_Tot = []
    listPDF = [] 
    totPDFp = []
    totPDFa = []
    for i in range(0,bound):
        listPDF.append(RooArgList())
        if signal:
            listPDF[i].add(sigEPDF[i])
        if combo:
            listPDF[i].add( combEPDF[i] )
        if other:
            listPDF[i].add(  bkgPDF[i] ) 
        name = TString("TotEPDF_m_")+sm[i] 
        totPDFp.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass', listPDF[i])) 
    
    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    for i in range(0,bound):
        print totPDFp[i].GetName()
        print sm[i].Data()
        totPDF.addPdf(totPDFp[i], sm[i].Data())
    totPDF.Print("v")
    
    ###------------------------------------------------------------------------------------------------------------------------------------###    
          ###--------------------------------------------  Instantiate and run the fitter  -------------------------------------------###  
    ###------------------------------------------------------------------------------------------------------------------------------------###

    fitter = FitMeTool( debug )
      
    fitter.setObservables( observables )

    fitter.setModelPDF( totPDF )
    fitter.setData(combData) 

    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    if plot_init :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )
   
    import sys
    import random
    
    fitter.fit(True, RooFit.Extended(), RooFit.NumCPU(4)) #,  RooFit.Verbose(False),  RooFit.ExternalConstraints(constList)) #, RooFit.InitialHesse(True))
    result = fitter.getFitResult()
    result.Print("v")
    floatpar = result.floatParsFinal()
    
    name = TString(sweightName)
    if (sweight):
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(RooFit.Eval)
        fitter.savesWeights(beautyMass.GetName(), combData, name)
        RooMsgService.instance().reset()

    
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
                   default = 'WS_MDFit_Results.root', 
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )

parser.add_option( '--sweightName',
                   dest = 'sweightName',
                   default = 'sWeights_Results.root', 
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
parser.add_option( '-p', '--pol','--polarity',
                   dest = 'pol',
                   metavar = 'POL',
                   default = 'down',
                   help = 'Sample: choose up or down '
                   )
parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'kkpi',
                   help = 'Mode: choose all, kkpi, kpipi, pipipi, nonres, kstk, phipi, 3modeskkpi'
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
                   default = '../data/Bs2DsK_3fbCPV/Bs2DsK/Bs2DsKConfigForNominalMassFit.py',
                   help = "name of the configuration file, the full path to the file is mandatory")
parser.add_option( '--wider',
                   dest = 'wider',
                   action = 'store_true',
                   default = False,
                   help = 'create and save sWeights'
                   )
parser.add_option( '--merge',
                   dest = 'merge',
                   default = "",
                   help = 'for merging magnet polarities use: --merge pol, for merging years of data taking use: --merge year, for merging both use: --merge both'
                   )

parser.add_option( '--dim',
                   dest = 'dim',
                   default = 1,
                   help = "Number of dimensionl of fit: 1 dim = beauty meson mass, 2 dim = beauty and charm meson mass, 3 dim == beauty and charm meson mass and pidk of bachelor")

parser.add_option( '--fileData',
                   dest = 'fileData',
                   default = '',
                   help = 'you can use it if you have separate files with templates and data'
                   )
parser.add_option( '--year',
                   dest = 'year',
                   default = "",
                   help = 'year of data taking can be: 2011, 2012, run1')

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

        
    runMDFitter( options.debug,  options.pol, options.mode, options.sweight, 
                 options.fileNameAll, options.fileNameToys, options.workName,
                 options.sweightName, configName, options.wider, 
                 options.merge, options.dim, options.fileData, options.year)

# -----------------------------------------------------------------------------
