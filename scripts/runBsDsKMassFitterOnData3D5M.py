
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
import B2DXFitters
import ROOT
from B2DXFitters import *
from ROOT import *
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc
gROOT.SetBatch()

# MISCELLANEOUS
bName = 'Bs'
dName = 'Ds'
#------------------------------------------------------------------------------
def runBsDsKMassFitterOnData( debug, sample, mVar, mdVar, tVar, terrVar, tagVar, tagOmegaVar, idVar, mode,
                              sweight,  fileNameAll, fileNameToys, workName, configName, wide, dim, merge ) :


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

    config = TString("../data/")+TString(configName)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)
    
    MDSettings.SetMassBVar(TString(mVar))
    MDSettings.SetMassDVar(TString(mdVar))
    MDSettings.SetTimeVar(TString(tVar))
    MDSettings.SetTerrVar(TString(terrVar))
    MDSettings.SetIDVar(TString(idVar))
        
    if merge:
        if sample == "up" or sample == "down":
            print "You cannot use option --merge with sample: up or down"
            exit(0)

    workspace = []
    workspace.append(GeneralUtils.LoadWorkspace(TString(fileNameAll),workNameTS, debug))
    #workData = GeneralUtils.LoadWorkspace(TString("work_dsk_data.root"),workNameTS, debug)
    workData = workspace[0]
     
    obsTS = TString(mVar)
    
    if (not toys ):
        mass        = GeneralUtils.GetObservable(workData,obsTS, debug)
        massDs      = GeneralUtils.GetObservable(workData,TString(mdVar), debug)
        PIDK        = GeneralUtils.GetObservable(workData,TString("lab1_PIDK"), debug)
        tvar        = GeneralUtils.GetObservable(workData,TString(tVar), debug)
        terrvar     = GeneralUtils.GetObservable(workData,TString(terrVar), debug)
        idvar       = GeneralUtils.GetCategory(workData,TString(idVar), debug)
        nTrvar      = GeneralUtils.GetObservable(workData,TString("nTracks"), debug)
        ptvar       = GeneralUtils.GetObservable(workData,TString("lab1_PT"), debug)
                
    else:
        mass        = GeneralUtils.GetObservable(workspaceToys,obsTS, debug)
        massDs      = GeneralUtils.GetObservable(workspaceToys,TString(mdVar), debug)
        PIDK        = GeneralUtils.GetObservable(workspaceToys,TString("lab1_PIDK"), debug)
        tvar        = GeneralUtils.GetObservable(workspaceToys,TString(tVar), debug)
        terrvar     = GeneralUtils.GetObservable(workspaceToys,TString(terrVar), debug)
        tagomegavar = GeneralUtils.GetObservable(workspaceToys,TString("tagOmegaComb"), debug)
        tagvar      = GeneralUtils.GetCategory(workspaceToys,TString("tagDecComb"), debug)
        idvar       = GeneralUtils.GetCategory(workspaceToys,TString(idVar), debug)
        trueidvar   = GeneralUtils.GetObservable(workspaceToys,TString("lab0_TRUEID"), debug)
        
                
    observables = RooArgSet( mass,massDs, PIDK, tvar, terrvar, idvar )
    if toys :
        observables.add(trueidvar)
        observables.add(tagvar)
        observables.add(tagomegavar)
    else:
        observables.add(nTrvar)
        observables.add(ptvar)

    if not toys:
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
                observables.add(tagOmegaVar[i])
                nameCalib = MDSettings.GetTagOmegaVar(i) + TString("_calib")
                tagOmegaVarCalib.append(GeneralUtils.GetObservable(workData, nameCalib, debug))
                observables.add(tagOmegaVarCalib[i])
                
        tagDecCombName = TString("tagDecComb")
        tagDecComb = GeneralUtils.GetCategory(workData, tagDecCombName, debug)
        tagOmegaCombName= TString("tagOmegaComb")
        tagOmegaComb = GeneralUtils.GetObservable(workData, tagOmegaCombName, debug)
        
        observables.add(tagDecComb)
        observables.add(tagOmegaComb)
                                                                                                 
 ###------------------------------------------------------------------------------------------------------------------------------------###
    ###-------------------------------------------------   Read data sets   --------------------------------------------------------###
 ###------------------------------------------------------------------------------------------------------------------------------------###   

    modeTS = TString(mode)
    sampleTS = TString(sample)
        
    datasetTS = TString("dataSetBsDsK_")
    sam = RooCategory("sample","sample")
    dim = int(dim)
    sm = []
    data = []
    nEntries = []
    t = TString('_')

    ### Obtain data set ###
    if toys:
        if mode == "all":
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
        countBDK   = [0,0,0,0,0]
        countBDsK  = [0,0,0,0,0]
        countDsPi  = [0,0,0,0,0]
        countLcK   = [0,0,0,0,0]
        countKstK  = [0,0,0,0,0]
        countRhoPi = [0,0,0,0,0]
        countDsp   = [0,0,0,0,0]
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
                        countBDK[j] += 1
                    if abs(trueid.getValV(obs2)-3.0) < 0.5 :
                        countBDsK[j] += 1
                    if abs(trueid.getValV(obs2)-4.0) < 0.5 :
                        countDsPi[j] += 1
                    if abs(trueid.getValV(obs2)-5.0) < 0.5 :
                        countLcK[j] += 1
                    if abs(trueid.getValV(obs2)-6.0) < 0.5 :
                        countDsp[j] += 1
                    if abs(trueid.getValV(obs2)-10.0) < 0.5 :
                        countCombo[j] += 1
                    if abs(trueid.getValV(obs2)-7.0) < 0.5 :
                        countKstK[j] += 1
                    if abs(trueid.getValV(obs2)-8.0) < 0.5 :
                        countRhoPi[j] += 1
                        

                        
    else:    
        combData =  GeneralUtils.GetDataSet(workspace[0], observables, sam, datasetTS, sampleTS, modeTS, merge, debug )
        sm = GeneralUtils.GetSampleMode(sampleTS, modeTS, merge, debug )
        s = GeneralUtils.GetSample(sampleTS, debug)
        m = GeneralUtils.GetMode(modeTS,debug)
        nEntries = GeneralUtils.GetEntriesCombData(workspace[0], datasetTS, sampleTS, modeTS, merge, debug ) 
                
    ran = sm.__len__()
    ranmode = m.__len__()
    ransample = s.__len__()
    if merge:
        bound = ranmode
    else:
        bound = ran
    print "bound: ",bound    
    
    ###------------------------------------------------------------------------------------------------------------------------------------###
          ###-------------------------   Create the signal PDF in Bs mass, Ds mass, PIDK   ------------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------------###

    workInt = RooWorkspace("workInt","workInt")
    nSig = []
    sigPDF = []
    sigDsPDF = []
    nSigEvts = []

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

    for i in range(0,bound):
        if wide:
            nSigEvts.append(0.4*nEntries[i])
        else:
            nSigEvts.append(0.4*nEntries[i])

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

        if dim > 1:
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
            getattr(workInt,'import')(sigDsPDF[i])
    #exit(0)
    nSigdG = []
    sigPIDKPDF = []
    sigProdPDF = []
    sigEPDF = []
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
    getattr(workInt,'import')(lumRatio)
    
    if dim > 2 :
        for i in range(0,bound):
            namePID = TString("Bs2DsK_")+sm[i]
            k = bound%2
            sigPIDKPDF.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace[0], namePID, s[k], lumRatio, true, debug))
            getattr(workInt,'import')(sigPIDKPDF[i])

    for i in range(0,bound):
        name2 = TString("SigProdPDF")+t+sm[i]
        name3 = TString("SigEPDF")+t+sm[i]
        if dim == 1:
            print "Signal 1D"
            sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigPDF[i], nSig[i]))
        elif dim == 2:
            print "Signal 2D"
            sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDsPDF[i])))
            sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigProdPDF[i], nSig[i]))
        elif dim == 3:
            print "Signal 3D"
            sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDsPDF[i],sigPIDKPDF[i])))
            sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigProdPDF[i], nSig[i]))
        else:
            print "[INFO] Wrong number of fitting dimensions: ",dim
            exit(0)

    ###------------------------------------------------------------------------------------------------------------------------------------###
        ###-------------------------------   Create the backgrounds PDF in Bs mass, Ds mass, PIDK --------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------------###
    
    nCombBkgEvts = []
    nKEvts = []
    for i in range(0,bound):
        nCombBkgEvts.append(0.5*nEntries[i])           # combinatorial background events
        nKEvts.append(0.3*nEntries[i])                 # Bs->DsK, Bs->Ds*K, Bs->DsK*, Bs->Ds*K* together
               
    evts = TString("Evts")
    nCombBkg = []
    nBsLb2DsDsstPPiRho = []
    nBs2DsDssKKst = []
    nBd2DK = []
    nBd2DPi = []
    nLb2LcK = []
    nLb2LcPi = [] 
    
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
        nameBsLb2DsDsstPPiRho = TString("nBsLb2DsDsstPPiRho_")+sm[i]+t+evts
        nameLb2LcK = TString("nLb2LcK_")+sm[i]+t+evts
        nameLb2LcPi = TString("nLb2LcPi_")+sm[i]+t+evts
        nameBs2DsDssKKst = TString("nBs2DsDsstKKst_")+sm[i]+t+evts
        nameBd2DK = TString("nBd2DK_")+sm[i]+t+evts
        nameBd2DPi = TString("nBd2DPi_")+sm[i]+t+evts

        if merge: 
            inBsLb2DsDsstPPiRhoEvts = myconfigfile["nBs2DsDsstPiRhoEvts"][i*2]+myconfigfile["nBs2DsDsstPiRhoEvts"][i*2+1]
            inLbLcKEvts = myconfigfile["nLbLcKEvts"][i*2] + myconfigfile["nLbLcKEvts"][i*2+1]
            inLbLcPiEvts = myconfigfile["nLbLcPiEvts"][i*2] + myconfigfile["nLbLcPiEvts"][i*2+1]
            inBdDKEvts = myconfigfile["nBdDKEvts"][i*2]+myconfigfile["nBdDKEvts"][i*2+1]
            inBdDPiEvts = myconfigfile["nBdDPiEvts"][i*2]+myconfigfile["nBdDPiEvts"][i*2+1]
        else    :
            inBsLb2DsDsstPPiRhoEvts = myconfigfile["nBs2DsDsstPiRhoEvts"][i]
            inLbLcKEvts = myconfigfile["nLbLcKEvts"][i]
            inLbLcPiEvts = myconfigfile["nLbLcPiEvts"][i]
            inBdDKEvts = myconfigfile["nBdDKEvts"][i]
            inBdDPiEvts = myconfigfile["nBdDPiEvts"][i]

        nCombBkg.append(RooRealVar( nameCombBkg.Data()  , nameCombBkg.Data() , nCombBkgEvts[i] , 0. , nEntries[i] ))
        nLb2LcK.append(RooRealVar( nameLb2LcK.Data(), nameLb2LcK.Data(), inLbLcKEvts)) 
        nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), inLbLcPiEvts))
        nBd2DK.append(RooRealVar( nameBd2DK.Data(), nameBd2DK.Data(), inBdDKEvts))        
        nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(), inBdDPiEvts))

        if wide:
            nBsLb2DsDsstPPiRho.append(RooRealVar( nameBsLb2DsDsstPPiRho.Data(), nameBsLb2DsDsstPPiRho.Data(),
                                                  inBsLb2DsDsstPPiRhoEvts*3,
                                                  inBsLb2DsDsstPPiRhoEvts-inBsLb2DsDsstPPiRhoEvts*1.0,
                                                  inBsLb2DsDsstPPiRhoEvts+inBsLb2DsDsstPPiRhoEvts*5.0 ))
            nBs2DsDssKKst.append(RooRealVar( nameBs2DsDssKKst.Data(), nameBs2DsDssKKst.Data(), nKEvts[i] , 0. , nEntries[i]/2 ))
        else:
            nBsLb2DsDsstPPiRho.append(RooRealVar( nameBsLb2DsDsstPPiRho.Data(), nameBsLb2DsDsstPPiRho.Data(),
                                                  inBsLb2DsDsstPPiRhoEvts/2, 0.0, inBsLb2DsDsstPPiRhoEvts*3.0))
            nBs2DsDssKKst.append(RooRealVar( nameBs2DsDssKKst.Data(), nameBs2DsDssKKst.Data(), inBsLb2DsDsstPPiRhoEvts/4, 0.0, inBsLb2DsDsstPPiRhoEvts/2 ))

        getattr(workInt,'import')(nCombBkg[i])
        getattr(workInt,'import')(nLb2LcK[i])
        getattr(workInt,'import')(nLb2LcPi[i])
        getattr(workInt,'import')(nBd2DPi[i])
        getattr(workInt,'import')(nBd2DK[i])
        getattr(workInt,'import')(nBsLb2DsDsstPPiRho[i])
        getattr(workInt,'import')(nBs2DsDssKKst[i])

        al1 = myconfigfile["alpha1_bc"][i] 
        al2 = myconfigfile["alpha2_bc"][i] 
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
        
        getattr(workInt,'import')(cBVar[i])
        getattr(workInt,'import')(cDVar[i])
        getattr(workInt,'import')(fracComb[i])
        
        if merge:
            j=j+1
        else:
            if i == 1 or i == 3:
                j=j+1

        #if toys:
        #    cDVar[i].setConstant()
        #    cBVar[i].setConstant()
        #    fracComb[i].setConstant()
                
        #---------------------------------------------------------------------------------------------------------------------------#                

    #shared variable:
    # Group 1: Bd->DsK, Bs->DsK*
    g1_f1              = RooRealVar( "g1_f1_frac","g1_f1_frac", 1.0)
    getattr(workInt,'import')(g1_f1)

    # Group 2 Bs->DsPi, Bs->DsstPi, Bs->DsRho: (g2_f1)*DsPi + (1-g2_f1)*[ (g2_f2)*DsstPi+(1-g2_f2)*DsRho]
    g2_f1              = RooRealVar( "g2_f1_frac","g2_f1_frac", 0.5, 0, 1) #myconfigfile["g2_f1"],0,1)
    g2_f2              = RooRealVar( "g2_f2_frac","g2_f2_frac", 0.5) #, 0, 1) #myconfigfile["g2_f2"],0,1)
    getattr(workInt,'import')(g2_f1)
    getattr(workInt,'import')(g2_f2)

    # Group 3: g3_f1*Lb->Dsp + (1-g3_f1)Lb->Ds*p
    g3_f1              = RooRealVar( "g3_f1_frac","g3_f1_frac", 0.75) #, 0.5, 1.0)
    getattr(workInt,'import')(g3_f1)

    # PIDcomponets
    g4_f1              = RooRealVar( "PID1_frac","PID1_frac", 0.6, 0.0, 1.0)
    g4_f2              = RooRealVar( "PID2_frac","PID2_frac", 0.6, 0.0, 1.0)
    getattr(workInt,'import')(g4_f1)
    getattr(workInt,'import')(g4_f2)

    # Global fraction: (g5_f1)*Bs2DsDsstPiRho + (1-g5_f1)*Lb2DsDsstp
    g5_f1              = RooRealVar( "g5_f1_frac","g5_f1_frac", 0.5, 0, 1);
    getattr(workInt,'import')(g5_f1)
            
    
    bkgPDF = []
    workInt.Print("v")

    if (mode == "all" and ( sample == "up" or sample == "down")):
        for i in range(0,3):
            bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsK_BKG_MDFitter(mass, massDs, workspace[0], workInt, bkgBdDsK[i], sm[i], dim, debug ))
    else:
        if merge:
            for i in range(0,bound):
                bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsK_BKG_MDFitter(mass, massDs, workspace[0], workInt, bkgBdDsK[i], sm[i], dim, debug ))
        else:
            for i in range(0,ranmode):
                for j in range (0,ransample):
                    bkgPDF.append(Bs2Dsh2011TDAnaModels.build_Bs2DsK_BKG_MDFitter(mass, massDs, workspace[0], workInt, 
                                                                                  bkgBdDsK[i*2+j], sm[i*2+j], dim, debug ))
                    
        
        
    ###------------------------------------------------------------------------------------------------------------------------------------###
          ###---------------------------------   Create the total PDF in Bs mass, Ds mass, PIDK --------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------------###
          

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

    ###------------------------------------------------------------------------------------------------------------------------------------###
          ###--------------------------------------------  Instantiate and run the fitter  -------------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------------###
    #exit(0)

    fitter = FitMeTool( debug )
    fitter.setObservables( observables )
    fitter.setModelPDF( totPDF )
    fitter.setData(combData) 
    
    fitter.fit(True, RooFit.Extended(), RooFit.Verbose(False)) #RooFit.SumW2Error(True), RooFit.Verbose(False))
    result = fitter.getFitResult()
    result.Print("v")
    floatpar = result.floatParsFinal()

    if ( not toys):
        BDTGTS = GeneralUtils.CheckBDTGBin(confTS, debug)
        name = TString("./sWeights_BsDsK_")+modeTS+TString("_")+sampleTS+TString("_")+BDTGTS+TString(".root")
    else:
        name = TString(options.sweightoutputname)
     
    if (sweight):
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(RooFit.Eval)
        fitter.savesWeights(mVar, combData, name)
        RooMsgService.instance().reset() 
                                                
    fitter.printYieldsInRange( '*Evts', obsTS.Data() , 5320, 5420 )

    if toys:
        AllSig = [0,0]
        AllDK = [0,0]
        AllLMK = [0,0]
        #AllDsPi = [0,0]
        AllLcK = [0,0]
        AllDsp = [0,0]
        AllLMPi = [0,0]
        AllCombo = [0,0]
        
        for i in range(0,bound):
            print sm[i]
            nameSig = TString("nSig")+t+sm[i]+t+TString("Evts")
            nameCombBkg = TString("nCombBkg_")+sm[i]+t+evts
            nameBs2DsDsstPiRho = TString("nBsLb2DsDsstPPiRho_")+sm[i]+t+evts
            #nameBs2DsPi = TString("nBs2DsPi_")+sm[i]+t+evts
            nameLb2LcK = TString("nLb2LcK_")+sm[i]+t+evts
            nameBs2DsDssKKst = TString("nBs2DsDsstKKst_")+sm[i]+t+evts
            nameLb2DsDsstp = TString("nLb2DsDsstp_")+sm[i]+t+evts
            nameBd2DK = TString("nBd2DK_")+sm[i]+t+evts

            AllSig[0]   += countSig[i]
            AllSig[1]   += floatpar.find(nameSig.Data()).getValV()
            AllDK[0]    += countBDK[i]
            AllDK[1]    += myconfigfile["nBdDKEvts"][i*2]+myconfigfile["nBdDKEvts"][i*2+1]+myconfigfile["nBdDPiEvts"][i*2]+myconfigfile["nBdDPiEvts"][i*2+1]
            AllLMK[0]   += countBDsK[i]+countKstK[i]
            AllLMK[1]   += floatpar.find(nameBs2DsDssKKst.Data()).getVal()
            #AllDsPi[0]  += countDsPi[i]
            #AllDsPi[1]  += floatpar.find(nameBs2DsPi.Data()).getValV()
            AllLcK[0]   += countLcK[i]
            AllLcK[1]   += myconfigfile["nLbLcKEvts"][i*2] + myconfigfile["nLbLcKEvts"][i*2+1]+myconfigfile["nLbLcPiEvts"][i*2] + myconfigfile["nLbLcPiEvts"][i*2+1]
            #AllDsp[0]   += countDsp[i]
            #AllDsp[1]   += floatpar.find(nameLb2DsDsstp.Data()).getValV()
            AllLMPi[0]  += countRhoPi[i]+countDsPi[i]+countDsp[i]
            AllLMPi[1]  += floatpar.find(nameBs2DsDsstPiRho.Data()).getValV()
            AllCombo[0] += countCombo[i]
            AllCombo[1] += floatpar.find(nameCombBkg.Data()).getValV()
            
            print "Number of %s signal events: generated %d, fitted %d"%(m[i], countSig[i], floatpar.find(nameSig.Data()).getValV())
            print "Number of %s B->DK events: generated %d, fitted %d"%(m[i],countBDK[i], 
                                                                        myconfigfile["nBdDKEvts"][i*2]+myconfigfile["nBdDKEvts"][i*2+1]
                                                                        +myconfigfile["nBdDPiEvts"][i*2]+myconfigfile["nBdDPiEvts"][i*2+1])
            print "Number of %s Bd->DsK, Bs->DsK* events: generated %d, fitted %d"%(m[i],countBDsK[i]+countKstK[i],
                                                                                    floatpar.find(nameBs2DsDssKKst.Data()).getValV())
            #print "Number of %s Bs->DsPi events: generated %d, fitted %d"%(m[i],countDsPi[i], floatpar.find(nameBs2DsPi.Data()).getValV())
            print "Number of %s Lb->LcK events: generated %d, fitted %d"%(m[i],countLcK[i],
                                                                          myconfigfile["nLbLcKEvts"][i*2] + myconfigfile["nLbLcKEvts"][i*2+1]
                                                                          +myconfigfile["nLbLcPiEvts"][i*2] + myconfigfile["nLbLcPiEvts"][i*2+1])
            #print "Number of %s Lb->Dsp,Dsstp events: generated %d, fitted %d"%(m[i],countDsp[i], floatpar.find(nameLb2DsDsstp.Data()).getValV())
            print "Number of %s Bs->DsstPi, DsRho events: generated %d, fitted %d"%(m[i],countRhoPi[i]+countDsPi[i]+countDsp[i],
                                                                                    floatpar.find(nameBs2DsDsstPiRho.Data()).getValV() )
            print "Number of %s Combinatorial events: generated %d, fitted %d"%(m[i],countCombo[i],floatpar.find(nameCombBkg.Data()).getValV())
            print "Number of events: ",nEntries[i]

        print "Number of all signal events: generated %d, fitted %d"%(AllSig[0], AllSig[1])
        print "Number of all B->DK events: generated %d, fitted %d"%(AllDK[0],AllDK[1])
        print "Number of all Bd->DsK, Bs->DsK* events: generated %d, fitted %d"%(AllLMK[0],AllLMK[1])
        #print "Number of all Bs->DsPi events: generated %d, fitted %d"%(AllDsPi[0],AllDsPi[1])
        print "Number of all Lb->LcK events: generated %d, fitted %d"%(AllLcK[0],AllLcK[1])
        #print "Number of all Lb->Dsp,Dsstp events: generated %d, fitted %d"%(AllDsp[0],AllDsp[1])
        print "Number of all Bs->DsstPi, DsRho events: generated %d, fitted %d"%(AllLMPi[0],AllLMPi[1] )
        print "Number of all Combinatorial events: generated %d, fitted %d"%(AllCombo[0],AllCombo[1])
                   
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
                   help = 'create and save sWeights, choose: yes or no'
                   )

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
    
    runBsDsKMassFitterOnData(   options.debug,  options.sample , options.mvar, options.mdvar, options.tvar, options.terrvar, \
                                options.tagvar, options.tagomegavar, options.idvar,\
                                options.mode, options.sweight, \
                                options.fileNameAll, options.fileNameToys,
                                options.workName, options.configName, options.wide, options.dim, options.merge)

# -----------------------------------------------------------------------------
