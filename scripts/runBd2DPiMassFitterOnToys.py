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
#   Author: Vincenzo Battista                                                 #
#   Date  : 04 / 02 / 2015                                                    #
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
#"
import B2DXFitters
import ROOT
from B2DXFitters import *
from ROOT import *
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
import os, sys, gc
from  os.path import exists
from array import array
import copy

from B2DXFitters.WS import WS as WS

gROOT.SetBatch()

# MISCELLANEOUS
bName = 'B'
dName = 'D'

#------------------------------------------------------------------------------
def runBd2DPiMassFitterOnToys( debug, sample, massplot, mode, year, toys,
                               sweight,  fileNameAll, fileNameToys, fileNamePull, workName, configName, wide, dim, merge, fileDataName,
                               nobackground) :
    
    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    config = TString("../data/")+TString(configName)+TString(".py")
    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings",False)

    MDSettings = mdt.getConfig()
    MDSettings.Print("v")
    
    print "=========================================================="
    print "MASS FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="

    configNameTS = TString(configName)
    workNameTS = TString(workName)
    yearTS = TString(year)

    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["LumRatio"][year])
    magpol = TString(sample)
    
    if toys:
        print "Toy workspace:"
        workspaceToys = GeneralUtils.LoadWorkspace(TString(fileNameToys),workNameTS, debug)
        workspaceToys.Print("v")
        
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    config = TString("../data/")+TString(configName)+TString(".py")
    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings",False)

    MDSettings = mdt.getConfig()
    MDSettings.Print("v")
        
    if merge:
        if sample == "up" or sample == "down":
            print "You cannot use option --merge with sample: up or down"
            exit(0)

    print "=========================================================="
    print "Getting input workspace"
    print "=========================================================="
    workspace = []
    workspace.append(GeneralUtils.LoadWorkspace(TString(fileNameAll),workNameTS, debug))
    if fileDataName == "":
        workData = workspace[0]
    else:    
        workData = GeneralUtils.LoadWorkspace(TString(fileDataName),workNameTS, debug)

    print "=========================================================="
    print "Getting observables"
    print "=========================================================="
    observables = workspaceToys.allVars()
    observables.add(GeneralUtils.GetCategory(workspaceToys, TString("tagDecComb"), debug))
    observables.add(GeneralUtils.GetCategory(workspaceToys, TString(myconfigfile["BasicVariables"]["BacCharge"]["Name"]), debug)) 
    observables.Print("v")

    mass = observables.find(MDSettings.GetMassBVarOutName().Data())
    mass.Print("v")
    obsTS = TString(mass.GetName())
    massD = NULL
    if dim>1:
        massD = observables.find(MDSettings.GetMassDVarOutName().Data())
        massD.Print("v")
                                                                                                 
 ###------------------------------------------------------------------------------------------------------------------------------------###
    ###-------------------------------------------------   Read data sets   --------------------------------------------------------###
 ###------------------------------------------------------------------------------------------------------------------------------------###   

    print "=========================================================="
    print "Getting dataset"
    print "=========================================================="

    modeTS = TString(mode)
    sampleTS = TString(sample)
        
    datasetTS = TString("dataSetBd2DPi_")
    sam = RooCategory("sample","sample")
    dim = int(dim)
    sm = []
    data = []
    nEntries = []
    t = TString('_')

    ### Obtain data set ###
    if toys:
        if mode == "KPiPi": #The only mode handled for Bd->DPi, at the moment
            s = [TString(sample)]
            m = [TString(mode)]
            for i in range(0,1):
                sm.append(s[0]+t+m[i]) 
                sam.defineType(sm[i].Data())
                print "Dataset name (toys): " + str(datasetTS+sm[i])
                data.append(GeneralUtils.GetDataSet(workspaceToys,datasetTS+sm[i],debug))
                nEntries.append(data[i].numEntries())
                print "nEntries: ", nEntries[i]
                
            combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                  RooFit.Index(sam),
                                  RooFit.Import(sm[0].Data(),data[0]))

            print "Combined data: entries ", combData.numEntries()
                    
    else:
        combData =  GeneralUtils.GetDataSet(workData, observables, sam, datasetTS, sampleTS, modeTS, merge, debug )
        sm = GeneralUtils.GetSampleMode(sampleTS, modeTS, merge, debug )
        s = GeneralUtils.GetSample(sampleTS, debug)
        m = GeneralUtils.GetMode(modeTS,debug)
        nEntries = GeneralUtils.GetEntriesCombData(workData, datasetTS, sampleTS, modeTS, merge, debug ) 
             
    ran = sm.__len__()
    ranmode = m.__len__()
    ransample = s.__len__()
    if merge:
        boundList = copy.deepcopy(m)
        bound = ranmode
    else:
        boundList = copy.deepcopy(sm)
        bound = ran
    if debug:
        print "bound: ", bound    

    for i in range(0,boundList.__len__()):
        boundList[i] = GeneralUtils.GetModeCapital(boundList[i],debug).Data()
        if debug:
            print "boundList: ", boundList[i]
    
    ###------------------------------------------------------------------------------------------------------------------------------------###
          ###-------------------------   Create the signal PDF in B mass, D mass   ------------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------------###

    workInt = RooWorkspace("workInt","workInt")
    
    nSig = []
    sigPDF = []
    sigDPDF = []
    nSigEvts = []

    mn = []
    mnD = []
    s1 = []
    s2 = []
    s1D = []
    s2D = []
    n1 = []
    n2 = []
    n1D = []
    n2D = []
    frac = []
    fracD = []    
    al1 = []
    al2 = []
    al1D = []
    al2D = []

    for i in range(0,bound):

        print "=========================================================="
        print "Creating B mass shape"
        print "Mode ", boundList[i]
        print "Year ", year
        print "=========================================================="

        mn.append(WS(workInt, RooRealVar("DblCBBPDF_%s_mean_%s"%(mass.GetName(),boundList[i]),"mean",myconfigfile["BsSignalShape"]["mean"]["All"], "MeV/c^{2}")))
        s1.append(WS(workInt, RooRealVar("DblCBBPDF_%s_sigma1_%s"%(mass.GetName(),boundList[i]),"sigma1",myconfigfile["BsSignalShape"]["sigma1"][year][boundList[i]], "MeV/c^{2}")))
        s2.append(WS(workInt, RooRealVar("DblCBBPDF_%s_sigma2_%s"%(mass.GetName(),boundList[i]),"sigma2",myconfigfile["BsSignalShape"]["sigma2"][year][boundList[i]], "MeV/c^{2}")))
        al1.append(WS(workInt, RooRealVar("DblCBBPDF_%s_alpha1_%s"%(mass.GetName(),boundList[i]),"alpha1",myconfigfile["BsSignalShape"]["alpha1"][year][boundList[i]])))
        al2.append(WS(workInt, RooRealVar("DblCBBPDF_%s_alpha2_%s"%(mass.GetName(),boundList[i]),"alpha2",myconfigfile["BsSignalShape"]["alpha2"][year][boundList[i]])))
        n1.append(WS(workInt, RooRealVar("DblCBBPDF_%s_n1_%s"%(mass.GetName(),boundList[i]),"n1",myconfigfile["BsSignalShape"]["n1"][year][boundList[i]])))
        n2.append(WS(workInt, RooRealVar("DblCBBPDF_%s_n2_%s"%(mass.GetName(),boundList[i]),"n2",myconfigfile["BsSignalShape"]["n2"][year][boundList[i]])))
        frac.append(WS(workInt, RooRealVar("DblCBBPDF_%s_frac_%s"%(mass.GetName(),boundList[i]),"frac",myconfigfile["BsSignalShape"]["frac"][year][boundList[i]])))

        nSigEvts.append(myconfigfile["Yields"]["Signal"][year][boundList[i]])
        if sampleTS == "up":
            nSigEvts[i]  = nSigEvts[i]*myconfigfile["LumRatio"][year]
        elif sampleTS == "down":
            nSigEvts[i]  = nSigEvts[i]*(1-myconfigfile["LumRatio"][year])
        
        name = TString("nSig")+t+sm[i]+t+TString("Evts")
        nSig.append(RooRealVar( name.Data(), name.Data(), nSigEvts[i], 0.5*nEntries[i], 1.5*nEntries[i] ))

        if debug:
            print "B mass shape parameters:"
            print mn[i].getVal()
            print al1[i].getVal()
            print al2[i].getVal()
            print n1[i].getVal()
            print n2[i].getVal()
            print frac[i].getVal()
            
        sigPDF.append(WS(workInt,Bs2Dsh2011TDAnaModels.buildDoubleCrystalBallPDF(mass,workInt,boundList[i],"DblCBBPDF",False,debug)))

        if dim > 1:

            print "=========================================================="
            print "Creating D mass shape"
            print "Mode ", boundList[i]
            print "Year ", year
            print "=========================================================="

            mnD.append(WS(workInt, RooRealVar("DblCBDPDF_%s_mean_%s"%(massD.GetName(),boundList[i]),"mean",myconfigfile["DsSignalShape"]["mean"]["All"], "MeV/c^{2}")))
            s1D.append(WS(workInt, RooRealVar("DblCBDPDF_%s_sigma1_%s"%(massD.GetName(),boundList[i]),"sigma1",myconfigfile["DsSignalShape"]["sigma1"][year][boundList[i]], "MeV/c^{2}")))
            s2D.append(WS(workInt, RooRealVar("DblCBDPDF_%s_sigma2_%s"%(massD.GetName(),boundList[i]),"sigma2",myconfigfile["DsSignalShape"]["sigma2"][year][boundList[i]], "MeV/c^{2}")))
            al1D.append(WS(workInt, RooRealVar("DblCBDPDF_%s_alpha1_%s"%(massD.GetName(),boundList[i]),"alpha1",myconfigfile["DsSignalShape"]["alpha1"][year][boundList[i]])))
            al2D.append(WS(workInt, RooRealVar("DblCBDPDF_%s_alpha2_%s"%(massD.GetName(),boundList[i]),"alpha2",myconfigfile["DsSignalShape"]["alpha2"][year][boundList[i]])))
            n1D.append(WS(workInt, RooRealVar("DblCBDPDF_%s_n1_%s"%(massD.GetName(),boundList[i]),"n1",myconfigfile["DsSignalShape"]["n1"][year][boundList[i]])))
            n2D.append(WS(workInt, RooRealVar("DblCBDPDF_%s_n2_%s"%(massD.GetName(),boundList[i]),"n2",myconfigfile["DsSignalShape"]["n2"][year][boundList[i]])))
            fracD.append(WS(workInt, RooRealVar("DblCBDPDF_%s_frac_%s"%(massD.GetName(),boundList[i]),"frac",myconfigfile["DsSignalShape"]["frac"][year][boundList[i]])))

            if debug:
                print "D mass shape parameters:"
                print mnD[i].getVal()
                print al1D[i].getVal()
                print al2D[i].getVal()
                print n1D[i].getVal()
                print n2D[i].getVal()
                print fracD[i].getVal()
                
            sigDPDF.append(WS(workInt,Bs2Dsh2011TDAnaModels.buildDoubleCrystalBallPDF(massD,workInt,boundList[i],"DblCBDPDF",False,debug)))
    
    nSigdG = []
    sigPIDKPDF = []
    sigProdPDF = []
    sigEPDF = []
    
    getattr(workInt,'import')(lumRatio)
    
    if dim > 2 : #NOT YET IMPLEMENTED FOR Bd->DPi
        for i in range(0,bound):
            namePID = TString("Bd2DPi_")+sm[i]
            if merge:
                k = bound%2
            else:
                k = 0
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
            sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDPDF[i])))
            sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigProdPDF[i], nSig[i]))
        elif dim == 3:
            print "Signal 3D"
            sigProdPDF.append(RooProdPdf(name2.Data(),name2.Data(),RooArgList(sigPDF[i],sigDPDF[i],sigPIDKPDF[i])))
            sigEPDF.append(RooExtendPdf(name3.Data(),name3.Data(),sigProdPDF[i], nSig[i]))
        else:
            print "[INFO] Wrong number of fitting dimensions: ",dim
            exit(0)

    ###------------------------------------------------------------------------------------------------------------------------------------###
        ###-------------------------------   Create the backgrounds PDF in B mass, D mass --------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------------###

    inComboEvts = []
    inBd2DKEvts = []
    inBs2DsPiEvts = []
    inLb2LcPiEvts = []
    inBd2DRhoEvts = []
    inBd2DstPiEvts = []
    inPeakBkgEvts = []
    inLMBkgEvts = []
               
    evts = TString("Evts")
    nComboBkg = []
    nBd2DK = []
    nBs2DsPi = []
    nLb2LcPi = []
    nBd2DRho = []
    nBd2DstPi = []
    nPeakBkg = []
    nLMBkg = []

    massB_Combo = []
    cBVar = []
    massD_Combo = []
    cDVar = []
    fracDComb = []
    MDFitter_Combo = []
    ComboEPDF = []

    MDFitter_Bd2DK = []
    Bd2DKEPDF = []

    massB_Bs2DsPi = []
    massD_Bs2DsPi = []
    MDFitter_Bs2DsPi = []
    Bs2DsPiEPDF = []

    MDFitter_Lb2LcPi = []
    Lb2LcPiEPDF = []

    massB_Bd2DRho = []
    massD_Bd2DRho = []
    MDFitter_Bd2DRho = []
    Bd2DRhoEPDF = []

    massB_Bd2DstPi = []
    massD_Bd2DstPi = []
    MDFitter_Bd2DstPi = []
    Bd2DstPiEPDF = []

    #f1PeakBkg = []
    #f2PeakBkg = []
    #MDFitter_PeakBkg = []
    #PeakBkgEPDF = []

    #f1LMBkg = []
    #MDFitter_LMBkg = []
    #LMBkgEPDF = []

    pdfList = []
    totPDF = []
    
    for i in range(0,bound):

        nameComboBkg = TString("nComboBkg_")+sm[i]+t+evts
        nameBd2DK = TString("nBd2DK_")+sm[i]+t+evts
        nameBs2DsPi = TString("nBs2DsPi_")+sm[i]+t+evts
        nameLb2LcPi = TString("nLb2LcPi_")+sm[i]+t+evts
        nameBd2DRho = TString("nBd2DRho_")+sm[i]+t+evts
        nameBd2DstPi = TString("nBd2DstPi_")+sm[i]+t+evts
        
        #namef1PeakBkg = TString("f1PeakBkg_")+sm[i]
        #namef2PeakBkg = TString("f2PeakBkg_")+sm[i]
        #namePeakBkg = TString("nPeakBkg_")+sm[i]+t+evts

        #namef1LMBkg = TString("f1LMBkg_")+sm[i]
        #nameLMBkg = TString("nLMBkg_")+sm[i]+t+evts

        inComboEvts.append(myconfigfile["Yields"]["Combo"][year][boundList[i]])
        inBd2DKEvts.append(myconfigfile["Yields"]["Bd2DK"][year][boundList[i]])
        inBs2DsPiEvts.append(myconfigfile["Yields"]["Bs2DsPi"][year][boundList[i]])
        inLb2LcPiEvts.append(myconfigfile["Yields"]["Lb2LcPi"][year][boundList[i]])
        inBd2DRhoEvts.append(myconfigfile["Yields"]["Bd2DRho"][year][boundList[i]])
        inBd2DstPiEvts.append(myconfigfile["Yields"]["Bd2DstPi"][year][boundList[i]])        

        #inPeakBkgEvts.append(inBs2DsPiEvts[i] + inBd2DKEvts[i] + inLb2LcPiEvts[i])
        #inLMBkgEvts.append(inBd2DstPiEvts[i] + inBd2DRhoEvts[i])

        if sampleTS == "up":
            inComboEvts[i]  = inComboEvts[i]*myconfigfile["LumRatio"][year]
            inBd2DKEvts[i]  = inBd2DKEvts[i]*myconfigfile["LumRatio"][year]
            inBs2DsPiEvts[i]  = inBs2DsPiEvts[i]*myconfigfile["LumRatio"][year]
            inLb2LcPiEvts[i] = inLb2LcPiEvts[i]*myconfigfile["LumRatio"][year]
            inBd2DRhoEvts[i]  = inBd2DRhoEvts[i]*myconfigfile["LumRatio"][year]
            inBd2DstPiEvts[i]  = inBd2DstPiEvts[i]*myconfigfile["LumRatio"][year]

            #inPeakBkgEvts[i] = inPeakBkgEvts[i]*myconfigfile["LumRatio"][year]
            #inLMBkgEvts[i] = inLMBkgEvts[i]*myconfigfile["LumRatio"][year]
            
        elif sampleTS == "down":
            inComboEvts[i]  = inComboEvts[i]*(1-myconfigfile["LumRatio"][year])
            inBd2DKEvts[i]  = inBd2DKEvts[i]*(1-myconfigfile["LumRatio"][year])
            inBs2DsPiEvts[i]  = inBs2DsPiEvts[i]*(1-myconfigfile["LumRatio"][year])
            inLb2LcPiEvts[i] = inLb2LcPiEvts[i]*(1-myconfigfile["LumRatio"][year])
            inBd2DRhoEvts[i]  = inBd2DRhoEvts[i]*(1-myconfigfile["LumRatio"][year])
            inBd2DstPiEvts[i]  = inBd2DstPiEvts[i]*(1-myconfigfile["LumRatio"][year])

            #inPeakBkgEvts[i] = inPeakBkgEvts[i]*(1-myconfigfile["LumRatio"][year])
            #inLMBkgEvts[i] = inLMBkgEvts[i]*(1-myconfigfile["LumRatio"][year])
            
        if nobackground:
            nComboBkg.append(WS(workInt,RooRealVar( nameComboBkg.Data()  , nameComboBkg.Data() , 0.0)))
            nBd2DK.append(WS(workInt,RooRealVar( nameBd2DK.Data(), nameBd2DK.Data(), 0.0)))
            nBs2DsPi.append(WS(workInt,RooRealVar( nameBs2DsPi.Data(), nameBs2DsPi.Data(), 0.0)))
            nLb2LcPi.append(WS(workInt,RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), 0.0)))
            nBd2DRho.append(WS(workInt,RooRealVar( nameBd2DRho.Data(), nameBd2DRho.Data(), 0.0)))
            nBd2DstPi.append(WS(workInt,RooRealVar( nameBd2DstPi.Data(), nameBd2DstPi.Data(), 0.0)))

            #nPeakBkg.append(WS(workInt,RooRealVar( namePeakBkg.Data(), namePeakBkg.Data(), 0.0)))
            #nLMBkg.append(WS(workInt,RooRealVar( nameLMBkg.Data(), nameLMBkg.Data(), 0.0)))
            
        else:
            nComboBkg.append(WS(workInt,RooRealVar( nameComboBkg.Data()  , nameComboBkg.Data() , inComboEvts[i] , 0.0 , nEntries[i])))
            nBd2DK.append(WS(workInt,RooRealVar( nameBd2DK.Data(), nameBd2DK.Data(), inBd2DKEvts[i], 0.0 , nEntries[i])))
            nBs2DsPi.append(WS(workInt,RooRealVar( nameBs2DsPi.Data(), nameBs2DsPi.Data(), inBs2DsPiEvts[i], 0.0 , nEntries[i])))
            nLb2LcPi.append(WS(workInt,RooRealVar( nameLb2LcPi.Data(), nameLb2LcPi.Data(), inLb2LcPiEvts[i], 0.0 , nEntries[i])))
            nBd2DRho.append(WS(workInt,RooRealVar( nameBd2DRho.Data(), nameBd2DRho.Data(), inBd2DRhoEvts[i], 0.0 , nEntries[i])))
            nBd2DstPi.append(WS(workInt,RooRealVar( nameBd2DstPi.Data(), nameBd2DstPi.Data(), inBd2DstPiEvts[i], 0.0 , nEntries[i])))

            #nPeakBkg.append(WS(workInt,RooRealVar( namePeakBkg.Data(), namePeakBkg.Data(), inPeakBkgEvts[i], 0.0 , nEntries[i])))
            #nLMBkg.append(WS(workInt,RooRealVar( nameLMBkg.Data(), nameLMBkg.Data(), inLMBkgEvts[i], 0.0 , nEntries[i])))

        #f1PeakBkg.append(WS(workInt,RooRealVar( namef1PeakBkg.Data()  ,
         #                            namef1PeakBkg.Data() ,
          #                           inBs2DsPiEvts[i] / (inBs2DsPiEvts[i] + inBd2DKEvts[i] + inLb2LcPiEvts[i]))))

        #f2PeakBkg.append(WS(workInt,RooRealVar( namef2PeakBkg.Data()  ,
        #                             namef2PeakBkg.Data() ,
        #                             inBd2DKEvts[i] / (inBs2DsPiEvts[i] + inBd2DKEvts[i] + inLb2LcPiEvts[i]))))

        #f1LMBkg.append(WS(workInt,RooRealVar( namef1LMBkg.Data()  ,
        #                           namef1LMBkg.Data() ,
        #                           inBd2DstPiEvts[i] / (inBd2DstPiEvts[i] + inBd2DRhoEvts[i]))))

        #---------------------------------------Combinatorial-------------------------------------------------------------------------------

        cBVar.append(RooRealVar("CombBkg_%s_cB_%s"%(mass.GetName(),sm[i]),"CombBkg_slope_B", myconfigfile["BsCombinatorialShape"]["cB"][year][boundList[i]]))
        massB_Combo.append(RooExponential("massB_Combo_%s"%(sm[i]),"massB_Combo",mass, cBVar[i]))

        cDVar.append(WS(workInt,RooRealVar("CombBkg_%s_cD_%s"%(massD.GetName(),sm[i]),"CombBkg_slope_D", myconfigfile["DsCombinatorialShape"]["cD"][year][boundList[i]])))
        fracDComb.append(WS(workInt,RooRealVar("CombBkg_%s_fracD_%s"%(massD.GetName(),sm[i]), "CombBkg_fracDComb",  myconfigfile["DsCombinatorialShape"]["fracCombD"][year][boundList[i]])))
        massD_Combo.append(Bs2Dsh2011TDAnaModels.buildExponentialPlusSignalPDF(massD, workInt, sm[i], "CombBkg"))

        MDFitter_Combo.append(RooProdPdf("MDFitter_Combo_m_%s"%(sm[i]),"MDFitter_Combo",RooArgList(massB_Combo[i], massD_Combo[i])))
        ComboEPDF.append(RooExtendPdf("ComboBkgEPDF_m_%s"%(sm[i]),"ComboBkgEPDF_m_%s"%(sm[i]),MDFitter_Combo[i],nComboBkg[i]))
        
        #----------------------------------------Bd->DK-----------------------------------------------------------------------------------

        MDFitter_Bd2DK.append(Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace[0], TString("Bd2DK"), magpol, yearTS, lumRatio, NULL, dim, debug))
        Bd2DKEPDF.append(RooExtendPdf("Bd2DKEPDF_m_%s"%(sm[i]),"Bd2DKEPDF_m_%s"%(sm[i]),MDFitter_Bd2DK[i],nBd2DK[i]))

        #----------------------------------------Bs2DsPi----------------------------------------------------------------------------------

        massB_Bs2DsPi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace[0], TString("Bs2DsPi"), yearTS, False, lumRatio, debug))
        massD_Bs2DsPi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace[0], TString("Bs2DsPi"), yearTS, True, lumRatio, debug))

        MDFitter_Bs2DsPi.append(RooProdPdf("MDFitter_Bs2DsPi_m_%s"%(sm[i]),"MDFitter_Bs2DsPi_m_%s"%(sm[i]),RooArgList(massB_Bs2DsPi[i], massD_Bs2DsPi[i])))
        Bs2DsPiEPDF.append(RooExtendPdf("Bs2DsPiEPDF_m_%s"%(sm[i]),"Bs2DsPiEPDF_m_%s"%(sm[i]),MDFitter_Bs2DsPi[i],nBs2DsPi[i]))

        #---------------------------------------Lb2LcPi-----------------------------------------------------------------------------------

        MDFitter_Lb2LcPi.append(Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace[0], TString("Lb2LcPi"), magpol, yearTS, lumRatio, NULL, dim, debug));
        Lb2LcPiEPDF.append(RooExtendPdf("Lb2LcPiEPDF_m_%s"%(sm[i]),"Lb2LcPiEPDF_m_%s"%(sm[i]),MDFitter_Lb2LcPi[i],nLb2LcPi[i]))
        
        #---------------------------------------Bd2DRho-----------------------------------------------------------------------------------

        massB_Bd2DRho = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace[0], TString("Bd2DRho"), yearTS, False, lumRatio, debug)
        massD_Bd2DRho.append(sigDPDF[i])
        
        MDFitter_Bd2DRho.append(RooProdPdf("MDFitter_Bd2DRho_m_%s"%(modeTS),"MDFitter_Bd2DRho_m_%s"%(sm[i]),RooArgList(massB_Bd2DRho, massD_Bd2DRho[i])))
        Bd2DRhoEPDF.append(RooExtendPdf("Bd2DRhoEPDF_m_%s"%(sm[i]),"Bd2DRhoEPDF_m_%s"%(sm[i]),MDFitter_Bd2DRho[i],nBd2DRho[i]))
        
        #---------------------------------------Bd2DstPi-----------------------------------------------------------------------------------

        massB_Bd2DstPi = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace[0], TString("Bd2DstPi"), yearTS, False, lumRatio, debug)
        massD_Bd2DstPi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace[0], TString("Bd2DstPi"), yearTS, True, lumRatio, debug))

        MDFitter_Bd2DstPi.append(RooProdPdf("MDFitter_Bd2DstPi_m_%s"%(sm[i]),"MDFitter_Bd2DstPi_m_%s"%(sm[i]),RooArgList(massB_Bd2DstPi, massD_Bd2DstPi[i])))
        Bd2DstPiEPDF.append(RooExtendPdf("Bd2DstPiEPDF_m_%s"%(sm[i]),"Bd2DstPiEPDF_m_%s"%(sm[i]),MDFitter_Bd2DstPi[i],nBd2DstPi[i]))


        #---------------------------------------Lb + Bs (Peaking) background-------------------------------------------------------------------------

        #MDFitter_PeakBkg.append(RooAddPdf("MDFitter_PeakBkg_m_%s"%(sm[i]),"MDFitter_PeakBkg_m_%s"%(sm[i]),
         #                                 RooArgList(MDFitter_Bs2DsPi[i],MDFitter_Bd2DK[i],MDFitter_Lb2LcPi[i]),RooArgList(f1PeakBkg[i],f2PeakBkg[i])))

        #PeakBkgEPDF.append(RooExtendPdf("PeakBkgEPDF_m_%s"%(sm[i]),"PeakBkgEPDF_m_%s"%(sm[i]),MDFitter_PeakBkg[i],nPeakBkg[i]))

        #---------------------------------------BdDstPi + BdDRho (Low mass) background---------------------------------------------------------------
        #MDFitter_LMBkg.append(RooAddPdf("MDFitter_LMBkg_m_%s"%(sm[i]),"MDFitter_LMBkg_m_%s"%(sm[i]),
         #                               RooArgList(MDFitter_Bd2DstPi[i],MDFitter_Bd2DRho[i]),RooArgList(f1LMBkg[i])))

        #LMBkgEPDF.append(RooExtendPdf("LMBkgEPDF_m_%s"%(sm[i]),"LMBkgEPDF_m_%s"%(sm[i]),MDFitter_LMBkg[i],nLMBkg[i]))
        
        ###------------------------------------------------------------------------------------------------------------------------------------###
          ###---------------------------------   Create the total PDF in B mass, D mass --------------------------------------###
        ###------------------------------------------------------------------------------------------------------------------------------------###
        
        pdfList.append(RooArgList(sigEPDF[i]))
        pdfList[i].add(ComboEPDF[i])
        pdfList[i].add(Bd2DKEPDF[i])
        pdfList[i].add(Bs2DsPiEPDF[i])
        pdfList[i].add(Lb2LcPiEPDF[i])
        pdfList[i].add(Bd2DRhoEPDF[i])
        pdfList[i].add(Bd2DstPiEPDF[i])
        #pdfList[i].add(PeakBkgEPDF[i])
        #pdfList[i].add(LMBkgEPDF[i])

        name = TString("TotEPDF_m_")+sm[i]

        totPDF.append(RooAddPdf( name.Data(), 'Model (signal & background) EPDF in mass', pdfList[i]))

        if debug:
            print "=========================================================="
            print "Mass fit PDFs"
            print "=========================================================="
            print "==> Signal"
            sigEPDF[i].Print("v")
            print "==> Combinatorial"
            ComboEPDF[i].Print("v")
            print "==> Bd2DK"
            Bd2DKEPDF[i].Print("v")
            print "==> Bs2DsPi"
            Bs2DsPiEPDF[i].Print("v")
            print "==> Lb2LcPi"
            Lb2LcPiEPDF[i].Print("v")
            print "==> Bd2DRho"
            Bd2DRhoEPDF[i].Print("v")
            print "==> Bd2DstPi"
            Bd2DstPiEPDF[i].Print("v")
            #print "==> Lb+Bs+BdDK (Peak)"
            #PeakBkgEPDF[i].Print("v")
            #print "==> BdDstPi+BdDRho (LM)"
            #LMBkgEPDF[i].Print("v")
            print "==> Total PDF"
            totPDF[i].Print("v")

    ###------------------------------------------------------------------------------------------------------------------------------------###
          ###--------------------------------------------  Instantiate and run the fitter  -------------------------------------------###
    ###------------------------------------------------------------------------------------------------------------------------------------###

    fitter = FitMeTool( debug )
    fitter.setObservables( observables )
    fitter.setModelPDF( totPDF[0] )
    fitter.setData( combData ) 
    
    fitter.fit(True, RooFit.Extended(), RooFit.Verbose(False)) #RooFit.SumW2Error(True), RooFit.Verbose(False))
    result = fitter.getFitResult()
    result.Print("v")
    floatpar = result.floatParsFinal()
    initpar = result.floatParsInit()

    corr = result.correlationMatrix()
    corr.Print("v")

    cov = result.covarianceMatrix()
    cov.Print("v")

    qual = result.covQual()
    print "Covariance matrix quality (3 means good): ", qual

    name = TString(options.sweightoutputname)
     
    if (sweight):
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(RooFit.Eval)
        fitter.savesWeights(mass.GetName(), combData, name)
        RooMsgService.instance().reset() 
                                                
    fitter.printYieldsInRange( '*Evts', obsTS.Data() , 5000, 6000 )

    for i in range(0,bound):
        print ""
        print "---Expected Yields:---"
        print "Signal %d"%(nSigEvts[i])
        print "Combinatorial %d"%(inComboEvts[i])
        print "Bd2DRho %d"%(inBd2DRhoEvts[i])
        print "Bd2DstPi %d"%(inBd2DstPiEvts[i])
        print "Bd2DK %d"%(inBd2DKEvts[i])
        print "Bs2DsPi %d"%(inBs2DsPiEvts[i])
        print "Lb2LcPi %d"%(inLb2LcPiEvts[i])
        #print "Lb+Bs+BdDK %d"%(inPeakBkgEvts[i])
        #print "BdDstPi+BdDRho %d"%(inLMBkgEvts[i])
        print ""

    if massplot:
        print "Creating file to store PDF/data for plotting"
        ws = RooWorkspace( "FitMeToolWS", "FitMeToolWS")
        getattr(ws,'import')(combData)
        getattr(ws,'import')(totPDF[0])
        ws.writeToFile( options.wsname )

    #-------------------------------------------------------------
    #Save fit results in rootfile (for pull histograms)
    from B2DXFitters.FitResultGrabberUtils import CreatePullTree as CreatePullTree
    CreatePullTree(fileNamePull, result, 'covQual')

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
                   default = 'WS_Mass_DPi.root', 
                   help = 'name of the root file to store PDF and generated dataset'
                   )

parser.add_option( '--massplot',
                   action = 'store_true',
                   dest = 'massplot',
                   default = False,
                   help = 'save the model PDF and generated dataset to file'
                   )

parser.add_option( '--sweightoutputname',
                   dest = 'sweightoutputname',
                   default = 'sWeights_Bd2DPi_both_all_BDTGA.root', 
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
                   default = 'kpipi',
                   help = 'Mode: choose all, kkpi, kpipi or pipipi'
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

parser.add_option( '--fileNamePull',
                   dest = 'fileNamePull',
                   default = 'pull.root',
                   help = 'name of the file to store info for pull plot'
                   )

parser.add_option( '--workName',
                   dest = 'workName',
                   default = 'workspace',
                   help = 'name of the workspace'
                   ) 
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bd2DPiConfigForNominalMassFit')
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
                   default = 2)

parser.add_option( '--year',
                   dest = 'year',
                   default = '2012')

parser.add_option( '--toys',
                   dest = 'toys',
                   action = 'store_true',
                   default = False,
                   help = 'Fit toys'
                   )

parser.add_option( '--fileData',
                   dest = 'fileData',
                   default = '',
                   help = 'you can use it if you have separate files with templates and data'
                   )

parser.add_option( '--nobackground',
                   dest = 'nobackground',
                   action = 'store_true',
                   default = False,
                   help = 'Fit a signal-only sample'
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
    import sys
    sys.path.append("../data/Bd2DPi_3fbCPV/Bd2DPi/")
 
    runBd2DPiMassFitterOnToys(   options.debug,  options.sample, options.massplot, \
                                 options.mode, options.year, options.toys, options.sweight, \
                                 options.fileNameAll, options.fileNameToys, options.fileNamePull, \
                                 options.workName, options.configName, options.wide, options.dim, options.merge, options.fileData, \
                                 options.nobackground)
    
# -----------------------------------------------------------------------------
