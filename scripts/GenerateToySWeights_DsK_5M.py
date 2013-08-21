# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to generate toys for DsK                                    #
#                                                                             #
#   Example usage:                                                            #
#      python GenerateToySWeights_DsK.py                                      #
#                                                                             #
#   Author: Vava Gligorov                                                     #
#   Date  : 14 / 06 / 2012                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 06 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #


from math import *
from optparse import OptionParser
from os.path  import join

import GaudiPython
GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import *

GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels
SFitUtils = GaudiPython.gbl.SFitUtils

from B2DXFitters import taggingutils, cpobservables


RooRandom.randomGenerator().SetSeed(78249292)

RooAbsData.setDefaultStorageType(RooAbsData.Tree)


RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-4)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-4)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','20Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)


#------------------------------------------------------------------------------
def runBsDsKGenerator( debug, single, configName, numberOfToys, numberOfEvents ) :

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
                                                                    
    #workout = RooWorkspace("workspace","workspace")

    Gammad       = RooRealVar('Gammad','Gammad', myconfigfile["Gammad"])                     # in ps^{-1}
    Gammas       = RooRealVar('Gammas','Gammas', myconfigfile["Gammas"])                     # in ps^{-1}
    DeltaGammad  = RooRealVar('DeltaGammad','DeltaGammad', myconfigfile["DeltaGammad"])      # in ps^{-1}
    DeltaGammas  = RooRealVar('DeltaGammas','DeltaGammas', myconfigfile["DeltaGammas"])      # in ps^{-1}
    TauInvGd     = Inverse( "TauInvGd","TauInvGd", Gammad)
    TauInvGs     = Inverse( "TauInvGs","TauInvGs", Gammas)
        
    DeltaMd      = RooRealVar('DeltaMd','DeltaMd', myconfigfile["DeltaMd"])                  # in ps^{-1}
    DeltaMs      = RooRealVar('DeltaMs','DeltaMs', myconfigfile["DeltaMs"])                  # in ps^{-1}
                        
    GammaLb      = RooRealVar('GammaLb','GammaLb',myconfigfile["GammaLb"])
    GammaCombo   = RooRealVar('GammaCombo','GammaCombo',myconfigfile["GammaCombo"])
    TauInvLb     = Inverse( "TauInvLb","TauInvLb", GammaLb)
    TauInvCombo  = Inverse( "TauInvCombo","TauInvCombo", GammaCombo)
        
    #TauRes       = RooRealVar('TauRes','TauRes',myconfigfile["TauRes"])
        
    zero     = RooConstVar('zero', '0', 0.)
    one      = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two      = RooConstVar('two', '2', 2.)

    sam = TString("both")
    #mode = TString("phipi")
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
           
    
    if single :
        ntoys = 1
    else:
        ntoys = int(numberOfToys)
                            
      
    gendata = []
    data = []
    
    fileName  = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/work_dsk_pid_53005800_PIDK5_5M_BDTGA.root"
    #fileName  = "work_dsk_pid_53005800_PIDK5_5M_BDTGA_2.root"
    fileName2 = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsK.root"
    workName = 'workspace'
    
    mVar = 'lab0_MassFitConsD_M'
    mdVar    = 'lab2_MM'
    PIDKVar  = 'lab1_PIDK'
    tVar     = 'lab0_LifetimeFit_ctau'
    terrVar  = 'lab0_LifetimeFit_ctauErr'
    trueID   = 'lab0_TRUEID'
    charge   = 'lab1_ID'
    tagdec   = 'lab0_BsTaggingTool_TAGDECISION_OS'
    tagomega = 'lab0_BsTaggingTool_TAGOMEGA_OS'
    
    
    #Read workspace with PDFs
    workspace = GeneralUtils.LoadWorkspace(TString(fileName),TString(workName), debug)
    workspace.Print("v")
    workspace_mistag = GeneralUtils.LoadWorkspace(TString(fileName2),TString(workName), debug)
    workspace_mistag.Print("v")
    #exit(0)

    timeVar_B   = RooRealVar(tVar,tVar,0,15) 
    terrVar_B   = RooRealVar(terrVar,terrVar,0.01,0.1)
    massVar_D   = GeneralUtils.GetObservable(workspace,TString(mdVar), debug)
    PIDKVar_B   = GeneralUtils.GetObservable(workspace,TString(PIDKVar), debug)
    massVar_B   = GeneralUtils.GetObservable(workspace,TString(mVar), debug)
    trueIDVar_B = RooRealVar(trueID,trueID,0,100)
    mistagVar_B = GeneralUtils.GetObservable(workspace_mistag,TString(tagomega), debug)
    #mistagVar_B.setMax(1.0)

    #Time resolution
    trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["resolutionMeanBias"], 'ps' )
    trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', myconfigfile["resolutionScaleFactor"] )
    trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGaussPEDTE', timeVar_B, trm_mean, terrVar_B, trm_scale)
            
    # Acceptance
    tacc_beta_pl        = RooRealVar('tacc_beta_pl'    , 'PowLawAcceptance_beta',      myconfigfile["tacc_beta_pl"]     )
    tacc_exponent_pl    = RooRealVar('tacc_exponent_pl', 'PowLawAcceptance_exponent',  myconfigfile["tacc_exponent_pl"] )
    tacc_offset_pl      = RooRealVar('tacc_offset_pl'  , 'PowLawAcceptance_offset',    myconfigfile["tacc_offset_pl"]   )
    tacc_turnon_pl      = RooRealVar('tacc_turnon_pl'  , 'PowLawAcceptance_turnon',    myconfigfile["tacc_turnon_pl"]   )
    ratiocorr           = RooConstVar('ratiocorr','ratiocorr',1.)
    tacc_powlaw         = PowLawAcceptance('BsPowLawAcceptance', 'PowLaw decay time acceptance function',
                                           tacc_turnon_pl, timeVar_B, tacc_offset_pl, tacc_exponent_pl, tacc_beta_pl,ratiocorr)

    calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"])
    calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"])
    avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"])

    mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
                                         mistagVar_B, calibration_p0,calibration_p1,avmistag)

    terr = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    mistag = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
      
    #Create out workspace
    #workout = RooWorkspace("workspace","workspace")
    
    #Tag maps
    bTagMap = RooCategory(tagdec, tagdec)
    bTagMap.defineType('B'       ,  1)
    bTagMap.defineType('Bbar'    , -1)
    bTagMap.defineType('Untagged',  0)
    
    fChargeMap = RooCategory(charge, charge)
    fChargeMap.defineType('h+',  1)
    fChargeMap.defineType('h-', -1)

    nameDs = [TString("nonres"), TString("phipi"), TString("kstk"), TString("kpipi"), TString("pipipi")]
    nameDs2 = ["nonres","phipi","kstk","kpipi","pipipi"]
    
    total_pdf = []

    meanVarBs = []
    sigma1VarBs = []
    sigma2VarBs = []
    alpha1VarBs = []
    alpha2VarBs = []
    n1VarBs = []
    n2VarBs = []
    fracVarBs = []
    massB_signal = []

    meanVarDs = []
    sigma1VarDs = []
    sigma2VarDs = []
    alpha1VarDs = []
    alpha2VarDs = []
    n1VarDs = []
    n2VarDs = []
    fracVarDs = []
    massD_signal = []

    PIDK_signal = []
    MDFitter_signal = []    
    timeandmass_signal = []

    meanVarBd   =  []
    sigma1VarBd =  []
    sigma2VarBd =  []
    
    massB_dsk = []
    massD_dsk = []
    PIDK_dsk = []
    MDFitter_dsk = []
    timeandmass_dsk = []

    massB_dspi = []
    massD_dspi = []
    PIDK_dspi = []
    MDFitter_dspi = []
    timeandmass_dspi = []

    massD_dsdsstp = []
    MDFitter_dsdsstp = []
    timeandmass_dsdsstp = []
    
    cBVar = []
    massB_combo = []     
    cDVar = [] 
    fracDsComb = []
    massD_combo = []
    MDFitter_combo = []
    timeandmass_combo = []
         
    massD_lm1 = []
    MDFitter_lm1 = []
    timeandmass_lm1 = []

    massD_lm2 = []
    MDFitter_lm2 = []
    timeandmass_lm2 = []

    timeandmass_dk = []
    timeandmass_lck = []
    
    num_signal = []
    num_dk = []
    num_dsk = []
    num_dspi = []
    num_lck = []
    num_dsdsstp = []
    num_combo = []
    num_lm1 = []
    num_lm2 = []

    # ------------------------------------------------ Signal -----------------------------------------------------#

    #The signal - time acceptance - tacc_powlaw
    tacc_signal = tacc_powlaw

    #The signal - resolution
    trm_signal = trm
    
    #The signal - time error
    terr_signal = terr #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_signal.SetName("terr_signal")
    
    #The signal - time
    ACPobs_signal = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"], myconfigfile["ArgLbarfbar_s"], myconfigfile["ModLf_s"])
    ACPobs_signal.printtable()
    
    C_signal     = RooRealVar('C_signal','C_signal',ACPobs_signal.Cf())
    S_signal     = RooRealVar('S_signal','S_signal',ACPobs_signal.Sf())
    D_signal     = RooRealVar('D_signal','D_signal',ACPobs_signal.Df())
    Sbar_signal  = RooRealVar('Sbar_signal','Sbar_signal',ACPobs_signal.Sfbar())
    Dbar_signal  = RooRealVar('Dbar_signal','Dbar_signal',ACPobs_signal.Dfbar())
    
    tagEff_signal    = RooRealVar("tagEff_signal","tagEff_signal", myconfigfile["tagEff_signal"])
    
    aProd_signal   = RooConstVar('aprod_signal',   'aprod_signal',   myconfigfile["aprod_signal"])        # production asymmetry
    aDet_signal    = RooConstVar('adet_signal',    'adet_signal',    myconfigfile["adet_signal"])         # detector asymmetry
    aTagEff_signal = RooConstVar('atageff_signal', 'atageff_signal', myconfigfile["atageff_signal"])      # taginng eff asymmetry
    
    #The Bs->DsK - mistag
    mistag_signal = mistag #Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_signal.SetName("mistag_signal")
    
    flag_signal = 0
    flag = 0

    otherargs_signal = [ mistagVar_B, mistag_signal, tagEff_signal ]
    otherargs_signal.append(mistagCalibrated)
    otherargs_signal.append(aProd_signal)
    otherargs_signal.append(aDet_signal)
    otherargs_signal.append(aTagEff_signal)
    
    cosh_signal = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven,
                               fChargeMap, bTagMap,  one,      one,      *otherargs_signal)
    sinh_signal = DecRateCoeff('signal_sinh', 'signal_sinh', flag_signal | DecRateCoeff.CPEven,
                               fChargeMap, bTagMap,  D_signal,    Dbar_signal, *otherargs_signal)
    cos_signal  = DecRateCoeff('signal_cos',  'signal_cos' , DecRateCoeff.CPOdd,
                               fChargeMap, bTagMap,  C_signal,    C_signal,    *otherargs_signal)
    sin_signal  = DecRateCoeff('signal_sin',  'signal_sin',  flag_signal | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                               fChargeMap, bTagMap,  S_signal, Sbar_signal,    *otherargs_signal)
    
    time_signal_noacc       = RooBDecay('time_signal_noacc','time_signal_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                        cosh_signal, sinh_signal, cos_signal, sin_signal,
                                        DeltaMs,trm_signal, RooBDecay.SingleSided)
    
    time_signal             = RooEffProd('time_signal','time_signal',time_signal_noacc,tacc_powlaw)

    #The signal - true ID
    trueid_signal = RooGenericPdf("trueid_signal","exp(-100.*abs(@0-1))",RooArgList(trueIDVar_B))
    
    
    #The Bs->DsK - total
    timeerr_signal = RooProdPdf('signal_timeerr', 'signal_timeerr',  RooArgSet(terr_signal),
                                RooFit.Conditional(RooArgSet(time_signal),
                                                   RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))

    #-------------------------------------------------- Bd -> DK ----------------------------------------------------#

    m = TString("Bd2DK")
    MDFitter_dk = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, debug)

    #The Bd->DK - acceptance - tacc_powlaw
    tacc_dk = tacc_powlaw
    
    #The Bd->DK - resolution
    trm_dk = trm
    
    #The Bd->DK - time
    tagEff_dk    = RooRealVar("tagEff_dk","tagEff_dk", myconfigfile["tagEff_dk"])
    
    C_dk    = RooRealVar('C_dk', 'C coeff. dk', 1.)
    S_dk    = RooRealVar('S_dk', 'S coeff. dk', 0.)
    D_dk    = RooRealVar('D_dk', 'D coeff. dk', 0.)
    Sbar_dk    = RooRealVar('Sbar_dk', 'Sbar coeff. dk', 0.)
    Dbar_dk    = RooRealVar('Dbar_dk', 'Dbar coeff. dk', 0.)
    
    aProd_dk   = RooConstVar('aprod_dk',   'aprod_dk',   myconfigfile["aprod_dk"])        # production asymmetry
    aDet_dk    = RooConstVar('adet_dk',    'adet_dk',    myconfigfile["adet_dk"])         # detector asymmetry
    aTagEff_dk = RooConstVar('atageff_dk', 'atageff_dk', myconfigfile["atageff_dk"])      # taginng eff asymmetry
    
    #The Bd->DPi - mistag
    mistag_dk = mistag_signal
    mistag_dk.SetName("mistag_dk")
    
    otherargs_dk = [ mistagVar_B, mistag_dk, tagEff_dk ]
    otherargs_dk.append(mistagCalibrated)
    otherargs_dk.append(aProd_dk)
    otherargs_dk.append(aDet_dk)
    otherargs_dk.append(aTagEff_dk)

    cosh_dk = DecRateCoeff('dk_cosh', 'dk_cosh', DecRateCoeff.CPEven,
                                                          fChargeMap, bTagMap,  one,      one,      *otherargs_dk)
    sinh_dk = DecRateCoeff('dk_sinh', 'dk_sinh', flag | DecRateCoeff.CPEven,
                                                          fChargeMap, bTagMap,  D_dk,    Dbar_dk, *otherargs_dk)
    cos_dk  = DecRateCoeff('dk_cos',  'dk_cos' , DecRateCoeff.CPOdd,
                                                          fChargeMap, bTagMap,  C_dk,    C_dk,    *otherargs_dk)
    sin_dk  = DecRateCoeff('dk_sin',  'dk_sin',  flag | DecRateCoeff.CPOdd,
                                                          fChargeMap, bTagMap,  Sbar_dk, S_dk,    *otherargs_dk)

    time_dk_noacc       = RooBDecay('time_dk_noacc','time_dk_noacc', timeVar_B, TauInvGd, DeltaGammad,
                                    cosh_dk, sinh_dk, cos_dk, sin_dk,
                                    DeltaMd, trm_dk, RooBDecay.SingleSided)
    
    
    time_dk             = RooEffProd('time_dk','time_dk',time_dk_noacc,tacc_dk)
    
    #The Bd->DK - true ID
    trueid_dk = RooGenericPdf("trueid_dk","exp(-100.*abs(@0-2))",RooArgList(trueIDVar_B))
    
    #The Bd->DPi - time error
    terr_dk = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_dk.SetName("terr_dk")
    
    #The Bd->DK - total
    timeerr_dk = RooProdPdf('dk_timeerr', 'dk_timeerr',  RooArgSet(terr_dk),
                            RooFit.Conditional(RooArgSet(time_dk),
                                               RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
                                            
    #------------------------------------------------- Bd -> DsK ----------------------------------------------------#

    #The Bd->DsK - acceptance - tacc_powlaw
    tacc_dsk = tacc_powlaw
    
    #The Bd->DsK - resolution
    trm_dsk = trm
    
    #The Bd->DsK - time
    tagEff_dsk    = RooRealVar("tagEff_dsk","tagEff_dsk",myconfigfile["tagEff_dsk"])
    
    C_dsk    = RooRealVar('C_dsk', 'C coeff. dsk', 1.)
    S_dsk    = RooRealVar('S_dsk', 'S coeff. dsk', 0.)
    D_dsk    = RooRealVar('D_dsk', 'D coeff. dsk', 0.)
    Sbar_dsk    = RooRealVar('Sbar_dsk', 'Sbar coeff. dsk', 0.)
    Dbar_dsk    = RooRealVar('Dbar_dsk', 'Dbar coeff. dsk', 0.)
    
    aProd_dsk   = RooConstVar('aprod_dsk',   'aprod_dsk',   myconfigfile["aprod_dsk"])        # production asymmetry
    aDet_dsk    = RooConstVar('adet_dsk',    'adet_dsk',    myconfigfile["adet_dsk"])         # detector asymmetry
    aTagEff_dsk = RooConstVar('atageff_dsk', 'atageff_dsk', myconfigfile["atageff_dsk"])      # taginng eff asymmetry
    
    #The Bd->DsPi - mistag
    mistag_dsk = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_dsk.SetName("mistag_dsk")

    otherargs_dsk = [ mistagVar_B, mistag_dsk, tagEff_dsk ]
    otherargs_dsk.append(mistagCalibrated)
    otherargs_dsk.append(aProd_dsk)
    otherargs_dsk.append(aDet_dsk)
    otherargs_dsk.append(aTagEff_dsk)
    
    cosh_dsk = DecRateCoeff('dsk_cosh', 'dsk_cosh', DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  one,       one,     *otherargs_dsk)
    sinh_dsk = DecRateCoeff('dsk_sinh', 'dsk_sinh', flag | DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  D_dsk,    Dbar_dsk, *otherargs_dsk)
    cos_dsk  = DecRateCoeff('dsk_cos',  'dsk_cos' , DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  C_dsk,    C_dsk,    *otherargs_dsk)
    sin_dsk  = DecRateCoeff('dsk_sin',  'dsk_sin',  flag | DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  Sbar_dsk, S_dsk,    *otherargs_dsk)
    
    time_dsk_noacc       = RooBDecay('time_dsk_noacc','time_dsk_noacc', timeVar_B, TauInvGd, DeltaGammad,
                                     cosh_dsk, sinh_dsk, cos_dsk, sin_dsk,
                                     DeltaMd,trm_dsk, RooBDecay.SingleSided)
    
    time_dsk             = RooEffProd('time_dsk','time_dsk',time_dsk_noacc,tacc_dsk)
    
    #The Bd->DsK - true ID
    trueid_dsk = RooGenericPdf("trueid_dsk","exp(-100.*abs(@0-3))",RooArgList(trueIDVar_B))
    
    #The Bd->DsPi - time error
    terr_dsk = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_dsk.SetName("terr_dsk")
    
    
    #The Bd->DsK - total
    timeerr_dsk = RooProdPdf('dsk_timeerr', 'dsk_timeerr',  RooArgSet(terr_dsk),
                             RooFit.Conditional(RooArgSet(time_dsk),
                                                RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    #------------------------------------------------- Bs -> DsPi ----------------------------------------------------#

    #The Bs->DsPi - acceptance - tacc_powlaw
    tacc_dspi = tacc_powlaw
    
    #The Bs->DsPi - resolution
    trm_dspi = trm
    
    #The Bs->DsPi - time
    tagEff_dspi    = RooRealVar("tagEff_dspi","tagEff_dspi", myconfigfile["tagEff_dspi"])
    
    C_dspi    = RooRealVar('C_dspi', 'C coeff. dspi', 1.)
    S_dspi    = RooRealVar('S_dspi', 'S coeff. dspi', 0.)
    D_dspi    = RooRealVar('D_dspi', 'D coeff. dspi', 0.)
    Sbar_dspi    = RooRealVar('Sbar_dspi', 'Sbar coeff. dspi', 0.)
    Dbar_dspi    = RooRealVar('Dbar_dspi', 'Dbar coeff. dspi', 0.)
    
    aProd_dspi   = RooConstVar('aprod_dspi',   'aprod_dspi',   myconfigfile["aprod_dspi"])        # production asymmetry
    aDet_dspi    = RooConstVar('adet_dspi',    'adet_dspi',    myconfigfile["adet_dspi"])         # detector asymmetry
    aTagEff_dspi = RooConstVar('atageff_dspi', 'atageff_dspi', myconfigfile["atageff_dspi"])      # taginng eff asymmetr
    
    mistag_dspi = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_dspi.SetName("mistag_dspi")
    
    otherargs_dspi = [ mistagVar_B, mistag_dspi, tagEff_dspi ]
    otherargs_dspi.append(mistagCalibrated)
    otherargs_dspi.append(aProd_dspi)
    otherargs_dspi.append(aDet_dspi)
    otherargs_dspi.append(aTagEff_dspi)

    cosh_dspi = DecRateCoeff('dspi_cosh', 'dspi_cosh', DecRateCoeff.CPEven, fChargeMap, bTagMap,
                             one,         one,         *otherargs_dspi)
    sinh_dspi = DecRateCoeff('dspi_sinh', 'dspi_sinh', DecRateCoeff.CPEven, fChargeMap, bTagMap,
                             D_dspi,    Dbar_dspi, *otherargs_dspi)
    cos_dspi  = DecRateCoeff('dspi_cos' , 'dspi_cos' , DecRateCoeff.CPOdd,  fChargeMap, bTagMap,
                             C_dspi,    C_dspi,    *otherargs_dspi)
    sin_dspi  = DecRateCoeff('dspi_sin' , 'dspi_sin' , DecRateCoeff.CPOdd,  fChargeMap, bTagMap,
                             Sbar_dspi, S_dspi,    *otherargs_dspi)
    
    time_dspi_noacc       = RooBDecay('time_dspi_noacc','time_dspi_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                      cosh_dspi, sinh_dspi, cos_dspi, sin_dspi,
                                      DeltaMs, trm_dspi, RooBDecay.SingleSided)
    
    
    time_dspi             = RooEffProd('time_dspi','time_dspi',time_dspi_noacc,tacc_dspi)
    
    #The Bs->DsPi - true ID
    trueid_dspi = RooGenericPdf("trueid_dspi","exp(-100.*abs(@0-4))",RooArgList(trueIDVar_B))
    
    #The Bs->DsPi - time error
    terr_dspi = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_dspi.SetName("terr_dspi")
    
    
    #The Bs->DsPi - total
    timeerr_dspi = RooProdPdf('dspi_timeerr', 'dspi_timeerr',  RooArgSet(terr_dspi),
                              RooFit.Conditional(RooArgSet(time_dspi),
                                                 RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))

    #------------------------------------------------- Lb -> LcK ----------------------------------------------------#

    #The Lb->LcK - mass
    m = TString("Lb2LcK");
    MDFitter_lck = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, debug);

    #The Lb->LcK - acceptance - tacc_powlaw
    tacc_lck = tacc_powlaw
    
    #The Lb->LcK - resolution
    trm_lck = trm
    
    #The Lb->LcK - time
    tagEff_lck    = RooRealVar("tagEff_lck","tagEff_lck", myconfigfile["tagEff_lck"])
    
    C_lck    = RooRealVar('C_lck', 'C coeff. lck', 1.)
    S_lck    = RooRealVar('S_lck', 'S coeff. lck', 0.)
    D_lck    = RooRealVar('D_lck', 'D coeff. lck', 0.)
    Sbar_lck    = RooRealVar('Sbar_lck', 'Sbar coeff. lck', 0.)
    Dbar_lck    = RooRealVar('Dbar_lck', 'Dbar coeff. lck', 0.)
    
    aProd_lck   = RooConstVar('aprod_lck',   'aprod_lck',   myconfigfile["aprod_lck"])        # production asymmetry
    aDet_lck    = RooConstVar('adet_lck',    'adet_lck',    myconfigfile["adet_lck"])         # detector asymmetry
    aTagEff_lck = RooConstVar('atageff_lck', 'atageff_lck', myconfigfile["atageff_lck"])      # taginng eff asymmetry
    
    #The Lb->LcK - mistag
    mistag_lck = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_lck.SetName("mistag_lck")
    
    otherargs_lck = [ mistagVar_B, mistag_lck, tagEff_lck ]
    otherargs_lck.append(mistagCalibrated)
    otherargs_lck.append(aProd_lck)
    otherargs_lck.append(aDet_lck)
    otherargs_lck.append(aTagEff_lck)
    
    cosh_lck = DecRateCoeff('lck_cosh', 'lck_cosh', DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  one,       one,     *otherargs_lck)
    sinh_lck = DecRateCoeff('lck_sinh', 'lck_sinh', flag | DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  D_lck,    Dbar_lck, *otherargs_lck)
    cos_lck  = DecRateCoeff('lck_cos',  'lck_cos' , DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  C_lck,    C_lck,    *otherargs_lck)
    sin_lck  = DecRateCoeff('lck_sin',  'lck_sin',  flag | DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  Sbar_lck, S_lck,    *otherargs_lck)
    
    time_lck_noacc       = RooBDecay('time_lck_noacc','time_lck_noacc', timeVar_B, TauInvLb, zero,
                                     cosh_lck, sinh_lck, cos_lck, sin_lck,
                                     zero,trm_lck, RooBDecay.SingleSided)

    time_lck             = RooEffProd('time_lck','time_lck',time_lck_noacc,tacc_powlaw)

    #The Lb->LcK - true ID
    trueid_lck = RooGenericPdf("trueid_lck","exp(-100.*abs(@0-5))",RooArgList(trueIDVar_B))

    #The Lb->LcK - time error
    terr_lck = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_lck.SetName("terr_lck")
    
    
    #The Lb->LcK - total
    timeerr_lck = RooProdPdf('lck_timeerr', 'lck_timeerr',  RooArgSet(terr_lck),
                             RooFit.Conditional(RooArgSet(time_lck),
                                                RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))

    #------------------------------------------------- Lb -> Dsp, Dsstp ----------------------------------------------------#

    #The Lb->Dsp, Lb->Dsstp - mass
    m = TString("Lb2Dsp")
    massB_dsp = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    m = TString("Lb2Dsstp")
    massB_dsstp = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    frac_dsdsstp = RooRealVar("frac_dsdsstp","frac_dsdsstp", myconfigfile["frac_dsdsstp"])
    massB_dsdsstp = RooAddPdf("mass_dsdsstp","mass_dsdsstp",RooArgList(massB_dsp,massB_dsstp),RooArgList(frac_dsdsstp))
                                                            

    #The Lb->Dsp, Lb->Dsstp - PIDK
    m = TString("Lb2Dsp")
    pidk_dsp = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("Lb2Dsstp")
    pidk_dsstp = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    PIDK_dsdsstp = RooAddPdf("pidk_dsdsstp","pidk_dsdsstp",RooArgList(pidk_dsp,pidk_dsstp),RooArgList(frac_dsdsstp))
            

    #The Lb->Dsp, Lb->Dsstp - acceptance - tacc_powlaw
    tacc_dsdsstp = tacc_powlaw
    
    #The Lb->Dsp, Lb->Dsstp - resolution
    trm_dsdsstp = trm
    
    #The Lb->Dsp, Lb->Dsstp - time
    tagEff_dsdsstp    = RooRealVar("tagEff_dsdsstp","tagEff_dsdsstp", myconfigfile["tagEff_dsdsstp"])
    tagWeight_dsdsstp = TagEfficiencyWeight('tagWeight_dsdsstp','tagWeight_dsdsstp',bTagMap,tagEff_dsdsstp)
    
    C_dsdsstp    = RooRealVar('C_dsdsstp', 'S coeff. dsdsstp', 1.)
    S_dsdsstp    = RooRealVar('S_dsdsstp', 'S coeff. dsdsstp', 0.)
    D_dsdsstp    = RooRealVar('D_dsdsstp', 'D coeff. dsdsstp', 0.)
    Sbar_dsdsstp    = RooRealVar('Sbar_dsdsstp', 'Sbar coeff. dsdsstp', 0.)
    Dbar_dsdsstp    = RooRealVar('Dbar_dsdsstp', 'Dbar coeff. dsdsstp', 0.)
    
    aProd_dsdsstp   = RooConstVar('aprod_dsdsstp',   'aprod_dsdsstp',   myconfigfile["aprod_dsdsstp"])        # production asymmetry
    aDet_dsdsstp    = RooConstVar('adet_dsdsstp',    'adet_dsdsstp',    myconfigfile["adet_dsdsstp"])         # detector asymmetry
    aTagEff_dsdsstp = RooConstVar('atageff_dsdsstp', 'atageff_dsdsstp', myconfigfile["atageff_dsdsstp"])      # taginng eff asymmetry
    
    #The Lb->Dsp, Lb->Dsstp - mistag
    mistag_dsdsstp = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_dsdsstp.SetName("mistag_dsdsstp")
    
    otherargs_dsdsstp = [ mistagVar_B, mistag_dsdsstp, tagEff_dsdsstp ]
    otherargs_dsdsstp.append(mistagCalibrated)
    otherargs_dsdsstp.append(aProd_dsdsstp)
    otherargs_dsdsstp.append(aDet_dsdsstp)
    otherargs_dsdsstp.append(aTagEff_dsdsstp)

    cosh_dsdsstp = DecRateCoeff('dsdsstp_cosh', 'dsdsstp_cosh', DecRateCoeff.CPEven,
                                fChargeMap, bTagMap,  one,       one,             *otherargs_dsdsstp)
    sinh_dsdsstp = DecRateCoeff('dsdsstp_sinh', 'dsdsstp_sinh', flag | DecRateCoeff.CPEven,
                                fChargeMap, bTagMap,  D_dsdsstp,    Dbar_dsdsstp, *otherargs_dsdsstp)
    cos_dsdsstp  = DecRateCoeff('dsdsstp_cos',  'dsdsstp_cos' , DecRateCoeff.CPOdd,
                                fChargeMap, bTagMap,  C_dsdsstp,    C_dsdsstp,    *otherargs_dsdsstp)
    sin_dsdsstp  = DecRateCoeff('dsdsstp_sin',  'dsdsstp_sin',  flag | DecRateCoeff.CPOdd,
                                fChargeMap, bTagMap,  Sbar_dsdsstp, S_dsdsstp,    *otherargs_dsdsstp)
    
    time_dsdsstp_noacc       = RooBDecay('time_dsdsstp_noacc','time_dsdsstp_noacc', timeVar_B, TauInvLb, zero,
                                         cosh_dsdsstp, sinh_dsdsstp, cos_dsdsstp, sinh_dsdsstp,
                                         zero,trm_dsdsstp, RooBDecay.SingleSided)
    
    time_dsdsstp             = RooEffProd('time_dsdsstp','time_dsdsstp',time_dsdsstp_noacc,tacc_powlaw)
    
    #The Lb->Dsp - true ID
    trueid_dsdsstp = RooGenericPdf("trueid_dsdsstp","exp(-100.*abs(@0-6))",RooArgList(trueIDVar_B))
    
    #The Lb->Dsp, Lb->Dsstp - time error
    terr_dsdsstp = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_dsdsstp.SetName("terr_dsdsstp")
    
    
    #The Lb->Dsp, Lb->Dsstp - total
    timeerr_dsdsstp = RooProdPdf('dsdsstp_timeerr', 'dsdsstp_timeerr',  RooArgSet(terr_dsdsstp),
                                 RooFit.Conditional(RooArgSet(time_dsdsstp),
                                                    RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))

    #------------------------------------------------- Combinatorial ----------------------------------------------------#
    
    #The combinatorics - PIDK
    fracPIDKComb1 = RooRealVar("CombBkg_fracPIDKComb1", "CombBkg_fracPIDKComb1",  myconfigfile["fracPIDKComb1"])
    fracPIDKComb2 = RooRealVar("CombBkg_fracPIDKComb2", "CombBkg_fracPIDKComb2",  myconfigfile["fracPIDKComb2"])
    m = TString("CombK")
    PIDK_combo_K = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("CombPi")
    PIDK_combo_Pi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("CombP")
    PIDK_combo_P = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    name = "ShapePIDKAll_Comb";
    PIDK_combo = RooAddPdf("ShapePIDKAll_combo","ShapePIDKAll_combo",
                           RooArgList(PIDK_combo_K, PIDK_combo_Pi, PIDK_combo_P), RooArgList(fracPIDKComb1, fracPIDKComb2), true)

    #The combinatorics - acceptance - tacc_powlaw
    tacc_combo = tacc_powlaw
    
    #The combinatorics - resolution
    trm_combo = trm
    
    #The combinatorics - time
    tagEff_combo    = RooRealVar("tagEff_combo","tagEff_combo", myconfigfile["tagEff_combo"])
    
    C_combo       = RooRealVar('C_combo', 'C coeff. combo', 1.)
    S_combo       = RooRealVar('S_combo', 'S coeff. combo', 0.)
    D_combo       = RooRealVar('D_combo', 'D coeff. combo', 0.)
    Sbar_combo    = RooRealVar('Sbar_combo', 'Sbar coeff. combo', 0.)
    Dbar_combo    = RooRealVar('Dbar_combo', 'Dbar coeff. combo', 0.)

    aProd_combo   = RooConstVar('aprod_combo',   'aprod_combo',   myconfigfile["aprod_combo"])        # production asymmetry
    aDet_combo    = RooConstVar('adet_combo',    'adet_combo',    myconfigfile["adet_combo"])         # detector asymmetry
    aTagEff_combo = RooConstVar('atageff_combo', 'atageff_combo', myconfigfile["atageff_combo"])      # taginng eff asymmetry

    #The combinatorics - mistag
    mistag_combo = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_combo.SetName("mistag_combo")
    
    otherargs_combo = [ mistagVar_B, mistag_combo, tagEff_combo ]
    otherargs_combo.append(mistagCalibrated)
    otherargs_combo.append(aProd_combo)
    otherargs_combo.append(aDet_combo)
    otherargs_combo.append(aTagEff_combo)
    
    cosh_combo = DecRateCoeff('combo_cosh', 'combo_cosh', DecRateCoeff.CPEven,
                              fChargeMap, bTagMap,  one,        one,        *otherargs_combo)
    sinh_combo = DecRateCoeff('combo_sinh', 'combo_sinh', flag | DecRateCoeff.CPEven,
                              fChargeMap, bTagMap,  D_combo,    Dbar_combo, *otherargs_combo)
    cos_combo  = DecRateCoeff('combo_cos',  'combo_cos' , DecRateCoeff.CPOdd,
                              fChargeMap, bTagMap,  C_combo,    C_combo,    *otherargs_combo)
    sin_combo  = DecRateCoeff('combo_sin',  'combo_sin',  flag | DecRateCoeff.CPOdd,
                              fChargeMap, bTagMap,  Sbar_combo, S_combo,    *otherargs_combo)
    
    time_combo_noacc       = RooBDecay('time_combo_noacc','time_combo_noacc', timeVar_B, TauInvCombo, zero,
                                       cosh_combo, sinh_combo, cos_combo, sin_combo,
                                       zero,trm_combo, RooBDecay.SingleSided)
    
    time_combo             = RooEffProd('time_combo','time_combo',time_combo_noacc, tacc_combo)

    #The combinatorics - true ID
    trueid_combo = RooGenericPdf("trueid_combo","exp(-100.*abs(@0-10))",RooArgList(trueIDVar_B))
    
    #The combinatorics - time error
    terr_combo = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_combo.SetName("terr_combo")
    
    timeerr_combo = RooProdPdf('combo_timeerr', 'combo_timeerr',  RooArgSet(terr_combo),
                               RooFit.Conditional(RooArgSet(time_combo),
                                                  RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))

    #------------------------------------------------- Low mass K ----------------------------------------------------#
    
    #The low mass - mass B
    m = TString("Bs2DsKst")
    massB_lm1 = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug);

    #The low mass - PIDK
    PIDK_lm1 = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug);
            
    #The low mass - acceptance - tacc_powlaw
    tacc_lm1 = tacc_powlaw

    #The low mass - resolution
    trm_lm1 = trm

    #The low mass - time
    ACPobs_lm1 = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"], myconfigfile["ArgLbarfbar_s"], myconfigfile["ModLf_s"])
    
    C_lm1     = RooRealVar('C_lm1','C_lm1',ACPobs_lm1.Cf())
    S_lm1     = RooRealVar('S_lm1','S_lm1',ACPobs_lm1.Sf())
    D_lm1     = RooRealVar('D_lm1','D_lm1',ACPobs_lm1.Df())
    Sbar_lm1  = RooRealVar('Sbar_lm1','Sbar_lm1',ACPobs_lm1.Sfbar())
    Dbar_lm1  = RooRealVar('Dbar_lm1','Dbar_lm1',ACPobs_lm1.Dfbar())
    
    tagEff_lm1    = RooRealVar("tagEff_lm1","tagEff_lm1",myconfigfile["tagEff_lm1"])
    
    aProd_lm1   = RooConstVar('aprod_lm1',   'aprod_lm1',   myconfigfile["aprod_lm1"])        # production asymmetry
    aDet_lm1    = RooConstVar('adet_lm1',    'adet_lm1',    myconfigfile["adet_lm1"])         # detector asymmetry
    aTagEff_lm1 = RooConstVar('atageff_lm1', 'atageff_lm1', myconfigfile["atageff_lm1"])      # taginng eff asymmetry
    
    #The low mass - mistag
    mistag_lm1 = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"),debug)
    mistag_lm1.SetName("mistag_lm1")
    
    otherargs_lm1 = [ mistagVar_B, mistag_lm1, tagEff_lm1 ]
    otherargs_lm1.append(mistagCalibrated)
    otherargs_lm1.append(aProd_lm1)
    otherargs_lm1.append(aDet_lm1)
    otherargs_lm1.append(aTagEff_lm1)

    flag_lm1 = 0 #DecRateCoeff.AvgDelta

    cosh_lm1 = DecRateCoeff('lm1_cosh', 'lm1_cosh', DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  one,      one,      *otherargs_lm1)
    sinh_lm1 = DecRateCoeff('lm1_sinh', 'lm1_sinh', flag_lm1 | DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  D_lm1,    Dbar_lm1, *otherargs_lm1)
    cos_lm1  = DecRateCoeff('lm1_cos',  'lm1_cos' , DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  C_lm1,    C_lm1,    *otherargs_lm1)
    sin_lm1  = DecRateCoeff('lm1_sin',  'lm1_sin',  flag_lm1 | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                            fChargeMap, bTagMap,  S_lm1, Sbar_lm1,    *otherargs_lm1)
    
    time_lm1_noacc       = RooBDecay('time_lm1_noacc','time_lm1_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                     cosh_lm1, sinh_lm1, cos_lm1, sin_lm1,
                                     DeltaMs,trm_lm1, RooBDecay.SingleSided)
    
    
    time_lm1             = RooEffProd('time_lm1','time_lm1',time_lm1_noacc,tacc_lm1)
                                                    
    #The low mass - true ID
    trueid_lm1 = RooGenericPdf("trueid_lm1","exp(-100.*abs(@0-7))",RooArgList(trueIDVar_B))
    
    #The low mass - time error
    terr_lm1 = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_lm1.SetName("terr_lm1")
    
    
    #The low mass - total
    timeerr_lm1 = RooProdPdf('lm1_timeerr', 'lm1_timeerr',  RooArgSet(terr_lm1),
                             RooFit.Conditional(RooArgSet(time_lm1),
                                                RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))

    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

    #The low mass - pi - mass B
    m = TString("Bs2DsstPi")
    massB_dsstpi = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    m = TString("Bs2DsRho")
    massB_dsrho = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    
    frac_g2_1 = RooRealVar("frac_g2_1","frac_g2_1", myconfigfile["frac_g2_1"])
    
    massB_lm2 = RooAddPdf("massB_lm2","massB_lm2",RooArgList(massB_dsstpi,massB_dsrho),RooArgList(frac_g2_1))

    #the low mass - pi - pidk
    m = TString("Bs2DsstPi")
    PIDK_dsstpi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("Bs2DsRho")
    PIDK_dsrho = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    PIDK_lm2 = RooAddPdf("PIDK_lm2","PIDK_lm2",RooArgList(PIDK_dsstpi,PIDK_dsrho),RooArgList(frac_g2_1))
            
    #The low mass - acceptance - tacc_powlaw
    tacc_lm2 = tacc_powlaw
    
    #The low mass - resolution
    trm_lm2 = trm
    
    #The low mass - time
    tagEff_lm2    = RooRealVar("tagEff_lm2","tagEff_lm2",myconfigfile["tagEff_lm2"])
    tagWeight_lm2 = TagEfficiencyWeight('tagWeight_lm2','tagWeight_lm2',bTagMap,tagEff_lm2)
    
    C_lm2    = RooRealVar('C_lm2', 'C coeff. lm2', 1.)
    S_lm2    = RooRealVar('S_lm2', 'S coeff. lm2', 0.)
    D_lm2    = RooRealVar('D_lm2', 'D coeff. lm2', 0.)
    Sbar_lm2    = RooRealVar('Sbar_lm2', 'Sbar coeff. lm2', 0.)
    Dbar_lm2    = RooRealVar('Dbar_lm2', 'Dbar coeff. lm2', 0.)
    
    aProd_lm2   = RooConstVar('aprod_lm2',   'aprod_lm2',   myconfigfile["aprod_lm2"])        # production asymmetry
    aDet_lm2    = RooConstVar('adet_lm2',    'adet_lm2',    myconfigfile["adet_lm2"])         # detector asymmetry
    aTagEff_lm2 = RooConstVar('atageff_lm2', 'atageff_lm2', myconfigfile["atageff_lm2"])      # taginng eff asymmetry
    
    #The low mass - mistag
    mistag_lm2 = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_lm2.SetName("mistag_lm2")
    
    otherargs_lm2 = [ mistagVar_B, mistag_lm2, tagEff_lm2 ]
    otherargs_lm2.append(mistagCalibrated)
    otherargs_lm2.append(aProd_lm2)
    otherargs_lm2.append(aDet_lm2)
    otherargs_lm2.append(aTagEff_lm2)
    
    cosh_lm2 = DecRateCoeff('lm2_cosh', 'lm2_cosh', DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  one,      one,      *otherargs_lm2)
    sinh_lm2 = DecRateCoeff('lm2_sinh', 'lm2_sinh', flag | DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  D_lm2,    Dbar_lm2, *otherargs_lm2)
    cos_lm2  = DecRateCoeff('lm2_cos',  'lm2_cos' , DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  C_lm2,    C_lm2,    *otherargs_lm2)
    sin_lm2  = DecRateCoeff('lm2_sin',  'lm2_sin',  flag | DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  Sbar_lm2, S_lm2,    *otherargs_lm2)
    
    time_lm2_noacc       = RooBDecay('time_lm2_noacc','time_lm2_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                     cosh_lm2, sinh_lm2, cos_lm2, sin_lm2,
                                     DeltaMs,trm_lm2, RooBDecay.SingleSided)
    
    
    time_lm2             = RooEffProd('time_lm2','time_lm2',time_lm2_noacc,tacc_lm2)
    
    #The low mass - true ID true
    trueid_lm2 = RooGenericPdf("trueid_lm2","exp(-100.*abs(@0-8))",RooArgList(trueIDVar_B))
    
    #The low mass - time error
    terr_lm2 = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_lm2.SetName("terr_lm2")

    #The low mass - total
    timeerr_lm2 = RooProdPdf('lm2_timeerr', 'lm2_timeerr',  RooArgSet(terr_lm2),
                             RooFit.Conditional(RooArgSet(time_lm2),
                                                RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
                                    
    
    #------------------------------------------------- Signal -----------------------------------------------------#
    for i in range(0,5):
        #The signal - mass
        
        meanVarBs.append(RooRealVar(   "DblCBBsPDF_mean_%s"%(nameDs2[i]) ,  "mean",    myconfigfile["mean"][i]    ))
        sigma1VarBs.append(RooRealVar( "DblCBBsPDF_sigma1_%s"%(nameDs2[i]), "sigma1",  myconfigfile["sigma1"][i]  ))
        sigma2VarBs.append(RooRealVar( "DblCBBsPDF_sigma2_%s"%(nameDs2[i]), "sigma2",  myconfigfile["sigma2"][i]  ))
        alpha1VarBs.append(RooRealVar( "DblCBBsPDF_alpha1_%s"%(nameDs2[i]), "alpha1",  myconfigfile["alpha1"][i]  ))
        alpha2VarBs.append(RooRealVar( "DblCBBsPDF_alpha2_%s"%(nameDs2[i]), "alpha2",  myconfigfile["alpha2"][i]  ))
        n1VarBs.append(RooRealVar(     "DblCBBsPDF_n1_%s"%(nameDs2[i]),     "n1",      myconfigfile["n1"][i]      ))
        n2VarBs.append(RooRealVar(     "DblCBBsPDF_n2_%s"%(nameDs2[i]),     "n2",      myconfigfile["n2"][i]      ))
        fracVarBs.append(RooRealVar(   "DblCBBsPDF_frac_%s"%(nameDs2[i]),   "frac",    myconfigfile["frac"][i]    ))
    
        num_signal.append(RooRealVar("num_signal_%s"%(nameDs2[i]),"num_signal_%s"%(nameDs2[i]), myconfigfile["num_signal"][i]))
    
        massB_signal.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBs[i],
                                                                        sigma1VarBs[i], alpha1VarBs[i], n1VarBs[i],
                                                                        sigma2VarBs[i], alpha2VarBs[i], n2VarBs[i], fracVarBs[i],
                                                                        num_signal[i], nameDs[i].Data(), "Bs", debug ))
                            
        #The signal - mass Ds
    
        meanVarDs.append(RooRealVar(   "DblCBDsPDF_mean_%s"%(nameDs2[i]) ,  "mean",    myconfigfile["meanDs"][i]    ))
        sigma1VarDs.append(RooRealVar( "DblCBDsPDF_sigma1_%s"%(nameDs2[i]), "sigma1",  myconfigfile["sigma1Ds"][i]  ))
        sigma2VarDs.append(RooRealVar( "DblCBDsPDF_sigma2_%s"%(nameDs2[i]), "sigma2",  myconfigfile["sigma2Ds"][i]  ))
        alpha1VarDs.append(RooRealVar( "DblCBDsPDF_alpha1_%s"%(nameDs2[i]), "alpha1",  myconfigfile["alpha1Ds"][i]  ))
        alpha2VarDs.append(RooRealVar( "DblCBDsPDF_alpha2_%s"%(nameDs2[i]), "alpha2",  myconfigfile["alpha2Ds"][i]  ))
        n1VarDs.append(RooRealVar(     "DblCBDsPDF_n1_%s"%(nameDs2[i]),     "n1",      myconfigfile["n1Ds"][i]      ))
        n2VarDs.append(RooRealVar(     "DblCBDsPDF_n2_%s"%(nameDs2[i]),     "n2",      myconfigfile["n2Ds"][i]      ))
        fracVarDs.append(RooRealVar(   "DblCBDsPDF_frac_%s"%(nameDs2[i]),   "frac",    myconfigfile["fracDs"][i]    ))
        
        massD_signal.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_D, meanVarDs[i],
                                                                        sigma1VarDs[i], alpha1VarDs[i], n1VarDs[i],
                                                                        sigma2VarDs[i], alpha2VarDs[i], n2VarDs[i], fracVarDs[i],
                                                                        num_signal[i], nameDs[i].Data(), "Ds", debug ))
        
        # The signal - PIDK
        m = TString("Bs2DsK_")+nameDs[i]
        PIDK_signal.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug))
        
        # The signal - MDFitter
        MDFitter_signal.append(RooProdPdf("MDFitter_signal_%s"%(nameDs2[i]),"MDFitter_signal",
                                          RooArgList(massB_signal[i], massD_signal[i], PIDK_signal[i])))
        
        timeandmass_signal.append(RooProdPdf("timeandmass_signal_%s"%(nameDs2[i]),"timeandmass_signal",RooArgList(timeerr_signal,
                                                                                                                  MDFitter_signal[i],
                                                                                                                  trueid_signal))) 
    
    
    #-------------------------------------------------- Bd -> DK ----------------------------------------------------#
    
        num_dk.append(RooRealVar("num_dk_%s"%(nameDs2[i]),"num_dk",myconfigfile["num_dk"][i]))
                    
               
        timeandmass_dk.append(RooProdPdf("timeandmass_dk_%s"%(nameDs2[i]),"timeandmass_dk",RooArgList(timeerr_dk,
                                                                                                      MDFitter_dk,
                                                                                                      trueid_dk))) 
    
      
    
    #------------------------------------------------- Bd -> DsK ----------------------------------------------------#
    
        #The Bd->DsK - mass
        meanVarBd.append(RooRealVar(    "DblCBBdPDF_mean_%s"%(nameDs2[i]) ,  "mean",    myconfigfile["mean"][i]-86.8))
        sigma1VarBd.append(RooRealVar( "DblCBBdPDF_sigma1_%s"%(nameDs2[i]), "sigma1",  myconfigfile["sigma1"][i]*myconfigfile["ratio1"] ))
        sigma2VarBd.append(RooRealVar(  "DblCBBdPDF_sigma2_%s"%(nameDs2[i]), "sigma2",  myconfigfile["sigma2"][i]*myconfigfile["ratio2"] ))
    
        num_dsk.append(RooRealVar("num_dsk_%s"%(nameDs[i]),"num_dsk",myconfigfile["num_dsk"][i]))
        
        massB_dsk.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBd[i],
                                                                     sigma1VarBd[i], alpha1VarBs[i], n1VarBs[i],
                                                                     sigma2VarBd[i], alpha2VarBs[i], n2VarBs[i],
                                                                     fracVarBs[i], num_dsk[i], nameDs[i].Data(), "Bd", debug ))
        
        # The signal - MDFitter
        massD_dsk.append(massD_signal[i])
        PIDK_dsk.append(PIDK_signal[i])
                
        MDFitter_dsk.append(RooProdPdf("MDFitter_dsk_%s"%(nameDs2[i]),"MDFitter_dsk",RooArgList(massB_dsk[i], massD_dsk[i], PIDK_dsk[i])))
                         
                
        timeandmass_dsk.append(RooProdPdf("timeandmass_dsk_%s"%(nameDs2[i]),"timeandmass_dsk",RooArgList(timeerr_dsk,
                                                                                                         MDFitter_dsk[i],
                                                                                                         trueid_dsk))) #,
                               
          
    #------------------------------------------------- Bs -> DsPi ----------------------------------------------------# 
    
        #The Bs->DsPi - mass B
        #mass_dspi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBsDsPi_m_down_kkpi"), debug) 
        m = TString("Bs2DsPi_")+nameDs[i]
        massB_dspi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug))
    
        #The Bs->DsPi- mass D
        massD_dspi.append(massD_signal[i])
               
        #The Bs->DsPi - PIDK
        PIDK_dspi.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug))
        
        #The Bs->DsPi - MDFitter
        MDFitter_dspi.append(RooProdPdf("MDFitter_dspi_%s"%(nameDs2[i]),"MDFitter_dspi",RooArgList(massB_dspi[i], massD_dspi[i], PIDK_dspi[i])))
                                 
        num_dspi.append(RooRealVar("num_dspi_%s"%(nameDs2[i]),"num_dspi", myconfigfile["num_dspi"][i]))
        
            
        
        timeandmass_dspi.append(RooProdPdf("timeandmass_dspi_%s"%(nameDs2[i]),"timeandmass_dspi",RooArgList(timeerr_dspi,
                                                                                                            MDFitter_dspi[i],
                                                                                                            trueid_dspi)))
                         
        
              
    #------------------------------------------------- Lb -> LcK ----------------------------------------------------#
    
              
        num_lck.append(RooRealVar("num_lck_%s"%(nameDs2[i]),"num_lck", myconfigfile["num_lck"][i]))
        
              
        timeandmass_lck.append(RooProdPdf("timeandmass_lck_%s"%(nameDs2[i]),"timeandmass_lck",RooArgList(timeerr_lck,
                                                                                                         MDFitter_lck,
                                                                                                         trueid_lck))) 
        
     
        
    #------------------------------------------------- Lb -> Dsp, Dsstp ----------------------------------------------------#
    
               
        num_dsdsstp.append(RooRealVar("num_dsdsstp_%s"%(nameDs2[i]),"num_dsdsstp", myconfigfile["num_dsdsstp"][i]))
        
        #The Lb->Dsp, Lb->Dsstp - mass
        massD_dsdsstp.append(massD_signal[i])
               
                                
        #The Lb->Dsp, Lb->Dsstp - MDFitter
        MDFitter_dsdsstp.append(RooProdPdf("MDFitter_dsdsstp_%s"%(nameDs2[i]),"MDFitter_dsdsstp",
                                           RooArgList(massB_dsdsstp, massD_dsdsstp[i], PIDK_dsdsstp)))
        
                      
        timeandmass_dsdsstp.append(RooProdPdf("timeandmass_dsdsstp_%s"%(nameDs2[i]),"timeandmass_dsdsstp",RooArgList(timeerr_dsdsstp,
                                                                                                                     MDFitter_dsdsstp[i],
                                                                                                                     trueid_dsdsstp)))
        
        
         
    
    #------------------------------------------------- Combinatorial ----------------------------------------------------#

        #The combinatorics - mass
        num_combo.append(RooRealVar("num_combo_%s"%(nameDs2[i]),"num_combo", myconfigfile["num_combo"][i]))
    
        #The combinatorics - mass B
        cBVar.append(RooRealVar("CombBkg_slope_Bs_%s"%(nameDs2[i]),"CombBkg_slope_Bs", myconfigfile["cB"][i]))
        massB_combo.append(RooExponential("massB_combo_%s","massB_combo",massVar_B, cBVar[i]))
        
        #The combinatorics - mass D
        cDVar.append(RooRealVar("CombBkg_slope_Ds_%s"%(nameDs2[i]),"CombBkg_slope_Ds", myconfigfile["cD"][i]))
        fracDsComb.append(RooRealVar("CombBkg_fracDsComb_%s"%(nameDs2[i]), "CombBkg_fracDsComb",  myconfigfile["fracDsComb"][i]))
        massD_combo.append(Bs2Dsh2011TDAnaModels.ObtainComboDs(massVar_D, cDVar[i], fracDsComb[i], massD_signal[i], nameDs[i], debug))
    
        #The combinatorics - MDFitter
        MDFitter_combo.append(RooProdPdf("MDFitter_combo_%s"%(nameDs2[i]),"MDFitter_combo",RooArgList(massB_combo[i], massD_combo[i], PIDK_combo)))
        
              
        timeandmass_combo.append(RooProdPdf("timeandmass_combo_%s"%(nameDs2[i]),"timeandmass_combo",RooArgList(timeerr_combo,
                                                                                                               MDFitter_combo[i],
                                                                                                               trueid_combo))) 
        
        
        #------------------------------------------------- Low mass K ----------------------------------------------------#
    
                
        #The low mass - mass D
        massD_lm1.append(massD_signal[i])
                     
        #The low mass - MDFitter
        MDFitter_lm1.append(RooProdPdf("MDFitter_lm1_%s"%(nameDs2[i]),"MDFitter_lm1",RooArgList(massB_lm1, massD_lm1[i], PIDK_lm1)))
        
        num_lm1.append( RooRealVar("num_lm1_%s"%(nameDs2[i]),"num_lm1",myconfigfile["num_lm1"][i]))
                     
        
        timeandmass_lm1.append(RooProdPdf("timeandmass_lm1_%s"%(nameDs2[i]),"timeandmass_lm1",RooArgList(timeerr_lm1,
                                                                                                         MDFitter_lm1[i],
                                                                                                         trueid_lm1))) 
     
          
    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

        num_lm2.append(RooRealVar("num_lm2_%s"%(nameDs2[i]),"num_lm2", myconfigfile["num_lm2"][i]))
    
        #The low mass - mass D
        massD_lm2.append(massD_signal[i])
             
                
        #The low mass - MDFitter
        MDFitter_lm2.append(RooProdPdf("MDFitter_lm2_%s"%(nameDs[i]),"MDFitter_lm2",RooArgList(massB_lm2, massD_lm2[i], PIDK_lm2)))
        
              
        timeandmass_lm2.append(RooProdPdf("timeandmass_lm2_%s"%(nameDs2[i]),"timeandmass_lm2",RooArgList(timeerr_lm2,
                                                                                                         MDFitter_lm2[i],
                                                                                                         trueid_lm2)))
    
      
    #------------------------------------------------- Total bkg ----------------------------------------------------#
    
        #Total
        total_pdf.append(RooAddPdf("total_pdf_%s"%(nameDs2[i]),"total_pdf",RooArgList(timeandmass_signal[i],
                                                                                      timeandmass_dk[i],timeandmass_dsk[i],timeandmass_dspi[i],
                                                                                      timeandmass_lck[i],timeandmass_dsdsstp[i],
                                                                                      timeandmass_combo[i],timeandmass_lm1[i],timeandmass_lm2[i]),
                                   RooArgList(num_signal[i], num_dk[i],num_dsk[i],num_dspi[i],num_lck[i],
                                              num_dsdsstp[i] ,num_combo[i],num_lm1[i],num_lm2[i])))

        #total_pdf.append(RooAddPdf("total_pdf_%s"%(nameDs2[i]),"total_pdf",RooArgList(timeandmass_signal[i],timeandmass_lck[i]),
        #                           RooArgList(num_signal[i],num_lck[i])))
        
        total_pdf[i].Print("v")

                         
           
    for i in range(0,ntoys) :

        workout = RooWorkspace("workspace","workspace")

        for j in range(0,5):
            
                
            gendata = total_pdf[j].generate(RooArgSet(massVar_B, massVar_D, PIDKVar_B,
                                                      timeVar_B, terrVar_B,
                                                      trueIDVar_B,bTagMap,fChargeMap,mistagVar_B),
                                            )
            
        
            tree = gendata.store().tree()
            dataName = TString("dataSetBsDsK_both_")+nameDs[j]
            
            data = SFitUtils.CopyDataForToys(tree,
                                                  TString(mVar),
                                                  TString(mdVar),
                                                  TString(PIDKVar),
                                                  TString(tVar),
                                                  TString(terrVar),
                                                  TString(tagdec)+TString("_idx"),
                                                  TString(tagomega),
                                                  TString(charge)+TString("_idx"),
                                                  TString(trueID),
                                                  dataName,
                                                  debug)
        
            getattr(workout,'import')(data)
            del gendata
            del tree
            del dataName
            del data 
        
        #Plot what we just did
        if single :
            
            legend = TLegend( 0.70, 0.65, 0.99, 0.99 )
            
            legend.SetTextSize(0.03)
            legend.SetTextFont(12)
            legend.SetFillColor(4000)
            legend.SetShadowColor(0)
            legend.SetBorderSize(0)
            legend.SetTextFont(132)
            legend.SetHeader("Toy generator")
            
            gr = TGraphErrors(10);
            gr.SetName("gr");
            gr.SetLineColor(kBlack);
            gr.SetLineWidth(2);
            gr.SetMarkerStyle(20);
            gr.SetMarkerSize(1.3);
            gr.SetMarkerColor(kBlack);
            gr.Draw("P");
            legend.AddEntry("gr","Generated data","lep");

            l1 = TLine()
            l1.SetLineColor(kRed-7)
            l1.SetLineWidth(4)
            l1.SetLineStyle(kDashed)
            legend.AddEntry(l1, "Signal B_{s}#rightarrow D_{s}K", "L")
            
            l2 = TLine()
            l2.SetLineColor(kRed)
            l2.SetLineWidth(4)
            legend.AddEntry(l2, "B #rightarrow DK", "L")
            
            l3 = TLine()
            l3.SetLineColor(kGreen-3)
            l3.SetLineWidth(4)
            legend.AddEntry(l3, "#Lambda_{b}#rightarrow #Lambda_{c}K", "L")
            
            l4 = TLine()
            l4.SetLineColor(kBlue-6)
            l4.SetLineWidth(4)
            legend.AddEntry(l4, "B_{s}#rightarrow D_{s}^{(*)}(#pi,#rho)", "L")

            l5 = TLine()
            l5.SetLineColor(kOrange)
            l5.SetLineWidth(4)
            legend.AddEntry(l5, "#Lambda_{b} #rightarrow D_{s}^{(*)}p", "L")
            
            l6 = TLine()
            l6.SetLineColor(kBlue-10)
            l6.SetLineWidth(4)
            legend.AddEntry(l6, "B_{(d,s)}#rightarrow D^{(*)}_{s}K^{(*)}", "L")
            
            l7 = TLine()
            l7.SetLineColor(kMagenta-2)
            l7.SetLineWidth(4)
            legend.AddEntry(l7, "Combinatorial", "L")

            
            gStyle.SetOptLogy(1)
            canv_Bmass = TCanvas("canv_Bmass","canv_Bmass", 1200, 1000)
            frame_Bmass = massVar_B.frame()
            frame_Bmass.SetTitle('')
            data[i].plotOn(frame_Bmass,RooFit.Binning(100))
            total_pdf.plotOn(frame_Bmass)
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_signal"),RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dk"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_lck"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_lm1,timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_lm2,timeandmass_dspi"),RooFit.LineColor(kBlue-6))
            #total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dspi"), RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_combo"),RooFit.LineColor(kMagenta-2))
            frame_Bmass.Draw()
            legend.Draw("same")
            canv_Bmass.Print("DsK_Toys_Bmass.pdf") 

            gStyle.SetOptLogy(1)
            canv_Dmass = TCanvas("canv_Dmass","canv_Dmass",1200, 1000)
            frame_Dmass = massVar_D.frame()
            frame_Dmass.SetTitle('')
            data[i].plotOn(frame_Dmass,RooFit.Binning(100))
            total_pdf.plotOn(frame_Dmass)
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_signal"), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dk"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_lck"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_lm1,timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_lm2,timeandmass_dspi"),RooFit.LineColor(kBlue-6))
            #total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dspi"), RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_combo"),RooFit.LineColor(kMagenta-2))
            frame_Dmass.Draw()
            legend.Draw("same")
            canv_Dmass.Print("DsK_Toys_Dmass.pdf")

            gStyle.SetOptLogy(1)
            canv_PIDK = TCanvas("canv_PIDK","canv_PIDK", 1200, 1000)
            frame_PIDK = PIDKVar_B.frame()
            frame_PIDK.SetTitle('')
            data[i].plotOn(frame_PIDK,RooFit.Binning(100))
            total_pdf.plotOn(frame_PIDK)
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_signal"), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dk"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_lck"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_lm1,timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_lm2,timeandmass_dspi"),RooFit.LineColor(kBlue-6))
            #total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dspi"), RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_combo"),RooFit.LineColor(kMagenta-2))
            frame_PIDK.Draw()
            legend.Draw("same")
            canv_PIDK.Print("DsK_Toys_PIDK.pdf")

            gStyle.SetOptLogy(0)
            canv_Bmistag = TCanvas("canv_Bmistag","canv_Btag", 1200, 1000)
            frame_Bmistag = mistagVar_B.frame()
            frame_Bmistag.SetTitle('')
            data[i].plotOn(frame_Bmistag,RooFit.Binning(100))
            frame_Bmistag.Draw()
            canv_Bmistag.Print("DsK_Toys_Bmistag.pdf")

            gStyle.SetOptLogy(0)
            canv_Bterr = TCanvas("canv_Bterr","canv_Bterr", 1200, 1000)
            frame_Bterr = terrVar_B.frame()
            frame_Bterr.SetTitle('')
            data[i].plotOn(frame_Bterr,RooFit.Binning(100))
            total_pdf.plotOn(frame_Bterr)
            frame_Bterr.Draw()
            canv_Bterr.Print("DsK_Toys_TimeErrors.pdf")

            obs = data[i].get()
            tagFName = TString(tagdec)+TString("_idx")
            tagF = obs.find(tagFName.Data())
            gStyle.SetOptLogy(0)
            canv_Btag = TCanvas("canv_Btag","canv_Btag", 1200, 1000)
            frame_Btag = tagF.frame()
            frame_Btag.SetTitle('')
            data[i].plotOn(frame_Btag,RooFit.Binning(5))
            frame_Btag.Draw()
            canv_Btag.Print("DsK_Toys_Tag.pdf")
            
            idFName = TString(charge)+TString("_idx")
            idF = obs.find(idFName.Data())
            gStyle.SetOptLogy(0)
            canv_Bid = TCanvas("canv_Bid","canv_Bid", 1200, 1000)
            frame_Bid = idF.frame()
            frame_Bid.SetTitle('')
            data[i].plotOn(frame_Bid,RooFit.Binning(2))
            frame_Bid.Draw()
            canv_Bid.Print("DsK_Toys_Charge.pdf")
            
            
            gStyle.SetOptLogy(1)
            
            canv_Btime = TCanvas("canv_Btime","canv_Btime", 1200, 1000)
            frame_Btime = timeVar_B.frame()
            frame_Btime.SetTitle('')
            data[i].plotOn(frame_Btime,RooFit.Binning(100))
            #total_pdf.plotOn(frame_Btime)
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_signal"),RooFit.LineStyle(2))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_dk"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lck"),RooFit.LineStyle(1),RooFit.LineColor(3))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm"),RooFit.LineStyle(1),RooFit.LineColor(6))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Btime.Draw()
            canv_Btime.Print("DsK_Toys_Btime.pdf")
        if not single :
            #workout.writeToFile("/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/DsK_Toys_Full_Work_2kSample_"+str(i)+".root")
            workout.writeToFile("/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M/DsK_Toys_Work_"+str(i+900)+".root")
            #outfile  = TFile("/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/DsK_Toys_Full_Tree_2kSample_"+str(i)+".root","RECREATE")
        else :
            workout.writeToFile("Data_Toys_Single_Work_DsK.root")
            outfile  = TFile("Data_Toys_Single_Tree_DsK.root","RECREATE")
        del workout
        #del gendata
        #del data
        #del tree 
        #tree.Write()
        #outfile.Close()
    
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '-s', '--single',
                   dest = 'single',
                   action = 'store_true',
                   default = False,
                                      )
parser.add_option( '--numberOfToys',
                   dest = 'numberOfToys',
                   default = 1000)

parser.add_option( '--numberOfEvents',
                   dest = 'numberOfEvents',
                   default = 7372)


parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsKConfigForGenerator5M')

# -----------------------------------------------------------------------------
if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    import sys
    sys.path.append("../data/")
    
    runBsDsKGenerator( options.debug,  options.single , options.configName, options.numberOfToys, options.numberOfEvents)
    
# -----------------------------------------------------------------------------
                                