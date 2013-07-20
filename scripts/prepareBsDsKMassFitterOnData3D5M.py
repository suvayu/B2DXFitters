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
#from ROOT import RooRealVar, RooStringVar
#from ROOT import RooArgSet, RooArgList
#from ROOT import RooAddPdf
#from ROOT import FitMeTool

GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels


# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

saveName      = 'work_'


#------------------------------------------------------------------------------
def prepareBsDsKMassFitterOnData( debug, mVar, tVar, terrVar, tagVar, tagOmegaVar, idVar, mdVar, mProbVar, save, OmegaPdf, TagTool, configName,
                                  Data, DsPi, DsPiPID, MC, MCPID, Signal, SignalPID, CombPID ) : 

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
            

    mVarTS = TString(mVar)
    tVarTS = TString(tVar)
    terrVarTS = TString(terrVar)
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

    workspace = RooWorkspace("workspace","workspace")
    
    if Data:     
        dataNames = [TString("#BsK kkpi nonres"),
                     TString("#BsK kkpi phipi"),
                     TString("#BsK kkpi kstk"),
                     TString("#BsK kpipi"),
                     TString("#BsK pipipi")]

        for i in range(0,5):
            workspace = MassFitUtils.ObtainData(TString(myconfigfile["dataName"]) , dataNames[i],
                                                myconfigfile["PIDBach"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                mVarTS, mdVarTS, tVarTS, terrVarTS, tagVarTS,
                                                tagOmegaVarTS, idVarTS, mProbVarTS,
                                                TString("BsDsK"),tagTool,
                                                workspace,
                                                debug)
        
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()
    #exit(0)

    if DsPi:
        DsPiNames = [TString("#BsPi kkpi nores"),
                     TString("#BsPi kkpi phipi"),
                     TString("#BsPi kkpi kstk"),
                     TString("#BsPi kpipi"),
                     TString("#BsPi pipipi")]

        for i in range(0,5):
            workspace = MassFitUtils.ObtainMissForBsDsK(TString(myconfigfile["dataName"]), DsPiNames[i],
                                                        myconfigfile["PIDBach"],
                                                        myconfigfile["PDown"], myconfigfile["PUp"],
                                                        myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                        myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                        myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                        myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                        myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                        mVarTS, mdVarTS, mProbVarTS,
                                                        TString("BsDsPi"), workspace, tagOmega, debug)

                
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()
    #exit(0)

    if DsPiPID:
        DsPiPIDDownNames = [TString("BsDsPi KKPi NonRes Pion Down"),
                            TString("BsDsPi KKPi PhiPi Pion Down"),
                            TString("BsDsPi KKPi KstK Pion Down"),
                            TString("BsDsPi KPiPi Pion Down"),
                            TString("BsDsPi PiPiPi Pion Down")]
        DsPiPIDUpNames = [TString("BsDsPi KKPi NonRes Pion Up"),
                          TString("BsDsPi KKPi PhiPi Pion Up"),
                          TString("BsDsPi KKPi KstK Pion Up"),
                          TString("BsDsPi KPiPi Pion Up"),
                          TString("BsDsPi PiPiPi Pion Up")]

        for i in range(0,5):
            workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDownPion"]),
                                                                TString(myconfigfile["workCalibPion"]),
                                                                myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                DsPiPIDDownNames[i],
                                                                workspace, workspace, debug)
        
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDownPion"]),
                                                                              TString(myconfigfile["workCalibPion"]),
                                                                              mProbVarTS,
                                                                              TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                              myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                              myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                              DsPiPIDDownNames[i],
                                                                              workspace, debug)
            
            workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibUpPion"]),
                                                                TString(myconfigfile["workCalibPion"]),
                                                                myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                DsPiPIDUpNames[i],
                                                                workspace, workspace, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibUpPion"]),
                                                                              TString(myconfigfile["workCalibPion"]),
                                                                              mProbVarTS,
                                                                              TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                              myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                              myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                              DsPiPIDUpNames[i],
                                                                              workspace, debug)
            saveNameTS = TString(saveName)+TString(save)+TString(".root")
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
            workspace.Print()

       
   
    if MC:
        workspace = MassFitUtils.ObtainSpecBack(TString(myconfigfile["dataName"]), TString("#MC FileName MD"), TString("#MC TreeName"),
                                                myconfigfile["PIDBach"], myconfigfile["PIDChild"], myconfigfile["PIDProton"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsK"),
                                                workspace, false, tagOmega, debug)

    '''                                        
    workspace = RooWorkspace("workspace","workspace")
    workspace = SFitUtils.ReadLbLcPiFromSWeights(TString(myconfigfile["pathFileLcPi"]),
                                                 TString(myconfigfile["treeNameLcPi"]),
                                                 myconfigfile["PDown"], myconfigfile["PUp"],
                                                 myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                 myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                 myconfigfile["PIDDown"], myconfigfile["PIDUp"],                              
                                                 mVarTS,
                                                 mdVarTS,
                                                 TString("lab1_P"),
                                                 TString("lab1_PT"),
                                                 TString("nTracks"),
                                                 mProbVarTS,
                                                 workspace,
                                                 debug
                                                 )

    saveNameTS = TString("work_lblcpi_sw_PIDK10.root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()
    '''
           
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()
    #exit(0)
    
    if MC:
        workspace = MassFitUtils.ObtainSpecBack(TString(myconfigfile["dataName"]), TString("#MC FileName MU"), TString("#MC TreeName"),
                                                myconfigfile["PIDBach"], myconfigfile["PIDChild"], myconfigfile["PIDProton"],
                                                myconfigfile["PDown"], myconfigfile["PUp"],
                                                myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                mVarTS, mdVarTS, mProbVarTS,
                                                TString("BsDsK"),
                                                workspace, false, tagOmega, debug)
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()
    #exit(0)
    
    if MCPID:

        calibSampleUpNames = [ TString(myconfigfile["fileCalibUpKaon"]),
                               TString(myconfigfile["fileCalibUpPion"]),
                               TString(myconfigfile["fileCalibUpProton"])]

        workNames = [TString(myconfigfile["workCalibKaon"]),
                     TString(myconfigfile["workCalibPion"]),
                     TString(myconfigfile["workCalibProton"])]

        MCUpNames = [TString("MC BsDsK Kaon"),
                     TString("MC BsDsK Pion"),
                     TString("MC BsDsK Proton")]

        for i in range(0,3):
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MU"),
                                                       calibSampleUpNames[i],
                                                       workNames[i],
                                                       myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                       TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                       myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                       myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                       MCUpNames[i],
                                                       workspace, debug)

            workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString("#MC FileName MU"),
                                                                     calibSampleUpNames[i],
                                                                     workNames[i],
                                                                     mProbVarTS,
                                                                     TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                     myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                     myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                     myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                     myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                     MCUpNames[i],
                                                                     workspace, debug)
            
            
            saveNameTS = TString(saveName)+TString(save)+TString(".root")
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
            workspace.Print()
        
        calibSampleDownNames = [ TString(myconfigfile["fileCalibDownKaon"]),
                                 TString(myconfigfile["fileCalibDownPion"]),
                                 TString(myconfigfile["fileCalibDownProton"])]

        for i in range(0,3):
            workspace = WeightingUtils.ObtainHistRatio(TString(myconfigfile["dataName"]), TString("#MC FileName MD"),
                                                       calibSampleDownNames[i],
                                                       workNames[i],
                                                       myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                       TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                       myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                       myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                       MCUpNames[i],
                                                       workspace, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSample(TString(myconfigfile["dataName"]), TString("#MC FileName MD"),
                                                                     calibSampleDownNames[i],
                                                                     workNames[i],
                                                                     mProbVarTS,
                                                                     TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                     myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                     myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                     myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                     myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                     MCUpNames[i],
                                                                     workspace, debug)

            saveNameTS = TString(saveName)+TString(save)+TString(".root")
            GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
            workspace.Print()
                      

    if MC:
        workspace = MassFitUtils.CreatePdfSpecBackground(TString(myconfigfile["dataName"]), TString("#MC FileName MD"),
                                                         TString(myconfigfile["dataName"]), TString("#MC FileName MU"),
                                                         mVarTS, mdVarTS,
                                                         myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                         myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                         workspace, tagOmega, debug)
        
    saveNameTS = TString(saveName)+TString(save)+TString(".root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    workspace.Print()
    
    if Signal:
        signalNames = [ TString("#Signal BsDsK NonRes"),
                        TString("#Signal BsDsK KstK"),
                        TString("#Signal BsDsK PhiPi"),
                        TString("#Signal BsDsK KPiPi"),
                        TString("#Signal BsDsK PiPiPi")]

        for i in range(0,5):
            workspace = MassFitUtils.ObtainSignal(TString(myconfigfile["dataName"]), signalNames[i],
                                                  myconfigfile["PIDBach"],
                                                  myconfigfile["PDown"], myconfigfile["PUp"],
                                                  myconfigfile["BDTGDown"], myconfigfile["BDTGUp"],
                                                  myconfigfile["DMassDown"], myconfigfile["DMassUp"],
                                                  myconfigfile["BMassDown"], myconfigfile["BMassUp"],
                                                  myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                  myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                  myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                  mVarTS, mdVarTS, tVarTS, terrVarTS, tagVarTS,
                                                  tagOmegaVarTS, idVarTS,
                                                  mProbVarTS,
                                                  TString("BsDsK"), false, false, workspace, debug)
            
                
    if SignalPID:
        signalPIDDownNames = [ TString("MC BsDsK KKPi NonRes Kaon Down"),
                               TString("MC BsDsK KKPi KstK Kaon Down"),
                               TString("MC BsDsK KKPi PhiPi Kaon Down"),
                               TString("MC BsDsK KPiPi Kaon Down"),
                               TString("MC BsDsK PiPiPi Kaon Down")]

        for i in range(0,5):
            workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDownKaon"]), TString(myconfigfile["workCalibKaon"]),
                                                                myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                signalPIDDownNames[i],
                                                                workspace, workspace, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDownKaon"]),
                                                                              TString(myconfigfile["workCalibKaon"]),
                                                                              mProbVarTS,
                                                                              TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                              myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                              myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                              signalPIDDownNames[i],
                                                                              workspace, debug)


        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()
                
        signalPIDUpNames = [ TString("MC BsDsK KKPi NonRes Kaon Up"),
                             TString("MC BsDsK KKPi KstK Kaon Up"),
                             TString("MC BsDsK KKPi PhiPi Kaon Up"),
                             TString("MC BsDsK KPiPi Kaon Up"),
                             TString("MC BsDsK PiPiPi Kaon Up")]
        
        
        for i in range(0,5):
            workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibUpKaon"]), TString(myconfigfile["workCalibKaon"]),
                                                                myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                signalPIDUpNames[i],
                                                                workspace, workspace, debug)
            
            workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibUpKaon"]),
                                                                              TString(myconfigfile["workCalibKaon"]),
                                                                              mProbVarTS,
                                                                              TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                              myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                              myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                              myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                              myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                              signalPIDUpNames[i],
                                                                              workspace, debug)
            
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()

    if CombPID:
        #workspace = GeneralUtils.LoadWorkspace(TString("work_dsk_pid_5358.root"),TString("workspace"),debug)
        workspaceL = GeneralUtils.LoadWorkspace(TString("/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsK_5358.root"),TString("workspace"),debug)
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDownPion"]),TString(myconfigfile["workCalibPion"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombK Pion Down"),
                                                            workspace, workspaceL, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDownPion"]),
                                                                          TString(myconfigfile["workCalibPion"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("CombK Pion Down"),
                                                                          workspace, debug)
        
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibUpPion"]),TString(myconfigfile["workCalibPion"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombK Pion Up"),
                                                            workspace, workspaceL, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibUpPion"]),
                                                                          TString(myconfigfile["workCalibPion"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("CombK Pion Up"),
                                                                          workspace, debug)
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()
        
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDownKaon"]),TString(myconfigfile["workCalibKaon"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombK Kaon Down"),
                                                            workspace, workspaceL, debug)
    
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDownKaon"]),
                                                                          TString(myconfigfile["workCalibKaon"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("CombK Kaon Down"),
                                                                          workspace, debug)
        
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibUpKaon"]),TString(myconfigfile["workCalibKaon"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombK Kaon Up"),
                                                            workspace, workspaceL, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibUpKaon"]),
                                                                          TString(myconfigfile["workCalibKaon"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("CombK Kaon Up"),
                                                                          workspace, debug)
        
        saveNameTS = TString(saveName)+TString(save)+TString(".root")
        GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
        workspace.Print()
        
        #workspace = GeneralUtils.LoadWorkspace(TString("work_dsk_pid_8.root"),TString("workspace"),debug)
        
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibDownProton"]),TString(myconfigfile["workCalibProton"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombK Proton Down"),
                                                            workspace, workspaceL, debug)
    
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibDownProton"]),
                                                                          TString(myconfigfile["workCalibProton"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("CombK Proton Down"),
                                                                          workspace, debug)
        
        workspace = WeightingUtils.ObtainHistRatioOneSample(TString(myconfigfile["fileCalibUpProton"]),TString(myconfigfile["workCalibProton"]),
                                                            myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                            TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                            myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                            myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                            TString("CombK Proton Up"),
                                                            workspace, workspaceL, debug)
        
        workspace = WeightingUtils.ObtainPIDShapeFromCalibSampleOneSample(TString(myconfigfile["fileCalibUpProton"]),
                                                                          TString(myconfigfile["workCalibProton"]),
                                                                          mProbVarTS,
                                                                          TString(myconfigfile["Var1"]), TString(myconfigfile["Var2"]),
                                                                          myconfigfile["PIDDown"], myconfigfile["PIDUp"],
                                                                          myconfigfile["PTDown"], myconfigfile["PTUp"],
                                                                          myconfigfile["nTracksDown"], myconfigfile["nTracksUp"],
                                                                          myconfigfile["Bin1"], myconfigfile["Bin2"],
                                                                          TString("CombK Proton Up"),
                                                                          workspace, debug)
        
    
#    workspace = MassFitUtils.ObtainSignal(myconfigfile["dataName"], TString("#Signal BdDsK"),
#                                          myconfigfile["PIDBach"],
#                                          myconfigfile["PDown"], myconfigfile["PUp"],
#                                          myconfigfile["BDTG"],
#                                          myconfigfile["DMassDown"], myconfigfile["DMassUp"],
#                                          myconfigfile["BMassDown"], myconfigfile["BMassUp"],
#                                          myconfigfile["TimeDown"], myconfigfile["TimeUp"],
#                                          mVarTS, mdVarTS, tVarTS, tagVarTS,
#                                          tagOmegaVarTS, idVarTS,
#                                          mProbVarTS,
#                                          TString("BdDsK"), workspace, tagOmega, debug)

    saveNameTS = TString(saveName)+TString(save)+TString(".root")
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
                   default = 'dsk',
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
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
parser.add_option( '--terrvar',
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
parser.add_option( '--mdvar',
                   dest = 'mdvar',
                   default = 'lab2_MM',
                   help = 'set observable '
                   )

parser.add_option( '-c', '--cutvariable',
                   dest = 'ProbVar',
                   default = 'lab1_PIDK',
                   help = 'set observable for PID '
                   )
parser.add_option( '--tagOmegaPdf',
                  dest = 'tagOmegaPdf',
                  default = "no",
                  help = 'create RooKeysPdf for TagOmega '
                  )
parser.add_option( '--tagTool',
                   dest = 'tagTool',
                   default = "no",
                   help = 'add to workspace a lot of tagging observables (for Matt) '
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

parser.add_option( '--DsPi',
                   dest = 'DsPi',
                   action = 'store_true',
                   default = False,
                   help= 'create data'
                   )

parser.add_option( '--DsPiPID',
                   dest = 'DsPiPID',
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
        
    prepareBsDsKMassFitterOnData(  options.debug, options.mvar, options.tvar, options.terrvar, \
                                   options.tagvar, options.tagomegavar, options.idvar, options.mdvar,\
                                   options.ProbVar, options.save, options.tagOmegaPdf,
                                   options.tagTool, options.configName,
                                   options.Data,
                                   options.DsPi, options.DsPiPID,
                                   options.MC, options.MCPID,
                                   options.Signal, options.SignalPID,
                                   options.CombPID)

# -----------------------------------------------------------------------------
