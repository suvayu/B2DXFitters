#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a mass fit on data for Bd -> D pi                    #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBsDsPiMassFitterOnData.py [-o all -m both -d]                #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Author: Agnieszka Dziurda                                                 #
#   Author: Vladimir Vava Gligorov                                            #
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
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MISCELLANEOUS
bName = 'Bs'
dName = 'Ds'

#------------------------------------------------------------------------------
def runBsDsKMassFitterOnData( debug, sample, mVar, mdVar, tVar, terrVar, tagVar, tagOmegaVar, idVar, mode, sweight, yieldBdDPi, 
                              fileNameAll, fileNameToys, workName,logoutputname,tagTool, configName, wider, merge ) :

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

    workNameTS = TString(workName)
    workspace = []
    workspace.append(GeneralUtils.LoadWorkspace(TString(fileNameAll),workNameTS,debug))
    #workspaceID = GeneralUtils.LoadWorkspace(TString(fileNameAllID),workNameTS,debug)
    
    obsTS = TString(mVar)
    
    configNameTS = TString(configName)
    if configNameTS.Contains("Toys") == false:
        toys = false
    else:
        toys = true
        workspaceToys = (GeneralUtils.LoadWorkspace(TString(fileNameToys),workNameTS, debug))
        workspaceToys.Print("v")
        
        
    if (not toys):
        tagvar      = GeneralUtils.GetObservable(workspace[0],TString(tagVar), debug)
        idvar       = GeneralUtils.GetObservable(workspace[0],TString(idVar), debug)
        mass        = GeneralUtils.GetObservable(workspace[0],obsTS, debug)
        massDs      = GeneralUtils.GetObservable(workspace[0],TString(mdVar), debug)
        PIDK        = GeneralUtils.GetObservable(workspace[0],TString("lab1_PIDK"), debug)
        tvar        = GeneralUtils.GetObservable(workspace[0],TString(tVar), debug)
        terrvar     = GeneralUtils.GetObservable(workspace[0],TString(terrVar), debug)
        tagomegavar = GeneralUtils.GetObservable(workspace[0],TString(tagOmegaVar), debug)
                            
    else:
        mass        = GeneralUtils.GetObservable(workspaceToys,obsTS, debug)
        massDs      = GeneralUtils.GetObservable(workspaceToys,TString(mdVar), debug)
        PIDK        = GeneralUtils.GetObservable(workspaceToys,TString("lab1_PIDK"), debug)
        tvar        = GeneralUtils.GetObservable(workspaceToys,TString(tVar), debug)
        terrvar     = GeneralUtils.GetObservable(workspaceToys,TString(terrVar), debug)
        tagomegavar = GeneralUtils.GetObservable(workspaceToys,TString(tagOmegaVar), debug)
        tagvar      = GeneralUtils.GetObservable(workspaceToys,TString(tagVar)+TString("_idx"), debug)
        idvar       = GeneralUtils.GetObservable(workspaceToys,TString(idVar)+TString("_idx"), debug)
        trueidvar   = GeneralUtils.GetObservable(workspaceToys,TString("lab0_TRUEID"), debug)
                                                                        
    if( tagTool == "yes"):
        tagsskaonvar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_SS_Kaon_PROB"), debug)
        tagosmuonvar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_OS_Muon_PROB"), debug)
        tagoselectronvar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_OS_Electron_PROB"), debug)
        tagoskaonvar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_OS_Kaon_PROB"), debug)
        tagvtxchargevar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_VtxCharge_PROB"), debug)
        pvar = GeneralUtils.GetObservable(workspace[0],TString("lab1_P"), debug)
        ptvar = GeneralUtils.GetObservable(workspace[0],TString("lab1_PT"), debug)
        
    if( tagTool == "no"):
        observables = RooArgSet( mass, massDs, PIDK, tvar, terrvar, tagvar,tagomegavar,idvar )
        if toys:
            observables.add(trueidvar)
    else:
        observables =  RooArgSet( mass,tagsskaonvar,tagosmuonvar,tagoselectronvar,tagoskaonvar,tagvtxchargevar, pvar, ptvar)
        
        
        
    

        
        
 ###------------------------------------------------------------------------------------------------------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------###
 ###------------------------------------------------------------------------------------------------------------------------------------###   

    modeTS = TString(mode)
    sampleTS = TString(sample)

    if(tagTool == "no"):
        datasetTS = TString("dataSetBsDsPi_")
    else:
        datasetTS = TString("dataSetTagToolBsDsPi_")
        
    sam = RooCategory("sample","sample")
    t = TString('_')

    sm = []
    data = []
    nEntries = []

    ### Obtain data set ###
    if toys:
        s = [sampleTS, sampleTS]
        m = [modeTS]
        sm.append(s[0]+t+m[0])
        data.append(GeneralUtils.GetDataSet(workspaceToys,datasetTS+TString("toys"),debug))
        nEntries.append(data[0].numEntries())
        sam.defineType(sm[0].Data())
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sm[0].Data(),data[0]))
        
    else:
        if sample == "both":
            if mode == "all":
                if debug:
                    print "[INFO] Sample both. Mode all."
                
                s = [TString('up'),TString('down')]
                m = [TString('nonres'),TString('phipi'),TString('kstk'),TString('kpipi'),TString('pipipi')]
                t = TString('_')
                
                for i in range(0,5):
                    for j in range(0,2):
                        sm.append(s[j]+t+m[i])
                        #sam.defineType(sm[i*2+j].Data())
                        data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[2*i+j], debug))
                        nEntries.append(data[i*2+j].numEntries())
                        
                if debug:
                    for i in range(0,5):
                        for j in range(0,2):
                            print "%s : %s : %f"%(sm[i*2+j],data[i*2+j].GetName(),nEntries[i*2+j])
                nEntries_up = nEntries[0]+nEntries[2]+nEntries[4]+nEntries[6]+nEntries[8]
                if debug:
                    print "nEntries_dw: %s + %s + %s + %s +%s= %s"%(nEntries[0],nEntries[2],nEntries[4],nEntries[6],nEntries[8],nEntries_up)
                    nEntries_dw = nEntries[1]+nEntries[3]+nEntries[5]+nEntries[7]+nEntries[9]
                if debug:
                    print "nEntries_up: %s + %s + %s +%s +%s= %s"%(nEntries[1],nEntries[3],nEntries[5],nEntries[7],nEntries[9],nEntries_dw)
                    print "nEntries: %s + %s = %s"%(nEntries_up, nEntries_dw,nEntries)


                if merge:
                    data[0].append(data[1])
                    data[2].append(data[3])
                    data[4].append(data[5])
                    data[6].append(data[7])
                    data[8].append(data[9])
                    nEntries[0] = nEntries[0]+nEntries[1]
                    nEntries[1] = nEntries[2]+nEntries[3]
                    nEntries[2] = nEntries[4]+nEntries[5]
                    nEntries[3] = nEntries[6]+nEntries[7]
                    nEntries[4] = nEntries[8]+nEntries[9]
                    s = [TString('both'),TString('both')]
                    for i in range(0,5):
                        sm[i] =s[0]+t+m[i]
                        sam.defineType(sm[i].Data())
                    
                    combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                          RooFit.Index(sam),
                                          RooFit.Import(sm[0].Data(),data[0]),
                                          RooFit.Import(sm[1].Data(),data[2]),
                                          RooFit.Import(sm[2].Data(),data[4]),
                                          RooFit.Import(sm[3].Data(),data[6]),
                                          RooFit.Import(sm[4].Data(),data[8]))
                else:
                    for i in range(0,5):
                        for j in range(0,2):
                            sam.defineType(sm[i*2+j].Data())
                            
                            combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                                  RooFit.Index(sam),
                                                  RooFit.Import(sm[0].Data(),data[0]),
                                                  RooFit.Import(sm[1].Data(),data[1]),
                                                  RooFit.Import(sm[2].Data(),data[2]),
                                                  RooFit.Import(sm[3].Data(),data[3]),
                                                  RooFit.Import(sm[4].Data(),data[4]),
                                                  RooFit.Import(sm[5].Data(),data[5]),
                                                  RooFit.Import(sm[6].Data(),data[6]),
                                                  RooFit.Import(sm[7].Data(),data[7]),
                                                  RooFit.Import(sm[8].Data(),data[8]),
                                                  RooFit.Import(sm[9].Data(),data[9])
                                                  )
                            
                
            elif mode == "3modes" or mode == "3modeskkpi" :
                if debug:
                    print "[INFO] Sample both. Mode all."
                    
                s = [TString('up'),TString('down')]
                if mode == "3modeskkpi":
                    m = [TString('nonres'),TString('phipi'),TString('kstk')]
                else:
                    m = [TString('kkpi'),TString('kpipi'),TString('pipipi')]
                    
                t = TString('_')
                
                for i in range(0,3):
                    for j in range(0,2):
                        sm.append(s[j]+t+m[i])
                        data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[i*2+j], debug))
                        nEntries.append(data[i*2+j].numEntries())           
                if debug:
                    for i in range(0,3):
                        for j in range(0,2):
                            print "%s : %s : %f"%(sm[i*2+j],data[i*2+j].GetName(),nEntries[i*2+j])
                            
                nEntries_up = nEntries[0]+nEntries[2]+nEntries[4]
                if debug:
                    print "nEntries_dw: %s + %s + %s = %s"%(nEntries[0],nEntries[2],nEntries[4], nEntries_up)
                    nEntries_dw = nEntries[1]+nEntries[3]+nEntries[5]
                if debug:
                    print "nEntries_up: %s + %s + %s = %s"%(nEntries[1],nEntries[3],nEntries[5],nEntries_dw)
                    print "nEntries: %s + %s = %s"%(nEntries_up, nEntries_dw,nEntries) 
                    
                if merge:
                    data[0].append(data[1])
                    data[2].append(data[3])
                    data[4].append(data[5])
                    nEntries[0] = nEntries[0]+nEntries[1]
                    nEntries[1] = nEntries[2]+nEntries[3]
                    nEntries[2] = nEntries[4]+nEntries[5]
                    s = [TString('both'),TString('both')]
                    for i in range(0,3):
                        sm[i] =s[0]+t+m[i]
                        sam.defineType(sm[i].Data())
                        
                    combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                          RooFit.Index(sam),
                                          RooFit.Import(sm[0].Data(),data[0]),
                                          RooFit.Import(sm[1].Data(),data[2]),
                                          RooFit.Import(sm[2].Data(),data[4]))
                else:
                    for i in range(0,3):
                        for j in range(0,2):
                            sam.defineType(sm[i*2+j].Data())
                            
                    combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                          RooFit.Index(sam),
                                          RooFit.Import(sm[0].Data(),data[0]),
                                          RooFit.Import(sm[1].Data(),data[1]),
                                          RooFit.Import(sm[2].Data(),data[2]),
                                          RooFit.Import(sm[3].Data(),data[3]),
                                          RooFit.Import(sm[4].Data(),data[4]),
                                          RooFit.Import(sm[5].Data(),data[5]))
                    
                    if debug:
                        print "CombData: %s number of entries %f"%(combData.GetName(),combData.numEntries())
                        
            elif mode == "kkpi" or mode == "kpipi" or mode == "pipipi":
                if debug:
                    print "Sample both. Mode %s."%(mode)
            
                s = [TString('up'),TString('down')]
                t = TString('_')
                
                for i in range(0,2):
                    sm.append(s[i]+t+modeTS)
                    print "%s"%(sm)
                    sam.defineType(sm[i].Data())
                    data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[i], debug))
                    nEntries.append(data[i].numEntries())
                    
                if debug:
                    print "nEntries: %s + %s = %s"%(nEntries[0], nEntries[1],nEntries[0]+nEntries[1])
                    combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                          RooFit.Index(sam),
                                          RooFit.Import(sm[0].Data(),data[0]),
                                          RooFit.Import(sm[1].Data(),data[1]))
            
                if debug:
                    print "CombData: %s number of entries %f"%(combData.GetName(),combData.numEntries())
            else:
                if debug:
                    print "[ERROR] Sample both. Wrong mode. Possibilities: all, kkpi, kpipi, pipipi" 
                    
        elif sample == "up" or sample == "down":
            
            if mode == "3modes":
                if debug:
                    print "Sample %s. Mode all"%(sample)
                    
                s = [sampleTS]
                m = [TString('kkpi'),TString('kpipi'),TString('pipipi')]
                t = TString('_')
                
                for i in range(0,3):
                    sm.append(sampleTS+t+m[i])
                    print "%s"%(sm)
                    sam.defineType(sm[i].Data())
                    data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[i], debug))
                    nEntries.append(data[i].numEntries())
                    
                if debug:
                    print "nEntries: %s + %s + %s= %s"%(nEntries[0], nEntries[1], nEntries[2], nEntries[0]+nEntries[1]+nEntries[2])
                    combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                          RooFit.Index(sam),
                                          RooFit.Import(sm[0].Data(),data[0]),
                                          RooFit.Import(sm[1].Data(),data[1]),
                                          RooFit.Import(sm[2].Data(),data[2])
                                          )
                                                                                                                        
                if debug:
                    print "CombData: %s number of entries %f"%(combData.GetName(),combData.numEntries())
            
            elif mode == "kkpi" or mode == "kpipi" or mode == "pipipi":
                s = [sampleTS]
                t = TString('_')
                sm.append(sampleTS+t+modeTS)
                sam.defineType(sm[0].Data())
                data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[0], debug))
                nEntries.append(data[0].numEntries())
                
                if debug:
                    print "nEntries: %s"%(nEntries[0])
                combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                      RooFit.Index(sam),
                                      RooFit.Import(sm[0].Data(),data[0])
                                      )
                
                if debug:
                    print "CombData: %s number of entries %f"%(combData.GetName(),combData.numEntries())
            
                
            else:
                if debug:
                    print "[ERROR] Sample %s. Wrong mode. Possibilities: all, kkpi, kpipi, pipipi"%(sample) 
                    
        else:    
            if debug:
                print "[ERROR] Wrong sample. Possibilities: both, up, down "
                exit(0)
                  

    # Create the background PDF in mass
    
    nSig = []
    sigPDF = []
    sigDsPDF = []
    nSigEvts = []

    if toys:
        ran = 1
        ranmode = 1
        ransample = 1
    else:
        if sample == "both":
            if mode == "all":
                ran = 10
                ranmode = 5
                ransample = 2
            elif mode == "3modes" or mode == "3modeskkpi":
                ran = 6
                ranmode = 3
                ransample = 2
            elif mode == "kkpi" or mode == "kpipi" or mode == "pipipi":
                ran = 2
                ransample = 2
                ranmode = 1
        elif sample == "up" or sample == "down":
            if mode == "all":
                ran = 3
                ranmode = 3
                ransample = 1
            elif mode == "kkpi" or mode == "kpipi" or mode == "pipipi":
                ran = 1
                ranmode = 1
                ransample = 1
                
    if merge:
        bound = ranmode
    else:
        bound = ran
                
    s1 = [] 
    s2 = []
    s1Ds = []
    s2Ds = []
    ratio1 = myconfigfile["ratio1"]
    ratio2 = myconfigfile["ratio2"]
                            
    r1 = RooRealVar( "ratio1", "ratio1", ratio1 )
    r2 = RooRealVar( "ratio2", "ratio2", ratio2 )
    mn = RooRealVar( "Signal_mean", "Signal_mean", myconfigfile["mean"][0],
                     myconfigfile["mean"][0]-50,    myconfigfile["mean"][0] +50, "MeV/c^{2}")    
    mnDs = RooRealVar( "Signal_mean_Ds", "Signal_mean_Ds", myconfigfile["meanDs"][0],
                       myconfigfile["meanDs"][0]-50,    myconfigfile["meanDs"][0] +50, "MeV/c^{2}")
    
    alpha1Var = []
    alpha2Var = []
    
    
    for i in range(0,bound):
        if wider:
            nSigEvts.append(0.35*nEntries[i])
        else:
            nSigEvts.append(0.6*nEntries[i])

        sig1 =  myconfigfile["sigma1_bc"][i]
        sig2 =  myconfigfile["sigma2_bc"][i]
        if sig1>sig2:
            sig1 = sig1*myconfigfile["sigma1Bsfrac"]
            sig2 = sig2*myconfigfile["sigma2Bsfrac"]
        else:
            sig1 = sig1*myconfigfile["sigma2Bsfrac"]
            sig2 = sig2*myconfigfile["sigma1Bsfrac"]
            
        name = TString("Signal_sigma1_")+sm[i]    
        s1.append(RooRealVar( name.Data(), name.Data(), sig1)) 
        name = TString("Signal_sigma2_")+sm[i]
        s2.append(RooRealVar( name.Data(), name.Data(), sig2)) 
                                          
        name = TString("nSig")+t+sm[i]+t+TString("Evts")
        nSig.append(RooRealVar( name.Data(), name.Data(), nSigEvts[i], 0., nEntries[i] ))

        al1 = myconfigfile["alpha1_bc"][i]*myconfigfile["alpha1Bsfrac"]
        al2 = myconfigfile["alpha2_bc"][i]*myconfigfile["alpha2Bsfrac"]
                    
        n1 =  myconfigfile["n1_bc"][i]
        n2 =  myconfigfile["n2_bc"][i]
        frac =  myconfigfile["frac_bc"][i]

        if debug:
            print al1
            print al2
            print n1
            print n2
            print frac
        
        sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_fix(mass,mn,
                                                                  s1[i], al1, n1,
                                                                  s2[i], al2, n2,
                                                                  frac,
                                                                  nSig[i],sm[i].Data(),bName,debug))


        sig1Ds = myconfigfile["sigma1Ds_bc"][i]
        sig2Ds = myconfigfile["sigma2Ds_bc"][i]
        if sig1Ds>sig2Ds:
            sig1Ds = sig1Ds*myconfigfile["sigma1Dsfrac"]
            sig2Ds = sig2Ds*myconfigfile["sigma2Dsfrac"]
        else:
            sig1Ds = sig1Ds*myconfigfile["sigma2Dsfrac"]
            sig2Ds = sig2Ds*myconfigfile["sigma1Dsfrac"]
                                                                
        name = TString("Signal_sigma1_Ds_")+sm[i]
        s1Ds.append(RooRealVar( name.Data(), name.Data(), sig1Ds))
        name = TString("Signal_sigma2_Ds_")+sm[i]
        s2Ds.append(RooRealVar( name.Data(), name.Data(), sig2Ds))
                                
        al1Ds  = myconfigfile["alpha1Ds_bc"][i]*myconfigfile["alpha1Dsfrac"]
        al2Ds  = myconfigfile["alpha2Ds_bc"][i]*myconfigfile["alpha2Dsfrac"]
        n1Ds   =  myconfigfile["n1Ds_bc"][i]
        n2Ds   =  myconfigfile["n2Ds_bc"][i]
        fracDs =  myconfigfile["fracDs_bc"][i]

        if debug:
            print al1Ds
            print al2Ds
            print n1Ds
            print n2Ds
            print fracDs
        
        sigDsPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_fix(massDs,mnDs,
                                                                    s1Ds[i], al1Ds, n1Ds,
                                                                    s2Ds[i], al2Ds, n2Ds,
                                                                    fracDs,
                                                                    nSig[i],sm[i].Data(),dName,debug))
        
                                                
    nSigdG = []
    sigProdPDF = []
    sigEPDF = []
    sigPIDKPDF = []
           
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
    j=0
    
    for i in range(0,bound):
        name2 = TString("SigProdPDF")+t+sm[i]
        name3 = TString("SigEPDF")+t+sm[i]
        name4 = TString("Bs2DsPi_")+sm[i]
        k = bound%2
        sigPIDKPDF.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace[0], name4, s[k], lumRatio, true, debug))
        sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDsPDF[i],sigPIDKPDF[i])))
        print sigProdPDF[i].GetName()
        sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigProdPDF[i], nSig[i]))
        print sigEPDF[i].GetName()
                    
                                                                                                                              
    #exit(0)            
    # Create the background PDF in mass
    
    nCombBkgEvts = []
    nPiRhoEvts = []
    nLamEvts = []
    nDsKEvts = []

    for i in range(0,bound):
        if wider:
            nCombBkgEvts.append(0.2*nEntries[i])         # combinatorial background events
            nPiRhoEvts.append(0.4*nEntries[i])           # Bs->DsstPi, Bs->DsRho,  
            nLamEvts.append(0.01*nEntries[i])            # Lb->LcPi
            nDsKEvts.append(0.01*nEntries[i]) 
        else:
            nCombBkgEvts.append(0.3*nEntries[i])         # combinatorial background events
            nPiRhoEvts.append(0.01*nEntries[i])          # Bs->DsstPi, Bs->DsRho,
            nLamEvts.append(0.02*nEntries[i])            # Lb->LcPi
            nDsKEvts.append(0.01*nEntries[i]) 
            
    evts = TString("Evts")
    nCombBkg = []
    nBs2DsDsstPiRho = []
    nBd2DPi = []
    nLb2LcPi = []
    nBs2DsK = []
    
    nBd2DsPi = []
    nBd2DsstPi = []

    nBd2DRho = []
    nBd2DstPi = []
    
    bkgBdDsPi = []

    width1 = []
    width2 = []
    #width1 = RooFormulaVar("BdDsX_sigma1" , "BdDsX_sigma1",'@0*@1', RooArgList(s1,r1))
    #width2 = RooFormulaVar("BdDsX_sigma2" , "BdDsX_sigma2",'@0*@1', RooArgList(s2,r2))
    shift = 5369.600-5279.400
    meanBdDsPi =  RooFormulaVar("BdDsX_mean" , "BdDsX_mean",'@0-86.6', RooArgList(mn))

    cBVar = []
    cB2Var = []
    cDVar = []
    fracDsComb = []
    fracBsComb = []
    #fracPIDKComb = []
    j = 0
    
    for i in range(0,bound):
        name = TString("BdDsX_sigma1_") + sm[i]
        width1.append(RooFormulaVar(name.Data(), name.Data(),'@0*@1', RooArgList(s1[i],r1)))
        name = TString("BdDsX_sigma2_") + sm[i]
        width2.append(RooFormulaVar(name.Data() , name.Data(),'@0*@1', RooArgList(s2[i],r2)))
            
        nameCombBkg = TString("nCombBkg_")+sm[i]+t+evts
        nameBs2DsDsstPiRho = TString("nBs2DsDsstPiRho_")+sm[i]+t+evts
        nameBd2DPi = TString("nBd2DPi_")+sm[i]+t+evts
        nameLb2LcPi = TString("nLb2LcPi_")+sm[i]+t+evts
        nameBd2DsPi = TString("nBd2DsPi_")+sm[i]+t+evts
        nameBd2DsstPi = TString("nBd2DsstPi_")+sm[i]+t+evts
        nameBd2DstPi = TString("nBd2DstPi_")+sm[i]+t+evts
        nameBd2DRho = TString("nBd2DRho_")+sm[i]+t+evts
        nameBs2DsK = TString("nBs2DsK_")+sm[i]+t+evts

        if merge:
            inBd2DPi    = myconfigfile["BdDPiEvents"][i]
            #inBd2DPiErr = myconfigfile["BdDPiEventsErr"][i]
            inLbLcPi    = myconfigfile["LbLcPiEvents"][i]
            #inLbLcPiErr = myconfigfile["LbLcPiEventsErr"][i]
            inBs2DsK    = myconfigfile["BsDsKEvents"][i]
            #inBs2DsKErr = myconfigfile["BsDsKEventsErr"][i]
            #inBd2DPi = myconfigfile["BdDPiEvents"][2*i]+myconfigfile["BdDPiEvents"][2*i+1]
            assumedSig = myconfigfile["assumedSig"][i*2]+ myconfigfile["assumedSig"][i*2+1] 
        else:
            inBd2DPi = myconfigfile["BdDPiEvents"][i]
            assumedSig = myconfigfile["assumedSig"][i]
        
        nCombBkg.append(RooRealVar( nameCombBkg.Data()  , nameCombBkg.Data() , nCombBkgEvts[i] , 0. , nEntries[i] ))

        if wider:
            nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(), nPiRhoEvts[i], 0. , nEntries[i] ))
        else:
            nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(), nPiRhoEvts[i], 0. , nEntries[i]/5 ))
        '''    
        if (sm[i].Contains("kstk") == true or sm[i].Contains("nonres") == true or sm[i].Contains("phipi") == true ) :
            if (yieldBdDPi == "yes"):                
                nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),
                                           inBd2DPi,
                                           inBd2DPi-inBd2DPi*0.20,
                                           inBd2DPi+inBd2DPi*0.20))
            elif( yieldBdDPi == "constr"):
                nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(), inBd2DPi ))
            else:
                nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),
                                           inBd2DPi/2,
                                           0,
                                           nEntries[i]))
        elif ( sm[i].Contains("kpipi") == true ):
            nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),
                                       inBd2DPi)) #,
                                       #0.0,
                                       #nEntries[i]))
                 
        else:    
            nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),  0. ))
        '''
        nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(), inBd2DPi)) #, inBd2DPi*0.25, inBd2DPi*1.75))
        #nBd2DPi[i].setError(inBd2DPiErr)
        nBs2DsK.append(RooRealVar( nameBs2DsK.Data(), nameBs2DsK.Data(), inBs2DsK)) #, inBs2DsK*0.25, inBs2DsK*1.75))    
        #nBs2DsK[i].setError(inBs2DsKErr)
        
        #if (sm[i].Contains("kkpi") == true
        #    or sm[i].Contains("nonres") == true
        #    or sm[i].Contains("phipi") == true
        #    or sm[i].Contains("kstk") == true
        #    or sm[i].Contains("kpipi") == true
        #    ) :
        #    nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), nLamEvts[i], 0. , nEntries[i]/3 ))
        #else:
        #    nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), 0 ))

        nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), inLbLcPi)) #, 0.25*inLbLcPi, 1.75*inLbLcPi ))    
        #nLb2LcPi[i].setError(inLbLcPiErr)
        
        if wider:
            nBd2DsPi.append(RooRealVar(nameBd2DsPi.Data() , nameBd2DsPi.Data(),assumedSig*myconfigfile["nBd2DsPi"],
                            0, assumedSig*myconfigfile["nBd2DsPi"]*2))

        else:
            nBd2DsPi.append(RooRealVar(nameBd2DsPi.Data() , nameBd2DsPi.Data(),nPiRhoEvts[i], 0. , nEntries[i]/10))
                                       #assumedSig*myconfigfile["nBd2DsPi"]/2,
                                       #0,assumedSig*myconfigfile["nBd2DsPi"]))

        if wider:
            nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(),assumedSig*myconfigfile["nBd2DsstPi"]))
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(),inBd2DPi*myconfigfile["nBd2DstPi"]))
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(),inBd2DPi*myconfigfile["nBd2DRho"]))
        else:
            nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(), 0.0))
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(), 0.0))
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(), 0.0))

        al1 = myconfigfile["alpha1_bc"][i] #*myconfigfile["alpha1Bsfrac"]
        al2 = myconfigfile["alpha2_bc"][i] #*myconfigfile["alpha2Bsfrac"]
        n1 =  myconfigfile["n1_bc"][i]
        n2 =  myconfigfile["n2_bc"][i]
        frac =  myconfigfile["frac_bc"][i]
        
        bkgBdDsPi.append(Bs2Dsh2011TDAnaModels.buildBdDsX(mass,meanBdDsPi,
                                                          width1[i],al1,n1,
                                                          width2[i],al2,n2,
                                                          frac,
                                                          m[j],
                                                          TString("Bd2DsPi"), debug))        

        print j
        print m[j]
        mul = 15.0
        confTS = TString(configName)
        if (confTS.Contains("BDTG3")  == true): 
            mul = 30.0
        name = TString("CombBkg_slope_Bs1_")+m[j] 
        cBVar.append(RooRealVar(name.Data(), name.Data(), myconfigfile["cB1"][i],
                                myconfigfile["cB1"][i]+myconfigfile["cB1"][i]*mul, 0.0))
        name = TString("CombBkg_slope_Bs2_")+m[j]
        if confTS.Contains("BDTG3"):
            cB2Var.append(RooRealVar(name.Data(), name.Data(), myconfigfile["cB2"][i])) 
                                    # myconfigfile["cB2"][i]+myconfigfile["cB2"][i]*mul/100, 0.0))
            name = TString("CombBkg_fracBsComb_")+m[j]
            fracBsComb.append(RooRealVar(name.Data(), name.Data(), 1.0))
                    
        else:
            cB2Var.append(RooRealVar(name.Data(), name.Data(), myconfigfile["cB2"][i])) #/100,
                                     #myconfigfile["cB2"][i]+myconfigfile["cB2"][i]*mul/100, 0.0))
            name = TString("CombBkg_fracBsComb_")+m[j]
#            if (sm[i].Contains("kpipi") == true or sm[i].Contains("pipipi") == true):
#                fracBsComb.append(RooRealVar(name.Data(), name.Data(), myconfigfile["fracBsComb"][i])) #, 0.0, 1.0))
#            else:
            fracBsComb.append(RooRealVar(name.Data(), name.Data(), myconfigfile["fracBsComb"][i], 0.0, 1.0))
        print name    
        name = TString("CombBkg_slope_Ds_")+m[j]
        print name
        cDVar.append(RooRealVar(name.Data(), name.Data(), myconfigfile["cD"][i],
                                myconfigfile["cD"][i]+myconfigfile["cD"][i]*mul, 0.0))
        name = TString("CombBkg_fracDsComb_")+m[j]
        print name
        if ( sm[i].Contains("kpipi") == true or sm[i].Contains("pipipi") == true ):
            fracDsComb.append(RooRealVar(name.Data(), name.Data(), myconfigfile["fracComb"][i]))
        else:
            fracDsComb.append(RooRealVar(name.Data(), name.Data(), myconfigfile["fracComb"][i], 0.0, 1.0))
        #name = TString("CombBkg_fracPIDKComb") #+m[j]    
        #print name
        #fracPIDKComb.append(RooRealVar(name.Data(), name.Data(), 0.5, 0.0, 1.0))    
        if merge:
            j=j+1
        else:
            if i == 1 or i == 3:
                j=j+1
            
        #---------------------------------------------------------------------------------------------------------------------------#                

    #shared variable:
    # Group 1: Bs->DsstPi, Bs->DsRho
    if wider:
        g1_f1              = RooRealVar( "g1_f1_frac","g1_f1_frac", 0.893, 0, 1)
    else:
        g1_f1              = RooRealVar( "g1_f1_frac","g1_f1_frac", 0.5, 0.0, 1.0)
        
    g1_f2              = RooRealVar( "g1_f2_frac","g1_f2_frac", 0.093, 0.0, 1.0)

    name = TString("CombBkg_fracPIDKComb") 
    print name
    fracPIDKComb = RooRealVar(name.Data(), name.Data(), 0.5, 0.0, 1.0)
                    
    
    bkgPDF = []

    if (mode == "all" and ( sample == "up" or sample == "down")):
        for i in range(0,5):
            bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_MDFitter(mass,
                                                                           massDs,
                                                                           workspace[0],
                                                                           #workspaceID,
                                                                           nCombBkg[i],
                                                                           nBd2DPi[i],
                                                                           nBs2DsDsstPiRho[i],
                                                                           g1_f1,
                                                                           g1_f2,
                                                                           nLb2LcPi[i],
                                                                           nBd2DsPi[i],
                                                                           bkgBdDsPi[i],
                                                                           nBd2DsstPi[i],
                                                                           nBd2DRho[i],
                                                                           nBd2DstPi[i],
                                                                           nBs2DsK[i],
                                                                           sigDsPDF[i],
                                                                           cBVar[i],
                                                                           cB2Var[i],
                                                                           fracBsComb[i],
                                                                           cDVar[i],
                                                                           fracDsComb[i],
                                                                           fracPIDKComb,
                                                                           sm[i],
                                                                           lumRatio,
                                                                           debug ))
            
    else:
        if merge:
            for i in range(0,bound):
                bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_MDFitter(mass,
                                                                               massDs,
                                                                               workspace[0],
                                                                               #workspaceID,
                                                                               nCombBkg[i],
                                                                               nBd2DPi[i],
                                                                               nBs2DsDsstPiRho[i],
                                                                               g1_f1,
                                                                               g1_f2,
                                                                               nLb2LcPi[i],
                                                                               nBd2DsPi[i],
                                                                               bkgBdDsPi[i],
                                                                               nBd2DsstPi[i],
                                                                               nBd2DRho[i],
                                                                               nBd2DstPi[i],
                                                                               nBs2DsK[i],
                                                                               sigDsPDF[i],
                                                                               cBVar[i],
                                                                               cB2Var[i],
                                                                               fracBsComb[i],
                                                                               cDVar[i],
                                                                               fracDsComb[i],
                                                                               fracPIDKComb,
                                                                               sm[i],
                                                                               lumRatio,
                                                                               debug ))
                
        else:
            for i in range(0,ranmode):
                for j in range (0,ransample):
                    bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_MDFitter(mass,
                                                                                   massDs,
                                                                                   workspace[0],
                                                                                   #workspaceID,
                                                                                   nCombBkg[i*2+j],
                                                                                   nBd2DPi[i*2+j],
                                                                                   nBs2DsDsstPiRho[i*2+j],
                                                                                   g1_f1,
                                                                                   g1_f2,
                                                                                   nLb2LcPi[i*2+j],
                                                                                   nBd2DsPi[i*2+j],
                                                                                   bkgBdDsPi[i*2+j],
                                                                                   nBd2DsstPi[i*2+j],
                                                                                   nBd2DRho[i*2+j],
                                                                                   nBd2DstPi[i*2+j],
                                                                                   nBs2DsK[i*2+j],
                                                                                   sigDsPDF[i*2+j],
                                                                                   cBVar[i*2+j],
                                                                                   cB2Var[i*2+j],
                                                                                   fracBsComb[i*2+j],
                                                                                   cDVar[i*2+j],
                                                                                   fracDsComb[i*2+j],
                                                                                   fracPIDComb,
                                                                                   sm[i*2+j],
                                                                                   lumRatio,
                                                                                   debug ))
                    
                                          
       
        
        
    # Create total the model PDF in mass

    N_Bkg_Tot = []

    totPDFp = []
    totPDFa = []
    for i in range(0,bound):
        name = TString("TotEPDF_m_")+sm[i]
        print sigEPDF[i].GetName()
        print bkgPDF[i].GetName()
        totPDFp.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass', RooArgList( sigEPDF[i], bkgPDF[i] )))
        
    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    for i in range(0,bound):
        print totPDFp[i].GetName()
        print sm[i].Data()
        totPDF.addPdf(totPDFp[i], sm[i].Data())
    totPDF.Print("v")
        
    # Instantiate and run the fitter
    fitter = FitMeTool( debug )
      
    fitter.setObservables( observables )

    fitter.setModelPDF( totPDF )
    
    fitter.setData(combData) 
    
    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    if plot_init :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )
   
    #import sys
    #import random
    #sys.stdout = open(logoutputname, 'w')
    fitter.fit(True, RooFit.Extended(), RooFit.SumW2Error(True), RooFit.Verbose(False)) #, RooFit.InitialHesse(True))
    result = fitter.getFitResult()
    result.Print("v")

    if (not toys ):
        BDTGTS = GeneralUtils.CheckBDTGBin(confTS, debug)
        name = TString("./sWeights_BsDsPi_")+modeTS+TString("_")+sampleTS+TString("_")+BDTGTS+TString(".root")
    else:
        name = TString(options.sweightoutputname)
        
    #Now includes setting things constant
    if sweight:
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(RooFit.Eval)
        fitter.savesWeights(mVar, combData, name)
        RooMsgService.instance().reset()
        
    fitter.printYieldsInRange( '*Evts', obsTS.Data() , 5320, 5420 )    
    if plot_fitted :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )

    #print nSig[0].getVal(), nSig[0].getErrorLo(), nSig[0].getErrorHi()    

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
                   default = 'WS_Mass_DsPi.root', 
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )

parser.add_option( '--sweightoutputname',
                   dest = 'sweightoutputname',
                   default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsPi_Toys_Full_sWeights_ForTimeFit_0.root', 
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )   

parser.add_option( '--logoutputname',
                   dest = 'logoutputname',
                   default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsPi_Toys_Full_MassFitResult_0.log'
                   )   

parser.add_option( '-i', '--initial-vars',
                   dest = 'initvars',
                   action = 'store_true',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '-m', '--sample',
                   dest = 'sample',
                   metavar = 'SAMPLE',
                   default = 'down',
                   help = 'Sample: choose up or down '
                   )
parser.add_option( '-o', '--mode',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'kkpi',
                   help = 'Mode: choose all, kkpi, kpipi or pipipi'
                   )
parser.add_option( '--mvar',
                   dest = 'mvar',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '          
                   )
parser.add_option( '--mdvar',
                   dest = 'mdvar',
                   default = 'lab2_MM',
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
parser.add_option( '-w', '--sweight',
                   dest = 'sweight',
                   action = 'store_true',
                   default = False,
                   help = 'create and save sWeights'
                   )
parser.add_option( '-y', '--yield',
                   dest = 'yieldBdDPi',
                   default = 'constr',
                   help = 'implement expected yield for BdDPi'
                   )

#parser.add_option( '--fitsignal',
#                   dest = 'fitSig',
#                   default = 'no',
#                   help = 'fit signal, yes or no'
#                   )

parser.add_option( '--tagTool',
                   dest = 'tagTool',
                   default = "no",
                   help = 'generate sWeights with tagTool variables (for Matt)'
                   )
parser.add_option( '--fileName',
                   dest = 'fileNameAll',
                   default = '../data/workspace/work_dspi.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--fileNameToys',
                   dest = 'fileNameToys',
                   default = '../data/workspace/work_dsk.root',
                   help = 'name of the inputfile'
                   )
parser.add_option( '--workName',
                   dest = 'workName',
                   default = 'workspace',
                   help = 'name of the workspace'
                   )   
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsPiConfigForNominalMassFit')
parser.add_option( '--wider',
                   dest = 'wider',
                   action = 'store_true',
                   default = False,
                   help = 'create and save sWeights'
                   )
parser.add_option( '--merge',
                   dest = 'merge',
                   action = 'store_true',
                   default = False,
                   help = 'merge magnet polarity'
                   )


# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    import sys
    sys.path.append("../data/")
        
    runBsDsKMassFitterOnData( options.debug,  options.sample , options.mvar, options.mdvar,options.tvar, options.terrvar, \
                              options.tagvar, options.tagomegavar, options.idvar,\
                              options.mode, options.sweight, options.yieldBdDPi, 
                              options.fileNameAll, options.fileNameToys, options.workName,
                              options.logoutputname,options.tagTool, options.configName, options.wider, options.merge)

# -----------------------------------------------------------------------------
