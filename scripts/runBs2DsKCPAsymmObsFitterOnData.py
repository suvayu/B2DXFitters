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
from B2DXFitters import *
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

# BLINDING
Blinding =  True

param_limits = {"lower" : -4., "upper" : 4.}

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
                           pereventmistag, pereventterr,
                           toys,pathName,
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

    # Reading data set
    #-----------------------
        
    config = TString("../data/")+TString(configNameMD)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettings.SetTimeVar(TString(tVar))
    MDSettings.SetTerrVar(TString(terrVar))
    #MDSettings.SetTagVar(TString(tagVar))
    #MDSettings.SetTagOmegaVar(TString(tagOmegaVar))
    MDSettings.SetIDVar(TString(idVar))
    MDSettings.SetMassBVar(TString(mVar))
    
    if (toys) :
        applykfactor = (not nokfactcorr)
    else :
        applykfactor = False
    
    MDSettings.Print("v")    

    if BDTGbins:
        bound = 3
        Bin = [TString("BDTG1"), TString("BDTG2"), TString("BDTG3")]
    else:
        bound = 1
        Bin = [TString("BDTGA")]
                
    workspace =[]
    workspaceW = []
    part = "BsDsK"
    for i in range (0,bound):
        workspace.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, TString(part),
                                                        false, toys, applykfactor, debug))
        workspaceW.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName),  MDSettings, TString(part),
                                                         true, toys, applykfactor, debug))
        
    workspace[0].Print()
    
    #exit(0)
    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)

    tagVarTS       = TString("qt")
    idVarTS        = TString("qf")

      
    # Data set
    #-----------------------
    nameData = TString("dataSet_time_")+part 
    data  = [] 
    dataW = []
    
    for i in range(0, bound):
        data.append(GeneralUtils.GetDataSet(workspace[i],   nameData, debug))
        dataW.append(GeneralUtils.GetDataSet(workspaceW[i],   nameData, debug))

    dataWA = dataW[0]    
    if BDTGbins:
        dataWA.append(dataW[1])
        dataWA.append(dataW[2])
           
    nEntries = dataWA.numEntries()    
        
    dataWA.Print("v")
    obs = dataWA.get()
    time = obs.find(tVar)
    terr = obs.find(terrVar)
    id = obs.find("qf")
    tag = obs.find("tagDecComb")
    mistag = obs.find("tagOmegaComb")
    mistag.setRange(0, 0.5)
    weight = obs.find("sWeights")
    observables = RooArgSet(time,tag,id)
        
    # Physical parameters
    #-----------------------
    
    mass = RooRealVar('mass', '%s mass' % bName, 5., 6.)
    
    gammas = RooRealVar('Gammas', '%s average lifetime' % bName, myconfigfile["Gammas"], 0., 5., 'ps^{-1}')
    gammas.setError(0.05)
    setConstantIfSoConfigured(gammas,myconfigfile)
    
    deltaGammas = RooRealVar('deltaGammas', 'Lifetime difference', myconfigfile["DeltaGammas"], -1., 1., 'ps^{-1}')
    setConstantIfSoConfigured(deltaGammas,myconfigfile)
    
    deltaMs = RooRealVar('deltaMs', '#Delta m_{s}', myconfigfile["DeltaMs"], 5., 30., 'ps^{-1}')
    setConstantIfSoConfigured(deltaMs,myconfigfile)

    # Decay time acceptance model
    # ---------------------------
         
    binName = TString("splineBinning")
    TimeBin = RooBinning(0.2,15,binName.Data())
    for i in range(0, myconfigfile["tacc_size"]):
        TimeBin.addBoundary(myconfigfile["tacc_knots"][i])
                
    
    TimeBin.removeBoundary(0.2)
    TimeBin.removeBoundary(15.0)
    TimeBin.removeBoundary(0.2)
    TimeBin.removeBoundary(15.0)
    TimeBin.Print("v")
    time.setBinning(TimeBin, binName.Data())
    time.setRange(0.2, 15.0)
    listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, time)
       
    tacc_list = RooArgList()
    tacc_var = []
    for i in range(0,myconfigfile["tacc_size"]):
        tacc_var.append(RooRealVar("var"+str(i+1), "var"+str(i+1), myconfigfile["tacc_values"][i]))
        print tacc_var[i].GetName()
        tacc_list.add(tacc_var[i])
    tacc_var.append(RooRealVar("var"+str(myconfigfile["tacc_size"]+1), "var"+str(myconfigfile["tacc_size"]+1), 1.0))
    len = tacc_var.__len__()
    tacc_list.add(tacc_var[len-1])
    print "n-2: ",tacc_var[len-2].GetName()
    print "n-1: ",tacc_var[len-1].GetName()
    tacc_var.append(RooAddition("var"+str(myconfigfile["tacc_size"]+2), "var"+str(myconfigfile["tacc_size"]+2),
                                RooArgList(tacc_var[len-2],tacc_var[len-1]), listCoeff))
    tacc_list.add(tacc_var[len])
    print "n: ",tacc_var[len].GetName()
                                                            
    spl = RooCubicSplineFun("splinePdf", "splinePdf", time, "splineBinning", tacc_list)
                                                                    
           
    # Decay time resolution model
    # ---------------------------
    if not pereventterr:
        trm = PTResModels.tripleGausEffModel( time,
                                              spl,
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
               
        trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["resolutionMeanBias"], 'ps' )
        trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', myconfigfile["resolutionScaleFactor"])
        trm = RooGaussEfficiencyModel("resmodel", "resmodel", time, spl, trm_mean, terr, trm_scale, trm_scale )
         
        terrWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["TerrFile"]), TString(myconfigfile["TerrWork"]), debug)
        terrpdf = []
        for i in range(0,bound):
            terrpdf.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(terrWork, TString(myconfigfile["TerrTempName"]), debug))
            

    # Tagging
    # -------
    tagEffSigList = RooArgList()
    tagEffSig = []
    for i in range(0,3):
        tagEffSig.append(RooRealVar('tagEffSig_'+str(i+1), 'Signal tagging efficiency', myconfigfile["TagEffSig"][i]))
        print tagEffSig[i].GetName()
        tagEffSigList.add(tagEffSig[i])
    #setConstantIfSoConfigured(tagEffSig,myconfigfile)
                                     
    # Per-event mistag
    # ---------------------------
        
    if pereventmistag :
        mistagCalibList = RooArgList()
        for i in range(0, 3):
            mistagCalibList.add(mistag)
            
        #mistagPDF = SFitUtils.CreateMistagTemplates(dataWA,MDSettings,50,true, debug)
        mistagWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["MistagFile"]), TString(myconfigfile["MistagWork"]), debug)
        mistagPDF = []
        mistagPDFList = RooArgList()
        for i in range(0,3):
            mistagPDF.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(mistagWork, TString(myconfigfile["MistagTempName"][i]), debug))
            mistagPDFList.add(mistagPDF[i])
                                                                                  
        observables.add( mistag )
                                
        # we need calibrated mistag
        #calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"]) #, 0.90, 1.5)
        #calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"]) #, 0.25, 0.5)
        #avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"]) #, 0.2, 0.6)
        
        #mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
        #                                     mistag, calibration_p0,calibration_p1,avmistag)
        #observables.add( mistag )
        #name = TString("sigMistagPdf")
        #mistagPDF  = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(templateWorkspaceK, TString(myconfigfile["MistagTemplateName"]), debug)
        #mistagPDF = GeneralUtils.CreateHistPDF(dataWA, mistag, name, myconfigfile['nBinsMistag'], debug)

    else:
        mistagHistPdf = None
        mistagCalibrated =  mistag
            

    # CP observables
    # ---------------------------
        
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

    # Production, detector and tagging asymmetries
    # ---------------------------

    aProd = zero     # production asymmetry
    aDet = zero      # detector asymmetry

    aTagEffSig = []
    aTagEffSigList = RooArgList()
    for i in range(0,3):
        aTagEffSig.append(RooRealVar('aTagEff_'+str(i+1), 'atageff', myconfigfile["aTagEffSig"][i]))
        print aTagEffSig[i].GetName()
        aTagEffSigList.add(aTagEffSig[i])
        

    # Coefficient in front of sin, cos, sinh, cosh
    # --------------------------------------------
        
    one1 = RooConstVar('one1', '1', 1.)
    one2 = RooConstVar('one2', '1', 1.)
        
    if pereventmistag:
        otherargs = [ mistag, mistagPDFList, tagEffSigList ]
    else:
        otherargs = [ tagEffSigList ]
    otherargs.append(mistagCalibList)
    otherargs.append(aProd)
    otherargs.append(aDet)
    otherargs.append(aTagEffSigList)

    flag = 0 #DecRateCoeff.AvgDelta
    
    cosh = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven, id, tag, one1, one2, *otherargs)
    sinh = DecRateCoeff('signal_sinh', 'signal_sinh', flag | DecRateCoeff.CPEven, id, tag, sigD, sigDbar, *otherargs)
    cos  = DecRateCoeff('signal_cos' , 'signal_cos' , DecRateCoeff.CPOdd, id, tag, sigC, sigC, *otherargs)
    sin  = DecRateCoeff('signal_sin' , 'signal_sin' , flag | DecRateCoeff.CPOdd | DecRateCoeff.Minus, id, tag, sigS, sigSbar, *otherargs)
        
    # Set the signal handler and a 5-second alarm
    #signal.signal(signal.SIGALRM, handler)
    #signal.alarm(120)

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
    

    # Total time PDF
    # ---------------------------
        
    tauinv          = Inverse( "tauinv","tauinv", gammas)
      
    timePDF = []
    for i in range(0,bound):
        name_time = TString("time_signal_")+Bin[i]
        timePDF.append(RooBDecay(name_time.Data(),name_time.Data(), time, tauinv, deltaGammas,
                                 cosh, sinh, cos, sin,
                                 deltaMs, trm, RooBDecay.SingleSided))
        
        
    if pereventterr:
        noncondset = RooArgSet(time, id, tag)
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


    # Fitting
    # ---------------------------
        
    if toys or not Blinding: #Unblind yourself
        if BDTGbins or Cat:
            myfitresult = pdf.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                    RooFit.Verbose(False), RooFit.SumW2Error(True))
            
        else:
            myfitresult = totPDF[0].fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                       RooFit.Verbose(False), RooFit.SumW2Error(True))
            
        myfitresult.Print("v")
        myfitresult.correlationMatrix().Print()
        myfitresult.covarianceMatrix().Print()
    else :    #Don't
        if BDTGbins or Cat:
            myfitresult = pdf.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                    RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            
        else:
            myfitresult = totPDF[0].fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
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
        getattr(workout,'import')(dataWA)
        getattr(workout,'import')(totPDF[0])
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
                                     options.pereventterr,
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

