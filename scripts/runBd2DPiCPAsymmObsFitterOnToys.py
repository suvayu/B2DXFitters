#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC fit for the CP asymmetry observables        #
#   in Bd -> DPi                                                              #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBd2DPiCPAsymmObsFitterOnToys.py [-d -s ]                     #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#   Author: Manuel Schiller                                                   #
#   Author: Agnieszka Dziurda                                                 #
#   Author: Vladimir Vava Gligorov                                            #
#   Author: Vincenzo Battista                                                 #
#                                                                             #
# --------------------------------------------------------------------------- #
# This file is used as both a shell script and as a Python script.

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
from  os.path import exists
from array import array
import os, sys, gc
import numpy

from B2DXFitters import taggingutils, cpobservables
from B2DXFitters.timepdfutils import buildBDecayTimePdf
from B2DXFitters.resmodelutils import getResolutionModel
from B2DXFitters.acceptanceutils import buildSplineAcceptance

gROOT.SetBatch()

from B2DXFitters import taggingutils, cpobservables
RooAbsData.setDefaultStorageType(RooAbsData.Tree)
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# BLINDING
Blinding =  False

param_limits = {"lower" : -4., "upper" : 4.}

# DATA FILES
saveName      = 'work_'

# MISCELLANEOUS
bName = 'B_{d}'

# INTERNAL WORKSPACE
from B2DXFitters.WS import WS as WS
ws = RooWorkspace("intWork","intWork")

#------------------------------------------------------------------------------
def printifdebug(debug,toprint) :
    if debug : print toprint

#------------------------------------------------------------------------------
'''
def setConstantIfSoConfigured(var,myconfigfile):
    if var.GetName() in myconfigfile["constParams"] :
        var.setConstant()
        if not var.isConstant():
            print '[ERROR] setConstantIfSoConfigured(): %s has not been fixed' % var.GetName()
            exit(-1)
        else:
            print '[INFO] setConstantIfSoConfigured(): %s fixed to %f' % (var.GetName(), var.getVal())
    else:
        print '[INFO] setConstantIfSoConfigured(): %s floating in the fit' % var.GetName()
'''
#------------------------------------------------------------------------------
def GenTimePdfUtils(configfile,
                    workspace,
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
    print " Utilities for building signal time PDF..."
    print "================================================================"
    print ""

    #CP observables
    print "=> Defining CP observables..."

    ACPobs = cpobservables.AsymmetryObservables(configfile["DecayRate"]["ArgLf_d"], configfile["DecayRate"]["ArgLbarfbar_d"], configfile["DecayRate"]["ModLf_d"])
    ACPobs.printtable()

    C     = WS(workspace,RooRealVar('C','C',ACPobs.Cf(),param_limits["lower"], param_limits["upper"]))
    S     = WS(workspace,RooRealVar('S','S',ACPobs.Sf(),param_limits["lower"], param_limits["upper"]))
    D     = WS(workspace,RooRealVar('D','D',ACPobs.Df(),param_limits["lower"], param_limits["upper"]))
    Sbar  = WS(workspace,RooRealVar('Sbar','Sbar',ACPobs.Sfbar(),param_limits["lower"], param_limits["upper"]))
    Dbar  = WS(workspace,RooRealVar('Dbar','Dbar',ACPobs.Dfbar(),param_limits["lower"], param_limits["upper"]))

    #C     = WS(workspace,RooRealVar('C','C',0.0))
    #S     = WS(workspace,RooRealVar('S','S',0.0))
    #D     = WS(workspace,RooRealVar('D','D',0.0))
    #Sbar  = WS(workspace,RooRealVar('Sbar','Sbar',0.0))
    #Dbar  = WS(workspace,RooRealVar('Dbar','Dbar',0.0))

    #setConstantIfSoConfigured(C,configfile)
    #setConstantIfSoConfigured(S,configfile)
    #setConstantIfSoConfigured(D,configfile)
    #setConstantIfSoConfigured(Sbar,configfile)
    #setConstantIfSoConfigured(Dbar,configfile)

    #Tagging efficiency
    print "=> Getting tagging efficiency..."
    tagEff = []
    tagEffList = []
    if notagging:
        print "=> Perfect tagging"
        if singletagger:
            print "=> Single tagger"
            tagEff.append(WS(workspace,RooRealVar('tagEff_'+str(1), 'Tagging efficiency', 1.0)))
            printifdebug(debug,tagEff[0].GetName()+": "+str(tagEff[0].getVal()) )
            tagEffList.append(tagEff[0])
        else:
            print "=> More taggers"
            for i in range(0,3):
                tagEff.append(WS(workspace,RooRealVar('tagEff_'+str(i+1), 'Tagging efficiency', 1.0)))
                printifdebug(debug,tagEff[i].GetName()+": "+str(tagEff[i].getVal()) )
                tagEffList.append(tagEff[i])
    else:
        print "=> Non-trivial tagging"
        if singletagger:
            print "=> Single tagger"
            tagEff.append(WS(workspace,RooRealVar('tagEff_'+str(1), 'Tagging efficiency', configfile["TagEff"]["Signal"][0])))
            printifdebug(debug,tagEff[0].GetName()+": "+str(tagEff[0].getVal()) )
            tagEffList.append(tagEff[0])
        else:
            print "=> More taggers"
            for i in range(0,3):
                tagEff.append(WS(workspace,RooRealVar('tagEff_'+str(i+1), 'Tagging efficiency', configfile["TagEff"]["Signal"][i])))
                printifdebug(debug,tagEff[i].GetName()+": "+str(tagEff[i].getVal()) )
                tagEffList.append(tagEff[i])

    #Asymmetries
    print "=> Getting production asymmetry..."
    if noprodasymmetry:
        print "=> No asymmetries"
        aProd = None
    else:
        print "=> Non-zero asymmetry"                        
        aProd   = WS(workspace,RooRealVar('aprod',   'aprod',   configfile["AProd"]["Signal"], -1.0, 1.0))
        #setConstantIfSoConfigured(aProd,configfile)
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
            aTagEff.append(WS(workspace,RooRealVar('aTagEff_'+str(1), 'atageff', configfile["ATagEff"]["Signal"][0])))
            printifdebug(debug,aTagEff[0].GetName()+": "+str(aTagEff[0].getVal()) )
            aTagEffList.append(aTagEff[0])
        else:
            for i in range(0,3):
                aTagEff.append(WS(workspace,RooRealVar('aTagEff_'+str(i+1), 'atageff', configfile["ATagEff"]["Signal"][i])))
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
def runBdGammaFitterOnToys(debug, wsname, 
                           pereventterr, year,
                           toys,pathName,
                           treeName, fileNamePull, configName, configNameMD,
                           sWeightsCorr,
                           noresolution, noacceptance, notagging,
                           noprodasymmetry, nodetasymmetry, notagasymmetries,
                           nosWeights, noUntagged,
                           singletagger) :
    
    if not Blinding and not toys :
        print "RUNNING UNBLINDED!"
        really = input('Do you really want to unblind? ')
        if really != "yes" :
            exit(-1)

    if sWeightsCorr and nosWeights:
        print "ERROR: cannot have sWeightsCorr and nosWeights at the same time!"
        exit(-1)

    if notagging and not singletagger:
        print "ERROR: having more perfect taggers is meaningless! Please check your options"
        exit(-1)
         
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

    if debug:
        myconfigfile['Debug'] = True
    else:
        myconfigfile['Debug'] = False

    #Choosing fitting context
    myconfigfile['Context'] = 'FIT'
 
    # tune integrator configuration
    print "---> Setting integrator configuration"
    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation','Wynn-Epsilon')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('maxSteps','1000')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('minSteps','0')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    # since we have finite ranges, the RooIntegrator1D is best suited to the job
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooIntegrator1D')

    # Reading data set
    #-----------------------

    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["LumRatio"][year])
    
    print "=========================================================="
    print "Getting configuration"
    print "=========================================================="

    config = TString("../data/")+TString(configName)+TString(".py")
    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings",False)
    
    MDSettings = mdt.getConfig()
    MDSettings.Print("v")

    bound = 1
    Bin = [TString("BDTGA")]

    from B2DXFitters.WS import WS as WS
    ws = RooWorkspace("intWork","intWork")

    workspace =[]
    workspaceW = []
    mode = "Bd2DPi"

    print "=========================================================="
    print "Getting sWeights"
    print "=========================================================="
    for i in range (0,bound):
        workspace.append(SFitUtils.ReadDataFromSWeights(TString(pathName),
                                                        TString(treeName),
                                                        MDSettings,
                                                        TString(mode),
                                                        TString(year),
                                                        TString(""),
                                                        TString("both"),
                                                        False, toys, False, sWeightsCorr, singletagger, debug))
        workspaceW.append(SFitUtils.ReadDataFromSWeights(TString(pathName),
                                                         TString(treeName),
                                                         MDSettings,
                                                         TString(mode),
                                                         TString(year),
                                                         TString(""),
                                                         TString("both"),
                                                         True, toys, False, sWeightsCorr, singletagger, debug))
    if nosWeights:
        workspace[0].Print("v")
    else:
        workspaceW[0].Print("v")
    zero = RooConstVar('zero', '0', 0.)
    half = RooConstVar('half','0.5',0.5)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)
      
    nameData = TString("dataSet_time_")+part 
    data  = [] 
    dataW = []

    print "=========================================================="
    print "Getting input dataset"
    print "=========================================================="
    for i in range(0, bound):
        data.append(GeneralUtils.GetDataSet(workspace[i],   nameData, debug))
        dataW.append(GeneralUtils.GetDataSet(workspaceW[i],   nameData, debug))

    dataWA = dataW[0]
    dataA = data[0]

    if nosWeights:
        nEntries = dataA.numEntries()
        dataA.Print("v")
    else:
        nEntries = dataWA.numEntries()    
        dataWA.Print("v")        

    print "=========================================================="
    print "Getting observables"
    print "=========================================================="
    if nosWeights:
        obs = dataA.get()
    else:
        obs = dataWA.get()
        
    obs.Print("v")

    print "=========================================================="
    print "Creating variables"
    print "=========================================================="
    time = WS(ws,obs.find(MDSettings.GetTimeVarOutName().Data()))
    time.setRange(myconfigfile["BasicVariables"]["BeautyTime"]["Range"][0],
                  myconfigfile["BasicVariables"]["BeautyTime"]["Range"][1])
    print "==> Time"
    time.Print("v")
    terr = WS(ws,obs.find(MDSettings.GetTerrVarOutName().Data()))
    terr.setRange(myconfigfile["BasicVariables"]["BeautyTimeErr"]["Range"][0],
                  myconfigfile["BasicVariables"]["BeautyTimeErr"]["Range"][1])
    print "==> Time error"
    terr.Print("v")
    if noresolution:
        terr.setMin(0.0)
        terr.setVal(0.0)
        terr.setConstant(True)
    id = WS(ws,obs.find(MDSettings.GetIDVarOutName().Data()))

    print "==> Bachelor charge (to create categories; not really a variable!)"
    id.Print("v")
    if singletagger:
        tag = WS(ws,RooCategory("tagDecComb","tagDecComb"))
        tag.defineType("Bbar_1",-1)
        tag.defineType("Untagged",0)
        tag.defineType("B_1",+1)
    else:
        tag = WS(ws,obs.find("tagDecComb"))
        
    print "==> Tagging decision"
    tag.Print("v")
    
    mistag = WS(ws,obs.find("tagOmegaComb"))
    mistag.setRange(0,0.5)
    if notagging:
        mistag.setVal(0.0)
        mistag.setConstant(True)
    print "==> Mistag"
    mistag.Print("v")
    observables = RooArgSet(time,tag)

    # Physical parameters
    #-----------------------

    print "=========================================================="
    print "Setting physical parameters"
    print "=========================================================="
    
    gammad = WS(ws,RooRealVar('Gammad', '%s average lifetime' % bName, myconfigfile["DecayRate"]["Gammad"], 0., 5., 'ps^{-1}'))
    #setConstantIfSoConfigured(ws.obj('Gammad'),myconfigfile)
    
    deltaGammad = WS(ws,RooRealVar('deltaGammad', 'Lifetime difference', myconfigfile["DecayRate"]["DeltaGammad"], -1., 1., 'ps^{-1}'))
    #setConstantIfSoConfigured(ws.obj('deltaGammad'),myconfigfile)
    
    deltaMd = WS(ws,RooRealVar('deltaMd', '#Delta m_{d}', myconfigfile["DecayRate"]["DeltaMd"], 0.0, 1.0, 'ps^{-1}'))
    #setConstantIfSoConfigured(ws.obj('deltaMd'),myconfigfile)

    
    # Decay time acceptance model
    # ---------------------------
    
    print "=========================================================="
    print "Defining decay time acceptance model"
    print "=========================================================="

    if noacceptance:
        print '==> Perfect acceptance ("straight line")'
        tacc = None
        taccNorm = None
    else:
        print '==> Time-dependent acceptance'
        tacc, taccNorm = buildSplineAcceptance(ws,
                                               ws.obj('BeautyTime'),
                                               "splinePDF",
                                               myconfigfile["AcceptanceKnots"],
                                               myconfigfile["AcceptanceValues"],
                                               False,
                                               debug)
        print tacc
        print taccNorm
        
    # Decay time resolution model
    # ---------------------------

    print "=========================================================="
    print "Defining decay time resolution model"
    print "=========================================================="

    if noresolution:
        print '===> Using perfect resolution'
        trm = None
        terrpdf = None
    else:
        if not pereventterr:
            print '===> Using a mean resolution model'
            myconfigfile["DecayTimeResolutionModel"] = myconfigfile["DecayTimeResolutionMeanModel"]
            terrpdf = None
        else:
            print '===> Using a per-event time resolution'
            myconfigfile["DecayTimeResolutionModel"] = myconfigfile["DecayTimeResolutionPEDTE"]

            observables.add( terr )
            terrWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["Toys"]["fileNameTerr"]), TString(myconfigfile["Toys"]["Workspace"]), debug)
            terrpdf = []
            for i in range(0,bound):
                terrtemp = WS(ws,Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(terrWork, TString(myconfigfile["Toys"]["TerrTempName"]), debug))
                #Dirty, nasty but temporary workaround to cheat RooFit strict requirements (changing dependent RooRealVar) 
                lab0_LifetimeFit_ctauErr = WS(ws,RooRealVar("lab0_LifetimeFit_ctauErr",
                                                      "lab0_LifetimeFit_ctauErr",
                                                      myconfigfile["BasicVariables"]["BeautyTimeErr"]["Range"][0],
                                                      myconfigfile["BasicVariables"]["BeautyTimeErr"]["Range"][1]))
                terrHist = WS(ws,terrtemp.createHistogram("terrHist",lab0_LifetimeFit_ctauErr))
                terrDataHist = WS(ws,RooDataHist("terrHist","terrHist",RooArgList(terr),terrHist))
                terrpdf.append(WS(ws,RooHistPdf(terrtemp.GetName(),terrtemp.GetTitle(),RooArgSet(terr),terrDataHist)))
                print terrpdf[i]
                
        trm, tacc = getResolutionModel(ws, myconfigfile, time, terr, tacc)
        print trm
        print tacc
    
    # Per-event mistag
    # ---------------------------

    print "=========================================================="
    print "Defining tagging and mistag"
    print "=========================================================="

    p0B = []
    p0Bbar = []
    p1B = []
    p1Bbar = []
    avB = []
    avBbar = []
    
    constList = RooArgSet()
    mistagCalibB = []
    mistagCalibBbar = []
    tagOmegaList = []
    
    if notagging:
        print '==> No tagging: <eta>=0'
        mistag.setVal(0.0)
        mistag.setConstant(True)
        tagOmegaList += [ [mistag] ]
    else:
        print '==> Non-trivial tagging'
        if singletagger:
            print '==> Single tagger'
            p0B.append(WS(ws,RooRealVar('p0_B_OS', 'p0_B_OS', myconfigfile["TaggingCalibration"]["OS"]["p0"], 0.0, 0.5)))
            p1B.append(WS(ws,RooRealVar('p1_B_OS', 'p1_B_OS', myconfigfile["TaggingCalibration"]["OS"]["p1"], 0.5, 1.5)))
            avB.append(WS(ws,RooRealVar('av_B_OS', 'av_B_OS', myconfigfile["TaggingCalibration"]["OS"]["average"])))
            #setConstantIfSoConfigured(p0B[0],myconfigfile)
            #setConstantIfSoConfigured(p1B[0],myconfigfile)
            mistagCalibB.append(WS(ws,MistagCalibration("mistagCalib_B_OS", "mistagCalib_B_OS", mistag, p0B[0], p1B[0], avB[0])))

            p0Bbar.append(WS(ws,RooRealVar('p0_Bbar_OS', 'p0_B_OS', myconfigfile["TaggingCalibration"]["OS"]["p0Bar"], 0.0, 0.5)))
            p1Bbar.append(WS(ws,RooRealVar('p1_Bbar_OS', 'p1_B_OS', myconfigfile["TaggingCalibration"]["OS"]["p1Bar"], 0.5, 1.5)))
            avBbar.append(WS(ws,RooRealVar('av_Bbar_OS', 'av_B_OS', myconfigfile["TaggingCalibration"]["OS"]["averageBar"])))
            #setConstantIfSoConfigured(p0Bbar[0],myconfigfile)
            #setConstantIfSoConfigured(p1Bbar[0],myconfigfile)
            mistagCalibBbar.append(WS(ws,MistagCalibration("mistagCalib_Bbar_OS", "mistagCalib_Bbar_OS", mistag, p0Bbar[0], p1Bbar[0], avBbar[0])))

            tagOmegaList += [ [mistagCalibB[0],mistagCalibBbar[0]] ]
        else:
            print '==> Combining more taggers'
            i=0
            for tg in ["OS","SS","OS+SS"]:
                p0B.append(WS(ws,RooRealVar('p0_B_'+tg, 'p0_B_'+tg, myconfigfile["TaggingCalibration"][tg]["p0"], 0., 0.5 )))
                p1B.append(WS(ws,RooRealVar('p1_B_'+tg, 'p1_B_'+tg, myconfigfile["TaggingCalibration"][tg]["p1"], 0.5, 1.5 )))
                avB.append(WS(ws,RooRealVar('av_B_'+tg, 'av_B_'+tg, myconfigfile["TaggingCalibration"][tg]["average"])))
                #setConstantIfSoConfigured(p0B[i],myconfigfile)
                #setConstantIfSoConfigured(p1B[i],myconfigfile)
                mistagCalibB.append(WS(ws,MistagCalibration("mistagCalib_B_"+tg, "mistagCalib_B_"+tg, mistag, p0B[i], p1B[i], avB[i])))
                
                p0Bbar.append(WS(ws,RooRealVar('p0_Bbar_'+tg, 'p0_Bbar_'+tg, myconfigfile["TaggingCalibration"][tg]["p0Bar"], 0., 0.5 )))
                p1Bbar.append(WS(ws,RooRealVar('p1_Bbar_'+tg, 'p1_Bbar_'+tg, myconfigfile["TaggingCalibration"][tg]["p1Bar"], 0.5, 1.5 )))
                avBbar.append(WS(ws,RooRealVar('av_Bbar_'+tg, 'av_Bbar_'+tg, myconfigfile["TaggingCalibration"][tg]["averageBar"])))
                #setConstantIfSoConfigured(p0Bbar[i],myconfigfile)
                #setConstantIfSoConfigured(p1Bbar[i],myconfigfile)
                mistagCalibBbar.append(WS(ws,MistagCalibration("mistagCalib_Bbar_"+tg, "mistagCalib_Bbar_"+tg, mistag, p0Bbar[i], p1Bbar[i], avBbar[i])))

                tagOmegaList += [ [mistagCalibB[i],mistagCalibBbar[i]] ]
                
                i = i+1

    print '==> Tagging calibration lists:'
    print tagOmegaList

    mistagWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["Toys"]["fileNameMistag"]), TString(myconfigfile["Toys"]["Workspace"]), debug)
    mistagPDF = []
    mistagPDFList = []
    if notagging:
        mistagPDFList = None
    else:
        for i in range(0,3):
            mistagPDF.append(WS(ws,Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(mistagWork, TString(myconfigfile["Toys"]["MistagTempName"][i]), debug)))
            if not singletagger:
                mistagPDFList.append(mistagPDF[i])

        if singletagger:
            mistagPDFList.append(mistagPDF[0])
            
        observables.add( mistag )

    print "=========================================================="
    print "Summary of observables"
    print "=========================================================="

    observables.Print("v")
        
    # Total time PDF
    # ---------------------------

    print "=========================================================="
    print "Creating time PDF"
    print "=========================================================="

    timePDFplus = []
    timePDFminus = []
    timePDF = []

    adet_plus = WS(ws,RooConstVar('adet_plus','+1',1.0))
    id_plus = WS(ws, RooCategory('id_plus','Pi+'))
    id_plus.defineType('h+',1)

    adet_minus = WS(ws,RooConstVar('adet_minus','-1',-1.0))
    id_minus = WS(ws, RooCategory('id_minus','Pi-'))
    id_minus.defineType('h-',-1)
    
    for i in range(0,bound):
        utils = GenTimePdfUtils(myconfigfile,
                                ws,
                                gammad,
                                deltaGammad,
                                deltaMd,
                                singletagger,
                                notagging,
                                noprodasymmetry,
                                notagasymmetries,
                                debug)
        
        timePDFplus.append(buildBDecayTimePdf(myconfigfile,
                                              "Signal_DmPip",
                                              ws,
                                              time, terr, tag, id_plus,
                                              tagOmegaList,
                                              utils['tagEff'],
                                              gammad,
                                              deltaGammad,
                                              deltaMd,
                                              utils['C'],
                                              utils['D'],
                                              utils['Dbar'],
                                              utils['S'],
                                              utils['Sbar'],
                                              trm,
                                              tacc,
                                              terrpdf[i] if terrpdf != None else terrpdf,
                                              mistagPDFList,
                                              mistag,
                                              None,
                                              None,
                                              utils['aProd'],
                                              adet_plus,
                                              utils['aTagEff']))

        timePDFminus.append(buildBDecayTimePdf(myconfigfile,
                                               "Signal_DpPim",
                                               ws,
                                               time, terr, tag, id_minus,
                                               tagOmegaList,
                                               utils['tagEff'],
                                               gammad,
                                               deltaGammad,
                                               deltaMd,
                                               utils['C'],
                                               utils['D'],
                                               utils['Dbar'],
                                               utils['S'],
                                               utils['Sbar'],
                                               trm,
                                               tacc,
                                               terrpdf[i] if terrpdf != None else terrpdf,
                                               mistagPDFList,
                                               mistag,
                                               None,
                                               None,
                                               utils['aProd'],
                                               adet_minus,
                                               utils['aTagEff']))

        timePDF.append(WS(ws,RooSimultaneous("Signal", "Signal", id)))
        timePDF[i].addPdf(timePDFplus[i],"h+")
        timePDF[i].addPdf(timePDFminus[i],"h-")
        
                                          
    totPDF = []
    for i in range(0,bound):
        totPDF.append(timePDF[i]) 

    # Fitting
    # ---------------------------

    print "=========================================================="
    print "Fixing what is required for the fit"
    print "=========================================================="
    from B2DXFitters.utils import setConstantIfSoConfigured
    setConstantIfSoConfigured(myconfigfile, totPDF[0])

    print "=========================================================="
    print "Fitting"
    print "=========================================================="
    if not Blinding and toys: #Unblind yourself
        if nosWeights:
            myfitresult = totPDF[0].fitTo(dataA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                          RooFit.Verbose(True), RooFit.SumW2Error(False), RooFit.Timer(True), RooFit.Offset(True))#,
            #RooFit.ExternalConstraints(constList))
        else:
            myfitresult = totPDF[0].fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2), RooFit.Timer(True),\
                                          RooFit.Verbose(True), RooFit.SumW2Error(True), RooFit.Timer(True), RooFit.Offset(True))#, 
            #RooFit.ExternalConstraints(constList))
        qual = myfitresult.covQual()
        status = myfitresult.status()
        print 'MINUIT status is ', myfitresult.status()
        print "---> Fit done; printing results"
        myfitresult.Print("v")
        myfitresult.correlationMatrix().Print()
        myfitresult.covarianceMatrix().Print()
        floatpar = myfitresult.floatParsFinal()
        initpar = myfitresult.floatParsInit()
        
    else :    #Don't
        myfitresult = totPDF[0].fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                      RooFit.SumW2Error(True), RooFit.PrintLevel(-1), RooFit.Offset(True), #RooFit.ExternalConstraints(constList),
                                      RooFit.Timer(True))     

    print "=========================================================="
    print "Fit done; saving output workspace"
    print "=========================================================="
    workout = RooWorkspace("workspace","workspace")
        
    if nosWeights:
        getattr(workout,'import')(dataWA)
    else:
        getattr(workout,'import')(dataWA)
    getattr(workout,'import')(totPDF[0])
    getattr(workout,'import')(myfitresult)
    saveNameTS = TString(wsname)
    workout.Print()
    GeneralUtils.SaveWorkspace(workout,saveNameTS, debug)

    #Save fit results for pull plots
    if not Blinding and toys:
        from B2DXFitters.FitResultGrabberUtils import CreatePullTree as CreatePullTree
        CreatePullTree(fileNamePull, myfitresult, 'status')
        
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
                  default = 'WS_Time_DsK.root',
                  help    = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                  )

parser.add_option( '--fileNamePull',
                   dest = 'fileNamePull',
                   default = 'pull.root',
                   help = 'name of the file to store info for pull plot'
                   )

parser.add_option( '--pereventterr',
                   dest = 'pereventterr',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event time errors?'
                   )

parser.add_option( '-t','--toys',
                   dest = 'toys',
                   action = 'store_true', 
                   default = False,
                   help = 'are we working with toys?'
                   )   

parser.add_option( '--pathName',
                   dest = 'pathName',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsK_all_both.root',
                   help = 'name of the inputfile'
                   )   

parser.add_option( '--treeName',
                   dest = 'treeName',
                   default = 'merged',
                   help = 'name of the workspace'
                   )  

parser.add_option( '--year',
                   dest = 'year',
                   default = '2012')

parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsKConfigForNominalGammaFit')

parser.add_option( '--configNameMDFitter',
                   dest = 'configNameMD',
                   default = 'Bs2DsKConfigForNominalMassFitBDTGA')

parser.add_option( '--sWeightsCorr',
                   dest = 'sWeightsCorr',
                   default = False,
                   action = 'store_true',
                   help = 'Apply sWeights correction factor to better estimate uncertainties'
                   )

parser.add_option( '--noresolution',
                   dest = 'noresolution',
                   action = 'store_true',
                   default = False,
                   help = 'Fit with perfect resolution'
                   )

parser.add_option( '--noacceptance',
                   dest = 'noacceptance',
                   action = 'store_true',
                   default = False,
                   help = 'Fit with perfect acceptance'
                   )

parser.add_option( '--notagging',
                   dest = 'notagging',
                   action = 'store_true',
                   default = False,
                   help = 'Fit with calibrated mistag always equal to zero'
                   )

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
                   help = 'Fit without tagging efficiency asymmetries'
                   )

parser.add_option( '--nosWeights',
                   dest = 'nosWeights',
                   action = 'store_true',
                   default = False,
                   help = 'Fit without applying sWeigthing (to be used with signal sample only)'
                   )

parser.add_option( '--noUntagged',
                   dest = 'noUntagged',
                   action = 'store_true',
                   default = False,
                   help = 'Fit tagged data only'
                   )

parser.add_option( '--singletagger',
                   dest = 'singletagger',
                   action = 'store_true',
                   default = False,
                   help = 'Using only one tagger'
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
    sys.path.append("../data/Bd2DPi_3fbCPV/Bd2DPi/")
    
    totPDF = runBdGammaFitterOnToys( options.debug,
                                     options.wsname,
                                     options.pereventterr,
                                     options.year,
                                     options.toys,
                                     options.pathName,
                                     options.treeName,
                                     options.fileNamePull,
                                     options.configName,
                                     options.configNameMD,
                                     options.sWeightsCorr,
                                     options.noresolution,
                                     options.noacceptance,
                                     options.notagging,
                                     options.noprodasymmetry,
                                     options.nodetasymmetry,
                                     options.notagasymmetries,
                                     options.nosWeights,
                                     options.noUntagged,
                                     options.singletagger)

                                                                                                                        
# -----------------------------------------------------------------------------

