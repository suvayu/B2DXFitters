
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
bName = 'Bs'
dName = 'Ds'
#------------------------------------------------------------------------------
def runBsDsKMassFitterOnData( debug, sample, mVar, mdVar, tVar, terrVar, tagVar, tagOmegaVar, idVar, mode,
                              sweight,  fileNameAll, fileNameToys, workName, configName, wide, merge ) :


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
    workNameTS = TString(workName)
    
    if configNameTS.Contains("Toys") == false:
        toys = false
    else:
        toys = true
        workspaceToys = (GeneralUtils.LoadWorkspace(TString(fileNameToys),workNameTS, debug))
        workspaceToys.Print("v")
        
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    if merge:
        if sample == "up" or sample == "down":
            print "You cannot use option --merge with sample: up or down"
            exit(0)

    workspace = []
    workspace.append(GeneralUtils.LoadWorkspace(TString(fileNameAll),workNameTS, debug))
         
    obsTS = TString(mVar)
    
    if (not toys ):
        mass        = GeneralUtils.GetObservable(workspace[0],obsTS, debug)
        massDs      = GeneralUtils.GetObservable(workspace[0],TString(mdVar), debug)
        PIDK        = GeneralUtils.GetObservable(workspace[0],TString("lab1_PIDK"), debug)
        tvar        = GeneralUtils.GetObservable(workspace[0],TString(tVar), debug)
        terrvar     = GeneralUtils.GetObservable(workspace[0],TString(terrVar), debug)
        tagomegavar = GeneralUtils.GetObservable(workspace[0],TString(tagOmegaVar), debug)
        tagvar      = GeneralUtils.GetObservable(workspace[0],TString(tagVar), debug)
        idvar       = GeneralUtils.GetObservable(workspace[0],TString(idVar), debug) 
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
                
    observables = RooArgSet( mass,massDs, PIDK, tvar, terrvar, tagvar,tagomegavar,idvar )
    if toys :
        observables.add(trueidvar) 
                                                  
    
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
    t = TString('_')

    ### Obtain data set ###
    if toys:
        s = [sampleTS, sampleTS]
        m = [modeTS]
        sm.append(s[0]+t+m[0])
        data.append(GeneralUtils.GetDataSet(workspaceToys,datasetTS+TString("toys"),debug))
        nEntries.append(data[0].numEntries())
        
        if debug:
            print "nEntries: %s"%(nEntries[0])

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
                                
                for i in range(0,5):
                    for j in range(0,2):
                        sm.append(s[j]+t+m[i])
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
                    print "[INFO] Sample both. Mode 3modes."
                    
                    s = [TString('up'),TString('down')]
                    if mode == "3modeskkpi":
                        m = [TString('nonres'),TString('phipi'),TString('kstk')]
                    else:
                        m = [TString('kkpi'),TString('kpipi'),TString('pipipi')]
            
                    t = TString('_')
            
                    for i in range(0,3):
                        for j in range(0,2):
                            sm.append(s[j]+t+m[i])
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
                print "Sample both. Mode %s."%(mode)
                
                m = [modeTS]
                s = [TString('up'),TString('down')]
                t = TString('_')
                
                for i in range(0,2):
                    sm.append(s[i]+t+modeTS)
                    data.append(GeneralUtils.GetDataSet(workspace[0],datasetTS+sm[i],debug))
                    nEntries.append(data[i].numEntries())
                    
                if debug:
                    print "nEntries: %s + %s = %s"%(nEntries[0], nEntries[1],nEntries[0]+nEntries[1])
                    
                if merge:
                    data[0].append(data[1])
                    s = [TString('both'),TString('both')]
                    for i in range(0,2):
                        sm[i] = s[i]+t+modeTS
                        sam.defineType(sm[i].Data())
                        
                        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                              RooFit.Index(sam),
                                              RooFit.Import(sm[0].Data(),data[0]))
                        nEntries[0] = nEntries[0]+nEntries[1]
                                                      
                else:
                    for i in range(0,2):
                        sam.defineType(sm[i].Data())
                        
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
                    
              
    s1 = []
    s2 = []
    s1Ds = []
    s2Ds = []
    ratio1 = myconfigfile["ratio1"]
    ratio2 = myconfigfile["ratio2"]
    
    r1 = RooRealVar( "ratio1", "ratio1", ratio1 )
    r2 = RooRealVar( "ratio2", "ratio2", ratio2 )
    mn = RooRealVar( "Signal_mean", "Signal_mean", myconfigfile["mean"][0],
                     myconfigfile["mean"][0]-100,    myconfigfile["mean"][0] +100, "MeV/c^{2}")
    mnDs = RooRealVar( "Signal_mean_Ds", "Signal_mean_Ds", myconfigfile["meanDs"][0],
                       myconfigfile["meanDs"][0]-100,    myconfigfile["meanDs"][0] +100, "MeV/c^{2}")
    
    alpha1Var = []
    alpha2Var = []
    

    if merge:
        bound = ranmode
    else:
        bound = ran
        
    for i in range(0,bound):
        if wide:
            nSigEvts.append(0.4*nEntries[i])
        else:
            nSigEvts.append(0.7*nEntries[i])

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
        s1Ds.append(RooRealVar( name.Data(), name.Data(), sig1Ds)) #,
        name = TString("Signal_sigma2_Ds_")+sm[i]
        s2Ds.append(RooRealVar( name.Data(), name.Data(), sig2Ds)) #,

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
        
    #exit(0)
    nSigdG = []
    sigPIDKPDF = []
    sigProdPDF = []
    sigEPDF = []
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])

    for i in range(0,bound):
        name2 = TString("SigProdPDF")+t+sm[i]
        name3 = TString("SigEPDF")+t+sm[i]
        namePID = TString("Bs2DsK_")+sm[i]
        k = bound%2
        print k
        sigPIDKPDF.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace[0], namePID, s[k], lumRatio, true, debug))
        sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDsPDF[i],sigPIDKPDF[i])))
        print sigProdPDF[i].GetName()
        sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigProdPDF[i], nSig[i]))
        print sigEPDF[i].GetName()
           
    # Create the background PDF in mass
    
    nCombBkgEvts = []
    nKEvts = []
    for i in range(0,bound):
        nCombBkgEvts.append(0.2*nEntries[i])           # combinatorial background events
        nKEvts.append(0.3*nEntries[i])                 # Bs->DsK, Bs->Ds*K, Bs->DsK*, Bs->Ds*K* together
               
    evts = TString("Evts")
    nCombBkg = []
    nBs2DsDsstPiRho = []
    nBs2DsPi = []
    nBs2DsDssKKst = []
    nLb2DsDsstp = []
    nBd2DK = []
    nLb2LcK = []
    
    bkgBdDsK = []
    width1 = []
    width2 = []
    shift = 5369.600-5279.400
    meanBdDsK =  RooFormulaVar("BsDsX_mean" , "BsDsX_mean",'@0-86.8', RooArgList(mn))

    cBVar = []
    cDVar = []
    fracComb = []
    j = 0

    for i in range(0,bound):
        name = TString("BdDsX_sigma1_") + sm[i]
        width1.append(RooFormulaVar(name.Data(), name.Data(),'@0*@1', RooArgList(s1[i],r1)))
        name = TString("BdDsX_sigma2_") + sm[i]
        width2.append(RooFormulaVar(name.Data() , name.Data(),'@0*@1', RooArgList(s2[i],r2)))
                        

        nameCombBkg = TString("nCombBkg_")+sm[i]+t+evts
        nameBs2DsDsstPiRho = TString("nBs2DsDsstPiRho_")+sm[i]+t+evts
        nameBs2DsPi = TString("nBs2DsPi_")+sm[i]+t+evts
        nameLb2LcK = TString("nLb2LcK_")+sm[i]+t+evts
        nameBs2DsDssKKst = TString("nBs2DsDssKKst_")+sm[i]+t+evts
        nameLb2DsDsstp = TString("nLb2DsDsstp_")+sm[i]+t+evts
        nameBd2DK = TString("nBd2DK_")+sm[i]+t+evts
        if merge:
            inBs2DsPiEvts = myconfigfile["nBs2DsPiEvts"][i*2]+myconfigfile["nBs2DsPiEvts"][i*2+1]
            inBs2DsDsstPiRhoEvts = myconfigfile["nBs2DsDsstPiRhoEvts"][i*2]+myconfigfile["nBs2DsDsstPiRhoEvts"][i*2+1]
            inLbLcKEvts = myconfigfile["nLbLcKEvts"][i*2] + myconfigfile["nLbLcKEvts"][i*2+1]
            inLbDspEvts = myconfigfile["nLbDspEvts"][i*2] + myconfigfile["nLbDspEvts"][i*2+1]
            inBdDKEvts = myconfigfile["nBdDKEvts"][i*2]+myconfigfile["nBdDKEvts"][i*2+1]
        else:
            inBs2DsDsstPiRhoEvts = myconfigfile["nBs2DsDsstPiRhoEvts"][i]
            inBs2DsPiEvts = myconfigfile["nBs2DsPiEvts"][i]
            inLbLcKEvts = myconfigfile["nLbLcKEvts"][i]
            inLbDspEvts = myconfigfile["nLbDspEvts"][i]
            inBdDKEvts = myconfigfile["nBdDKEvts"][i]
            
        nCombBkg.append(RooRealVar( nameCombBkg.Data()  , nameCombBkg.Data() , nCombBkgEvts[i] , 0. , nEntries[i] ))

        if wide:
            nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(),
                                               inBs2DsDsstPiRhoEvts*3,
                                               inBs2DsDsstPiRhoEvts-inBs2DsDsstPiRhoEvts*1.0,
                                               inBs2DsDsstPiRhoEvts+inBs2DsDsstPiRhoEvts*5.0 ))
        else:
            nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(),  inBs2DsDsstPiRhoEvts/2, 0.0, inBs2DsDsstPiRhoEvts*3.0 ))

        nBs2DsPi.append(RooRealVar( nameBs2DsPi.Data(), nameBs2DsPi.Data(),  inBs2DsPiEvts))     
        nLb2LcK.append(RooRealVar( nameLb2LcK.Data(), nameLb2LcK.Data(), inLbLcKEvts)) #/2, 0, inLbLcKEvts*2.0))    

        if wide:
            nBs2DsDssKKst.append(RooRealVar( nameBs2DsDssKKst.Data(), nameBs2DsDssKKst.Data(), nKEvts[i] , 0. , nEntries[i]/2 ))
        else:
            nBs2DsDssKKst.append(RooRealVar( nameBs2DsDssKKst.Data(), nameBs2DsDssKKst.Data(), nEntries[i]/15 , nEntries[i]/200, nEntries[i]/3 ))

        if wide:
            nLb2DsDsstp.append(RooRealVar( nameLb2DsDsstp.Data(), nameLb2DsDsstp.Data(), inLbDspEvts,
                                           0.0, inLbDspEvts*3))
        else:
            nLb2DsDsstp.append(RooRealVar( nameLb2DsDsstp.Data(), nameLb2DsDsstp.Data(), inLbDspEvts/2,
                                           0, inLbDspEvts*4.0))
                                           #myconfigfile["nLbDspEvts"][i]/15, myconfigfile["nLbDspEvts"][i]*4.0))
            
        if wide:
            nBd2DK.append(RooRealVar( nameBd2DK.Data(), nameBd2DK.Data(), inBdDKEvts,
                                      0, inBdDKEvts*2))    
        else:
            nBd2DK.append(RooRealVar( nameBd2DK.Data(), nameBd2DK.Data(), inBdDKEvts)) #/2, 0, inBdDKEvts))
                                                                            
        al1 = myconfigfile["alpha1_bc"][i] #*myconfigfile["alpha1Bsfrac"]
        al2 = myconfigfile["alpha2_bc"][i] #*myconfigfile["alpha2Bsfrac"]
        n1 =  myconfigfile["n1_bc"][i]
        n2 =  myconfigfile["n2_bc"][i]
        frac =  myconfigfile["frac_bc"][i]
                                
        bkgBdDsK.append(Bs2Dsh2011TDAnaModels.buildBdDsX(mass,meanBdDsK,
                                                         width1[i],al1,n1,
                                                         width2[i],al2,n2,
                                                         frac,
                                                         m[j],
                                                         TString("Bd2DsK"), debug))

        mul = 10.0
        confTS = TString(configName)
        if confTS.Contains("BDTG3"):
            mul = 30.0
        name = TString("CombBkg_slope_Bs_")+m[j]
        cBVar.append(RooRealVar(name.Data(), name.Data(), myconfigfile["cB"][i],
                                myconfigfile["cB"][i]+myconfigfile["cB"][i]*mul, 0))
        name = TString("CombBkg_slope_Ds_")+m[j]
        cDVar.append(RooRealVar(name.Data(), name.Data(), myconfigfile["cD"][i],
                                myconfigfile["cD"][i]+myconfigfile["cD"][i]*mul, 0))
        name = TString("CombBkg_fracComb_")+m[j]
        if ( sm[i].Contains("kpipi") == true or sm[i].Contains("pipipi") == true ):
            fracComb.append(RooRealVar(name.Data(), name.Data(), myconfigfile["fracComb"][i]))
        else:
            fracComb.append(RooRealVar(name.Data(), name.Data(), myconfigfile["fracComb"][i], 0.0, 1.0))
           
        if merge:
            j=j+1
        else:
            if i == 1 or i == 3:
                j=j+1
                
                
        #---------------------------------------------------------------------------------------------------------------------------#                

    #shared variable:
    # Group 1: Bd->DsK, Bs->DsK*, Bs->Ds*K, Bs->Ds*K*

    g1_f1              = RooRealVar( "g1_f1_frac","g1_f1_frac", 0.5, 0, 1);
    g1_f2              = RooRealVar( "g1_f2_frac","g1_f2_frac", 0.5, 0, 1);
    g1_f3              = RooRealVar( "g1_f3_frac","g1_f3_frac", 0.5, 0, 1);
                        
    # Group 2:
    g2_f1              = RooRealVar( "g2_f1_frac","g2_f1_frac", 0.5, 0, 1) #myconfigfile["g2_f1"],0,1)
    g2_f2              = RooRealVar( "g2_f2_frac","g2_f2_frac", 0.5, 0, 1) #myconfigfile["g2_f2"],0,1)
    g2_f3              = RooRealVar( "g2_f3_frac","g2_f3_frac", 0.5, 0, 1) #myconfigfile["g2_f3"],0,1)
        
    #if toys :   
    #    g2_f1              = RooRealVar( "g2_f1_frac","g2_f1_frac", 0.374)
    #    g2_f2              = RooRealVar( "g2_f2_frac","g2_f2_frac", 0.196)
    #    g2_f3              = RooRealVar( "g2_f3_frac","g2_f3_frac", 0.127)

    # Group 3: g3_f1*Lb->Dsp + (1-g3_f1)Lb->Ds*p
    if toys:
        g3_f1              = RooRealVar( "g3_f1_frac","g3_f1_frac", 0.9)
    else:
        g3_f1              = RooRealVar( "g3_f1_frac","g3_f1_frac", 0.5, 0.0, 1.0)

    g4_f1              = RooRealVar( "g4_f1_frac","g4_f1_frac", 0.6, 0.5, 1.0)
    g4_f2              = RooRealVar( "g4_f2_frac","g4_f2_frac", 0.6, 0.0, 1.0)
    
    bkgPDF = []

    if (mode == "all" and ( sample == "up" or sample == "down")):
        for i in range(0,3):
            bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsK_BKG_MDFitter(mass,
                                                                          massDs,
                                                                          workspace[0],
                                                                          #workspaceID,
                                                                          #workspaceID2,
                                                                          bkgBdDsK[i],
                                                                          nCombBkg[i],
                                                                          nBs2DsDsstPiRho[i],
                                                                          nBs2DsPi[i],
                                                                          nBs2DsDssKKst[i],
                                                                          nLb2DsDsstp[i],
                                                                          nBd2DK[i],
                                                                          nLb2LcK[i],
                                                                          g1_f1,
                                                                          g1_f2,
                                                                          g1_f3,
                                                                          g2_f1,
                                                                          #g2_f2,
                                                                          #g2_f3,
                                                                          g3_f1,
                                                                          g4_f1,
                                                                          g4_f2,
                                                                          sigDsPDF[i],
                                                                          cBVar[i],
                                                                          cDVar[i],
                                                                          fracComb[i],
                                                                          sm[i],
                                                                          lumRatio,
                                                                          debug ))
    else:
        if merge:
            for i in range(0,bound):
                bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsK_BKG_MDFitter(mass,
                                                                              massDs,
                                                                              workspace[0],
                                                                              #workspaceID,
                                                                              #workspaceID2,
                                                                              bkgBdDsK[i],
                                                                              nCombBkg[i],
                                                                              nBs2DsDsstPiRho[i],
                                                                              nBs2DsPi[i],
                                                                              nBs2DsDssKKst[i],
                                                                              nLb2DsDsstp[i],
                                                                              nBd2DK[i],
                                                                              nLb2LcK[i],
                                                                              g1_f1,
                                                                              g1_f2,
                                                                              g1_f3,
                                                                              g2_f1,
                                                                              #g2_f2,
                                                                              #g2_f3,
                                                                              g3_f1,
                                                                              g4_f1,
                                                                              g4_f2,
                                                                              sigDsPDF[i],
                                                                              cBVar[i],
                                                                              cDVar[i],
                                                                              fracComb[i],
                                                                              sm[i],
                                                                              lumRatio,
                                                                              debug ))
                
        else:
           
            for i in range(0,ranmode):
                for j in range (0,ransample):
                    print "i %s, j %s"%(i,j)
                    print "sample: %s, sm: %s, name: %s"%(s[j],sm[i*2+j],nCombBkg[i*2+j])
                    bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsK_BKG_MDFitter(mass,
                                                                                  massDs,
                                                                                  workspace[0],
                                                                                  #workspaceID,
                                                                                  #workspaceID2,
                                                                                  bkgBdDsK[i*2+j],
                                                                                  nCombBkg[i*2+j],
                                                                                  nBs2DsDsstPiRho[i*2+j],
                                                                                  nBs2DsPi[i*2+j],
                                                                                  nBs2DsDssKKst[i*2+j],
                                                                                  nLb2DsDsstp[i*2+j],
                                                                                  nBd2DK[i*2+j],
                                                                                  nLb2LcK[i*2+j],
                                                                                  g1_f1,
                                                                                  g1_f2,
                                                                                  g1_f3,
                                                                                  g2_f1,
                                                                                  #g2_f2,
                                                                                  #g2_f3,
                                                                                  g3_f1,
                                                                                  g4_f1,
                                                                                  g4_f2,
                                                                                  sigDsPDF[i*2+j],
                                                                                  cBVar[i*2+j],
                                                                                  cDVar[i*2+j],
                                                                                  fracComb[i*2+j],
                                                                                  sm[i*2+j],
                                                                                  lumRatio,
                                                                                  debug ))
                    
        
        
    # Create total the model PDF in mass

    N_Bkg_Tot = []

    totPDFp = []
    totPDFa = []
    for i in range(0,bound):
        name = TString("TotEPDF_m_")+sm[i]
        #N_Bkg_Tot.append(RooFormulaVar((TString("N_Bkg_Tot_")+sm[i]+TString("_Evts")).Data(),"@0+@1+@2+@3+@4+@5",\
        #                 RooArgList(nCombBkg[i],nBs2DsDsstPiRho[i],nBs2DsDssKKst[i],nLb2DsDsstp[i],nBd2DK[i],nLb2LcK[i]))) 
        print sigEPDF[i].GetName()
        print bkgPDF[i].GetName()
        totPDFp.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass', RooArgList( sigEPDF[i], bkgPDF[i] )))
        
    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    for i in range(0,bound):
        print totPDFp[i].GetName()
        print sm[i].Data()
        totPDF.addPdf(totPDFp[i], sm[i].Data())
    totPDF.Print("v")    
    #exit(0)       
    # Instantiate and run the fitter
    fitter = FitMeTool( debug )
      
    fitter.setObservables( observables )

    fitter.setModelPDF( totPDF )
    print "w"
    fitter.setData(combData) 
        
    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    #if plot_init :
    #    fitter.saveModelPDF( options.wsname )
    #    fitter.saveData ( options.wsname )
    
    fitter.fit(True, RooFit.Extended(), RooFit.SumW2Error(True), RooFit.Verbose(True))
    result = fitter.getFitResult()
    result.Print("v")
    #fitter.printYieldsInRange( '*Evts', obsTS.Data() , 5320, 5420 )    

    if ( not toys):
        BDTGTS = GeneralUtils.CheckBDTGBin(confTS, debug)
        name = TString("./sWeights_BsDsK_")+modeTS+TString("_")+sampleTS+TString("_")+BDTGTS+TString("3M.root")
    else:
        name = TString(options.sweightoutputname)

     
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
                   default = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/DsKToys_sWeights_ForTimeFit_0.root', 
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
                   help = 'create and save sWeights, choose: yes or no'
                   )

#parser.add_option( '--fitsignal',
#                   dest = 'fitsig',
#                   default = 'no',
#                   help = 'fitsignal shape, yes or no'
#s                   )

parser.add_option( '--fileName',
                   dest = 'fileNameAll',
                   default = '../data/workspace/work_dsk.root',
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
                   default = 'Bs2DsKConfigForNominalMassFit')
parser.add_option( '--wide', 
                   dest = 'wide',
                   action = 'store_true',
                   default = False,
                   help = 'create and save sWeights, choose: yes or no'
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
    
    runBsDsKMassFitterOnData(   options.debug,  options.sample , options.mvar, options.mdvar, options.tvar, options.terrvar, \
                                options.tagvar, options.tagomegavar, options.idvar,\
                                options.mode, options.sweight, \
                                options.fileNameAll, options.fileNameToys,
                                options.workName, options.configName, options.wide, options.merge)

# -----------------------------------------------------------------------------
