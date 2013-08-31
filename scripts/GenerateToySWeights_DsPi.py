# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to generate toys for DsPi                                   #
#                                                                             #
#   Example usage:                                                            #
#      python GenerateToySWeights_DsPi.py                                     #
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

RooRandom.randomGenerator().SetSeed(446829203);
RooAbsData.setDefaultStorageType(RooAbsData.Tree)

RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-2)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-2)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','20Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)


#------------------------------------------------------------------------------
def runBsDsPiGenerator( debug, single, configName, numberOfToys, numberOfEvents ) :
    
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
        
    zero     = RooConstVar('zero', '0', 0.) 
    one      = RooConstVar('one', '1', 1.) 
    minusone = RooConstVar('minusone', '-1', -1.)
    two      = RooConstVar('two', '2', 2.) 

    sam = TString("both")
    mode = TString("phipi")
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
     
    if single :
        ntoys = 1
    else:
        ntoys = int(numberOfToys)

    gendata = []
    data = []

    fileName  = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/work_dspi_pid_53005800_PIDK0_5M_BDTGA.root"
    fileName2 = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    workName  = 'workspace'
    
    mVar     = 'lab0_MassFitConsD_M'
    mdVar    = 'lab2_MM'
    PIDKVar  = 'lab1_PIDK'
    tVar     = 'lab0_LifetimeFit_ctau'
    terrVar  = 'lab0_LifetimeFit_ctauErr'
    trueID   = 'lab0_TRUEID'
    charge   = 'lab1_ID'
    tagdec   = 'lab0_BsTaggingTool_TAGDECISION_OS'
    tagomega = 'lab0_BsTaggingTool_TAGOMEGA_OS'

    
    #Read workspace with PDFs
    workspace = GeneralUtils.LoadWorkspace(TString(fileName),TString(workName),debug)
    workspace.Print("v")
    
    workspace_mistag = GeneralUtils.LoadWorkspace(TString(fileName2),TString(workName), debug)
    workspace_mistag.Print("v")
    
    massVar_B   = GeneralUtils.GetObservable(workspace,TString(mVar), debug)
    massVar_D   = GeneralUtils.GetObservable(workspace,TString(mdVar), debug)
    PIDKVar_B   = GeneralUtils.GetObservable(workspace,TString(PIDKVar), debug)
    timeVar_B   = RooRealVar(tVar,tVar,0.2,15)
    terrVar_B   = RooRealVar(terrVar,terrVar,0.01,0.1)
    trueIDVar_B = RooRealVar(trueID,trueID,0,100) 
    mistagVar_B = GeneralUtils.GetObservable(workspace_mistag,TString(tagomega), debug)
    #mistagVar_B.setMax(1.0)
    
    bTagMap = RooCategory(tagdec, tagdec)
    bTagMap.defineType('B'       ,  1)
    bTagMap.defineType('Bbar'    , -1)
    bTagMap.defineType('Untagged',  0)
    
    fChargeMap = RooCategory(charge, charge)
    fChargeMap.defineType('h+',  1)
    fChargeMap.defineType('h-', -1)

    #The acceptance
    tacc_beta       = RooRealVar('tacc_beta'    , 'tacc_beta',      myconfigfile["tacc_beta"]       )
    tacc_exponent   = RooRealVar('tacc_exponent', 'tacc_exponent',  myconfigfile["tacc_exponent"]   )
    tacc_offset     = RooRealVar('tacc_offset'  , 'tacc_offset',    myconfigfile["tacc_offset"]     )
    tacc_turnon     = RooRealVar('tacc_turnon'  , 'tacc_turnon',    myconfigfile["tacc_turnon"]     )
    tacc            = PowLawAcceptance('tacc', 'tacc', tacc_turnon, timeVar_B, tacc_offset, tacc_exponent, tacc_beta)

    #The time resolution
    trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["resolutionMeanBias"], 'ps' )
    trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', myconfigfile["resolutionScaleFactor"] )
    trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGaussPEDTE', timeVar_B, trm_mean, terrVar_B, trm_scale)

      
    #------------------------------------------------- Signal -----------------------------------------------------#
    
    #The signal - mass Bs
    
    meanVarBs   =  RooRealVar( "DblCBBsPDF_mean" ,  "mean",    myconfigfile["mean"]    )
    sigma1VarBs =  RooRealVar( "DblCBBsPDF_sigma1", "sigma1",  myconfigfile["sigma1"]  ) 
    sigma2VarBs =  RooRealVar( "DblCBBsPDF_sigma2", "sigma2",  myconfigfile["sigma2"]  )
    alpha1VarBs =  RooRealVar( "DblCBBsPDF_alpha1", "alpha1",  myconfigfile["alpha1"]  ) 
    alpha2VarBs =  RooRealVar( "DblCBBsPDF_alpha2", "alpha2",  myconfigfile["alpha2"]  ) 
    n1VarBs     =  RooRealVar( "DblCBBsPDF_n1",     "n1",      myconfigfile["n1"]      ) 
    n2VarBs     =  RooRealVar( "DblCBBsPDF_n2",     "n2",      myconfigfile["n2"]      ) 
    fracVarBs   =  RooRealVar( "DblCBBsPDF_frac",   "frac",    myconfigfile["frac"]    ) 
    
    num_signal  = RooRealVar("num_signal","num_signal", myconfigfile["num_signal"])
    
    massB_signal = Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBs,
                                                               sigma1VarBs, alpha1VarBs, n1VarBs,
                                                               sigma2VarBs, alpha2VarBs, n2VarBs, fracVarBs,
                                                               num_signal, "all", "Bs", debug )
    
    #The signal - mass Ds
        
    meanVarDs   =  RooRealVar( "DblCBDsPDF_mean" ,  "mean",    myconfigfile["meanDs"]    )
    sigma1VarDs =  RooRealVar( "DblCBDsPDF_sigma1", "sigma1",  myconfigfile["sigma1Ds"]  )
    sigma2VarDs =  RooRealVar( "DblCBDsPDF_sigma2", "sigma2",  myconfigfile["sigma2Ds"]  )
    alpha1VarDs =  RooRealVar( "DblCBDsPDF_alpha1", "alpha1",  myconfigfile["alpha1Ds"]  )
    alpha2VarDs =  RooRealVar( "DblCBDsPDF_alpha2", "alpha2",  myconfigfile["alpha2Ds"]  )
    n1VarDs     =  RooRealVar( "DblCBDsPDF_n1",     "n1",      myconfigfile["n1Ds"]      )
    n2VarDs     =  RooRealVar( "DblCBDsPDF_n2",     "n2",      myconfigfile["n2Ds"]      )
    fracVarDs   =  RooRealVar( "DblCBDsPDF_frac",   "frac",    myconfigfile["fracDs"]    )
    
    massD_signal = Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_D, meanVarDs,
                                                               sigma1VarDs, alpha1VarDs, n1VarDs,
                                                               sigma2VarDs, alpha2VarDs, n2VarDs, fracVarDs,
                                                               num_signal, "all", "Ds", debug )
    
    # The signal - PIDK
    
    m = TString("Bs2DsPi_")+mode
    PIDK_signal = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug)
    
    # The signal - MDFitter
    MDFitter_signal = RooProdPdf("MDFitter_signal","MDFitter_signal",RooArgList(massB_signal, massD_signal, PIDK_signal))
    
    #The signal - time error
    terr_signal = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_signal.SetName("terr_signal")
    
    #The signal - time
    tagEff_signal    = RooRealVar("tagEff_signal","tagEff_signal", myconfigfile["tagEff_signal"])
      
    C_signal = RooRealVar('C_signal', 'C coeff.', 1.)
    S_signal = RooRealVar('S_signal', 'S coeff.', 0.)
    D_signal = RooRealVar('D_signal', 'D coeff.', 0.)
    Sbar_signal = RooRealVar('Sbar_signal', 'Sbar coeff.', 0.)
    Dbar_signal = RooRealVar('Dbar_signal', 'Dbar coeff.', 0.)
    
    flag = 0
    aProd_signal   = RooConstVar('aprod_signal',   'aprod_signal',   myconfigfile["aprod_signal"])        # production asymmetry
    aDet_signal    = RooConstVar('adet_signal',    'adet_signal',    myconfigfile["adet_signal"])         # detector asymmetry
    aTagEff_signal = RooConstVar('atageff_signal', 'atageff_signal', myconfigfile["atageff_signal"])      # taginng eff asymmetry
    
    
    calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"])
    calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"])
    avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"])
    
    mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
                                         mistagVar_B, calibration_p0,calibration_p1,avmistag)
    
    #The signal - mistag
    mistag_signal = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_signal.SetName("mistag_signal")
    
    otherargs_signal = [ mistagVar_B, mistag_signal, tagEff_signal ]
    #otherargs_signal = [ tagEff_signal ]
    #otherargs_signal.append(mistagVar_B) 
    otherargs_signal.append(mistagCalibrated)
    otherargs_signal.append(aProd_signal)
    otherargs_signal.append(aDet_signal)
    otherargs_signal.append(aTagEff_signal)
    
    cosh_signal = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven, fChargeMap, bTagMap,
                               one,         one,         *otherargs_signal)
    sinh_signal = DecRateCoeff('signal_sinh', 'signal_sinh', DecRateCoeff.CPEven, fChargeMap, bTagMap,
                               D_signal,    Dbar_signal, *otherargs_signal)
    cos_signal  = DecRateCoeff('signal_cos' , 'signal_cos' , DecRateCoeff.CPOdd,  fChargeMap, bTagMap,
                               C_signal,    C_signal,    *otherargs_signal)
    sin_signal  = DecRateCoeff('signal_sin' , 'signal_sin' , DecRateCoeff.CPOdd,  fChargeMap, bTagMap,
                               Sbar_signal, S_signal,    *otherargs_signal)
    
    time_signal_noacc = RooBDecay('time_signal_noacc','time_signal_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_signal, sinh_signal, cos_signal, sin_signal,
                                  DeltaMs, trm , RooBDecay.SingleSided)
    
    time_signal             = RooEffProd('time_signal','time_signal',time_signal_noacc,tacc)
           
    noncondset = RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )
    timeerr_signal = RooProdPdf('signal_timeerr', 'signal_timeerr',  RooArgSet(terr_signal),
                                RooFit.Conditional(RooArgSet(time_signal),
                                                   RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    #The signal - true ID
    trueid_signal = RooGenericPdf("trueid_signal","exp(-100.*abs(@0-1))",RooArgList(trueIDVar_B))
    
      
    #The signal - total
    #timemistag_signal = RooProdPdf("timemistag_signal","timemistag_signal",RooArgSet(mistag_signal),
    #                               RooFit.Conditional(RooArgSet(time_signal),
    #                                                  RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    timeandmass_signal = RooProdPdf("timeandmass_signal","timeandmass_signal",RooArgList(timeerr_signal,
                                                                                         MDFitter_signal,
                                                                                         trueid_signal)) 
        
     
    #------------------------------------------------- Bd -> DPi -----------------------------------------------------#
    
    #The Bd->DPi - mass
    #mass_dpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DPiPdf_m_down_kpipi"), debug)

    m = TString("Bd2DPi");
    MDFitter_dpi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, debug); 
    num_dpi = RooRealVar("num_dpi","num_dpi",myconfigfile["num_dpi"])
    
    
    #The dpi - time
    #First generate the observables
    ACPobs_dpi = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_d"], myconfigfile["ArgLbarfbar_d"], myconfigfile["ModLf_d"])
    
    C_dpi     = RooRealVar('C_dpi','C_dpi',ACPobs_dpi.Cf())
    S_dpi     = RooRealVar('S_dpi','S_dpi',ACPobs_dpi.Sf())
    D_dpi     = RooRealVar('D_dpi','D_dpi',ACPobs_dpi.Df())
    Sbar_dpi  = RooRealVar('Sbar_dpi','Sbar_dpi',ACPobs_dpi.Sfbar())
    Dbar_dpi  = RooRealVar('Dbar_dpi','Dbar_dpi',ACPobs_dpi.Dfbar())
    
    tagEff_dpi    = RooRealVar("tagEff_dpi","tagEff_dpi",myconfigfile["tagEff_dpi"])
    tagWeight_dpi = TagEfficiencyWeight("tagWeight_dpi","tagWeight_dpi",bTagMap,tagEff_dpi)
    
    aProd_dpi   = RooConstVar('aprod_dpi',   'aprod_dpi',   myconfigfile["aprod_dpi"])        # production asymmetry
    aDet_dpi    = RooConstVar('adet_dpi',    'adet_dpi',    myconfigfile["adet_dpi"])         # detector asymmetry
    aTagEff_dpi = RooConstVar('atageff_dpi', 'atageff_dpi', myconfigfile["atageff_dpi"])      # taginng eff asymmetry
    
    #The Bd->DPi - mistag
    mistag_dpi = mistag_signal
    mistag_dpi.SetName("mistag_dpi")
    
    otherargs_dpi = [ mistagVar_B, mistag_dpi, tagEff_dpi ]
    #otherargs_dpi = [ tagEff_dpi ]
    #otherargs_dpi.append(mistagVar_B)
    otherargs_dpi.append(mistagCalibrated)
    otherargs_dpi.append(aProd_dpi)
    otherargs_dpi.append(aDet_dpi)
    otherargs_dpi.append(aTagEff_dpi)
    
    cosh_dpi = DecRateCoeff('dpi_cosh', 'dpi_cosh', DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  one,      one,      *otherargs_dpi)
    sinh_dpi = DecRateCoeff('dpi_sinh', 'dpi_sinh', flag | DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  D_dpi,    Dbar_dpi, *otherargs_dpi)
    cos_dpi  = DecRateCoeff('dpi_cos',  'dpi_cos' , DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  C_dpi,    C_dpi,    *otherargs_dpi)
    sin_dpi  = DecRateCoeff('dpi_sin',  'dpi_sin',  flag | DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  Sbar_dpi, S_dpi,    *otherargs_dpi)

    time_dpi_noacc = RooBDecay('time_dpi_noacc','time_dpi_noacc', timeVar_B, TauInvGd, DeltaGammad,
                               cosh_dpi, sinh_dpi, cos_dpi, sin_dpi,
                               DeltaMd, trm, RooBDecay.SingleSided)
                                         
    time_dpi = RooEffProd('time_dpi','time_dpi',time_dpi_noacc,tacc)
    
    #The Bd->DPi - time error
    terr_dpi = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_dpi.SetName("terr_dpi")
    
    
    #The Bd->DPi - true ID
    trueid_dpi = RooGenericPdf("trueid_dpi","exp(-100.*abs(@0-2))",RooArgList(trueIDVar_B))        
    
    #The Bd->DPi - total
    #timemistag_dpi  = RooProdPdf("timemistag_dpi","timemistag_dpi",RooArgSet(mistag_dpi),
    #                             RooFit.Conditional(RooArgSet(time_dpi),
    #                                                RooArgSet(timeVar_B,bTagMap,fChargeMap)))   
    
    timeerr_dpi = RooProdPdf('dpi_timeerr', 'dpi_timeerr',  RooArgSet(terr_dpi),
                             RooFit.Conditional(RooArgSet(time_dpi),
                                                RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_dpi = RooProdPdf("timeandmass_dpi","timeandmass_dpi",RooArgList(timeerr_dpi,
                                                                                MDFitter_dpi,
                                                                                trueid_dpi)) 
           
    
    #------------------------------------------------- Bd -> DsPi ----------------------------------------------------#
    
    #The Bd->DsPi - mass
    meanVarBd   =  RooRealVar( "DblCBBdPDF_mean" ,  "mean",    myconfigfile["mean"]-86.8)
    sigma1VarBd =  RooRealVar( "DblCBBdPDF_sigma1", "sigma1",  myconfigfile["sigma1"]*myconfigfile["ratio1"] )
    sigma2VarBd =  RooRealVar( "DblCBBdPDF_sigma2", "sigma2",  myconfigfile["sigma2"]*myconfigfile["ratio2"] )
    
    num_bddspi = RooRealVar("num_dspi","num_dspi",myconfigfile["num_dspi"])
    massB_bddspi= Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBd, sigma1VarBd, alpha1VarBs, n1VarBs, sigma2VarBd, alpha2VarBs,
                                                              n2VarBs, fracVarBs, num_bddspi, "bddspi", "Bd", debug )
    
    # The signal - MDFitter
    massD_bddspi = massD_signal
    massD_bddspi.SetName("massD_bddspi")
    PIDK_bddspi = PIDK_signal
    PIDK_bddspi.SetName("PIDK_bddspi")
    
    MDFitter_bddspi = RooProdPdf("MDFitter_bddspi","MDFitter_bddspi",RooArgList(massB_bddspi, massD_bddspi, PIDK_bddspi))
    
      
    #The Bd->DsPi - time
    #First generate the observables
    tagEff_bddspi    = RooRealVar("tagEff_bddspi","tagEff_bddspi",myconfigfile["tagEff_dspi"])
    tagWeight_bddspi = TagEfficiencyWeight('tagWeight_bddspi','tagWeight_bddspi',bTagMap,tagEff_bddspi)
    
    C_bddspi    = RooRealVar('C_bddspi', 'C coeff. bddspi', 1.)
    S_bddspi    = RooRealVar('S_bddspi', 'S coeff. bddspi', 0.) 
    D_bddspi    = RooRealVar('D_bddspi', 'D coeff. bddspi', 0.)
    Sbar_bddspi    = RooRealVar('S_bddspi', 'S coeff. bddspi', 0.)
    Dbar_bddspi    = RooRealVar('D_bddspi', 'D coeff. bddspi', 0.)
    
    
    aProd_bddspi   = RooConstVar('aprod_bddspi',   'aprod_bddspi',   myconfigfile["aprod_bddspi"])        # production asymmetry
    aDet_bddspi    = RooConstVar('adet_bddspi',    'adet_bddspi',    myconfigfile["adet_bddspi"])         # detector asymmetry
    aTagEff_bddspi = RooConstVar('atageff_bddspi', 'atageff_bddspi', myconfigfile["atageff_bddspi"])      # taginng eff asymmetry
    
    #The Bd->DsPi - mistag
    mistag_bddspi = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_bddspi.SetName("mistag_bddspi")
    
    otherargs_bddspi = [ mistagVar_B, mistag_bddspi, tagEff_bddspi ]       
    #otherargs_bddspi = [ tagEff_bddspi ]
    #otherargs_bddspi.append(mistagVar_B)
    otherargs_bddspi.append(mistagCalibrated)
    otherargs_bddspi.append(aProd_bddspi)
    otherargs_bddspi.append(aDet_bddspi)
    otherargs_bddspi.append(aTagEff_bddspi)
    
    cosh_bddspi = DecRateCoeff('bddspi_cosh', 'bddspi_cosh', DecRateCoeff.CPEven,
                               fChargeMap, bTagMap,  one,       one,           *otherargs_bddspi)
    sinh_bddspi = DecRateCoeff('bddspi_sinh', 'bddspi_sinh', flag | DecRateCoeff.CPEven,
                               fChargeMap, bTagMap,  D_bddspi,    Dbar_bddspi, *otherargs_bddspi)
    cos_bddspi  = DecRateCoeff('bddspi_cos',  'bddspi_cos' , DecRateCoeff.CPOdd,
                               fChargeMap, bTagMap,  C_bddspi,    C_bddspi,    *otherargs_bddspi)
    sin_bddspi  = DecRateCoeff('bddspi_sin',  'bddspi_sin',  flag | DecRateCoeff.CPOdd,
                               fChargeMap, bTagMap,  Sbar_bddspi, S_bddspi,    *otherargs_bddspi)
    
    time_bddspi_noacc = RooBDecay('time_bddspi_noacc','time_bddspi_noacc', timeVar_B, TauInvGd, DeltaGammad,
                                  cosh_bddspi, sinh_bddspi, cos_bddspi, sin_bddspi,
                                  DeltaMd, trm, RooBDecay.SingleSided)
    
    time_bddspi             = RooEffProd('time_bddspi','time_bddspi',time_bddspi_noacc,tacc)
    
    #The Bd->DsPi - time error
    terr_bddspi = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_bddspi.SetName("terr_bddspi")
    
    
    #The Bd->DsPi - true ID
    trueid_bddspi = RooGenericPdf("trueid_bddspi","exp(-100.*abs(@0-3))",RooArgList(trueIDVar_B))        
    
    #The Bd->DsPi - total
    #timemistag_bddspi  = RooProdPdf("timemistag_bddspi","timemistag_bddspi",RooArgSet(mistag_bddspi),
    #                                RooFit.Conditional(RooArgSet(time_bddspi),
    #                                                   RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    timeerr_bddspi = RooProdPdf('bddspi_timeerr', 'bddspi_timeerr',  RooArgSet(terr_bddspi),
                                RooFit.Conditional(RooArgSet(time_bddspi),
                                                   RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_bddspi = RooProdPdf("timeandmass_bddspi","timeandmass_bddspi",RooArgList(timeerr_bddspi,
                                                                                         MDFitter_bddspi,
                                                                                         trueid_bddspi)) #,
        
    #------------------------------------------------- Lb -> LcPi -----------------------------------------------------#
    
    #The Lb->LcPi - mass
    #mass_lcpi =  Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgLb2LcPiPdf_m_both"), debug)
    m = TString("Lb2LcPi");
    MDFitter_lcpi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, debug);
    
    num_lcpi = RooRealVar("num_lcpi","num_lcpi", myconfigfile["num_lcpi"])
    
       
    #The Lb->LcPi - time
    tagEff_lcpi    = RooRealVar("tagEff_lcpi","tagEff_lcpi",myconfigfile["tagEff_lcpi"])
    tagWeight_lcpi = TagEfficiencyWeight('tagWeight_lcpi','tagWeight_lcpi',bTagMap,tagEff_lcpi)
    
    C_lcpi       = RooRealVar('C_lcpi', 'C coeff. lcpi', 1.)
    S_lcpi       = RooRealVar('S_lcpi', 'S coeff. lcpi', 0.)
    D_lcpi       = RooRealVar('D_lcpi', 'D coeff. lcpi', 0.)
    Sbar_lcpi    = RooRealVar('Sbar_lcpi', 'Sbar coeff. lcpi', 0.)
    Dbar_lcpi    = RooRealVar('Dbar_lcpi', 'Dbar coeff. lcpi', 0.)
    
    aProd_lcpi   = RooConstVar('aprod_lcpi',   'aprod_lcpi',   myconfigfile["aprod_lcpi"])        # production asymmetry
    aDet_lcpi    = RooConstVar('adet_lcpi',    'adet_lcpi',    myconfigfile["adet_lcpi"])         # detector asymmetry
    aTagEff_lcpi = RooConstVar('atageff_lcpi', 'atageff_lcpi', myconfigfile["atageff_lcpi"])      # taginng eff asymmetry
    
    #The Lb->LcPi - mistag
    mistag_lcpi = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_lcpi.SetName("mistag_lcpi")
    
    
    otherargs_lcpi = [ mistagVar_B, mistag_lcpi, tagEff_lcpi ]       
    #otherargs_lcpi = [ tagEff_lcpi ]
    #otherargs_lcpi.append(mistagVar_B)
    otherargs_lcpi.append(mistagCalibrated)
    otherargs_lcpi.append(aProd_lcpi)
    otherargs_lcpi.append(aDet_lcpi)
    otherargs_lcpi.append(aTagEff_lcpi)
    
    
    cosh_lcpi = DecRateCoeff('lcpi_cosh', 'lcpi_cosh', DecRateCoeff.CPEven,
                             fChargeMap, bTagMap,  one,       one,      *otherargs_lcpi)
    sinh_lcpi = DecRateCoeff('lcpi_sinh', 'lcpi_sinh', flag | DecRateCoeff.CPEven,
                             fChargeMap, bTagMap,  D_lcpi,    Dbar_lcpi, *otherargs_lcpi)
    cos_lcpi  = DecRateCoeff('lcpi_cos',  'lcpi_cos' , DecRateCoeff.CPOdd,
                             fChargeMap, bTagMap,  C_lcpi,    C_lcpi,    *otherargs_lcpi)
    sin_lcpi  = DecRateCoeff('lcpi_sin',  'lcpi_sin',  flag | DecRateCoeff.CPOdd,
                             fChargeMap, bTagMap,  Sbar_lcpi, S_lcpi,    *otherargs_lcpi)
    
    time_lcpi_noacc = RooBDecay('time_lcpi_noacc','time_lcpi_noacc', timeVar_B, TauInvLb, zero,
                                cosh_lcpi, sinh_lcpi, cos_lcpi, sin_lcpi,
                                zero, trm, RooBDecay.SingleSided)
    
    
    time_lcpi             = RooEffProd('time_lcpi','time_lcpi',time_lcpi_noacc,tacc)
    
    #The Lb->LcPi - time error
    terr_lcpi = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_lcpi.SetName("terr_lcpi")
    
    #The Lb->LcPi - true ID
    trueid_lcpi = RooGenericPdf("trueid_lcpi","exp(-100.*abs(@0-4))",RooArgList(trueIDVar_B))
    
    #The Lb->LcPi - total
    #timemistag_lcpi  = RooProdPdf("timemistag_lcpi","timemistag_lcpi",RooArgSet(mistag_lcpi),
    #                              RooFit.Conditional(RooArgSet(time_lcpi),
    #                                                 RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    timeerr_lcpi = RooProdPdf('lcpi_timeerr', 'lcpi_timeerr',  RooArgSet(terr_lcpi),
                              RooFit.Conditional(RooArgSet(time_lcpi),
                                                 RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_lcpi = RooProdPdf("timeandmass_lcpi","timeandmass_lcpi",RooArgList(timeerr_lcpi,
                                                                                   MDFitter_lcpi,
                                                                                   trueid_lcpi)) #,
    #terr_lcpi))
    
    #------------------------------------------------- Combinatorial -----------------------------------------------------#
    
    #The combinatorics - mass
    #exposlope_combo = RooRealVar("exposlope_combo","exposlope_combo", myconfigfile["exposlope_combo"])
    #mass_combo = RooExponential("mass_combo","mass_combo",massVar_B,exposlope_combo)
    num_combo = RooRealVar("num_combo","num_combo", myconfigfile["num_combo"])
    
    #The combinatorics - mass B
    cB1Var = RooRealVar("CombBkg_slope_Bs1","CombBkg_slope_Bs1", myconfigfile["cB1"])
    cB2Var = RooRealVar("CombBkg_slope_Bs2","CombBkg_slope_Bs2", myconfigfile["cB2"])
    fracBsComb = RooRealVar("CombBkg_fracBsComb", "CombBkg_fracBsComb",  myconfigfile["fracBsComb"])
    massB_combo = Bs2Dsh2011TDAnaModels.ObtainComboBs(massVar_B, cB1Var, cB2Var, fracBsComb, mode, debug)
    
    #The combinatorics - mass D
    cDVar = RooRealVar("CombBkg_slope_Ds","CombBkg_slope_Ds", myconfigfile["cD"])
    fracDsComb = RooRealVar("CombBkg_fracDsComb", "CombBkg_fracDsComb",  myconfigfile["fracDsComb"])
    massD_combo = Bs2Dsh2011TDAnaModels.ObtainComboDs(massVar_D, cDVar, fracDsComb, massD_signal, mode, debug)
    
    #The combinatorics - PIDK
    fracPIDKComb = RooRealVar("CombBkg_fracPIDKComb", "CombBkg_fracPIDKComb",  myconfigfile["fracPIDKComb"])
    m = TString("Comb")
    PIDK1_combo = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("CombK")
    PIDK2_combo = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    name = "ShapePIDKAll_Comb";
    PIDK_combo = RooAddPdf("ShapePIDKAll_combo","ShapePIDKAll_combo", PIDK1_combo, PIDK2_combo, fracPIDKComb)
    
    #The combinatorics - MDFitter
    MDFitter_combo = RooProdPdf("MDFitter_combo","MDFitter_combo",RooArgList(massB_combo, massD_combo, PIDK_combo))
           
    #The combinatorics - time
    tagEff_combo    = RooRealVar("tagEff_combo","tagEff_combo", myconfigfile["tagEff_combo"])
    tagWeight_combo = TagEfficiencyWeight('tagWeight_combo','tagWeight_combo',bTagMap,tagEff_combo)
    
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
    #otherargs_combo = [ tagEff_combo ]
    #otherargs_combo.append(mistagVar_B)
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
    
    time_combo_noacc = RooBDecay('time_combo_noacc','time_combo_noacc', timeVar_B, TauInvCombo, zero,
                                 cosh_combo, sinh_combo, cos_combo, sin_combo,
                                 zero, trm, RooBDecay.SingleSided)
    
    time_combo             = RooEffProd('time_combo','time_combo',time_combo_noacc,tacc)
    
    #The combinatorics - true ID
    trueid_combo = RooGenericPdf("trueid_combo","exp(-100.*abs(@0-10))",RooArgList(trueIDVar_B))
    
    
    #The combinatorics - time error
    terr_combo = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_combo.SetName("terr_combo")
    
    
    #The combinatorics - total
    #timemistag_combo  = RooProdPdf("timemistag_combo","timemistag_combo",RooArgSet(mistag_combo),
    #                               RooFit.Conditional(RooArgSet(time_combo),
    #                                                  RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    timeerr_combo = RooProdPdf('combo_timeerr', 'combo_timeerr',  RooArgSet(terr_combo),
                               RooFit.Conditional(RooArgSet(time_combo),
                                                  RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_combo = RooProdPdf("timeandmass_combo","timeandmass_combo",RooArgList(timeerr_combo,
                                                                                      MDFitter_combo,
                                                                                      trueid_combo)) #,
        
    #------------------------------------------------- Low Mass Bs-------------------------------------------------------#

    #The low mass - mass
    num_lm1 = RooRealVar("num_lm1","num_lm1", myconfigfile["num_lm1"])
    
    #mass_dsstpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstPiPdf_m_both"), debug)
    #mass_dsrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsRhoPdf_m_both"), debug)
    #mass_dsstrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstRhoPdf_m_both"), debug)
    
    m = TString("Bs2DsstPi");
    massB_dsstpi = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug);
    massD_dsstpi = massD_signal
    massD_dsstpi.SetName("massD_dsstpi")
    PIDK_dsstpi = PIDK_signal
    PIDK_dsstpi.SetName("PIDK_dsstpi")
    
    MDFitter_dsstpi = RooProdPdf("MDFitter_dsstpi","MDFitter_dsstpi",RooArgList(massB_dsstpi, massD_dsstpi, PIDK_dsstpi))
    
    
    #frac_g1_1 = RooRealVar("frac_g1_1","frac_g1_1", myconfigfile["frac_g1_1"])
    #frac_g1_2 = RooRealVar("frac_g1_2","frac_g1_2", myconfigfile["frac_g1_2"])
    #total_lm1 = RooAddPdf("total_lm1","total_lm1",RooArgList(mass_dsstpi,mass_dsrho,mass_dsstrho),RooArgList(frac_g1_1, frac_g1_2))
    
       
    #The low mass - time
    tagEff_lm1    = RooRealVar("tagEff_lm1","tagEff_lm1", myconfigfile["tagEff_lm1"])
    tagWeight_lm1 = TagEfficiencyWeight('tagWeight_lm1','tagWeight_lm1',bTagMap,tagEff_lm1)
    
    C_lm1    = RooRealVar('C_lm1', 'C coeff. lm1', 1.)
    S_lm1    = RooRealVar('S_lm1', 'S coeff. lm1', 0.)
    D_lm1    = RooRealVar('D_lm1', 'D coeff. lm1', 0.)
    Sbar_lm1    = RooRealVar('Sbar_lm1', 'Sbar coeff. lm1', 0.)
    Dbar_lm1    = RooRealVar('Dbar_lm1', 'Dbar coeff. lm1', 0.)
    
    
    aProd_lm1   = RooConstVar('aprod_lm1',   'aprod_lm1',   myconfigfile["aprod_lm1"])        # production asymmetry
    aDet_lm1    = RooConstVar('adet_lm1',    'adet_lm1',    myconfigfile["adet_lm1"])         # detector asymmetry
    aTagEff_lm1 = RooConstVar('atageff_lm1', 'atageff_lm1', myconfigfile["atageff_lm1"])      # taginng eff asymmetry
    
    #The low mass - mistag
    mistag_lm1 = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"),debug)
    mistag_lm1.SetName("mistag_lm1")
    
    
    otherargs_lm1 = [ mistagVar_B, mistag_lm1, tagEff_lm1 ]       
    #otherargs_lm1 = [ tagEff_lm1 ]
    #otherargs_lm1.append(mistagVar_B)
    otherargs_lm1.append(mistagCalibrated)
    otherargs_lm1.append(aProd_lm1)
    otherargs_lm1.append(aDet_lm1)
    otherargs_lm1.append(aTagEff_lm1)
    
    cosh_lm1 = DecRateCoeff('lm1_cosh', 'lm1_cosh', DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  one,      one,      *otherargs_lm1)
    sinh_lm1 = DecRateCoeff('lm1_sinh', 'lm1_sinh', flag | DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  D_lm1,    Dbar_lm1, *otherargs_lm1)
    cos_lm1  = DecRateCoeff('lm1_cos',  'lm1_cos' , DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  C_lm1,    C_lm1,    *otherargs_lm1)
    sin_lm1  = DecRateCoeff('lm1_sin',  'lm1_sin',  flag | DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  Sbar_lm1, S_lm1,    *otherargs_lm1)
    
    time_lm1_noacc = RooBDecay('time_lm1_noacc','time_lm1_noacc', timeVar_B, TauInvGs, DeltaGammas,
                         cosh_lm1, sinh_lm1, cos_lm1, sin_lm1,
                         DeltaMs, trm, RooBDecay.SingleSided)
      
    time_lm1 = RooEffProd('time_lm1','time_lm1',time_lm1_noacc,tacc)
    
    
    #The low mass - time error
    terr_lm1 = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_lm1.SetName("terr_lm1")
    
    
    #The low mass - true ID
    trueid_lm1 = RooGenericPdf("trueid_lm1","exp(-100.*abs(@0-5))",RooArgList(trueIDVar_B))
    
    #The low mass - total
    #timemistag_lm1  = RooProdPdf("timemistag_lm1","timemistag_lm1",RooArgSet(total_mistag_lm1),
    #                             RooFit.Conditional(RooArgSet(time_lm1),
    #                                                RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    timeerr_lm1 = RooProdPdf('lm1_timeerr', 'lm1_timeerr',  RooArgSet(terr_lm1),
                             RooFit.Conditional(RooArgSet(time_lm1),
                                                RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_lm1 = RooProdPdf("timeandmass_lm1","timeandmass_lm1",RooArgList(timeerr_lm1,
                                                                                MDFitter_dsstpi,
                                                                                trueid_lm1)) #,
    ##terr_lm1))
    
    #------------------------------------------------- Low Mass Bd-------------------------------------------------------#
    '''
    mass_bddrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DRhoPdf_m_both"), debug)
    mass_bddstpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DstPiPdf_m_both"), debug)
    mass_bddsstpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DsstPiPdf_m_both"), debug)
    
    frac_g2_1 = RooRealVar("frac_g2_1","frac_g2_1", myconfigfile["frac_g2_1"])
    frac_g2_2 = RooRealVar("frac_g2_2","frac_g2_2", myconfigfile["frac_g2_1"])
    
    total_lm2 = RooAddPdf("total_lm2","total_lm2",RooArgList(mass_bddsstpi,mass_bddstpi,mass_bddrho),RooArgList(frac_g2_1, frac_g2_2))
    num_lm2 = RooRealVar("num_lm2","num_lm2", myconfigfile["num_lm2"])
    
      
    #The low mass - time
    #First generate the observables
    ACPobs_lm2 = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_d"], myconfigfile["ArgLbarfbar_d"], myconfigfile["ModLf_d"])
    
    tagEff_lm2    = RooRealVar("tagEff_lm2","tagEff_lm2", myconfigfile["tagEff_lm2"])
    tagWeight_lm2 = TagEfficiencyWeight("tagWeight_lm2","tagWeight_lm2",bTagMap,tagEff_lm2)
    
    
    C_lm2     = RooRealVar('C_lm2','C_lm2',ACPobs_lm2.Cf())
    S_lm2     = RooRealVar('S_lm2','S_lm2',ACPobs_lm2.Sf())
    D_lm2     = RooRealVar('D_lm2','D_lm2',ACPobs_lm2.Df())
    Sbar_lm2  = RooRealVar('Sbar_lm2','Sbar_lm2',ACPobs_lm2.Sfbar())
    Dbar_lm2  = RooRealVar('Dbar_lm2','Dbar_lm2',ACPobs_lm2.Dfbar())
    
    aProd_lm2   = RooConstVar('aprod_lm2',   'aprod_lm2',   myconfigfile["aprod_lm2"])        # production asymmetry
    aDet_lm2    = RooConstVar('adet_lm2',    'adet_lm2',    myconfigfile["adet_lm2"])         # detector asymmetry
    aTagEff_lm2 = RooConstVar('atageff_lm2', 'atageff_lm2', myconfigfile["atageff_lm2"])      # taginng eff asymmetry
    
    #The low mass - mistag
    total_mistag_lm2 = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    total_mistag_lm2.SetName("mistag_lm2")
    
    otherargs_lm2 = [ mistagVar_B, mistag_lm2, tagEff_lm2 ]       
    #otherargs_lm2 = [ tagEff_lm2 ]
    #otherargs_lm2.append(mistagVar_B)
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
    
    time_lm2_noacc = RooBDecay('time_lm2_noacc','time_lm2_noacc', timeVar_B, TauInvGd, DeltaGammad,
    cosh_lm2, sinh_lm2, cos_lm2, sin_lm2,
    DeltaMd,trm, RooBDecay.SingleSided)

    time_lm2 = RooEffProd('time_lm2','time_lm2',time_lm2_noacc,tacc)   
     
    #The low mass - time error
    terr_lm2 = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_lm2.SetName("terr_lm2")
    

    #The low mass - true ID
    trueid_lm2 = RooGenericPdf("trueid_lm2","exp(-100.*abs(@0-6))",RooArgList(trueIDVar_B))
    
    #The low mass - total
    #timemistag_lm2  = RooProdPdf("timemistag_lm2","timemistag_lm2",RooArgSet(total_mistag_lm2),
    #                             RooFit.Conditional(RooArgSet(time_lm2),
    #                                                RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    timeerr_lm2 = RooProdPdf('lm2_timeerr', 'lm2_timeerr',  RooArgSet(terr_lm2),
    RooFit.Conditional(RooArgSet(time_lm2),
    RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_lm2 = RooProdPdf("timeandmass_lm2","timeandmass_lm2",RooArgList(timeerr_lm2,
    total_lm2,
    trueid_lm2)) #,
    #terr_lm2))       
    '''
    
    #------------------------------------------------- Bs->DsK  -----------------------------------------------------#
    
    m = TString("Bs2DsK");
    MDFitter_dsk = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, debug);
    
    num_dsk = RooRealVar("num_dsk","num_dsk", myconfigfile["num_dsk"])
            
    #The Bs->DsK - time
    ACPobs_dsk = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"], myconfigfile["ArgLbarfbar_s"], myconfigfile["ModLf_s"])
    ACPobs_dsk.printtable()
    
    C_dsk     = RooRealVar('C_dsk','C_dsk',ACPobs_dsk.Cf())
    S_dsk     = RooRealVar('S_dsk','S_dsk',ACPobs_dsk.Sf())
    D_dsk     = RooRealVar('D_dsk','D_dsk',ACPobs_dsk.Df())
    Sbar_dsk  = RooRealVar('Sbar_dsk','Sbar_dsk',ACPobs_dsk.Sfbar())
    Dbar_dsk  = RooRealVar('Dbar_dsk','Dbar_dsk',ACPobs_dsk.Dfbar())
    
    tagEff_dsk    = RooRealVar("tagEff_dsk","tagEff_dsk", myconfigfile["tagEff_dsk"])
    tagWeight_dsk = TagEfficiencyWeight("tagWeight_dsk","tagWeight_dsk",bTagMap,tagEff_dsk)
    
    aProd_dsk   = RooConstVar('aprod_dsk',   'aprod_dsk',   myconfigfile["aprod_dsk"])        # production asymmetry
    aDet_dsk    = RooConstVar('adet_dsk',    'adet_dsk',    myconfigfile["adet_dsk"])         # detector asymmetry
    aTagEff_dsk = RooConstVar('atageff_dsk', 'atageff_dsk', myconfigfile["atageff_dsk"])      # taginng eff asymmetry
    
    #The Bs->DsK - mistag
    mistag_dsk = mistag_signal #Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_dsk.SetName("mistag_dsk")
    
    otherargs_dsk = [ mistagVar_B, mistag_dsk, tagEff_dsk ]       
    otherargs_dsk.append(mistagCalibrated)
    otherargs_dsk.append(aProd_dsk)
    otherargs_dsk.append(aDet_dsk)
    otherargs_dsk.append(aTagEff_dsk)
    
    flag_dsk = 0 #DecRateCoeff.AvgDelta
    
    cosh_dsk = DecRateCoeff('dsk_cosh', 'dsk_cosh', DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  one,      one,      *otherargs_dsk)
    sinh_dsk = DecRateCoeff('dsk_sinh', 'dsk_sinh', flag_dsk | DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  D_dsk,    Dbar_dsk, *otherargs_dsk)
    cos_dsk  = DecRateCoeff('dsk_cos',  'dsk_cos' , DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  C_dsk,    C_dsk,    *otherargs_dsk)
    sin_dsk  = DecRateCoeff('dsk_sin',  'dsk_sin',  flag_dsk | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                            fChargeMap, bTagMap,  S_dsk, Sbar_dsk,    *otherargs_dsk)
    
    time_dsk_noacc = RooBDecay('time_dsk_noacc','time_dsk_noacc', timeVar_B, TauInvGs, DeltaGammas,
                               cosh_dsk, sinh_dsk, cos_dsk, sin_dsk,
                               DeltaMs, trm, RooBDecay.SingleSided)
    
    time_dsk = RooEffProd('time_dsk','time_dsk',time_dsk_noacc,tacc)
    
    #The Bs->DsK - true ID
    trueid_dsk = RooGenericPdf("trueid_dsk","exp(-100.*abs(@0-7))",RooArgList(trueIDVar_B))
    
    
    #The Bs->DsK - time error
    terr_dsk = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_dsk.SetName("terr_dsk")
    
    
    #The Bs->DsK - total
    #timemistag_dsk = RooProdPdf("timemistag_dsk","timemistag_dsk",RooArgSet(mistag_dsk),
    #                            RooFit.Conditional(RooArgSet(time_dsk),
    #                                               RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    timeerr_dsk = RooProdPdf('dsk_timeerr', 'dsk_timeerr',  RooArgSet(terr_dsk),
                             RooFit.Conditional(RooArgSet(time_dsk),
                                                RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_dsk = RooProdPdf("timeandmass_dsk","timeandmass_dsk",RooArgList(timeerr_dsk,
                                                                                MDFitter_dsk,
                                                                                trueid_dsk)) #,
    #terr_dsk)) 
    
    
    #------------------------------------------------- Total bkg -----------------------------------------------------#
    
    #Total background
    #total_back_pdf = RooAddPdf("total_back_pdf","total_back_pdf",
    #                           RooArgList(timeandmass_dpi,timeandmass_lcpi,timeandmass_combo, timeandmass_bddspi, timeandmass_lm1, timeandmass_lm2),
    #                           RooArgList(num_dpi,num_lcpi,num_combo, num_bddspi, num_lm1, num_lm2))

    total_pdf = RooAddPdf("total_pdf","total_back_pdf",
                          RooArgList(timeandmass_signal, timeandmass_dpi,timeandmass_lcpi,
                                     timeandmass_combo, timeandmass_bddspi, timeandmass_lm1,
                                     timeandmass_dsk),
                          RooArgList(num_signal, num_dpi, num_lcpi, num_combo, num_bddspi, num_lm1, num_dsk))
    
    
    #Total
    #total_pdf = RooAddPdf("total_pdf","total_pdf",RooArgList(etimeandmass_signal,total_back_pdf))
    #getattr(workout,'import')(total_pdf)

    
    for i in range(0,ntoys) :
        
        #Create out workspace
        workout = RooWorkspace("workspace","workspace")

        getattr(workout,'import')(total_pdf)
                
        #Generate
        gendata.append(total_pdf.generate(RooArgSet(massVar_B, massVar_D, PIDKVar_B,
                                                    timeVar_B, terrVar_B,
                                                    trueIDVar_B, bTagMap, fChargeMap, mistagVar_B),
                                          int(numberOfEvents+100)))
        print gendata[i].numEntries()
        tree = gendata[i].store().tree()
        
        data.append(SFitUtils.CopyDataForToys(tree,
                                              TString(mVar),
                                              TString(mdVar),
                                              TString(PIDKVar),
                                              TString(tVar),
                                              TString(terrVar),
                                              TString(tagdec)+TString("_idx"),
                                              TString(tagomega),
                                              TString(charge)+TString("_idx"),
                                              TString(trueID),
                                              TString("dataSetBsDsPi_toys"), debug))
       
        getattr(workout,'import')(data[i])
                                                                            

        #exit(0)
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
            legend.AddEntry(l1, "Signal B_{s}#rightarrow D_{s}#pi", "L")

            l2 = TLine()
            l2.SetLineColor(kOrange-2)
            l2.SetLineWidth(4)
            legend.AddEntry(l2, "B #rightarrow D#pi", "L")

            l3 = TLine()
            l3.SetLineColor(kRed)
            l3.SetLineWidth(4)
            legend.AddEntry(l3, "#Lambda_{b}#rightarrow #Lambda_{c}#pi", "L")

            l4 = TLine()
            l4.SetLineColor(kBlue-10)
            l4.SetLineWidth(4)
            legend.AddEntry(l4, "B_{s}#rightarrow D_{s}^{(*)}(#pi,#rho)", "L")
                                                
            l5 = TLine()
            l5.SetLineColor(kGreen+3)
            l5.SetLineWidth(4)
            legend.AddEntry(l5, "B_{s}#rightarrow D_{s}K", "L")

            l6 = TLine()
            l6.SetLineColor(kMagenta-2)
            l6.SetLineWidth(4)
            legend.AddEntry(l6, "B_{d}#rightarrow D_{s}#pi", "L")
            
            l7 = TLine()
            l7.SetLineColor(kBlue-6)
            l7.SetLineWidth(4)
            legend.AddEntry(l7, "Combinatorial", "L")
                                                


            gStyle.SetOptLogy(1)
            canv_Bmass = TCanvas("canv_Bmass","canv_Bmass", 1200, 1000)
            frame_Bmass = massVar_B.frame()
            frame_Bmass.SetTitle('')
            data[i].plotOn(frame_Bmass,RooFit.Binning(100))
            total_pdf.plotOn(frame_Bmass)
            total_pdf.plotOn(frame_Bmass,RooFit.Components("DblCBPDFBsall"),RooFit.LineStyle(2), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgBd2DPiPdf_m_both_kpipi"),RooFit.LineColor(kOrange-2))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgLb2LcPiPdf_m_both"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgBs2DsstPiPdf_m_both"),RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_Bmass,RooFit.Components("total_lm2"),RooFit.LineColor(7))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgBs2DsKPdf_m_both"),RooFit.LineColor(kGreen+3))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("DblCBPDFBdbddspi"),RooFit.LineColor(kMagenta-2))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("CombBkgPDF_phipi"),RooFit.LineColor(kBlue-6))
            frame_Bmass.Draw()
            legend.Draw("same")
            canv_Bmass.Print("DsPi_Toys_Bmass.pdf")

            gStyle.SetOptLogy(0)
            canv_Bmistag = TCanvas("canv_Bmistag","canv_Bmistag", 1200, 1000)
            frame_Bmistag = mistagVar_B.frame()
            frame_Bmistag.SetTitle('')
            data[i].plotOn(frame_Bmistag,RooFit.Binning(100))
            #mistag_signal.plotOn(frame_Bmistag)
            #total_pdf.plotOn(frame_Bmistag)
            #total_pdf.plotOn(frame_Bmistag,RooFit.Components("mistag_signal"),RooFit.LineStyle(2), RooFit.LineColor(kRed-7))
            #total_pdf.plotOn(frame_Bmistag,RooFit.Components("mistag_dpi"),RooFit.LineColor(kOrange-2))
            #total_pdf.plotOn(frame_Bmistag,RooFit.Components("mistag_lcpi"),RooFit.LineColor(kRed))
            #total_pdf.plotOn(frame_Bmistag,RooFit.Components("mistag_lm1"),RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_Bmistag,RooFit.Components("mistag_lm2"),RooFit.LineColor(7))
            #total_pdf.plotOn(frame_Bmistag,RooFit.Components("mistag_dsk"),RooFit.LineColor(kGreen+3))
            #total_pdf.plotOn(frame_Bmistag,RooFit.Components("mistag_bddspi"),RooFit.LineColor(kMagenta-2))
            #total_pdf.plotOn(frame_Bmistag,RooFit.Components("mistag_combo"),RooFit.LineColor(kBlue-6))
            frame_Bmistag.Draw()
            canv_Bmistag.Print("DsPi_Toys_Bmistag.pdf")


            gStyle.SetOptLogy(0)
            canv_Btrueid = TCanvas("canv_Btrueid","canv_Btrueid", 1200, 1000)
            frame_Btrueid = trueIDVar_B.frame()
            frame_Btrueid.SetTitle('')
            data[i].plotOn(frame_Btrueid,RooFit.Binning(10))
            total_pdf.plotOn(frame_Btrueid)
            total_pdf.plotOn(frame_Btrueid,RooFit.Components("trueid_signal"),RooFit.LineStyle(2), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Btrueid,RooFit.Components("trueid_dpi"),RooFit.LineColor(kOrange-2))
            total_pdf.plotOn(frame_Btrueid,RooFit.Components("trueid_lcpi"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Btrueid,RooFit.Components("trueid_lm1"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_Btrueid,RooFit.Components("trueid_lm2"),RooFit.LineColor(7))
            total_pdf.plotOn(frame_Btrueid,RooFit.Components("trueid_dsk"),RooFit.LineColor(kGreen+3))
            total_pdf.plotOn(frame_Btrueid,RooFit.Components("trueid_bddspi"),RooFit.LineColor(kMagenta-2))
            total_pdf.plotOn(frame_Btrueid,RooFit.Components("trueid_combo"),RooFit.LineColor(kBlue-6))
            frame_Btrueid.Draw()
            canv_Btrueid.Print("DsPi_Toys_TrueID.pdf")
                                                                                                                                                    
            
            gStyle.SetOptLogy(1)
            canv_Dmass = TCanvas("canv_Dmass","canv_Dmass",1200, 1000)
            frame_Dmass = massVar_D.frame()
            frame_Dmass.SetTitle('')
            data[i].plotOn(frame_Dmass,RooFit.Binning(100))
            total_pdf.plotOn(frame_Dmass)
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_signal"), RooFit.LineStyle(2), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("PhysBkgBd2DPiPdf_m_both_kpipi_Ds"),RooFit.LineColor(kOrange-2))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("PhysBkgLb2LcPiPdf_m_both_Ds"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("MDFitter_dsstpi"), RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_Dmass,RooFit.Components("total_lm2"), RooFit.LineColor(7))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("PhysBkgBs2DsKPdf_m_both_Ds"), RooFit.LineColor(kGreen+3))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_bddspi"), RooFit.LineColor(kMagenta-2))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("CombBkgPDF_phipi_Ds"), RooFit.LineColor(kBlue-6))
            frame_Dmass.Draw()
            legend.Draw("same")
            canv_Dmass.Print("DsPi_Toys_Dmass.pdf")

            gStyle.SetOptLogy(1)
            canv_PIDK = TCanvas("canv_PIDK","canv_PIDK", 1200, 1000)
            frame_PIDK = PIDKVar_B.frame()
            frame_PIDK.SetTitle('')
            data[i].plotOn(frame_PIDK,RooFit.Binning(100))
            total_pdf.plotOn(frame_PIDK)
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_signal"),RooFit.LineStyle(2), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("PIDKShape_Bd2DPi_both"), RooFit.LineColor(kOrange-2))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("PIDKShape_Lb2LcPi_both"), RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("MDFitter_dsstpi"), RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_PIDK,RooFit.Components("total_lm2"), RooFit.LineColor(7))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("PIDKShape_Bs2DsK_both"), RooFit.LineColor(kGreen+3))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_bddspi"), RooFit.LineColor(kMagenta-2))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("ShapePIDKAll_combo"), RooFit.LineColor(kBlue-6))
            frame_PIDK.Draw()
            legend.Draw("same")
            canv_PIDK.Print("DsPi_Toys_PIDK.pdf")

            obs = data[i].get()
            tagFName = TString(tagdec)+TString("_idx")
            tagF = obs.find(tagFName.Data())
            gStyle.SetOptLogy(0)
            canv_Btag = TCanvas("canv_Btag","canv_Btag", 1200, 1000)
            frame_Btag = tagF.frame()
            frame_Btag.SetTitle('')
            data[i].plotOn(frame_Btag,RooFit.Binning(5))
            frame_Btag.Draw()
            canv_Btag.Print("DsPi_Toys_Tag.pdf")

            idFName = TString(charge)+TString("_idx")
            idF = obs.find(idFName.Data())
            gStyle.SetOptLogy(0)
            canv_Bid = TCanvas("canv_Bid","canv_Bid", 1200, 1000)
            frame_Bid = idF.frame()
            frame_Bid.SetTitle('')
            data[i].plotOn(frame_Bid,RooFit.Binning(2))
            frame_Bid.Draw()
            canv_Bid.Print("DsPi_Toys_Charge.pdf")
                                                                                                                        

            gStyle.SetOptLogy(0)
            canv_Bterr = TCanvas("canv_Bterr","canv_Bterr", 1200, 1000)
            frame_Bterr = terrVar_B.frame()
            frame_Bterr.SetTitle('')
            data[i].plotOn(frame_Bterr,RooFit.Binning(100))
            total_pdf.plotOn(frame_Bterr)
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_dpi"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_bddspi"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_lcpi"),RooFit.LineStyle(1),RooFit.LineColor(3))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm1"),RooFit.LineStyle(1),RooFit.LineColor(6))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm2"),RooFit.LineStyle(1),RooFit.LineColor(7))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Bterr.Draw()
            canv_Bterr.Print("DsPi_Toys_TimeErrors.pdf")
                                                                                                                                                            

                                                                                                                                         
            gStyle.SetOptLogy(1)
            canv_Btime = TCanvas("canv_Btime","canv_Btime", 1200, 1000)
            frame_Btime = timeVar_B.frame()
            frame_Btime.SetTitle('')
            data[i].plotOn(frame_Btime,RooFit.Binning(100))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_dpi"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_bddspi"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lcpi"),RooFit.LineStyle(1),RooFit.LineColor(3))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm1"),RooFit.LineStyle(1),RooFit.LineColor(6))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm2"),RooFit.LineStyle(1),RooFit.LineColor(7))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Btime.Draw()
            canv_Btime.Print("DsPi_Toys_Time.pdf")
            
            
        if not single :
            #workout.writeToFile("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/DsPi_Toys_Full_Work_"+str(i)+".root")
            #outfile  = TFile("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/DsPi_Toys_Full_Tree_"+str(i)+".root","RECREATE")
            workout.writeToFile("/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/PETE/DsPi_Toys_Work_"+str(i+750)+".root")
            #outfile  = TFile("/afs/cern.ch/work/a/adudziak/public/DsPiToys/DsPi_Toys_Tree_"+str(i)+".root","RECREATE")
            
        else :
            workout.writeToFile("Data_Toys_Single_Work_DsPi.root")
            outfile  = TFile("Data_Toys_Single_Tree_DsPi.root","RECREATE")
            #workout.Print('v')    
        del workout
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
                   default = 250)

parser.add_option( '--numberOfEvents',
                   dest = 'numberOfEvents',
                   default = 43466)

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsPiConfigForGenerator')

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
            
    import sys
    sys.path.append("../data/")
        
    runBsDsPiGenerator( options.debug,  options.single , options.configName, options.numberOfToys, options.numberOfEvents)

# -----------------------------------------------------------------------------
                                        
