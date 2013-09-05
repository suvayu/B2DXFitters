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
ROOT.gROOT.SetBatch()

from optparse import OptionParser
from math     import pi

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------


# MODELS
#AcceptanceFunction       =  'BdPTAcceptance'  # None/BdPTAcceptance/DTAcceptanceLHCbNote2007041
AcceptanceFunction       =  'PowLawAcceptance'

# BLINDING
Blinding =  True

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
def runBdGammaFitterOnData(debug, wsname, initvars, var, terrvar, probvar,pereventmistag, toys,pathName,
                           treeName,splitCharge,fitMeTool,configName,nokfactcorr,
                           smearaccept, accsmearfile, accsmearhist,
                           BDTGbins, pathName2, pathName3, Cat) :

    if not Blinding and not toys :
        print "RUNNING UNBLINDED!"
        really = input('Do you really want to unblind? ')
        if really != "yes" :
            exit(-1)

    #if toys :
    #    if int(pathToys.split('.')[1].split('_')[-1]) in bannedtoys :
    #        exit(-1)

    from B2DXFitters import taggingutils, cpobservables
    GeneralModels = ROOT.GeneralModels
    PTResModels   = ROOT.PTResModels

    GeneralUtils = ROOT.GeneralUtils
    SFitUtils = ROOT.SFitUtils
     
    Bs2Dsh2011TDAnaModels = ROOT.Bs2Dsh2011TDAnaModels
    
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay
    from ROOT import RooGaussModel, RooTruthModel,RooUnblindUniform
    from ROOT import RooAbsReal, RooDataSet, RooGaussModel
    from ROOT import RooAbsPdf, RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooSimultaneous, RooBinnedPdf
    from ROOT import RooExponential, RooPolynomial, RooPolyVar, RooUniform, RooEffResModel, RooHistPdf
    from ROOT import RooFit, RooBDecay, RooEffProd
    from ROOT import FitMeTool, IfThreeWay, Dilution, IfThreeWayPdf
    from ROOT import CombBkgPTPdf, TagEfficiencyWeightNoCat
    from ROOT import BdPTAcceptance, TagEfficiencyWeight,PowLawAcceptance
    from ROOT import TString, Inverse, IfThreeWayCat,MistagCalibration
    from ROOT import RooUnblindCPAsymVar, RooUnblindPrecision, RooWorkspace
    from ROOT import RooNLLVar, RooMinuit, RooProfileLL, kRed, kBlue, kGreen, kOrange, TCanvas, gStyle 
    from ROOT import TFile,TTree,RooDataHist,RooHistFunc  
    from ROOT import RooBinned1DQuinticBase, DecRateCoeff
 
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
    #RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    #RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    #RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    #RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','20Points')
    #RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)

    tVarTS         = TString(var)
    terrVarTS      = TString(terrvar)
    tProbVarTS     = TString(probvar)
    tagVarTS       = TString("lab0_BsTaggingTool_TAGDECISION_OS")       
    tagWeightVarTS = TString("lab0_BsTaggingTool_TAGOMEGA_OS")
    idVarTS        = TString("lab1_ID")

    if BDTGbins:
        if (toys) :
            applykfactor = (not nokfactcorr)
        else :
            applykfactor = False
        workspace = SFitUtils.ReadDataFromSWeights(TString("DsK"),TString(pathName), TString(treeName),
                                                    myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                    tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, 
                                                    False, debug, applykfactor)
                   
        workspace2 = SFitUtils.ReadDataFromSWeights(TString("DsK"),TString(pathName2), TString(treeName),
                                                    myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                    tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, 
                                                    False, debug, applykfactor)
        
        workspace3 = SFitUtils.ReadDataFromSWeights(TString("DsK"),TString(pathName3), TString(treeName),
                                                    myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                    tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, 
                                                    False, debug, applykfactor)

        workspaceW = SFitUtils.ReadDataFromSWeights(TString("DsK"),TString(pathName), TString(treeName),
                                                    myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                    #time, tag, mistag, id,
                                                    tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, 
                                                    True, debug, applykfactor)
        
        workspace2W = SFitUtils.ReadDataFromSWeights(TString("DsK"),TString(pathName2), TString(treeName),
                                                     myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                     tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, 
                                                     True, debug, applykfactor)
        
        workspace3W = SFitUtils.ReadDataFromSWeights(TString("DsK"),TString(pathName3), TString(treeName),
                                                     myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                     tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, 
                                                     True, debug, applykfactor)
                    
    else:
        if (toys) :
            applykfactor = (not nokfactcorr)
        else :
            applykfactor = False
        workspace = SFitUtils.ReadDataFromSWeights(TString("DsK"),TString(pathName), TString(treeName),
                                                   myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                   tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, 
                                                   False, debug, applykfactor)

        workspaceW = SFitUtils.ReadDataFromSWeights(TString("DsK"),TString(pathName), TString(treeName),
                                                    myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                    tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, 
                                                    True, debug, applykfactor)
   
    workspace.Print()
        
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
    if BDTGbins:
        data   = GeneralUtils.GetDataSet(workspace,   nameData, debug)
        data2  = GeneralUtils.GetDataSet(workspace2,  nameData, debug)
        data3  = GeneralUtils.GetDataSet(workspace3,  nameData, debug)
        data1W = GeneralUtils.GetDataSet(workspaceW,  nameData, debug)
        data2W = GeneralUtils.GetDataSet(workspace2W, nameData, debug)
        data3W = GeneralUtils.GetDataSet(workspace3W, nameData, debug)
        dataWW = [data1W, data2W, data3W]
        dataW  = GeneralUtils.GetDataSet(workspaceW,  nameData, debug)
        dataW.append(data2W)
        dataW.append(data3W)
    else:
        data  = GeneralUtils.GetDataSet(workspace, nameData, debug)
        dataW = GeneralUtils.GetDataSet(workspaceW, nameData, debug)
                    
    nEntries = data.numEntries()    
        
    dataW.Print("v")
    obs = data.get()
    time = obs.find(tVarTS.Data())
    mistag = obs.find(tagWeightVarTS.Data())
    fChargeMap = obs.find(idVarTS.Data())
    bTagMap = obs.find(tagVarTS.Data())
    terr = obs.find(terrVarTS.Data())
    observables = RooArgSet(time,bTagMap,fChargeMap)

    if debug:
        frame = time.frame()
        sliceData_1 = dataW.reduce(RooArgSet(time,fChargeMap,bTagMap),"(qt == 0)")
        sliceData_1.plotOn(frame,RooFit.MarkerColor(kRed))
        print "Untagged: number of events: %d, sum of events: %d"%(sliceData_1.numEntries(),sliceData_1.sumEntries())
        sliceData_2 = dataW.reduce(RooArgSet(time,fChargeMap,bTagMap),"(qt == 1)")
        print "Bs tagged: number of events: %d, sum of events: %d"%(sliceData_2.numEntries(),sliceData_2.sumEntries())
        sliceData_2.plotOn(frame,RooFit.MarkerColor(kBlue+2))
        sliceData_3 = dataW.reduce(RooArgSet(time,fChargeMap,bTagMap),"(qt == -1)")
        sliceData_3.plotOn(frame,RooFit.MarkerColor(kOrange+2))
        print "barBs tagged: number of events: %d, sum of events: %d"%(sliceData_3.numEntries(),sliceData_3.sumEntries())        
        dataW.plotOn(frame)
        canvas = TCanvas("canvas", "canvas", 1200, 1000)
        canvas.cd()
        frame.Draw()
        frame.GetYaxis().SetRangeUser(0.1,150)
        canvas.GetPad(0).SetLogy()
        canvas.SaveAs('data_time_DsK.pdf')

    templateWorkspacePi = GeneralUtils.LoadWorkspace(TString(myconfigfile["TemplateFilePi"]), TString(myconfigfile["TemplateWorkspace"]), debug)
    templateWorkspaceK = GeneralUtils.LoadWorkspace(TString(myconfigfile["TemplateFileK"]), TString(myconfigfile["TemplateWorkspace"]), debug)

    if BDTGbins:
        Bin = [TString("BDTG1"), TString("BDTG2"), TString("BDTG3")]
    else:
        Bin = [TString("BDTGA")]
        
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
        
        if BDTGbins:
            terrpdf = []
            for i in range(0,3):
                name = TString("sigTimeErrorPdf_%s")+Bin[i]
                terrpdf.append(GeneralUtils.CreateHistPDF(dataWW[i], terr, name, myconfigfile['nBinsProperTimeErr'], debug))
                
        else:
            name = TString("sigTimeErrorPdf")
            terrpdf = GeneralUtils.CreateHistPDF(dataW, terr, name, myconfigfile['nBinsProperTimeErr'], debug)
            #terrpdf  = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(templateWorkspaceK, TString(myconfigfile["TimeErrorTemplateBDTGA"]),debug)
        
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

            if BDTGbins:
                tacc_beta = []
                tacc_exponent = []
                tacc_offset = []
                tacc_turnon = []
                tacc = []
                
                for i in range(0,3):
                    name_beta = TString("tacc_beta_")+Bin[i]
                    tacc_beta.append(RooRealVar(name_beta.Data(), name_beta.Data(), myconfigfile[name_beta.Data()],  0.00 , 0.15))
                    name_exponent = TString("tacc_exponent_")+Bin[i]
                    tacc_exponent.append(RooRealVar(name_exponent.Data(), name_exponent.Data(), myconfigfile[name_exponent.Data()], 1.00 , 4.00))
                    name_offset = TString("tacc_offset_")+Bin[i]
                    tacc_offset.append(RooRealVar(name_offset.Data(), name_offset.Data(), myconfigfile[name_offset.Data()], -0.2 , 0.10))
                    name_turnon = TString("tacc_turnon_")+Bin[i]
                    tacc_turnon.append(RooRealVar(name_turnon.Data(), name_turnon.Data(), myconfigfile[name_turnon.Data()], 0.50 , 5.00))
                    name_tacc = TString("BsPowLawAcceptance_")+Bin[i]
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
                        
                        
            else:
                tacc_beta       = RooRealVar('tacc_beta'    , 'PowLawAcceptance_beta',      myconfigfile["tacc_beta"]       , 0.00 , 0.05) 
                tacc_exponent   = RooRealVar('tacc_exponent', 'PowLawAcceptance_exponent',  myconfigfile["tacc_exponent"]   , 1.00 , 4.00)
                tacc_offset     = RooRealVar('tacc_offset'  , 'PowLawAcceptance_offset',    myconfigfile["tacc_offset"]     , -0.2 , 0.10)
                tacc_turnon     = RooRealVar('tacc_turnon'  , 'PowLawAcceptance_turnon',    myconfigfile["tacc_turnon"]     , 0.50 , 5.00)  
                accratio.Print("v") 
                if smearaccept :
                    tacc = PowLawAcceptance('BsPowLawAcceptance', '%s decay time acceptance function' % bName,
                                            tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta,accratio)
                else :
                    tacc = PowLawAcceptance('BsPowLawAcceptance', '%s decay time acceptance function' % bName,
                                            tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta)
                setConstantIfSoConfigured(tacc_beta,myconfigfile)
                setConstantIfSoConfigured(tacc_exponent,myconfigfile)
                setConstantIfSoConfigured(tacc_offset,myconfigfile)
                setConstantIfSoConfigured(tacc_turnon,myconfigfile)
    else :
        tacc = None

    # Bin acceptance
    if myconfigfile["nBinsAcceptance"] > 0:
        # provide binning for acceptance
        from ROOT import RooUniformBinning
        acceptanceBinning = RooUniformBinning(time.getMin(), time.getMax(), myconfigfile["nBinsAcceptance"],'acceptanceBinning')
        time.setBinning(acceptanceBinning, 'acceptanceBinning')
        if BDTGbins:
            acceptance = []
            timeresmodel = []
            for i in range(0,3):
                acceptance.append(RooBinnedPdf("%sBinned"%tacc[i].GetName(),"%sBinnedA"%tacc[i].GetName(), time, 'acceptanceBinning', tacc[i]))
                acceptance[i].setForceUnitIntegral(True)
                timeresmodel.append(RooEffResModel("%s_timeacc_%s"% (trm.GetName(), acceptance[i].GetName()),
                                                   "trm plus acceptance", trm, acceptance[i]))
        else:
            acceptance = RooBinnedPdf("%sBinned" % tacc.GetName(),  "%sBinnedA" % tacc.GetName(), time, 'acceptanceBinning', tacc)
            acceptance.setForceUnitIntegral(True)
            timeresmodel = RooEffResModel("%s_timeacc_%s"% (trm.GetName(), acceptance.GetName()),"trm plus acceptance", trm, acceptance)
            
       
        
    if 'PEDTE' in myconfigfile["DecayTimeResolutionModel"] and 0 != myconfigfile['nBinsProperTimeErr']:
        if debug:
            print "Set binning for time error: %d"%(myconfigfile['nBinsProperTimeErr'])
        terr.setBins(myconfigfile['nBinsProperTimeErr'], 'cache')
        if BDTGbins:
            for i in range(0,3):
                timeresmodel[i].setParameterizeIntegral(RooArgSet(terr))
        else:
            timeresmodel.setParameterizeIntegral(RooArgSet(terr))
                                                
    if pereventmistag :
        # we need calibrated mistag
        calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"]) #, 0.90, 1.5)
        calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"]) #, 0.25, 0.5)
        avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"]) #, 0.2, 0.6)
        
        mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
                                             mistag, calibration_p0,calibration_p1,avmistag)
        observables.add( mistag )
        name = TString("sigMistagPdf")
        mistagPDF  = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(templateWorkspacePi, TString(myconfigfile["MistagTemplateName"]), debug)
        #mistagPDF = GeneralUtils.CreateHistPDF(dataW, mistag, name, myconfigfile['nBinsMistag'], debug)

    else:
        mistagHistPdf = None
        mistagCalibrated =  mistag
        

    #sigTagWeight = TagEfficiencyWeight('sTagEffWeight','tag efficiency weight', bTagMap,tagEffSig)

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
    
    if not splitCharge and not fitMeTool:
          
        #if debug :
        #    print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!' 
        #    data.Print("v")
        #    for i in range(0,nEntries) : 
        #        data.get(i).Print("v")
        #        print data.weight()
    
        tauinv          = Inverse( "tauinv","tauinv", gammas)
        #time_noacc      = RooBDecay('time_signal_noacc','time_signal_noacc', time, tauinv, deltaGammas, 
        #                                    sigCosh, sigSinh,sigCos, sigSin,
        #                                    deltaMs,trm, RooBDecay.SingleSided)

        '''
        bTagMap.setBins(5,'cache')
        fChargeMap.setBins(5,'cache')
        mistag.setBins(6,'cache')
        time_noacc.setParameterizeIntegral(RooArgSet(mistag))
        '''   
        #sigTimePDF      = RooEffProd('time_signal','time_signal',time_noacc,tacc)
        '''
        if debug :
            print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!'
            data.Print("v")
            for i in range(0,nEntries) :
                obs = data.get(i)
                obs.Print("v")
                #data.get(i).Print("v")
                print data.weight()
                print cos.getValV(obs)
                print sin.getValV(obs)
                print cosh.getValV(obs)
                print sinh.getValV(obs)
        '''                                                                                                                

        if BDTGbins:
            timePDF = []
            for i in range(0,3):
                name_time = TString("time_signal_")+Bin[i]
                timePDF.append(RooBDecay(name_time.Data(),name_time.Data(), time, tauinv, deltaGammas,
                                         cosh, sinh, cos, sin,
                                         deltaMs, timeresmodel[i], RooBDecay.SingleSided))
                
        else:
            timePDF = RooBDecay('time_signal','time_signal', time, tauinv, deltaGammas,
                                 cosh, sinh, cos, sin,
                                 deltaMs, timeresmodel, RooBDecay.SingleSided)
             
        
        
        if 'PEDTE' in myconfigfile["DecayTimeResolutionModel"]:
            noncondset = RooArgSet(time, fChargeMap, bTagMap)
            if pereventmistag:
                noncondset.add(mistag)
            if BDTGbins:
                totPDF = []
                for i in range(0,3):
                    name_timeterr = TString("signal_TimeTimeerrPdf_")+Bin[i]
                    totPDF.append(RooProdPdf(name_timeterr.Data(), name_timeterr.Data(),
                                             RooArgSet(terrpdf[i]), RooFit.Conditional(RooArgSet(timePDF[i]), noncondset)))
                    
            else:
                totPDF = RooProdPdf('signal_TimeTimeerrPdf', 'signal_TimeTimerrPdf', 
                                    RooArgSet(terrpdf), RooFit.Conditional(RooArgSet(timePDF), noncondset))
                
        else:
            if BDTGbins:
                totPDF = []
                for i in range(0,3):
                    totPDF.append(timePDF)
                                        
            else:
                totPDF  = timePDF
        if Cat:
            if BDTGbins:
                BdtgBin = RooCategory("bdtgbin","bidtgbin")
                for i in range(0,3):
                    BdtgBin.defineType(Bin[i].Data())

                weight = obs.find("sWeights")
                observables.add( weight )
                
                combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                      RooFit.Index(BdtgBin),
                                      RooFit.Import(Bin[0].Data(),data),
                                      RooFit.Import(Bin[1].Data(),data2),
                                      RooFit.Import(Bin[2].Data(),data3),
                                      RooFit.WeightVar("sWeights"))
                                  #RooFit.SumW2Error(True))
            
                totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
                totPDFSim.addPdf(totPDF[0],  Bin[0].Data())
                totPDFSim.addPdf(totPDF[1], Bin[1].Data())
                totPDFSim.addPdf(totPDF[2], Bin[2].Data())
            else:
                BdtgBin = RooCategory("bdtgbin","bidtgbin")
                BdtgBin.defineType(Bin[0].Data())

                weight = obs.find("sWeights")
                observables.add( weight )
                
                combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                      RooFit.Index(BdtgBin),
                                      RooFit.Import(Bin[0].Data(),data),
                                      RooFit.WeightVar("sWeights"))
                                  #RooFit.SumW2Error(True))
                
                totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
                totPDFSim.addPdf(totPDF,  Bin[0].Data())
                           
            pdf = RooAddPdf('totPDFtot', 'totPDFtot', RooArgList(totPDFSim), RooArgList())
            
        if toys or not Blinding: #Unblind yourself
            if BDTGbins or Cat:
                myfitresult = pdf.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                        RooFit.Verbose(False), RooFit.SumW2Error(True))
                
            else:
                myfitresult = totPDF.fitTo(dataW, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                           RooFit.Verbose(False), RooFit.SumW2Error(True))
                
            myfitresult.Print("v")
            myfitresult.correlationMatrix().Print()
            myfitresult.covarianceMatrix().Print()
        else :    #Don't
            if BDTGbins or Cat:
                myfitresult = totPDFSim.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                              RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
                
            else:
                myfitresult = totPDF.fitTo(dataW, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                           RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
                    
            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 
            par[1].Print("v")
            par[2].Print("v")
            par[3].Print("v")
            par[4].Print("v")
            if  (sigS.getVal() < param_limits["lower"] + sigS.getError() ) or \
                (sigS.getVal() > param_limits["upper"] - sigS.getError() ) :
                print "S IS CLOSE TO THE FIT LIMITS!!!!"       
            if  (sigSbar.getVal() < param_limits["lower"] + sigSbar.getError() ) or \
                (sigSbar.getVal() > param_limits["upper"] - sigSbar.getError() ) : 
                print "Sbar IS CLOSE TO THE FIT LIMITS!!!!"
            if  (sigD.getVal() < param_limits["lower"] + sigD.getError() ) or \
                (sigD.getVal() > param_limits["upper"] - sigD.getError() ) : 
                print "D IS CLOSE TO THE FIT LIMITS!!!!"       
            if  (sigDbar.getVal() < param_limits["lower"] + sigDbar.getError() ) or \
                (sigDbar.getVal() > param_limits["upper"] - sigDbar.getError() ) :
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
                
    elif not splitCharge :   
        sigCosh         = RooProduct('sigCosh',      'cosh coefficient', RooArgSet(untaggedWeight, sigTagWeight)        )   
        sigSinh         = RooProduct('sigSinh',      'sinh coefficient', RooArgSet(sigCosh, sigWeightedDs)              )   
        sigCos          = RooProduct('sigCos',       'cos coefficient',  RooArgSet(sigCosSin_i0, sigC)                  )   
        sigSin          = RooProduct('sigSin',       'sin coefficient',  RooArgSet(sigCosSin_i0, sigWeightedSs)         )
               
        if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
            sigTimePDF = GeneralModels.buildRooBDecayPDF(
                time, gammas, deltaGammas, deltaMs,
                sigCosh, sigSinh, sigCos, sigSin,
                trm, tacc,
                'Sig', bName, debug)
        else :
            sigTimePDF = GeneralModels.buildRooBDecayPDFWithPEDTE(
                time, timeerr, gammas, deltaGammas, deltaMs,
                sigCosh, sigSinh, sigCos, sigSin,
                terrpdf, trm, tacc,
                'Sig', bName, debug)
       
        totPDF = sigTimePDF               
        fitter = FitMeTool(debug)
    
        fitter.setObservables(observables)
        fitter.setModelPDF(totPDF)
        fitter.setData(data)
      
        s1=TString("comb")
        mode = TString("time_BsDsK")
        GeneralUtils.SaveDataSet(data, time, s1, mode, debug);
       
        plot_init   = (wsname != None) and initvars
        plot_fitted = (wsname != None) and (not initvars)
    
        if plot_init :
            fitter.saveModelPDF(wsname)
            fitter.saveData(wsname)
       
        if toys or not Blinding: #Unblind yourself
            fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2), RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult = fitter.getFitResult()
            myfitresult.Print("v")
        else :    #Don't
            fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            myfitresult = fitter.getFitResult()
            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 
            par[1].Print("v")
            par[2].Print("v")
            par[3].Print("v")
            par[4].Print("v")        

        workout = RooWorkspace("workspace","workspace")
        getattr(workout,'import')(data)
        getattr(workout,'import')(totPDF)
        getattr(workout,'import')(myfitresult)
        workout.writeToFile("WS_Time_DsK.root")
                               
        if not toys and plot_fitted :
            fitter.saveModelPDF(wsname)
            fitter.saveData(wsname)
         
        del fitter
    else : #if we are splitting by charge
        sigCosh_pos         = RooProduct('sigCosh_pos',      'cosh coefficient', RooArgSet(untaggedWeight, sigTagWeight) )
        sigSinh_pos         = RooProduct('sigSinh_pos',      'sinh coefficient', RooArgSet(sigCosh_pos, sigD)         )
        sigCos_pos          = RooProduct('sigCos_pos',       'cos coefficient',  RooArgSet(sigCosSin_i0, sigC)        )
        sigSin_pos          = RooProduct('sigSin_pos',       'sin coefficient',  RooArgSet(sigCosSin_i0, sigS)        )
    
        sigCosh_neg         = RooProduct('sigCosh_neg',      'cosh coefficient', RooArgSet(untaggedWeight, sigTagWeight) )
        sigSinh_neg         = RooProduct('sigSinh_neg',      'sinh coefficient', RooArgSet(sigCosh_neg, sigDbar)      )
        sigCos_neg          = RooProduct('sigCos_neg',       'cos coefficient',  RooArgSet(sigCosSin_i0, sigCbar)     )
        sigSin_neg          = RooProduct('sigSin_neg',       'sin coefficient',  RooArgSet(sigCosSin_i0, sigSbar)     )

        if debug :
            print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!'
            data_pos.Print("v")
            for i in range(0,nEntries_pos) :
                data_pos.get(i).Print("v")
                print data_pos.weight()
            data_neg.Print("v")
            for i in range(0,nEntries_neg) :
                data_neg.get(i).Print("v")
                print data_neg.weight()
    
        tauinv          = Inverse( "tauinv","tauinv", gammas)
        trm             = RooGaussModel('PTRMGaussian_signal','PTRMGaussian_signal',time, zero, timeerravg)
        
        time_noacc_pos  = RooBDecay('time_signal_noacc_pos','time_signal_noacc', time, tauinv, deltaGammas,
                                            sigCosh_pos, sigSinh_pos,sigCos_pos, sigSin_pos, deltaMs,trm, RooBDecay.SingleSided)
        sigTimePDF_pos  = RooEffProd('time_signal','time_signal',time_noacc_pos,tacc)
        totPDF_pos      = sigTimePDF_pos
        
        time_noacc_neg  = RooBDecay('time_signal_noacc_neg','time_signal_noacc', time, tauinv, deltaGammas,
                                            sigCosh_neg, sigSinh_neg,sigCos_neg, sigSin_neg, deltaMs,trm, RooBDecay.SingleSided)
        sigTimePDF_neg  = RooEffProd('time_signal','time_signal',time_noacc_neg,tacc)
        totPDF_neg      = sigTimePDF_neg

        if toys or not Blinding: #Unblind yourself
            myfitresult_pos = totPDF_pos.fitTo(data_pos, RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                                         RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult_pos.Print("v")
            myfitresult_neg = totPDF_neg.fitTo(data_neg, RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                                         RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult_neg.Print("v")
        else :    #Don't
            myfitresult_pos = totPDF.fitTo(data_pos,  RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                                      RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            myfitresult_neg = totPDF.fitTo(data_neg,  RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                                      RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            print 'Matrix quality pos is',myfitresult_pos.covQual()
            par_pos = myfitresult_pos.floatParsFinal()
            par_pos[0].Print("v")
            par_pos[1].Print("v")
            par_pos[2].Print("v")

            print 'Matrix quality neg is',myfitresult_neg.covQual()
            par_neg = myfitresult_neg.floatParsFinal()
            par_neg[0].Print("v")
            par_neg[1].Print("v")
            par_neg[2].Print("v")

        workout = RooWorkspace("workspace","workspace")
        getattr(workout,'import')(data)
        getattr(workout,'import')(totPDF)
        getattr(workout,'import')(myfitresult)
        workout.writeToFile(wsname)
                         
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
parser.add_option('-i', '--initial-vars',
                  dest    = 'initvars',
                  default = False,
                  action  = 'store_true',
                  help    = 'save the model PDF parameters before the fit (default: after the fit)'
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
parser.add_option( '-c', '--cutvariable',
                   dest = 'ProbVar',
                   default = 'lab1_PIDK',
                   help = 'set observable for PID '
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

parser.add_option( '--splitCharge',
                   dest = 'splitCharge',
                   action = 'store_true',
                   default = False) 

parser.add_option( '--fitMeTool',
                    dest = 'fitMeTool',
                    action = 'store_true',
                    default = False)

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
    sys.path.append("../../data/")
    sys.path.append("../data")
    
    totPDF = runBdGammaFitterOnData( options.debug,
                                     options.wsname,
                                     options.initvars,
                                     options.tvar,
                                     options.terrvar,
                                     options.ProbVar,
                                     options.pereventmistag,
                                     options.toys,
                                     options.pathName,
                                     options.treeName,
                                     options.splitCharge,
                                     options.fitMeTool,
                                     options.configName,
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

