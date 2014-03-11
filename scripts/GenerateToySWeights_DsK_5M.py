# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to generate toys for DsK                                    #
#                                                                             #
#   Example usage:                                                            #
#      python GenerateToySWeights_DsK.py                                      #
#                                                                             #
#   Author: Vava Gligorov                                                     #
#   Date  : 14 / 06 / 2012                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 06 / 2012                                                    #
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
import os, sys, gc
gROOT.SetBatch()

from B2DXFitters import taggingutils, cpobservables
RooAbsData.setDefaultStorageType(RooAbsData.Tree)
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)


#------------------------------------------------------------------------------
def runBsDsKGenerator( debug, single, configName, rangeDown, rangeUp, seed , size, dir) :

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

    RooRandom.randomGenerator().SetSeed(int(seed)) #746829203) #78249292)
    print int(seed)
    size = int(size)
    print size
    #workout = RooWorkspace("workspace","workspace")

    Gammad       = RooRealVar('Gammad','Gammad', myconfigfile["Gammad"])                     # in ps^{-1}
    Gammas       = RooRealVar('Gammas','Gammas', myconfigfile["Gammas"])                     # in ps^{-1}
    DeltaGammad  = RooRealVar('DeltaGammad','DeltaGammad', myconfigfile["DeltaGammad"])      # in ps^{-1}
    DeltaGammas  = RooRealVar('DeltaGammas','DeltaGammas', myconfigfile["DeltaGammas"])      # in ps^{-1}
    TauInvGd     = Inverse( "TauInvGd","TauInvGd", Gammad)
    TauInvGs     = Inverse( "TauInvGs","TauInvGs", Gammas)
        
    DeltaMd      = RooRealVar('DeltaMd','DeltaMd', myconfigfile["DeltaMd"])                  # in ps^{-1}
    DeltaMs      = RooRealVar('DeltaMs','DeltaMs', myconfigfile["DeltaMs"])                  # in ps^{-1}
                        
    GammaLb      = RooRealVar('GammaLb','GammaLb',myconfigfile["GammaLb"])
    GammaCombo   = RooRealVar('GammaCombo','GammaCombo',myconfigfile["GammaCombo"])
    TauInvLb     = Inverse( "TauInvLb","TauInvLb", GammaLb)
    TauInvCombo  = Inverse( "TauInvCombo","TauInvCombo", GammaCombo)
        
    #TauRes       = RooRealVar('TauRes','TauRes',myconfigfile["TauRes"])

    half     = RooConstVar('half','0.5',0.5)    
    zero     = RooConstVar('zero', '0', 0.)
    one      = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two      = RooConstVar('two', '2', 2.)

    sam = TString("both")
    #mode = TString("phipi")
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
    dim = int(3) 
    
    #if single :
    #    ntoys = 1
    #else:
    #    ntoys = int()
                            
      
    gendata = []
    data = []
    
    fileName  = "work_dsk_pid_53005800_PIDK5_5M_BDTGA_4.root"
    fileNameData = "work_dsk_pid_53005800_PIDK5_5M_BDTGA_4.root"
    fileNameTerr = "../data/workspace/MDFitter/template_Data_Terr_BsDsK.root"
    fileNameMistag = "../data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root"
    fileNameMistagBDPi = "../data/workspace/MDFitter/template_Data_Mistag_BDPi.root"
    fileNameMistagComb = "../data/workspace/MDFitter/template_Data_Mistag_CombBkg.root"
    fileNameKFactor =  "../data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root"
    dupa = "5320_5420"
    fileNameKFactor =  "../data/workspace/MDFitter/dsk_ktemplates_mass_bin_%s.root"%(dupa)
    workName = 'workspace'

    #Read workspace with PDFs
    workspace = GeneralUtils.LoadWorkspace(TString(fileName),TString(workName), debug)
    workspace.Print("v")
    workspaceData = GeneralUtils.LoadWorkspace(TString(fileNameData),TString(workName), debug)
    workspaceData.Print("v")
        
    workTerr = GeneralUtils.LoadWorkspace(TString(fileNameTerr),TString(workName), debug)
    workTerr.Print("v")
    workMistag = GeneralUtils.LoadWorkspace(TString(fileNameMistag),TString(workName), debug)
    workMistag.Print("v")
    workMistagBDPi = GeneralUtils.LoadWorkspace(TString(fileNameMistagBDPi),TString(workName), debug)
    workMistagBDPi.Print("v")
    workMistagComb = GeneralUtils.LoadWorkspace(TString(fileNameMistagComb),TString(workName), debug)
    workMistagComb.Print("v")
    workKFactor = GeneralUtils.LoadWorkspace(TString(fileNameKFactor),TString(workName), debug)
    workKFactor.Print("v")
    #exit(0)
    
    kFactor = GeneralUtils.GetObservable(workKFactor,TString("kfactorVar"), debug)
    kFactor.setRange(0.80, 1.10)
    
    dataKFactorDown = []
    dataKFactorUp   = []
    names = ["Bd2DK","Bd2DPi","Lb2LcK","Lb2LcPi","Lb2Dsstp","Lb2Dsp","Bs2DsstPi","Bs2DsRho","Bs2DsPi"]
    #names = ["Bs2DsstPi","Bs2DsK","Lb2LcPi","Bd2DPi"]
    for i in range(0,names.__len__()):
        dataNameUp = "kfactor_dataset_"+names[i]+"_up" 
        dataKFactorUp.append(GeneralUtils.GetDataSet(workKFactor,TString(dataNameUp), debug))
        dataKFactorUp[i].Print("v")
        print dataKFactorUp[i].sumEntries()
        dataNameDown = "kfactor_dataset_"+names[i]+"_down"
        dataKFactorDown.append(GeneralUtils.GetDataSet(workKFactor,TString(dataNameDown), debug))
        dataKFactorDown[i].Print("v")
        print dataKFactorDown[i].sumEntries()

    max = [-2.0,-2.0,-2.0,-2.0,-2.0,-2.0,-2.0,-2.0,-2.0]
    min = [2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0]
    for i in range(0,names.__len__()):
        for j in range(0,dataKFactorUp[i].numEntries()) :
            obsKF = dataKFactorUp[i].get(j)
            kF = obsKF.find("kfactorVar")
            kNum = kF.getVal()
            #print kNum
            if kNum > max[i]:
                max[i] = kNum
            if kNum < min[i]:
                min[i] = kNum
        for j in range(0,dataKFactorDown[i].numEntries()) :
            obsKF = dataKFactorDown[i].get(j)
            kF = obsKF.find("kfactorVar")
            kNum = kF.getVal()
            if kNum > max[i]:
                max[i] = kNum
            if kNum < min[i]:
                min[i] = kNum
                
    print max
    print min
    maxRange = []
    minRange = []
    for i in range(0,names.__len__()):
        q = max[i] - min[i]
        maxRange.append(max[i]+0.05*q)
        minRange.append(min[i]-0.05*q)

    print maxRange
    print minRange

    plotSet = PlotSettings("plotSet","plotSet")
    

    histDW = []
    histUP = []
    hist   = []
    pdfKF     = []
    lumRatio = RooRealVar("lumRatio","lumRatio",myconfigfile["lumRatio"])
    gMax = -100.0
    gMin = 100.0
    for i in range(0,names.__len__()):
        kFactor.setRange(minRange[i], maxRange[i])
        if gMax < maxRange[i]:
            gMax = maxRange[i]
        if gMin > minRange[i]:
            gMin = minRange[i]
        name = "kFactor_"+names[i]+"_both"
        pdfKF.append(GeneralUtils.CreateHistPDF(dataKFactorUp[i], dataKFactorDown[i], myconfigfile["lumRatio"],
                                                kFactor, TString(name), 100, debug))
        t = TString("both")
        GeneralUtils.SaveTemplate(NULL, pdfKF[i], kFactor, TString(names[i]), t, plotSet, debug );
        
    print gMin
    print gMax
    workOut = RooWorkspace("workspace","workspace")
    kFactor.setRange(gMin,gMax)
    getattr(workOut,'import')(kFactor) 
    for i in range(0,names.__len__()):
        getattr(workOut,'import')(pdfKF[i])
        
    workOut.SaveAs("template_MC_KFactor_BsDsK_%s.root"%(dupa))
    workOut.Print("v")
    exit(0)
    
    
    mVar         = 'lab0_MassFitConsD_M'
    mdVar        = 'lab2_MM'
    PIDKVar      = 'lab1_PIDK'
    tVar         = 'lab0_LifetimeFit_ctau'
    terrVar      = 'lab0_LifetimeFit_ctauErr'
    trueID       = 'lab0_TRUEID'
    charge       = 'lab1_ID'
    tagdec       = ['lab0_TAGDECISION_OS','lab0_SS_nnetKaon_DEC' ]
    tagomega     = ['lab0_TAGOMEGA_OS',   'lab0_SS_nnetKaon_PROB']
       
    timeVar_B       = GeneralUtils.GetObservable(workspace,TString(tVar), debug) 
    terrVar_B       = GeneralUtils.GetObservable(workspace,TString(terrVar), debug)
    massVar_D       = GeneralUtils.GetObservable(workspace,TString(mdVar), debug)
    PIDKVar_B       = GeneralUtils.GetObservable(workspace,TString(PIDKVar), debug)
    massVar_B       = GeneralUtils.GetObservable(workspace,TString(mVar), debug)
    trueIDVar_B     = RooRealVar(trueID,trueID,0,100)
    idVar_B         = GeneralUtils.GetCategory(workspaceData,TString(charge), debug)  

    # Tagging parameters
    tagVar_B        = []
    mistagVar_B     = []
    tagList         = RooArgList() 
    mistagList      = RooArgList()
    for i in range(0,2):
        print i
        tagVar_B.append(GeneralUtils.GetCategory(workspaceData,TString(tagdec[i]), debug))
        mistagVar_B.append(GeneralUtils.GetObservable(workspaceData,TString(tagomega[i]), debug))
        mistagList.add(mistagVar_B[i])
        print "Add mistag: ",mistagVar_B[i].GetName()
        tagList.add(tagVar_B[i])
        print "Add tag: ",tagVar_B[i].GetName()
    '''        
    name = ["OS","SS"]    
    calibration_p0   = []
    calibration_p1   = []
    calibration_av   = []
    mistagCalibration = []
    mistagCalibList = RooArgList()
    for i in range(0,2):
        calibration_p0.append(RooRealVar('calibration_p0_'+name[i], 'calibration_p0_'+name[i], myconfigfile["calibration_p0"][i]))
        calibration_p1.append(RooRealVar('calibration_p1_'+name[i], 'calibration_p1_'+name[i], myconfigfile["calibration_p1"][i]))
        calibration_av.append(RooRealVar('calibration_av_'+name[i], 'calibration_av_'+name[i], myconfigfile["calibration_av"][i]))
        mistagCalibration.append(MistagCalibration('mistag_calibrated_'+name[i], 'mistag_calibrated_'+name[i],
                                              mistagVar_B[i], calibration_p0[i], calibration_p1[i], calibration_av[i]))
        mistagCalibList.add(mistagCalibration[i])

        print calibration_p0[i].GetName()
        print calibration_p1[i].GetName()
        print calibration_av[i].GetName()
        print mistagVar_B[i].GetName()
        print mistagCalibration[i].GetName()
        
    combiner     = DLLTagCombiner("tagCombiner", "tagCombiner", tagList, mistagCalibList)
    '''
        
    tagDecComb   = GeneralUtils.GetCategory(workspaceData,TString("tagDecComb"), debug)
    tagOmegaComb = GeneralUtils.GetObservable(workspaceData,TString("tagOmegaComb"), debug)
    tagOmegaComb.setConstant(False)
    tagDecComb.setConstant(False)
    tagOmegaComb.setRange(0,0.5)
        
    calibHalf = MistagCalibration('calibHalf', 'calibHalf', tagOmegaComb, half, zero)
    calibIdentity = MistagCalibration('calibIdentity', 'calibIdentity', tagOmegaComb, zero, one)
    tagOmegaList = RooArgList(calibIdentity, calibIdentity, calibIdentity)
    tagOmegaListBd = RooArgList(calibIdentity, calibHalf, calibIdentity)

    mistagBs = []
    mistagBsPDFList = RooArgList()
    mistagBd = []
    mistagBdPDFList = RooArgList()
    mistagComb = []
    mistagCombPDFList = RooArgList()
    for i in range(0,3):
        namePDF = TString("sigMistagPdf_")+TString(str(i+1))
        print namePDF
        mistagBs.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workMistag, namePDF, debug))
        mistagBs[i].SetName("sigMistagPdf_BsDsK_"+str(i))
        mistagBd.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workMistagBDPi, namePDF, debug))
        mistagBd[i].SetName("sigMistagPdf_Bd2DPi_"+str(i))
        mistagComb.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workMistagComb, namePDF, debug))
        mistagComb[i].SetName("sigMistagPdf_CombBkg_"+str(i))
        mistagBsPDFList.add(mistagBs[i])
        #mistagBdPDFList.add(mistagBd[i])
        mistagCombPDFList.add(mistagComb[i])

    mistagBdPDFList.add(mistagBd[0])
    mistagBdPDFList.add(mistagBd[1])
    mistagBdPDFList.add(mistagBd[0])
    print 'name',mistagBd[0].GetName()
    print 'name',mistagBd[1].GetName()
    #exit(0)
    
    # Acceptance
    binName = TString("splineBinning")
    TimeBin = RooBinning(0.2,15,binName.Data())
    for i in range(0, myconfigfile["tacc_size"]):
        TimeBin.addBoundary(myconfigfile["tacc_knots"][i])
                
    
    TimeBin.removeBoundary(0.2)
    TimeBin.removeBoundary(15.0)
    TimeBin.removeBoundary(0.2)
    TimeBin.removeBoundary(15.0)
    TimeBin.Print("v")
    timeVar_B.setBinning(TimeBin, binName.Data())
    timeVar_B.setRange(0.2, 15.0)
    listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, timeVar_B)

    tacc_list = RooArgList()
    tacc_var = []
    for i in range(0, myconfigfile["tacc_size"]):
        tacc_var.append(RooRealVar("var"+str(i+1), "var"+str(i+1), myconfigfile["tacc_values"][i]))
        print tacc_var[i].GetName()
        tacc_list.add(tacc_var[i])
    tacc_var.append(RooRealVar("var"+str(myconfigfile["tacc_size"]+1), "var"+str(myconfigfile["tacc_size"]+1), 1.0))
    len = tacc_var.__len__()
    tacc_list.add(tacc_var[len-1])
    print "n-2: ",tacc_var[len-2].GetName()
    print "n-1: ",tacc_var[len-1].GetName()
    tacc_var.append(RooAddition("var"+str(myconfigfile["tacc_size"]+2),"var"+str(myconfigfile["tacc_size"]+2),
                                RooArgList(tacc_var[len-2],tacc_var[len-1]), listCoeff))
    tacc_list.add(tacc_var[len])
    print "n: ",tacc_var[len].GetName()
    #exit(0)
    
    taccNoNorm = RooCubicSplineFun("splinePdf", "splinePdf", timeVar_B, "splineBinning", tacc_list)
    it = tacc_list.fwdIterator()
    m = 0.
    while True:
        obj = it.next()
        if None == obj: break
        if obj.getVal() > m:
            m = obj.getVal()
    print "max: ",m
    SplineConst = RooConstVar('SplineAccNormCoeff', 'SplineAccNormCoeff', 1. / m)
    tacc = RooProduct('SplineAcceptanceNormalised','SplineAcceptanceNormalised', RooArgList(taccNoNorm, SplineConst))
    
    #Time resolution
    trm_mean    = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["resolutionMeanBias"], 'ps' )
    trm_scale = RooRealVar( 'trm_sigmaSF', 'Gaussian resolution model scale factor', myconfigfile["resolutionScaleFactor"] )
    trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGaussPEDTE', timeVar_B, trm_mean, terrVar_B, trm_scale)
           
    nameDs = [TString("nonres"), TString("phipi"), TString("kstk"), TString("kpipi"), TString("pipipi")]
    nameDs2 = ["nonres","phipi","kstk","kpipi","pipipi"]
    
    total_pdf = []

    meanVarBs = []
    sigma1VarBs = []
    sigma2VarBs = []
    alpha1VarBs = []
    alpha2VarBs = []
    n1VarBs = []
    n2VarBs = []
    fracVarBs = []
    massB_signal = []

    meanVarDs = []
    sigma1VarDs = []
    sigma2VarDs = []
    alpha1VarDs = []
    alpha2VarDs = []
    n1VarDs = []
    n2VarDs = []
    fracVarDs = []
    massD_signal = []

    PIDK_signal = []
    MDFitter_signal = []    
    timeandmass_signal = []

    meanVarBd   =  []
    sigma1VarBd =  []
    sigma2VarBd =  []
    
    massB_dsk = []
    massD_dsk = []
    PIDK_dsk = []
    MDFitter_dsk = []
    timeandmass_dsk = []

    massB_dspi = []
    massD_dspi = []
    PIDK_dspi = []
    MDFitter_dspi = []
    timeandmass_dspi = []

    massD_dsp = []
    MDFitter_dsp = []
    timeandmass_dsp = []

    massD_dsstp = []
    MDFitter_dsstp = []
    timeandmass_dsstp = []
            
    
    cBVar = []
    massB_combo = []     
    cDVar = [] 
    fracDsComb = []
    massD_combo = []
    MDFitter_combo = []
    timeandmass_combo = []
         
    massD_lm1 = []
    MDFitter_lm1 = []
    timeandmass_lm1 = []

    massD_dsstpi = []
    MDFitter_dsstpi = []
    timeandmass_dsstpi = []

    massD_dsrho = []
    MDFitter_dsrho = []
    timeandmass_dsrho = []
               
    timeandmass_dk = []
    timeandmass_lck = []
    timeandmass_dpi = []
    timeandmass_lcpi = []

    
    num_signal = []
    num_dk = []
    num_dpi = []
    num_dsk = []
    num_dspi = []
    num_lck = []
    num_lcpi = []
    num_dsp = []
    num_dsstp = []
    num_combo = []
    num_lm1 = []
    num_dsstpi = []
    num_dsrho = []
    
    evNum  = 0

    # ------------------------------------------------ Signal -----------------------------------------------------#

    #The signal - time acceptance - tacc_powlaw
    tacc_signal = tacc

    #The signal - resolution
    trm_signal = trm
    
    #The signal - time error
    terr_signal = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsK"), debug)
        
    #The signal - time
    ACPobs_signal = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"], myconfigfile["ArgLbarfbar_s"], myconfigfile["ModLf_s"])
    ACPobs_signal.printtable()
    
    C_signal     = RooRealVar('C_signal','C_signal',ACPobs_signal.Cf())
    S_signal     = RooRealVar('S_signal','S_signal',ACPobs_signal.Sf())
    D_signal     = RooRealVar('D_signal','D_signal',ACPobs_signal.Df())
    Sbar_signal  = RooRealVar('Sbar_signal','Sbar_signal',ACPobs_signal.Sfbar())
    Dbar_signal  = RooRealVar('Dbar_signal','Dbar_signal',ACPobs_signal.Dfbar())

    tagEff_signal = []
    tagEffList_signal = RooArgList()
    for i in range(0,3):
        tagEff_signal.append(RooRealVar('tagEff_signal_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_signal"][i]))
        print tagEff_signal[i].GetName()
        tagEffList_signal.add(tagEff_signal[i])
       
    aProd_signal   = RooConstVar('aprod_signal',   'aprod_signal',   myconfigfile["aprod_signal"])        # production asymmetry
    aDet_signal    = RooConstVar('adet_signal',    'adet_signal',    myconfigfile["adet_signal"])         # detector asymmetry
    
    aTagEff_signal = []
    aTagEffList_signal = RooArgList()
    for i in range(0,3):
        aTagEff_signal.append(RooRealVar('aTagEff_signal_'+str(i+1), 'atageff', myconfigfile["atageff_signal"][i]))
        print aTagEff_signal[i].GetName()
        aTagEffList_signal.add(aTagEff_signal[i])
      
    #The Bs->DsK - mistag
    mistag_signal = mistagBsPDFList 
    
    flag_signal = 0
    flag = 0

    otherargs_signal = [ tagOmegaComb, mistag_signal, tagEffList_signal ]
    otherargs_signal.append(tagOmegaList)
    otherargs_signal.append(aProd_signal)
    otherargs_signal.append(aDet_signal)
    otherargs_signal.append(aTagEffList_signal)
    
    cosh_signal = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven,
                               idVar_B, tagDecComb,  one,      one,      *otherargs_signal)
    sinh_signal = DecRateCoeff('signal_sinh', 'signal_sinh', flag_signal | DecRateCoeff.CPEven,
                               idVar_B, tagDecComb,  D_signal,    Dbar_signal, *otherargs_signal)
    cos_signal  = DecRateCoeff('signal_cos',  'signal_cos' , DecRateCoeff.CPOdd,
                               idVar_B, tagDecComb,  C_signal,    C_signal,    *otherargs_signal)
    sin_signal  = DecRateCoeff('signal_sin',  'signal_sin',  flag_signal | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                               idVar_B, tagDecComb,  S_signal, Sbar_signal,    *otherargs_signal)
    
    
    time_signal_noacc       = RooBDecay('time_signal_noacc','time_signal_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_signal, sinh_signal, cos_signal, sin_signal,
                                  DeltaMs, trm, RooBDecay.SingleSided)
    
    time_signal             = RooEffProd('time_signal','time_signal',time_signal_noacc,tacc)

    #The signal - true ID
    trueid_signal = RooGenericPdf("trueid_signal","exp(-100.*abs(@0-1))",RooArgList(trueIDVar_B))
    
    
    #The Bs->DsK - total
    timeerr_signal = RooProdPdf('signal_timeerr', 'signal_timeerr',  RooArgSet(terr_signal),
                                RooFit.Conditional(RooArgSet(time_signal),
                                                   RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #exit(0)
    #-------------------------------------------------- Bd -> DK ----------------------------------------------------#

    m = TString("Bd2DK")
    MDFitter_dk = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, dim, debug)

    #The Bd->DK - acceptance - tacc_powlaw
    tacc_dk = tacc
    
    #The Bd->DK - resolution
    trm_dk = trm
    kfactor_dk = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bd2DK_both"), debug)
    trm_kf_dk = RooKResModel('kresmodel_dk', 'kresmodel_dk', trm_dk, kfactor_dk, kFactor,  RooArgSet(Gammad, DeltaGammad, DeltaMd))
    
    #The Bd->DK - time
    tagEff_dk = []
    tagEffList_dk = RooArgList()
    for i in range(0,3):
        tagEff_dk.append(RooRealVar('tagEff_dk_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dk"][i]))
        print tagEff_dk[i].GetName()
        tagEffList_dk.add(tagEff_dk[i])
                                   
    
    C_dk    = RooRealVar('C_dk', 'C coeff. dk', 1.)
    S_dk    = RooRealVar('S_dk', 'S coeff. dk', 0.)
    D_dk    = RooRealVar('D_dk', 'D coeff. dk', 0.)
    Sbar_dk    = RooRealVar('Sbar_dk', 'Sbar coeff. dk', 0.)
    Dbar_dk    = RooRealVar('Dbar_dk', 'Dbar coeff. dk', 0.)
    
    aProd_dk   = RooConstVar('aprod_dk',   'aprod_dk',   myconfigfile["aprod_dk"])        # production asymmetry
    aDet_dk    = RooConstVar('adet_dk',    'adet_dk',    myconfigfile["adet_dk"])         # detector asymmetry
    aTagEff_dk = []
    aTagEffList_dk = RooArgList()
    for i in range(0,3):
        aTagEff_dk.append(RooRealVar('aTagEff_dk_'+str(i+1), 'atageff', myconfigfile["atageff_dk"][i]))
        print aTagEff_dk[i].GetName()
        aTagEffList_dk.add(aTagEff_dk[i])
        
    
    #The Bd->DPi - mistag
    mistag_dk = mistagBdPDFList
    
    otherargs_dk = [ tagOmegaComb, mistag_dk, tagEffList_dk ]
    otherargs_dk.append(tagOmegaListBd)
    otherargs_dk.append(aProd_dk)
    otherargs_dk.append(aDet_dk)
    otherargs_dk.append(aTagEffList_dk)
                    

    cosh_dk = DecRateCoeff('dk_cosh', 'dk_cosh', DecRateCoeff.CPEven,
                           idVar_B, tagDecComb,  one,      one,      *otherargs_dk)
    sinh_dk = DecRateCoeff('dk_sinh', 'dk_sinh', flag | DecRateCoeff.CPEven,
                           idVar_B, tagDecComb,  D_dk,    Dbar_dk, *otherargs_dk)
    cos_dk  = DecRateCoeff('dk_cos',  'dk_cos' , DecRateCoeff.CPOdd,
                           idVar_B, tagDecComb, C_dk,    C_dk,    *otherargs_dk)
    sin_dk  = DecRateCoeff('dk_sin',  'dk_sin',  flag | DecRateCoeff.CPOdd,
                           idVar_B, tagDecComb,  Sbar_dk, S_dk,    *otherargs_dk)

    time_dk_noacc  = RooBDecay('time_dk_noacc','time_dk_noacc', timeVar_B, TauInvGd, DeltaGammad,
                         cosh_dk, sinh_dk, cos_dk, sin_dk,
                         DeltaMd, trm_dk, RooBDecay.SingleSided)
    
    
    time_dk             = RooEffProd('time_dk','time_dk',time_dk_noacc, tacc_dk)
    
    #The Bd->DK - true ID
    trueid_dk = RooGenericPdf("trueid_dk","exp(-100.*abs(@0-2))",RooArgList(trueIDVar_B))
    
    #The Bd->DPi - time error
    terr_dk = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bd2DK"), debug)
        
    #The Bd->DK - total
    timeerr_dk = RooProdPdf('dk_timeerr', 'dk_timeerr',  RooArgSet(terr_dk),
                            RooFit.Conditional(RooArgSet(time_dk),
                                               RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
                                            
    #-------------------------------------------------- Bd -> DPi ----------------------------------------------------#                                      

    m = TString("Bd2DPi")
    MDFitter_dpi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, dim, debug)

    #The Bd->DPi - acceptance - tacc_powlaw                                                                                                                  
    tacc_dpi = tacc

    #The Bd->DPi - resolution                                                                                                                                
    trm_dpi = trm
    kfactor_dpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bd2DK_both"), debug)
    trm_kf_dpi = RooKResModel('kresmodel_dpi', 'kresmodel_dpi', trm_dpi, kfactor_dpi, kFactor,  RooArgSet(Gammad, DeltaGammad, DeltaMd))

    #The Bd->DK - time                                                                                                                                         
    tagEff_dpi = []
    tagEffList_dpi = RooArgList()
    for i in range(0,3):
        tagEff_dpi.append(RooRealVar('tagEff_dpi_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dpi"][i]))
        print tagEff_dpi[i].GetName()
        tagEffList_dpi.add(tagEff_dpi[i])

    #First generate the observables                                                                                                                           
    ACPobs_dpi = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_d"], myconfigfile["ArgLbarfbar_d"], myconfigfile["ModLf_d"])
    
    C_dpi     = RooRealVar('C_dpi','C_dpi',ACPobs_dpi.Cf())
    S_dpi     = RooRealVar('S_dpi','S_dpi',ACPobs_dpi.Sf())
    D_dpi     = RooRealVar('D_dpi','D_dpi',ACPobs_dpi.Df())
    Sbar_dpi  = RooRealVar('Sbar_dpi','Sbar_dpi',ACPobs_dpi.Sfbar())
    Dbar_dpi  = RooRealVar('Dbar_dpi','Dbar_dpi',ACPobs_dpi.Dfbar())

    aProd_dpi   = RooConstVar('aprod_dpi',   'aprod_dpi',   myconfigfile["aprod_dpi"])        # production asymmetry                                               
    aDet_dpi    = RooConstVar('adet_dpi',    'adet_dpi',    myconfigfile["adet_dpi"])         # detector asymmetry                                                 
    aTagEff_dpi = []
    aTagEffList_dpi = RooArgList()
    for i in range(0,3):
        aTagEff_dpi.append(RooRealVar('aTagEff_dpi_'+str(i+1), 'atageff', myconfigfile["atageff_dpi"][i]))
        print aTagEff_dpi[i].GetName()
        aTagEffList_dpi.add(aTagEff_dpi[i])

    #The Bd->DPi - mistag                                                                                                                                     
    mistag_dpi = mistagBdPDFList

    otherargs_dpi = [ tagOmegaComb, mistag_dpi, tagEffList_dpi ]
    otherargs_dpi.append(tagOmegaListBd)
    otherargs_dpi.append(aProd_dpi)
    otherargs_dpi.append(aDet_dpi)
    otherargs_dpi.append(aTagEffList_dpi)


    cosh_dpi = DecRateCoeff('dpi_cosh', 'dpi_cosh', DecRateCoeff.CPEven,
                           idVar_B, tagDecComb,  one,      one,      *otherargs_dpi)
    sinh_dpi = DecRateCoeff('dpi_sinh', 'dpi_sinh', flag | DecRateCoeff.CPEven,
                           idVar_B, tagDecComb,  D_dpi,    Dbar_dpi, *otherargs_dpi)
    cos_dpi  = DecRateCoeff('dpi_cos',  'dpi_cos' , DecRateCoeff.CPOdd,
                           idVar_B, tagDecComb, C_dpi,    C_dpi,    *otherargs_dpi)
    sin_dpi  = DecRateCoeff('dpi_sin',  'dpi_sin',  flag | DecRateCoeff.CPOdd,
                           idVar_B, tagDecComb,  Sbar_dpi, S_dpi,    *otherargs_dpi)

    time_dpi_noacc  = RooBDecay('time_dpi_noacc','time_dpi_noacc', timeVar_B, TauInvGd, DeltaGammad,
                         cosh_dpi, sinh_dpi, cos_dpi, sin_dpi,
                         DeltaMd, trm_dpi, RooBDecay.SingleSided)


    time_dpi             = RooEffProd('time_dpi','time_dpi',time_dpi_noacc, tacc_dpi)

     #The Bd->DK - true ID                                                                                                                                    
    trueid_dpi = RooGenericPdf("trueid_dpi","exp(-100.*abs(@0-2))",RooArgList(trueIDVar_B))

    #The Bd->DPi - time error                                                                                                                                 
    terr_dpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bd2DK"), debug)

    #The Bd->DK - total                                                                                                                                        
    timeerr_dpi = RooProdPdf('dpi_timeerr', 'dpi_timeerr',  RooArgSet(terr_dpi),
                            RooFit.Conditional(RooArgSet(time_dpi),
                                               RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))


    #------------------------------------------------- Bd -> DsK ----------------------------------------------------#

    #The Bd->DsK - acceptance - tacc_powlaw
    tacc_dsk = tacc
    
    #The Bd->DsK - resolution
    trm_dsk = trm
    
    #The Bd->DsK - time
    tagEff_dsk = []
    tagEffList_dsk = RooArgList()
    for i in range(0,3):
        tagEff_dsk.append(RooRealVar('tagEff_dsk_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dsk"][i]))
        print tagEff_dsk[i].GetName()
        tagEffList_dsk.add(tagEff_dsk[i])
                                    
    
    C_dsk    = RooRealVar('C_dsk', 'C coeff. dsk', 1.)
    S_dsk    = RooRealVar('S_dsk', 'S coeff. dsk', 0.)
    D_dsk    = RooRealVar('D_dsk', 'D coeff. dsk', 0.)
    Sbar_dsk    = RooRealVar('Sbar_dsk', 'Sbar coeff. dsk', 0.)
    Dbar_dsk    = RooRealVar('Dbar_dsk', 'Dbar coeff. dsk', 0.)
    
    aProd_dsk   = RooConstVar('aprod_dsk',   'aprod_dsk',   myconfigfile["aprod_dsk"])        # production asymmetry
    aDet_dsk    = RooConstVar('adet_dsk',    'adet_dsk',    myconfigfile["adet_dsk"])         # detector asymmetry

    aTagEff_dsk = []
    aTagEffList_dsk = RooArgList()
    for i in range(0,3):
        aTagEff_dsk.append(RooRealVar('aTagEff_dsk_'+str(i+1), 'atageff', myconfigfile["atageff_dsk"][i]))
        print aTagEff_dsk[i].GetName()
        aTagEffList_dsk.add(aTagEff_dsk[i])
        
        
    #The Bd->DsPi - mistag
    mistag_dsk = mistagBdPDFList

    otherargs_dsk = [ tagOmegaComb, mistag_dsk, tagEffList_dsk ]
    otherargs_dsk.append(tagOmegaListBd)
    otherargs_dsk.append(aProd_dsk)
    otherargs_dsk.append(aDet_dsk)
    otherargs_dsk.append(aTagEffList_dsk)
                    
    
    cosh_dsk = DecRateCoeff('dsk_cosh', 'dsk_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,       one,     *otherargs_dsk)
    sinh_dsk = DecRateCoeff('dsk_sinh', 'dsk_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_dsk,    Dbar_dsk, *otherargs_dsk)
    cos_dsk  = DecRateCoeff('dsk_cos',  'dsk_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb, C_dsk,    C_dsk,    *otherargs_dsk)
    sin_dsk  = DecRateCoeff('dsk_sin',  'dsk_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_dsk, S_dsk,    *otherargs_dsk)
    
    time_dsk_noacc    = RooBDecay('time_dsk_noacc','time_dsk_noacc', timeVar_B, TauInvGd, DeltaGammad,
                                  cosh_dsk, sinh_dsk, cos_dsk, sin_dsk,
                                  DeltaMd,trm_dsk, RooBDecay.SingleSided)
    
    time_dsk             = RooEffProd('time_dsk','time_dsk',time_dsk_noacc,tacc_dsk)
    
    #The Bd->DsK - true ID
    trueid_dsk = RooGenericPdf("trueid_dsk","exp(-100.*abs(@0-3))",RooArgList(trueIDVar_B))
    
    #The Bd->DsK - time error
    terr_dsk = terr_dk = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsK"), debug)
       
    
    #The Bd->DsK - total
    timeerr_dsk = RooProdPdf('dsk_timeerr', 'dsk_timeerr',  RooArgSet(terr_dsk),
                             RooFit.Conditional(RooArgSet(time_dsk),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    
    #------------------------------------------------- Bs -> DsPi ----------------------------------------------------#

    #The Bs->DsPi - acceptance - tacc_powlaw
    tacc_dspi = tacc
    
    #The Bs->DsPi - resolution
    trm_dspi = trm
    kfactor_dspi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bs2DsPi_both"), debug)
    trm_kf_dspi = RooKResModel('kresmodel_dspi', 'kresmodel_dspi', trm_dspi, kfactor_dspi,
                               kFactor,  RooArgSet(Gammas, DeltaGammas, DeltaMs))
        
    
    #The Bs->DsPi - time
    tagEff_dspi = []
    tagEffList_dspi = RooArgList()
    for i in range(0,3):
        tagEff_dspi.append(RooRealVar('tagEff_dspi_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dspi"][i]))
        print tagEff_dspi[i].GetName()
        tagEffList_dspi.add(tagEff_dspi[i])
            
    C_dspi    = RooRealVar('C_dspi', 'C coeff. dspi', 1.)
    S_dspi    = RooRealVar('S_dspi', 'S coeff. dspi', 0.)
    D_dspi    = RooRealVar('D_dspi', 'D coeff. dspi', 0.)
    Sbar_dspi    = RooRealVar('Sbar_dspi', 'Sbar coeff. dspi', 0.)
    Dbar_dspi    = RooRealVar('Dbar_dspi', 'Dbar coeff. dspi', 0.)
    
    aProd_dspi   = RooConstVar('aprod_dspi',   'aprod_dspi',   myconfigfile["aprod_dspi"])        # production asymmetry
    aDet_dspi    = RooConstVar('adet_dspi',    'adet_dspi',    myconfigfile["adet_dspi"])         # detector asymmetry
    aTagEff_dspi = []
    aTagEffList_dspi = RooArgList()
    for i in range(0,3):
        aTagEff_dspi.append(RooRealVar('aTagEff_dspi_'+str(i+1), 'atageff', myconfigfile["atageff_dspi"][i]))
        print aTagEff_dspi[i].GetName()
        aTagEffList_dspi.add(aTagEff_dspi[i])
                                    
    
    mistag_dspi = mistagBsPDFList
    
    otherargs_dspi = [ tagOmegaComb, mistag_dspi, tagEffList_dspi ]
    otherargs_dspi.append(tagOmegaList)
    otherargs_dspi.append(aProd_dspi)
    otherargs_dspi.append(aDet_dspi)
    otherargs_dspi.append(aTagEffList_dspi)
    

    cosh_dspi = DecRateCoeff('dspi_cosh', 'dspi_cosh', DecRateCoeff.CPEven, idVar_B, tagDecComb,
                             one,         one,         *otherargs_dspi)
    sinh_dspi = DecRateCoeff('dspi_sinh', 'dspi_sinh', DecRateCoeff.CPEven, idVar_B, tagDecComb,
                             D_dspi,    Dbar_dspi, *otherargs_dspi)
    cos_dspi  = DecRateCoeff('dspi_cos' , 'dspi_cos' , DecRateCoeff.CPOdd,  idVar_B, tagDecComb,
                             C_dspi,    C_dspi,    *otherargs_dspi)
    sin_dspi  = DecRateCoeff('dspi_sin' , 'dspi_sin' , DecRateCoeff.CPOdd,  idVar_B, tagDecComb,
                             Sbar_dspi, S_dspi,    *otherargs_dspi)
    
    time_dspi_noacc = RooBDecay('time_dspi_noacc','time_dspi_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                cosh_dspi, sinh_dspi, cos_dspi, sin_dspi,
                                DeltaMs, trm_dspi, RooBDecay.SingleSided)
    
    
    time_dspi             = RooEffProd('time_dspi','time_dspi',time_dspi_noacc,tacc_dspi)
    
    #The Bs->DsPi - true ID
    trueid_dspi = RooGenericPdf("trueid_dspi","exp(-100.*abs(@0-4))",RooArgList(trueIDVar_B))
    
    #The Bs->DsPi - time error
    terr_dspi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsPi"), debug)
        
    
    #The Bs->DsPi - total
    timeerr_dspi = RooProdPdf('dspi_timeerr', 'dspi_timeerr',  RooArgSet(terr_dspi),
                              RooFit.Conditional(RooArgSet(time_dspi),
                                                 RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))

    #------------------------------------------------- Lb -> LcK ----------------------------------------------------#

    #The Lb->LcK - mass
    m = TString("Lb2LcK");
    MDFitter_lck = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, dim, debug);

    #The Lb->LcK - acceptance - tacc_powlaw
    tacc_lck = tacc
    
    #The Lb->LcK - resolution
    trm_lck = trm
    kfactor_lck = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Lb2LcK_both"), debug)
    trm_kf_lck = RooKResModel('kresmodel_lck', 'kresmodel_lck', trm_lck, kfactor_lck,
                                                                  kFactor,  RooArgSet(GammaLb, zero, zero))
        
    
    #The Lb->LcK - time
    tagEff_lck = []
    tagEffList_lck = RooArgList()
    for i in range(0,3):
        tagEff_lck.append(RooRealVar('tagEff_lck_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_lck"][i]))
        print tagEff_lck[i].GetName()
        tagEffList_lck.add(tagEff_lck[i])
                                    
    
    C_lck    = RooRealVar('C_lck', 'C coeff. lck', 0.)
    S_lck    = RooRealVar('S_lck', 'S coeff. lck', 0.)
    D_lck    = RooRealVar('D_lck', 'D coeff. lck', 0.)
    Sbar_lck    = RooRealVar('Sbar_lck', 'Sbar coeff. lck', 0.)
    Dbar_lck    = RooRealVar('Dbar_lck', 'Dbar coeff. lck', 0.)
    
    aProd_lck   = RooConstVar('aprod_lck',   'aprod_lck',   myconfigfile["aprod_lck"])        # production asymmetry
    aDet_lck    = RooConstVar('adet_lck',    'adet_lck',    myconfigfile["adet_lck"])         # detector asymmetry
    aTagEff_lck = []
    aTagEffList_lck = RooArgList()
    for i in range(0,3):
        aTagEff_lck.append(RooRealVar('aTagEff_lck_'+str(i+1), 'atageff', myconfigfile["atageff_lck"][i]))
        print aTagEff_lck[i].GetName()
        aTagEffList_lck.add(aTagEff_lck[i])
        
    
    #The Lb->LcK - mistag
    mistag_lck = mistagBdPDFList
    
    otherargs_lck = [ tagOmegaComb, mistag_lck, tagEffList_lck ]
    otherargs_lck.append(tagOmegaListBd)
    otherargs_lck.append(aProd_lck)
    otherargs_lck.append(aDet_lck)
    otherargs_lck.append(aTagEffList_lck)
                    
    
    cosh_lck = DecRateCoeff('lck_cosh', 'lck_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,       one,     *otherargs_lck)
    sinh_lck = DecRateCoeff('lck_sinh', 'lck_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_lck,    Dbar_lck, *otherargs_lck)
    cos_lck  = DecRateCoeff('lck_cos',  'lck_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_lck,    C_lck,    *otherargs_lck)
    sin_lck  = DecRateCoeff('lck_sin',  'lck_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_lck, S_lck,    *otherargs_lck)
    
    time_lck_noacc    = RooBDecay('time_lck_noacc','time_lck_noacc', timeVar_B, TauInvLb, zero,
                            cosh_lck, sinh_lck, cos_lck, sin_lck,
                            zero,trm_lck, RooBDecay.SingleSided)

    time_lck             = RooEffProd('time_lck','time_lck',time_lck_noacc,tacc_lck)

    #The Lb->LcK - true ID
    trueid_lck = RooGenericPdf("trueid_lck","exp(-100.*abs(@0-5))",RooArgList(trueIDVar_B))

    #The Lb->LcK - time error
    terr_lck = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2LcK"), debug)
        
    #The Lb->LcK - total
    timeerr_lck = RooProdPdf('lck_timeerr', 'lck_timeerr',  RooArgSet(terr_lck),
                             RooFit.Conditional(RooArgSet(time_lck),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))


    #------------------------------------------------- Lb -> LcPi ----------------------------------------------------#                                       
 
    #The Lb->LcPi - mass                                                                                                                                      
    m = TString("Lb2LcPi");
    MDFitter_lcpi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, dim, debug);

    #The Lb->LcPi - acceptance - tacc_powlaw                                                                                                                  
    tacc_lcpi = tacc

    #The Lb->LcPi - resolution                                                                                                                               
    trm_lcpi = trm
    kfactor_lcpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Lb2LcK_both"), debug)
    trm_kf_lcpi = RooKResModel('kresmodel_lcpi', 'kresmodel_lcpi', trm_lcpi, kfactor_lcpi,
                               kFactor,  RooArgSet(GammaLb, zero, zero))


    #The Lb->LcPi - time                                                                                                                                      
    tagEff_lcpi = []
    tagEffList_lcpi = RooArgList()
    for i in range(0,3):
        tagEff_lcpi.append(RooRealVar('tagEff_lcpi_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_lcpi"][i]))
        print tagEff_lcpi[i].GetName()
        tagEffList_lcpi.add(tagEff_lcpi[i])

    C_lcpi    = RooRealVar('C_lcpi', 'C coeff. lcpi', 0.)
    S_lcpi    = RooRealVar('S_lcpi', 'S coeff. lcpi', 0.)
    D_lcpi    = RooRealVar('D_lcpi', 'D coeff. lcpi', 0.)
    Sbar_lcpi    = RooRealVar('Sbar_lcpi', 'Sbar coeff. lcpi', 0.)
    Dbar_lcpi    = RooRealVar('Dbar_lcpi', 'Dbar coeff. lcpi', 0.)

    aProd_lcpi   = RooConstVar('aprod_lcpi',   'aprod_lcpi',   myconfigfile["aprod_lcpi"])        # production asymmetry                                
    aDet_lcpi    = RooConstVar('adet_lcpi',    'adet_lcpi',    myconfigfile["adet_lcpi"])         # detector asymmetry                                   
    aTagEff_lcpi = []
    aTagEffList_lcpi = RooArgList()
    for i in range(0,3):
        aTagEff_lcpi.append(RooRealVar('aTagEff_lcpi_'+str(i+1), 'atageff', myconfigfile["atageff_lcpi"][i]))
        print aTagEff_lcpi[i].GetName()
        aTagEffList_lcpi.add(aTagEff_lcpi[i])


    #The Lb->LcPi - mistag                                                                                                                                
    mistag_lcpi = mistagBdPDFList

    otherargs_lcpi = [ tagOmegaComb, mistag_lcpi, tagEffList_lcpi ]
    otherargs_lcpi.append(tagOmegaListBd)
    otherargs_lcpi.append(aProd_lcpi)
    otherargs_lcpi.append(aDet_lcpi)
    otherargs_lcpi.append(aTagEffList_lcpi)

    cosh_lcpi = DecRateCoeff('lcpi_cosh', 'lcpi_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,       one,     *otherargs_lcpi)
    sinh_lcpi = DecRateCoeff('lcpi_sinh', 'lcpi_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_lcpi,    Dbar_lcpi, *otherargs_lcpi)
    cos_lcpi  = DecRateCoeff('lcpi_cos',  'lcpi_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_lcpi,    C_lcpi,    *otherargs_lcpi)
    sin_lcpi  = DecRateCoeff('lcpi_sin',  'lcpi_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_lcpi, S_lcpi,    *otherargs_lcpi)

    time_lcpi_noacc    = RooBDecay('time_lcpi_noacc','time_lcpi_noacc', timeVar_B, TauInvLb, zero,
                            cosh_lcpi, sinh_lcpi, cos_lcpi, sin_lcpi,
                            zero, trm_lcpi, RooBDecay.SingleSided)

    time_lcpi             = RooEffProd('time_lcpi','time_lcpi',time_lcpi_noacc,tacc_lcpi)

    #The Lb->LcK - true ID                                                                                                                                    
    trueid_lcpi = RooGenericPdf("trueid_lcpi","exp(-100.*abs(@0-5))",RooArgList(trueIDVar_B))

    #The Lb->LcK - time error                                                                                                                                 
    terr_lcpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2LcK"), debug)

    #The Lb->LcK - total                                                                                                                                      
    timeerr_lcpi = RooProdPdf('lcpi_timeerr', 'lcpi_timeerr',  RooArgSet(terr_lcpi),
                              RooFit.Conditional(RooArgSet(time_lcpi),
                                                 RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    
    #------------------------------------------------- Lb -> Dsp -------------------------------------------------------#

    #The Lb->Dsp - Bs
    m = TString("Lb2Dsp")
    massB_dsp = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)

    #Thee Lb->Dsp - PIDK
    m = TString("Lb2Dsp")
    PIDK_dsp = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
          

    #The Lb->Dsp - acceptance 
    tacc_dsp = tacc
    
    #The Lb->Dsp - resolution
    trm_dsp = trm
    kfactor_dsp = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Lb2Dsp_both"), debug)
     
    trm_kf_dsp = RooKResModel('kresmodel_dsp', 'kresmodel_dsp', trm_dsp, kfactor_dsp,
                              kFactor,  RooArgSet(GammaLb, zero, zero))
        
    
    #The Lb->Dsp - time
    tagEff_dsp = []
    tagEffList_dsp = RooArgList()
    for i in range(0,3):
        tagEff_dsp.append(RooRealVar('tagEff_dsp_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dsp"][i]))
        print tagEff_dsp[i].GetName()
        tagEffList_dsp.add(tagEff_dsp[i])
            
    C_dsp    = RooRealVar('C_dsp', 'S coeff. dsp', 0.)
    S_dsp    = RooRealVar('S_dsp', 'S coeff. dsp', 0.)
    D_dsp    = RooRealVar('D_dsp', 'D coeff. dsp', 0.)
    Sbar_dsp = RooRealVar('Sbar_dsp', 'Sbar coeff. dsp', 0.)
    Dbar_dsp = RooRealVar('Dbar_dsp', 'Dbar coeff. dsp', 0.)
    
    aProd_dsp   = RooConstVar('aprod_dsp',   'aprod_dsp',   myconfigfile["aprod_dsp"])        # production asymmetry
    aDet_dsp    = RooConstVar('adet_dsp',    'adet_dsp',    myconfigfile["adet_dsp"])         # detector asymmetry
    
    aTagEff_dsp = []
    aTagEffList_dsp = RooArgList()
    for i in range(0,3):
        aTagEff_dsp.append(RooRealVar('aTagEff_dsp_'+str(i+1), 'atageff', myconfigfile["atageff_dsp"][i]))
        print aTagEff_dsp[i].GetName()
        aTagEffList_dsp.add(aTagEff_dsp[i])
                              
                              
    #The Lb->Dsp - mistag
    mistag_dsp = mistagBdPDFList
    
    otherargs_dsp = [ tagOmegaComb, mistag_dsp, tagEffList_dsp ]
    otherargs_dsp.append(tagOmegaListBd)
    otherargs_dsp.append(aProd_dsp)
    otherargs_dsp.append(aDet_dsp)
    otherargs_dsp.append(aTagEffList_dsp)
                    

    cosh_dsp = DecRateCoeff('dsp_cosh', 'dsp_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,       one,             *otherargs_dsp)
    sinh_dsp = DecRateCoeff('dsp_sinh', 'dsp_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_dsp,    Dbar_dsp, *otherargs_dsp)
    cos_dsp  = DecRateCoeff('dsp_cos',  'dsp_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_dsp,    C_dsp,    *otherargs_dsp)
    sin_dsp  = DecRateCoeff('dsp_sin',  'dsp_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_dsp, S_dsp,    *otherargs_dsp)
    
    time_dsp_noacc      = RooBDecay('time_dsp_noacc','time_dsp_noacc', timeVar_B, TauInvLb, zero,
                                  cosh_dsp, sinh_dsp, cos_dsp, sinh_dsp,
                                  zero,trm_dsp, RooBDecay.SingleSided)
    
    time_dsp             = RooEffProd('time_dsp','time_dsp',time_dsp_noacc,tacc_dsp)
    
    #The Lb->Dsp - true ID
    trueid_dsp = RooGenericPdf("trueid_dsp","exp(-100.*abs(@0-6))",RooArgList(trueIDVar_B))
    
    #The Lb->Dsp, Lb->Dsstp - time error
    terr_dsp = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2Dsp"), debug)
       
    #The Lb->Dsp, Lb->Dsstp - total
    timeerr_dsp = RooProdPdf('dsp_timeerr', 'dsp_timeerr',  RooArgSet(terr_dsp),
                             RooFit.Conditional(RooArgSet(time_dsp),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    
    #------------------------------------------------- Lb ->  Dsstp ----------------------------------------------------#
    
    #The Lb->Dsstp - mass
    m = TString("Lb2Dsstp")
    massB_dsstp = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    
    #The Lb->Dsp, Lb->Dsstp - PIDK
    m = TString("Lb2Dsstp")
    PIDK_dsstp = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
       
    #The Lb->Dsp, Lb->Dsstp - acceptance - tacc_powlaw
    tacc_dsstp = tacc
    
    #The Lb->Dsp, Lb->Dsstp - resolution
    trm_dsstp = trm
    kfactor_dsstp = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Lb2Dsstp_both"), debug)
    trm_kf_dsstp = RooKResModel('kresmodel_dsstp', 'kresmodel_dsstp', trm_dsstp, kfactor_dsstp,
                                kFactor,  RooArgSet(GammaLb, zero, zero))
    
    
    #The Lb->Dsp, Lb->Dsstp - time
    tagEff_dsstp = []
    tagEffList_dsstp = RooArgList()
    for i in range(0,3):
        tagEff_dsstp.append(RooRealVar('tagEff_dsstp_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dsstp"][i]))
        print tagEff_dsstp[i].GetName()
        tagEffList_dsstp.add(tagEff_dsstp[i])

    C_dsstp    = RooRealVar('C_dsstp', 'S coeff. dsstp', 0.)
    S_dsstp    = RooRealVar('S_dsstp', 'S coeff. dsstp', 0.)
    D_dsstp    = RooRealVar('D_dsstp', 'D coeff. dsstp', 0.)
    Sbar_dsstp    = RooRealVar('Sbar_dsstp', 'Sbar coeff. dsstp', 0.)
    Dbar_dsstp    = RooRealVar('Dbar_dsstp', 'Dbar coeff. dsstp', 0.)
    
    aProd_dsstp   = RooConstVar('aprod_dsstp',   'aprod_dsstp',   myconfigfile["aprod_dsstp"])        # production asymmetry
    aDet_dsstp    = RooConstVar('adet_dsstp',    'adet_dsstp',    myconfigfile["adet_dsstp"])         # detector asymmetry
    
    aTagEff_dsstp = []
    aTagEffList_dsstp = RooArgList()
    for i in range(0,3):
        aTagEff_dsstp.append(RooRealVar('aTagEff_dsstp_'+str(i+1), 'atageff', myconfigfile["atageff_dsstp"][i]))
        print aTagEff_dsstp[i].GetName()
        aTagEffList_dsstp.add(aTagEff_dsstp[i])
        
    #The Lb->Dsstp - mistag
    mistag_dsstp = mistagBdPDFList
    
    otherargs_dsstp = [ tagOmegaComb, mistag_dsstp, tagEffList_dsstp ]
    otherargs_dsstp.append(tagOmegaListBd)
    otherargs_dsstp.append(aProd_dsstp)
    otherargs_dsstp.append(aDet_dsstp)
    otherargs_dsstp.append(aTagEffList_dsstp)
    
    
    cosh_dsstp = DecRateCoeff('dsstp_cosh', 'dsstp_cosh', DecRateCoeff.CPEven,
                                idVar_B, tagDecComb,  one,       one,             *otherargs_dsstp)
    sinh_dsstp = DecRateCoeff('dsstp_sinh', 'dsstp_sinh', flag | DecRateCoeff.CPEven,
                                idVar_B, tagDecComb,  D_dsstp,    Dbar_dsstp, *otherargs_dsstp)
    cos_dsstp  = DecRateCoeff('dsstp_cos',  'dsstp_cos' , DecRateCoeff.CPOdd,
                               idVar_B, tagDecComb,  C_dsstp,    C_dsstp,    *otherargs_dsstp)
    sin_dsstp  = DecRateCoeff('dsstp_sin',  'dsstp_sin',  flag | DecRateCoeff.CPOdd,
                                idVar_B, tagDecComb,  Sbar_dsstp, S_dsstp,    *otherargs_dsstp)
    
    time_dsstp_noacc      = RooBDecay('time_dsstp_noacc','time_dsstp_noacc', timeVar_B, TauInvLb, zero,
                                        cosh_dsstp, sinh_dsstp, cos_dsstp, sinh_dsstp,
                                        zero,trm_dsstp, RooBDecay.SingleSided)
    
    time_dsstp             = RooEffProd('time_dsstp','time_dsstp',time_dsstp_noacc,tacc_dsstp)
    
    #The Lb->Dsstp - true ID
    trueid_dsstp = RooGenericPdf("trueid_dsstp","exp(-100.*abs(@0-6))",RooArgList(trueIDVar_B))
    
    #The Lb->Dsstp - time error
    terr_dsstp = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2Dsstp"), debug)
    
    #The Lb->Dsstp - total
    timeerr_dsstp = RooProdPdf('dsstp_timeerr', 'dsstp_timeerr',  RooArgSet(terr_dsstp),
                                 RooFit.Conditional(RooArgSet(time_dsstp),
                                                    RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
        
    
    #------------------------------------------------- Combinatorial ----------------------------------------------------#
    
    #The combinatorics - PIDK
    fracPIDKComb1 = RooRealVar("CombBkg_fracPIDKComb1", "CombBkg_fracPIDKComb1",  myconfigfile["fracPIDKComb1"])
    fracPIDKComb2 = RooRealVar("CombBkg_fracPIDKComb2", "CombBkg_fracPIDKComb2",  myconfigfile["fracPIDKComb2"])
    m = TString("CombK")
    PIDK_combo_K = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("CombPi")
    PIDK_combo_Pi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("CombP")
    PIDK_combo_P = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    name = "ShapePIDKAll_Comb";
    PIDK_combo = RooAddPdf("ShapePIDKAll_combo","ShapePIDKAll_combo",
                           RooArgList(PIDK_combo_K, PIDK_combo_Pi, PIDK_combo_P), RooArgList(fracPIDKComb1, fracPIDKComb2), true)
    
    #The combinatorics - acceptance - tacc_powlaw
    tacc_combo = tacc
    
    #The combinatorics - resolution
    trm_combo = trm
    
    #The combinatorics - time
    tagEff_combo = []
    tagEffList_combo = RooArgList()
    for i in range(0,3):
        tagEff_combo.append(RooRealVar('tagEff_combo_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_combo"][i]))
        print tagEff_combo[i].GetName()
        tagEffList_combo.add(tagEff_combo[i])
        
        
    C_combo       = RooRealVar('C_combo', 'C coeff. combo', 0.)
    S_combo       = RooRealVar('S_combo', 'S coeff. combo', 0.)
    D_combo       = RooRealVar('D_combo', 'D coeff. combo', 0.)
    Sbar_combo    = RooRealVar('Sbar_combo', 'Sbar coeff. combo', 0.)
    Dbar_combo    = RooRealVar('Dbar_combo', 'Dbar coeff. combo', 0.)

    aProd_combo   = RooConstVar('aprod_combo',   'aprod_combo',   myconfigfile["aprod_combo"])        # production asymmetry
    aDet_combo    = RooConstVar('adet_combo',    'adet_combo',    myconfigfile["adet_combo"])         # detector asymmetry
    aTagEff_combo = []
    aTagEffList_combo = RooArgList()
    for i in range(0,3):
        aTagEff_combo.append(RooRealVar('aTagEff_combo_'+str(i+1), 'atageff', myconfigfile["atageff_combo"][i]))
        print aTagEff_combo[i].GetName()
        aTagEffList_combo.add(aTagEff_combo[i])
        

    #The combinatorics - mistag
    mistag_combo = mistagCombPDFList
    
    otherargs_combo = [ tagOmegaComb, mistag_combo, tagEffList_combo ]
    otherargs_combo.append(tagOmegaList)
    otherargs_combo.append(aProd_combo)
    otherargs_combo.append(aDet_combo)
    otherargs_combo.append(aTagEffList_combo)
                    
    
    cosh_combo = DecRateCoeff('combo_cosh', 'combo_cosh', DecRateCoeff.CPEven,
                              idVar_B, tagDecComb,  one,        one,        *otherargs_combo)
    sinh_combo = DecRateCoeff('combo_sinh', 'combo_sinh', flag | DecRateCoeff.CPEven,
                              idVar_B, tagDecComb,  D_combo,    Dbar_combo, *otherargs_combo)
    cos_combo  = DecRateCoeff('combo_cos',  'combo_cos' , DecRateCoeff.CPOdd,
                              idVar_B, tagDecComb,  C_combo,    C_combo,    *otherargs_combo)
    sin_combo  = DecRateCoeff('combo_sin',  'combo_sin',  flag | DecRateCoeff.CPOdd,
                              idVar_B, tagDecComb,  Sbar_combo, S_combo,    *otherargs_combo)
    
    time_combo_noacc    = RooBDecay('time_combo_noacc','time_combo_noacc', timeVar_B, TauInvCombo, zero,
                              cosh_combo, sinh_combo, cos_combo, sin_combo,
                              zero,trm_combo, RooBDecay.SingleSided)
    
    time_combo             = RooEffProd('time_combo','time_combo',time_combo_noacc, tacc_combo)

    #The combinatorics - true ID
    trueid_combo = RooGenericPdf("trueid_combo","exp(-100.*abs(@0-10))",RooArgList(trueIDVar_B))
    
    #The combinatorics - time error
    terr_combo = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_CombBkg"), debug)
    
    timeerr_combo = RooProdPdf('combo_timeerr', 'combo_timeerr',  RooArgSet(terr_combo),
                               RooFit.Conditional(RooArgSet(time_combo),
                                                  RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))

    #------------------------------------------------- Low mass K ----------------------------------------------------#
    
    #The low mass - mass B
    m = TString("Bs2DsKst")
    massB_lm1 = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug);

    #The low mass - PIDK
    PIDK_lm1 = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug);
            
    #The low mass - acceptance - tacc_powlaw
    tacc_lm1 = tacc

    #The low mass - resolution
    trm_lm1 = trm
    #kfactor_lm1 = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bd2DK_both"), debug)
    #trm_kf_lm1 = RooKResModel('kresmodel_dk', 'kresmodel_dk', trm_dk, kfactor_dk, kFactor,  RooArgSet(Gammad, DeltaGammad, DeltaMd))
        

    #The low mass - time
    ACPobs_lm1 = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"], myconfigfile["ArgLbarfbar_s"], myconfigfile["ModLf_s"])
    
    C_lm1     = RooRealVar('C_lm1','C_lm1',ACPobs_lm1.Cf())
    S_lm1     = RooRealVar('S_lm1','S_lm1',ACPobs_lm1.Sf())
    D_lm1     = RooRealVar('D_lm1','D_lm1',ACPobs_lm1.Df())
    Sbar_lm1  = RooRealVar('Sbar_lm1','Sbar_lm1',ACPobs_lm1.Sfbar())
    Dbar_lm1  = RooRealVar('Dbar_lm1','Dbar_lm1',ACPobs_lm1.Dfbar())
    
    tagEff_lm1 = []
    tagEffList_lm1 = RooArgList()
    for i in range(0,3):
        tagEff_lm1.append(RooRealVar('tagEff_lm1_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_lm1"][i]))
        print tagEff_lm1[i].GetName()
        tagEffList_lm1.add(tagEff_lm1[i])
        
    
    aProd_lm1   = RooConstVar('aprod_lm1',   'aprod_lm1',   myconfigfile["aprod_lm1"])        # production asymmetry
    aDet_lm1    = RooConstVar('adet_lm1',    'adet_lm1',    myconfigfile["adet_lm1"])         # detector asymmetry
    aTagEff_lm1 = []
    aTagEffList_lm1 = RooArgList()
    for i in range(0,3):
        aTagEff_lm1.append(RooRealVar('aTagEff_lm1_'+str(i+1), 'atageff', myconfigfile["atageff_lm1"][i]))
        print aTagEff_lm1[i].GetName()
        aTagEffList_lm1.add(aTagEff_lm1[i])
        

        
    #The low mass - mistag
    mistag_lm1 = mistagBsPDFList
    
    otherargs_lm1 = [ tagOmegaComb, mistag_lm1, tagEffList_lm1 ]
    otherargs_lm1.append(tagOmegaList)
    otherargs_lm1.append(aProd_lm1)
    otherargs_lm1.append(aDet_lm1)
    otherargs_lm1.append(aTagEffList_lm1)
                    

    flag_lm1 = 0 #DecRateCoeff.AvgDelta

    cosh_lm1 = DecRateCoeff('lm1_cosh', 'lm1_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,      one,      *otherargs_lm1)
    sinh_lm1 = DecRateCoeff('lm1_sinh', 'lm1_sinh', flag_lm1 | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_lm1,    Dbar_lm1, *otherargs_lm1)
    cos_lm1  = DecRateCoeff('lm1_cos',  'lm1_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_lm1,    C_lm1,    *otherargs_lm1)
    sin_lm1  = DecRateCoeff('lm1_sin',  'lm1_sin',  flag_lm1 | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                            idVar_B, tagDecComb,  S_lm1, Sbar_lm1,    *otherargs_lm1)
    
    time_lm1_noacc    = RooBDecay('time_lm1_noacc','time_lm1_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_lm1, sinh_lm1, cos_lm1, sin_lm1,
                                  DeltaMs,trm_lm1, RooBDecay.SingleSided)
    
    
    time_lm1             = RooEffProd('time_lm1','time_lm1',time_lm1_noacc,tacc_lm1)
                                                    
    #The low mass - true ID
    trueid_lm1 = RooGenericPdf("trueid_lm1","exp(-100.*abs(@0-7))",RooArgList(trueIDVar_B))
    
    #The low mass - time error
    terr_lm1 = terr_signal     
    
    #The low mass - total
    timeerr_lm1 = RooProdPdf('lm1_timeerr', 'lm1_timeerr',  RooArgSet(terr_lm1),
                             RooFit.Conditional(RooArgSet(time_lm1),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))

    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

    #The low mass - pi - mass B
    m = TString("Bs2DsstPi")
    massB_dsstpi = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    
    #the low mass - pi - pidk
    m = TString("Bs2DsstPi")
    PIDK_dsstpi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
                
    #The low mass - acceptance - tacc_powlaw
    tacc_dsstpi = tacc
        
    #The low mass - resolution
    trm_dsstpi = trm
    kfactor_dsstpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bs2DsstPi_both"), debug)
    trm_kf_dsstpi = RooKResModel('kresmodel_dsstpi', 'kresmodel_dsstpi',
                                 trm_dsstpi, kfactor_dsstpi, kFactor,  RooArgSet(Gammas, DeltaGammas, DeltaMs))
    
    #The low mass - time
    tagEff_dsstpi = []
    tagEffList_dsstpi = RooArgList()
    for i in range(0,3):
        tagEff_dsstpi.append(RooRealVar('tagEff_dsstpi_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dsstpi"][i]))
        print tagEff_dsstpi[i].GetName()
        tagEffList_dsstpi.add(tagEff_dsstpi[i])
            
    C_dsstpi       = RooRealVar('C_dsstpi', 'C coeff. dsstpi', 1.)
    S_dsstpi       = RooRealVar('S_dsstpi', 'S coeff. dsstpi', 0.)
    D_dsstpi       = RooRealVar('D_dsstpi', 'D coeff. dsstpi', 0.)
    Sbar_dsstpi    = RooRealVar('Sbar_dsstpi', 'Sbar coeff. dsstpi', 0.)
    Dbar_dsstpi    = RooRealVar('Dbar_dsstpi', 'Dbar coeff. dsstpi', 0.)
    
    aProd_dsstpi   = RooConstVar('aprod_dsstpi',   'aprod_dsstpi',   myconfigfile["aprod_dsstpi"])        # production asymmetry
    aDet_dsstpi    = RooConstVar('adet_dsstpi',    'adet_dsstpi',    myconfigfile["adet_dsstpi"])         # detector asymmetry
    aTagEff_dsstpi = []
    aTagEffList_dsstpi = RooArgList()
    for i in range(0,3):
        aTagEff_dsstpi.append(RooRealVar('aTagEff_dsstpi_'+str(i+1), 'atageff', myconfigfile["atageff_dsstpi"][i]))
        print aTagEff_dsstpi[i].GetName()
        aTagEffList_dsstpi.add(aTagEff_dsstpi[i])
        
    
    #The low mass - mistag
    mistag_dsstpi = mistagBsPDFList
    
    otherargs_dsstpi = [ tagOmegaComb, mistag_dsstpi, tagEffList_dsstpi ]
    otherargs_dsstpi.append(tagOmegaList)
    otherargs_dsstpi.append(aProd_dsstpi)
    otherargs_dsstpi.append(aDet_dsstpi)
    otherargs_dsstpi.append(aTagEffList_dsstpi)
    
    cosh_dsstpi = DecRateCoeff('dsstpi_cosh', 'dsstpi_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,      one,      *otherargs_dsstpi)
    sinh_dsstpi = DecRateCoeff('dsstpi_sinh', 'dsstpi_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_dsstpi,    Dbar_dsstpi, *otherargs_dsstpi)
    cos_dsstpi  = DecRateCoeff('dsstpi_cos',  'dsstpi_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_dsstpi,    C_dsstpi,    *otherargs_dsstpi)
    sin_dsstpi  = DecRateCoeff('dsstpi_sin',  'dsstpi_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_dsstpi, S_dsstpi,    *otherargs_dsstpi)
    
    time_dsstpi_noacc    = RooBDecay('time_dsstpi_noacc','time_dsstpi_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_dsstpi, sinh_dsstpi, cos_dsstpi, sin_dsstpi,
                                  DeltaMs,trm_dsstpi, RooBDecay.SingleSided)
    
    time_dsstpi             = RooEffProd('time_dsstpi','time_dsstpi',time_dsstpi_noacc,tacc_dsstpi)
    
    #The low mass - true ID true
    trueid_dsstpi = RooGenericPdf("trueid_dsstpi","exp(-100.*abs(@0-8))",RooArgList(trueIDVar_B))
    
    #The low mass - time error
    terr_dsstpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsstPi"), debug)
    
    #The low mass - total
    timeerr_dsstpi = RooProdPdf('dsstpi_timeerr', 'dsstpi_timeerr',  RooArgSet(terr_dsstpi),
                                RooFit.Conditional(RooArgSet(time_dsstpi),
                                                   RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    
        
    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

    #The low mass - pi - mass B
    m = TString("Bs2DsRho")
    massB_dsrho = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    
    #The low mass - pi - pidk
    m = TString("Bs2DsRho")
    PIDK_dsrho = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
        
    #The low mass - acceptance - tacc_powlaw
    tacc_dsrho = tacc

    #The low mass - resolution
    trm_dsrho = trm
    kfactor_dsrho = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bs2DsRho_both"), debug)
    trm_kf_dsrho = RooKResModel('kresmodel_dsrho', 'kresmodel_dsrho',
                                trm_dsrho, kfactor_dsrho, kFactor,  RooArgSet(Gammas, DeltaGammas, DeltaMs))

    #The low mass - time
    tagEff_dsrho = []
    tagEffList_dsrho = RooArgList()
    for i in range(0,3):
        tagEff_dsrho.append(RooRealVar('tagEff_dsrho_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dsrho"][i]))
        print tagEff_dsrho[i].GetName()
        tagEffList_dsrho.add(tagEff_dsrho[i])
        

    C_dsrho    = RooRealVar('C_dsrho', 'C coeff. dsrho', 1.)
    S_dsrho    = RooRealVar('S_dsrho', 'S coeff. dsrho', 0.)
    D_dsrho    = RooRealVar('D_dsrho', 'D coeff. dsrho', 0.)
    Sbar_dsrho    = RooRealVar('Sbar_dsrho', 'Sbar coeff. dsrho', 0.)
    Dbar_dsrho    = RooRealVar('Dbar_dsrho', 'Dbar coeff. dsrho', 0.)
    
    
    aProd_dsrho   = RooConstVar('aprod_dsrho',   'aprod_dsrho',   myconfigfile["aprod_dsrho"])        # production asymmetry
    aDet_dsrho    = RooConstVar('adet_dsrho',    'adet_dsrho',    myconfigfile["adet_dsrho"])         # detector asymmetry
    aTagEff_dsrho = []
    aTagEffList_dsrho = RooArgList()
    for i in range(0,3):
        aTagEff_dsrho.append(RooRealVar('aTagEff_dsrho_'+str(i+1), 'atageff', myconfigfile["atageff_dsrho"][i]))
        print aTagEff_dsrho[i].GetName()
        aTagEffList_dsrho.add(aTagEff_dsrho[i])
        
        
    #The low mass - mistag
    mistag_dsrho = mistagBsPDFList
    
    otherargs_dsrho = [ tagOmegaComb, mistag_dsrho, tagEffList_dsrho ]
    otherargs_dsrho.append(tagOmegaList)
    otherargs_dsrho.append(aProd_dsrho)
    otherargs_dsrho.append(aDet_dsrho)
    otherargs_dsrho.append(aTagEffList_dsrho)
    
    cosh_dsrho = DecRateCoeff('dsrho_cosh', 'dsrho_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,      one,      *otherargs_dsrho)
    sinh_dsrho = DecRateCoeff('dsrho_sinh', 'dsrho_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_dsrho,    Dbar_dsrho, *otherargs_dsrho)
    cos_dsrho  = DecRateCoeff('dsrho_cos',  'dsrho_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_dsrho,    C_dsrho,    *otherargs_dsrho)
    sin_dsrho  = DecRateCoeff('dsrho_sin',  'dsrho_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_dsrho, S_dsrho,    *otherargs_dsrho)

    time_dsrho_noacc    = RooBDecay('time_dsrho_noacc','time_dsrho_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_dsrho, sinh_dsrho, cos_dsrho, sin_dsrho,
                                  DeltaMs,trm_dsrho, RooBDecay.SingleSided)

    time_dsrho             = RooEffProd('time_dsrho','time_dsrho',time_dsrho_noacc,tacc_dsrho)
    
    #The low mass - true ID true
    trueid_dsrho = RooGenericPdf("trueid_dsrho","exp(-100.*abs(@0-8))",RooArgList(trueIDVar_B))
    
    #The low mass - time error
    terr_dsrho = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsRho"), debug)
    
    #The low mass - total
    timeerr_dsrho = RooProdPdf('dsrho_timeerr', 'dsrho_timeerr',  RooArgSet(terr_dsrho),
                               RooFit.Conditional(RooArgSet(time_dsrho),
                                                            RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
                               
                               
    #------------------------------------------------- Signal -----------------------------------------------------#
    for i in range(0,5):
        #The signal - mass
        
        meanVarBs.append(RooRealVar(   "DblCBBsPDF_mean_%s"%(nameDs2[i]) ,  "mean",    myconfigfile["mean"][i]    ))
        sigma1VarBs.append(RooRealVar( "DblCBBsPDF_sigma1_%s"%(nameDs2[i]), "sigma1",  myconfigfile["sigma1"][i]  ))
        sigma2VarBs.append(RooRealVar( "DblCBBsPDF_sigma2_%s"%(nameDs2[i]), "sigma2",  myconfigfile["sigma2"][i]  ))
        alpha1VarBs.append(RooRealVar( "DblCBBsPDF_alpha1_%s"%(nameDs2[i]), "alpha1",  myconfigfile["alpha1"][i]  ))
        alpha2VarBs.append(RooRealVar( "DblCBBsPDF_alpha2_%s"%(nameDs2[i]), "alpha2",  myconfigfile["alpha2"][i]  ))
        n1VarBs.append(RooRealVar(     "DblCBBsPDF_n1_%s"%(nameDs2[i]),     "n1",      myconfigfile["n1"][i]      ))
        n2VarBs.append(RooRealVar(     "DblCBBsPDF_n2_%s"%(nameDs2[i]),     "n2",      myconfigfile["n2"][i]      ))
        fracVarBs.append(RooRealVar(   "DblCBBsPDF_frac_%s"%(nameDs2[i]),   "frac",    myconfigfile["frac"][i]    ))
    
        num_signal.append(RooRealVar("num_signal_%s"%(nameDs2[i]),"num_signal_%s"%(nameDs2[i]), myconfigfile["num_signal"][i]*size))
        evNum += myconfigfile["num_signal"][i]*size
        print myconfigfile["num_signal"][i]*size

        massB_signal.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBs[i],
                                                                        sigma1VarBs[i], alpha1VarBs[i], n1VarBs[i],
                                                                        sigma2VarBs[i], alpha2VarBs[i], n2VarBs[i], fracVarBs[i],
                                                                        num_signal[i], nameDs[i].Data(), "Bs", debug ))
                               
        #The signal - mass Ds
    
        meanVarDs.append(RooRealVar(   "DblCBDsPDF_mean_%s"%(nameDs2[i]) ,  "mean",    myconfigfile["meanDs"][i]    ))
        sigma1VarDs.append(RooRealVar( "DblCBDsPDF_sigma1_%s"%(nameDs2[i]), "sigma1",  myconfigfile["sigma1Ds"][i]  ))
        sigma2VarDs.append(RooRealVar( "DblCBDsPDF_sigma2_%s"%(nameDs2[i]), "sigma2",  myconfigfile["sigma2Ds"][i]  ))
        alpha1VarDs.append(RooRealVar( "DblCBDsPDF_alpha1_%s"%(nameDs2[i]), "alpha1",  myconfigfile["alpha1Ds"][i]  ))
        alpha2VarDs.append(RooRealVar( "DblCBDsPDF_alpha2_%s"%(nameDs2[i]), "alpha2",  myconfigfile["alpha2Ds"][i]  ))
        n1VarDs.append(RooRealVar(     "DblCBDsPDF_n1_%s"%(nameDs2[i]),     "n1",      myconfigfile["n1Ds"][i]      ))
        n2VarDs.append(RooRealVar(     "DblCBDsPDF_n2_%s"%(nameDs2[i]),     "n2",      myconfigfile["n2Ds"][i]      ))
        fracVarDs.append(RooRealVar(   "DblCBDsPDF_frac_%s"%(nameDs2[i]),   "frac",    myconfigfile["fracDs"][i]    ))
        
        massD_signal.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_D, meanVarDs[i],
                                                                        sigma1VarDs[i], alpha1VarDs[i], n1VarDs[i],
                                                                        sigma2VarDs[i], alpha2VarDs[i], n2VarDs[i], fracVarDs[i],
                                                                        num_signal[i], nameDs[i].Data(), "Ds", debug ))
        
        # The signal - PIDK
        m = TString("Bs2DsK_")+nameDs[i]
        PIDK_signal.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug))
        
        # The signal - MDFitter
        MDFitter_signal.append(RooProdPdf("MDFitter_signal_%s"%(nameDs2[i]),"MDFitter_signal",
                                          RooArgList(massB_signal[i], massD_signal[i], PIDK_signal[i])))
        
        timeandmass_signal.append(RooProdPdf("timeandmass_signal_%s"%(nameDs2[i]),"timeandmass_signal",RooArgList(timeerr_signal,
                                                                                                                  MDFitter_signal[i],
                                                                                                                  trueid_signal))) 
    
    
    #-------------------------------------------------- Bd -> DK ----------------------------------------------------#
                               
        num_dk.append(RooRealVar("num_dk_%s"%(nameDs2[i]),"num_dk",myconfigfile["num_dk"][i]*size))
        evNum += myconfigfile["num_dk"][i]*size
        print myconfigfile["num_dk"][i]*size
               
        timeandmass_dk.append(RooProdPdf("timeandmass_dk_%s"%(nameDs2[i]),"timeandmass_dk",RooArgList(timeerr_dk,
                                                                                                      MDFitter_dk,
                                                                                                      trueid_dk))) 
    #-------------------------------------------------- Bd -> DPi ----------------------------------------------------#                          

        num_dpi.append(RooRealVar("num_dpi_%s"%(nameDs2[i]),"num_dpi",myconfigfile["num_dpi"][i]*size))
        evNum += myconfigfile["num_dpi"][i]*size
        print myconfigfile["num_dpi"][i]*size

        timeandmass_dpi.append(RooProdPdf("timeandmass_dpi_%s"%(nameDs2[i]),"timeandmass_dpi",RooArgList(timeerr_dpi,
                                                                                                         MDFitter_dpi,
                                                                                                         trueid_dpi)))
    
    #------------------------------------------------- Bd -> DsK ----------------------------------------------------#
    
        #The Bd->DsK - mass
        meanVarBd.append(RooRealVar(    "DblCBBdPDF_mean_%s"%(nameDs2[i]) ,  "mean",    myconfigfile["mean"][i]-86.8))
        sigma1VarBd.append(RooRealVar( "DblCBBdPDF_sigma1_%s"%(nameDs2[i]), "sigma1",  myconfigfile["sigma1"][i]*myconfigfile["ratio1"] ))
        sigma2VarBd.append(RooRealVar(  "DblCBBdPDF_sigma2_%s"%(nameDs2[i]), "sigma2",  myconfigfile["sigma2"][i]*myconfigfile["ratio2"] ))
    
        num_dsk.append(RooRealVar("num_dsk_%s"%(nameDs[i]),"num_dsk",myconfigfile["num_dsk"][i]*size))
        evNum += myconfigfile["num_dsk"][i]*size
        print myconfigfile["num_dsk"][i]*size
                       
        massB_dsk.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBd[i],
                                                                     sigma1VarBd[i], alpha1VarBs[i], n1VarBs[i],
                                                                     sigma2VarBd[i], alpha2VarBs[i], n2VarBs[i],
                                                                     fracVarBs[i], num_dsk[i], nameDs[i].Data(), "Bd", debug ))
        
        # The signal - MDFitter
        massD_dsk.append(massD_signal[i])
        PIDK_dsk.append(PIDK_signal[i])
                
        MDFitter_dsk.append(RooProdPdf("MDFitter_dsk_%s"%(nameDs2[i]),"MDFitter_dsk",RooArgList(massB_dsk[i], massD_dsk[i], PIDK_dsk[i])))
                               
                
        timeandmass_dsk.append(RooProdPdf("timeandmass_dsk_%s"%(nameDs2[i]),"timeandmass_dsk",RooArgList(timeerr_dsk,
                                                                                                         MDFitter_dsk[i],
                                                                                                         trueid_dsk))) #,
                               
          
    #------------------------------------------------- Bs -> DsPi ----------------------------------------------------# 
    
        #The Bs->DsPi - mass B
        #mass_dspi = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace,TString("PhysBkgBsDsPi_m_down_kkpi"), debug) 
        m = TString("Bs2DsPi_")+nameDs[i]
        massB_dspi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug))
    
        #The Bs->DsPi- mass D
        massD_dspi.append(massD_signal[i])
               
        #The Bs->DsPi - PIDK
        PIDK_dspi.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug))
        
        #The Bs->DsPi - MDFitter
        MDFitter_dspi.append(RooProdPdf("MDFitter_dspi_%s"%(nameDs2[i]),"MDFitter_dspi",RooArgList(massB_dspi[i], massD_dspi[i], PIDK_dspi[i])))
                                 
        num_dspi.append(RooRealVar("num_dspi_%s"%(nameDs2[i]),"num_dspi", myconfigfile["num_dspi"][i]*size))
        evNum += myconfigfile["num_dspi"][i]*size
        print myconfigfile["num_dspi"][i]*size
        
        timeandmass_dspi.append(RooProdPdf("timeandmass_dspi_%s"%(nameDs2[i]),"timeandmass_dspi",RooArgList(timeerr_dspi,
                                                                                                            MDFitter_dspi[i],
                                                                                                            trueid_dspi)))
                         
        
              
    #------------------------------------------------- Lb -> LcK ----------------------------------------------------#
    
              
        num_lck.append(RooRealVar("num_lck_%s"%(nameDs2[i]),"num_lck", myconfigfile["num_lck"][i]*size))
        evNum += myconfigfile["num_lck"][i]*size
        print myconfigfile["num_lck"][i]*size
        
        timeandmass_lck.append(RooProdPdf("timeandmass_lck_%s"%(nameDs2[i]),"timeandmass_lck",RooArgList(timeerr_lck,
                                                                                                         MDFitter_lck,
                                                                                                         trueid_lck))) 
        
    #------------------------------------------------- Lb -> LcPi ----------------------------------------------------#                                       

        num_lcpi.append(RooRealVar("num_lcpi_%s"%(nameDs2[i]),"num_lcpi", myconfigfile["num_lcpi"][i]*size))
        evNum += myconfigfile["num_lcpi"][i]*size
        print myconfigfile["num_lcpi"][i]*size

        timeandmass_lcpi.append(RooProdPdf("timeandmass_lcpi_%s"%(nameDs2[i]),"timeandmass_lcpi",RooArgList(timeerr_lcpi,
                                                                                                         MDFitter_lcpi,
                                                                                                         trueid_lcpi)))

        
    #------------------------------------------------- Lb -> Dsstp ----------------------------------------------------#
                               
               
        num_dsstp.append(RooRealVar("num_dsstp_%s"%(nameDs2[i]),"num_dsstp", myconfigfile["num_dsstp"][i]*size))
        evNum += myconfigfile["num_dsstp"][i]*size
        print myconfigfile["num_dsstp"][i]*size

        #The Lb->Dsp, Lb->Dsstp - mass
        massD_dsstp.append(massD_signal[i])
                               
                               
        #The Lb->Dsp, Lb->Dsstp - MDFitter
        MDFitter_dsstp.append(RooProdPdf("MDFitter_dsstp_%s"%(nameDs2[i]),"MDFitter_dsstp",
                                           RooArgList(massB_dsstp, massD_dsstp[i], PIDK_dsstp)))
        
                      
        timeandmass_dsstp.append(RooProdPdf("timeandmass_dsstp_%s"%(nameDs2[i]),"timeandmass_dsstp",RooArgList(timeerr_dsstp,
                                                                                                               MDFitter_dsstp[i],
                                                                                                               trueid_dsstp)))
        

    #------------------------------------------------- Lb -> Dsp ----------------------------------------------------#


        num_dsp.append(RooRealVar("num_dsp_%s"%(nameDs2[i]),"num_dsp", myconfigfile["num_dsp"][i]*size))
        evNum += myconfigfile["num_dsp"][i]*size
        print myconfigfile["num_dsp"][i]*size

        #The Lb->Dsp - mass
        massD_dsp.append(massD_signal[i])
    
    
        #The Lb->Dsp
        MDFitter_dsp.append(RooProdPdf("MDFitter_dsp_%s"%(nameDs2[i]),"MDFitter_dsp",
                                       RooArgList(massB_dsp, massD_dsp[i], PIDK_dsp)))
        
        
        timeandmass_dsp.append(RooProdPdf("timeandmass_dsp_%s"%(nameDs2[i]),"timeandmass_dsp",RooArgList(timeerr_dsp,
                                                                                                         MDFitter_dsp[i],
                                                                                                         trueid_dsp)))
        
         
    
    #------------------------------------------------- Combinatorial ----------------------------------------------------#

        #The combinatorics - mass
        num_combo.append(RooRealVar("num_combo_%s"%(nameDs2[i]),"num_combo", myconfigfile["num_combo"][i]*size))
        evNum += myconfigfile["num_combo"][i]*size
        print myconfigfile["num_combo"][i]*size

        #The combinatorics - mass B
        cBVar.append(RooRealVar("CombBkg_slope_Bs_%s"%(nameDs2[i]),"CombBkg_slope_Bs", myconfigfile["cB"][i]))
        massB_combo.append(RooExponential("massB_combo_%s","massB_combo",massVar_B, cBVar[i]))
        
        #The combinatorics - mass D
        cDVar.append(RooRealVar("CombBkg_slope_Ds_%s"%(nameDs2[i]),"CombBkg_slope_Ds", myconfigfile["cD"][i]))
        fracDsComb.append(RooRealVar("CombBkg_fracDsComb_%s"%(nameDs2[i]), "CombBkg_fracDsComb",  myconfigfile["fracDsComb"][i]))
        massD_combo.append(Bs2Dsh2011TDAnaModels.ObtainComboDs(massVar_D, cDVar[i], fracDsComb[i], massD_signal[i], nameDs[i], debug))
    
        #The combinatorics - MDFitter
        MDFitter_combo.append(RooProdPdf("MDFitter_combo_%s"%(nameDs2[i]),"MDFitter_combo",RooArgList(massB_combo[i], massD_combo[i], PIDK_combo)))
        
              
        timeandmass_combo.append(RooProdPdf("timeandmass_combo_%s"%(nameDs2[i]),"timeandmass_combo",RooArgList(timeerr_combo,
                                                                                                               MDFitter_combo[i],
                                                                                                               trueid_combo))) 
        
        
        #------------------------------------------------- Low mass K ----------------------------------------------------#
    
                
        #The low mass - mass D
        massD_lm1.append(massD_signal[i])
                     
        #The low mass - MDFitter
        MDFitter_lm1.append(RooProdPdf("MDFitter_lm1_%s"%(nameDs2[i]),"MDFitter_lm1",RooArgList(massB_lm1, massD_lm1[i], PIDK_lm1)))
        
        num_lm1.append( RooRealVar("num_lm1_%s"%(nameDs2[i]),"num_lm1",myconfigfile["num_lm1"][i]*size))
        evNum += myconfigfile["num_lm1"][i]*size
        print myconfigfile["num_lm1"][i]*size
        
        timeandmass_lm1.append(RooProdPdf("timeandmass_lm1_%s"%(nameDs2[i]),"timeandmass_lm1",RooArgList(timeerr_lm1,
                                                                                                         MDFitter_lm1[i],
                                                                                                         trueid_lm1))) 
     
          
    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

        num_dsstpi.append(RooRealVar("num_dsstpi_%s"%(nameDs2[i]),"num_dsstpi", myconfigfile["num_dsstpi"][i]*size))
        evNum += myconfigfile["num_dsstpi"][i]*size
        print myconfigfile["num_dsstpi"][i]*size

        #The low mass - mass D
        massD_dsstpi.append(massD_signal[i])
             
                
        #The low mass - MDFitter
        MDFitter_dsstpi.append(RooProdPdf("MDFitter_dsstpi_%s"%(nameDs[i]),"MDFitter_dsstpi",
                                          RooArgList(massB_dsstpi, massD_dsstpi[i], PIDK_dsstpi)))
        
              
        timeandmass_dsstpi.append(RooProdPdf("timeandmass_dsstpi_%s"%(nameDs2[i]),"timeandmass_dsstpi",RooArgList(timeerr_dsstpi,
                                                                                                                  MDFitter_dsstpi[i],
                                                                                                                  trueid_dsstpi)))
                               
    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

        num_dsrho.append(RooRealVar("num_dsrho_%s"%(nameDs2[i]),"num_dsrho", myconfigfile["num_dsrho"][i]*size))
        evNum += myconfigfile["num_dsrho"][i]*size
        print myconfigfile["num_dsrho"][i]*size

        #The low mass - mass D
        massD_dsrho.append(massD_signal[i])


        #The low mass - MDFitter
        MDFitter_dsrho.append(RooProdPdf("MDFitter_dsrho_%s"%(nameDs[i]),"MDFitter_dsrho",
                                         RooArgList(massB_dsrho, massD_dsrho[i], PIDK_dsrho)))


        timeandmass_dsrho.append(RooProdPdf("timeandmass_dsrho_%s"%(nameDs2[i]),"timeandmass_dsrho",RooArgList(timeerr_dsrho,
                                                                                                               MDFitter_dsrho[i],
                                                                                                               trueid_dsrho)))
        print "partial total num of events: ",evNum
    #------------------------------------------------- Total bkg ----------------------------------------------------#
    
        #Total
        pdfList = RooArgList(timeandmass_signal[i],
                             timeandmass_dk[i],timeandmass_dsk[i],timeandmass_dspi[i],
                             timeandmass_lck[i])
        pdfList.add(timeandmass_dsp[i])
        pdfList.add(timeandmass_dsstp[i])
        pdfList.add(timeandmass_combo[i])
        pdfList.add(timeandmass_lm1[i])
        pdfList.add(timeandmass_dsstpi[i])
        pdfList.add(timeandmass_dsrho[i])
        pdfList.add(timeandmass_dpi[i])
        pdfList.add(timeandmass_lcpi[i])

        numList = RooArgList(num_signal[i], num_dk[i], num_dsk[i], num_dspi[i], num_lck[i])
        numList.add(num_dsp[i])
        numList.add(num_dsstp[i])
        numList.add(num_combo[i])
        numList.add(num_lm1[i])
        numList.add(num_dsstpi[i])
        numList.add(num_dsrho[i])
        numList.add(num_dpi[i])
        numList.add(num_lcpi[i])
        
        total_pdf.append(RooAddPdf("total_pdf_%s"%(nameDs2[i]),"total_pdf", pdfList, numList))
                                   
        #total_pdf.append(RooAddPdf("total_pdf_%s"%(nameDs2[i]),"total_pdf",RooArgList(timeandmass_signal[i],timeandmass_lck[i]),
        #                           RooArgList(num_signal[i],num_lck[i])))
        
        #total_pdf[i].Print("v")

    rd = int(rangeDown)
    ru = int(rangeUp)
    
    
    print "Number of generated events: ",evNum

    for i in range(rd,ru) :

        workout = RooWorkspace("workspace","workspace")

        for j in range(0,5):
            
                
            gendata = total_pdf[j].generate(RooArgSet(massVar_B, massVar_D, PIDKVar_B,
                                                      timeVar_B, terrVar_B,
                                                      trueIDVar_B, idVar_B, tagDecComb, tagOmegaComb), 
                                            RooFit.Extended(),
                                            RooFit.NumEvents(evNum))
                                            
            
            #gendata.Print("v")
            #print "Data name: ",gendata.GetName()

            gendata.SetName("dataSetBsDsK_both_"+nameDs2[j])

            #print "Data name: ",gendata.GetName()
            #gendata.Print("v")
            #exit(0)
            #tree = gendata.store().tree()
            #dataName = TString("dataSetBsDsK_both_")+nameDs[j]
            
            #data = SFitUtils.CopyDataForToys(tree,
            #                                 TString(mVar),
            #                                 TString(mdVar),
            #                                 TString(PIDKVar),
            #                                 TString(tVar),
            #                                 TString(terrVar),
            #                                 TString("tagDecComb")+TString("_idx"),
            #                                 TString("tagOmegaComb"),
            #                                 TString(charge)+TString("_idx"),
            #                                 TString(trueID),
            #                                 dataName,
            #                                 debug)
        
            getattr(workout,'import')(gendata)
            del gendata 
        
        #Plot what we just did
        if single :
            
            legend = TLegend( 0.70, 0.65, 0.99, 0.99 )
            
            legend.SetTextSize(0.03)
            legend.SetTextFont(12)
            legend.SetFillColor(4000)
            legend.SetShadowColor(0)
            legend.SetBorderSize(0)
            legend.SetTextFont(132)
            legend.SetHeader("Toy generator")
            
            gr = TGraphErrors(10);
            gr.SetName("gr");
            gr.SetLineColor(kBlack);
            gr.SetLineWidth(2);
            gr.SetMarkerStyle(20);
            gr.SetMarkerSize(1.3);
            gr.SetMarkerColor(kBlack);
            gr.Draw("P");
            legend.AddEntry("gr","Generated data","lep");

            l1 = TLine()
            l1.SetLineColor(kRed-7)
            l1.SetLineWidth(4)
            l1.SetLineStyle(kDashed)
            legend.AddEntry(l1, "Signal B_{s}#rightarrow D_{s}K", "L")
            
            l2 = TLine()
            l2.SetLineColor(kRed)
            l2.SetLineWidth(4)
            legend.AddEntry(l2, "B #rightarrow DK", "L")
            
            l3 = TLine()
            l3.SetLineColor(kGreen-3)
            l3.SetLineWidth(4)
            legend.AddEntry(l3, "#Lambda_{b}#rightarrow #Lambda_{c}K", "L")
            
            l4 = TLine()
            l4.SetLineColor(kBlue-6)
            l4.SetLineWidth(4)
            legend.AddEntry(l4, "B_{s}#rightarrow D_{s}^{(*)}(#pi,#rho)", "L")

            l5 = TLine()
            l5.SetLineColor(kOrange)
            l5.SetLineWidth(4)
            legend.AddEntry(l5, "#Lambda_{b} #rightarrow D_{s}^{(*)}p", "L")
            
            l6 = TLine()
            l6.SetLineColor(kBlue-10)
            l6.SetLineWidth(4)
            legend.AddEntry(l6, "B_{(d,s)}#rightarrow D^{(*)}_{s}K^{(*)}", "L")
            
            l7 = TLine()
            l7.SetLineColor(kMagenta-2)
            l7.SetLineWidth(4)
            legend.AddEntry(l7, "Combinatorial", "L")

            
            gStyle.SetOptLogy(1)
            canv_Bmass = TCanvas("canv_Bmass","canv_Bmass", 1200, 1000)
            frame_Bmass = massVar_B.frame()
            frame_Bmass.SetTitle('')
            data.plotOn(frame_Bmass,RooFit.Binning(100))
            '''
            total_pdf.plotOn(frame_Bmass)
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_signal"),RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dk"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_lck"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_lm1,timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_lm2,timeandmass_dspi"),RooFit.LineColor(kBlue-6))
            #total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dspi"), RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_combo"),RooFit.LineColor(kMagenta-2))
            '''
            frame_Bmass.Draw()
            legend.Draw("same")
            canv_Bmass.Print("DsK_Toys_Bmass.pdf") 

            gStyle.SetOptLogy(1)
            canv_Dmass = TCanvas("canv_Dmass","canv_Dmass",1200, 1000)
            frame_Dmass = massVar_D.frame()
            frame_Dmass.SetTitle('')
            data.plotOn(frame_Dmass,RooFit.Binning(100))
            '''
            total_pdf.plotOn(frame_Dmass)
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_signal"), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dk"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_lck"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_lm1,timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_lm2,timeandmass_dspi"),RooFit.LineColor(kBlue-6))
            #total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dspi"), RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_combo"),RooFit.LineColor(kMagenta-2))
            '''
            frame_Dmass.Draw()
            legend.Draw("same")
            canv_Dmass.Print("DsK_Toys_Dmass.pdf")

            gStyle.SetOptLogy(1)
            canv_PIDK = TCanvas("canv_PIDK","canv_PIDK", 1200, 1000)
            frame_PIDK = PIDKVar_B.frame()
            frame_PIDK.SetTitle('')
            data.plotOn(frame_PIDK,RooFit.Binning(100))
            '''
            total_pdf.plotOn(frame_PIDK)
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_signal"), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dk"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_lck"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_lm1,timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_lm2,timeandmass_dspi"),RooFit.LineColor(kBlue-6))
            #total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dsk"),RooFit.LineColor(kBlue-10))
            #total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dspi"), RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_combo"),RooFit.LineColor(kMagenta-2))
            '''
            frame_PIDK.Draw()
            legend.Draw("same")
            canv_PIDK.Print("DsK_Toys_PIDK.pdf")

            gStyle.SetOptLogy(0)
            canv_Bmistag = TCanvas("canv_Bmistag","canv_Btag", 1200, 1000)
            frame_Bmistag = mistagVar_B.frame()
            frame_Bmistag.SetTitle('')
            data.plotOn(frame_Bmistag,RooFit.Binning(50))
            frame_Bmistag.Draw()
            canv_Bmistag.Print("DsK_Toys_Bmistag.pdf")

            gStyle.SetOptLogy(0)
            canv_Bterr = TCanvas("canv_Bterr","canv_Bterr", 1200, 1000)
            frame_Bterr = terrVar_B.frame()
            frame_Bterr.SetTitle('')
            data.plotOn(frame_Bterr,RooFit.Binning(100))
            #total_pdf.plotOn(frame_Bterr)
            frame_Bterr.Draw()
            canv_Bterr.Print("DsK_Toys_TimeErrors.pdf")

            obs = data.get()
            tagFName = TString(tagdec)+TString("_idx")
            tagF = obs.find(tagFName.Data())
            gStyle.SetOptLogy(0)
            canv_Btag = TCanvas("canv_Btag","canv_Btag", 1200, 1000)
            frame_Btag = tagF.frame()
            frame_Btag.SetTitle('')
            data.plotOn(frame_Btag,RooFit.Binning(5))
            frame_Btag.Draw()
            canv_Btag.Print("DsK_Toys_Tag.pdf")
            
            idFName = TString(charge)+TString("_idx")
            idF = obs.find(idFName.Data())
            gStyle.SetOptLogy(0)
            canv_Bid = TCanvas("canv_Bid","canv_Bid", 1200, 1000)
            frame_Bid = idF.frame()
            frame_Bid.SetTitle('')
            data.plotOn(frame_Bid,RooFit.Binning(2))
            frame_Bid.Draw()
            canv_Bid.Print("DsK_Toys_Charge.pdf")
            
            
            gStyle.SetOptLogy(1)
            
            canv_Btime = TCanvas("canv_Btime","canv_Btime", 1200, 1000)
            frame_Btime = timeVar_B.frame()
            frame_Btime.SetTitle('')
            data.plotOn(frame_Btime,RooFit.Binning(100))
            #total_pdf.plotOn(frame_Btime)
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_signal"),RooFit.LineStyle(2))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_dk"),RooFit.LineStyle(2),RooFit.LineColor(2))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lck"),RooFit.LineStyle(1),RooFit.LineColor(3))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_lm"),RooFit.LineStyle(1),RooFit.LineColor(6))
            #total_pdf.plotOn(frame_Btime,RooFit.Components("time_combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Btime.Draw()
            canv_Btime.Print("DsK_Toys_Btime.pdf")
        if not single :
            workout.writeToFile(dir+"DsK_Toys_Work_"+str(i)+".root")
        else :
            workout.writeToFile("Data_Toys_Single_Work_DsK.root")

        del workout
        
    
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--single',
                   dest = 'single',
                   action = 'store_true',
                   default = False,
                                      )
parser.add_option( '-s','--start',
                   dest = 'rangeDown',
                   default = 0)

parser.add_option( '-e','--end',
                   dest = 'rangeUp',
                   default = 1)

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsKConfigForGenerator5M')

parser.add_option( '--seed',
                   dest = 'seed',
                   default = 746829245)

parser.add_option( '--size',
                   dest = 'size',
                   default = 1)

parser.add_option( '--dir',
                   dest = 'dir',
                   default = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M_2T_MD/')


# -----------------------------------------------------------------------------
if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    import sys
    sys.path.append("../data/")
    
    runBsDsKGenerator( options.debug,  options.single , options.configName,
                       options.rangeDown, options.rangeUp, 
                       options.seed, options.size, options.dir)
    
# -----------------------------------------------------------------------------
                                
