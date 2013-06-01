#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a mass fit on data for Bd -> D pi                    #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBdMassFitterOnData.py [-d | --debug]                         #
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
from ROOT import RooCruijff
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

# FIT CONFIGURATION
extendedFit =  True

# INITIAL PARAMETERS

PIDcut = 0
PIDchild = 0
PIDproton = 0
Pcut_down = 0.0
Pcut_up = 650000.0
Dmass_down = 1830
Dmass_up = 1910 #900
Bmass_down = 5000
Bmass_up = 5600
tagOmega = false

dataName      = '../data/config_B2DPi.txt'

# DATA FILES
# MISCELLANEOUS
bName = 'B'
dName = 'D'

#------------------------------------------------------------------------------
def fitB2DPi( debug, var,
              DK, DsPi, LcPi, BkgX, DRho, DstPi,
              MD, sweight, BDTG, configName, merge ) :

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
                                              
    
    dataTS = TString(dataName)
    mVarTS = TString("lab0_MassFitConsD_M")
    modeTS = TString("BDPi") 
    t = TString('_')

    BDTGTS = TString(BDTG)
    if  BDTGTS == "BDTGA":
        BDTG_down = 0.3
        BDTG_up = 1.0
    elif BDTGTS == "BDTGC":
        BDTG_down = 0.5
        BDTG_up= 1.0
    elif BDTGTS== "BDTG1":
        BDTG_down = 0.3
        BDTG_up= 0.7
    elif BDTGTS== "BDTG2":
        BDTG_down = 0.7
        BDTG_up= 0.9
    elif BDTGTS== "BDTG3":
        BDTG_down = 0.9
        BDTG_up= 1.0
                       
                        
    print "BDTG Range: (%f,%f)"%(BDTG_down,BDTG_up)
    
    
    workspace = MassFitUtils.ObtainBDPi(dataTS, TString("#BdPi"),
                                        PIDcut,
                                        Pcut_down, Pcut_up,
                                        BDTG_down, BDTG_up,
                                        Bmass_down, Bmass_up,
                                        Dmass_down, Dmass_up,
                                        mVarTS, TString("lab1_PIDK"),
                                        TString("BdDPi"),false, TString("DsPi")) #TString("BdDPi"))
    
    workspace.Print()
    
    #saveNameTS = TString("work_dpi_")+BDTGTS+TString(".root")
    #GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    #exit(0)
    
    workspace = MassFitUtils.ObtainSpecBack(dataTS, TString("#MC FileName MD"), TString("#MC TreeName"),
                                            PIDcut, PIDchild, PIDproton,
                                            Pcut_down,Pcut_up,
                                            BDTG_down,BDTG_up,
                                            Dmass_down, Dmass_up,
                                            Bmass_down, Bmass_up,
                                            mVarTS, TString("lab2_MM"), TString("lab1_PIDK"),
                                            TString("BdDPi"),
                                            workspace, false, tagOmega, debug)
    
    workspace = MassFitUtils.ObtainSpecBack(dataTS, TString("#MC FileName MU"), TString("#MC TreeName"),
                                            PIDcut, PIDchild, PIDproton,
                                            Pcut_down,Pcut_up,
                                            BDTG_down,BDTG_up,
                                            Dmass_down, Dmass_up,
                                            Bmass_down, Bmass_up,
                                            mVarTS, TString("lab2_MM"), TString("lab1_PIDK"),
                                            TString("BdDPi"),
                                            workspace, false, tagOmega, debug)
    
    
    workspace = MassFitUtils.CreatePdfSpecBackground(dataTS, TString("#MC FileName MD"),
                                                     dataTS, TString("#MC FileName MU"),
                                                     mVarTS, TString("lab2_MM"),
                                                     Bmass_down, Bmass_up,
                                                     Dmass_down, Dmass_up,
                                                     workspace, tagOmega, debug)
                
                                                     
                                                     
    workspace.Print()
    saveNameTS = TString("work_dpi_")+BDTGTS+TString("_5600.root")
    GeneralUtils.SaveWorkspace(workspace,saveNameTS, debug)
    #exit(0)
    
    
    loadNameTS = TString("work_dpi_")+BDTGTS+TString("_5600.root")
    workDK = GeneralUtils.LoadWorkspace(loadNameTS,TString("workspace"),debug)

    obsTS = TString(var)
    mass = GeneralUtils.GetObservable(workspace,obsTS)
    mom = GeneralUtils.GetObservable(workspace,TString("lab1_P"))
    momB = GeneralUtils.GetObservable(workspace,TString("lab0_P"))
    pt = GeneralUtils.GetObservable(workspace,TString("lab1_PT"))
    nTr = GeneralUtils.GetObservable(workspace,TString("nTracks"))
    if MD:
        massB = GeneralUtils.GetObservable(workspace,mVarTS)
        massD = GeneralUtils.GetObservable(workspace,TString("lab2_MM"))
        observables = RooArgSet( massB, massD, mom, momB, pt, nTr )
    else:    
        observables = RooArgSet( mass, mom, pt, nTr )
    #exit(0)
    
    data= []
    nEntries = []
    sample = [TString("up"),TString("down")]
    ran = 2.0
    
    for i in range(0,ran):
        datasetTS = TString("dataSetMCBdDPi")+TString("_")+sample[i]
        data.append(GeneralUtils.GetDataSet(workspace,datasetTS))
        nEntries.append(data[i].numEntries())
        print "Data set: %s with number of events: %s"%(data[i].GetName(),nEntries[i])

    if merge:
        data[0].append(data[1])
        nEntries[0] = nEntries[0]+nEntries[1]
        print "Data set: %s with number of events: %s"%(data[0].GetName(),nEntries[0])
        sample[0] = TString("both")
        sample[1] = TString("both")
        ran = 1
        
    meanD  = 1869
    meanB  = 5280
    index  = 0
    sigma1DName = modeTS + TString("_D_") + BDTGTS + TString ("_sigma1_bc")
    sigma2DName = modeTS + TString("_D_") + BDTGTS + TString ("_sigma2_bc")
    n1DName = modeTS + TString("_D_") + BDTGTS + TString ("_n1_bc")
    n2DName = modeTS + TString("_D_") + BDTGTS + TString ("_n2_bc")
    alpha1DName = modeTS + TString("_D_") + BDTGTS + TString ("_alpha1_bc")
    alpha2DName = modeTS + TString("_D_") + BDTGTS + TString ("_alpha2_bc")
    fracDName = modeTS + TString("_D_") + BDTGTS + TString ("_frac_bc")
    if debug:
        print sigma1DName
        print sigma2DName
        print n1DName
        print n2DName
        print alpha1DName
        print alpha2DName
        print fracDName

    sigma1BName = modeTS + TString("_B_") + BDTGTS + TString ("_sigma1_bc")
    sigma2BName = modeTS + TString("_B_") + BDTGTS + TString ("_sigma2_bc")
    n1BName = modeTS + TString("_B_") + BDTGTS + TString ("_n1_bc")
    n2BName = modeTS + TString("_B_") + BDTGTS + TString ("_n2_bc")
    alpha1BName = modeTS + TString("_B_") + BDTGTS + TString ("_alpha1_bc")
    alpha2BName = modeTS + TString("_B_") + BDTGTS + TString ("_alpha2_bc")
    fracBName = modeTS + TString("_B_") + BDTGTS + TString ("_frac_bc")
    if debug:
        print sigma1BName
        print sigma2BName
        print n1BName
        print n2BName
        print alpha1BName
        print alpha2BName
        print fracBName
                                                        
    cB1Name = modeTS + TString("_B_") + BDTGTS + TString ("_slope1")
    cB2Name = modeTS + TString("_B_") + BDTGTS + TString ("_slope2")
    fracCombBName = modeTS + TString("_B_") + BDTGTS + TString ("_fracComb")
    cDName = modeTS + TString("_D_") + BDTGTS + TString ("_slope")
    fracCombDName = modeTS + TString("_D_") + BDTGTS + TString ("_fracComb")
    if debug:
        print cB1Name
        print cB2Name
        print fracCombBName
        print cDName
        print fracCombDName
       
    sigma1DVar =  RooRealVar( "sigma1D", "sigma1D", myconfigfile[sigma1DName.Data()][index], 1.0, 30.0)
    sigma2DVar =  RooRealVar( "sigma2D", "sigma2D", myconfigfile[sigma2DName.Data()][index], 1.0, 30.0)
    n1DVar     =  RooRealVar( "n1D", "n1D", myconfigfile[n1DName.Data()][index])
    n2DVar     =  RooRealVar( "n2D", "n2D", myconfigfile[n2DName.Data()][index])
    alpha1DVar =  RooRealVar( "alpha1D", "alhpa1D", myconfigfile[alpha1DName.Data()][index]) #, 0.0, 6.0)
    alpha2DVar =  RooRealVar( "alpha2D", "alpha2D", myconfigfile[alpha2DName.Data()][index]) #, -6.0, 0.0)
    fracDVar   =  RooRealVar( "fracD",   "fracD",    myconfigfile[fracDName.Data()][index])
    
    sigma1BVar =  RooRealVar( "sigma1B", "sigma1B", myconfigfile[sigma1BName.Data()][index], 1.0, 30.0)
    sigma2BVar =  RooRealVar( "sigma2B", "sigma2B", myconfigfile[sigma2BName.Data()][index], 1.0, 30.0)
    n1BVar     =  RooRealVar( "n1B", "n1B", myconfigfile[n1BName.Data()][index])
    n2BVar     =  RooRealVar( "n2B", "n2B", myconfigfile[n2BName.Data()][index])
    alpha1BVar =  RooRealVar( "alpha1B", "alhpa1B", myconfigfile[alpha1BName.Data()][index]) #, 1.0, 6.0)
    alpha2BVar =  RooRealVar( "alpha2B", "alpha2B", myconfigfile[alpha2BName.Data()][index]) #, -6.0, 1.0)
    fracBVar   =  RooRealVar( "fracB",   "fracB",    myconfigfile[fracBName.Data()][index])
    
    meanDVar   =  [RooRealVar( "meanD" ,  "mean",    meanD,    meanD-100, meanD+100, "MeV/c^{2}") ,
                  RooRealVar( "meanD_down" ,  "mean",    meanD,    meanD-100, meanD+100, "MeV/c^{2}")]
                                                                                                                                  
    meanBVar   =  [RooRealVar( "meanB" ,  "mean",    meanB,    meanB-100, meanB+100, "MeV/c^{2}") ,
                   RooRealVar( "meanB_down" ,  "mean",    meanB,    meanB-100, meanB+100, "MeV/c^{2}")]

    meanBkg = meanB+86.6
    sigmaBkg = 50.0
    meanBkgXVar  =  RooRealVar( "meanBkg" ,  "mean",    meanBkg,    meanBkg-100, meanBkg+100, "MeV/c^{2}")
    sigmaBkgXVar =  RooRealVar( "sigmaBkg", "sigma1",  sigmaBkg,  3.0, 80.0)

    nSigEvts = []
    nSig = []
    sigPDF = []
    sigDPDF = []
    sigProdPDF = []
    sigEPDF = []

    for i in range(0,ran):
        nSigEvts.append(0.9*nEntries[i])
        nameSig = TString("nSig_")+sample[i]+TString("_Evts")
        nSig.append(RooRealVar( nameSig.Data(), nameSig.Data(), nSigEvts[i], 0., nEntries[i] ))
        #sigEPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVar, sigma1Var, alpha1Var, n1Var, sigma2Var, alpha2Var, n2Var, fracVar, nSig[i], sample[i].Data(), bName, debug ))
        #sigEPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleGEPDF_sim(mass, meanVar, sigma1Var, sigma2Var,  fracVar, nSig[i], sample[i].Data(), bName, true, debug ))
        if MD:
            nameSigPDF = TString("pdfDsSignal_")+sample[i]
            #sigDPDF.append(RooCruijff(nameSigPDF.Data(), nameSigPDF.Data(),massD, meanDVar[i], sigma1DVar, sigma2DVar,alpha1DVar, alpha2DVar))

            #sigDPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleGEPDF_sim(massD, meanDVar[i], sigma1DVar, sigma2DVar,  fracDVar,
            #                                                          nSig[i], sample[i].Data(), bName, false, debug ))

            sigDPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massD, meanDVar[i],
                                                                       sigma1DVar, alpha1DVar, n1DVar,
                                                                       sigma2DVar, alpha2DVar, n2DVar,
                                                                       fracDVar, nSig[i], sample[i].Data(), dName, debug ))
                       
            sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massB, meanBVar[i],
                                                                      sigma1BVar, alpha1BVar, n1BVar,
                                                                      sigma2BVar, alpha2BVar, n2BVar,
                                                                      fracBVar, nSig[i], sample[i].Data(), bName, debug ))


            #sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleGEPDF_sim(mass, meanBVar[i], sigma1BVar, sigma2BVar,  fracBVar,
            #                                                         nSig[i], sample[i].Data(), bName, false, debug ))
                                                                      
            namePROD = TString("SigProdPDF")+t+sample[i]
            sigProdPDF.append(RooProdPdf(namePROD.Data(),namePROD.Data(),RooArgList(sigPDF[i],sigDPDF[i])))

            nameEPDF = TString("SigEPDF_")+sample[i]
            sigEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), sigProdPDF[i]  , nSig[i]  ))
            
        else:
            if obsTS == "lab2_MM":
                nameSigPDF = TString("pdfDsSignal_")+sample[i]
                #sigPDF.append(RooCruijff(nameSigPDF.Data(), nameSigPDF.Data(),mass, meanDVar[i], sigma1DVar, sigma2DVar,alpha1DVar, alpha2DVar))
                sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleGEPDF_sim(mass, meanDVar[i], sigma1DVar, sigma2DVar,  fracDVar,
                                                                          nSig[i], sample[i].Data(), bName, false, debug ))
            else:
                
                sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanBVar[i], sigma1BVar, alpha1BVar, n1BVar,
                                                                          sigma2BVar, alpha2BVar, n2BVar, fracBVar, nSig[i], sample[i].Data(), bName, debug ))
            nameEPDF = TString("SigEPDF_")+sample[i]
            sigEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), sigPDF[i]  , nSig[i]  ))
                            
            

    type = 0
    sam = RooCategory("sample","sample")

    if merge:
        sam.defineType(sample[0].Data())
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sample[0].Data(),data[0]))
               
    else:
        sam.defineType(sample[0].Data())
        sam.defineType(sample[1].Data())
        
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sample[0].Data(),data[0]),
                              RooFit.Import(sample[1].Data(),data[1]))


    ny = TString("combData")    
    GeneralUtils.SaveDataSet(combData, mass, sample[0], ny, true)    
    totPDFsim = RooSimultaneous("simPdf","simultaneous pdf",sam)
    bkgPDF1 = []
    bkgPDF2 = []
    bkgPDF = []
    c2 = []
    cb1 = []
    cb2 = []
    cB = []
    cB2 = []
    cD = []
    fracbkg = []
    fracbkg2 = []
    
    totEPDF = []
    nBkgEvts = []
    nBkg = []
    bkgEPDF = []
    nBd2DK = []
    bkgBDK = []
    bkgBDKEPDF = []
    
    bkgBPDF = []
    bkgBPDF1 = []
    bkgBPDF2 = []
    bkgDPDF = []
    bkgDPDF1 = []
    
    bkgProdPDF = []

    bkgBBDK = []
    bkgDBDK = []
   

    nBs2DsPi = []
    bkgBsDsPi = []
    bkgBsDsPiEPDF = []
    bkgBBsDsPi = []
    bkgDBsDsPi = []

    nLb2LcPi = []
    bkgLbLcPi = []
    bkgLbLcPiEPDF = []
    bkgBLbLcPi = []
    bkgDLbLcPi = []

    nBkgX = []
    bkgBkgX = []
    bkgBkgXEPDF = []
    bkgBBkgX = []
    bkgDBkgX = []

    nBd2DstPi = []
    bkgBdDstPi = []
    bkgBdDstPiEPDF = []
    bkgBBdDstPi = []
    bkgDBdDstPi = []

    nBd2DRho = []
    bkgBdDRho = []
    bkgBdDRhoEPDF = []
    bkgBBdDRho = []
    bkgDBdDRho = []
                    
       
    predSignalName = TString("pred_Signal_")+BDTGTS
    predBDKName = TString("pred_BDK_")+BDTGTS
    
    for i in range(0,ran):
        if MD:
            cB.append(RooRealVar("cB","coefficient #2", 5*myconfigfile[cB1Name.Data()][index], -0.1, 0.0)) 
            bkgBPDF.append(RooExponential("expB", "expB" , massB, cB[i]))

            cB2.append(RooRealVar("cB2","coefficient #2", myconfigfile[cB2Name.Data()][index], -0.01, 0.0))
            bkgBPDF2.append(RooExponential("expB2", "expB2" , massB, cB2[i]))

            fracbkg2.append(RooRealVar("fracComb2","fracComb2", myconfigfile[fracCombBName.Data()][index], 0.0, 1.0))
            #bkgBPDF.append(RooAddPdf("bkgBAddPdf","bkgBAddPdf",bkgBPDF1[i], bkgBPDF2[i], fracbkg2[i]))                                    
            
            fracbkg.append(RooRealVar("fracComb","fracComb", myconfigfile[fracCombDName.Data()][index])) 
            cD.append(RooRealVar("cD","coefficient #2", myconfigfile[cDName.Data()][index])) #, -0.01, 0.0))  
            bkgDPDF1.append(RooExponential("expD", "expB" , massD, cD[i]))
            
            bkgDPDF.append(RooAddPdf("bkgDAddPdf","bkgAddPdf",bkgDPDF1[i], sigDPDF[i], fracbkg[i]))

            namePROD = TString("bkgProdPDF")+t+sample[i]
            bkgPDF1.append(RooProdPdf(namePROD.Data(),namePROD.Data(),RooArgList(bkgBPDF[i],bkgDPDF[i])))
                        
        else:    
            c2.append(RooRealVar("c2","coefficient #2", -0.008 ,-0.5, -0.000007)) 
            #if ( obsTS == "lab2_MM"):
            bkgPDF1.append(RooExponential("exp", "exp" , mass, c2[i]))
            #else:
            #    bkgPDF1.append(RooExponential("exp", "exp" , mass, c2[i]))
                
        nBkgEvts.append(0.4*nEntries[i])
        nameBkg = TString("nBkg_")+sample[i]+TString("_Evts")
        
        nBkg.append(RooRealVar( nameBkg.Data(), nameBkg.Data(), nBkgEvts[i], 0., nEntries[i] ))
        nameEPDF = TString("BkgEPDF_")+sample[i]
        bkgEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgPDF1[i]  , nBkg[i]  ))  
        
        nameBd2DK = TString("nBd2DK_")+sample[i]+TString("_Evts")
        nameBs2DsPi = TString("nBs2DsPi_")+sample[i]+TString("_Evts")
        nameLb2LcPi = TString("nLb2LcPi_")+sample[i]+TString("_Evts")
        nameBkgX = TString("nBkgX_")+sample[i]+TString("_Evts")
        nameBd2DstPi = TString("nBd2DstPi_")+sample[i]+TString("_Evts")
        nameBd2DRho = TString("nBd2DRho_")+sample[i]+TString("_Evts")

        if merge:
            predSignal = myconfigfile[predSignalName.Data()][i]+myconfigfile[predSignalName.Data()][i+1]
        else:
            predSignal = myconfigfile[predSignalName.Data()][i]
            
        if (DK == true):
            nBd2DK.append(RooRealVar(nameBd2DK.Data() , nameBd2DK.Data(), myconfigfile[predBDKName.Data()]))
                                     #predSignal*0.0735*0.64/2,
                                     #0.0, #predSignal*0.735*0.64*0.05,
                                     #predSignal*0.735*0.64*2))
        else:
            nBd2DK.append(RooRealVar(nameBd2DK.Data() , nameBd2DK.Data(),0))
        
        if (DsPi == true):
            nBs2DsPi.append(RooRealVar(nameBs2DsPi.Data() , nameBs2DsPi.Data(), 50, 0, 5000 ))
        else:
            nBs2DsPi.append(RooRealVar(nameBs2DsPi.Data() , nameBs2DsPi.Data(),0))
            
        if (LcPi == true):
            nLb2LcPi.append(RooRealVar(nameLb2LcPi.Data() , nameLb2LcPi.Data(), 200, 0, 1500 ))
        else:
            nLb2LcPi.append(RooRealVar(nameLb2LcPi.Data() , nameLb2LcPi.Data(),0))

        if ( BkgX == true):
            nBkgX.append(RooRealVar(nameBkgX.Data() , nameBkgX.Data(), 500, 0, 1000 ))
        else:
            nBkgX.append(RooRealVar(nameBkgX.Data() , nameBkgX.Data(),0))
                                        
        if ( DRho == true):
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(), nEntries[i]/6, 0, nEntries[i]))
        else:
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(),0))
            
        if ( DRho == true):
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(), nEntries[i]/4, 0, nEntries[i]))
        else:
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(),0))
            
                    
        if MD:
            bkgDBDK.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBd2DKPdf_m_both_Ds"), true))
            bkgBBDK.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBd2DKPdf_m_both"), true))
            namePROD = TString("bkgProdBDKPDF")+t+sample[i]
            bkgBDK.append(RooProdPdf(namePROD.Data(),namePROD.Data(),RooArgList(bkgBBDK[i],sigDPDF[i])))

            bkgDBdDstPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBd2DstPiPdf_m_both_Ds"), true))
            bkgBBdDstPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBd2DstPiPdf_m_both"), true))
            namePROD = TString("bkgProdBdDstPiPDF")+t+sample[i]
            bkgBdDstPi.append(RooProdPdf(namePROD.Data(),namePROD.Data(),RooArgList(bkgBBdDstPi[i],sigDPDF[i])))
            
            bkgDBdDRho.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBd2DRhoPdf_m_both_Ds"), true))
            bkgBBdDRho.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBd2DRhoPdf_m_both"), true))
            namePROD = TString("bkgProdBdRhoPDF")+t+sample[i]
            bkgBdDRho.append(RooProdPdf(namePROD.Data(),namePROD.Data(),RooArgList(bkgBBdDRho[i],sigDPDF[i])))
            
            bkgDBsDsPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBs2DsPiPdf_m_both_Ds"), true))
            bkgBBsDsPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBs2DsPiPdf_m_both"), true))
            namePROD = TString("bkgProdBsDsPiPDF")+t+sample[i]
            bkgBsDsPi.append(RooProdPdf(namePROD.Data(),namePROD.Data(),RooArgList(bkgBBsDsPi[i],bkgDBsDsPi[i])))
                                    
            bkgDLbLcPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgLb2LcPiPdf_m_both_Ds"), true))
            bkgBLbLcPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgLb2LcPiPdf_m_both"), true))
            namePROD = TString("bkgProdLbLcPiPDF")+t+sample[i]
            bkgLbLcPi.append(RooProdPdf(namePROD.Data(),namePROD.Data(),RooArgList(bkgBLbLcPi[i],bkgDLbLcPi[i])))

            #shift = 5369.600-5279.400
            #meanBsDPi =  RooFormulaVar("BsDPi_mean" , "BsDPi_mean",'@0+86.6', RooArgList(meanBVar))
                
            #bkgBBkgX.append(RooGaussian("gaussX","gaussX",massB,meanBkgXVar,sigmaBkgXVar))
            #namePROD = TString("bkgProdBkgXPDF")+t+sample[i]
            #bkgBkgX.append(RooProdPdf(namePROD.Data(),namePROD.Data(),RooArgList(bkgBBkgX[i],sigDPDF[i])))
                        
        else:
            if ( obsTS == "lab2_MM"):
                bkgBDK.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBd2DKPdf_m_both_Ds"), true))
                bkgBsDsPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBs2DsPiPdf_m_both_Ds"), true))
                bkgLbLcPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgLb2LcPiPdf_m_both_Ds"), true))
                 
            else:
                bkgBDK.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBd2DKPdf_m_both"), true))
                bkgBsDsPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgBs2DsPiPdf_m_both"), true))
                bkgLbLcPi.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workDK, TString("PhysBkgLb2LcPiPdf_m_both"), true))
                
        nameEPDF = TString("BkgBDKEPDF_")+sample[i]
        bkgBDKEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgBDK[i]  , nBd2DK[i]  ))

        nameEPDF = TString("BkgBsDsPiEPDF_")+sample[i]
        bkgBsDsPiEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgBsDsPi[i]  , nBs2DsPi[i]  ))

        nameEPDF = TString("BkgLbLcPiEPDF_")+sample[i]
        bkgLbLcPiEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgLbLcPi[i]  , nLb2LcPi[i]  ))
                
        #nameEPDF = TString("BkgBkgXEPDF_")+sample[i]
        #bkgBkgXEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgBkgX[i]  , nBkgX[i]  ))

        nameEPDF = TString("BkgBdDstPiEPDF_")+sample[i]
        bkgBdDstPiEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgBdDstPi[i]  , nBd2DstPi[i]  ))

        nameEPDF = TString("BkgBdDRhoEPDF_")+sample[i]
        bkgBdDRhoEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), bkgBdDRho[i]  , nBd2DRho[i]  ))
                
                
        name = TString("TotEPDF_m_")+sample[i]
        totEPDF.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass',
                                  RooArgList( sigEPDF[i], bkgEPDF[i], bkgBDKEPDF[i],
                                              bkgBsDsPiEPDF[i],bkgLbLcPiEPDF[i],
                                              bkgBdDstPiEPDF[i], bkgBdDRhoEPDF[i]))) #,bkgBkgXEPDF[i] ) ))
                

    #totPDFsim.addPdf(totEPDF[type], sample[type].Data())
    if merge:
        totPDFsim.addPdf(totEPDF[0], sample[0].Data())
    else:
        totPDFsim.addPdf(totEPDF[0], sample[0].Data())
        totPDFsim.addPdf(totEPDF[1], sample[1].Data())
                          
    # Instantiate and run the fitter
    fitter = FitMeTool( debug )
      
    fitter.setObservables( observables )

    fitter.setModelPDF( totPDFsim )
    
    fitter.setData(combData) 
      
    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    if plot_init :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )
    
    fitter.fit()
    

    name = TString("./sWeights_BdDPi_")+sample[type]+TString(".root")
    #Now includes setting things constant
    if sweight:
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(RooFit.Eval)
        fitter.savesWeights(mVarTS.Data(), combData, name)
        RooMsgService.instance().reset()
        
    if plot_fitted :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )

    gROOT.SetStyle( 'Plain' )
    #gROOT.SetBatch( False )
    gStyle.SetOptLogy(1)

    result = fitter.getFitResult()
    result.Print()
    model = fitter.getModelPDF()

    del fitter

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
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )
parser.add_option( '-i', '--initial-vars',
                   dest = 'initvars',
                   action = 'store_true',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
                   )
parser.add_option( '--DK',
                   action = 'store_true',
                   dest = 'DK',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '--DsPi',
                   action = 'store_true',
                   dest = 'DsPi',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '--LcPi',
                   action = 'store_true',
                   dest = 'LcPi',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

parser.add_option( '--BkgX',
                   action = 'store_true',
                   dest = 'BkgX',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

parser.add_option( '--DRho',
                   action = 'store_true',
                   dest = 'DRho',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

parser.add_option( '--DstPi',
                   action = 'store_true',
                   dest = 'DstPi',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

parser.add_option( '--merge',
                   action = 'store_true',
                   dest = 'merge',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

parser.add_option( '--MD',
                   action = 'store_true',
                   dest = 'MD',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '--sweight',
                   action = 'store_true',
                   dest = 'sweight',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

parser.add_option( '--BDTG', 
                   dest = 'BDTG',
                   default = 'BDTGA',
                   help = 'Set BDTG range '
                   )

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'B2DPiConfigForNominalMassFit'
                   )


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    import sys
    sys.path.append("../data/")
        
    fitB2DPi( options.debug, options.var,
              options.DK, options.DsPi, options.LcPi, options.BkgX, options.DRho, options.DstPi,
              options.MD, options.sweight, options.BDTG,
              options.configName, options.merge)

# -----------------------------------------------------------------------------
