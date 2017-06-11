# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to generate toys for DPi                                    #
#                                                                             #
#   Example usage:                                                            #
#      python GenerateToySWeights_DPi.py                                      #
#                                                                             #
#   Author: Vava Gligorov                                                     #
#   Date  : 14 / 06 / 2012                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 06 / 2012                                                    #
#   Author: Vincenzo Battista                                                 #
#   Date  : 06 / 10 / 2015                                                    #
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
#"
import B2DXFitters
import ROOT
from B2DXFitters import *
from ROOT import *
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
import os, sys, gc
import copy

from B2DXFitters.timepdfutils import buildBDecayTimePdf
from B2DXFitters.resmodelutils import getResolutionModel
from B2DXFitters.acceptanceutils import buildSplineAcceptance

from B2DXFitters.WS import WS as WS
ws = RooWorkspace("intWork","intWork")

gROOT.SetBatch()

from B2DXFitters import taggingutils, cpobservables
RooAbsData.setDefaultStorageType(RooAbsData.Tree)
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)


# Some convenient constants when we build up the decays
half     = RooRealVar('half','0.5',0.5)
zero     = RooRealVar('zero', '0', 0.)
one      = RooRealVar('one', '1', 1.)
minusone = RooRealVar('minusone', '-1', -1.)
two      = RooRealVar('two', '2', 2.)

#------------------------------------------------------------------------------
def printifdebug(debug,toprint) :
    if debug : print toprint

#------------------------------------------------------------------------------
def GenTimePdfUtils(configfile,
                    workspace,
                    mode,
                    Gamma,
                    DeltaGamma,
                    DeltaM,
                    singletagger,
                    notagging,
                    noprodasymmetry,
                    notagasymmetries,
                    debug) :

    print ""
    print "================================================================"
    print " Utilities for " +str(mode)+ " generating PDF..."
    print "================================================================"
    print ""
            
    #CP observables
    print "=> Defining CP observables..."
            
    if mode == "Signal":
        ACPobs = cpobservables.AsymmetryObservables(configfile["DecayRate"]["ArgLf_d"], configfile["DecayRate"]["ArgLbarfbar_d"], configfile["DecayRate"]["ModLf_d"])
        ACPobs.printtable()
        
        C     = WS(workspace,RooRealVar('C_'+str(mode),'C_'+str(mode),ACPobs.Cf()))
        S     = WS(workspace,RooRealVar('S_'+str(mode),'S_'+str(mode),ACPobs.Sf()))
        D     = WS(workspace,RooRealVar('D_'+str(mode),'D_'+str(mode),ACPobs.Df()))
        Sbar  = WS(workspace,RooRealVar('Sbar_'+str(mode),'Sbar_'+str(mode),ACPobs.Sfbar()))
        Dbar  = WS(workspace,RooRealVar('Dbar_'+str(mode),'Dbar_'+str(mode),ACPobs.Dfbar()))

        #C     = WS(workspace,RooRealVar('C_'+str(mode),'C_'+str(mode),0.0))
        #S     = WS(workspace,RooRealVar('S_'+str(mode),'S_'+str(mode),0.0))
        #D     = WS(workspace,RooRealVar('D_'+str(mode),'D_'+str(mode),0.0))
        #Sbar  = WS(workspace,RooRealVar('Sbar_'+str(mode),'Sbar_'+str(mode),0.0))
        #Dbar  = WS(workspace,RooRealVar('Dbar_'+str(mode),'Dbar_'+str(mode),0.0))
        
    elif mode == "Lb2LcPi" or mode == "Combo":
        C     = WS(workspace,RooRealVar('C_'+str(mode),'C_'+str(mode),0.0))
        S     = WS(workspace,RooRealVar('S_'+str(mode),'S_'+str(mode),0.0))
        D     = WS(workspace,RooRealVar('D_'+str(mode),'D_'+str(mode),0.0))
        Sbar  = WS(workspace,RooRealVar('Sbar_'+str(mode),'Sbar_'+str(mode),0.0))
        Dbar  = WS(workspace,RooRealVar('Dbar_'+str(mode),'Dbar_'+str(mode),0.0))
        
    else:
        C     = WS(workspace,RooRealVar('C_'+str(mode),'C_'+str(mode),1.0))
        S     = WS(workspace,RooRealVar('S_'+str(mode),'S_'+str(mode),0.0))
        D     = WS(workspace,RooRealVar('D_'+str(mode),'D_'+str(mode),0.0))
        Sbar  = WS(workspace,RooRealVar('Sbar_'+str(mode),'Sbar_'+str(mode),0.0))
        Dbar  = WS(workspace,RooRealVar('Dbar_'+str(mode),'Dbar_'+str(mode),0.0))
        
    #Tagging efficiency
    print "=> Getting tagging efficiency..."
    tagEff = []
    tagEffList = []
    if notagging:
        print "=> Perfect tagging"
        if singletagger:
            print "=> Single tagger"
            tagEff.append(WS(workspace,RooRealVar('tagEff_'+str(mode)+'_'+str(1), str(mode)+' tagging efficiency', 1.0)))
            printifdebug(debug,tagEff[0].GetName()+": "+str(tagEff[0].getVal()) )
            tagEffList.append(tagEff[0])
        else:
            print "=> More taggers"
            for i in range(0,3):
                tagEff.append(WS(workspace,RooRealVar('tagEff_'+str(mode)+'_'+str(i+1), str(mode)+' tagging efficiency', 1.0)))
                printifdebug(debug,tagEff[i].GetName()+": "+str(tagEff[i].getVal()) )
                tagEffList.append(tagEff[i])
    else:
        print "=> Non-trivial tagging"
        if singletagger:
            print "=> Single tagger"
            tagEff.append(WS(workspace,RooRealVar('tagEff_'+str(mode)+'_'+str(1), str(mode)+' tagging efficiency', configfile["TagEff"][mode][0])))
            printifdebug(debug,tagEff[0].GetName()+": "+str(tagEff[0].getVal()) )
            tagEffList.append(tagEff[0])
        else:
            print "=> More taggers"
            for i in range(0,3):
                tagEff.append(WS(workspace,RooRealVar('tagEff_'+str(mode)+'_'+str(i+1), str(mode)+' tagging efficiency', configfile["TagEff"][mode][i])))
                printifdebug(debug,tagEff[i].GetName()+": "+str(tagEff[i].getVal()) )
                tagEffList.append(tagEff[i])
                
    #Asymmetries
    print "=> Getting production asymmetry..."
    if noprodasymmetry:
        print "=> No asymmetries"
        aProd = None
    else:
        print "=> Non-zero asymmetry"
        aProd   = WS(workspace,RooConstVar('aprod_'+str(mode),   'aprod_'+str(mode),   configfile["AProd"][mode]))
        printifdebug(debug,aProd.GetName()+": "+str(aProd.getVal()) )
    
    print "=> Getting tagging asymmetries..."
    if notagasymmetries:
        print "=> No asymmetries"
        aTagEffList = None            
    else:
        aTagEff = []
        aTagEffList = []
        print "=> Non-zero asymmetries"
        if singletagger:
            aTagEff.append(WS(workspace,RooRealVar('aTagEff_'+str(mode)+'_'+str(1), 'atageff', configfile["ATagEff"][mode][0])))
            printifdebug(debug,aTagEff[0].GetName()+": "+str(aTagEff[0].getVal()) )
            aTagEffList.append(aTagEff[0])
        else:
            for i in range(0,3):
                aTagEff.append(WS(workspace,RooRealVar('aTagEff_'+str(mode)+'_'+str(i+1), 'atageff', configfile["ATagEff"][mode][i])))
                printifdebug(debug,aTagEff[i].GetName()+": "+str(aTagEff[i].getVal()) )
                aTagEffList.append(aTagEff[i])

    #Summary of memory location
    if debug:
        print "==> Memory location of returned objects:"
        print "C: "
        print C
        print C.getVal()
        print "D: "
        print D
        print D.getVal()
        print "Dbar: "
        print Dbar
        print Dbar.getVal()
        print "S: "
        print S
        print S.getVal()
        print "Sbar: "
        print Sbar
        print Sbar.getVal()
        print "aProd: "
        print aProd
        if None != aProd: print aProd.getVal()
        print "tagEff: "
        print tagEff
        print "aTagEff: "
        print aTagEffList
    
    #Return things
    return { 'C': C,
             'D': D,
             'Dbar': Dbar,
             'S': S,
             'Sbar': Sbar,
             'aProd': aProd,
             'tagEff': tagEffList,
             'aTagEff': aTagEffList } 

#------------------------------------------------------------------------------  
def runBDPiGenerator(  debug, single, configName, year, rangeDown, rangeUp,
                       seed, dir, savetree,
                       noresolution, noacceptance, notagging,
                       noprodasymmetry, nodetasymmetry, notagasymmetries, nobackground,
                       singletagger, meanresolution, singlecalibration) :

    if meanresolution and noresolution:
        print '==> ERROR: cannot have meanresolution and noresolution options at the same time!'
        exit(-1)

    if notagging and not singletagger:
        print "ERROR: having more perfect taggers is meaningless! Please check your options"
        exit(-1)

    print "=========================================================="
    print "===============STARTING THE TOY GENERATOR================="
    print "=========================================================="
    
    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()
    # 
    print "=========================================================="
    print "THE GENERATOR IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="
    #
    if debug:
        myconfigfile['Debug'] = True
    else:
        myconfigfile['Debug'] = False

    config = TString("../data/")+TString(configName)+TString(".py")
    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings",False)
    
    MDSettings = mdt.getConfig()
    MDSettings.Print("v")

    #Choosing generation context
    myconfigfile['Context'] = 'GEN'

    # Seed and yields
    gInterpreter.ProcessLine('gRandom->SetSeed('+str(int(seed)*int(seed))+')')
    RooRandom.randomGenerator().SetSeed(int(seed)) 
    print "Generating toys beginning with seed",int(seed)

    # Our parameters
    Gammad       = RooRealVar('Gammad','Gammad', myconfigfile["DecayRate"]["Gammad"])                     # in ps^{-1}
    Gammas       = RooRealVar('Gammas','Gammas', myconfigfile["DecayRate"]["Gammas"])                     # in ps^{-1}
    DeltaGammad  = RooRealVar('DeltaGammad','DeltaGammad', myconfigfile["DecayRate"]["DeltaGammad"])      # in ps^{-1}
    DeltaGammas  = RooRealVar('DeltaGammas','DeltaGammas', myconfigfile["DecayRate"]["DeltaGammas"])      # in ps^{-1}
    DeltaMd      = RooRealVar('DeltaMd','DeltaMd', myconfigfile["DecayRate"]["DeltaMd"])                  # in ps^{-1}
    DeltaMs      = RooRealVar('DeltaMs','DeltaMs', myconfigfile["DecayRate"]["DeltaMs"])                  # in ps^{-1}
    GammaLb      = RooRealVar('GammaLb','GammaLb', myconfigfile["DecayRate"]["GammaLb"])

    GammaCombo = []
    DeltaGammaCombo = []
    TauInvCombo = []
    ComboLabel = ["OS","SSPiBDT","OS+SSPiBDT","UN"]

    GammaCombo       = RooRealVar('Gammad','Gammad', myconfigfile["DecayRate"]["GammaCombo"][0])
    DeltaGammaCombo  = RooRealVar('DeltaGammad','DeltaGammad', myconfigfile["DecayRate"]["DeltaGammaCombo"][0])
    TauInvCombo      = Inverse( "TauInvCombo","TauInvCombo", GammaCombo)
        
    # Which polarity?
    magpol = TString("both")
    lumRatio = RooRealVar("lumRatio","lumRatio",myconfigfile["LumRatio"][year])
    yearTS = TString(year)
    # Enforce that we are doing the 2D generation
    dim = int(2) 
    gendata = []
    data = []
    # Some names
    workName = 'workspace'
    fileNamePrefix = "DPi_Toys_"
    # Read workspace with PDFs
    workspace = GeneralUtils.LoadWorkspace(TString(myconfigfile["Toys"]["fileName"]),TString(workName), debug)
    # 
    workTerr = GeneralUtils.LoadWorkspace(TString(myconfigfile["Toys"]["fileNameTerr"]),TString(workName), debug)
    #
    workMistag = GeneralUtils.LoadWorkspace(TString(myconfigfile["Toys"]["fileNameMistag"]),TString(workName), debug)
    #
    workMistagBDPi = GeneralUtils.LoadWorkspace(TString(myconfigfile["Toys"]["fileNameMistagBDPi"]),TString(workName), debug)
    #
    workMistagComb = GeneralUtils.LoadWorkspace(TString(myconfigfile["Toys"]["fileNameMistagComb"]),TString(workName), debug)
    
    # Define the observables we care about
    mVar         = myconfigfile["BasicVariables"]["BeautyMass"]["Name"]
    mdVar        = myconfigfile["BasicVariables"]["CharmMass"]["Name"]
    tVar         = myconfigfile["BasicVariables"]["BeautyTime"]["Name"]
    terrVar      = myconfigfile["BasicVariables"]["BeautyTimeErr"]["Name"]
    charge       = myconfigfile["BasicVariables"]["BacCharge"]["Name"]
    tagdec       = [myconfigfile["BasicVariables"]["TagDecOS"]["Name"],
                    myconfigfile["BasicVariables"]["TagDecSS"]["Name"]]
    tagomega     = [myconfigfile["BasicVariables"]["MistagOS"]["Name"],
                    myconfigfile["BasicVariables"]["MistagSS"]["Name"]]
    # Now grab them from the workspace   
    timeVar_B       = WS(ws,GeneralUtils.GetObservable(workspace,TString(tVar), debug))
    timeVar_B.setRange(myconfigfile["BasicVariables"]["BeautyTime"]["Range"][0],
                       myconfigfile["BasicVariables"]["BeautyTime"]["Range"][1])
    timeVar_B.Print("v")
    
    terrVar_B       = WS(ws,GeneralUtils.GetObservable(workspace,TString(terrVar), debug))
    terrVar_B.setRange(myconfigfile["BasicVariables"]["BeautyTimeErr"]["Range"][0],
                       myconfigfile["BasicVariables"]["BeautyTimeErr"]["Range"][1])
    terrVar_B.Print("v")

    massVar_D       = WS(ws,GeneralUtils.GetObservable(workspace,TString(mdVar), debug))
    massVar_D.setRange(myconfigfile["BasicVariables"]["CharmMass"]["Range"][0],
                       myconfigfile["BasicVariables"]["CharmMass"]["Range"][1])
    massVar_D.Print("v")

    massVar_B       = WS(ws,GeneralUtils.GetObservable(workspace,TString(mVar), debug))
    massVar_B.setRange(myconfigfile["BasicVariables"]["BeautyMass"]["Range"][0],
                       myconfigfile["BasicVariables"]["BeautyMass"]["Range"][1])
    massVar_B.Print("v")

    idVar_B         = WS(ws,GeneralUtils.GetCategory(workspace,TString(charge), debug))
    idVar_B.Print("v")

    #Acceptance
    if noacceptance:
        print '==> Perfect acceptance ("straight line")'
        tacc = None
        taccNorm = None
    else:
        print '==> Time-dependent acceptance'
        tacc, taccNorm = buildSplineAcceptance(ws,
                                               timeVar_B,
                                               "splinePDF",
                                               myconfigfile["AcceptanceKnots"],
                                               myconfigfile["AcceptanceValues"],
                                               False,
                                               debug)
        
        #For generation, we use normalized acceptance
        tacc = taccNorm
        tacc.Print("v")

    #Resolution model
    if noresolution:
        print '===> Using perfect resolution'
        trm = None
    else:
        if meanresolution:
            print '===> Using a mean resolution model'
            myconfigfile["DecayTimeResolutionModel"] = myconfigfile["DecayTimeResolutionMeanModel"]
        else:
            print '===> Using a per-event time resolution'
            myconfigfile["DecayTimeResolutionModel"] = myconfigfile["DecayTimeResolutionPEDTE"]
            
        trm, tacc = getResolutionModel(ws, myconfigfile, timeVar_B, terrVar_B, tacc)
        trm.Print("v")
        tacc.Print("v")
        
    # Tagging parameters : note that we now deal with tagging calibration
    # uncertainties exclusively from the data, so this is not handled here
    # on purpose.
    tagVar_B            = []
    mistagVar_B         = []
    mistagBs            = []
    mistagBd            = []
    mistagComb          = []
    mistagBsPDFList     = []
    mistagBdPDFList     = []
    mistagCombPDFList   = []

    mistagCalibB        = []
    mistagCalibBbar     = []
    tagOmegaList        = []

    p0B = []
    p0Bbar = []
    p1B = []
    p1Bbar = []
    avB = []
    avBbar = []
                        
    # Now grab the combined tagging decision
    tagOmegaComb = WS(ws,GeneralUtils.GetObservable(workspace,TString("tagOmegaComb"), debug))
    if singletagger:
        tagDecComb = WS(ws,RooCategory("tagDecComb","tagDecComb"))
        tagDecComb.defineType("Bbar_1",-1)
        tagDecComb.defineType("Untagged",0)
        tagDecComb.defineType("B_1",+1)
        
    else:
        tagDecComb   = WS(ws,GeneralUtils.GetCategory(workspace,TString("tagDecComb"), debug))
        
    tagOmegaComb.setConstant(False)
    tagDecComb.setConstant(False)
    tagOmegaComb.setRange(0.0, 0.5)

    tagDecComb.Print("v")
    tagOmegaComb.Print("v")
    #
    if notagging:
        print '==> No tagging: <eta>=0'
        tagOmegaComb.setVal(0.0)
        tagOmegaComb.setConstant(True)
        tagOmegaList += [ [tagOmegaComb ] ]
            
    else:
        if singletagger:
            print '==> Using a single tagger (by default, use the well-established standard OS)'
            p0B.append(RooRealVar('p0_B_OS', 'p0_B_OS', myconfigfile["TaggingCalibration"]["OS"]["p0"]))
            p1B.append(RooRealVar('p1_B_OS', 'p1_B_OS', myconfigfile["TaggingCalibration"]["OS"]["p1"]))
            avB.append(RooRealVar('av_B_OS', 'av_B_OS', myconfigfile["TaggingCalibration"]["OS"]["average"]))
            p0Bbar.append(RooRealVar('p0_Bbar_OS', 'p0_B_OS', myconfigfile["TaggingCalibration"]["OS"]["p0Bar"]))
            p1Bbar.append(RooRealVar('p1_Bbar_OS', 'p1_B_OS', myconfigfile["TaggingCalibration"]["OS"]["p1Bar"]))
            avBbar.append(RooRealVar('av_Bbar_OS', 'av_B_OS', myconfigfile["TaggingCalibration"]["OS"]["averageBar"]))
            
            mistagCalibB.append(MistagCalibration("mistagCalib_B_OS", "mistagCalib_B_OS", tagOmegaComb, p0B[0], p1B[0], avB[0]))
            mistagCalibBbar.append(MistagCalibration("mistagCalib_Bbar_OS", "mistagCalib_Bbar_OS", tagOmegaComb, p0Bbar[0], p1Bbar[0], avBbar[0]))

            tagOmegaList += [ [mistagCalibB[0],mistagCalibBbar[0]] ]
        else:
            print '==> Combining more taggers'
            i=0
            for tag in ["OS","SS","OS+SS"]:
                p0B.append(RooRealVar('p0_B_'+tag, 'p0_B_'+tag, myconfigfile["TaggingCalibration"][tag]["p0"]))
                p1B.append(RooRealVar('p1_B_'+tag, 'p1_B_'+tag, myconfigfile["TaggingCalibration"][tag]["p1"]))
                avB.append(RooRealVar('av_B_'+tag, 'av_B_'+tag, myconfigfile["TaggingCalibration"][tag]["average"]))
                p0Bbar.append(RooRealVar('p0_Bbar_'+tag, 'p0_B_'+tag, myconfigfile["TaggingCalibration"][tag]["p0Bar"]))
                p1Bbar.append(RooRealVar('p1_Bbar_'+tag, 'p1_B_'+tag, myconfigfile["TaggingCalibration"][tag]["p1Bar"]))
                avBbar.append(RooRealVar('av_Bbar_'+tag, 'av_B_'+tag, myconfigfile["TaggingCalibration"][tag]["averageBar"]))
                
                mistagCalibB.append(MistagCalibration("mistagCalib_B_"+tag, "mistagCalib_B_"+tag, tagOmegaComb, p0B[i], p1B[i], avB[i]))
                mistagCalibBbar.append(MistagCalibration("mistagCalib_Bbar_"+tag, "mistagCalib_Bbar_"+tag, tagOmegaComb, p0Bbar[i], p1Bbar[i], avBbar[i]))
                
                tagOmegaList += [ [mistagCalibB[i],mistagCalibBbar[i]] ]
                
                print "==> p0_B_"+tag
                print "==> p1_B_"+tag
                print "==> av_B_"+tag
                print "==> p0_Bbar_"+tag
                print "==> p1_Bbar_"+tag
                print "==> av_Bbar_"+tag
                
                i = i+1

    print '==> Tagging calibration lists:'
    print tagOmegaList
                
    # Get the different mistag PDFs
    print "==> Mistag distributions from workspace"
    if notagging:
        mistagBdPDFList = None
        mistagBsPDFList = None
        mistagCombPDFList = None
    else:
        for i in range(0,3):
            namePDF = TString("sigMistagPdf_")+TString(str(i+1))
            printifdebug(debug,"Getting the mistag PDFs for "+str(namePDF))
            mistagBs.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workMistag, namePDF, debug))
            mistagBs[i].SetName("sigMistagPdf_BsDsK_"+str(i))
            mistagBd.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workMistagBDPi, namePDF, debug))
            mistagBd[i].SetName("sigMistagPdf_Bd2DPi_"+str(i))
            mistagComb.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workMistagComb, namePDF, debug))
            mistagComb[i].SetName("sigMistagPdf_CombBkg_"+str(i))
            if not singletagger:
                mistagBdPDFList.append(mistagBd[i])
                mistagBsPDFList.append(mistagBs[i])
                mistagCombPDFList.append(mistagComb[i])

        if singletagger:
            mistagBsPDFList.append(mistagBs[0])
            mistagCombPDFList.append(mistagComb[0])
            mistagBdPDFList.append(mistagBd[0])

            print "==> List of mistag PDFs:"
            print mistagBsPDFList
            print mistagCombPDFList
            print mistagBdPDFList
    
    # Now the names of the D modes
    nameD = []
    for cm in myconfigfile["CharmModes"]:
        nameD.append(cm)

    #----------------------------------------------------------------------------------------------------------------#
    # Build time and mass models for generation. The generation is made separately for the two final states          #
    #----------------------------------------------------------------------------------------------------------------#
    
    #PDFs container
    TOTPDFs = {}
    TOTPDFs["plus"] = []
    TOTPDFs["minus"] = []

    #Yields and pdfs
    timeandmass_Signal           = {}
    timeandmass_Signal["plus"]   = []
    timeandmass_Signal["minus"]  = []
    num_Signal                   = {}
    num_Signal["plus"]           = []
    num_Signal["minus"]           = []
    massB_Signal              = {}
    massB_Signal["plus"]      = []
    massB_Signal["minus"]      = []
    massD_Signal              = {}
    massD_Signal["plus"]      = []
    massD_Signal["minus"]      = []
    MDFitter_Signal              = {}
    MDFitter_Signal["plus"]      = []
    MDFitter_Signal["minus"]      = []

    timeandmass_Bd2DK            = {}
    timeandmass_Bd2DK["plus"]   = []
    timeandmass_Bd2DK["minus"]  = []
    num_Bd2DK                   = {}
    num_Bd2DK["plus"]           = []
    num_Bd2DK["minus"]           = []
    massB_Bd2DK                = []
    massD_Bd2DK                = []
    
    timeandmass_Bs2DsPi          = {}
    timeandmass_Bs2DsPi["plus"]   = []
    timeandmass_Bs2DsPi["minus"]  = []
    num_Bs2DsPi                   = {}
    num_Bs2DsPi["plus"]           = []
    num_Bs2DsPi["minus"]           = []
    massB_Bs2DsPi               = []
    massD_Bs2DsPi               = []
    MDFitter_Bs2DsPi            = []
    
    timeandmass_Bd2DRho          = {}
    timeandmass_Bd2DRho["plus"]   = []
    timeandmass_Bd2DRho["minus"]  = []
    num_Bd2DRho                   = {}
    num_Bd2DRho["plus"]           = []
    num_Bd2DRho["minus"]           = []
    massD_Bd2DRho               = {}
    massD_Bd2DRho["plus"]       = []
    massD_Bd2DRho["minus"]      = []
    MDFitter_Bd2DRho            = {}
    MDFitter_Bd2DRho["plus"]    = [] 
    MDFitter_Bd2DRho["minus"]    = []
    
    timeandmass_Bd2DstPi         = {}
    timeandmass_Bd2DstPi["plus"]   = []
    timeandmass_Bd2DstPi["minus"]  = []
    num_Bd2DstPi                   = {}
    num_Bd2DstPi["plus"]           = []
    num_Bd2DstPi["minus"]           = []
    massB_Bd2DstPi              = []
    massD_Bd2DstPi              = []
    MDFitter_Bd2DstPi           = []
    
    timeandmass_Lb2LcPi          = {}
    timeandmass_Lb2LcPi["plus"]   = []
    timeandmass_Lb2LcPi["minus"]  = []
    num_Lb2LcPi                   = {}
    num_Lb2LcPi["plus"]           = []
    num_Lb2LcPi["minus"]           = []
    
    timeandmass_Combo            = {}
    timeandmass_Combo["plus"]   = []
    timeandmass_Combo["minus"]  = []
    num_Combo                   = {}
    num_Combo["plus"]           = []
    num_Combo["minus"]           = []
    massB_Combo                 = []
    massD_Combo                  = {}
    massD_Combo["plus"]          = []
    massD_Combo["minus"]          = []
    MDFitter_Combo               = {}
    MDFitter_Combo["plus"]       = []
    MDFitter_Combo["minus"]      = []

    #PDF shape parameters
    meanVarB                    = []
    sigma1VarB                  = []
    sigma2VarB                  = []
    alpha1VarB                  = []
    alpha2VarB                  = []
    n1VarB                      = []
    n2VarB                      = []
    fracVarB                    = []

    meanVarD                    = []
    sigma1VarD                  = []
    sigma2VarD                  = []
    alpha1VarD                  = []
    alpha2VarD                  = []
    n1VarD                      = []
    n2VarD                      = []
    fracVarD                    = []

    cBVar                       = []
    massB_Combo                 = []
    cDVar                       = []
    fracDComb                   = []

    #Other utilities
    plusCat = WS(ws,RooCategory("qf_plus","+1 category"))
    plusCat.defineType('h+', +1)
    minusCat = WS(ws,RooCategory("qf_minus","-1 category"))
    minusCat.defineType('h-', -1)

    adetPlus = WS(ws,RooConstVar("adet_plus","+1",1.0))
    adetMinus = WS(ws,RooConstVar("adet_minus","-1",-1.0))
    
    finalList = [ [adetPlus,plusCat,1,"plus"], [adetMinus,minusCat,-1,"minus"] ]

    compNameList = []
    compNameList = ["Signal", "Bd2DK", "Bs2DsPi", "Lb2LcPi", "Combo", "Bd2DstPi", "Bd2DRho"]
    GammaList = [Gammad, Gammad, Gammas, GammaLb, GammaCombo, Gammad, Gammad]
    DeltaGammaList = [DeltaGammad, DeltaGammad, DeltaGammas, zero, DeltaGammaCombo, DeltaGammad, DeltaGammad]
    DeltaMList = [DeltaMd, DeltaMd, DeltaMs, zero, zero, DeltaMd, DeltaMd]

    timeerrList = {}
    timeerrList["plus"] = {}
    timeerrList["minus"] = {}
    
    mistagList = {}
    mistagList["plus"] = {}
    mistagList["minus"] = {}

    #Correct yields for detection asymmetry
    yieldsList = {}
    Nplus = 0
    Nminus = 0
    for comp in compNameList:
        for nm in nameD:
            yieldsList[comp]={}
            yieldsList[comp][year]={}
            yieldsList[comp][year][nm] = {}
            if comp == "Signal":
                if nodetasymmetry:
                    yieldsList[comp][year][nm]["plus"] = myconfigfile["Yields"][comp][year][nm]/2.0
                    yieldsList[comp][year][nm]["minus"] = myconfigfile["Yields"][comp][year][nm]/2.0
                else:
                    yieldsList[comp][year][nm]["plus"] = (myconfigfile["Yields"][comp][year][nm]/2.0)*(1+myconfigfile["ADet"][comp])
                    yieldsList[comp][year][nm]["minus"] = (myconfigfile["Yields"][comp][year][nm]/2.0)*(1-myconfigfile["ADet"][comp])
            else:
                if nobackground:
                    yieldsList[comp][year][nm]["plus"] = 0.0
                    yieldsList[comp][year][nm]["minus"] = 0.0
                else:
                    if nodetasymmetry:
                        yieldsList[comp][year][nm]["plus"] = myconfigfile["Yields"][comp][year][nm]/2.0
                        yieldsList[comp][year][nm]["minus"] = myconfigfile["Yields"][comp][year][nm]/2.0
                    else:
                        yieldsList[comp][year][nm]["plus"] = (myconfigfile["Yields"][comp][year][nm]/2.0)*(1+myconfigfile["ADet"][comp])
                        yieldsList[comp][year][nm]["minus"] = (myconfigfile["Yields"][comp][year][nm]/2.0)*(1-myconfigfile["ADet"][comp])

            Nplus = Nplus + yieldsList[comp][year][nm]["plus"]
            Nminus = Nminus + yieldsList[comp][year][nm]["minus"]

    print "Number of D-pi+ to generate: " + str(int(round(Nplus)))
    print "Number of D+pi- to generate: " + str(int(round(Nminus)))
    print "Sum of the modes: " + str(Nplus+Nminus)

    #Create time pdfs (dependent on pion charge)  
    for final in finalList:

        print "==> Final state:"
        print final

        i=0 #index associated to comp
        for comp in compNameList:
        
            #Time error pdf
            if not noresolution and not meanresolution:
                print "==> Creating time error PDF for " + str(comp)
            
                if comp == "Signal":
                    terrtemp = WS(workspace,Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsK"), debug))
                elif comp == "Combo":
                    terrtemp = WS(workspace,Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_CombBkg"), debug))
                elif comp == "Bd2DstPi":
                    terrtemp = WS(workspace,Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bd2DPi"), debug))
                elif comp == "Bd2DRho":
                    terrtemp = WS(workspace,Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsRho"), debug))
                else:
                    terrtemp = WS(workspace,Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_"+str(comp)), debug))
                    
                terrtemp.SetNameTitle("TimeErrorPdf_"+str(comp),"TimeErrorPdf_"+str(comp))
        
                #Workaround to cheat RooFit strict requirements (changing dependent RooRealVar)
                lab0_LifetimeFit_ctauErr = RooRealVar("lab0_LifetimeFit_ctauErr",
                                                      "lab0_LifetimeFit_ctauErr",
                                                      myconfigfile["BasicVariables"]["BeautyTimeErr"]["Range"][0],
                                                      myconfigfile["BasicVariables"]["BeautyTimeErr"]["Range"][1])
                terrHist = terrtemp.createHistogram("terrHist_"+comp,lab0_LifetimeFit_ctauErr)
                terrDataHist = RooDataHist("terrHist_"+comp,"terrHist_"+comp,RooArgList(terrVar_B),terrHist)
                terr = WS(ws,RooHistPdf(terrtemp.GetName(),terrtemp.GetTitle(),RooArgSet(terrVar_B),terrDataHist))
                
                print terr
                
            else:
                terr = None

            #Utilities
            utils = GenTimePdfUtils(myconfigfile,
                                    ws,
                                    comp,
                                    GammaList[i],
                                    DeltaGammaList[i],
                                    DeltaMList[i],
                                    singletagger,
                                    notagging,
                                    noprodasymmetry,
                                    notagasymmetries,
                                    debug)

            #Hack to avoid conflicts in the ws workspace
            if comp == "Signal" or comp == "Bs2DsPi":
                mistagList[final[3]] = copy.deepcopy(mistagBsPDFList)
            else:
                mistagList[final[3]] = copy.deepcopy(mistagBdPDFList)

            if not notagging:
                for item in mistagList[final[3]]:
                    item.SetNameTitle(item.GetName()+"_"+comp, item.GetTitle()+"_"+comp)

            #Total time pdf
            timeerrList[final[3]][comp] = buildBDecayTimePdf(myconfigfile,
                                                             comp+"_"+str(final[3]),
                                                             ws,
                                                             timeVar_B, terrVar_B, tagDecComb,
                                                             final[1], #qf: only +1 or -1 final state
                                                             tagOmegaList,
                                                             utils['tagEff'],
                                                             GammaList[i],
                                                             DeltaGammaList[i],
                                                             DeltaMList[i],
                                                             utils['C'],
                                                             utils['D'],
                                                             utils['Dbar'],
                                                             utils['S'],
                                                             utils['Sbar'],
                                                             trm,
                                                             tacc,
                                                             terr,
                                                             mistagList[final[3]],
                                                             tagOmegaComb,
                                                             None,
                                                             None,
                                                             utils['aProd'],
                                                             final[0], #aDet: only +1 or -1 final state
                                                             utils['aTagEff'])
        
            i = i+1
        #end loop on components
        
    #end loop on final states
    print "Time pdfs list:"
    print timeerrList

    #Create all the things independent of the pion charge (mass pdf etc...)

    #----------------------------------------------- Bd -> DK mass PDF --------------------------------------------------#
    # Notice that here we build a single MDFitter_Bd2DK model upfront
    print "==> Creating MD PDF for Bd2DK"
    MDFitter_Bd2DK = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, TString("Bd2DK"), magpol, yearTS, lumRatio, NULL, dim, debug)
    
    #------------------------------------------------- Lb -> LcPi Mass PDF----------------------------------------------------#
    # Build a single MDFitter instance upfront
    print "==> Creating MD PDF for Lb2LcPi"
    MDFitter_Lb2LcPi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, TString("Lb2LcPi"), magpol, yearTS, lumRatio, NULL, dim, debug)
    
    #--------------------------------------------- Bd->DRho Mass PDF -----------------------------------------------#
    # Here we build the B upfront, will build the D later by mode
    print "==> Creating B mass PDF for Bd2DRho"
    massB_Bd2DRho = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bd2DRho"), yearTS, False, lumRatio, debug)

    
    i=0 #index associated to nm
    for nm in nameD:
        print "===> Creating Signal Total PDF"
        
        #The signal - mass
        meanVarB.append(WS(ws, RooRealVar(   "DblCBBPDF_%s_mean_%s"%(massVar_B.GetName(),nm) ,  "mean",    myconfigfile["BsSignalShape"]["mean"]["All"]    )))
        sigma1VarB.append(WS(ws, RooRealVar( "DblCBBPDF_%s_sigma1_%s"%(massVar_B.GetName(),nm), "sigma1",  myconfigfile["BsSignalShape"]["sigma1"][year][nm]  )))
        sigma2VarB.append(WS(ws, RooRealVar( "DblCBBPDF_%s_sigma2_%s"%(massVar_B.GetName(),nm), "sigma2",  myconfigfile["BsSignalShape"]["sigma2"][year][nm]  )))
        alpha1VarB.append(WS(ws, RooRealVar( "DblCBBPDF_%s_alpha1_%s"%(massVar_B.GetName(),nm), "alpha1",  myconfigfile["BsSignalShape"]["alpha1"][year][nm]  )))
        alpha2VarB.append(WS(ws, RooRealVar( "DblCBBPDF_%s_alpha2_%s"%(massVar_B.GetName(),nm), "alpha2",  myconfigfile["BsSignalShape"]["alpha2"][year][nm]  )))
        n1VarB.append(WS(ws, RooRealVar(     "DblCBBPDF_%s_n1_%s"%(massVar_B.GetName(),nm),     "n1",      myconfigfile["BsSignalShape"]["n1"][year][nm]      )))
        n2VarB.append(WS(ws, RooRealVar(     "DblCBBPDF_%s_n2_%s"%(massVar_B.GetName(),nm),     "n2",      myconfigfile["BsSignalShape"]["n2"][year][nm]      )))
        fracVarB.append(WS(ws, RooRealVar(   "DblCBBPDF_%s_frac_%s"%(massVar_B.GetName(),nm),   "frac",    myconfigfile["BsSignalShape"]["frac"][year][nm]    )))
        
        #The signal - mass D
        meanVarD.append(WS(ws, RooRealVar(   "DblCBDPDF_%s_mean_%s"%(massVar_D.GetName(),nm) ,  "mean",    myconfigfile["DsSignalShape"]["mean"]["All"]    )))
        sigma1VarD.append(WS(ws, RooRealVar( "DblCBDPDF_%s_sigma1_%s"%(massVar_D.GetName(),nm), "sigma1",  myconfigfile["DsSignalShape"]["sigma1"][year][nm]  )))
        sigma2VarD.append(WS(ws, RooRealVar( "DblCBDPDF_%s_sigma2_%s"%(massVar_D.GetName(),nm), "sigma2",  myconfigfile["DsSignalShape"]["sigma2"][year][nm]  )))
        alpha1VarD.append(WS(ws, RooRealVar( "DblCBDPDF_%s_alpha1_%s"%(massVar_D.GetName(),nm), "alpha1",  myconfigfile["DsSignalShape"]["alpha1"][year][nm]  )))
        alpha2VarD.append(WS(ws, RooRealVar( "DblCBDPDF_%s_alpha2_%s"%(massVar_D.GetName(),nm), "alpha2",  myconfigfile["DsSignalShape"]["alpha2"][year][nm]  )))
        n1VarD.append(WS(ws, RooRealVar(     "DblCBDPDF_%s_n1_%s"%(massVar_D.GetName(),nm),     "n1",      myconfigfile["DsSignalShape"]["n1"][year][nm]      )))
        n2VarD.append(WS(ws, RooRealVar(     "DblCBDPDF_%s_n2_%s"%(massVar_D.GetName(),nm),     "n2",      myconfigfile["DsSignalShape"]["n2"][year][nm]      )))
        fracVarD.append(WS(ws, RooRealVar(   "DblCBDPDF_%s_frac_%s"%(massVar_D.GetName(),nm),   "frac",    myconfigfile["DsSignalShape"]["frac"][year][nm]    )))

        #------------------------------------------------- Bs -> DsPi ----------------------------------------------------# 
        print "===> Creating Bs->DsPi Total PDF"
        
        #The Bs->DsPi - mass B (add + nameD[i] to TString("Bs2DsPi") to select a mode (not needed for B->Dpi analysis))
        massB_Bs2DsPi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bs2DsPi"), yearTS, False, lumRatio, debug))
        #The Bs->DsPi - mass D (add + nameD[i] to TString("Bs2DsPi") to select a mode (not needed for B->Dpi analysis))
        massD_Bs2DsPi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bs2DsPi"), yearTS, True, lumRatio, debug))
        #The Bs->DsPi - MDFitter
        MDFitter_Bs2DsPi.append(RooProdPdf("MDFitter_Bs2DsPi_%s"%(nm),"MDFitter_Bs2DsPi",RooArgList(massB_Bs2DsPi[i], massD_Bs2DsPi[i])))
                                                                                                                 
        #------------------------------------------------- Combinatorial ----------------------------------------------------#
        #The combinatorics - mass B
        cBVar.append(RooRealVar("CombBkg_%s_cB_%s"%(massVar_B.GetName(), nm),"CombBkg_slope_B", myconfigfile["BsCombinatorialShape"]["cB"][year][nm]))
        massB_Combo.append(RooExponential("massB_Combo_%s","massB_Combo",massVar_B, cBVar[i]))
        #The combinatorics - mass D
        cDVar.append(WS(ws,RooRealVar("CombBkg_%s_cD_%s"%(massVar_D.GetName(), nm),"CombBkg_slope_D", myconfigfile["DsCombinatorialShape"]["cD"][year][nm])))
        fracDComb.append(WS(ws,RooRealVar("CombBkg_%s_fracD_%s"%(massVar_D.GetName(), nm), "CombBkg_fracDComb",  myconfigfile["DsCombinatorialShape"]["fracCombD"][year][nm])))
            
        #------------------------------------------------- D*Pi ----------------------------------------------------#
        #The low mass - mass B
        massB_Bd2DstPi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bd2DstPi"), yearTS, False, lumRatio, debug))
        #The low mass - mass D
        massD_Bd2DstPi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bd2DstPi"), yearTS, True, lumRatio, debug))
        MDFitter_Bd2DstPi.append(RooProdPdf("MDFitter_Bd2DstPi_%s"%(nm),"MDFitter_Bd2DstPi",
                                            RooArgList(massB_Bd2DstPi[i], massD_Bd2DstPi[i])))
        
        
        i = i+1
        
    #Now create thing that depend on the pion charge and sum up all components
    for final in finalList:
        i=0 #index associated to nm
        for nm in nameD:

            #Signal
            print "===> Creating Signal Total PDF"
            num_Signal[final[3]].append(RooRealVar("num_Signal_%s_%s"%(nm,final[3]),"num_Signal_%s"%(nm), yieldsList["Signal"][year][nm][final[3]] )) #According to the det asymmetry
            printifdebug(debug,"Generating "+str( yieldsList["Signal"][year][nm][final[3]] )+" signal events")
            massB_Signal[final[3]].append(WS(ws,Bs2Dsh2011TDAnaModels.buildDoubleCrystalBallPDF(massVar_B,ws,nm,"DblCBBPDF",False,debug)))
            massD_Signal[final[3]].append(WS(ws,Bs2Dsh2011TDAnaModels.buildDoubleCrystalBallPDF(massVar_D,ws,nm,"DblCBDPDF",False,debug)))
            MDFitter_Signal[final[3]].append(RooProdPdf("MDFitter_Signal_%s_%s"%(nm,final[3]),"MDFitter_Signal",
                                              RooArgList(massB_Signal[final[3]][i], massD_Signal[final[3]][i])))
            timeandmass_Signal[final[3]].append(RooProdPdf("timeandmass_Signal_%s_%s"%(nm,final[3]),"timeandmass_Signal",
                                                           RooArgList(timeerrList[final[3]]["Signal"],
                                                                      MDFitter_Signal[final[3]][i])))

            #Bd -> DK
            print "===> Creating Bd->DK Total PDF"
            num_Bd2DK[final[3]].append(RooRealVar("num_Bd2DK_%s_%s"%(nm,final[3]),"num_Bd2DK",yieldsList["Bd2DK"][year][nm][final[3]] ))
            printifdebug(debug,"Generating "+str(yieldsList["Bd2DK"][year][nm][final[3]] )+" DK events")
            #
            timeandmass_Bd2DK[final[3]].append(RooProdPdf("timeandmass_Bd2DK_%s_%s"%(nm,final[3]),"timeandmass_Bd2DK",RooArgList(timeerrList[final[3]]["Bd2DK"],
                                                                                                                     MDFitter_Bd2DK)))
            #Bs -> DsPi
            print "===> Creating Bs->DsPi Total PDF"
            num_Bs2DsPi[final[3]].append(RooRealVar("num_Bs2DsPi_%s_%s"%(nm,final[3]),"num_Bs2DsPi", yieldsList["Bs2DsPi"][year][nm][final[3]] ))
            printifdebug(debug,"Generating "+str(yieldsList["Bs2DsPi"][year][nm][final[3]] )+" DsPi events")
            #
            timeandmass_Bs2DsPi[final[3]].append(RooProdPdf("timeandmass_Bs2DsPi_%s_%s"%(nm,final[3]),"timeandmass_Bs2DsPi",RooArgList(timeerrList[final[3]]["Bs2DsPi"],
                                                                                                                           MDFitter_Bs2DsPi[i])))
            #Lb -> LcPi
            print "===> Creating Lb->LcPi Total PDF"
            num_Lb2LcPi[final[3]].append(RooRealVar("num_Lb2LcPi_%s_%s"%(nm,final[3]),"num_Lb2LcPi", yieldsList["Lb2LcPi"][year][nm][final[3]] ))
            printifdebug(debug,"Generating "+str(yieldsList["Lb2LcPi"][year][nm][final[3]] )+" LcPi events")
            #
            timeandmass_Lb2LcPi[final[3]].append(RooProdPdf("timeandmass_Lb2LcPi_%s_%s"%(nm,final[3]),"timeandmass_Lb2LcPi",RooArgList(timeerrList[final[3]]["Lb2LcPi"],
                                                                                                                           MDFitter_Lb2LcPi)))
            #Combinatorial
            print "===> Creating Combinatorial Total PDF"
            massD_Combo[final[3]].append(Bs2Dsh2011TDAnaModels.buildExponentialPlusSignalPDF(massVar_D, ws, nm, "CombBkg"))
            MDFitter_Combo[final[3]].append(RooProdPdf("MDFitter_Combo_%s_%s"%(nm,final[3]),"MDFitter_Combo",RooArgList(massB_Combo[i], massD_Combo[final[3]][i])))
            num_Combo[final[3]].append(RooRealVar("num_Combo_%s_%s"%(nm,final[3]),"num_Combo", yieldsList["Combo"][year][nm][final[3]]))
            printifdebug(debug,"Generating "+str(yieldsList["Combo"][year][nm][final[3]] )+" combo events")
            timeandmass_Combo[final[3]].append(RooProdPdf("timeandmass_Combo_%s_%s"%(nm,final[3]),"timeandmass_Combo",RooArgList(timeerrList[final[3]]["Combo"],
                                                                                                                     MDFitter_Combo[final[3]][i])))
            #B -> D*Pi
            print "===> Creating Bd->D*Pi Total PDF"
            num_Bd2DstPi[final[3]].append(RooRealVar("num_Bd2DstPi_%s_%s"%(nm,final[3]),"num_Bd2DstPi", yieldsList["Bd2DstPi"][year][nm][final[3]] ))
            printifdebug(debug,"Generating "+str(yieldsList["Bd2DstPi"][year][nm][final[3]] )+" D*Pi events")
            timeandmass_Bd2DstPi[final[3]].append(RooProdPdf("timeandmass_Bd2DstPi_%s_%s"%(nm,final[3]),"timeandmass_Bd2DstPi",RooArgList(timeerrList[final[3]]["Bd2DstPi"],
                                                                                                                              MDFitter_Bd2DstPi[i])))
            #B -> DRho
            print "===> Creating Bd->DRho Total PDF"
            massD_Bd2DRho[final[3]].append(massD_Signal[final[3]][i])
            MDFitter_Bd2DRho[final[3]].append(RooProdPdf("MDFitter_Bd2DRho_%s_%s"%(nm,final[3]),"MDFitter_Bd2DRho",
                                               RooArgList(massB_Bd2DRho, massD_Bd2DRho[final[3]][i])))
            num_Bd2DRho[final[3]].append(RooRealVar("num_Bd2DRho_%s_%s"%(nm,final[3]),"num_Bd2DRho", yieldsList["Bd2DRho"][year][nm][final[3]] ))
            printifdebug(debug,"Generating "+str(yieldsList["Bd2DRho"][year][nm][final[3]] )+" DRho events")
            timeandmass_Bd2DRho[final[3]].append(RooProdPdf("timeandmass_Bd2DRho_%s_%s"%(nm,final[3]),"timeandmass_Bd2DRho",RooArgList(timeerrList[final[3]]["Bd2DRho"],
                                                                                                                           MDFitter_Bd2DRho[final[3]][i])))
            
            #------------------------------------------------- Total pdf ----------------------------------------------------#
            print "===> Adding up all components:"

            #Total
            pdfList = RooArgList(timeandmass_Signal[final[3]][i])
            pdfList.add(timeandmass_Bd2DK[final[3]][i])
            pdfList.add(timeandmass_Bs2DsPi[final[3]][i])
            pdfList.add(timeandmass_Lb2LcPi[final[3]][i])
            pdfList.add(timeandmass_Combo[final[3]][i])
            pdfList.add(timeandmass_Bd2DstPi[final[3]][i])
            pdfList.add(timeandmass_Bd2DRho[final[3]][i])
            #
            numList = RooArgList(num_Signal[final[3]][i])
            numList.add(num_Bd2DK[final[3]][i])
            numList.add(num_Bs2DsPi[final[3]][i])
            numList.add(num_Lb2LcPi[final[3]][i])
            numList.add(num_Combo[final[3]][i])
            numList.add(num_Bd2DstPi[final[3]][i])
            numList.add(num_Bd2DRho[final[3]][i])
            #

            print "==> List of pdfs:"
            for pdf in range(0,pdfList.getSize()):
                print "%s"%(pdfList[pdf].GetName())
            print "==> List of yields:"
            for num in range(0,numList.getSize()):
                print "%s"%(numList[num].getVal())

            TOTPDFs[final[3]].append(RooAddPdf("total_pdf_%s_%s"%(nm, final[3]),"total_pdf_%s_%s"%(nm, final[3]), pdfList, numList))
           
            i = i+1

            #End loop on final
    
    for i in range(rangeDown,rangeUp) :

        workout = RooWorkspace(workName,workName)
        j=0 #index corresponding to nm in nameD
        for nm in nameD:
            print "===> Generating toys"
            genArgSet = RooArgSet(massVar_B, massVar_D, timeVar_B, tagDecComb)
            if notagging:
                tagOmegaComb.setVal(0.0)
                tagOmegaComb.setConstant(True)
            else:
                genArgSet.add(tagOmegaComb)
                
            if noresolution or meanresolution:
                terrVar_B.setMin(0.0)
                terrVar_B.setVal(0.0)
                terrVar_B.setConstant(True)
            else:
                genArgSet.add(terrVar_B)

            sw = TStopwatch()
            sw.Start()

            if Nplus>0:
                print "Start generating %d D-pi+ events..."%(Nplus)
                print "PDF: %s"%(TOTPDFs["plus"][j].GetName())
                idVar_B.setIndex(1)
                TOTPDFs["plus"][j].Print("v")
                gendataPlus = TOTPDFs["plus"][j].generate(genArgSet,
                                                          RooFit.Extended(),
                                                          RooFit.NumEvents(int(round(Nplus))))
                gendataPlus.addColumn(idVar_B)

                #frameplus = timeVar_B.frame()
                #gendataPlus.plotOn(frameplus)
                #cplus = TCanvas("cplus")
                #frameplus.Draw()
                #cplus.SaveAs("testPlus.eps")
                
                print "D-pi+ dataset:"
                gendataPlus.Print("v")
                print "...entries: "+str(gendataPlus.sumEntries())
                if notagging:
                    # Since p0=p1=<eta>=0, the calibrated mistag is always zero.
                    # We replace the eta distribution in the output workspace
                    # with a column filled with zeroes
                    gendataPlus.addColumn(tagOmegaComb)
                if noresolution or meanresolution:
                    gendataPlus.addColumn(terrVar_B)
                
            if Nminus>0:
                print "Start generating %d D+pi- events..."%(Nminus)
                print "PDF: %s"%(TOTPDFs["minus"][j].GetName())
                idVar_B.setIndex(-1)
                TOTPDFs["minus"][j].Print("v")
                gendataMinus = TOTPDFs["minus"][j].generate(genArgSet,
                                                            RooFit.Extended(),
                                                            RooFit.NumEvents(int(round(Nminus))))
                gendataMinus.addColumn(idVar_B)

                #frameminus = timeVar_B.frame()
                #gendataMinus.plotOn(frameminus)
                #cminus = TCanvas("cminus")
                #frameminus.Draw()
                #cminus.SaveAs("testMinus.eps")

                print "D+pi- dataset:"
                gendataMinus.Print("v")
                print "...entries: "+str(gendataMinus.sumEntries())
                if notagging:
                    # Since p0=p1=<eta>=0, the calibrated mistag is always zero.
                    # We replace the eta distribution in the output workspace
                    # with a column filled with zeroes
                    gendataMinus.addColumn(tagOmegaComb)
                if noresolution or meanresolution:
                    gendataMinus.addColumn(terrVar_B)

            genArgSet.add(idVar_B)
            if Nplus==0 and Nminus>0:
                gendataMinus.SetName("dataSetBdDPi_both_"+str(nm))
                gendataMinus.SetTitle("dataSetBdDPi_both_"+str(nm))
                gendata = copy.deepcopy(gendataMinus)
            elif Nplus>0 and Nminus==0:
                gendataPlus.SetName("dataSetBdDPi_both_"+str(nm))
                gendataPlus.SetTitle("dataSetBdDPi_both_"+str(nm))
                gendata = copy.deepcopy(gendataPlus)
            elif Nplus>0 and Nminus>0:
                gendata = RooDataSet("dataSetBdDPi_both_"+str(nm),
                                     "dataSetBdDPi_both_"+str(nm),
                                     genArgSet,
                                     RooFit.Index(idVar_B),
                                     RooFit.Import("h+",gendataPlus),
                                     RooFit.Import("h-",gendataMinus))
            else:
                print "ERROR: zero entries produced! Please check your options."
                exit(-1)
            
            sw.Stop()
            sw.Print()

            print "Sum of datasets:"
            print "...entries: "+str(gendata.sumEntries())

            gendata.SetName("dataSetBdDPi_both_"+str(nm))
            gendata.SetTitle("dataSetBdDPi_both_"+str(nm))
            if debug : gendata.Print("v")
            tree = gendata.store().tree()
            tree.SetName("dataSetBdDPi_both_"+str(nm))
            tree.SetTitle("dataSetBdDPi_both_"+str(nm))
            if single :
                dataName = TString("dataSetBdDPi_both_")+TString(nm)
                print "Copying data for toys"
                data.append(SFitUtils.CopyDataForToys(tree,
                                                      TString(mVar),
                                                      TString(mdVar),
                                                      TString(""),
                                                      TString(tVar),
                                                      TString(terrVar),
                                                      TString("tagDecComb")+TString("_idx"),
                                                      TString("tagOmegaComb"),
                                                      TString(charge)+TString("_idx"),
                                                      TString(""),
                                                      dataName,
                                                      debug))
            if savetree :
                print "Saving Tree"
                outfile  = TFile(dir+fileNamePrefix+"Tree_"+str(nm)+"_"+str(i)+".root","RECREATE")
                tree.Write()
                outfile.Close()
                del tree
            print "Importing all in the workspace"
            getattr(workout,'import')(gendata)
            del gendata

            j=j+1
        
        print "Save the workspace"
        workout.writeToFile(dir+fileNamePrefix+"Work_"+str(i)+".root")
        workout.Print("v")
        
        del workout
    
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--single',
                   dest = 'single',
                   action = 'store_true',
                   default = False,
                                      )
parser.add_option( '-s','--start',
                   dest = 'rangeDown',
                   default = 0)

parser.add_option( '-e','--end',
                   dest = 'rangeUp',
                   default = 1)

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'B2DPiConfigForGenerator5M')

parser.add_option( '-y','--year',
                   dest = 'year',
                   default = '2012')

parser.add_option( '--seed',
                   dest = 'seed',
                   default = 746829245)

parser.add_option( '--savetree',
                   dest = 'savetree',
                   action = 'store_true',
                   default = False,
                   help = 'Save an ntuple as well as a workspace')

parser.add_option( '--noresolution',
                   dest = 'noresolution',
                   action = 'store_true',
                   default = False,
                   help = 'Generate with perfect resolution')

parser.add_option( '--noacceptance',
                   dest = 'noacceptance',
                   action = 'store_true',
                   default = False,
                   help = 'Generate with perfect acceptance')

parser.add_option( '--notagging',
                   dest = 'notagging',
                   action = 'store_true',
                   default = False,
                   help = 'Generate with calibrated mistag always equal to zero')

parser.add_option( '--noprodasymmetry',
                   dest = 'noprodasymmetry',
                   action = 'store_true',
                   default = False,
                   help = 'Generate without production asymmetries')

parser.add_option( '--nodetasymmetry',
                   dest = 'nodetasymmetry',
                   action = 'store_true',
                   default = False,
                   help = 'Generate without detection asymmetries')

parser.add_option( '--notagasymmetries',
                   dest = 'notagasymmetries',
                   action = 'store_true',
                   default = False,
                   help = 'Generate without tagging efficiency asymmetries')

parser.add_option( '--nobackground',
                   dest = 'nobackground',
                   action = 'store_true',
                   default = False,
                   help = 'Generate without background components')

parser.add_option( '--singletagger',
                   dest = 'singletagger',
                   action = 'store_true',
                   default = False,
                   help = 'Generate with a single tagger')

parser.add_option( '--singlecalibration',
                   dest = 'singlecalibration',
                   action = 'store_true',
                   default = False,
                   help = 'Use the same FT calibration for B0 and B0bar')

parser.add_option( '--meanresolution',
                   dest = 'meanresolution',
                   action = 'store_true',
                   default = False,
                   help = 'Generate with a mean resolution model')

parser.add_option( '--dir',
                   dest = 'dir',
                   default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/For1fbPaper/Gamma70_5M_2T_MD/')

# -----------------------------------------------------------------------------
if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    import sys
    sys.path.append("../data/Bd2DPi_3fbCPV/Bd2DPi/")
    
    runBDPiGenerator( options.debug,  options.single , options.configName, options.year,
                      int(options.rangeDown), int(options.rangeUp), 
                      options.seed, options.dir, options.savetree,
                      options.noresolution, options.noacceptance,
                      options.notagging, options.noprodasymmetry,
                      options.nodetasymmetry, options.notagasymmetries,
                      options.nobackground, options.singletagger,
                      options.meanresolution, options.singlecalibration)
    
# -----------------------------------------------------------------------------
                                
