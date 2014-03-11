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
# settings for running without GaudiPython
# -----------------------------------------------------------------------------
""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.

# make sure the environment is set up properly
if test -n "$CMTCONFIG" \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersDict.so \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersLib.so; then
    # all ok, software environment set up correctly, so don't need to do
    # anything
    true
else
    if test -n "$CMTCONFIG"; then
        # clean up incomplete LHCb software environment so we can run
        # standalone
        echo Cleaning up incomplete LHCb software environment.
        PYTHONPATH=`echo $PYTHONPATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export PYTHONPATH
        LD_LIBRARY_PATH=`echo $LD_LIBRARY_PATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
	export LD_LIBRARY_PATH
        exec env -u CMTCONFIG -u B2DXFITTERSROOT "$0" "$@"
    fi
    # automatic set up in standalone build mode
    if test -z "$B2DXFITTERSROOT"; then
        cwd="$(pwd)"
        if test -z "$(dirname $0)"; then
            # have to guess location of setup.sh
            cd ../standalone
            . ./setup.sh
            cd "$cwd"
        else
            # know where to look for setup.sh
            cd "$(dirname $0)"/../standalone
            . ./setup.sh
            cd "$cwd"
        fi
        unset cwd
    fi
fi
# figure out which custom allocators are available
# prefer jemalloc over tcmalloc
for i in libjemalloc libtcmalloc; do
    for j in `echo "$LD_LIBRARY_PATH" | tr ':' ' '` \
            /usr/local/lib /usr/lib /lib; do
        for k in `find "$j" -name "$i"'*.so.?' | sort -r`; do
            if test \! -e "$k"; then
                continue
            fi
            echo adding $k to LD_PRELOAD
            if test -z "$LD_PRELOAD"; then
                export LD_PRELOAD="$k"
                break 3
            else
                export LD_PRELOAD="$LD_PRELOAD":"$k"
                break 3
            fi
        done
    done
done
# set batch scheduling (if schedtool is available)
schedtool="`which schedtool 2>/dev/zero`"
if test -n "$schedtool" -a -x "$schedtool"; then
    echo "enabling batch scheduling for this job (schedtool -B)"
    schedtool="$schedtool -B -e"
else
    schedtool=""
fi

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from B2DXFitters import *
from ROOT import * 
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc
gROOT.SetBatch()

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MISCELLANEOUS
bName = 'Bs'
dName = 'Ds'

#------------------------------------------------------------------------------
def runBsDsKMassFitterOnData( debug, sample,
                              mVar, mdVar, tVar, terrVar, tagVar, tagOmegaVar, idVar,
                              mode, sweight,  
                              fileNameAll, fileNameToys, workName,logoutputname,
                              tagTool, configName, wider, merge, dim ) :

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

    config = TString("../data/")+TString(configName)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)    
           
    workNameTS = TString(workName)
    #workData = GeneralUtils.LoadWorkspace(TString("work_dspi_data.root"),workNameTS,debug)
    workspace = []
    workspace.append(GeneralUtils.LoadWorkspace(TString(fileNameAll),workNameTS,debug))
    workData = workspace[0]

    obsTS = TString(mVar)
    
    configNameTS = TString(configName)
    if configNameTS.Contains("Toys") == false:
        toys = false
    else:
        toys = true
        workspaceToys = (GeneralUtils.LoadWorkspace(TString(fileNameToys),workNameTS, debug))
        workspaceToys.Print("v")
        workData = workspaceToys
                 
    if mode == "hhhpi0":
        mdVar = "Ds_MM"
        mVar = "Bs_MassConsDs_M"
        pidVar = "Bac_PIDK"
        tVar  = "Bs_LifetimeFit_ctau"
        terrVar = "Bs_LifetimeFit_ctauErr"
        #idVar   = "Bs_ID"
        nTrVar  = "nTracks"
        ptVar = "Bac_PT"
    else:
        pidVar = "lab1_PIDK"
        nTrVar = "nTracks"
        ptVar = "lab1_PT"

    MDSettings.SetMassBVar(TString(mVar))
    MDSettings.SetMassDVar(TString(mdVar))
    MDSettings.SetTimeVar(TString(tVar))
    MDSettings.SetTerrVar(TString(terrVar))
    MDSettings.SetIDVar(TString(idVar))    

    if (not toys ):
        mass        = GeneralUtils.GetObservable(workData,TString(mVar), debug)
        massDs      = GeneralUtils.GetObservable(workData,TString(mdVar), debug)
        PIDK        = GeneralUtils.GetObservable(workData,TString(pidVar), debug)
        tvar        = GeneralUtils.GetObservable(workData,TString(tVar), debug)
        terrvar     = GeneralUtils.GetObservable(workData,TString(terrVar), debug)
        idvar       = GeneralUtils.GetCategory(workData,TString(idVar), debug)
        nTrvar      = GeneralUtils.GetObservable(workData,TString(nTrVar), debug)
        ptvar       = GeneralUtils.GetObservable(workData,TString(ptVar), debug)
                
    else:
        mass        = GeneralUtils.GetObservable(workspaceToys,obsTS, debug)
        massDs      = GeneralUtils.GetObservable(workspaceToys,TString(mdVar), debug)
        PIDK        = GeneralUtils.GetObservable(workspaceToys,TString("lab1_PIDK"), debug)
        tvar        = GeneralUtils.GetObservable(workspaceToys,TString(tVar), debug)
        terrvar     = GeneralUtils.GetObservable(workspaceToys,TString(terrVar), debug)
        idvar       = GeneralUtils.GetCategory(workspaceToys,TString(idVar), debug)
        trueidvar   = GeneralUtils.GetObservable(workspaceToys,TString("lab0_TRUEID"), debug)
                
    observables = RooArgSet( mass,massDs, PIDK, tvar, terrvar, idvar )
    
    if toys :
        observables.add(trueidvar)
    else:
        observables.add(nTrvar)
        observables.add(ptvar)
        
    if MDSettings.CheckAddVar() == true:
        for i in range(0,MDSettings.GetNumAddVar()):
            addVar = GeneralUtils.GetObservable(workData, MDSettings.GetAddVarName(i), debug)
            observables.add(addVar)

    tagVar = []
    if MDSettings.CheckTagVar() == true:
        for i in range(0,MDSettings.GetNumTagVar()):
            tagVar.append(GeneralUtils.GetCategory(workData, MDSettings.GetTagVar(i), debug))
            observables.add(tagVar[i])
                        
    tagOmegaVar = []
    tagOmegaVarCalib = []
    if MDSettings.CheckTagOmegaVar() == true:
        for i in range(0,MDSettings.GetNumTagOmegaVar()):
            tagOmegaVar.append(GeneralUtils.GetObservable(workData, MDSettings.GetTagOmegaVar(i), debug))
            nameCalib = MDSettings.GetTagOmegaVar(i) + TString("_calib")
            tagOmegaVarCalib.append(GeneralUtils.GetObservable(workData, nameCalib, debug))
            observables.add(tagOmegaVar[i])
            observables.add(tagOmegaVarCalib[i])
            
    tagDecCombName = TString("tagDecComb")         
    tagDecComb = GeneralUtils.GetCategory(workData, tagDecCombName, debug)
    tagOmegaCombName= TString("tagOmegaComb")
    tagOmegaComb = GeneralUtils.GetObservable(workData, tagOmegaCombName, debug) 

    observables.add(tagDecComb)
    observables.add(tagOmegaComb)
               
    
 ###------------------------------------------------------------------------------------------------------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------###
 ###------------------------------------------------------------------------------------------------------------------------------------###   
    dim = int(dim)
    modeTS = TString(mode)
    sampleTS = TString(sample)

    datasetTS = TString("dataSetBsDsPi_")
            
    sam = RooCategory("sample","sample")
    t = TString('_')

    sm = []
    data = []
    nEntries = []

    ### Obtain data set ###
    if toys:
        s = [TString("both"), TString("both"), TString("both"), TString("both"), TString("both")]
        m = [TString("nonres"), TString("phipi"), TString("kstk"), TString("kpipi"), TString("pipipi")]
        for i in range(0,5):
            sm.append(s[0]+t+m[i])
            sam.defineType(sm[i].Data())
            data.append(GeneralUtils.GetDataSet(workspaceToys,datasetTS+sm[i],debug))
            nEntries.append(data[i].numEntries())
            
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sm[0].Data(),data[0]),
                              RooFit.Import(sm[1].Data(),data[1]),
                              RooFit.Import(sm[2].Data(),data[2]),
                              RooFit.Import(sm[3].Data(),data[3]),
                              RooFit.Import(sm[4].Data(),data[4]))
        
        countSig   = [0,0,0,0,0]
        countCombo = [0,0,0,0,0]
        countLcPi  = [0,0,0,0,0]
        countBDPi  = [0,0,0,0,0]
        countBDsPi = [0,0,0,0,0]
        countRhoPi = [0,0,0,0,0]
        countDsK   = [0,0,0,0,0]
        if debug:
            for j in range(0,m.__len__()):
                print "nEntries: %s"%(nEntries[j])
                obs = data[j].get()
                trueid = obs.find("lab0_TRUEID")
                for i in range(0,nEntries[j]):
                    obs2 = data[j].get(i)
                    if abs(trueid.getValV(obs2)-1.0) < 0.5 :
                        countSig[j] += 1
                    if abs(trueid.getValV(obs2)-2.0) < 0.5 :
                        countBDPi[j] += 1
                    if abs(trueid.getValV(obs2)-3.0) < 0.5 :
                        countBDsPi[j] += 1
                    if abs(trueid.getValV(obs2)-4.0) < 0.5 :
                        countLcPi[j] += 1
                    if abs(trueid.getValV(obs2)-5.0) < 0.5 :
                        countRhoPi[j] += 1
                    if abs(trueid.getValV(obs2)-7.0) < 0.5 :
                        countDsK[j] += 1
                    if abs(trueid.getValV(obs2)-10.0) < 0.5 :
                        countCombo[j] += 1

        #s = [sampleTS, sampleTS]
        #m = [modeTS]
        #sm.append(s[0]+t+m[0])
        #data.append(GeneralUtils.GetDataSet(workspaceToys,datasetTS+TString("toys"),debug))
        #nEntries.append(data[0].numEntries())
        #sam.defineType(sm[0].Data())
        #combData = RooDataSet("combData","combined data",RooArgSet(observables),
        #                      RooFit.Index(sam),
        #                      RooFit.Import(sm
    else:
        combData =  GeneralUtils.GetDataSet(workspace[0], observables, sam, datasetTS, sampleTS, modeTS, merge, debug )
        sm = GeneralUtils.GetSampleMode(sampleTS, modeTS, merge, debug )
        s = GeneralUtils.GetSample(sampleTS, debug)
        m = GeneralUtils.GetMode(modeTS,debug)
        nEntries = GeneralUtils.GetEntriesCombData(workspace[0], datasetTS, sampleTS, modeTS, merge, debug )
        for en in nEntries:
            print en

    # Create the background PDF in mass
    #exit(0)
    nSig = []
    sigPDF = []
    sigDsPDF = []
    nSigEvts = []

    ran = sm.__len__()
    ranmode = m.__len__()
    ransample = s.__len__()
                
    if merge:
        bound = ranmode
    else:
        bound = ran

    #exit(0)
    
    ###------------------------------------------------------------------------------------------------------------------------------------###    
          ###-------------------------   Create the signal PDF in Bs mass, Ds mass, PIDK   ------------------------------------------###          
    ###------------------------------------------------------------------------------------------------------------------------------------###        
    
    workInt = RooWorkspace("workInt","workInt")    

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

        getattr(workInt,'import')(sigPDF[i])
        if ( dim > 1):
            if mode == "hhhpi0":
                sig1Ds = myconfigfile["sigma1Ds_bc"][i]*(myconfigfile["sigma1Dsfrac"]+myconfigfile["sigma2Dsfrac"])/2
                sigma1Var = RooRealVar( "GaussPDF_sigma1", "sigma1",  sig1Ds, "MeV/c^{2}")
                name = TString("sigDs_")+sm[i]
                sigDsPDF.append(RooGaussian(name.Data(), name.Data(), massDs, mnDs, sigma1Var))
            else:    
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
            getattr(workInt,'import')(sigDsPDF[i])
        
    nSigdG = []
    sigProdPDF = []
    sigEPDF = []
    sigPIDKPDF = []
           
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
    getattr(workInt,'import')(lumRatio)

    if dim > 2 :
        for i in range(0,bound):
            namePID = TString("Bs2DsPi_")+sm[i]
            k = bound%2
            sigPIDKPDF.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace[0], namePID, s[k], lumRatio, true, debug))
            getattr(workInt,'import')(sigPIDKPDF[i])

    j=0
    for i in range(0,bound):
        name2 = TString("SigProdPDF")+t+sm[i]
        name3 = TString("SigEPDF")+t+sm[i]
        if dim == 1:
            print "Signal 1D"
            sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i])))
        elif dim == 2:
            print "Signal 2D"
            sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDsPDF[i])))
        elif dim == 3:
            print "Signal 3D"
            sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDsPDF[i],sigPIDKPDF[i])))
        else:
            print "[INFO] Wrong number of fitting dimensions: ",dim
            exit(0)
        sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigProdPDF[i], nSig[i]))    
                    
    ###------------------------------------------------------------------------------------------------------------------------------------###         
        ###-------------------------------   Create the backgrounds PDF in Bs mass, Ds mass, PIDK --------------------------------------###       
    ###------------------------------------------------------------------------------------------------------------------------------------### 

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
    nBd2DsstRho = []
    
    bkgBdDsPi = []

    width1 = []
    width2 = []
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
        nameBd2DsstRho = TString("nBd2DsstRho_")+sm[i]+t+evts
        
        nCombBkg.append(RooRealVar( nameCombBkg.Data()  , nameCombBkg.Data() , nCombBkgEvts[i] , 0. , nEntries[i] ))

        if wider:
            nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(), nPiRhoEvts[i], 0. , nEntries[i] ))
            if mode == "hhhpi0":
                nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(),0,0,nEntries[i]/4))
            else:    
                nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(),assumedSig*myconfigfile["nBd2DsstPi"]))
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(),myconfigfile["BdDPiEvents"][i]*myconfigfile["nBd2DstPi"]))
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(),myconfigfile["BdDPiEvents"][i]*myconfigfile["nBd2DRho"]))
        else:
            nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(), nPiRhoEvts[i], 0. , nEntries[i]/5 ))
            nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(), 0.0))
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(), 0.0))
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(), 0.0))

        if mode != "hhhpi0":    
            nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(), myconfigfile["BdDPiEvents"][i])) #, inBd2DPi*0.25, inBd2DPi*1.75))
            nBs2DsK.append(RooRealVar( nameBs2DsK.Data(), nameBs2DsK.Data(), myconfigfile["BsDsKEvents"][i])) #, inBs2DsK*0.25, inBs2DsK*1.75))    
            nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(),  myconfigfile["LbLcPiEvents"][i])) #, 0.25*inLbLcPi, 1.75*inLbLcPi ))    
        else:
            nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(), 0,0,nEntries[i]/4))       
            nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), 0,0,nEntries[i]/4))
            nBd2DsstRho.append(RooRealVar(nameBd2DsstRho.Data() , nameBd2DsstRho.Data(),0))

        getattr(workInt,'import')(nCombBkg[i])
        if mode != "hhhpi0":
            getattr(workInt,'import')(nBs2DsK[i])
        getattr(workInt,'import')(nLb2LcPi[i])
        getattr(workInt,'import')(nBd2DPi[i])
        getattr(workInt,'import')(nBd2DsstPi[i])
        getattr(workInt,'import')(nBd2DstPi[i])
        getattr(workInt,'import')(nBd2DRho[i])
        getattr(workInt,'import')(nBs2DsDsstPiRho[i])
        if mode == "hhhpi0":
             getattr(workInt,'import')(nBd2DsstRho[i])

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
            name = TString("CombBkg_fracBsComb_")+m[j]
            fracBsComb.append(RooRealVar(name.Data(), name.Data(), 1.0))
                    
        else:
            cB2Var.append(RooRealVar(name.Data(), name.Data(), myconfigfile["cB2"][i]))
            name = TString("CombBkg_fracBsComb_")+m[j]
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
        
        getattr(workInt,'import')(cBVar[i])
        getattr(workInt,'import')(cB2Var[i])
        getattr(workInt,'import')(cDVar[i])
        getattr(workInt,'import')(fracDsComb[i])
        getattr(workInt,'import')(fracBsComb[i])
    
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
    getattr(workInt,'import')(g1_f1)
    getattr(workInt,'import')(g1_f2)
    
    name = TString("CombBkg_fracPIDKComb") 
    print name
    fracPIDKComb = RooRealVar(name.Data(), name.Data(), 0.5, 0.0, 1.0)
    getattr(workInt,'import')(fracPIDKComb)
    
    bkgPDF = []

    if (mode == "all" and ( sample == "up" or sample == "down")):
        for i in range(0,5):
            bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_MDFitter(mass, massDs, workspace[0], workInt, bkgBdDsPi[i], sm[i], dim, debug ))
            
    else:
        if merge:
            if mode == "hhhpi0":
                for i in range(0,bound):
                    bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_HHHPi0(mass, massDs, workspace[0], workInt, bkgBdDsPi[i], sm[i], dim, debug ))
            else:    
                for i in range(0,bound):
                    bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_MDFitter(mass, massDs, workspace[0], workInt, bkgBdDsPi[i], sm[i], dim, debug ))
                
        else:
            for i in range(0,ranmode):
                for j in range (0,ransample):
                    if mode == "hhhpi0":
                        bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_HHHPi0(mass, massDs, workspace[0], workInt, bkgBdDsPi[i*2+j],
                                                                                     sm[i*2+j], dim, debug ))
                    else:    
                        bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsPi_BKG_MDFitter(mass, massDs, workspace[0], workInt, bkgBdDsPi[i*2+j],
                                                                                       sm[i*2+j], dim, debug ))
        
    ###------------------------------------------------------------------------------------------------------------------------------------### 
          ###---------------------------------   Create the total PDF in Bs mass, Ds mass, PIDK --------------------------------------###  
    ###------------------------------------------------------------------------------------------------------------------------------------###  

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
        
    ###------------------------------------------------------------------------------------------------------------------------------------###    
          ###--------------------------------------------  Instantiate and run the fitter  -------------------------------------------###  
    ###------------------------------------------------------------------------------------------------------------------------------------###

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
    fitter.fit(True, RooFit.Extended(),  RooFit.Verbose(False)) #, RooFit.InitialHesse(True))
    result = fitter.getFitResult()
    result.Print("v")
    floatpar = result.floatParsFinal()

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
        
    fitter.printYieldsInRange( '*Evts', mVar , 5320, 5420 )    
    if plot_fitted :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData ( options.wsname )

    #print nSig[0].getVal(), nSig[0].getErrorLo(), nSig[0].getErrorHi()    
    if toys:
        AllSig = [0,0]
        AllDPi = [0,0]                                                                                                                                      
        AllLcPi = [0,0]
        AllLMPi = [0,0]
        AllCombo = [0,0]
        AllDsK   = [0,0]

        for i in range(0,bound):
            print sm[i]
            nameSig = TString("nSig")+t+sm[i]+t+TString("Evts")
            nameCombBkg = TString("nCombBkg_")+sm[i]+t+evts
            nameBs2DsDsstPiRho = TString("nBs2DsDsstPiRho_")+sm[i]+t+evts
            nameLb2LcK = TString("nLb2LcPi_")+sm[i]+t+evts
            nameBd2DK = TString("nBd2DPi_")+sm[i]+t+evts
            nameBs2DsK = TString("nBs2DsK_")+sm[i]+t+evts


            AllSig[0]   += countSig[i]
            AllSig[1]   += floatpar.find(nameSig.Data()).getValV()
            AllDPi[0]   += countBDPi[i]
            AllDPi[1]   += myconfigfile["BdDPiEvents"][i]
            AllLcPi[0]   += countLcPi[i]
            AllLcPi[1]   += myconfigfile["LbLcPiEvents"][i]
            AllDsK[0]   += countDsK[i]
            AllDsK[1]   += myconfigfile["BsDsKEvents"][i]
            AllLMPi[0]  += countRhoPi[i]+countBDsPi[i]
            AllLMPi[1]  += floatpar.find(nameBs2DsDsstPiRho.Data()).getValV()
            AllCombo[0] += countCombo[i]
            AllCombo[1] += floatpar.find(nameCombBkg.Data()).getValV()
            
            print "Number of %s signal events: generated %d, fitted %d"%(m[i], countSig[i], floatpar.find(nameSig.Data()).getValV())
            print "Number of %s B->DPi events: generated %d, fitted %d"%(m[i],countBDPi[i], myconfigfile["BdDPiEvents"][i]) 
            print "Number of %s Lb->LcPi events: generated %d, fitted %d"%(m[i],countLcPi[i],myconfigfile["LbLcPiEvents"][i])
            print "Number of %s Bs->DsK events: generated %d, fitted %d"%(m[i],countDsK[i],myconfigfile["BsDsKEvents"][i])
            print "Number of %s Bs->DsstPi, DsRho events: generated %d, fitted %d"%(m[i],countRhoPi[i]+countBDsPi[i],
                                                                                    floatpar.find(nameBs2DsDsstPiRho.Data()).getValV() )
            print "Number of %s Combinatorial events: generated %d, fitted %d"%(m[i],countCombo[i],floatpar.find(nameCombBkg.Data()).getValV())
            print "Number of events: ",nEntries[i]

        print "Number of all signal events: generated %d, fitted %d"%(AllSig[0], AllSig[1])
        print "Number of all B->DPi events: generated %d, fitted %d"%(AllDPi[0],AllDPi[1])  
        print "Number of all Lb->LcPi events: generated %d, fitted %d"%(AllLcPi[0],AllLcPi[1])
        print "Number of all Bs->DsK events: generated %d, fitted %d"%(AllDsK[0],AllDsK[1])
        print "Number of all Bs->DsstPi, DsRho events: generated %d, fitted %d"%(AllLMPi[0],AllLMPi[1] )
        print "Number of all Combinatorial events: generated %d, fitted %d"%(AllCombo[0],AllCombo[1])
    

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
                   default = 'lab0_TAGDECISION_OS',
                   help = 'set observable '
                   )
parser.add_option( '--tagomegavar',
                   dest = 'tagomegavar',
                   default = 'lab0_TAGOMEGA_OS',
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

#parser.add_option( '--fitsignal',
#                   dest = 'fitSig',
#                   default = 'no',
#                   help = 'fit signal, yes or no'
#                   )

parser.add_option( '--tagTool',
                   dest = 'tagTool',
                   action = 'store_true',
                   default = False,
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
parser.add_option( '--dim',
                   dest = 'dim',
                   default = 3)


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
                              options.mode, options.sweight, 
                              options.fileNameAll, options.fileNameToys, options.workName,
                              options.logoutputname,options.tagTool, options.configName, options.wider, options.merge, options.dim)

# -----------------------------------------------------------------------------
