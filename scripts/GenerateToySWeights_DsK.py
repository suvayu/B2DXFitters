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


import ROOT
from ROOT import *
from math import *
import os,sys
from optparse import OptionParser
from os.path  import join

import GaudiPython
GaudiPython.loaddict( 'B2DXFittersDict' )
GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils
SFitUtils = GaudiPython.gbl.SFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels
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
    
    if single :
        ntoys = 1
    else:
        ntoys = numberOfToys
                            
      
    gendata = []
    data = []
    
    fileName = "/afs/cern.ch/work/a/adudziak/public/workspace/work_dsk.root"
    fileName2 = "/afs/cern.ch/work/a/adudziak/public/workspace/work_toys_dsk.root"
    workName = 'workspace'
    
    mVar = 'lab0_MassFitConsD_M'
    tVar = 'lab0_LifetimeFit_ctau'
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
    massVar_B  = GeneralUtils.GetObservable(workspace,TString(mVar), debug)
    trueIDVar_B = RooRealVar(trueID,trueID,0,100)
    mistagVar_B = GeneralUtils.GetObservable(workspace_mistag,TString(tagomega), debug)
    mistagVar_B.setMax(1.0)

    import GaudiPython
    GaudiPython.loaddict('B2DXFittersDict')
    trm = PTResModels.getPTResolutionModel("TripleGaussian",timeVar_B, 'Bs', False,1.15)

    tacc_beta_pl        = RooRealVar('tacc_beta_pl'    , 'PowLawAcceptance_beta',      myconfigfile["tacc_beta_pl"]     )
    tacc_exponent_pl    = RooRealVar('tacc_exponent_pl', 'PowLawAcceptance_exponent',  myconfigfile["tacc_exponent_pl"] )
    tacc_offset_pl      = RooRealVar('tacc_offset_pl'  , 'PowLawAcceptance_offset',    myconfigfile["tacc_offset_pl"]   )
    tacc_turnon_pl      = RooRealVar('tacc_turnon_pl'  , 'PowLawAcceptance_turnon',    myconfigfile["tacc_turnon_pl"]   )
    ratiocorr           = RooConstVar('ratiocorr','ratiocorr',1.)
    tacc_powlaw         = PowLawAcceptance('BsPowLawAcceptance', 'PowLaw decay time acceptance function',
                                           tacc_turnon_pl, timeVar_B, tacc_offset_pl, tacc_exponent_pl, tacc_beta_pl,ratiocorr)
    
    for i in range(0,ntoys) :

        #Create out workspace
        workout = RooWorkspace("workspace","workspace")
        
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
        
                 
        edoubleCB_signal = Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBs, sigma1VarBs, alpha1VarBs, n1VarBs, sigma2VarBs, alpha2VarBs, n2VarBs, fracVarBs, num_signal, "all", "Bs", debug )
        
        #The signal - time acceptance - tacc_powlaw
               
        #The signal - resolution
        trm_signal = trm
                
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
        
        time_signal             = RooEffProd('time_signal','time_signal',time_signal_noacc,tacc_powlaw)
        
        #The signal - true ID
        trueid_signal = RooGenericPdf("trueid_signal","exp(-100.*abs(@0-1))",RooArgList(trueIDVar_B))
        
        #The signal - mistag
        #mistag_signal =Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsKPdf_m_down_mistag"), debug)
        mistag_signal = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        
        #The signal - total
        timemistag_signal = RooProdPdf("timemistag_signal","timemistag_signal",RooArgSet(mistag_signal),
                                       RooFit.Conditional(RooArgSet(time_signal),
                                                          RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_signal = RooProdPdf("timeandmass_signal","timeandmass_signal",RooArgList(timemistag_signal,edoubleCB_signal,trueid_signal))
        
    #-------------------------------------------------- Bd -> DK ----------------------------------------------------#
    
        #The Bd->DK - mass
        mass_dk = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DKPdf_m_both"), debug)
        num_dk = RooRealVar("num_dk","num_dk",myconfigfile["num_dk"])
        
        #The Bd->DK - acceptance - tacc_powlaw 
                
        #The Bd->DK - resolution
        trm_dk = trm
        #RooGaussModel('PTRMGaussian_dk','PTRMGaussian_dk',timeVar_B, zero, TauRes)
        
        #The Bd->DK - time
        tagEff_dk    = RooRealVar("tagEff_dk","tagEff_dk", myconfigfile["tagEff_dk"])
        tagWeight_dk = TagEfficiencyWeight('tagWeight_dk','tagWeight_dk',bTagMap,tagEff_dk)
        
        S_dk    = RooRealVar('S_dk', 'S coeff. dk', 0.) 
        D_dk    = RooRealVar('D_dk', 'D coeff. dk', 0.) 
        
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
         
        time_dk             = RooEffProd('time_dk','time_dk',time_dk_noacc,tacc_powlaw)
        
        #The Bd->DK - true ID
        trueid_dk = RooGenericPdf("trueid_dk","exp(-100.*abs(@0-2))",RooArgList(trueIDVar_B))
        
        #The Bd->DK - mistag
        mistag_dk = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        #Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBd2DKPdf_m_both_mistag"), debug) 
        
        #The Bd->DK - total
        timemistag_dk = RooProdPdf("timemistag_dk","timemistag_dk",RooArgSet(mistag_dk),
                                   RooFit.Conditional(RooArgSet(time_dk),
                                                      RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_dk = RooProdPdf("timeandmass_dk","timeandmass_dk",RooArgList(timemistag_dk,mass_dk,trueid_dk))
    #------------------------------------------------- Bd -> DsK ----------------------------------------------------#
    
        #The Bd->DsK - mass
        meanVarBd   =  RooRealVar( "DblCBBdPDF_mean" ,  "mean",    myconfigfile["mean"]-86.8)
        sigma1VarBd =  RooRealVar( "DblCBBdPDF_sigma1", "sigma1",  myconfigfile["sigma1"]*myconfigfile["ratio1"] )
        sigma2VarBd =  RooRealVar( "DblCBBdPDF_sigma2", "sigma2",  myconfigfile["sigma2"]*myconfigfile["ratio2"] )
                       
        num_dsk = RooRealVar("num_dsk","num_dsk",myconfigfile["num_dsk"])
        mass_dsk = Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBd, sigma1VarBd, alpha1VarBs, n1VarBs, sigma2VarBd, alpha2VarBs,
                                                               n2VarBs, fracVarBs, num_dsk, "bddsk", "Bd", debug )
        
        #The Bd->DsK - acceptance - tacc_powlaw
                
        #The Bd->DsK - resolution
        trm_dsk = trm
        #RooGaussModel('PTRMGaussian_dsk','PTRMGaussian_dsk',timeVar_B, zero, TauRes)
        
        #The Bd->DsK - time
        tagEff_dsk    = RooRealVar("tagEff_dsk","tagEff_dsk",myconfigfile["tagEff_dsk"])
        tagWeight_dsk = TagEfficiencyWeight('tagWeight_dsk','tagWeight_dsk',bTagMap,tagEff_dsk)
        
        S_dsk    = RooRealVar('S_dsk', 'S coeff. dsk', 0.) 
        D_dsk    = RooRealVar('D_dsk', 'D coeff. dsk', 0.) 
        
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
        
        time_dsk             = RooEffProd('time_dsk','time_dsk',time_dsk_noacc,tacc_powlaw)
        
        #The Bd->DsK - true ID
        trueid_dsk = RooGenericPdf("trueid_dsk","exp(-100.*abs(@0-3))",RooArgList(trueIDVar_B))
        
        #The Bd->DsK- mistag
        mistag_dsk = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBd2DsKPdf_m_both_mistag"), debug)
        
        #The Bd->DsK - total
        timemistag_dsk = RooProdPdf("timemistag_dsk","timemistag_dsk",RooArgSet(mistag_dsk), 
                                    RooFit.Conditional(RooArgSet(time_dsk),
                                                       RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_dsk = RooProdPdf("timeandmass_dsk","timeandmass_dsk",RooArgList(timemistag_dsk,mass_dsk,trueid_dsk))
        
    #------------------------------------------------- Bs -> DsPi ----------------------------------------------------# 
    
        #The Bs->DsPi - mass
        mass_dspi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBsDsPi_m_down_kkpi"), debug) 
        num_dspi = RooRealVar("num_dspi","num_dspi", myconfigfile["num_dspi"])
        
        #The Bs->DsPi - acceptance - tacc_powlaw
                
        #The Bs->DsPi - resolution
        trm_dspi = trm
                
        #The Bs->DsPi - time
        tagEff_dspi    = RooRealVar("tagEff_signal","tagEff_signal", myconfigfile["tagEff_dspi"])
        tagWeight_dspi = TagEfficiencyWeight('tagWeight_dspi','tagWeight_dspi',bTagMap,tagEff_dspi)
        
        S_dspi    = RooRealVar('S_dspi', 'S coeff. dspi', 0.)
        D_dspi    = RooRealVar('D_dspi', 'D coeff. dspi', 0.)
        
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
        
        time_dspi             = RooEffProd('time_dspi','time_dspi',time_dspi_noacc,tacc_powlaw)
        
        #The Bs->DsPi - true ID
        trueid_dspi = RooGenericPdf("trueid_dspi","exp(-100.*abs(@0-4))",RooArgList(trueIDVar_B))
        
        #The Bs->DsPi- mistag
        mistag_dspi =Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        
        #The Bs->DsPi - total
        timemistag_dspi = RooProdPdf("timemistag_dspi","timemistag_dspi",RooArgSet(mistag_dspi),
                                     RooFit.Conditional(RooArgSet(time_dspi),
                                                        RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_dspi = RooProdPdf("timeandmass_dspi","timeandmass_dspi",RooArgList(timemistag_dspi,mass_dspi,trueid_dspi))
        
    #------------------------------------------------- Lb -> LcK ----------------------------------------------------#
    
        #The Lb->LcK - mass
        mass_lck = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgLb2LcKPdf_m_both"), debug)
        num_lck = RooRealVar("num_lck","num_lck", myconfigfile["num_lck"])
        
        #The Lb->LcK - acceptance - tacc_powlaw
                
        #The Lb->LcK - resolution
        trm_lck = trm
        
        #The Lb->LcK - time
        tagEff_lck    = RooRealVar("tagEff_lck","tagEff_lck", myconfigfile["tagEff_lck"])
        tagWeight_lck = TagEfficiencyWeight('tagWeight_lck','tagWeight_lck',bTagMap,tagEff_lck)
        
        S_lck    = RooRealVar('S_lck', 'S coeff. lck', 0.)
        D_lck    = RooRealVar('D_lck', 'D coeff. lck', 0.)
        
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
        
        time_lck             = RooEffProd('time_lck','time_lck',time_lck_noacc,tacc_powlaw)
         
        #The Lb->LcK - true ID
        trueid_lck = RooGenericPdf("trueid_lck","exp(-100.*abs(@0-5))",RooArgList(trueIDVar_B))
        
        #The Lb->LcK- mistag
        mistag_lck = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        #Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgLb2LcKPdf_m_both_mistag"), debug)
        
        #The Lb->LcK - total
        timemistag_lck = RooProdPdf("timemistag_lck","timemistag_lck",RooArgSet(mistag_lck),
                                    RooFit.Conditional(RooArgSet(time_lck),
                                                       RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_lck = RooProdPdf("timeandmass_lck","timeandmass_lck",RooArgList(timemistag_lck,mass_lck,trueid_lck))    
        
    #------------------------------------------------- Lb -> Dsp, Dsstp ----------------------------------------------------#
    
        #The Lb->Dsp, Lb->Dsstp - mass
        mass_dsp = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgLb2DspPdf_m_both"), debug)
        mass_dsstp = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgLb2DsstpPdf_m_both"), debug)
        frac_dsdsstp = RooRealVar("frac_dsdsstp","frac_dsdsstp", myconfigfile["frac_dsdsstp"])
        
        mass_dsdsstp = RooAddPdf("total_dsdsstp","total_dsdsstp",RooArgList(mass_dsp,mass_dsstp),RooArgList(frac_dsdsstp))
        num_dsdsstp = RooRealVar("num_dsdsstp","num_dsdsstp", myconfigfile["num_dsdsstp"])
        
        #The Lb->Dsp, Lb->Dsstp - acceptance - tacc_powlaw
               
        #The Lb->Dsp, Lb->Dsstp - resolution
        trm_dsdsstp = trm
        
        #The Lb->Dsp, Lb->Dsstp - time
        tagEff_dsdsstp    = RooRealVar("tagEff_dsdsstp","tagEff_dsdsstp", myconfigfile["tagEff_dsdsstp"])
        tagWeight_dsdsstp = TagEfficiencyWeight('tagWeight_dsdsstp','tagWeight_dsdsstp',bTagMap,tagEff_dsdsstp)
        
        S_dsdsstp    = RooRealVar('S_dsdsstp', 'S coeff. dsdsstp', 0.)
        D_dsdsstp    = RooRealVar('D_dsdsstp', 'D coeff. dsdsstp', 0.)
        
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
        
        time_dsdsstp             = RooEffProd('time_dsdsstp','time_dsdsstp',time_dsdsstp_noacc,tacc_powlaw)
        
        #The Lb->Dsp - true ID
        trueid_dsdsstp = RooGenericPdf("trueid_dsdsstp","exp(-100.*abs(@0-6))",RooArgList(trueIDVar_B))
        
        #The Lb->Dsp, Lb->Dsstp - mistag
        mistag_dsp =Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgLb2DspPdf_m_both_mistag"), debug)
        mistag_dsstp =Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgLb2DsstpPdf_m_both_mistag"), debug)    
        total_mistag_dsdsstp = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        #RooAddPdf("total_mistag_dsdsstp","total_mistag_dsdsstp",RooArgList(mistag_dsp,mistag_dsstp),RooArgList(frac_dsdsstp))
                           
        #The Lb->Dsp, Lb->Dsstp - total
        timemistag_dsdsstp = RooProdPdf("timemistag_dsdsstp","timemistag_dsdsstp",RooArgSet(total_mistag_dsdsstp),
                                        RooFit.Conditional(RooArgSet(time_dsdsstp),
                                                           RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_dsdsstp = RooProdPdf("timeandmass_dsdsstp","timeandmass_dsdsstp",RooArgList(timemistag_dsdsstp,mass_dsdsstp,trueid_dsdsstp))   
 

    #------------------------------------------------- Combinatorial ----------------------------------------------------#

        #The combinatorics - mass
        exposlope_combo = RooRealVar("exposlope_combo","exposlope_combo", myconfigfile["exposlope_combo"])
        mass_combo = RooExponential("mass_combo","mass_combo",massVar_B,exposlope_combo)
        num_combo = RooRealVar("num_combo","num_combo", myconfigfile["num_combo"])
        
        #The combinatorics - acceptance - tacc_powlaw
        
        #The combinatorics - resolution
        trm_combo = trm
        
        #The combinatorics - time
        tagEff_combo    = RooRealVar("tagEff_combo","tagEff_combo", myconfigfile["tagEff_combo"])
        tagWeight_combo = TagEfficiencyWeight('tagWeight_combo','tagWeight_combo',bTagMap,tagEff_combo)
        
        S_combo    = RooRealVar('S_combo', 'S coeff. combo', 0.)
        D_combo    = RooRealVar('D_combo', 'D coeff. combo', 0.)
        
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
        
        time_combo             = RooEffProd('time_combo','time_combo',time_combo_noacc,tacc_powlaw)
        
        #The combinatorics - true ID
        trueid_combo = RooGenericPdf("trueid_combo","exp(-100.*abs(@0-10))",RooArgList(trueIDVar_B))
    
        #The combinatorics - mistag
        mistag_combo = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        #Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsKPdf_m_down_mistag"))
        
        #The combinatorics - total
        timemistag_combo = RooProdPdf("timemistag_combo","timemistag_combo",RooArgSet(mistag_combo),
                                      RooFit.Conditional(RooArgSet(time_combo),
                                                         RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_combo = RooProdPdf("timeandmass_combo","timeandmass_combo",RooArgList(timemistag_combo,mass_combo,trueid_combo))
    #------------------------------------------------- Low mass K ----------------------------------------------------#
    
        #The low mass - mass
        mass_dskst = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsKstPdf_m_both"), debug)
        mass_dsstkst = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstKstPdf_m_both"), debug)
        mass_dsstk = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstKPdf_m_both"), debug)
        
        frac_g1_1lmk = RooRealVar("frac_g1_1lmk","frac_g1_1lmk",myconfigfile["frac_g1_1lmk"])
        frac_g1_2lmk = RooRealVar("frac_g1_2lmk","frac_g1_2lmk",myconfigfile["frac_g1_2lmk"])
        
        mass_lm1 = RooAddPdf("mass_lm1","mass_lm1",RooArgList(mass_dskst,mass_dsstkst,mass_dsstk),RooArgList(frac_g1_1lmk, frac_g1_2lmk))
        num_lm1 = RooRealVar("num_lm1","num_lm1",myconfigfile["num_lm1"])
        
        #The low mass - acceptance - tacc_powlaw
                
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
        
        time_lm1             = RooEffProd('time_lm1','time_lm1',time_lm1_noacc,tacc_powlaw)
        
        #The low mass - true ID 
        trueid_lm1 = RooGenericPdf("trueid_lm1","exp(-100.*abs(@0-7))",RooArgList(trueIDVar_B))
        
        #The low mass - mistag
        mistag_dskst = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsKstPdf_m_both_mistag"), debug)
        mistag_dsstkst = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsstKstPdf_m_both_mistag"), debug)
        mistag_dsstk = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsstKPdf_m_both_mistag"), debug)
        total_mistag_lm1 = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        #RooAddPdf("total_mistag_lm","total_mistag_lm",RooArgList(mistag_dskst,mistag_dsstkst,mistag_dsstk),RooArgList(frac_g1_1, frac_g1_2))

        #The low mass - total
        timemistag_lm1 = RooProdPdf("timemistag_lm1","timemistag_lm1",RooArgSet(total_mistag_lm1),
                                    RooFit.Conditional(RooArgSet(time_lm1),
                                                       RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_lm1 = RooProdPdf("timeandmass_lm1","timeandmass_lm1",RooArgList(timemistag_lm1,mass_lm1,trueid_lm1))

    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

        mass_dsstpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstPiPdf_m_both"), debug)
        mass_dsrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsRhoPdf_m_both"), debug)
        mass_dsstrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstRhoPdf_m_both"), debug)
        
        frac_g2_1 = RooRealVar("frac_g2_1","frac_g2_1", myconfigfile["frac_g2_1"])
        frac_g2_2 = RooRealVar("frac_g2_2","frac_g2_2", myconfigfile["frac_g2_1"])
        
        mass_lm2 = RooAddPdf("mass_lm2","mass_lm2",RooArgList(mass_dsstpi,mass_dsrho,mass_dsstrho),RooArgList(frac_g2_1, frac_g2_2))
        num_lm2 = RooRealVar("num_lm2","num_lm2", myconfigfile["num_lm2"])
        
        #The low mass - acceptance - tacc_powlaw
               
        #The low mass - resolution
        trm_lm2 = trm
        
        #The low mass - time
        tagEff_lm2    = RooRealVar("tagEff_lm2","tagEff_lm2",myconfigfile["tagEff_lm2"])
        tagWeight_lm2 = TagEfficiencyWeight('tagWeight_lm2','tagWeight_lm2',bTagMap,tagEff_lm2)
        
        S_lm2    = RooRealVar('S_lm2', 'S coeff. lm2', 0.)
        D_lm2    = RooRealVar('D_lm2', 'D coeff. lm2', 0.)
        
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
        
        time_lm2             = RooEffProd('time_lm2','time_lm2',time_lm2_noacc,tacc_powlaw)
        
        #The low mass - true ID true
        trueid_lm2 = RooGenericPdf("trueid_lm2","exp(-100.*abs(@0-8))",RooArgList(trueIDVar_B))
        
        #The low mass - mistag
        mistag_dsstpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsstPiPdf_m_both_mistag"), debug)
        mistag_dsrho = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsRhoPdf_m_both_mistag"), debug)
        mistag_dsstrho = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsstRhoPdf_m_both_mistag"), debug)
        total_mistag_lm2 = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"), debug)
        #RooAddPdf("total_mistag_lm2","total_mistag_lm",RooArgList(mistag_dsstpi,mistag_dsrho,mistag_dsstrho),RooArgList(frac_g2_1, frac_g2_2))
        
        #The low mass - total
        timemistag_lm2 = RooProdPdf("timemistag_lm2","timemistag_lm2",RooArgSet(total_mistag_lm2),
                                    RooFit.Conditional(RooArgSet(time_lm2),
                                                       RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_lm2 = RooProdPdf("timeandmass_lm2","timeandmass_lm2",RooArgList(timemistag_lm2,mass_lm2,trueid_lm2))                
    #------------------------------------------------- Total bkg ----------------------------------------------------#
    
        #Total background
        total_back_pdf = RooAddPdf("total_back_pdf","total_back_pdf",RooArgList(timeandmass_dk,timeandmass_dsk,timeandmass_dspi,timeandmass_lck,timeandmass_dsdsstp,timeandmass_combo,timeandmass_lm1,timeandmass_lm2),RooArgList(num_dk,num_dsk,num_dspi,num_lck,num_dsdsstp,num_combo,num_lm1,num_lm2))
        
        #Total
        total_pdf = RooAddPdf("total_pdf","total_pdf",RooArgList(timeandmass_signal,total_back_pdf))
        getattr(workout,'import')(total_pdf)
        
        #Generate
        gendata.append(total_pdf.generate(RooArgSet(massVar_B,timeVar_B,trueIDVar_B,bTagMap,fChargeMap,mistagVar_B),numberOfEvents))
        tree = gendata[-1].store().tree()
        
        data.append(SFitUtils.CopyDataForToys(tree,
                                              TString(mVar),
                                              TString(tVar),
                                              TString(tagdec)+TString("_idx"),
                                              TString(tagomega),
                                              TString(charge)+TString("_idx"),
                                              TString(trueID),
                                              TString("dataSetBsDsK_down_kkpi"),
                                              debug))
        
        getattr(workout,'import')(data[-1])
    
        
        #Plot what we just did
        if single :
            canv_Bmass = TCanvas("canv_Bmass","canv_Bmass")
            frame_Bmass = massVar_B.frame()
            data[i].plotOn(frame_Bmass,RooFit.Binning(100))
            total_pdf.plotOn(frame_Bmass)
            total_pdf.plotOn(frame_Bmass,RooFit.Components("SigEPDF_all"),RooFit.LineStyle(2))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgBd2DKPdf_m_both"),RooFit.LineStyle(2),RooFit.LineColor(2))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgLb2LcKPdf_m_both"),RooFit.LineStyle(1),RooFit.LineColor(3))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("total_lm"),RooFit.LineStyle(1),RooFit.LineColor(6))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("total_lm2"),RooFit.LineStyle(1),RooFit.LineColor(5))
            #total_pdf.plotOn(frame_Bmass,RooFit.Components("gaussian_lm2"),RooFit.LineStyle(1),RooFit.LineColor(5))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("SigEPDF_bddsk"),RooFit.LineStyle(1),RooFit.LineColor(7))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgBsDsPi_m_down_kkpi"),RooFit.LineStyle(1),RooFit.LineColor(8))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("total_dsdsstp"),RooFit.LineStyle(1),RooFit.LineColor(9))        
            total_pdf.plotOn(frame_Bmass,RooFit.Components("mass_combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Bmass.Draw()
            canv_Bmass.Print("Bmass_DsK_Toys.pdf") 
            
            canv_Btag = TCanvas("canv_Btag","canv_Btag")
            frame_Btag = mistagVar_B.frame()
            data[i].plotOn(frame_Btag,RooFit.Binning(100))
            frame_Btag.Draw()
            canv_Btag.Print("Btagomega_DsK_Toys.pdf")
            
            gStyle.SetOptLogy(1)
            
            canv_Btime = TCanvas("canv_Btime","canv_Btime")
            frame_Btime = timeVar_B.frame()
            data[i].plotOn(frame_Btime,RooFit.Binning(100))
            #total_pdf.plotOn(frame_Btime)
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_signal"),RooFit.LineStyle(2))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_dk"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lck"),RooFit.LineStyle(1),RooFit.LineColor(3))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm"),RooFit.LineStyle(1),RooFit.LineColor(6))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Btime.Draw()
            canv_Btime.Print("Btime_DsK_Toys.pdf")
        if not single :
            workout.writeToFile("/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/DsK_Toys_Full_Work_2kSample_"+str(i)+".root")
            outfile  = TFile("/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/DsK_Toys_Full_Tree_2kSample_"+str(i)+".root","RECREATE")
        else :
                workout.writeToFile("Data_Toys_Single_Work_DsK.root")
                outfile  = TFile("Data_Toys_Single_Tree_DsK.root","RECREATE")
        tree.Write()
        outfile.Close()
    
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
                   default = True,
                                      )
parser.add_option( '--numberOfToys',
                   dest = 'numberOfToys',
                   default = 200)

parser.add_option( '--numberOfEvents',
                   dest = 'numberOfEvents',
                   default = 6000)


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
                                
