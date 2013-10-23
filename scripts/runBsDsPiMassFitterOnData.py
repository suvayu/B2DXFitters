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

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def runBsDsKMassFitterOnData( debug, sample, mVar, tVar, tagVar, tagOmegaVar, idVar, mode, sweight, yieldBdDPi, fitBdLow,
                              fileNameAll, workName,logoutputname,tagTool, configName, merge ) :

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
    
    obsTS = TString(mVar)
    mass        = GeneralUtils.GetObservable(workspace[0],obsTS, debug)
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
        observables = RooArgSet( mass,tvar,tagvar,tagomegavar,idvar )
    else:
        observables =  RooArgSet( mass,tagsskaonvar,tagosmuonvar,tagoselectronvar,tagoskaonvar,tagvtxchargevar, pvar, ptvar)
        
    sampleMC = [TString("up"),TString("down")]

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
        if mode == "all" :
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
                
                    
            for i in range(0,3):
                for j in range(0,2):
                    sm.append(s[j]+t+m[i])
                    if debug:
                        print "%s"%(sm[i*2+j])
                    sam.defineType(sm[i*2+j].Data())
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
        
        if mode == "all":
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
    sigEPDF = []
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
                            
    s1 = RooRealVar( "Signal_sigma1", "Signal_sigma1", sigma1, 5., 50 )
    s2 = RooRealVar( "Signal_sigma2", "Signal_sigma2", sigma2, 5., 50 )
    r1 = RooRealVar( "ratio1", "ratio1", ratio1 )
    r2 = RooRealVar( "ratio2", "ratio2", ratio2 )
    mn = RooRealVar( "Signal_mean", "Signal_mean", mean, 5100, 5600, "MeV/c^{2}")    
                                        
    for i in range(0,bound):
        nSigEvts.append(0.4*nEntries[i])
        name = TString("nSig")+t+sm[i]+t+TString("Evts")
        nSig.append(RooRealVar( name.Data(), name.Data(), nSigEvts[i], 0., nEntries[i] ))
        sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_fix(mass,mn,s1,alpha1,n1,s2,alpha2,n2,frac,nSig[i],sm[i].Data(),bName,debug))
        name3 = TString("SigEPDF")+t+sm[i]
        sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigPDF[i], nSig[i]))
    # Create the background PDF in mass
    
    nCombBkgEvts = []
    nPiRhoEvts = []
    nLamEvts = []

    for i in range(0,bound):
        nCombBkgEvts.append(0.2*nEntries[i])           # combinatorial background events
        nPiRhoEvts.append(0.4*nEntries[i])             # Bs->DsstPi, Bs->DsRho,  
        nLamEvts.append(0.2*nEntries[i])               # Lb->LcPi

    evts = TString("Evts")
    nCombBkg = []
    nBs2DsDsstPiRho = []
    nBd2DPi = []
    nLb2LcPi = []
    nBs2DsK  = []
    nBd2DsPi = []
    nBd2DsstPi = []

    nBd2DRho = []
    nBd2DstPi = []
    
    bkgBdDsPi = []
    
    width1 = RooFormulaVar("BdDsX_sigma1" , "BdDsX_sigma1",'@0*@1', RooArgList(s1,r1))
    width2 = RooFormulaVar("BdDsX_sigma2" , "BdDsX_sigma2",'@0*@1', RooArgList(s2,r2))
    shift = 5369.600-5279.400
    meanBdDsPi =  RooFormulaVar("BdDsX_mean" , "BdDsX_mean",'@0-86.6', RooArgList(mn))

    cB1Var = []
    cB2Var = []
    fracComb = []
    j = 0
              
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
        
    for i in range(0,bound):
        nameCombBkg = TString("nCombBkg_")+sm[i]+t+evts
        nCombBkg.append(RooRealVar( nameCombBkg.Data()  , nameCombBkg.Data() , nCombBkgEvts[i] , 0. , nEntries[i] ))

        nameBs2DsDsstPiRho = TString("nBs2DsDsstPiRho_")+sm[i]+t+evts
        nBs2DsDsstPiRho.append(RooRealVar( nameBs2DsDsstPiRho.Data(), nameBs2DsDsstPiRho.Data(), nPiRhoEvts[i], 0. , nEntries[i] ))

        if merge:
            inBd2DPi = myconfigfile["BdDPiEvents"][2*i]+myconfigfile["BdDPiEvents"][2*i+1]
            assumedSig = myconfigfile["assumedSig"][i*2]+ myconfigfile["assumedSig"][i*2+1]
        else:
            inBd2DPi = myconfigfile["BdDPiEvents"][i]
            assumedSig = myconfigfile["assumedSig"][i]
                                                                                                                                        
        nameBd2DPi = TString("nBd2DPi_")+sm[i]+t+evts
        if (sm[i].Contains("kkpi") == true or sm[i].Contains("kpipi") == true) :
            if (yieldBdDPi == "yes"):                
                nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),
                                           inBd2DPi,
                                           inBd2DPi*0.80,
                                           inBd2DPi*1.20))
            elif( yieldBdDPi == "constr"):
                nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(), inBd2DPi ))
            else:
                nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),
                                           inBd2DPi ,
                                           0.,
                                           nEntries[i]))
            
        else:    
            nBd2DPi.append(RooRealVar( nameBd2DPi.Data(), nameBd2DPi.Data(),  0. ))
            
        nameLb2LcPi = TString("nLb2LcPi_")+sm[i]+t+evts
        if (sm[i].Contains("kkpi") == true) :
            nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), nLamEvts[i], 0. , nEntries[i]/3 ))
        else:
            nLb2LcPi.append(RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), 0 ))

        nameBs2DsK = TString("nBs2DsK_")+sm[i]+t+evts    
        nBs2DsK.append(RooRealVar( nameBs2DsK.Data(), nameBs2DsK.Data(), 0.0))
        
        nameBd2DsPi = TString("nBd2DsPi_")+sm[i]+t+evts
        nBd2DsPi.append(RooRealVar(nameBd2DsPi.Data() , nameBd2DsPi.Data(),assumedSig*myconfigfile["nBd2DsPi"]))

        nameBd2DsstPi = TString("nBd2DsstPi_")+sm[i]+t+evts
        nameBd2DstPi = TString("nBd2DstPi_")+sm[i]+t+evts
        nameBd2DRho = TString("nBd2DRho_")+sm[i]+t+evts

        if fitBdLow:            
            nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(),assumedSig*myconfigfile["nBd2DsstPi"]))
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(),assumedSig*myconfigfile["nBd2DstPi"]))
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(),assumedSig*myconfigfile["nBd2DRho"]))
        else:
            nBd2DsstPi.append(RooRealVar(nameBd2DsstPi.Data() , nameBd2DsstPi.Data(), 0.0))
            nBd2DstPi.append(RooRealVar(nameBd2DstPi.Data() , nameBd2DstPi.Data(), 0.0))
            nBd2DRho.append(RooRealVar(nameBd2DRho.Data() , nameBd2DRho.Data(), 0.0))
            
                
        bkgBdDsPi.append(Bs2Dsh2011TDAnaModels.buildBdDsX(mass,meanBdDsPi,width1,alpha1,n1,width2,alpha2,n2,frac,TString("Bd2DsPi"), debug))        

        name = TString("CombBkg_slope_Bs1_")+m[j]
        cB1Var.append(RooRealVar(name.Data(), name.Data(), -0.001, -0.1, 0.0))

        name = TString("CombBkg_slope_Bs2_")+m[j]
        cB2Var.append(RooRealVar(name.Data(), name.Data(), 0.0)) #-0.01, -0.1, 0.0))

        name = TString("CombBkg_fracComb_")+m[j]
        fracComb.append(RooRealVar(name.Data(), name.Data(), 0.5, 0.0, 1.0))
                
        
        if merge:
            j=j+1
        else:
            if i == 1 or i == 3:
                j=j+1
                                                
     
        #---------------------------------------------------------------------------------------------------------------------------#                

    #shared variable:
    # Group 1: Bs->DsstPi, Bs->DsRho

    g1_f1              = RooRealVar( "g1_f1_frac","g1_f1_frac", 0.893, 0, 1)
    g1_f2              = RooRealVar( "g1_f2_frac","g1_f2_frac", 0.093, 0, 1)
               
    bkgPDF = []

    if (mode == "all" and ( sample == "up" or sample == "down")):
        for i in range(0,5):
            bkgPDF.append(Bs2Dsh2011TDAnaModels.buildBsDsPi_sim(mass, workspace[0],
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
                                                                cB1Var[i],
                                                                cB2Var[i],
                                                                fracComb[i],
                                                                sm[i],
                                                                lumRatio,
                                                                toys, debug ))
    else:
        if merge:
            for i in range(0,bound):
                bkgPDF.append(Bs2Dsh2011TDAnaModels.buildBsDsPi_sim(mass, workspace[0],
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
                                                                    cB1Var[i],
                                                                    cB2Var[i],
                                                                    fracComb[i],
                                                                    sm[i],
                                                                    lumRatio,
                                                                    toys, debug ))
        else:
            for i in range(0,ranmode):
                for j in range (0,ransample):
                    if debug:
                        print "i %s, j %s"%(i,j)
                        print "sample: %s, sm: %s, name: %s"%(s[j],sm[i*2+j],nCombBkg[i*2+j])
                        bkgPDF.append(Bs2Dsh2011TDAnaModels.buildBsDsPi_sim(mass, workspace[0],
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
                                                                            cB1Var[i*2+j],
                                                                            cB2Var[i*2+j],
                                                                            fracComb[i*2+j],
                                                                            sm[i*2+j],
                                                                            lumRatio,
                                                                            toys, debug ))
                        
                        
                        
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

parser.add_option( '--fitBdLow',
                   dest = 'fitBdLow',
                   action = 'store_true',
                   default = False,
                   help = 'fit BDRho, BDstPi, BDsstPi'
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

parser.add_option( '--workName',
                   dest = 'workName',
                   default = 'workspace',
                   help = 'name of the workspace'
                   )   
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsPiConfigForNominalMassFit')

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
        
    runBsDsKMassFitterOnData( options.debug,  options.sample , options.mvar, options.tvar, \
                              options.tagvar, options.tagomegavar, options.idvar,\
                              options.mode, options.sweight, options.yieldBdDPi, options.fitBdLow,
                              options.fileNameAll, options.workName,options.logoutputname,options.tagTool, options.configName,
                              options.merge)

# -----------------------------------------------------------------------------
