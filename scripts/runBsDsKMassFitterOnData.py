
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

GeneralUtils = GaudiPython.gbl.GeneralUtils
MassFitUtils = GaudiPython.gbl.MassFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------
def runBsDsKMassFitterOnData( debug, sample, mVar, tVar, tagVar, tagOmegaVar, idVar, mode,
                              sweight, fitSignal, fileNameAll,workName,configName ) :


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

    configNameTS = TString(configName)
    if configNameTS.Contains("Toys") == false:
        toys = false
    else:
        toys = true
                            
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    workNameTS = TString(workName)
    workspace = []
    workspace.append(GeneralUtils.LoadWorkspace(TString(fileNameAll),workNameTS, debug))

    obsTS = TString(mVar)
    mass        = GeneralUtils.GetObservable(workspace[0],obsTS, debug)
    tvar        = GeneralUtils.GetObservable(workspace[0],TString(tVar), debug)
    tagomegavar = GeneralUtils.GetObservable(workspace[0],TString(tagOmegaVar), debug)
    if (not toys ):
        tagvar      = GeneralUtils.GetObservable(workspace[0],TString(tagVar), debug)
        idvar       = GeneralUtils.GetObservable(workspace[0],TString(idVar), debug) 
    else:
        tagvar      = GeneralUtils.GetObservable(workspace[0],TString(tagVar)+TString("_idx"), debug)
        idvar       = GeneralUtils.GetObservable(workspace[0],TString(idVar)+TString("_idx"), debug)
        trueidvar   = GeneralUtils.GetObservable(workspace[0],TString("lab0_TRUEID"), debug)
                
    observables = RooArgSet( mass,tvar,tagvar,tagomegavar,idvar )
    if toys :
        observables = RooArgSet( mass,tvar,tagvar,tagomegavar,idvar,trueidvar) 

    sampleMC = [TString("up"),TString("down")]

    if ( fitSignal == "yes" ):
        dataMCBs= []
        nEntriesMCBs = []
        for i in range(0,2):
            datasetMCBsTS = TString("dataSetMCBsDsK_")+sampleMC[i]
            dataMCBs.append(GeneralUtils.GetDataSet(workspace[0],datasetMCBsTS, debug))
            nEntriesMCBs.append(dataMCBs[i].numEntries())
            if debug:
                print "Data set: %s with number of events: %s"%(dataMCBs[i].GetName(),nEntriesMCBs[i])
        
        dataMCBd= []
        nEntriesMCBd = []
        for i in range(0,2):
            datasetMCBdTS = TString("dataSetMCBdDsK_")+sampleMC[i]
            dataMCBd.append(GeneralUtils.GetDataSet(workspace[0],datasetMCBdTS, debug))
            nEntriesMCBd.append(dataMCBd[i].numEntries())
            if debug:
                print "Data set: %s with number of events: %s"%(dataMCBd[i].GetName(),nEntriesMCBd[i])
                                            
        meanVarBs   =  RooRealVar( "DblCBBsPDF_mean" ,  "mean",    5367.51,  5000.,  5600., "MeV/c^{2}")
        sigma1VarBs =  RooRealVar( "DblCBBsPDF_sigma1", "sigma1",  10.0880 , 5,      25, "MeV/c^{2}")
        sigma2VarBs =  RooRealVar( "DblCBBsPDF_sigma2", "sigma2",  15.708,   10,     50, "MeV/c^{2}")
        alpha1VarBs =  RooRealVar( "DblCBBsPDF_alpha1", "alpha1",  1.8086,   0,      4)
        alpha2VarBs =  RooRealVar( "DblCBBsPDF_alpha2", "alpha2",  -1.8169,  -4,      0)
        n1VarBs     =  RooRealVar( "DblCBBsPDF_n1",     "n1",      1.3830,   0.0001, 5)
        n2VarBs     =  RooRealVar( "DblCBBsPDF_n2",     "n2",      8.8559,   0.1,    12)
        fracVarBs   =  RooRealVar( "DblCBBsPDF_frac",   "frac",    0.47348,  0,      1);

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
            nSigMCBs.append(RooRealVar( nameSigMCBs.Data(), nameSigMCBs.Data(), nSigEvtsMCBs[i], 0., nEntriesMCBs[i] ))
            sigPDFMCBs.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVarBs, sigma1VarBs, alpha1VarBs, n1VarBs, sigma2VarBs, alpha2VarBs, n2VarBs, fracVarBs, nSigMCBs[i], sampleMC[i].Data(), bName, debug ))
            
        nSigEvtsMCBd = []
        nSigMCBd = []
        sigPDFMCBd = []
        for i in range(0,2):
            nSigEvtsMCBd.append(0.9*nEntriesMCBd[i])
            nameSigMCBd = TString("nSigEvtsBd_")+sampleMC[i]
            nSigMCBd.append(RooRealVar( nameSigMCBd.Data(), nameSigMCBd.Data(), nSigEvtsMCBd[i], 0., nEntriesMCBd[i] ))
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
        resultMCBd.Print()
        modelBd = fitterMCBd.getModelPDF()
        
        paramsBd = modelBd.getVariables() 
        paramsBd.Print("v")
        
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
        
    datasetTS = TString("dataSetBsDsK_")
    sam = RooCategory("sample","sample")

    sm = []
    data = []
    nEntries = []

    ### Obtain data set ###
    
    if sample == "both":
        if mode == "all" :
            if debug:
                print "[INFO] Sample both. Mode all."
            
            s = [TString('up'),TString('down')]
            m = [TString('kkpi'),TString('kpipi'),TString('pipipi')]
            t = TString('_')

            for i in range(0,3):
                for j in range(0,2):
                    sm.append(s[j]+t+m[i])
                    sam.defineType(sm[i*2+j].Data())
                    data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[2*i+j], debug))
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
            print "Sample both. Mode %s."%(mode)
            
            s = [TString('up'),TString('down')]
            t = TString('_')

            for i in range(0,2):
                sm.append(s[i]+t+modeTS)
                sam.defineType(sm[i].Data())
                data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[i],debug))
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
        
        if mode == "all":
            if debug:
                print "Sample %s. Mode all"%(sample)

            s = [sampleTS]
            m = [TString('kkpi'),TString('kpipi'),TString('pipipi')]
            t = TString('_')

            for i in range(0,3):
                sm.append(sampleTS+t+m[i])
                sam.defineType(sm[i].Data())
                data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[i],debug))
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
            data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[0]))
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
            
    s1 = RooRealVar( "Signal_sigma1", "Signal_sigma1", sigma1, 5., 50 )
    s2 = RooRealVar( "Signal_sigma2", "Signal_sigma2", sigma2, 5., 50 )
    r1 = RooRealVar( "ratio1", "ratio1", ratio1 )
    r2 = RooRealVar( "ratio2", "ratio2", ratio2 )
    mn = RooRealVar( "Signal_mean", "Signal_mean", mean, 5100, 5600, "MeV/c^{2}")    
                                        
    for i in range(0,ran):
        nSigEvts.append(0.4*nEntries[i])
        name = TString("nSig")+t+sm[i]+t+TString("Evts")
        nSig.append(RooRealVar( name.Data(), name.Data(), nSigEvts[i], 0., nEntries[i] ))
        sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_fix(mass,mn,s1,alpha1,n1,s2,alpha2,n2,frac,nSig[i],sm[i].Data(),bName,debug))

             
    # Create the background PDF in mass
    
    nCombBkgEvts = []
    nKEvts = []
    for i in range(0,ran):
        nCombBkgEvts.append(0.2*nEntries[i])           # combinatorial background events
        nKEvts.append(0.3*nEntries[i])                 # Bs->DsK, Bs->Ds*K, Bs->DsK*, Bs->Ds*K* together
               
    evts = TString("Evts")
    nCombBkg = []
    nBs2DsDsstPiRho = []
    nBs2DsDssKKst = []
    nLb2DsDsstp = []
    nBd2DK = []
    
    bkgBdDsK = []
    width1 = RooFormulaVar("BsDsX_sigma1" , "BsDsX_sigma1",'@0*@1', RooArgList(s1,r1))
    width2 = RooFormulaVar("BsDsX_sigma2" , "BsDsX_sigma2",'@0*@1', RooArgList(s2,r2))
    shift = 5369.600-5279.400
    meanBdDsK =  RooFormulaVar("BsDsX_mean" , "BsDsX_mean",'@0-86.8', RooArgList(mn))

    for i in range(0,ran):
        
        nameCombBkg = TString("nCombBkg_")+sm[i]+t+evts
        nCombBkg.append(RooRealVar( nameCombBkg.Data()  , nameCombBkg.Data() , nCombBkgEvts[i] , 0. , nEntries[i] ))

        nameBs2DsDsstPiRho = TString("nBs2DsDsstPiRho_")+sm[i]+t+evts
        nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(),
                                           myconfigfile["nBs2DsDsstPiRhoEvts"][i],
                                           myconfigfile["nBs2DsDsstPiRhoEvts"][i]-myconfigfile["nBs2DsDsstPiRhoEvts"][i]*1.0,
                                           myconfigfile["nBs2DsDsstPiRhoEvts"][i]+myconfigfile["nBs2DsDsstPiRhoEvts"][i]*2.0 ))

        nameLb2LcK = TString("nLb2LcK_")+sm[i]+t+evts
        
        nLb2LcK.append(RooRealVar( nameLb2LcK.Data(), nameLb2LcK.Data(), myconfigfile["nLbLcKEvts"][i]))    
        
        nameBs2DsDssKKst = TString("nBs2DsDssKKst_")+sm[i]+t+evts
        nBs2DsDssKKst.append(RooRealVar( nameBs2DsDssKKst.Data(), nameBs2DsDssKKst.Data(), nKEvts[i] , 0. , nEntries[i]/2 ))

        nameLb2DsDsstp = TString("nLb2DsDsstp_")+sm[i]+t+evts
        nLb2DsDsstp.append(RooRealVar( nameLb2DsDsstp.Data(), nameLb2DsDsstp.Data(), myconfigfile["nLbDspEvts"][i]))
       
        nameBd2DK = TString("nBd2DK_")+sm[i]+t+evts
        nBd2DK.append(RooRealVar( nameBd2DK.Data(), nameBd2DK.Data(), myconfigfile["nBdDKEvts"][i]))    
                       
        bkgBdDsK.append(Bs2Dsh2011TDAnaModels.buildBdDsX(mass,meanBdDsK,width1,alpha1,n1,width2,alpha2,n2,frac,TString("Bd2DsK")))        

        #---------------------------------------------------------------------------------------------------------------------------#                

    #shared variable:
    # Group 1: Bd->DsK, Bs->DsK*, Bs->Ds*K, Bs->Ds*K*

    g1_f1              = RooRealVar( "g1_f1_frac","g1_f1_frac", 0.5, 0, 1);
    g1_f2              = RooRealVar( "g1_f2_frac","g1_f2_frac", 0.5, 0, 1);
    g1_f3              = RooRealVar( "g1_f3_frac","g1_f3_frac", 0.5, 0, 1);
                        
    # Group 2:
    g2_f1              = RooRealVar( "g2_f1_frac","g2_f1_frac", myconfigfile["g2_f1"])
    g2_f2              = RooRealVar( "g2_f2_frac","g2_f2_frac", myconfigfile["g2_f2"])
    g2_f3              = RooRealVar( "g2_f3_frac","g2_f3_frac", myconfigfile["g2_f3"])
        
    if toys :   
        g2_f1              = RooRealVar( "g2_f1_frac","g2_f1_frac", 0.374)
        g2_f2              = RooRealVar( "g2_f2_frac","g2_f2_frac", 0.196)
        g2_f3              = RooRealVar( "g2_f3_frac","g2_f3_frac", 0.127)

    # Group 3: g3_f1*Lb->Dsp + (1-g3_f1)Lb->Ds*p
    g3_f1              = RooRealVar( "g3_f1_frac","g3_f1_frac", 0.5)

    bkgPDF = []

    if (mode == "all" and ( sample == "up" or sample == "down")):
        for i in range(0,3):
            bkgPDF.append(Bs2Dsh2011TDAnaModels.buildBsDsK_sim(mass, workspace[0],
                                                               bkgBdDsK[i],
                                                               nCombBkg[i],
                                                               nBs2DsDsstPiRho[i],
                                                               nBs2DsDssKKst[i],
                                                               nLb2DsDsstp[i],
                                                               nBd2DK[i],
                                                               nLb2LcK[i],
                                                               g1_f1,
                                                               g1_f2,
                                                               g1_f3,
                                                               g2_f1,
                                                               g2_f2,
                                                               g2_f3,
                                                               g3_f1,
                                                               s[0], sm[i], toys, debug ))
    else:
        for i in range(0,ranmode):
            for j in range (0,ransample):
                print "i %s, j %s"%(i,j)
                print "sample: %s, sm: %s, name: %s"%(s[j],sm[i*2+j],nCombBkg[i*2+j])
                bkgPDF.append(Bs2Dsh2011TDAnaModels.buildBsDsK_sim(mass, workspace[0],
                                                                   bkgBdDsK[i*2+j],
                                                                   nCombBkg[i*2+j],
                                                                   nBs2DsDsstPiRho[i*2+j],
                                                                   nBs2DsDssKKst[i*2+j],
                                                                   nLb2DsDsstp[i*2+j],
                                                                   nBd2DK[i*2+j],
                                                                   nLb2LcK[i*2+j],
                                                                   g1_f1,
                                                                   g1_f2,
                                                                   g1_f3,
                                                                   g2_f1,
                                                                   g2_f2,
                                                                   g2_f3,
                                                                   g3_f1,
                                                                   s[j], sm[i*2+j], toys, debug ))

        
        
    # Create total the model PDF in mass

    N_Bkg_Tot = []

    totPDFp = []    
    for i in range(0,ran):    
        name = TString("TotEPDF_m_")+sm[i]
        N_Bkg_Tot.append(RooFormulaVar((TString("N_Bkg_Tot_")+sm[i]+TString("_Evts")).Data(),"@0+@1+@2+@3+@4+@5",\
                         RooArgList(nCombBkg[i],nBs2DsDsstPiRho[i],nBs2DsDssKKst[i],nLb2DsDsstp[i],nBd2DK[i],nLb2LcK[i]))) 
        totPDFp.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass', RooArgList( sigPDF[i], bkgPDF[i] ),RooArgList(nSig[i],N_Bkg_Tot[i]) ))

    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    for i in range(0,ran):
        totPDF.addPdf(totPDFp[i], sm[i].Data())
        
    # Instantiate and run the fitter
    fitter = FitMeTool( debug )
      
    fitter.setObservables( observables )

    fitter.setModelPDF( totPDF )
    
    fitter.setData(combData) 
        
    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    #if plot_init :
    #    fitter.saveModelPDF( options.wsname )
    #    fitter.saveData ( options.wsname )
    
    fitter.fit(True, RooFit.Extended(), RooFit.SumW2Error(True))
    result = fitter.getFitResult()
    result.Print("v")
    #fitter.printYieldsInRange( '*Evts', obsTS.Data() , 5320, 5420 )    

    if ( not toys):
        name = TString("./sWeights_BsDsK_")+modeTS+TString("_")+sampleTS+TString(".root")
    else:
        name = options.sweightoutputname

     
    if (sweight):
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(RooFit.Eval)
        fitter.savesWeights(mVar, combData, name)
        RooMsgService.instance().reset() 

    fitter.printYieldsInRange( '*Evts', obsTS.Data() , 5320, 5420 )

    if plot_fitted :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )
                        
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
                   default = 'WS_Mass_DsK.root', 
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )
parser.add_option( '--sweightoutputname',
                   dest = 'sweightoutputname',
                   default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_080912/DsK_Toys_Full_sWeights_ForTimeFit_2kSample_55.root', 
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
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
                   help = 'create and save sWeights, choose: yes or no'
                   )

parser.add_option( '--fitsignal',
                   dest = 'fitsig',
                   default = 'no',
                   help = 'fitsignal shape, yes or no'
                   )

parser.add_option( '--fileName',
                   dest = 'fileNameAll',
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
                   default = 'Bs2DsKConfigForNominalMassFit')

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
    import sys
    sys.path.append("../data/")
    
    runBsDsKMassFitterOnData(   options.debug,  options.sample , options.mvar, options.tvar, \
                                options.tagvar, options.tagomegavar, options.idvar,\
                                options.mode, options.sweight, options.fitsig, \
                                options.fileNameAll, options.workName, options.configName)

# -----------------------------------------------------------------------------
