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

import ROOT
from ROOT import *
from math import *
import os,sys
from optparse import OptionParser
from os.path  import join


import GaudiPython
from B2DXFitters import taggingutils, cpobservables
GaudiPython.loaddict( 'B2DXFittersDict' )
GeneralUtils = GaudiPython.gbl.GeneralUtils
SFitUtils = GaudiPython.gbl.SFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

RooRandom.randomGenerator().SetSeed(4613508);
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

    fileName = "/afs/cern.ch/work/a/adudziak/public/workspace/work_dspi.root"
    fileName2 = "/afs/cern.ch/work/a/adudziak/public/workspace/work_toys_dspi.root"
    workName = 'workspace'
    
    mVar     = 'lab0_MassFitConsD_M'
    tVar     = 'lab0_LifetimeFit_ctau'
    trueID   = 'lab0_TRUEID'
    charge   = 'lab1_ID'
    tagdec   = 'lab0_BsTaggingTool_TAGDECISION_OS'
    tagomega = 'lab0_BsTaggingTool_TAGOMEGA_OS'

    for i in range(0,ntoys) :

        #Create out workspace
        workout = RooWorkspace("workspace","workspace")

        #Read workspace with PDFs
        workspace = GeneralUtils.LoadWorkspace(TString(fileName),TString(workName),debug)
        workspace.Print("v")

        workspace_mistag = GeneralUtils.LoadWorkspace(TString(fileName2),TString(workName), debug)
        workspace_mistag.Print("v")
            
        massVar_B   = GeneralUtils.GetObservable(workspace,TString(mVar), debug)
        timeVar_B   = RooRealVar(tVar,tVar,0,15)
        trueIDVar_B = RooRealVar(trueID,trueID,0,100) 
        mistagVar_B = GeneralUtils.GetObservable(workspace_mistag,TString(tagomega), debug)
        mistagVar_B.setMax(1.0)
    
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
        
        edoubleCB_signal = Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBs, sigma1VarBs, alpha1VarBs, n1VarBs, sigma2VarBs, alpha2VarBs,n2VarBs, fracVarBs, num_signal, "all", "Bs", debug )
    
        #The signal - acceptance
        tacc_slope_signal   = RooRealVar('tacc_slope_signal' , 'BdPTAcceptance_slope_signal' , myconfigfile["tacc_slope_signal"]  )
        tacc_offset_signal  = RooRealVar('tacc_offset_signal', 'BdPTAcceptance_offset_signal', myconfigfile["tacc_offset_signal"] )
        tacc_beta_signal    = RooRealVar('tacc_beta_signal'  , 'BdPTAcceptance_beta_signal',   myconfigfile["tacc_beta_signal"]   )
        tacc_signal         = BdPTAcceptance('BsPTAccFunction_signal', 'signal decay time acceptance function' ,
                                            timeVar_B, tacc_beta_signal, tacc_slope_signal, tacc_offset_signal)

        #The signal - resolution
        trm_signal = RooGaussModel('PTRMGaussian_signal','PTRMGaussian_signal',timeVar_B, zero, TauRes)
        
        #The signal - time
        tagEff_signal    = RooRealVar("tagEff_signal","tagEff_signal", myconfigfile["tagEff_signal"])
        tagWeight_signal = TagEfficiencyWeight('tagWeight_signal','tagWeight_signal',bTagMap,tagEff_signal)
        
        S_signal    = RooRealVar('S_signal', 'S coeff. signal', 0.) 
        D_signal    = RooRealVar('D_signal', 'D coeff. signal', 0.) 
        
        untaggedWeight_signal   = IfThreeWayCat('untaggedWeight_signal', 'untaggedWeight_signal', bTagMap, one, two, one)
        Dilution_signal         = RooFormulaVar('Dilution_signal',"1-2*@0",RooArgList(mistagVar_B))
        mixState_signal         = RooFormulaVar('mixState_signal','@0*@1',RooArgList(bTagMap,fChargeMap)) 
        
        Cos_signal              = RooProduct('sigCosSin_i0_signal', 'sigCosSin_i0 signal', 
                                             RooArgSet(mixState_signal, Dilution_signal, tagWeight_signal))
        Cosh_signal             = RooProduct('sigCosh_signal', 'cosh coefficient signal', 
                                             RooArgSet(untaggedWeight_signal, tagWeight_signal))
    
        time_signal_noacc       = RooBDecay('time_signal_noacc','time_signal_noacc', timeVar_B, Gammas, DeltaGammas, 
                                            Cosh_signal, D_signal, Cos_signal, S_signal,
                                            DeltaMs,trm_signal, RooBDecay.SingleSided)

        time_signal             = RooEffProd('time_signal','time_signal',time_signal_noacc,tacc_signal)
        
        #The signal - true ID
        trueid_signal = RooGenericPdf("trueid_signal","exp(-100.*abs(@0-1))",RooArgList(trueIDVar_B))
        
        #The signal - mistag
        mistag_signal = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_mistag"), debug)

        #The signal - total
        timemistag_signal = RooProdPdf("timemistag_signal","timemistag_signal",RooArgSet(mistag_signal),
                                       RooFit.Conditional(RooArgSet(time_signal),
                                                          RooArgSet(timeVar_B,bTagMap,fChargeMap)))
  
        timeandmass_signal = RooProdPdf("timeandmass_signal","timeandmass_signal",RooArgList(timemistag_signal,edoubleCB_signal,trueid_signal))
 
    #------------------------------------------------- Bd -> DPi -----------------------------------------------------#
     
        #The Bd->DPi - mass
        mass_dpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DPiPdf_m_down_kpipi"), debug)
        num_dpi = RooRealVar("num_dpi","num_dpi",myconfigfile["num_dpi"])
        
        #The Bd->DPi - acceptance
        tacc_slope_dpi   = RooRealVar('tacc_slope_dpi' , 'BdPTAcceptance_slope_dpi' , myconfigfile["tacc_slope_dpi"]  )
        tacc_offset_dpi  = RooRealVar('tacc_offset_dpi', 'BdPTAcceptance_offset_dpi', myconfigfile["tacc_offset_dpi"] )
        tacc_beta_dpi    = RooRealVar('tacc_beta_dpi'  , 'BdPTAcceptance_beta_dpi',   myconfigfile["tacc_beta_dpi"] )
        tacc_dpi         = BdPTAcceptance('BsPTAccFunction_dpi', 'dpi decay time acceptance function' ,
                              timeVar_B, tacc_beta_dpi, tacc_slope_dpi, tacc_offset_dpi)

        #The dpi - resolution
        trm_dpi = RooGaussModel('PTRMGaussian_dpi','PTRMGaussian_dpi',timeVar_B, zero, TauRes)

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

        untaggedWeight_dpi   = IfThreeWayCat('untaggedWeight_dpi', 'untaggedWeight_dpi', bTagMap, one, two, one)
        Dilution_dpi         = RooFormulaVar('Dilution_dpi',"1-2*@0",RooArgList(mistagVar_B))
        mixState_dpi         = RooFormulaVar('mixState_dpi','@0*@1',RooArgList(bTagMap,fChargeMap))

        weightedDs_dpi       = IfThreeWayCat('weightedDs_dpi', 'weightedDs_dpi',fChargeMap, D_dpi, zero, Dbar_dpi)
        weightedSs_dpi       = IfThreeWayCat('weightedSs_dpi', 'weightedSs_dpi',fChargeMap, Sbar_dpi, zero, S_dpi)    
        
        CosSin_i0_dpi        = RooProduct('CosSin_i0_dpi', 'CosSin_i0_dpi', RooArgSet(mixState_dpi, Dilution_dpi, tagWeight_dpi))
        
        Cos_dpi              = RooProduct('Cos_dpi', 'Cos dpi', RooArgSet(C_dpi,CosSin_i0_dpi))
        Cosh_dpi             = RooProduct('Cosh_dpi', 'cosh coefficient dpi', RooArgSet(untaggedWeight_dpi, tagWeight_dpi))
        Sin_dpi              = RooProduct('Sin_dpi', 'Sin dpi', RooArgSet(CosSin_i0_dpi,weightedSs_dpi))
        Sinh_dpi             = RooProduct('Sinh_dpi','Sinh_dpi',RooArgSet(Cosh_dpi,weightedDs_dpi))    
        
        time_dpi_noacc       = RooBDecay('time_dpi_noacc','time_dpi_noacc', timeVar_B, Gammad, DeltaGammad, 
                                         Cosh_dpi, Sinh_dpi, Cos_dpi, Sin_dpi,
                                         DeltaMd,trm_dpi, RooBDecay.SingleSided)

        time_dpi             = RooEffProd('time_dpi','time_dpi',time_dpi_noacc,tacc_dpi)
        
        #The Bd->DPi - mistag
        mistag_dpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_mistag"), debug)
        
        #The Bd->DPi - true ID
        trueid_dpi = RooGenericPdf("trueid_dpi","exp(-100.*abs(@0-2))",RooArgList(trueIDVar_B))        

        #The Bd->DPi - total
        timemistag_dpi  = RooProdPdf("timemistag_dpi","timemistag_dpi",RooArgSet(mistag_dpi),
                                     RooFit.Conditional(RooArgSet(time_dpi),
                                                        RooArgSet(timeVar_B,bTagMap,fChargeMap)))   

        timeandmass_dpi = RooProdPdf("timeandmass_dpi","timeandmass_dpi",RooArgList(mass_dpi,trueid_dpi,timemistag_dpi))

    #------------------------------------------------- Bd -> DsPi ----------------------------------------------------#

        #The Bd->DsPi - mass
        meanVarBd   =  RooRealVar( "DblCBBdPDF_mean" ,  "mean",    myconfigfile["mean"]-86.8)
        sigma1VarBd =  RooRealVar( "DblCBBdPDF_sigma1", "sigma1",  myconfigfile["sigma1"]*myconfigfile["ratio1"] )
        sigma2VarBd =  RooRealVar( "DblCBBdPDF_sigma2", "sigma2",  myconfigfile["sigma2"]*myconfigfile["ratio2"] )
        
        num_bddspi = RooRealVar("num_dspi","num_dspi",myconfigfile["num_dspi"])
        mass_bddspi= Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBd, sigma1VarBd, alpha1VarBs, n1VarBs, sigma2VarBd, alpha2VarBs,
                                                                 n2VarBs, fracVarBs, num_bddspi, "bddspi", "Bd", debug )

        #The Bd->DsPi - acceptance
        tacc_slope_bddspi   = RooRealVar('tacc_slope_bddspi' , 'BdPTAcceptance_slope_bddspi' , myconfigfile["tacc_slope_dspi"]  )
        tacc_offset_bddspi  = RooRealVar('tacc_offset_bddspi', 'BdPTAcceptance_offset_bddspi', myconfigfile["tacc_offset_dspi"] )
        tacc_beta_bddspi    = RooRealVar('tacc_beta_bddspi'  , 'BdPTAcceptance_beta_bddspi',   myconfigfile["tacc_beta_dspi"]   )
        tacc_bddspi         = BdPTAcceptance('BsPTAccFunction_bddspi', 'bddspi decay time acceptance function' ,
                                             timeVar_B, tacc_beta_bddspi, tacc_slope_bddspi, tacc_offset_bddspi)

        #The Bd->DsPi - resolution
        trm_bddspi = RooGaussModel('PTRMGaussian_bddspi','PTRMGaussian_bddspi',timeVar_B, zero, TauRes)

        #The Bd->DsPi - time
        #First generate the observables
        tagEff_bddspi    = RooRealVar("tagEff_bddspi","tagEff_bddspi",myconfigfile["tagEff_dspi"])
        tagWeight_bddspi = TagEfficiencyWeight('tagWeight_bddspi','tagWeight_bddspi',bTagMap,tagEff_bddspi)
    
        S_bddspi    = RooRealVar('S_bddspi', 'S coeff. bddspi', 0.) 
        D_bddspi    = RooRealVar('D_bddspi', 'D coeff. bddspi', 0.) 
        
        untaggedWeight_bddspi   = IfThreeWayCat('untaggedWeight_bddspi', 'untaggedWeight_bddspi', bTagMap, one, two, one)
        Dilution_bddspi         = RooFormulaVar('Dilution_bddspi',"1-2*@0",RooArgList(mistagVar_B))
        mixState_bddspi         = RooFormulaVar('mixState_bddspi','@0*@1',RooArgList(bTagMap,fChargeMap))
        
        Cos_bddspi              = RooProduct('sigCosSin_i0_bddspi', 'sigCosSin_i0 bddspi',
                                             RooArgSet(mixState_bddspi, Dilution_bddspi, tagWeight_bddspi))
        Cosh_bddspi             = RooProduct('sigCosh_bddspi', 'cosh coefficient bddspi',
                                             RooArgSet(untaggedWeight_bddspi, tagWeight_bddspi))
        
        time_bddspi_noacc       = RooBDecay('time_bddspi_noacc','time_bddspi_noacc', timeVar_B, Gammad, DeltaGammad,
                                            Cosh_bddspi, D_bddspi, Cos_bddspi, S_bddspi,
                                            DeltaMd,trm_bddspi, RooBDecay.SingleSided)

        time_bddspi             = RooEffProd('time_bddspi','time_bddspi',time_bddspi_noacc,tacc_bddspi)
        
        #The Bd->DsPi - mistag
        mistag_bddspi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_mistag"), debug)
        #Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBdDsPiPdf_m_down_mistag"))

        #The Bd->DsPi - true ID
        trueid_bddspi = RooGenericPdf("trueid_bddspi","exp(-100.*abs(@0-3))",RooArgList(trueIDVar_B))        
    
        #The Bd->DsPi - total
        timemistag_bddspi  = RooProdPdf("timemistag_bddspi","timemistag_bddspi",RooArgSet(mistag_bddspi),
                                        RooFit.Conditional(RooArgSet(time_bddspi),
                                                           RooArgSet(timeVar_B,bTagMap,fChargeMap)))
    
        timeandmass_bddspi = RooProdPdf("timeandmass_bddspi","timeandmass_bddspi",RooArgList(mass_bddspi,trueid_bddspi,timemistag_bddspi))

    #------------------------------------------------- Lb -> LcPi -----------------------------------------------------#
    
        #The Lb->LcPi - mass
        mass_lcpi =  Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgLb2LcPiPdf_m_both"), debug)
        num_lcpi = RooRealVar("num_lcpi","num_lcpi", myconfigfile["num_lcpi"])
        
        #The Lb->LcPi - acceptance
        tacc_slope_lcpi   = RooRealVar('tacc_slope_lcpi' , 'BdPTAcceptance_slope_lcpi' , myconfigfile["tacc_slope_lcpi"]  )
        tacc_offset_lcpi  = RooRealVar('tacc_offset_lcpi', 'BdPTAcceptance_offset_lcpi', myconfigfile["tacc_offset_lcpi"] )
        tacc_beta_lcpi    = RooRealVar('tacc_beta_lcpi'  , 'BdPTAcceptance_beta_lcpi',   myconfigfile["tacc_beta_lcpi"]   )
        tacc_lcpi         = BdPTAcceptance('BsPTAccFunction_lcpi', 'lcpi decay time acceptance function' ,
                                           timeVar_B, tacc_beta_lcpi, tacc_slope_lcpi, tacc_offset_lcpi)
        
        #The Lb->LcPi - resolution
        trm_lcpi = RooGaussModel('PTRMGaussian_lcpi','PTRMGaussian_lcpi',timeVar_B, zero, TauRes)

        #The Lb->LcPi - time
        tagEff_lcpi    = RooRealVar("tagEff_lcpi","tagEff_lcpi",myconfigfile["tagEff_lcpi"])
        tagWeight_lcpi = TagEfficiencyWeight('tagWeight_lcpi','tagWeight_lcpi',bTagMap,tagEff_lcpi)

        S_lcpi    = RooRealVar('S_lcpi', 'S coeff. lcpi', 0.)
        D_lcpi    = RooRealVar('D_lcpi', 'D coeff. lcpi', 0.)

        untaggedWeight_lcpi   = IfThreeWayCat('untaggedWeight_lcpi', 'untaggedWeight_lcpi', bTagMap, one, two, one)
        Dilution_lcpi         = RooFormulaVar('Dilution_lcpi',"1-2*@0",RooArgList(mistagVar_B))
        mixState_lcpi         = RooFormulaVar('mixState_lcpi','@0*@1',RooArgList(bTagMap,fChargeMap))
        
        Cos_lcpi              = RooProduct('sigCosSin_i0_lcpi', 'sigCosSin_i0 lcpi',
                                           RooArgSet(mixState_lcpi, Dilution_lcpi, tagWeight_lcpi))
        Cosh_lcpi             = RooProduct('sigCosh_lcpi', 'cosh coefficient lcpi',
                                           RooArgSet(untaggedWeight_lcpi, tagWeight_lcpi))
        
        time_lcpi_noacc       = RooBDecay('time_lcpi_noacc','time_lcpi_noacc', timeVar_B, GammaLb, zero,
                                          Cosh_lcpi, D_lcpi, Cos_lcpi, S_lcpi,
                                          zero,trm_lcpi, RooBDecay.SingleSided) 

        time_lcpi             = RooEffProd('time_lcpi','time_lcpi',time_lcpi_noacc,tacc_lcpi)
        
        #The Lb->LcPi - mistag
        mistag_lcpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_mistag"), debug)
        #Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgLb2LcPiPdf_m_mistag"))

        #The Lb->LcPi - true ID
        trueid_lcpi = RooGenericPdf("trueid_lcpi","exp(-100.*abs(@0-4))",RooArgList(trueIDVar_B))
    
        #The Lb->LcPi - total
        timemistag_lcpi  = RooProdPdf("timemistag_lcpi","timemistag_lcpi",RooArgSet(mistag_lcpi),
                                      RooFit.Conditional(RooArgSet(time_lcpi),
                                                         RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_lcpi = RooProdPdf("timeandmass_lcpi","timeandmass_lcpi",RooArgList(mass_lcpi,trueid_lcpi,timemistag_lcpi))
 
    #------------------------------------------------- Combinatorial -----------------------------------------------------#

        #The combinatorics - mass
        exposlope_combo = RooRealVar("exposlope_combo","exposlope_combo", myconfigfile["exposlope_combo"])
        mass_combo = RooExponential("mass_combo","mass_combo",massVar_B,exposlope_combo)
        num_combo = RooRealVar("num_combo","num_combo", myconfigfile["num_combo"])
        
        #The combinatorics - acceptance
        tacc_slope_combo   = RooRealVar('tacc_slope_combo' , 'BdPTAcceptance_slope_combo' , myconfigfile["tacc_slope_combo"])
        tacc_offset_combo  = RooRealVar('tacc_offset_combo', 'BdPTAcceptance_offset_combo', myconfigfile["tacc_offset_combo"])
        tacc_beta_combo    = RooRealVar('tacc_beta_combo'  , 'BdPTAcceptance_beta_combo',   myconfigfile["tacc_beta_combo"])
        tacc_combo         = BdPTAcceptance('BsPTAccFunction_combo', 'combo decay time acceptance function' ,
                                            timeVar_B, tacc_beta_combo, tacc_slope_combo, tacc_offset_combo)
        
        #The combinatorics - resolution
        trm_combo = RooGaussModel('PTRMGaussian_combo','PTRMGaussian_combo',timeVar_B, zero, TauRes)
        
        #The combinatorics - time
        tagEff_combo    = RooRealVar("tagEff_combo","tagEff_combo", myconfigfile["tagEff_combo"])
        tagWeight_combo = TagEfficiencyWeight('tagWeight_combo','tagWeight_combo',bTagMap,tagEff_combo)
        
        S_combo    = RooRealVar('S_combo', 'S coeff. combo', 0.)
        D_combo    = RooRealVar('D_combo', 'D coeff. combo', 0.)
        
        untaggedWeight_combo   = IfThreeWayCat('untaggedWeight_combo', 'untaggedWeight_combo', bTagMap, one, two, one)
        Dilution_combo         = RooFormulaVar('Dilution_combo',"1-2*@0",RooArgList(mistagVar_B))
        mixState_combo         = RooFormulaVar('mixState_combo','@0*@1',RooArgList(bTagMap,fChargeMap))
        
        Cos_combo              = RooProduct('sigCosSin_i0_combo', 'sigCosSin_i0 combo',
                                            RooArgSet(mixState_combo, Dilution_combo, tagWeight_combo))
        Cosh_combo             = RooProduct('sigCosh_combo', 'cosh coefficient combo',
                                            RooArgSet(untaggedWeight_combo, tagWeight_combo))

        time_combo_noacc       = RooBDecay('time_combo_noacc','time_combo_noacc', timeVar_B, GammaCombo, zero,
                                           Cosh_combo, D_combo, Cos_combo, S_combo,
                                           zero,trm_combo, RooBDecay.SingleSided)         
        
        time_combo             = RooEffProd('time_combo','time_combo',time_combo_noacc,tacc_combo)
        
        #The combinatorics - true ID
        trueid_combo = RooGenericPdf("trueid_combo","exp(-100.*abs(@0-10))",RooArgList(trueIDVar_B))
        
        #The combinatorics - mistag
        mistag_combo = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_mistag"), debug)
    
        #The combinatorics - total
        timemistag_combo  = RooProdPdf("timemistag_combo","timemistag_combo",RooArgSet(mistag_combo),
                                       RooFit.Conditional(RooArgSet(time_combo),
                                                          RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_combo = RooProdPdf("timeandmass_combo","timeandmass_combo",RooArgList(mass_combo,trueid_combo,timemistag_combo))

    #------------------------------------------------- Low Mass Bs-------------------------------------------------------#

        #The low mass - mass
        num_lm1 = RooRealVar("num_lm1","num_lm1", myconfigfile["num_lm1"])
        
        mass_dsstpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstPiPdf_m_both"), debug)
        mass_dsrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsRhoPdf_m_both"), debug)
        mass_dsstrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBs2DsstRhoPdf_m_both"), debug)
        
        frac_g1_1 = RooRealVar("frac_g1_1","frac_g1_1", myconfigfile["frac_g1_1"])
        frac_g1_2 = RooRealVar("frac_g1_2","frac_g1_2", myconfigfile["frac_g1_2"])
        
        total_lm1 = RooAddPdf("total_lm1","total_lm1",RooArgList(mass_dsstpi,mass_dsrho,mass_dsstrho),RooArgList(frac_g1_1, frac_g1_2))
    
        #The low mass - acceptance
        tacc_slope_lm1   = RooRealVar('tacc_slope_lm1' , 'BdPTAcceptance_slope_lm1' , myconfigfile["tacc_slope_lm1"])
        tacc_offset_lm1  = RooRealVar('tacc_offset_lm1', 'BdPTAcceptance_offset_lm1', myconfigfile["tacc_offset_lm1"])
        tacc_beta_lm1    = RooRealVar('tacc_beta_lm1'  , 'BdPTAcceptance_beta_lm1',   myconfigfile["tacc_beta_lm1"])
        tacc_lm1         = BdPTAcceptance('BsPTAccFunction_lm1', 'lm1 decay time acceptance function' ,
                                          timeVar_B, tacc_beta_lm1, tacc_slope_lm1, tacc_offset_lm1)
        
        #The low mass - resolution
        trm_lm1 = RooGaussModel('PTRMGaussian_lm1','PTRMGaussian_lm1',timeVar_B, zero, TauRes)
        
        #The low mass - time
        tagEff_lm1    = RooRealVar("tagEff_lm1","tagEff_lm1", myconfigfile["tagEff_lm1"])
        tagWeight_lm1 = TagEfficiencyWeight('tagWeight_lm1','tagWeight_lm1',bTagMap,tagEff_lm1)
        
        S_lm1    = RooRealVar('S_lm1', 'S coeff. lm1', 0.)
        D_lm1    = RooRealVar('D_lm1', 'D coeff. lm1', 0.)
        
        untaggedWeight_lm1   = IfThreeWayCat('untaggedWeight_lm1', 'untaggedWeight_lm1', bTagMap, one, two, one)
        Dilution_lm1         = RooFormulaVar('Dilution_lm1',"1-2*@0",RooArgList(mistagVar_B))
        mixState_lm1         = RooFormulaVar('mixState_lm1','@0*@1',RooArgList(bTagMap,fChargeMap))
        
        Cos_lm1              = RooProduct('sigCosSin_i0_lm1', 'sigCosSin_i0 lm1',
                                          RooArgSet(mixState_lm1, Dilution_lm1, tagWeight_lm1))
        Cosh_lm1             = RooProduct('sigCosh_lm1', 'cosh coefficient lm1', 
                                          RooArgSet(untaggedWeight_lm1, tagWeight_lm1))
                                                
        time_lm1_noacc       = RooBDecay('time_lm1_noacc','time_lm1_noacc', timeVar_B, Gammas, DeltaGammas,
                                         Cosh_lm1, D_lm1, Cos_lm1, S_lm1,
                                         DeltaMs,trm_lm1, RooBDecay.SingleSided)
        
        time_lm1             = RooEffProd('time_lm1','time_lm1',time_lm1_noacc,tacc_lm1)
        
        #The low mass - mistag
        #mistag_dsstpi =Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsstPiPdf_m_mistag"), debug)
        #mistag_dsrho =Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsRhoPdf_m_mistag"), debug)
        #mistag_dsstrho =Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBs2DsstRhoPdf_m_mistag"), debug)
        total_mistag_lm1 = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_mistag"),debug)
        #RooAddPdf("total_mistag_lm1","total_mistag_lm1",RooArgList(mistag_dsstpi,mistag_dsrho,mistag_dsstrho),RooArgList(frac_g1_1, frac_g1_2))

        #The low mass - true ID
        trueid_lm1 = RooGenericPdf("trueid_lm1","exp(-100.*abs(@0-5))",RooArgList(trueIDVar_B))
        
        #The low mass - total
        timemistag_lm1  = RooProdPdf("timemistag_lm1","timemistag_lm1",RooArgSet(total_mistag_lm1),
                                     RooFit.Conditional(RooArgSet(time_lm1),
                                                        RooArgSet(timeVar_B,bTagMap,fChargeMap)))
        
        timeandmass_lm1 = RooProdPdf("timeandmass_lm1","timeandmass_lm1",RooArgList(total_lm1,trueid_lm1,timemistag_lm1))

    #------------------------------------------------- Low Mass Bd-------------------------------------------------------#

        mass_bddrho = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DRhoPdf_m_both"), debug)
        mass_bddstpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DstPiPdf_m_both"), debug)
        mass_bddsstpi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBd2DsstPiPdf_m_both"), debug)
        
        frac_g2_1 = RooRealVar("frac_g2_1","frac_g2_1", myconfigfile["frac_g2_1"])
        frac_g2_2 = RooRealVar("frac_g2_2","frac_g2_2", myconfigfile["frac_g2_1"])
        
        total_lm2 = RooAddPdf("total_lm2","total_lm2",RooArgList(mass_bddsstpi,mass_bddstpi,mass_bddrho),RooArgList(frac_g2_1, frac_g2_2))
        num_lm2 = RooRealVar("num_lm2","num_lm2", myconfigfile["num_lm2"])
        
        #The low mass - acceptance
        tacc_slope_lm2   = RooRealVar('tacc_slope_lm2' , 'BdPTAcceptance_slope_lm2' , myconfigfile["tacc_slope_lm2"])
        tacc_offset_lm2  = RooRealVar('tacc_offset_lm2', 'BdPTAcceptance_offset_lm2', myconfigfile["tacc_offset_lm2"])
        tacc_beta_lm2    = RooRealVar('tacc_beta_lm2'  , 'BdPTAcceptance_beta_lm2',   myconfigfile["tacc_beta_lm2"])
        tacc_lm2         = BdPTAcceptance('BsPTAccFunction_lm2', 'lm2 decay time acceptance function' ,
                                          timeVar_B, tacc_beta_lm2, tacc_slope_lm2, tacc_offset_lm2)
        
        #The low mass - resolution   
        trm_lm2 = RooGaussModel('PTRMGaussian_lm2','PTRMGaussian_lm2',timeVar_B, zero, TauRes)
        
        #The low mass - time
        #First generate the observables
        ACPobs_lm2 = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_d"], myconfigfile["ArgLbarfbar_d"], myconfigfile["ModLf_d"])
    
        C_lm2     = RooRealVar('C_lm2','C_lm2',ACPobs_lm2.Cf())
        S_lm2     = RooRealVar('S_lm2','S_lm2',ACPobs_lm2.Sf())
        D_lm2     = RooRealVar('D_lm2','D_lm2',ACPobs_lm2.Df())
        Sbar_lm2  = RooRealVar('Sbar_lm2','Sbar_lm2',ACPobs_lm2.Sfbar())
        Dbar_lm2  = RooRealVar('Dbar_lm2','Dbar_lm2',ACPobs_lm2.Dfbar())
                        
        tagEff_lm2    = RooRealVar("tagEff_lm2","tagEff_lm2", myconfigfile["tagEff_lm2"])
        tagWeight_lm2 = TagEfficiencyWeight("tagWeight_lm2","tagWeight_lm2",bTagMap,tagEff_lm2)
        
        untaggedWeight_lm2   = IfThreeWayCat('untaggedWeight_lm2', 'untaggedWeight_lm2', bTagMap, one, two, one)
        Dilution_lm2         = RooFormulaVar('Dilution_lm2',"1-2*@0",RooArgList(mistagVar_B))
        mixState_lm2         = RooFormulaVar('mixState_lm2','@0*@1',RooArgList(bTagMap,fChargeMap))
        
        weightedDs_lm2       = IfThreeWayCat('weightedDs_lm2', 'weightedDs_lm2',fChargeMap, D_lm2, zero, Dbar_lm2)
        weightedSs_lm2       = IfThreeWayCat('weightedSs_lm2', 'weightedSs_lm2',fChargeMap, Sbar_lm2, zero, S_lm2)
    
        CosSin_i0_lm2        = RooProduct('CosSin_i0_lm2', 'CosSin_i0_lm2', RooArgSet(mixState_lm2, Dilution_lm2, tagWeight_lm2))
        
        Cos_lm2              = RooProduct('Cos_lm2', 'Cos lm2', RooArgSet(C_lm2,CosSin_i0_lm2))
        Cosh_lm2             = RooProduct('Cosh_lm2', 'cosh coefficient lm2', RooArgSet(untaggedWeight_lm2, tagWeight_lm2))
        Sin_lm2              = RooProduct('Sin_lm2', 'Sin lm2', RooArgSet(CosSin_i0_lm2,weightedSs_lm2))
        Sinh_lm2             = RooProduct('Sinh_lm2','Sinh_lm2',RooArgSet(Cosh_lm2,weightedDs_lm2))
        
        time_lm2_noacc       = RooBDecay('time_lm2_noacc','time_lm2_noacc', timeVar_B, Gammad, DeltaGammad,
                                         Cosh_lm2, Sinh_lm2, Cos_lm2, Sin_lm2,
                                         DeltaMd,trm_lm2, RooBDecay.SingleSided)
        
        time_lm2             = RooEffProd('time_lm2','time_lm2',time_lm2_noacc,tacc_lm2)
    
        #The low mass - mistag
        #mistag_bddrho =Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBd2DRhoPdf_m_mistag"))
        #mistag_bddstpi =Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBd2DstPiPdf_m_mistag"))
        #mistag_bddsstpi =Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBd2DsstPiPdf_m_mistag"))
        total_mistag_lm2 = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_mistag"), debug)
        #RooAddPdf("total_mistag_lm2","total_mistag_lm2",RooArgList(mistag_bddsstpi,mistag_bddstpi,mistag_bddrho),RooArgList(frac_g2_1, frac_g2_2))

        #The low mass - true ID
        trueid_lm2 = RooGenericPdf("trueid_lm2","exp(-100.*abs(@0-6))",RooArgList(trueIDVar_B))

        #The low mass - total
        timemistag_lm2  = RooProdPdf("timemistag_lm2","timemistag_lm2",RooArgSet(total_mistag_lm2),
                                     RooFit.Conditional(RooArgSet(time_lm2),
                                                        RooArgSet(timeVar_B,bTagMap,fChargeMap)))

        timeandmass_lm2 = RooProdPdf("timeandmass_lm2","timeandmass_lm2",RooArgList(total_lm2,trueid_lm2,timemistag_lm2))       
 
    #------------------------------------------------- Total bkg -----------------------------------------------------#

        #Total background
        total_back_pdf = RooAddPdf("total_back_pdf","total_back_pdf",
                                   RooArgList(timeandmass_dpi,timeandmass_lcpi,timeandmass_combo, timeandmass_bddspi, timeandmass_lm1, timeandmass_lm2),
                                   RooArgList(num_dpi,num_lcpi,num_combo, num_bddspi, num_lm1, num_lm2))
   
        #Total
        total_pdf = RooAddPdf("total_pdf","total_pdf",RooArgList(timeandmass_signal,total_back_pdf))
        getattr(workout,'import')(total_pdf)
        

        #Generate
        gendata.append(total_pdf.generate(RooArgSet(massVar_B,timeVar_B,trueIDVar_B,bTagMap,fChargeMap,mistagVar_B),numberOfEvents))
        tree = gendata[i].store().tree()
        
        data.append(SFitUtils.CopyDataForToys(tree,
                                              TString(mVar),
                                              TString(tVar),
                                              TString(tagdec)+TString("_idx"),
                                              TString(tagomega),
                                              TString(charge)+TString("_idx"),
                                              TString(trueID),
                                              TString("dataSetBsDsPi_down_kkpi"), debug))
       
        getattr(workout,'import')(data[i])
    
                                                                                

    #exit(0)
        #Plot what we just did
        if single :
            canv_Bmass = TCanvas("canv_Bmass","canv_Bmass")
            frame_Bmass = massVar_B.frame()
            data[i].plotOn(frame_Bmass,RooFit.Binning(100))
            total_pdf.plotOn(frame_Bmass)
            total_pdf.plotOn(frame_Bmass,RooFit.Components("SigEPDF_all"),RooFit.LineStyle(2))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgBd2DPiPdf_m_down_kpipi"),RooFit.LineStyle(2),RooFit.LineColor(2))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("PhysBkgLb2LcPiPdf_m_both"),RooFit.LineStyle(1),RooFit.LineColor(3))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("total_lm1"),RooFit.LineStyle(1),RooFit.LineColor(6))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("total_lm2"),RooFit.LineStyle(1),RooFit.LineColor(7))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("SigEPDF_bddspi"),RooFit.LineStyle(1),RooFit.LineColor(7))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("mass_combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Bmass.Draw()
            canv_Bmass.Print("Bmass_DsPi_Toys.pdf")
           
            canv_Btag = TCanvas("canv_Btag","canv_Btag")
            frame_Btag = mistagVar_B.frame()
            data[i].plotOn(frame_Btag,RooFit.Binning(100))
            frame_Btag.Draw()
            canv_Btag.Print("Btagomega_DsPi_Toys.pdf")
            
            gStyle.SetOptLogy(1)
            canv_Btime = TCanvas("canv_Btime","canv_Btime")
            frame_Btime = timeVar_B.frame()
            data[i].plotOn(frame_Btime,RooFit.Binning(100))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_dpi"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_bddspi"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_lcpi"),RooFit.LineStyle(1),RooFit.LineColor(3))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm1"),RooFit.LineStyle(1),RooFit.LineColor(6))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm2"),RooFit.LineStyle(1),RooFit.LineColor(7))
            #        total_pdf.plotOn(frame_Btime,RooFit.Components("time_combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Btime.Draw()
            canv_Btime.Print("Btime_DsPi_Toys.pdf")
            
            
            if not single :
                workout.writeToFile("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/DsPi_Toys_Full_Work_"+str(i)+".root")
                outfile  = TFile("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/DsPi_Toys_Full_Tree_"+str(i)+".root","RECREATE")
            else :
                workout.writeToFile("Data_Toys_Single_Work_DsPi.root")
                outfile  = TFile("Data_Toys_Single_Tree_DsPi.root","RECREATE")
            workout.Print('v')    
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
                   default = 75000)

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
                                        
