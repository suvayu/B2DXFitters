#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to prepare a mass fit on data for Bd -> D pi                    #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python prepareBdMassFitterOnData.py [-d | --debug]                         #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 08 / 06 / 2011                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 02 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from os.path  import join

import GaudiPython

GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import *
GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils
WeightingUtils = GaudiPython.gbl.WeightingUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels


# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------
saveName      = 'work_'
#------------------------------------------------------------------------------
def prepareBsDsPiMassFitterOnData( debug, mVar, tVar, tagVar, tagOmegaVar, idVar, mdVar, mProbVar, save, OmegaPdf, TagTool, configName,
                                   Data, DPi, DPiPID, MC, MCPID, Signal, SignalPID, CombPID) :

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
    

    #dataTS = TString(dataName)
    mVarTS = TString(mVar)
    tVarTS = TString(tVar)
    tagVarTS = TString(tagVar)
    tagOmegaVarTS = TString(tagOmegaVar)
    idVarTS = TString(idVar)
    mProbVarTS = TString(mProbVar)
    mdVarTS = TString(mdVar)

    if ( OmegaPdf == "no" ):
        tagOmega = false
    else:
        tagOmega = true

    if ( TagTool == "no"):
        tagTool = false
    else:
        tagTool = true
    dataTS  = TString(myconfigfile["dataName"])

    workspace = RooWorkspace("workspace","workspace")

    if Data:
        workspace = MassFitUtils.ObtainData(dataTS, TString("#BsDsPi KKPi NonRes"),
                                            myconfigfile["PIDBach"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDownData"], myconfigfile["BMassUpData"],
                                            myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                            mVarTS, mdVarTS, tVarTS, tagVarTS,
                                            tagOmegaVarTS, idVarTS, 
                                            mProbVarTS,
                                            TString("BsDsPi"), tagTool, NULL, debug)
        
        workspace = MassFitUtils.ObtainData(dataTS,TString("#BsDsPi KKPi PhiPi"),
                                            myconfigfile["PIDBach"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDownData"], myconfigfile["BMassUpData"],
                                            myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                            mVarTS, mdVarTS, tVarTS, tagVarTS,
                                            tagOmegaVarTS, idVarTS,
                                            mProbVarTS,
                                            TString("BsDsPi"), tagTool, workspace, debug)
        
        workspace = MassFitUtils.ObtainData(dataTS,TString("#BsDsPi KKPi KstK"),
                                            myconfigfile["PIDBach"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDownData"], myconfigfile["BMassUpData"],
                                            myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                            mVarTS, mdVarTS, tVarTS, tagVarTS,
                                            tagOmegaVarTS, idVarTS,
                                            mProbVarTS,
                                            TString("BsDsPi"), tagTool, workspace, debug)
        
        workspace = MassFitUtils.ObtainData(dataTS,TString("#BsDsPi KPiPi"),
                                            myconfigfile["PIDBach"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDownData"], myconfigfile["BMassUpData"],
                                            myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                            mVarTS, mdVarTS, tVarTS, tagVarTS,
                                            tagOmegaVarTS, idVarTS,
                                            mProbVarTS,
                                            TString("BsDsPi"), tagTool, workspace, debug)
        
        
        workspace = MassFitUtils.ObtainData(dataTS,TString("#BsDsPi PiPiPi"),
                                            myconfigfile["PIDBach"],
                                            myconfigfile["PDown"], myconfigfile["PUp"],
                                            myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                            myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                            myconfigfile["BMassDownData"], myconfigfile["BMassUpData"],
                                            myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                            mVarTS, mdVarTS, tVarTS, tagVarTS,
                                            tagOmegaVarTS, idVarTS,
                                            mProbVarTS,
                                            TString("BsDsPi"),tagTool, workspace, debug)
        
    
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    #exit(0)
    
    if DPi:
        workspace = MassFitUtils.ObtainMissForBsDsPi(dataTS,TString("#BdPi"),
                                                     TString("nonres"), #myconfigfile["PIDChild"], 
                                                     myconfigfile["PDown"], myconfigfile["PUp"],
                                                     myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                     myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                     myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                     myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                     myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                     mVarTS, mdVarTS, mProbVarTS,
                                                     TString("Bd2DPi"),workspace, tagOmega, debug)
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)

    if DPiPID:
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("DPi Down"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                          TString("DPi Pion Down"),
                                                                          workspace, debug)
                                                                          
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)

    if DPiPID:
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]), 
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("DPi Up"),
                                                            workspace, workspace, debug)
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("DPi Pion Up"),
                                                                          workspace, debug)
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    
    
    if MC:
        workspace = MassFitUtils.ObtainSpecBack(dataTS, TString("#MC FileName MD"), TString("#MC TreeName"),
                                                myconfigfile["PIDBach2"], myconfigfile["PIDChild"], myconfigfile["PIDProton"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsPi"),
                                                workspace, false, tagOmega, debug)
        
        workspace = MassFitUtils.ObtainSpecBack(dataTS, TString("#MC FileName MU"), TString("#MC TreeName"),
                                                myconfigfile["PIDBach2"], myconfigfile["PIDChild"], myconfigfile["PIDProton"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsPi") ,
                                                workspace, false, tagOmega, debug)
                                            
    
        workspace = MassFitUtils.CreatePdfSpecBackground(dataTS, TString("#MC FileName MD"),
                                                         dataTS, TString("#MC FileName MU"),
                                                         mVarTS, mdVarTS,
                                                         myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                         myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                         workspace, tagOmega, debug)
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
          
    
    if MCPID:
        workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MD"),
                                                   TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                   myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                   TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                   myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                   myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                   TString("MC BsDsPi Pion"),
                                                   workspace, debug)
        workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MU"),
                                                   TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                   myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                   TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                   myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                   myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                   TString("MC BsDsPi Pion"),
                                                   workspace, debug)
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        
        workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MD"),
                                                   TString(myconfigfile["fileCalibKaonDown"]), TString(myconfigfile["workCalib"]),
                                                   myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                   TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]), 
                                                   myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                   myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                   TString("MC BsDsPi Kaon"),
                                                   workspace, debug)
        workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MU"),
                                                   TString(myconfigfile["fileCalibKaonUp"]), TString(myconfigfile["workCalib"]),
                                                   myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                   TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                   myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                   myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                   TString("MC BsDsPi Kaon"),
                                                   workspace, debug)
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString("#MC FileName MD"),
                                                                 TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                                 mProbVarTS,
                                                                 TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]), 
                                                                 myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                 myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                 myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                 myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                 TString("MC BsDsPi Pion"),
                                                                 workspace, debug)
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString("#MC FileName MU"),
                                                                 TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                                 mProbVarTS,
                                                                 TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]), 
                                                                 myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                 myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                 myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                 myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                 TString("MC BsDsPi Pion"),
                                                                 workspace, debug)
    
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString("#MC FileName MD"),
                                                                 TString(myconfigfile["fileCalibKaonDown"]), TString(myconfigfile["workCalib"]),
                                                                 mProbVarTS,
                                                                 TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]), 
                                                                 myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                 myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                 myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                 myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                 TString("MC BsDsPi Kaon"),
                                                                 workspace, debug)
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString("#MC FileName MU"),
                                                                 TString(myconfigfile["fileCalibKaonUp"]), TString(myconfigfile["workCalib"]),
                                                                 mProbVarTS,
                                                                 TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                 myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                 myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                 myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                 myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                 TString("MC BsDsPi Kaon"),
                                                                 workspace, debug)
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
                
    if Signal:
        workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), TString("#Signal BsDsPi NonRes"),
                                              myconfigfile["PIDBach"],
                                              myconfigfile["PDown"], myconfigfile["PUp"],
                                              myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                              myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                              myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                              myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                              mVarTS, mdVarTS, tVarTS, tagVarTS,
                                              tagOmegaVarTS, idVarTS, mProbVarTS,
                                              TString("BsDsPi"), true, false, workspace, debug)
        
        workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), TString("#Signal BsDsPi KstK"),
                                              myconfigfile["PIDBach"],
                                              myconfigfile["PDown"], myconfigfile["PUp"],
                                              myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                              myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                              myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                              myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                              mVarTS, mdVarTS, tVarTS, tagVarTS,
                                              tagOmegaVarTS, idVarTS, mProbVarTS,
                                              TString("BsDsPi"), true, false, workspace, debug)
        
        workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), TString("#Signal BsDsPi PhiPi"),
                                              myconfigfile["PIDBach"],
                                              myconfigfile["PDown"], myconfigfile["PUp"],
                                              myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                              myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                              myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                              myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                              mVarTS, mdVarTS, tVarTS, tagVarTS,
                                              tagOmegaVarTS, idVarTS, mProbVarTS,
                                              TString("BsDsPi"), true, false, workspace, debug)
        
        workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), TString("#Signal BsDsPi KPiPi"),
                                              myconfigfile["PIDBach"],
                                              myconfigfile["PDown"], myconfigfile["PUp"],
                                              myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                              myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                              myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                              myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                              mVarTS, mdVarTS, tVarTS, tagVarTS,
                                              tagOmegaVarTS, idVarTS, mProbVarTS,
                                              TString("BsDsPi"), true, false, workspace, debug)

        workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), TString("#Signal BsDsPi PiPiPi"),
                                              myconfigfile["PIDBach"],
                                              myconfigfile["PDown"], myconfigfile["PUp"],
                                              myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                              myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                              myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                              myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                              mVarTS, mdVarTS, tVarTS, tagVarTS,
                                              tagOmegaVarTS, idVarTS, mProbVarTS,
                                              TString("BsDsPi"), true, false, workspace, debug)
        workspace.Print()
    if SignalPID:
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]), 
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi KKPi NonRes Pion Down"),
                                                            workspace, workspace, debug)
       
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                          TString("MC BsDsPi KKPi NonRes Pion Down"),
                                                                          workspace, debug)

        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi KKPi PhiPi Pion Down"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("MC BsDsPi KKPi PhiPi Pion Down"),
                                                                          workspace, debug)
        
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi KKPi KstK Pion Down"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("MC BsDsPi KKPi KstK Pion Down"),
                                                                          workspace, debug)

        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi KPiPi Pion Down"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("MC BsDsPi KPiPi Pion Down"),
                                                                          workspace, debug)

        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi PiPiPi Pion Down"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("MC BsDsPi PiPiPi Pion Down"),
                                                                          workspace, debug)
        
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        #exit(0)
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalib"]),TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]), 
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi KKPi NonRes Pion Up"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                          TString("MC BsDsPi KKPi NonRes Pion Up"),
                                                                          workspace, debug)

        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalib"]),TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi KKPi PhiPi Pion Up"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("MC BsDsPi KKPi PhiPi Pion Up"),
                                                                          workspace, debug)

        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalib"]),TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi KKPi KstK Pion Up"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("MC BsDsPi KKPi KstK Pion Up"),
                                                                          workspace, debug)

        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalib"]),TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi KPiPi Pion Up"),
                                                            workspace, workspace, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("MC BsDsPi KPiPi Pion Up"),
                                                                          workspace, debug)

        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalib"]),TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("MC BsDsPi PiPiPi Pion Up"),
                                                            workspace, workspace, debug)

        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("MC BsDsPi PiPiPi Pion Up"),
                                                                          workspace, debug)
        
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    
    
    '''
    workspace = MassFitUtils.ObtainSignal(myconfigfile["dataName"], TString("#Signal BdDPi"),
                                          myconfigfile["PIDBach"],
                                          myconfigfile["PDown"], myconfigfile["PUp"],
                                          myconfigfile["BDTG"],
                                          myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                          myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                          myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                          mVarTS, mdVarTS, tVarTS, tagVarTS,
                                          tagOmegaVarTS, idVarTS, mProbVarTS,
                                          TString("BsDsPi"), workspace, debug)
    
     
    '''
    
    
    if CombPID:
        workspaceL = GeneralUtils.LoadWorkspace(TString("/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root"),TString("workspace"),debug)
    
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDown"]),TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombPi Pion Down"),
                                                            workspace, workspaceL, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDown"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("CombPi Pion Down"),
                                                                          workspace, debug)
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombPi Pion Up"),
                                                            workspace, workspaceL, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalib"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]),TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                          TString("CombPi Pion Up"),
                                                                          workspace, debug)
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        
    
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibKaonDown"]),TString(myconfigfile["workCalib"]),
                                                        myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                        TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                        myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                        myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                        TString("CombPi Kaon Down"),
                                                        workspace, workspaceL, debug)
    
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibKaonDown"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                          TString("CombPi Kaon Down"),
                                                                          workspace, debug)
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        workspace.Print()
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibKaonUp"]), TString(myconfigfile["workCalib"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombPi Kaon Up"),
                                                            workspace, workspaceL, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibKaonUp"]), TString(myconfigfile["workCalib"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]),TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"], 
                                                                          TString("CombPi Kaon Up"),
                                                                          workspace, debug)
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    exit(0)
    
    
  #  workspace = MassFitUtils.ObtainSignal(myconfigfile["dataName"], TString("#Signal BdDsPi"),
  #                                        myconfigfile["PIDBach"],
  #                                        myconfigfile["PDown"], myconfigfile["PUp"],
  #                                        myconfigfile["BDTG"],
  #                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
  #                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
  #                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
  #                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
  #                                        tagOmegaVarTS, idVarTS,
  #                                        mProbVarTS, TString("BdDsPi"), workspace, xsdebug)
        

    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    workspace.Print()
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        
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
                   default = 'dspi',
                   help = 'save workspace to file work_dspi.root'
                   )
parser.add_option( '-i', '--initial-vars',
                   dest = 'initvars',
                   action = 'store_true',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '--mvar',
                   dest = 'mvar',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
                   )
parser.add_option( '--tvar',
                   dest = 'tvar',
                   default = 'lab0_LifetimeFit_ctau',
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
parser.add_option( '--mdvar',
                   dest = 'mdvar',
                   default = 'lab2_MM',
                   help = 'set observable '
                   )


parser.add_option( '-c', '--cutvariable',
                   dest = 'ProbVar',
                   default = 'lab1_PIDK',
                   help = 'set observable '
                   )
parser.add_option( '--tagOmegaPdf',
                   dest = 'tagOmegaPdf',
                   default = "no",
                   help = 'create RooKeysPdf for TagOmega '
                   )
parser.add_option( '--tagTool',
                   dest = 'tagTool',
                   default = "no",
                   help = 'add to workspace a lot of tagging observables '
                   )
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsPiConfigForNominalMassFit')

parser.add_option( '--Data',
                   dest = 'Data',
                   action = 'store_true',
                   default = False,
                   help = 'create data'
                   )

parser.add_option( '--DPi',
                   dest = 'DPi',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--DPiPID',
                   dest = 'DPiPID',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--MC',
                   dest = 'MC',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--MCPID',
                   dest = 'MCPID',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--Signal',
                   dest = 'Signal',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--SignalPID',
                   dest = 'SignalPID',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                                      )
parser.add_option( '--CombPID',
                   dest = 'CombPID',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    import sys
    sys.path.append("../data/")
        
    prepareBsDsPiMassFitterOnData(  options.debug, options.mvar, options.tvar, \
                                    options.tagvar, options.tagomegavar, options.idvar,options.mdvar,\
                                    options.ProbVar, options.save, options.tagOmegaPdf, options.tagTool, options.configName,
                                    options.Data,
                                    options.DPi, options.DPiPID,
                                    options.MC, options.MCPID,
                                    options.Signal, options.SignalPID,
                                    options.CombPID)
    

# -----------------------------------------------------------------------------
