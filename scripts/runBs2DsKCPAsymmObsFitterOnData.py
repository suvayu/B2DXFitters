#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC fit for the CP asymmetry observables        #
#   in Bs -> Ds K                                                             #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBs2DsKCPAsymmObsFitterOnData.py [-d -s ]                     #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#   Author: Manuel Schiller                                                   #
#   Author: Agnieszka Dziurda                                                 #
#   Author: Vladimir Vava Gligorov                                            #
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
import B2DXFitters
import ROOT
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------


# MODELS
AcceptanceFunction       =  'PowLawAcceptance'

# BLINDING
Blinding =  False

param_limits = {"lower" : -10., "upper" : 10.}

# DATA FILES
saveName      = 'work_'

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------
def setConstantIfSoConfigured(var,myconfigfile):
    if var.GetName() in myconfigfile["constParams"] : var.setConstant()

#------------------------------------------------------------------------------
import threading,os,signal
from threading import *
def killme() :
    os._exit(1)
def handler(signum, frame):
    print 'Signal handler called with signal', signum
    os._exit(1)
#------------------------------------------------------------------------------
def runBdGammaFitterOnData(debug, wsname, 
                           tVar, terrVar, tagVar, tagOmegaVar, idVar, mVar,
                           pereventmistag, toys,pathName,
                           treeName, configName, configNameMD, nokfactcorr,
                           smearaccept, accsmearfile, accsmearhist,
                           BDTGbins, pathName2, pathName3, Cat) :

    #if not Blinding and not toys :
    #    print "RUNNING UNBLINDED!"
    #    really = input('Do you really want to unblind? ')
    #    if really != "yes" :
    #        exit(-1)

    #if toys :
    #    if int(pathToys.split('.')[1].split('_')[-1]) in bannedtoys :
    #        exit(-1)

    from B2DXFitters import taggingutils, cpobservables
         
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
 
    # tune integrator configuration
    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation','WynnEpsilon')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('maxSteps','1000')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('minSteps','0')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    # since we have finite ranges, the RooIntegrator1D is best suited to the job
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooIntegrator1D')
    
    config = TString("../data/")+TString(configNameMD)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettings.SetTimeVar(TString(tVar))
    MDSettings.SetTerrVar(TString(terrVar))
    MDSettings.SetTagVar(TString(tagVar))
    MDSettings.SetTagOmegaVar(TString(tagOmegaVar))
    MDSettings.SetIDVar(TString(idVar))
    MDSettings.SetMassBVar(TString(mVar))
    
    if (toys) :
        applykfactor = (not nokfactcorr)
    else :
        applykfactor = False
    
    MDSettings.Print()    

    if BDTGbins:
        bound = 3
        Bin = [TString("BDTG1"), TString("BDTG2"), TString("BDTG3")]
    else:
        bound = 1
        Bin = [TString("BDTGA")]
                
    workspace =[]
    workspaceW = []
            
    for i in range (0,3):
        workspace.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, TString("DsK"),
                                                        false, toys, applykfactor, debug))
        workspaceW.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName),  MDSettings, TString("DsK"),
                                                         true, toys, applykfactor, debug))
        
    workspace[0].Print()
        
    #exit(0)
    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)

    tagVarTS       = TString("qt")
    idVarTS        = TString("qf")
        
    mass = RooRealVar('mass', '%s mass' % bName, 5., 6.)
     
    gammas = RooRealVar('Gammas', '%s average lifetime' % bName, myconfigfile["Gammas"], 0., 5., 'ps^{-1}')
    gammas.setError(0.05)
    setConstantIfSoConfigured(gammas,myconfigfile)

    deltaGammas = RooRealVar('deltaGammas', 'Lifetime difference', myconfigfile["DeltaGammas"], -1., 1., 'ps^{-1}')
    setConstantIfSoConfigured(deltaGammas,myconfigfile)

    deltaMs = RooRealVar('deltaMs', '#Delta m_{s}', myconfigfile["DeltaMs"], 5., 30., 'ps^{-1}')
    setConstantIfSoConfigured(deltaMs,myconfigfile)

    # tagging
    # -------
    tagEffSig = RooRealVar('tagEffSig', 'Signal tagging efficiency'    , myconfigfile["TagEffSig"], 0.2, 0.8) #0., 1.)
    setConstantIfSoConfigured(tagEffSig,myconfigfile)
    
    # Data set
    #-----------------------
    nameData = TString("dataSet_time_Bs2DsK") 
    data  = [] 
    dataW = []
    
    for i in range(0, bound):
        data.append(GeneralUtils.GetDataSet(workspace[i],   nameData, debug))
        dataW.append(GeneralUtils.GetDataSet(workspace[i],   nameData, debug))

    dataWA = dataW[0]    
    if BDTGbins:
        dataWA.append(dataW[1])
        dataWA.append(dataW[2])
           
    nEntries = dataWA.numEntries()    
        
    dataWA.Print("v")
    obs = dataWA.get()
    time = obs.find(tVar)
    mistag = obs.find(tagOmegaVar)
    fChargeMap = obs.find("qf")
    bTagMap = obs.find("qt")
    terr = obs.find(terrVar)
    weight = obs.find("sWeights")
    observables = RooArgSet(time,bTagMap,fChargeMap)

    if debug:
        frame = time.frame()
        sliceData_1 = dataWA.reduce(RooArgSet(time,fChargeMap,bTagMap),"(qt == 0)")
        sliceData_1.plotOn(frame,RooFit.MarkerColor(kRed))
        print "Untagged: number of events: %d, sum of events: %d"%(sliceData_1.numEntries(),sliceData_1.sumEntries())
        sliceData_2 = dataWA.reduce(RooArgSet(time,fChargeMap,bTagMap),"(qt == 1)")
        print "Bs tagged: number of events: %d, sum of events: %d"%(sliceData_2.numEntries(),sliceData_2.sumEntries())
        sliceData_2.plotOn(frame,RooFit.MarkerColor(kBlue+2))
        sliceData_3 = dataWA.reduce(RooArgSet(time,fChargeMap,bTagMap),"(qt == -1)")
        sliceData_3.plotOn(frame,RooFit.MarkerColor(kOrange+2))
        print "barBs tagged: number of events: %d, sum of events: %d"%(sliceData_3.numEntries(),sliceData_3.sumEntries())        
        dataWA.plotOn(frame)
        canvas = TCanvas("canvas", "canvas", 1200, 1000)
        canvas.cd()
        frame.Draw()
        frame.GetYaxis().SetRangeUser(0.1,150)
        canvas.GetPad(0).SetLogy()
        canvas.SaveAs('data_time_DsK.pdf')

    templateWorkspacePi = GeneralUtils.LoadWorkspace(TString(myconfigfile["TemplateFilePi"]), TString(myconfigfile["TemplateWorkspace"]), debug)
    templateWorkspaceK = GeneralUtils.LoadWorkspace(TString(myconfigfile["TemplateFileK"]), TString(myconfigfile["TemplateWorkspace"]), debug)

           
    # Decay time resolution model
    # ---------------------------
    if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
        trm = PTResModels.tripleGausResolutionModel( time,
                                                     myconfigfile["resolutionScaleFactor"],
                                                     myconfigfile["resolutionMeanBias"],
                                                     myconfigfile["resolutionSigma1"],
                                                     myconfigfile["resolutionSigma2"],
                                                     myconfigfile["resolutionSigma3"],
                                                     myconfigfile["resolutionFrac1"],
                                                     myconfigfile["resolutionFrac2"],
                                                     debug
                                                     )
        
        
        terrpdf = None
    else :
        # the decay time error is an extra observable !
        observables.add( terr )
        # time, mean, scale, timeerr
        
        trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["resolutionMeanBias"], 'ps' )
        trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', myconfigfile["resolutionScaleFactor"])
        trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGausPEDTE',
                             time, trm_mean, terr, trm_scale) 
        
        terrpdf = []
        for i in range(0,bound):
            name = TString("sigTimeErrorPdf_%s")+Bin[i]
            #if BDTGbins:
            #    terrpdf.append(GeneralUtils.CreateHistPDF(dataW[i], terr, name, myconfigfile['nBinsProperTimeErr'], debug))
            #else:
            #    terrpdf.append(GeneralUtils.CreateHistPDF(dataWA, terr, name, myconfigfile['nBinsProperTimeErr'], debug))
            terrpdf.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(templateWorkspaceK,
                                                                            TString(myconfigfile["TimeErrorTemplateBDTGA"]),debug))
        
    # Decay time acceptance function
    # ------------------------------
    if AcceptanceFunction and not (AcceptanceFunction == None or AcceptanceFunction == 'None'):
        if AcceptanceFunction == "BdPTAcceptance" :
            tacc_slope  = RooRealVar('tacc_slope'   , 'BdPTAcceptance_slope'    , myconfigfile["tacc_slope"]    , -100.0 , 100.0 )
            tacc_offset = RooRealVar('tacc_offset'  , 'BdPTAcceptance_offset'   , myconfigfile["tacc_offset"]   , -100.0 , 100.0 )
            tacc_beta   = RooRealVar('tacc_beta'    , 'BdPTAcceptance_beta'     , myconfigfile["tacc_beta"]     , -10.00 , 10.00 )
            tacc = BdPTAcceptance('BsPTAccFunction', '%s decay time acceptance function' % bName,
                                  time, tacc_beta, tacc_slope, tacc_offset)
            setConstantIfSoConfigured(tacc_slope,myconfigfile)
            setConstantIfSoConfigured(tacc_offset,myconfigfile)
            setConstantIfSoConfigured(tacc_beta,myconfigfile)
        elif AcceptanceFunction == 'PowLawAcceptance' : 
            if smearaccept :
                print 'SMEARING THE ACCEPTANCE FUNCTION FROM HISTOGRAM'
                print accsmearfile, accsmearhist 
                rfile = TFile(accsmearfile, 'read')
                hcorr = rfile.Get(accsmearhist)
                ardhist = RooDataHist('ardhist', 'DsK/DsPi acceptance ratio datahist',
                                        RooArgList(time), RooFit.Import(hcorr, False))
                accratio = RooHistFunc('accratio', 'DsK/DsPi acceptance ratio',
                                        RooArgSet(time), ardhist)
            else :
                print 'NOT SMEARING THE ACCEPTANCE FUNCTION'
                accratio = RooConstVar('accratio','accratio',1.)

            tacc_beta = []
            tacc_exponent = []
            tacc_offset = []
            tacc_turnon = []
            tacc = []
            
            for i in range(0,bound):
                if BDTGbins:
                    name_beta = TString("tacc_beta_")+Bin[i]
                    name_exponent = TString("tacc_exponent_")+Bin[i]
                    name_offset = TString("tacc_offset_")+Bin[i]
                    name_turnon = TString("tacc_turnon_")+Bin[i]
                    name_tacc = TString("BsPowLawAcceptance_")+Bin[i]
                else:
                    name_beta = TString("tacc_beta")
                    name_exponent = TString("tacc_exponent")
                    name_offset = TString("tacc_offset")
                    name_turnon = TString("tacc_turnon")
                    name_tacc = TString("BsPowLawAcceptance")
                    
                tacc_beta.append(RooRealVar(name_beta.Data(), name_beta.Data(), myconfigfile[name_beta.Data()],  0.00 , 0.15))
                tacc_exponent.append(RooRealVar(name_exponent.Data(), name_exponent.Data(), myconfigfile[name_exponent.Data()], 1.00 , 4.00))
                tacc_offset.append(RooRealVar(name_offset.Data(), name_offset.Data(), myconfigfile[name_offset.Data()], -0.2 , 0.10))
                tacc_turnon.append(RooRealVar(name_turnon.Data(), name_turnon.Data(), myconfigfile[name_turnon.Data()], 0.50 , 5.00))
                if smearaccept :
                    tacc.append(PowLawAcceptance(name_tacc.Data(), name_tacc.Data(),
                                                 tacc_turnon[i], time, tacc_offset[i], tacc_exponent[i], tacc_beta[i],accratio))
                else:
                    tacc.append(PowLawAcceptance(name_tacc.Data(), name_tacc.Data(),
                                                 tacc_turnon[i], time, tacc_offset[i], tacc_exponent[i], tacc_beta[i]))
                setConstantIfSoConfigured(tacc_beta[i],myconfigfile)
                setConstantIfSoConfigured(tacc_exponent[i],myconfigfile)
                setConstantIfSoConfigured(tacc_offset[i],myconfigfile)
                setConstantIfSoConfigured(tacc_turnon[i],myconfigfile)
                if debug:
                    print "[INFO] Create %s with parameters %s, %s, %s, %s"%(name_tacc.Data(),
                                                                             name_beta.Data(),
                                                                             name_exponent.Data(),
                                                                             name_offset.Data(),
                                                                             name_turnon.Data())
                          
            
    else :
        tacc = None

    # Bin acceptance
    if myconfigfile["nBinsAcceptance"] > 0:
        # provide binning for acceptance
        from ROOT import RooUniformBinning
        acceptanceBinning = RooUniformBinning(time.getMin(), time.getMax(), myconfigfile["nBinsAcceptance"],'acceptanceBinning')
        time.setBinning(acceptanceBinning, 'acceptanceBinning')
        acceptance = []
        timeresmodel = []
        for i in range(0,bound):
            acceptance.append(RooBinnedPdf("%sBinned"%tacc[i].GetName(),"%sBinnedA"%tacc[i].GetName(), time, 'acceptanceBinning', tacc[i]))
            acceptance[i].setForceUnitIntegral(True)
            timeresmodel.append(RooEffResModel("%s_timeacc_%s"% (trm.GetName(), acceptance[i].GetName()),
                                               "trm plus acceptance", trm, acceptance[i]))
                    
       
        
    if 'PEDTE' in myconfigfile["DecayTimeResolutionModel"] and 0 != myconfigfile['nBinsProperTimeErr']:
        if debug:
            print "Set binning for time error: %d"%(myconfigfile['nBinsProperTimeErr'])
        terr.setBins(myconfigfile['nBinsProperTimeErr'], 'cache')
        for i in range(0,bound):
                timeresmodel[i].setParameterizeIntegral(RooArgSet(terr))
        
                                                
    if pereventmistag :
        # we need calibrated mistag
        calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"]) #, 0.90, 1.5)
        calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"]) #, 0.25, 0.5)
        avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"]) #, 0.2, 0.6)
        
        mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
                                             mistag, calibration_p0,calibration_p1,avmistag)
        observables.add( mistag )
        name = TString("sigMistagPdf")
        mistagPDF  = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(templateWorkspaceK, TString(myconfigfile["MistagTemplateName"]), debug)
        #mistagPDF = GeneralUtils.CreateHistPDF(dataWA, mistag, name, myconfigfile['nBinsMistag'], debug)

    else:
        mistagHistPdf = None
        mistagCalibrated =  mistag
        
   
    ACPobs = cpobservables.AsymmetryObservables(myconfigfile["ArgLf"], myconfigfile["ArgLbarfbar"], myconfigfile["ModLf"])
    ACPobs.printtable()
        
    Cf    = ACPobs.Cf()
    Sf    = ACPobs.Sf()
    Df    = ACPobs.Df()
    Sfbar = ACPobs.Sfbar()
    Dfbar = ACPobs.Dfbar()

    sigC = RooRealVar('C', 'C coeff.', Cf, param_limits["lower"], param_limits["upper"])
    sigS = RooRealVar('S', 'S coeff.', Sf, param_limits["lower"], param_limits["upper"])
    sigD = RooRealVar('D', 'D coeff.', Df, param_limits["lower"], param_limits["upper"])
    sigCbar = RooRealVar('Cbar', 'Cbar coeff.', Cf, param_limits["lower"], param_limits["upper"])
    sigSbar = RooRealVar('Sbar', 'Sbar coeff.', Sfbar, param_limits["lower"], param_limits["upper"])
    sigDbar = RooRealVar('Dbar', 'Dbar coeff.', Dfbar, param_limits["lower"], param_limits["upper"])
    setConstantIfSoConfigured(sigC,myconfigfile)
    setConstantIfSoConfigured(sigS,myconfigfile)
    setConstantIfSoConfigured(sigD,myconfigfile)
    setConstantIfSoConfigured(sigCbar,myconfigfile)
    setConstantIfSoConfigured(sigSbar,myconfigfile)
    setConstantIfSoConfigured(sigDbar,myconfigfile)    
    print "lower limit: %s, upper limit: %s"%(str(param_limits["lower"]), str(param_limits["upper"]))
    aProd = zero     # production asymmetry
    aDet = zero      # detector asymmetry
    aTagEff = zero   # taginng eff asymmetry

    if pereventmistag:
        otherargs = [ mistag, mistagPDF, tagEffSig ]
    else:
        otherargs = [ tagEffSig ]
    otherargs.append(mistagCalibrated)
    otherargs.append(aProd)
    otherargs.append(aDet)
    otherargs.append(aTagEff)

    flag = 0 #DecRateCoeff.AvgDelta
    
    cosh = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven, fChargeMap, bTagMap, one, one, *otherargs)
    sinh = DecRateCoeff('signal_sinh', 'signal_sinh', flag | DecRateCoeff.CPEven, fChargeMap, bTagMap, sigD, sigDbar, *otherargs)
    cos  = DecRateCoeff('signal_cos' , 'signal_cos' , DecRateCoeff.CPOdd, fChargeMap, bTagMap, sigC, sigC, *otherargs)
    sin  = DecRateCoeff('signal_sin' , 'signal_sin' , flag | DecRateCoeff.CPOdd | DecRateCoeff.Minus, fChargeMap, bTagMap, sigS, sigSbar, *otherargs)
    
    
    # Set the signal handler and a 5-second alarm
    #signal.signal(signal.SIGALRM, handler)
    #signal.alarm(120)
    
    
    #if debug :
    #    print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!' 
    #    data.Print("v")
    #    for i in range(0,nEntries) : 
    #        data.get(i).Print("v")
    #        print data.weight()
    
    tauinv          = Inverse( "tauinv","tauinv", gammas)
    
    
    
    #if debug :
    #    print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!'
    #    data.Print("v")
    #    for i in range(0,nEntries) :
    #        obs = data.get(i)
    #        obs.Print("v")
    #        #data.get(i).Print("v")
    #        print data.weight()
    #        print cos.getValV(obs)
    #        print sin.getValV(obs)
    #        print cosh.getValV(obs)
    #        print sinh.getValV(obs)
    
    
    timePDF = []
    for i in range(0,bound):
        name_time = TString("time_signal_")+Bin[i]
        timePDF.append(RooBDecay(name_time.Data(),name_time.Data(), time, tauinv, deltaGammas,
                                 cosh, sinh, cos, sin,
                                 deltaMs, timeresmodel[i], RooBDecay.SingleSided))
        
        
    if 'PEDTE' in myconfigfile["DecayTimeResolutionModel"]:
        noncondset = RooArgSet(time, fChargeMap, bTagMap)
        if pereventmistag:
            noncondset.add(mistag)
        totPDF = []
        for i in range(0,bound):
            name_timeterr = TString("signal_TimeTimeerrPdf_")+Bin[i]
            totPDF.append(RooProdPdf(name_timeterr.Data(), name_timeterr.Data(),
                                     RooArgSet(terrpdf[i]), RooFit.Conditional(RooArgSet(timePDF[i]), noncondset)))
            
            
    else:
        totPDF = []
        for i in range(0,bound):
            totPDF.append(timePDF[i])
                                        
            
    if Cat:
        if BDTGbins:
            BdtgBin = RooCategory("bdtgbin","bidtgbin")
            for i in range(0,3):
                BdtgBin.defineType(Bin[i].Data())

            weight = obs.find("sWeights")
            observables.add( weight )
            
            combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                  RooFit.Index(BdtgBin),
                                  RooFit.Import(Bin[0].Data(),data[0]),
                                  RooFit.Import(Bin[1].Data(),data[1]),
                                  RooFit.Import(Bin[2].Data(),data[2]),
                                  RooFit.WeightVar("sWeights"))
            
            
            totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
            totPDFSim.addPdf(totPDF[0], Bin[0].Data())
            totPDFSim.addPdf(totPDF[1], Bin[1].Data())
            totPDFSim.addPdf(totPDF[2], Bin[2].Data())
        else:
            BdtgBin = RooCategory("bdtgbin","bidtgbin")
            BdtgBin.defineType(Bin[0].Data())
            
            weight = obs.find("sWeights")
            observables.add( weight )
            
            combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                  RooFit.Index(BdtgBin),
                                  RooFit.Import(Bin[0].Data(),data[0]),
                                  RooFit.WeightVar("sWeights"))
            
            totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
            totPDFSim.addPdf(totPDF[0],  Bin[0].Data())
            
        pdf = RooAddPdf('totPDFtot', 'totPDFtot', RooArgList(totPDFSim), RooArgList())
            
    if toys or not Blinding: #Unblind yourself
        if BDTGbins or Cat:
            myfitresult = pdf.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                    RooFit.Verbose(False), RooFit.SumW2Error(True))
            
        else:
            myfitresult = totPDF.fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                       RooFit.Verbose(False), RooFit.SumW2Error(True))
            
        myfitresult.Print("v")
        myfitresult.correlationMatrix().Print()
        myfitresult.covarianceMatrix().Print()
    else :    #Don't
        if BDTGbins or Cat:
            myfitresult = pdf.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                    RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            
        else:
            myfitresult = totPDF.fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                       RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            
        print 'Matrix quality is',myfitresult.covQual()
        par = myfitresult.floatParsFinal() 
        par[0].Print("v") 
        par[1].Print("v")
        par[2].Print("v")
        par[3].Print("v")
        par[4].Print("v")
        if  (sigS.getVal() < param_limits["lower"] + sigS.getError() ) or (sigS.getVal() > param_limits["upper"] - sigS.getError() ) :
            print "S IS CLOSE TO THE FIT LIMITS!!!!"       
        if  (sigSbar.getVal() < param_limits["lower"] + sigSbar.getError() ) or (sigSbar.getVal() > param_limits["upper"] - sigSbar.getError() ) : 
            print "Sbar IS CLOSE TO THE FIT LIMITS!!!!"
        if  (sigD.getVal() < param_limits["lower"] + sigD.getError() ) or  (sigD.getVal() > param_limits["upper"] - sigD.getError() ) : 
            print "D IS CLOSE TO THE FIT LIMITS!!!!"       
        if  (sigDbar.getVal() < param_limits["lower"] + sigDbar.getError() ) or  (sigDbar.getVal() > param_limits["upper"] - sigDbar.getError() ) :
            print "Dbar IS CLOSE TO THE FIT LIMITS!!!!"     
            
    workout = RooWorkspace("workspace","workspace")
        
    if Cat or BDTGbins:
        getattr(workout,'import')(combData)
        getattr(workout,'import')(pdf)
    else:
        getattr(workout,'import')(data)
        getattr(workout,'import')(totPDF)
    getattr(workout,'import')(myfitresult)
    #workout.writeToFile(wsname)
    saveNameTS = TString(wsname)
    workout.Print()
    GeneralUtils.SaveWorkspace(workout,saveNameTS, debug)
    workout.Print()
                
                         
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
parser.add_option( '--tvar',
                   dest = 'tvar',
                   default = 'lab0_LifetimeFit_ctau',
                   help = 'set observable '
                   )

parser.add_option( '--timeerr',
                   dest = 'terrvar',
                   default = 'lab0_LifetimeFit_ctauErr',
                   help = 'set observable '
                   )
parser.add_option( '--tagvar',
                   dest = 'tagvar',
                   default = 'lab0_BsTaggingTool_TAGDECISION_OS',
                   help = 'set observable '
                   )
parser.add_option( '--tagomegavar',
                   dest = 'tagomegavar',
                   default = 'lab0_BsTaggingTool_TAGOMEGA_OS',
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

parser.add_option( '--pereventmistag',
                   dest = 'pereventmistag',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event mistag?'
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

parser.add_option( '--pathName2',
                   dest = 'pathName2',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsK_all_both.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--pathName3',
                   dest = 'pathName3',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsK_all_both.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--BDTGbins',
                   dest = 'BDTGbins',
                   default = False,
                   action = 'store_true'
                   )

parser.add_option( '--treeName',
                   dest = 'treeName',
                   default = 'merged',
                   help = 'name of the workspace'
                   )  


parser.add_option( '--kfactcorr',
                    dest = 'nokfactcorr',
                    action = 'store_false',
                    default = True)

parser.add_option( '--smearAccept',
                   dest = 'smearaccept',
                   action = 'store_true',
                   default = False)  

parser.add_option( '--smearAcceptFile',
                   dest = 'accsmearfile',
                   default = '../data/acceptance-ratio-hists.root')

parser.add_option( '--smearAcceptHist',
                   dest = 'accsmearhist',
                   default = 'haccratio_cpowerlaw')

parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsKConfigForNominalGammaFit')

parser.add_option( '--configNameMDFitter',
                   dest = 'configNameMD',
                   default = 'Bs2DsKConfigForNominalMassFitBDTGA')

parser.add_option( '--cat',
                   dest = 'cat',
                   default = False,
                   action = 'store_true'
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
    sys.path.append("../data")
    
    totPDF = runBdGammaFitterOnData( options.debug,
                                     options.wsname,
                                     options.tvar,
                                     options.terrvar,
                                     options.tagvar,
                                     options.tagomegavar,
                                     options.idvar,
                                     options.mvar,
                                     options.pereventmistag,
                                     options.toys,
                                     options.pathName,
                                     options.treeName,
                                     options.configName,
                                     options.configNameMD,
                                     options.nokfactcorr,
                                     options.smearaccept,
                                     options.accsmearfile,
                                     options.accsmearhist,
                                     options.BDTGbins,
                                     options.pathName2,
                                     options.pathName3,
                                     options.cat
                                     )

                                                                                                                        
# -----------------------------------------------------------------------------

