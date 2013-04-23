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
bName = 'B_{s}'


#------------------------------------------------------------------------------
def runBsDsKMassFitterOnData( debug, sample, mVar, mdVar, tVar, tagVar, tagOmegaVar, idVar, mode, sweight, yieldBdDPi, fitSignal,
                              fileNameAll, fileNameAllID, workName,logoutputname,tagTool, configName, wider, merge ) :

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
    workspaceID = GeneralUtils.LoadWorkspace(TString(fileNameAllID),workNameTS,debug)
    
    obsTS = TString(mVar)
    mass        = GeneralUtils.GetObservable(workspace[0],obsTS, debug)
    massDs      = GeneralUtils.GetObservable(workspace[0],TString(mdVar), debug)
    PIDK        = GeneralUtils.GetObservable(workspace[0],TString("lab1_PIDK"), debug)
    tvar        = GeneralUtils.GetObservable(workspace[0],TString(tVar), debug)
    tagomegavar = GeneralUtils.GetObservable(workspace[0],TString(tagOmegaVar), debug)

    configNameTS = TString(configName)
    if configNameTS.Contains("Toys") == false:
        toys = false
    else:
        toys = true
        
    if (not toys):
        tagvar      = GeneralUtils.GetObservable(workspace[0],TString(tagVar), debug)
        idvar       = GeneralUtils.GetObservable(workspace[0],TString(idVar), debug)
    else:
        tagvar      = GeneralUtils.GetObservable(workspace[0],TString(tagVar)+TString("_idx"), debug)
        idvar       = GeneralUtils.GetObservable(workspace[0],TString(idVar)+TString("_idx"), debug)

    if( tagTool == "yes"):
        tagsskaonvar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_SS_Kaon_PROB"), debug)
        tagosmuonvar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_OS_Muon_PROB"), debug)
        tagoselectronvar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_OS_Electron_PROB"), debug)
        tagoskaonvar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_OS_Kaon_PROB"), debug)
        tagvtxchargevar = GeneralUtils.GetObservable(workspace[0],TString("lab0_BsTaggingTool_VtxCharge_PROB"), debug)
        pvar = GeneralUtils.GetObservable(workspace[0],TString("lab1_P"), debug)
        ptvar = GeneralUtils.GetObservable(workspace[0],TString("lab1_PT"), debug)
        
    if( tagTool == "no"):
        observables = RooArgSet( mass, massDs, PIDK, tvar,tagvar,tagomegavar,idvar )
    else:
        observables =  RooArgSet( mass,tagsskaonvar,tagosmuonvar,tagoselectronvar,tagoskaonvar,tagvtxchargevar, pvar, ptvar)
        
    sampleMC = [TString("up"),TString("down")]

    if (fitSignal == "yes"):
        
        dataMCBs= []
        nEntriesMCBs = []
        for i in range(0,2):
            datasetMCBsTS = TString("dataSetMCBsDsPi_")+sampleMC[i]
            dataMCBs.append(GeneralUtils.GetDataSet(workspace[0],datasetMCBsTS, debug))
            nEntriesMCBs.append(dataMCBs[i].numEntries())
            if debug:
                print "Data set: %s with number of events: %s"%(dataMCBs[i].GetName(),nEntriesMCBs[i])
        
        dataMCBd= []
        nEntriesMCBd = []
        for i in range(0,2):
            datasetMCBdTS = TString("dataSetMCBdDsPi_")+sampleMC[i]
            dataMCBd.append(GeneralUtils.GetDataSet(workspace[0],datasetMCBdTS,debug))
            nEntriesMCBd.append(dataMCBd[i].numEntries())
            if debug:
                print "Data set: %s with number of events: %s"%(dataMCBd[i].GetName(),nEntriesMCBd[i])
                                            

        meanVarBs   =  RooRealVar( "DblCBBsPDF_mean" ,  "mean",    5363.51,  5000.,  5600., "MeV/c^{2}")
        sigma1VarBs =  RooRealVar( "DblCBBsPDF_sigma1", "sigma1",  12.691,   5,      20, "MeV/c^{2}")
        sigma2VarBs =  RooRealVar( "DblCBBsPDF_sigma2", "sigma2",  20.486,   10,     30, "MeV/c^{2}")
        alpha1VarBs =  RooRealVar( "DblCBBsPDF_alpha1", "alpha1",  2.1260,   0,      4)
        alpha2VarBs =  RooRealVar( "DblCBBsPDF_alpha2", "alpha2",  -2.0649,  -4,     0)
        n1VarBs     =  RooRealVar( "DblCBBsPDF_n1",     "n1",      1.1019,   0.0001, 5)
        n2VarBs     =  RooRealVar( "DblCBBsPDF_n2",     "n2",      5.8097,   0.1,    12)
        fracVarBs   =  RooRealVar( "DblCBBsPDF_frac",   "frac",    0.78044,  0,      1);

        meanVarBd   =  RooRealVar( "DblCBBdPDF_mean" ,  "mean",    5367.51,  5000.,  5600., "MeV/c^{2}")
        sigma1VarBd =  RooRealVar( "DblCBBdPDF_sigma1", "sigma1",  15,       5,      25, "MeV/c^{2}")
        sigma2VarBd =  RooRealVar( "DblCBBdPDF_sigma2", "sigma2",  15,       10,     50, "MeV/c^{2}")
        alpha1VarBd =  RooRealVar( "DblCBBdPDF_alpha1", "alpha1",  2,        0,      4)
        alpha2VarBd =  RooRealVar( "DblCBBdPDF_alpha2", "alpha2",  -2,      -4,      0)
        n1VarBd     =  RooRealVar( "DblCBBdPDF_n1",     "n1",      1.5,      0.0001, 5)
        n2VarBd     =  RooRealVar( "DblCBBdPDF_n2",     "n2",      1.5,      0.1,    12)
        fracVarBd   =  RooRealVar( "DblCBBdPDF_frac",   "frac",    0.5,      0,      1);
    
        nSigEvtsMCBs = []
        nSigMCBs = []
        sigPDFMCBs = []
        for i in range(0,2):
            nSigEvtsMCBs.append(0.9*nEntriesMCBs[i])
            nameSigMCBs = TString("nSigEvtsBs_")+sampleMC[i]
            nSigMCBs.append(RooRealVar( nameSigMCBs.Data(), nameSigMCBs.Data(), nSigEvtsMCBs[i], 0., 100*nEntriesMCBs[i] ))
            sigPDFMCBs.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVarBs, sigma1VarBs, alpha1VarBs, n1VarBs, sigma2VarBs, alpha2VarBs, n2VarBs, fracVarBs, nSigMCBs[i], sampleMC[i].Data(), bName, debug ))
            
        nSigEvtsMCBd = []
        nSigMCBd = []
        sigPDFMCBd = []
        for i in range(0,2):
            nSigEvtsMCBd.append(0.9*nEntriesMCBd[i])
            nameSigMCBd = TString("nSigEvtsBd_")+sampleMC[i]
            nSigMCBd.append(RooRealVar( nameSigMCBd.Data(), nameSigMCBd.Data(), nSigEvtsMCBd[i], 0., 100*nEntriesMCBd[i] ))
            sigPDFMCBd.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVarBd, sigma1VarBd, alpha1VarBd, n1VarBd, sigma2VarBd, alpha2VarBd, n2VarBd, fracVarBd, nSigMCBd[i], sampleMC[i].Data(), bName, debug ))
                                            
        
        samMC = RooCategory("sample","sample")
        for i in range(0,2):
            samMC.defineType(sampleMC[i].Data())
            
        combDataMCBs = RooDataSet("combDataMC","combined data",RooArgSet(observables),
                                  RooFit.Index(samMC),
                                  RooFit.Import(sampleMC[0].Data(),dataMCBs[0]),
                                  RooFit.Import(sampleMC[1].Data(),dataMCBs[1]))

        totPDFMCBs = RooSimultaneous("simPdfMC","simultaneous pdfMC",samMC)
        for i in range(0,2):
            totPDFMCBs.addPdf(sigPDFMCBs[i], sampleMC[i].Data())
         
        fitterMCBs = FitMeTool( debug )
        fitterMCBs.setObservables( observables )
        fitterMCBs.setModelPDF( totPDFMCBs )
        fitterMCBs.setData(combDataMCBs)
        fitterMCBs.fit()

        resultMCBs = fitterMCBs.getFitResult()
        resultMCBs.Print()
        modelBs = fitterMCBs.getModelPDF()
        
                            
        paramsBs = modelBs.getVariables() ;
        paramsBs.Print("v");
        
        mean = paramsBs.getRealValue("DblCBBsPDF_mean")
        sigma1  = paramsBs.getRealValue("DblCBBsPDF_sigma1")  
        sigma2 = paramsBs.getRealValue("DblCBBsPDF_sigma2") 
        alpha1 = paramsBs.getRealValue("DblCBBsPDF_alpha1")
        alpha2 = paramsBs.getRealValue("DblCBBsPDF_alpha2")
        n1 = paramsBs.getRealValue("DblCBBsPDF_n1")
        n2 = paramsBs.getRealValue("DblCBBsPDF_n2")
        frac = paramsBs.getRealValue("DblCBBsPDF_frac")
        

        combDataMCBd = RooDataSet("combDataMC","combined data",RooArgSet(observables),
                                  RooFit.Index(samMC),
                                  RooFit.Import(sampleMC[0].Data(),dataMCBs[0]),
                                  RooFit.Import(sampleMC[1].Data(),dataMCBs[1]))
        
        totPDFMCBd = RooSimultaneous("simPdfMC","simultaneous pdfMC",samMC)
        for i in range(0,2):
            totPDFMCBd.addPdf(sigPDFMCBd[i], sampleMC[i].Data())

        fitterMCBd = FitMeTool( debug )
        fitterMCBd.setObservables( observables )
        fitterMCBd.setModelPDF( totPDFMCBd )
        fitterMCBd.setData(combDataMCBd)
        fitterMCBd.fit()

        resultMCBd = fitterMCBd.getFitResult()
        if debug:
            resultMCBd.Print()
        modelBd = fitterMCBd.getModelPDF()

        paramsBd = modelBd.getVariables() ;
        if debug:
            paramsBd.Print("v");
        
        sigma1Bd = paramsBd.getRealValue("DblCBBdPDF_sigma1")
        sigma2Bd = paramsBd.getRealValue("DblCBBdPDF_sigma2")
        
        ratio1 = sigma1Bd/sigma1
        ratio2 = sigma2Bd/sigma2
        
        print "Ratio1: %s / %s = %s Ratio2 %s / %s = %s"%(sigma1,sigma1Bd,ratio1,sigma2,sigma2Bd,ratio2)  

    else:

        mean   = myconfigfile["mean"]
        sigma1 = myconfigfile["sigma1"]
        sigma2 = myconfigfile["sigma2"]
        alpha1 = myconfigfile["alpha1"]
        alpha2 = myconfigfile["alpha2"]
        n1     = myconfigfile["n1"]
        n2     = myconfigfile["n2"]
        frac   = myconfigfile["frac"]
        ratio1 = myconfigfile["ratio1"]
        ratio2 = myconfigfile["ratio2"]

        
        
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

    sm = []
    data = []
    nEntries = []

    ### Obtain data set ###
    
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
    nSigEvts = []
    
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
                
    s1 = RooRealVar( "Signal_sigma1", "Signal_sigma1", sigma1) #, 5., 50 )
    s2 = RooRealVar( "Signal_sigma2", "Signal_sigma2", sigma2) #, 5., 50 )
    r1 = RooRealVar( "ratio1", "ratio1", ratio1 )
    r2 = RooRealVar( "ratio2", "ratio2", ratio2 )
    mn = RooRealVar( "Signal_mean", "Signal_mean", mean, 5100, 5600, "MeV/c^{2}")    
                                        
    sigma1Var = []
    sigma2Var = []
    alpha1Var = []
    alpha2Var = []
    
    
    for i in range(0,bound):
        if wider:
            nSigEvts.append(0.35*nEntries[i])
        else:
            nSigEvts.append(0.85*nEntries[i])
            
        name = TString("nSig")+t+sm[i]+t+TString("Evts")
        nSig.append(RooRealVar( name.Data(), name.Data(), nSigEvts[i], 0., nEntries[i] ))
        sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_fix(mass,mn,s1,alpha1,n1,s2,alpha2,n2,frac,nSig[i],sm[i].Data(),bName,debug))
        
    meanVarDs = []
    sigma1VarDs = []
    sigma2VarDs = []
    alpha1VarDs = []
    alpha2VarDs = []
    fracVarDs = []
    j=0

    for i in range(0,bound):
        name = TString("DCruijff_mean_")+m[j]
        print name
        meanVarDs.append(RooRealVar( name.Data() ,  name.Data(),    myconfigfile["meanDs"][i],
                                     myconfigfile["meanDs"][i]-100,    myconfigfile["meanDs"][i] +100 ))
        name = TString("DCruijff_sigma1_")+m[j]
        print name
        sigma1VarDs.append(RooRealVar( name.Data(), name.Data(),  myconfigfile["sigma1Ds"][i])) #25, 15, 35))
        name = TString("DCruijff_sigma2_")+m[j]
        print name
        sigma2VarDs.append(RooRealVar( name.Data(), name.Data(),  myconfigfile["sigma2Ds"][i])) #3, 0 , 20  ))
        
        name = TString("DCruijff_alpha1_")+m[j]
        print name
        alpha1VarDs.append(RooRealVar( name.Data(), name.Data(),  myconfigfile["alpha1Ds"][i])) #25, 15, 35))
        name = TString("DCruijff_alpha2_")+m[j]
        print name
        alpha2VarDs.append(RooRealVar( name.Data(), name.Data(),  myconfigfile["alpha2Ds"][i])) #3, 0 , 20  ))
        name = TString("DCruijff_frac_")+m[j]
        print name
        fracVarDs.append(RooRealVar( name.Data(),  name.Data(),    myconfigfile["fracDs"][i], 0.0, 1.0))
        if merge:
            j=j+1
        else:
            if i == 1 or i == 3:
                j=j+1
                                                
    nSigdG = []
    sigDsPDF = []
    sigProdPDF = []
    sigEPDF = []
    sigPIDKPDF = []
    sigPIDKPDF1 = []
    sigPIDKPDF2 = []
        
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
    
    for i in range(0,bound):
        name = TString("DCruijffPDF_")+sm[i]
        name2 = TString("SigProdPDF")+t+sm[i]
        name3 = TString("SigEPDF")+t+sm[i]
        if merge:
            sigPIDKPDF1.append(Bs2Dsh2011TDAnaModels.GetRooAddPdfFromWorkspace(workspaceID,TString("ShapePIDK_BsDsPi_down"),debug))
            sigPIDKPDF2.append(Bs2Dsh2011TDAnaModels.GetRooAddPdfFromWorkspace(workspaceID,TString("ShapePIDK_BsDsPi_up"),debug))
            name4 = TString("ShapePIDK_BsDsPi_both")
            sigPIDKPDF.append(RooAddPdf( name4.Data(), name4.Data(), RooArgList( sigPIDKPDF2[i], sigPIDKPDF1[i]),RooArgList(lumRatio)))
            print "Create %s"%(sigPIDKPDF[0].GetName())
        else:
            if(sm[i].Contains("down")):
                sigPIDKPDF.append(Bs2Dsh2011TDAnaModels.GetRooAddPdfFromWorkspace(workspaceID,TString("ShapePIDK_BsDsPi_down"),debug))
            else:
                sigPIDKPDF.append(Bs2Dsh2011TDAnaModels.GetRooAddPdfFromWorkspace(workspaceID,TString("ShapePIDK_BsDsPi_up"),debug))
        sigDsPDF.append(RooCruijff(name.Data(), name.Data(),massDs, meanVarDs[i], sigma1VarDs[i], sigma2VarDs[i],alpha1VarDs[i], alpha2VarDs[i]))
        print sigDsPDF[i].GetName()
        sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDsPDF[i],sigPIDKPDF[i])))
        print sigProdPDF[i].GetName()
        sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigProdPDF[i], nSig[i]))
        print sigEPDF[i].GetName()
                                                                                                                              
                
    # Create the background PDF in mass
    
    nCombBkgEvts = []
    nPiRhoEvts = []
    nLamEvts = []
    nDsKEvts = []

    for i in range(0,bound):
        if wider:
            nCombBkgEvts.append(0.2*nEntries[i])           # combinatorial background events
            nPiRhoEvts.append(0.4*nEntries[i])             # Bs->DsstPi, Bs->DsRho,  
            nLamEvts.append(0.2*nEntries[i])               # Lb->LcPi
            nDsKEvts.append(0.01*nEntries[i]) 
        else:
            nCombBkgEvts.append(0.2*nEntries[i])           # combinatorial background events
            nPiRhoEvts.append(0.01*nEntries[i])             # Bs->DsstPi, Bs->DsRho,
            nLamEvts.append(0.2*nEntries[i])               # Lb->LcPi
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
    
    width1 = RooFormulaVar("BdDsX_sigma1" , "BdDsX_sigma1",'@0*@1', RooArgList(s1,r1))
    width2 = RooFormulaVar("BdDsX_sigma2" , "BdDsX_sigma2",'@0*@1', RooArgList(s2,r2))
    shift = 5369.600-5279.400
    meanBdDsPi =  RooFormulaVar("BdDsX_mean" , "BdDsX_mean",'@0-86.6', RooArgList(mn))
    
    for i in range(0,bound):
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
            inBd2DPi = myconfigfile["BdDPiEvents"][2*i]+myconfigfile["BdDPiEvents"][2*i+1]
            assumedSig = myconfigfile["assumedSig"][i*2]+ myconfigfile["assumedSig"][i*2+1] 
        else:
            inBd2DPi = myconfigfile["BdDPiEvents"][i]
            assumedSig = myconfigfile["assumedSig"][i]
        
        nCombBkg.append(RooRealVar( nameCombBkg.Data()  , nameCombBkg.Data() , nCombBkgEvts[i] , 0. , nEntries[i] ))

        if wider:
            nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(), nPiRhoEvts[i], 0. , nEntries[i] ))
        else:
            nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(), nPiRhoEvts[i], 0. , nEntries[i]/10 ))
            
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
                                           inBd2DPi,
                                           0,
                                           nEntries[i]))
        elif ( sm[i].Contains("kpipi") == true ):
            nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),
                                       inBd2DPi,
                                       0.0,
                                       nEntries[i]))
                 
        else:    
            nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),  0. ))

        nBs2DsK.append(RooRealVar( nameBs2DsK.Data(), nameBs2DsK.Data(), nDsKEvts[i], 0. , nEntries[i]/10 ))    
            
        if (sm[i].Contains("kkpi") == true
            or sm[i].Contains("nonres") == true
            or sm[i].Contains("phipi") == true
            or sm[i].Contains("kstk") == true
            or sm[i].Contains("kpipi") == true
            ) :
            nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), nLamEvts[i], 0. , nEntries[i]/3 ))
        else:
            nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), 0 ))
            
        if wider:
            nBd2DsPi.append(RooRealVar(nameBd2DsPi.Data() , nameBd2DsPi.Data(),assumedSig*myconfigfile["nBd2DsPi"],
                            0, assumedSig*myconfigfile["nBd2DsPi"]*2))

        else:
            nBd2DsPi.append(RooRealVar(nameBd2DsPi.Data() , nameBd2DsPi.Data(),assumedSig*myconfigfile["nBd2DsPi"]/2,
                                       0,assumedSig*myconfigfile["nBd2DsPi"]))

        if wider:
            nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(),assumedSig*myconfigfile["nBd2DsstPi"]))
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(),inBd2DPi*myconfigfile["nBd2DstPi"]))
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(),inBd2DPi*myconfigfile["nBd2DRho"]))
        else:
            nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(), 0.0))
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(), 0.0))
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(), 0.0))

        print nBd2DsstPi[i].GetName()
        print nBd2DstPi[i].GetName()
        print nBd2DRho[i].GetName()
        bkgBdDsPi.append(Bs2Dsh2011TDAnaModels.buildBdDsX(mass,meanBdDsPi,width1,alpha1,n1,width2,alpha2,n2,frac,TString("Bd2DsPi"), debug))        
     
        #---------------------------------------------------------------------------------------------------------------------------#                

    #shared variable:
    # Group 1: Bs->DsstPi, Bs->DsRho
    if wider:
        g1_f1              = RooRealVar( "g1_f1_frac","g1_f1_frac", 0.893, 0, 1)
    else:
        g1_f1              = RooRealVar( "g1_f1_frac","g1_f1_frac", 1.0)
        
    g1_f2              = RooRealVar( "g1_f2_frac","g1_f2_frac", 0.093, 0, 1)
               
    bkgPDF = []

    if (mode == "all" and ( sample == "up" or sample == "down")):
        for i in range(0,5):
            bkgPDF.append(Bs2Dsh2011TDAnaModels.buildBsDsPi_2D(mass,
                                                               massDs,
                                                               workspace[0],
                                                               workspaceID,
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
                                                               meanVarDs[i],
                                                               sigma1VarDs[i],
                                                               sigma2VarDs[i],
                                                               alpha1VarDs[i],
                                                               alpha2VarDs[i],
                                                               fracVarDs[i],
                                                               sm[i],
                                                               lumRatio,
                                                               toys,
                                                               debug ))
            
    else:
        if merge:
            for i in range(0,bound):
                bkgPDF.append(Bs2Dsh2011TDAnaModels.buildBsDsPi_2D(mass,
                                                                   massDs,
                                                                   workspace[0],
                                                                   workspaceID,
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
                                                                   meanVarDs[i],
                                                                   sigma1VarDs[i],
                                                                   sigma2VarDs[i],
                                                                   alpha1VarDs[i],
                                                                   alpha2VarDs[i],
                                                                   fracVarDs[i],
                                                                   sm[i],
                                                                   lumRatio,
                                                                   toys,
                                                                   debug ))
                
        else:
            for i in range(0,ranmode):
                for j in range (0,ransample):
                    bkgPDF.append(Bs2Dsh2011TDAnaModels.buildBsDsPi_2D(mass,
                                                                       massDs,
                                                                       PIDK,
                                                                       workspace[0],
                                                                       workspaceID,
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
                                                                       meanVarDs[i*2+j],
                                                                       sigma1VarDs[i*2+j],
                                                                       sigma2VarDs[i*2+j],
                                                                       alpha1VarDs[i*2+j],
                                                                       alpha2VarDs[i*2+j],
                                                                       fracVarDs[i*2+j],
                                                                       sm[i*2+j],
                                                                       lumRatio,
                                                                       toys,
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
    fitter.fit(True, RooFit.Extended(), RooFit.SumW2Error(True))
    result = fitter.getFitResult()
    result.Print("v")

    if (not toys ):
        name = TString("./sWeights_BsDsPi_")+modeTS+TString("_")+sampleTS+TString(".root")
    else:
        name = options.sweightoutputname
        
    #Now includes setting things constant
    if sweight:
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(RooFit.Eval)
        fitter.savesWeights(mVar, combData, name)
        RooMsgService.instance().reset()
        
    fitter.printYieldsInRange( '*Evts', obsTS.Data() , 5340, 5400 )    
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

parser.add_option( '--fitsignal',
                   dest = 'fitSig',
                   default = 'no',
                   help = 'fit signal, yes or no'
                   )

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

parser.add_option( '--fileNameID',
                   dest = 'fileNameAllID',
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
        
    runBsDsKMassFitterOnData( options.debug,  options.sample , options.mvar, options.mdvar,options.tvar, \
                              options.tagvar, options.tagomegavar, options.idvar,\
                              options.mode, options.sweight, options.yieldBdDPi, options.fitSig,
                              options.fileNameAll, options.fileNameAllID, options.workName,
                              options.logoutputname,options.tagTool, options.configName, options.wider, options.merge)

# -----------------------------------------------------------------------------
