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


RooRandom.randomGenerator().SetSeed(6757867824)#97783461)#93637445714)#204573)#4378678643)3421128394);
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
                                                                    


    Gammad       = RooRealVar('Gammad','Gammad', myconfigfile["Gammad"])                     # in ps^{-1}
    Gammas       = RooRealVar('Gammas','Gammas', myconfigfile["Gammas"])                     # in ps^{-1}
    DeltaGammad  = RooRealVar('DeltaGammad','DeltaGammad', myconfigfile["DeltaGammad"])      # in ps^{-1}
    DeltaGammas  = RooRealVar('DeltaGammas','DeltaGammas', myconfigfile["DeltaGammas"])      # in ps^{-1}
    DeltaMd      = RooRealVar('DeltaMd','DeltaMd', myconfigfile["DeltaMd"])                  # in ps^{-1}
    DeltaMs      = RooRealVar('DeltaMs','DeltaMs', myconfigfile["DeltaMs"])                  # in ps^{-1}
                        
    GammaLb      = RooRealVar('GammaLb','GammaLb',myconfigfile["GammaLb"])
    GammaCombo   = RooRealVar('GammaCombo','GammaCombo',myconfigfile["GammaCombo"])
        
    TauRes       = RooRealVar('TauRes','TauRes',myconfigfile["TauRes"])
        
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
    
    fileName  = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/work_dsk_pid_53005800_PIDK5_5M_BDTGA.root"
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
    massVar_B  = GeneralUtils.GetObservable(workspace,TString(mVar), debug)
    trueIDVar_B = RooRealVar(trueID,trueID,0,100)
    mistagVar_B = GeneralUtils.GetObservable(workspace_mistag,TString(tagomega), debug)
    #mistagVar_B.setMax(1.0)

    import GaudiPython
    GaudiPython.loaddict('B2DXFittersDict')
    #trm = PTResModels.getPTResolutionModel("TripleGaussian",timeVar_B, 'Bs', False,1.15)
    trm = RooGaussModel('PTRMGaussian_signal','PTRMGaussian_signal',timeVar_B, zero, TauRes)

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
    
    #------------------------------------------------- Signal -----------------------------------------------------#
    
    #The signal - mass
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
    m = TString("Bs2DsK_")+mode
    PIDK_signal = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug)
    
    # The signal - MDFitter
    MDFitter_signal = RooProdPdf("MDFitter_signal","MDFitter_signal",RooArgList(massB_signal, massD_signal, PIDK_signal))
    
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
    tagWeight_signal = TagEfficiencyWeight("tagWeight_signal","tagWeight_signal",bTagMap,tagEff_signal)
    
    aProd_signal   = RooConstVar('aprod_signal',   'aprod_signal',   myconfigfile["aprod_signal"])        # production asymmetry
    aDet_signal    = RooConstVar('adet_signal',    'adet_signal',    myconfigfile["adet_signal"])         # detector asymmetry
    aTagEff_signal = RooConstVar('atageff_signal', 'atageff_signal', myconfigfile["atageff_signal"])      # taginng eff asymmetry
    
    #The Bs->DsK - mistag
    mistag_signal = mistag #Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("MistagPdf_signal_BDTGA"), debug)
    mistag_signal.SetName("mistag_signal")
    
    #flag_signal = DecRateCoeff.AvgDelta
    flag_signal = 0
    flag = 0
    
    otherargs_signal = [ mistagVar_B, mistag_signal, tagEff_signal ]
    #otherargs_signal = [ tagEff_signal ]
    #otherargs_signal.append(mistagVar_B)
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
    
    time_signal_noacc       = RooBDecay('time_signal_noacc','time_signal_noacc', timeVar_B, Gammas, DeltaGammas,
                                        cosh_signal, sinh_signal, cos_signal, sin_signal,
                                        DeltaMs,trm_signal, RooBDecay.SingleSided)
    

    '''
    untaggedWeight_signal   = IfThreeWayCat('untaggedWeight_signal', 'untaggedWeight_signal', bTagMap, one, two, one)
    Dilution_signal         = RooFormulaVar('Dilution_signal',"1-2*@0",RooArgList(mistagVar_B))
    mixState_signal         = RooFormulaVar('mixState_signal','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    weightedDs_signal       = IfThreeWayCat('weightedDs_signal', 'weightedDs_signal',fChargeMap, D_signal, zero, Dbar_signal)
    weightedSs_signal       = IfThreeWayCat('weightedSs_signal', 'weightedSs_signal',fChargeMap, S_signal, zero, Sbar_signal)    
    
    CosSin_i0_signal        = RooProduct('CosSin_i0_signal', 'CosSin_i0_signal', RooArgSet(mixState_signal, Dilution_signal, tagWeight_signal))
    
    CE_signal               = RooRealVar("CE_signal","CE_signal",1 + myconfigfile["prodasy_signal"]*myconfigfile["tageffasy_signal"])
    CO_signal               = RooRealVar("CO_signal","CO_signal", myconfigfile["prodasy_signal"] + myconfigfile["tageffasy_signal"])
    
    CPOddFact_signal        = RooFormulaVar("CPOddFact_signal","@2+@0*@1",RooArgList(CosSin_i0_signal,CE_signal,CO_signal))
    CPEvenFact_signal       = RooFormulaVar("CPEvenFact_signal","@1+@0*@2",RooArgList(CosSin_i0_signal,CE_signal,CO_signal))
    
    Cos_signal              = RooProduct('Cos_signal', 'Cos signal', RooArgSet(CPOddFact_signal,C_signal))
    Cosh_signal             = RooProduct('Cosh_signal', 'cosh coefficient signal', RooArgSet(untaggedWeight_signal, tagWeight_signal,CPEvenFact_signal))
    Sin_signal              = RooProduct('Sin_signal', 'Sin signal', RooArgSet(CPOddFact_signal,weightedSs_signal,minusone))
    Sinh_signal             = RooProduct('Sinh_signal','Sinh_signal',RooArgSet(Cosh_signal,weightedDs_signal))    
    
    time_signal_noacc       = RooBDecay('time_signal_noacc','time_signal_noacc', timeVar_B, Gammas, DeltaGammas, 
    Cosh_signal, Sinh_signal, Cos_signal, Sin_signal,
    DeltaMs,trm_signal, RooBDecay.SingleSided)
    '''
        
    time_signal             = RooEffProd('time_signal','time_signal',time_signal_noacc,tacc_powlaw)
    
    #The signal - true ID
    trueid_signal = RooGenericPdf("trueid_signal","exp(-100.*abs(@0-1))",RooArgList(trueIDVar_B))
    
    
    #The signal - total
    #timemistag_signal = RooProdPdf("timemistag_signal","timemistag_signal",RooArgSet(mistag_signal),
    #                               RooFit.Conditional(RooArgSet(time_signal),
    #                                                  RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    #timeandmass_signal = RooProdPdf("timeandmass_signal","timeandmass_signal",RooArgList(timemistag_signal,edoubleCB_signal,trueid_signal))
    
    
    #The Bs->DsK - total
    timeerr_signal = RooProdPdf('signal_timeerr', 'signal_timeerr',  RooArgSet(terr_signal),
                                RooFit.Conditional(RooArgSet(time_signal),
                                                   RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_signal = RooProdPdf("timeandmass_signal","timeandmass_signal",RooArgList(timeerr_signal,
                                                                                         MDFitter_signal,
                                                                                         trueid_signal)) 
    
    
    #-------------------------------------------------- Bd -> DK ----------------------------------------------------#
    
    #The Bd->DK - mass
    #mass_dk = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DKPdf_m_both"), debug)
    m = TString("Bd2DK")
    MDFitter_dk = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, debug)
    num_dk = RooRealVar("num_dk","num_dk",myconfigfile["num_dk"])
    
    #The Bd->DK - acceptance - tacc_powlaw 
    tacc_dk = tacc_powlaw
    
    #The Bd->DK - resolution
    trm_dk = trm
    
    #The Bd->DK - time
    tagEff_dk    = RooRealVar("tagEff_dk","tagEff_dk", myconfigfile["tagEff_dk"])
    tagWeight_dk = TagEfficiencyWeight('tagWeight_dk','tagWeight_dk',bTagMap,tagEff_dk)
    
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
    #otherargs_dk = [ tagEff_dk ]
    #otherargs_dk.append(mistagVar_B)
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
    
    time_dk_noacc       = RooBDecay('time_dk_noacc','time_dk_noacc', timeVar_B, Gammad, DeltaGammad,
                                    cosh_dk, sinh_dk, cos_dk, sin_dk,
                                    DeltaMd, trm_dk, RooBDecay.SingleSided)
    
    
    '''
    untaggedWeight_dk   = IfThreeWayCat('untaggedWeight_dk', 'untaggedWeight_dk', bTagMap, one, two, one)
    Dilution_dk         = RooFormulaVar('Dilution_dk',"1-2*@0",RooArgList(mistagVar_B))
    mixState_dk         = RooFormulaVar('mixState_dk','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    CE_dk               = RooRealVar("CE_dk","CE_dk",1 + myconfigfile["prodasy_dk"]*myconfigfile["tageffasy_dk"])
    CO_dk               = RooRealVar("CO_dk","CO_dk",myconfigfile["prodasy_signal"] + myconfigfile["tageffasy_signal"])
    
    CosSin_i0_dk        = RooProduct('sigCosSin_i0_dk', 'sigCosSin_i0 dk', RooArgSet(mixState_dk, Dilution_dk, tagWeight_dk))
    
    CPOddFact_dk        = RooFormulaVar("CPOddFact_dk","@2+@0*@1",RooArgList(CosSin_i0_dk,CE_dk,CO_dk))    
    CPEvenFact_dk       = RooFormulaVar("CPEvenFact_dk","@1+@0*@2",RooArgList(CosSin_i0_dk,CE_dk,CO_dk))
    
    Cos_dk              = CPOddFact_dk
    
    Cosh_dk             = RooProduct('sigCosh_dk', 'cosh coefficient dk',
    RooArgSet(CPEvenFact_dk,untaggedWeight_dk, tagWeight_dk))
    
    time_dk_noacc       = RooBDecay('time_dk_noacc','time_dk_noacc', timeVar_B, Gammad, DeltaGammad,
    Cosh_dk, D_dk, Cos_dk, S_dk,
    DeltaMd,trm_dk, RooBDecay.SingleSided)
    '''
    
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
    
    timeandmass_dk = RooProdPdf("timeandmass_dk","timeandmass_dk",RooArgList(timeerr_dk,
                                                                             MDFitter_dk,
                                                                             trueid_dk)) 
    
    
    
    #timemistag_dk = RooProdPdf("timemistag_dk","timemistag_dk",RooArgSet(mistag_dk),
    #                           RooFit.Conditional(RooArgSet(time_dk),
    #                                              RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
    #timeandmass_dk = RooProdPdf("timeandmass_dk","timeandmass_dk",RooArgList(timemistag_dk,mass_dk,trueid_dk))
    #------------------------------------------------- Bd -> DsK ----------------------------------------------------#
    
    #The Bd->DsK - mass
    meanVarBd   =  RooRealVar( "DblCBBdPDF_mean" ,  "mean",    myconfigfile["mean"]-86.8)
    sigma1VarBd =  RooRealVar( "DblCBBdPDF_sigma1", "sigma1",  myconfigfile["sigma1"]*myconfigfile["ratio1"] )
    sigma2VarBd =  RooRealVar( "DblCBBdPDF_sigma2", "sigma2",  myconfigfile["sigma2"]*myconfigfile["ratio2"] )
    
    num_dsk = RooRealVar("num_dsk","num_dsk",myconfigfile["num_dsk"])
    
    massB_dsk = Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBd, sigma1VarBd, alpha1VarBs, n1VarBs, sigma2VarBd, alpha2VarBs,
                                                            n2VarBs, fracVarBs, num_dsk, "bddsk", "Bd", debug )
    
    # The signal - MDFitter
    massD_dsk = massD_signal
    massD_dsk.SetName("massD_dsk")
    PIDK_dsk = PIDK_signal
    PIDK_dsk.SetName("PIDK_dsk")
    
    MDFitter_dsk = RooProdPdf("MDFitter_dsk","MDFitter_dsk",RooArgList(massB_dsk, massD_dsk, PIDK_dsk))
    
    
    #The Bd->DsK - acceptance - tacc_powlaw
    tacc_dsk = tacc_powlaw
    
    #The Bd->DsK - resolution
    trm_dsk = trm
    
    #The Bd->DsK - time
    tagEff_dsk    = RooRealVar("tagEff_dsk","tagEff_dsk",myconfigfile["tagEff_dsk"])
    tagWeight_dsk = TagEfficiencyWeight('tagWeight_dsk','tagWeight_dsk',bTagMap,tagEff_dsk)
    
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
    #otherargs_dsk = [ tagEff_dsk ]
    #otherargs_dsk.append(mistagVar_B)
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
    
    time_dsk_noacc       = RooBDecay('time_dsk_noacc','time_dsk_noacc', timeVar_B, Gammad, DeltaGammad,
                                     cosh_dsk, sinh_dsk, cos_dsk, sin_dsk,
                                     DeltaMd,trm_dsk, RooBDecay.SingleSided)
    
    
    
    '''
    untaggedWeight_dsk   = IfThreeWayCat('untaggedWeight_dsk', 'untaggedWeight_dsk', bTagMap, one, two, one)
    Dilution_dsk         = RooFormulaVar('Dilution_dsk',"1-2*@0",RooArgList(mistagVar_B))
    mixState_dsk         = RooFormulaVar('mixState_dsk','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    CosSin_i0_dsk        = RooProduct('sigCosSin_i0_dsk', 'sigCosSin_i0 dsk', RooArgSet(mixState_dsk, Dilution_dsk, tagWeight_dsk))
    
    CE_dsk               = RooRealVar("CE_dsk","CE_dsk",1 + myconfigfile["prodasy_dsk"]*myconfigfile["tageffasy_dsk"])
    CO_dsk               = RooRealVar("CO_dsk","CO_dsk", myconfigfile["prodasy_dsk"] + myconfigfile["tageffasy_dsk"])
    
    CPOddFact_dsk        = RooFormulaVar("CPOddFact_dsk","@2+@0*@1",RooArgList(CosSin_i0_dsk,CE_dsk,CO_dsk))
    CPEvenFact_dsk       = RooFormulaVar("CPEvenFact_dsk","@1+@0*@2",RooArgList(CosSin_i0_dsk,CE_dsk,CO_dsk))
    
    Cos_dsk              = CPOddFact_dsk
    
    Cosh_dsk             = RooProduct('sigCosh_dsk', 'cosh coefficient dsk',
    RooArgSet(CPEvenFact_dsk,untaggedWeight_dsk, tagWeight_dsk))
    
    time_dsk_noacc       = RooBDecay('time_dsk_noacc','time_dsk_noacc', timeVar_B, Gammad, DeltaGammad,
    Cosh_dsk, D_dsk, Cos_dsk, S_dsk,
    DeltaMd,trm_dsk, RooBDecay.SingleSided)
    '''
    
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
    
    timeandmass_dsk = RooProdPdf("timeandmass_dsk","timeandmass_dsk",RooArgList(timeerr_dsk,
                                                                                MDFitter_dsk,
                                                                                trueid_dsk)) #,
    
    
    #timemistag_dsk = RooProdPdf("timemistag_dsk","timemistag_dsk",RooArgSet(mistag_dsk), 
    #                            RooFit.Conditional(RooArgSet(time_dsk),
    #                                               RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    #timeandmass_dsk = RooProdPdf("timeandmass_dsk","timeandmass_dsk",RooArgList(timemistag_dsk,mass_dsk,trueid_dsk))
        
    #------------------------------------------------- Bs -> DsPi ----------------------------------------------------# 
    
    #The Bs->DsPi - mass B
    #mass_dspi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBsDsPi_m_down_kkpi"), debug) 
    m = TString("Bs2DsPi_phipi")
    massB_dspi = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    
    #The Bs->DsPi- mass D
    massD_dspi = massD_signal
    massD_dspi.SetName("massD_dspi")
    
    #The Bs->DsPi - PIDK
    PIDK_dspi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug)
    
    #The Bs->DsPi - MDFitter
    MDFitter_dspi =  RooProdPdf("MDFitter_dspi","MDFitter_dspi",RooArgList(massB_dspi, massD_dspi, PIDK_dspi))
    
    num_dspi = RooRealVar("num_dspi","num_dspi", myconfigfile["num_dspi"])
    
    #The Bs->DsPi - acceptance - tacc_powlaw
    tacc_dspi = tacc_powlaw
    
    #The Bs->DsPi - resolution
    trm_dspi = trm
    
    #The Bs->DsPi - time
    tagEff_dspi    = RooRealVar("tagEff_signal","tagEff_signal", myconfigfile["tagEff_dspi"])
    tagWeight_dspi = TagEfficiencyWeight('tagWeight_dspi','tagWeight_dspi',bTagMap,tagEff_dspi)
    
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
    #otherargs_dspi = [ tagEff_dspi ]
    #otherargs_dspi.append(mistagVar_B)
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
    
    time_dspi_noacc       = RooBDecay('time_dspi_noacc','time_dspi_noacc', timeVar_B, Gammas, DeltaGammas,
                                      cosh_dspi, sinh_dspi, cos_dspi, sin_dspi,
                                      DeltaMs, trm_dspi, RooBDecay.SingleSided)
    
    
    '''
    untaggedWeight_dspi   = IfThreeWayCat('untaggedWeight_dspi', 'untaggedWeight_dspi', bTagMap, one, two, one)
    Dilution_dspi         = RooFormulaVar('Dilution_dspi',"1-2*@0",RooArgList(mistagVar_B))
    mixState_dspi         = RooFormulaVar('mixState_dspi','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    CE_dspi               = RooRealVar("CE_dspi","CE_dspi",1 + myconfigfile["prodasy_dspi"]*myconfigfile["tageffasy_dspi"])
    CO_dspi               = RooRealVar("CO_dspi","CO_dspi", myconfigfile["prodasy_dspi"] + myconfigfile["tageffasy_dspi"])
    
    CosSin_i0_dspi        = RooProduct('sigCosSin_i0_dspi', 'sigCosSin_i0 dspi', RooArgSet(mixState_dspi, Dilution_dspi, tagWeight_dspi))
    
    CPOddFact_dspi        = RooFormulaVar("CPOddFact_dspi","@2+@0*@1",RooArgList(CosSin_i0_dspi,CE_dspi,CO_dspi))
    CPEvenFact_dspi       = RooFormulaVar("CPEvenFact_dspi","@1+@0*@2",RooArgList(CosSin_i0_dspi,CE_dspi,CO_dspi))
    
    Cos_dspi              = CPOddFact_dspi
    
    Cosh_dspi             = RooProduct('sigCosh_dspi', 'cosh coefficient dspi',
    RooArgSet(CPEvenFact_dspi,untaggedWeight_dspi, tagWeight_dspi))   
    
    time_dspi_noacc       = RooBDecay('time_dspi_noacc','time_dspi_noacc', timeVar_B, Gammas, DeltaGammas,
    Cosh_dspi, D_dspi, Cos_dspi, S_dspi,
    DeltaMs,trm_dspi, RooBDecay.SingleSided)
    '''
        
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
        
    
    timeandmass_dspi = RooProdPdf("timeandmass_dspi","timeandmass_dspi",RooArgList(timeerr_dspi,
                                                                                   MDFitter_dspi,
                                                                                   trueid_dspi)) #,
    
    
    #timemistag_dspi = RooProdPdf("timemistag_dspi","timemistag_dspi",RooArgSet(mistag_dspi),
    #                             RooFit.Conditional(RooArgSet(time_dspi),
    #                                                RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
    #timeandmass_dspi = RooProdPdf("timeandmass_dspi","timeandmass_dspi",RooArgList(timemistag_dspi,mass_dspi,trueid_dspi))
        
    #------------------------------------------------- Lb -> LcK ----------------------------------------------------#
    
    #The Lb->LcK - mass
    #mass_lck = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgLb2LcKPdf_m_both"), debug)
    m = TString("Lb2LcK");
    MDFitter_lck = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, debug);
    
    num_lck = RooRealVar("num_lck","num_lck", myconfigfile["num_lck"])
    
    #The Lb->LcK - acceptance - tacc_powlaw
    tacc_lck = tacc_powlaw
        
    #The Lb->LcK - resolution
    trm_lck = trm
    
    #The Lb->LcK - time
    tagEff_lck    = RooRealVar("tagEff_lck","tagEff_lck", myconfigfile["tagEff_lck"])
    tagWeight_lck = TagEfficiencyWeight('tagWeight_lck','tagWeight_lck',bTagMap,tagEff_lck)
    
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
    #otherargs_lck = [ tagEff_lck ]
    #otherargs_lck.append(mistagVar_B)
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
    
    time_lck_noacc       = RooBDecay('time_lck_noacc','time_lck_noacc', timeVar_B, GammaLb, zero,
                                     cosh_lck, sinh_lck, cos_lck, sin_lck,
                                     zero,trm_lck, RooBDecay.SingleSided)
    
    
    '''
    untaggedWeight_lck   = IfThreeWayCat('untaggedWeight_lck', 'untaggedWeight_lck', bTagMap, one, two, one)
    Dilution_lck         = RooFormulaVar('Dilution_lck',"1-2*@0",RooArgList(mistagVar_B))
    mixState_lck         = RooFormulaVar('mixState_lck','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    CE_lck               = RooRealVar("CE_lck","CE_lck",1 + myconfigfile["prodasy_lck"]*myconfigfile["tageffasy_lck"])
    CO_lck               = RooRealVar("CO_lck","CO_lck",myconfigfile["prodasy_lck"] + myconfigfile["tageffasy_lck"])
    
    CosSin_i0_lck        = RooProduct('sigCosSin_i0_lck', 'sigCosSin_i0 lck', RooArgSet(mixState_lck, Dilution_lck, tagWeight_lck))
    
    CPOddFact_lck        = RooFormulaVar("CPOddFact_lck","@2+@0*@1",RooArgList(CosSin_i0_lck,CE_lck,CO_lck))
    CPEvenFact_lck       = RooFormulaVar("CPEvenFact_lck","@1+@0*@2",RooArgList(CosSin_i0_lck,CE_lck,CO_lck))
    
    Cos_lck              = CPOddFact_lck
        
    Cosh_lck             = RooProduct('sigCosh_lck', 'cosh coefficient lck',
    RooArgSet(CPEvenFact_lck,untaggedWeight_lck, tagWeight_lck))   
    
    time_lck_noacc       = RooBDecay('time_lck_noacc','time_lck_noacc', timeVar_B, GammaLb, zero,
    Cosh_lck, D_lck, Cos_lck, S_lck,
    zero,trm_lck, RooBDecay.SingleSided)
    '''
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
    
    
    timeandmass_lck = RooProdPdf("timeandmass_lck","timeandmass_lck",RooArgList(timeerr_lck,
                                                                                MDFitter_lck,
                                                                                trueid_lck)) 
        
                                                                                                        
    
    #timemistag_lck = RooProdPdf("timemistag_lck","timemistag_lck",RooArgSet(mistag_lck),
    #                            RooFit.Conditional(RooArgSet(time_lck),
    #                                               RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
    #timeandmass_lck = RooProdPdf("timeandmass_lck","timeandmass_lck",RooArgList(timemistag_lck,mass_lck,trueid_lck))    
        
    #------------------------------------------------- Lb -> Dsp, Dsstp ----------------------------------------------------#
    
    #The Lb->Dsp, Lb->Dsstp - mass
    m = TString("Lb2Dsp")
    massB_dsp = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    m = TString("Lb2Dsstp")
    massB_dsstp = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    frac_dsdsstp = RooRealVar("frac_dsdsstp","frac_dsdsstp", myconfigfile["frac_dsdsstp"])
    massB_dsdsstp = RooAddPdf("mass_dsdsstp","mass_dsdsstp",RooArgList(massB_dsp,massB_dsstp),RooArgList(frac_dsdsstp))
    
    num_dsdsstp = RooRealVar("num_dsdsstp","num_dsdsstp", myconfigfile["num_dsdsstp"])
    
    #The Lb->Dsp, Lb->Dsstp - mass
    massD_dsdsstp = massD_signal
    massD_dsdsstp.SetName("massD_dsdsstp")
    
    #The Lb->Dsp, Lb->Dsstp - PIDK
    m = TString("Lb2Dsp")
    pidk_dsp = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("Lb2Dsstp")
    pidk_dsstp = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    PIDK_dsdsstp = RooAddPdf("pidk_dsdsstp","pidk_dsdsstp",RooArgList(pidk_dsp,pidk_dsstp),RooArgList(frac_dsdsstp))
    
    #The Lb->Dsp, Lb->Dsstp - MDFitter
    MDFitter_dsdsstp =  RooProdPdf("MDFitter_dsdsstp","MDFitter_dsdsstp",RooArgList(massB_dsdsstp, massD_dsdsstp, PIDK_dsdsstp))
    
    
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
    #otherargs_dsdsstp = [ tagEff_dsdsstp ]
    #otherargs_dsdsstp.append(mistagVar_B)
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
    
    time_dsdsstp_noacc       = RooBDecay('time_dsdsstp_noacc','time_dsdsstp_noacc', timeVar_B, GammaLb, zero,
                                         cosh_dsdsstp, sinh_dsdsstp, cos_dsdsstp, sinh_dsdsstp,
                                         zero,trm_dsdsstp, RooBDecay.SingleSided)
    
    
    '''
    untaggedWeight_dsdsstp   = IfThreeWayCat('untaggedWeight_dsdsstp', 'untaggedWeight_dsdsstp', bTagMap, one, two, one)
    Dilution_dsdsstp         = RooFormulaVar('Dilution_dsdsstp',"1-2*@0",RooArgList(mistagVar_B))
    mixState_dsdsstp         = RooFormulaVar('mixState_dsdsstp','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    CosSin_i0_dsdsstp        = RooProduct('sigCosSin_i0_dsdsstp', 'sigCosSin_i0 dsdsstp', 
    RooArgSet(mixState_dsdsstp, Dilution_dsdsstp, tagWeight_dsdsstp))
    
    CE_dsdsstp               = RooRealVar("CE_dsdsstp","CE_dsdsstp",1 + myconfigfile["prodasy_dsdsstp"]*myconfigfile["tageffasy_dsdsstp"])
    CO_dsdsstp               = RooRealVar("CO_dsdsstp","CO_dsdsstp",myconfigfile["prodasy_dsdsstp"] + myconfigfile["tageffasy_dsdsstp"])
    
    CPOddFact_dsdsstp        = RooFormulaVar("CPOddFact_dsdsstp","@2+@0*@1",RooArgList(CosSin_i0_dsdsstp,CE_dsdsstp,CO_dsdsstp))
    CPEvenFact_dsdsstp       = RooFormulaVar("CPEvenFact_dsdsstp","@1+@0*@2",RooArgList(CosSin_i0_dsdsstp,CE_dsdsstp,CO_dsdsstp))
    
    Cos_dsdsstp              = CPOddFact_dsdsstp
    
    Cosh_dsdsstp             = RooProduct('sigCosh_dsdsstp', 'cosh coefficient dsdsstp',
    RooArgSet(CPEvenFact_dsdsstp,untaggedWeight_dsdsstp, tagWeight_dsdsstp))   
    
    time_dsdsstp_noacc       = RooBDecay('time_dsdsstp_noacc','time_dsdsstp_noacc', timeVar_B, GammaLb, zero,
    Cosh_dsdsstp, D_dsdsstp, Cos_dsdsstp, S_dsdsstp,
    zero,trm_dsdsstp, RooBDecay.SingleSided)
    '''
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
    
    
    timeandmass_dsdsstp = RooProdPdf("timeandmass_dsdsstp","timeandmass_dsdsstp",RooArgList(timeerr_dsdsstp,
                                                                                            MDFitter_dsdsstp,
                                                                                            trueid_dsdsstp))
    

    #timemistag_dsdsstp = RooProdPdf("timemistag_dsdsstp","timemistag_dsdsstp",RooArgSet(total_mistag_dsdsstp),
    #                                RooFit.Conditional(RooArgSet(time_dsdsstp),
    #                                                   RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    #
    #timeandmass_dsdsstp = RooProdPdf("timeandmass_dsdsstp","timeandmass_dsdsstp",RooArgList(timemistag_dsdsstp,mass_dsdsstp,trueid_dsdsstp))   
        
    
    #------------------------------------------------- Combinatorial ----------------------------------------------------#

    #The combinatorics - mass
    num_combo = RooRealVar("num_combo","num_combo", myconfigfile["num_combo"])
    
    #The combinatorics - mass B
    cBVar = RooRealVar("CombBkg_slope_Bs","CombBkg_slope_Bs", myconfigfile["cB"])
    massB_combo = RooExponential("massB_combo","massB_combo",massVar_B, cBVar)
    
    #The combinatorics - mass D
    cDVar = RooRealVar("CombBkg_slope_Ds","CombBkg_slope_Ds", myconfigfile["cD"])
    fracDsComb = RooRealVar("CombBkg_fracDsComb", "CombBkg_fracDsComb",  myconfigfile["fracDsComb"])
    massD_combo = Bs2Dsh2011TDAnaModels.ObtainComboDs(massVar_D, cDVar, fracDsComb, massD_signal, mode, debug)
    
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
    
    #The combinatorics - MDFitter
    MDFitter_combo = RooProdPdf("MDFitter_combo","MDFitter_combo",RooArgList(massB_combo, massD_combo, PIDK_combo))
    
    #The combinatorics - acceptance - tacc_powlaw
    tacc_combo = tacc_powlaw
    
    #The combinatorics - resolution
    trm_combo = trm
    
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
    
    time_combo_noacc       = RooBDecay('time_combo_noacc','time_combo_noacc', timeVar_B, GammaCombo, zero,
                                       cosh_combo, sinh_combo, cos_combo, sin_combo,
                                       zero,trm_combo, RooBDecay.SingleSided)
    
    
    '''
    untaggedWeight_combo   = IfThreeWayCat('untaggedWeight_combo', 'untaggedWeight_combo', bTagMap, one, two, one)
    Dilution_combo         = RooFormulaVar('Dilution_combo',"1-2*@0",RooArgList(mistagVar_B))
    mixState_combo         = RooFormulaVar('mixState_combo','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    CosSin_i0_combo        = RooProduct('sigCosSin_i0_combo', 'sigCosSin_i0 combo', RooArgSet(mixState_combo, Dilution_combo, tagWeight_combo))
    
    CE_combo               = RooRealVar("CE_combo","CE_combo",1 + myconfigfile["prodasy_combo"]*myconfigfile["tageffasy_combo"])
    CO_combo               = RooRealVar("CO_combo","CO_combo",myconfigfile["prodasy_combo"] + myconfigfile["tageffasy_combo"])
    
    CPOddFact_combo        = RooFormulaVar("CPOddFact_combo","@2+@0*@1",RooArgList(CosSin_i0_combo,CE_combo,CO_combo))
    CPEvenFact_combo       = RooFormulaVar("CPEvenFact_combo","@1+@0*@2",RooArgList(CosSin_i0_combo,CE_combo,CO_combo))
    
    Cos_combo              = CPOddFact_combo
    
    Cosh_combo             = RooProduct('sigCosh_combo', 'cosh coefficient combo',
                                            RooArgSet(CPEvenFact_combo,untaggedWeight_combo, tagWeight_combo))   
                                            
                                            time_combo_noacc       = RooBDecay('time_combo_noacc','time_combo_noacc', timeVar_B, GammaCombo, zero,
                                            Cosh_combo, D_combo, Cos_combo, S_combo,
                                            zero,trm_combo, RooBDecay.SingleSided)
    '''
    
    time_combo             = RooEffProd('time_combo','time_combo',time_combo_noacc, tacc_combo)
    
    #The combinatorics - true ID
    trueid_combo = RooGenericPdf("trueid_combo","exp(-100.*abs(@0-10))",RooArgList(trueIDVar_B))
    
    #The combinatorics - time error
    terr_combo = terr_signal #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("TimeErrorPdf_signal_BDTGA"), debug)
    terr_combo.SetName("terr_combo")
    
    timeerr_combo = RooProdPdf('combo_timeerr', 'combo_timeerr',  RooArgSet(terr_combo),
                               RooFit.Conditional(RooArgSet(time_combo),
                                                  RooArgSet(timeVar_B, fChargeMap, bTagMap, mistagVar_B )))
    
    
    timeandmass_combo = RooProdPdf("timeandmass_combo","timeandmass_combo",RooArgList(timeerr_combo,
                                                                                      MDFitter_combo,
                                                                                      trueid_combo)) 
        
    
    
    #The combinatorics - total
    #timemistag_combo = RooProdPdf("timemistag_combo","timemistag_combo",RooArgSet(mistag_combo),
    #                              RooFit.Conditional(RooArgSet(time_combo),
    #                                                 RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    #
    #timeandmass_combo = RooProdPdf("timeandmass_combo","timeandmass_combo",RooArgList(timemistag_combo,mass_combo,trueid_combo))
    #------------------------------------------------- Low mass K ----------------------------------------------------#
    
    #The low mass - mass B
    #mass_dskst = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsKstPdf_m_both"), debug)
    #mass_dsstkst = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstKstPdf_m_both"), debug)
    #mass_dsstk = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstKPdf_m_both"), debug)
        
    #frac_g1_1lmk = RooRealVar("frac_g1_1lmk","frac_g1_1lmk",myconfigfile["frac_g1_1lmk"])
    #frac_g1_2lmk = RooRealVar("frac_g1_2lmk","frac_g1_2lmk",myconfigfile["frac_g1_2lmk"])
        
    #mass_lm1 = RooAddPdf("mass_lm1","mass_lm1",RooArgList(mass_dskst,mass_dsstkst,mass_dsstk),RooArgList(frac_g1_1lmk, frac_g1_2lmk))

    m = TString("Bs2DsKst")
    massB_lm1 = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug);
    
    #The low mass - mass D
    massD_lm1 = massD_signal
    massD_lm1.SetName("massD_lm1")
    
    #The low mass - PIDK 
    PIDK_lm1 = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug);
    
    #The low mass - MDFitter
    MDFitter_lm1 = RooProdPdf("MDFitter_lm1","MDFitter_lm1",RooArgList(massB_lm1, massD_lm1, PIDK_lm1))
    
    num_lm1 = RooRealVar("num_lm1","num_lm1",myconfigfile["num_lm1"])
    
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
    tagWeight_lm1 = TagEfficiencyWeight("tagWeight_lm1","tagWeight_lm1",bTagMap,tagEff_lm1)
    
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
    
    flag_lm1 = 0 #DecRateCoeff.AvgDelta
    
    cosh_lm1 = DecRateCoeff('lm1_cosh', 'lm1_cosh', DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  one,      one,      *otherargs_lm1)
    sinh_lm1 = DecRateCoeff('lm1_sinh', 'lm1_sinh', flag_lm1 | DecRateCoeff.CPEven,
                            fChargeMap, bTagMap,  D_lm1,    Dbar_lm1, *otherargs_lm1)
    cos_lm1  = DecRateCoeff('lm1_cos',  'lm1_cos' , DecRateCoeff.CPOdd,
                            fChargeMap, bTagMap,  C_lm1,    C_lm1,    *otherargs_lm1)
    sin_lm1  = DecRateCoeff('lm1_sin',  'lm1_sin',  flag_lm1 | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                            fChargeMap, bTagMap,  S_lm1, Sbar_lm1,    *otherargs_lm1)
    
    time_lm1_noacc       = RooBDecay('time_lm1_noacc','time_lm1_noacc', timeVar_B, Gammas, DeltaGammas,
                                     cosh_lm1, sinh_lm1, cos_lm1, sin_lm1,
                                     DeltaMs,trm_lm1, RooBDecay.SingleSided)
    
    
    '''
    untaggedWeight_lm1   = IfThreeWayCat('untaggedWeight_lm1', 'untaggedWeight_lm1', bTagMap, one, two, one)
    Dilution_lm1         = RooFormulaVar('Dilution_lm1',"1-2*@0",RooArgList(mistagVar_B))
    mixState_lm1         = RooFormulaVar('mixState_lm1','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    weightedDs_lm1       = IfThreeWayCat('weightedDs_lm1', 'weightedDs_lm1',fChargeMap, D_lm1, zero, Dbar_lm1)
    weightedSs_lm1       = IfThreeWayCat('weightedSs_lm1', 'weightedSs_lm1',fChargeMap, S_lm1, zero, Sbar_lm1)
    CosSin_i0_lm1        = RooProduct('CosSin_i0_lm1', 'CosSin_i0_lm1', RooArgSet(mixState_lm1, Dilution_lm1, tagWeight_lm1))
    
    CE_lm1               = RooRealVar("CE_lm1","CE_lm1",1 + myconfigfile["prodasy_lm1"]*myconfigfile["tageffasy_lm1"])
    CO_lm1               = RooRealVar("CO_lm1","CO_lm1",myconfigfile["prodasy_lm1"] + myconfigfile["tageffasy_lm1"])
    
    CPOddFact_lm1        = RooFormulaVar("CPOddFact_lm1","@2+@0*@1",RooArgList(CosSin_i0_lm1,CE_lm1,CO_lm1))
    CPEvenFact_lm1       = RooFormulaVar("CPEvenFact_lm1","@1+@0*@2",RooArgList(CosSin_i0_lm1,CE_lm1,CO_lm1))
    
    Cos_lm1              = RooProduct('Cos_lm1', 'Cos lm1', RooArgSet(CPOddFact_lm1,C_lm1))
    Cosh_lm1             = RooProduct('Cosh_lm1', 'cosh coefficient lm1', RooArgSet(untaggedWeight_lm1, tagWeight_lm1,CPEvenFact_lm1))
    Sin_lm1              = RooProduct('Sin_lm1', 'Sin lm1', RooArgSet(CPOddFact_lm1,weightedSs_lm1,minusone))
    Sinh_lm1             = RooProduct('Sinh_lm1','Sinh_lm1',RooArgSet(Cosh_lm1,weightedDs_lm1))
    
    time_lm1_noacc       = RooBDecay('time_lm1_noacc','time_lm1_noacc', timeVar_B, Gammas, DeltaGammas,
    Cosh_lm1, Sinh_lm1, Cos_lm1, Sin_lm1,
    DeltaMs,trm_lm1, RooBDecay.SingleSided)
    '''
    
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
    
    
    timeandmass_lm1 = RooProdPdf("timeandmass_lm1","timeandmass_lm1",RooArgList(timeerr_lm1,
                                                                                MDFitter_lm1,
                                                                                trueid_lm1)) 
        
    #timemistag_lm1 = RooProdPdf("timemistag_lm1","timemistag_lm1",RooArgSet(total_mistag_lm1),
    #                            RooFit.Conditional(RooArgSet(time_lm1),
    #                                               RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    #
    #timeandmass_lm1 = RooProdPdf("timeandmass_lm1","timeandmass_lm1",RooArgList(timemistag_lm1,mass_lm1,trueid_lm1))
        
    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

    #The low mass - pi - mass B
    m = TString("Bs2DsstPi")
    massB_dsstpi = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    m = TString("Bs2DsRho")
    massB_dsrho = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    #mass_dsstrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstRhoPdf_m_both"), debug)
    
    frac_g2_1 = RooRealVar("frac_g2_1","frac_g2_1", myconfigfile["frac_g2_1"])
    #frac_g2_2 = RooRealVar("frac_g2_2","frac_g2_2", myconfigfile["frac_g2_1"])
    
    #mass_lm2 = RooAddPdf("mass_lm2","mass_lm2",RooArgList(mass_dsstpi,mass_dsrho,mass_dsstrho),RooArgList(frac_g2_1, frac_g2_2))
    massB_lm2 = RooAddPdf("massB_lm2","massB_lm2",RooArgList(massB_dsstpi,massB_dsrho),RooArgList(frac_g2_1))
    num_lm2 = RooRealVar("num_lm2","num_lm2", myconfigfile["num_lm2"])
    
    #The low mass - mass D
    massD_lm2 = massD_signal
    massD_lm2.SetName("massD_lm2")
    
    #the low mass - pi - pidk
    m = TString("Bs2DsstPi")
    PIDK_dsstpi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("Bs2DsRho")
    PIDK_dsrho = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    PIDK_lm2 = RooAddPdf("PIDK_lm2","PIDK_lm2",RooArgList(PIDK_dsstpi,PIDK_dsrho),RooArgList(frac_g2_1))
        
    #The low mass - MDFitter
    MDFitter_lm2 = RooProdPdf("MDFitter_lm2","MDFitter_lm2",RooArgList(massB_lm2, massD_lm2, PIDK_lm2))
    
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
    
    time_lm2_noacc       = RooBDecay('time_lm2_noacc','time_lm2_noacc', timeVar_B, Gammas, DeltaGammas,
                                     cosh_lm2, sinh_lm2, cos_lm2, sin_lm2,
                                     DeltaMs,trm_lm2, RooBDecay.SingleSided)
    
    
    
    '''
    untaggedWeight_lm2   = IfThreeWayCat('untaggedWeight_lm2', 'untaggedWeight_lm2', bTagMap, one, two, one)
    Dilution_lm2         = RooFormulaVar('Dilution_lm2',"1-2*@0",RooArgList(mistagVar_B))
    mixState_lm2         = RooFormulaVar('mixState_lm2','@0*@1',RooArgList(bTagMap,fChargeMap))
    
    CosSin_i0_lm2        = RooProduct('sigCosSin_i0_lm2', 'sigCosSin_i0 lm2', RooArgSet(mixState_lm2, Dilution_lm2, tagWeight_lm2))
    
    CE_lm2               = RooRealVar("CE_lm2","CE_lm2",1 + myconfigfile["prodasy_lm2"]*myconfigfile["tageffasy_lm2"])
    CO_lm2               = RooRealVar("CO_lm2","CO_lm2",myconfigfile["prodasy_lm2"] + myconfigfile["tageffasy_lm2"])
    
    CPOddFact_lm2        = RooFormulaVar("CPOddFact_lm2","@2+@0*@1",RooArgList(CosSin_i0_lm2,CE_lm2,CO_lm2))
    CPEvenFact_lm2       = RooFormulaVar("CPEvenFact_lm2","@1+@0*@2",RooArgList(CosSin_i0_lm2,CE_lm2,CO_lm2))
    
    Cos_lm2              = CPOddFact_lm2
    
    Cosh_lm2             = RooProduct('sigCosh_lm2', 'cosh coefficient lm2',
    RooArgSet(CPEvenFact_lm2,untaggedWeight_lm2, tagWeight_lm2))   
    
    time_lm2_noacc       = RooBDecay('time_lm2_noacc','time_lm2_noacc', timeVar_B, Gammas, DeltaGammas,
    Cosh_lm2, D_lm2, Cos_lm2, S_lm2,
    DeltaMs,trm_lm2, RooBDecay.SingleSided)
    '''
    
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
    
    
    timeandmass_lm2 = RooProdPdf("timeandmass_lm2","timeandmass_lm2",RooArgList(timeerr_lm2,
                                                                                MDFitter_lm2,
                                                                                trueid_lm2)) 
    

    #timemistag_lm2 = RooProdPdf("timemistag_lm2","timemistag_lm2",RooArgSet(total_mistag_lm2),
    #                            RooFit.Conditional(RooArgSet(time_lm2),
    #                                               RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    #
    #timeandmass_lm2 = RooProdPdf("timeandmass_lm2","timeandmass_lm2",RooArgList(timemistag_lm2,mass_lm2,trueid_lm2))                
    #------------------------------------------------- Total bkg ----------------------------------------------------#
    
    #Total background
    #total_back_pdf = RooAddPdf("total_back_pdf","total_back_pdf",
    #                           RooArgList(timeandmass_dk,timeandmass_dsk,timeandmass_dspi,
    #                                      timeandmass_lck,timeandmass_dsdsstp,
    #                                      timeandmass_combo,timeandmass_lm1,timeandmass_lm2),
    #                           RooArgList(num_dk,num_dsk,num_dspi,num_lck,num_dsdsstp,num_combo,num_lm1,num_lm2))
        
    #Total
    total_pdf = RooAddPdf("total_pdf","total_pdf",RooArgList(timeandmass_signal,
                                                             timeandmass_dk,timeandmass_dsk,timeandmass_dspi,
                                                             timeandmass_lck,timeandmass_dsdsstp,
                                                             timeandmass_combo,timeandmass_lm1,timeandmass_lm2),
                          RooArgList(num_signal, num_dk,num_dsk,num_dspi,num_lck,num_dsdsstp,num_combo,num_lm1,num_lm2))
    #getattr(workout,'import')(total_pdf)
        
        #Generate

        
    for i in range(0,ntoys) :

        workout = RooWorkspace("workspace","workspace")
        getattr(workout,'import')(total_pdf)
        
        gendata.append(total_pdf.generate(RooArgSet(massVar_B, massVar_D, PIDKVar_B,
                                                    timeVar_B, terrVar_B,
                                                    trueIDVar_B,bTagMap,fChargeMap,mistagVar_B),
                                          int(numberOfEvents+30))
                       )
        
        tree = gendata[-1].store().tree()
        
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
                                              TString("dataSetBsDsK_toys"),
                                              debug))
        
        getattr(workout,'import')(data[-1])
        
        
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
            workout.writeToFile("/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma140/DsK_Toys_Work_"+str(i)+".root")
            #outfile  = TFile("/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/DsK_Toys_Full_Tree_2kSample_"+str(i)+".root","RECREATE")
        else :
            workout.writeToFile("Data_Toys_Single_Work_DsK.root")
            outfile  = TFile("Data_Toys_Single_Tree_DsK.root","RECREATE")
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
                   default = 500)

parser.add_option( '--numberOfEvents',
                   dest = 'numberOfEvents',
                   default = 7372)


parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsKConfigForGenerator')

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
                                
