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
    
    fileName  = "work_dspi_pid_53005800_PIDK0_5M_BDTGA.root"
    fileNameData = "work_dspi_pid_53005800_PIDK0_5M_BDTGA.root"
    fileNameTerr = "../data/workspace/MDFitter/template_Data_Terr_BsDsPi.root"
    fileNameMistag = "../data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root"
    fileNameMistagBDPi = "../data/workspace/MDFitter/template_Data_Mistag_BDPi.root"
    fileNameMistagComb = "../data/workspace/MDFitter/template_Data_Mistag_CombBkg.root"
    #fileNameKFactor =  "../data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root"
    #fileNameKFactor =  "../data/workspace/MDFitter/ktemplates.root"
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
    #workKFactor = GeneralUtils.LoadWorkspace(TString(fileNameKFactor),TString(workName), debug)
    #workKFactor.Print("v")
    
   # kFactor = GeneralUtils.GetObservable(workKFactor,TString("kfactorVar"), debug)
   # kFactor.setRange(0.80, 1.10)
    
    '''
    dataKFactorDown = []
    dataKFactorUp   = []
    names = ["Bd2DK","Lb2LcK","Lb2Dsstp","Lb2Dsp","Bs2DsstPi","Bs2DsRho","Bs2DsPi"]
    for i in range(0,7):
        dataNameUp = "kfactor_dataset_"+names[i]+"_up" 
        dataKFactorUp.append(GeneralUtils.GetDataSet(workKFactor,TString(dataNameUp), debug))
        dataKFactorUp[i].Print("v")
        print dataKFactorUp[i].sumEntries()
        dataNameDown = "kfactor_dataset_"+names[i]+"_down"
        dataKFactorDown.append(GeneralUtils.GetDataSet(workKFactor,TString(dataNameDown), debug))
        dataKFactorDown[i].Print("v")
        print dataKFactorDown[i].sumEntries()

    max = [-2.0,-2.0,-2.0,-2.0,-2.0,-2.0,-2.0]
    min = [2.0,2.0,2.0,2.0,2.0,2.0,2.0]
    for i in range(0,7):
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
    for i in range(0,7):
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
    for i in range(0,7):
        kFactor.setRange(minRange[i], maxRange[i])

        name = "kFactor_"+names[i]+"_both"
        pdfKF.append(GeneralUtils.CreateHistPDF(dataKFactorUp[i], dataKFactorDown[i], myconfigfile["lumRatio"],
                                                kFactor, TString(name), 100, debug))
        t = TString("both")
        GeneralUtils.SaveTemplate(NULL, pdfKF[i], kFactor, TString(names[i]), t, plotSet, debug );
        
    workOut = RooWorkspace("workspace","workspace")
    for i in range(0,7):
        getattr(workOut,'import')(pdfKF[i])
        
    workOut.SaveAs("template_MC_KFactor_BsDsK.root")
    workOut.Print("v")
    exit(0)
    '''
    
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
    
    massD_dsk = []
    MDFitter_dsk = []
    timeandmass_dsk = []

    massB_dspi = []
    massD_dspi = []
    PIDK_dspi = []
    MDFitter_dspi = []
    timeandmass_dspi = []
    
    cB1Var = []
    cB2Var = []
    fracBsComb = []
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
    PIDK_dsstpi = []
    MDFitter_dsstpi = []
    timeandmass_dsstpi = []

    massD_dsrho = []
    PIDK_dsrho = []
    MDFitter_dsrho = []
    timeandmass_dsrho = []
               
    timeandmass_dpi = []
    timeandmass_lcpi = []

    num_signal = []
    num_dpi = []
    num_dsk = []
    num_dspi = []
    num_lcpi = []
    num_combo = []
    num_dsstpi = []
    num_dsrho = []
    
    evNum  = 0
#------------------------------------------------- Bs -> DsPi ----------------------------------------------------#

    #The Bs->DsPi - acceptance - tacc_powlaw
    tacc_signal = tacc
    
    #The Bs->DsPi - resolution
    trm_signal = trm
    #kfactor_dspi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bs2DsPi_both"), debug)
    #trm_kf_dspi = RooKResModel('kresmodel_dspi', 'kresmodel_dspi', trm_dspi, kfactor_dspi,
    #                           kFactor,  RooArgSet(Gammas, DeltaGammas, DeltaMs))
        
    
    #The Bs->DsPi - time
    tagEff_signal = []
    tagEffList_signal = RooArgList()
    for i in range(0,3):
        tagEff_signal.append(RooRealVar('tagEff_signal_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_signal"][i]))
        print tagEff_signal[i].GetName()
        tagEffList_signal.add(tagEff_signal[i])
            
    C_signal    = RooRealVar('C_signal', 'C coeff. signal', 1.)
    S_signal    = RooRealVar('S_signal', 'S coeff. signal', 0.)
    D_signal    = RooRealVar('D_signal', 'D coeff. signal', 0.)
    Sbar_signal    = RooRealVar('Sbar_signal', 'Sbar coeff. signal', 0.)
    Dbar_signal    = RooRealVar('Dbar_signal', 'Dbar coeff. signal', 0.)	

    aProd_signal   = RooConstVar('aprod_signal',   'aprod_signal',   myconfigfile["aprod_signal"])        # production asymmetry
    aDet_signal    = RooConstVar('adet_signal',    'adet_signal',    myconfigfile["adet_signal"])         # detector asymmetry
    aTagEff_signal = []
    aTagEffList_signal = RooArgList()
    for i in range(0,3):
        aTagEff_signal.append(RooRealVar('aTagEff_signal_'+str(i+1), 'atageff', myconfigfile["atageff_signal"][i]))
        print aTagEff_signal[i].GetName()
        aTagEffList_signal.add(aTagEff_signal[i])
                                    
    
    mistag_signal = mistagBsPDFList
    
    otherargs_signal = [ tagOmegaComb, mistag_signal, tagEffList_signal ]
    otherargs_signal.append(tagOmegaList)
    otherargs_signal.append(aProd_signal)
    otherargs_signal.append(aDet_signal)
    otherargs_signal.append(aTagEffList_signal)
    
    flag = 0
    cosh_signal = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven, idVar_B, tagDecComb,
                               one,         one,         *otherargs_signal)
    sinh_signal = DecRateCoeff('signal_sinh', 'signal_sinh', DecRateCoeff.CPEven, idVar_B, tagDecComb,
                               D_signal,    Dbar_signal, *otherargs_signal)
    cos_signal  = DecRateCoeff('signal_cos' , 'signal_cos' , DecRateCoeff.CPOdd,  idVar_B, tagDecComb,
                               C_signal,    C_signal,    *otherargs_signal)
    sin_signal  = DecRateCoeff('signal_sin' , 'signal_sin' , DecRateCoeff.CPOdd,  idVar_B, tagDecComb,
                               Sbar_signal, S_signal,    *otherargs_signal)
    
    time_signal_noacc = RooBDecay('time_signal_noacc','time_signal_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_signal, sinh_signal, cos_signal, sin_signal,
                                  DeltaMs, trm_signal, RooBDecay.SingleSided)
    
    
    time_signal             = RooEffProd('time_signal','time_signal',time_signal_noacc,tacc_signal)
    
    #The Bs->DsPi - true ID
    trueid_signal = RooGenericPdf("trueid_signal","exp(-100.*abs(@0-1))",RooArgList(trueIDVar_B))
    
    #The Bs->DsPi - time error
    terr_signal = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsPi"), debug)
    
    #The Bs->DsPi - total
    timeerr_signal = RooProdPdf('signal_timeerr', 'signal_timeerr',  RooArgSet(terr_signal),
                                RooFit.Conditional(RooArgSet(time_signal),
                                                 RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))

#------------------------------------------------- Bd -> DsPi ----------------------------------------------------#

    #The Bd->DsK - acceptance - tacc_powlaw
    tacc_dspi = tacc
    
    #The Bd->DsK - resolution
    trm_dspi = trm
    
    #The Bd->DsK - time
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
        
        
    #The Bd->DsPi - mistag
    mistag_dspi = mistagBdPDFList

    otherargs_dspi = [ tagOmegaComb, mistag_dspi, tagEffList_dspi ]
    otherargs_dspi.append(tagOmegaListBd)
    otherargs_dspi.append(aProd_dspi)
    otherargs_dspi.append(aDet_dspi)
    otherargs_dspi.append(aTagEffList_dspi)
                    
    
    cosh_dspi = DecRateCoeff('dspi_cosh', 'dspi_cosh', DecRateCoeff.CPEven,
                             idVar_B, tagDecComb,  one,       one,     *otherargs_dspi)
    sinh_dspi = DecRateCoeff('dspi_sinh', 'dspi_sinh', flag | DecRateCoeff.CPEven,
                             idVar_B, tagDecComb,  D_dspi,    Dbar_dspi, *otherargs_dspi)
    cos_dspi  = DecRateCoeff('dspi_cos',  'dspi_cos' , DecRateCoeff.CPOdd,
                             idVar_B, tagDecComb, C_dspi,    C_dspi,    *otherargs_dspi)
    sin_dspi  = DecRateCoeff('dspi_sin',  'dspi_sin',  flag | DecRateCoeff.CPOdd,
                             idVar_B, tagDecComb,  Sbar_dspi, S_dspi,    *otherargs_dspi)

    time_dspi_noacc    = RooBDecay('time_dspi_noacc','time_dspi_noacc', timeVar_B, TauInvGd, DeltaGammad,
                                  cosh_dspi, sinh_dspi, cos_dspi, sin_dspi,
                                  DeltaMd, trm_dspi, RooBDecay.SingleSided)
    
    time_dspi             = RooEffProd('time_dspi','time_dspi',time_dspi_noacc,tacc_dspi)
    
    #The Bd->DsK - true ID
    trueid_dspi = RooGenericPdf("trueid_dspi","exp(-100.*abs(@0-3))",RooArgList(trueIDVar_B))
    
    #The Bd->DsK - time error
    terr_dspi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsPi"), debug)
       
    
    #The Bd->DsK - total
    timeerr_dspi = RooProdPdf('dspi_timeerr', 'dspi_timeerr',  RooArgSet(terr_dspi),
                             RooFit.Conditional(RooArgSet(time_dspi),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))

    # ------------------------------------------------ Bs->DsK -----------------------------------------------------#
    #The Bs->DsK - mass B 
    m = TString("Bs2DsK")
    massB_dsk = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)

    #The Bs->DsK - PIDK                                                                                                                                 
    PIDK_dsk = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug)
    
    #The signal - time acceptance - tacc_powlaw
    tacc_dsk = tacc

    #The signal - resolution
    trm_dsk = trm
    
    #The signal - time error
    terr_dsk = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsK"), debug)
        
    #The signal - time
    ACPobs_dsk = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"], myconfigfile["ArgLbarfbar_s"], myconfigfile["ModLf_s"])
    ACPobs_dsk.printtable()
    
    C_dsk     = RooRealVar('C_dsk','C_dsk',ACPobs_dsk.Cf())
    S_dsk     = RooRealVar('S_dsk','S_dsk',ACPobs_dsk.Sf())
    D_dsk     = RooRealVar('D_dsk','D_dsk',ACPobs_dsk.Df())
    Sbar_dsk  = RooRealVar('Sbar_dsk','Sbar_dsk',ACPobs_dsk.Sfbar())
    Dbar_dsk  = RooRealVar('Dbar_dsk','Dbar_dsk',ACPobs_dsk.Dfbar())

    tagEff_dsk = []
    tagEffList_dsk = RooArgList()
    for i in range(0,3):
        tagEff_dsk.append(RooRealVar('tagEff_dsk_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_dsk"][i]))
        print tagEff_dsk[i].GetName()
        tagEffList_dsk.add(tagEff_dsk[i])
       
    aProd_dsk   = RooConstVar('aprod_dsk',   'aprod_dsk',   myconfigfile["aprod_dsk"])        # production asymmetry
    aDet_dsk    = RooConstVar('adet_dsk',    'adet_dsk',    myconfigfile["adet_dsk"])         # detector asymmetry
    
    aTagEff_dsk = []
    aTagEffList_dsk = RooArgList()
    for i in range(0,3):
        aTagEff_dsk.append(RooRealVar('aTagEff_dsk_'+str(i+1), 'atageff', myconfigfile["atageff_dsk"][i]))
        print aTagEff_dsk[i].GetName()
        aTagEffList_dsk.add(aTagEff_dsk[i])
      
    #The Bs->DsK - mistag
    mistag_dsk = mistagBsPDFList 
    
    flag_dsk = 0
    flag = 0

    otherargs_dsk = [ tagOmegaComb, mistag_dsk, tagEffList_dsk ]
    otherargs_dsk.append(tagOmegaList)
    otherargs_dsk.append(aProd_dsk)
    otherargs_dsk.append(aDet_dsk)
    otherargs_dsk.append(aTagEffList_dsk)
    
    cosh_dsk = DecRateCoeff('dsk_cosh', 'dsk_cosh', DecRateCoeff.CPEven,
                               idVar_B, tagDecComb,  one,      one,      *otherargs_dsk)
    sinh_dsk = DecRateCoeff('dsk_sinh', 'dsk_sinh', flag_dsk | DecRateCoeff.CPEven,
                               idVar_B, tagDecComb,  D_dsk,    Dbar_dsk, *otherargs_dsk)
    cos_dsk  = DecRateCoeff('dsk_cos',  'dsk_cos' , DecRateCoeff.CPOdd,
                               idVar_B, tagDecComb,  C_dsk,    C_dsk,    *otherargs_dsk)
    sin_dsk  = DecRateCoeff('dsk_sin',  'dsk_sin',  flag_dsk | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                               idVar_B, tagDecComb,  S_dsk, Sbar_dsk,    *otherargs_dsk)
    
    
    time_dsk_noacc       = RooBDecay('time_dsk_noacc','time_dsk_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_dsk, sinh_dsk, cos_dsk, sin_dsk,
                                  DeltaMs, trm, RooBDecay.SingleSided)
    
    time_dsk             = RooEffProd('time_dsk','time_dsk',time_dsk_noacc,tacc)

    #The signal - true ID
    trueid_dsk = RooGenericPdf("trueid_dsk","exp(-100.*abs(@0-7))",RooArgList(trueIDVar_B))
    
    #The Bs->DsK - total
    timeerr_dsk = RooProdPdf('dsk_timeerr', 'dsk_timeerr',  RooArgSet(terr_dsk),
                                RooFit.Conditional(RooArgSet(time_dsk),
                                                   RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #exit(0)
                                            
    #-------------------------------------------------- Bd -> DPi ----------------------------------------------------#                                      

    m = TString("Bd2DPi_kpipi")
    MDFitter_dpi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, dim, debug)

    #The Bd->DPi - acceptance - tacc_powlaw                                                                                                                  
    tacc_dpi = tacc

    #The Bd->DPi - resolution                                                                                                                                
    trm_dpi = trm
    #kfactor_dpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bd2DK_both"), debug)
    #trm_kf_dpi = RooKResModel('kresmodel_dpi', 'kresmodel_dpi', trm_dpi, kfactor_dpi, kFactor,  RooArgSet(Gammad, DeltaGammad, DeltaMd))

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
    terr_dpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bd2DPi"), debug)

    #The Bd->DK - total                                                                                                                                        
    timeerr_dpi = RooProdPdf('dpi_timeerr', 'dpi_timeerr',  RooArgSet(terr_dpi),
                            RooFit.Conditional(RooArgSet(time_dpi),
                                               RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))

    #------------------------------------------------- Lb -> LcPi ----------------------------------------------------#                                       
 
    #The Lb->LcPi - mass                                                                                                                                      
    m = TString("Lb2LcPi");
    MDFitter_lcpi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, m, sam, lumRatio, NULL, dim, debug);

    #The Lb->LcPi - acceptance - tacc_powlaw                                                                                                                  
    tacc_lcpi = tacc

    #The Lb->LcPi - resolution                                                                                                                               
    trm_lcpi = trm
    #kfactor_lcpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Lb2LcK_both"), debug)
    #trm_kf_lcpi = RooKResModel('kresmodel_lcpi', 'kresmodel_lcpi', trm_lcpi, kfactor_lcpi,
    #                           kFactor,  RooArgSet(GammaLb, zero, zero))

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
    trueid_lcpi = RooGenericPdf("trueid_lcpi","exp(-100.*abs(@0-4))",RooArgList(trueIDVar_B))

    #The Lb->LcK - time error                                                                                                                                 
    terr_lcpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2LcPi"), debug)

    #The Lb->LcK - total                                                                                                                                      
    timeerr_lcpi = RooProdPdf('lcpi_timeerr', 'lcpi_timeerr',  RooArgSet(terr_lcpi),
                              RooFit.Conditional(RooArgSet(time_lcpi),
                                                 RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    
        
    
    #------------------------------------------------- Combinatorial ----------------------------------------------------#
    
    #The combinatorics - PIDK
    fracPIDKComb = RooRealVar("CombBkg_fracPIDKComb", "CombBkg_fracPIDKComb",  myconfigfile["fracPIDKComb"])
    m = TString("Comb")
    PIDK1_combo = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    m = TString("CombK")
    PIDK2_combo = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
    name = "ShapePIDKAll_Comb";
    PIDK_combo = RooAddPdf("ShapePIDKAll_combo","ShapePIDKAll_combo", PIDK1_combo, PIDK2_combo, fracPIDKComb)
    
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

    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

    #The low mass - pi - mass B
    m = TString("Bs2DsstPi")
    massB_dsstpi = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    
    #the low mass - pi - pidk
    #m = TString("Bs2DsstPi")
    #PIDK_dsstpi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
                
    #The low mass - acceptance - tacc_powlaw
    tacc_dsstpi = tacc
        
    #The low mass - resolution
    trm_dsstpi = trm
    #kfactor_dsstpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bs2DsstPi_both"), debug)
    #trm_kf_dsstpi = RooKResModel('kresmodel_dsstpi', 'kresmodel_dsstpi',
    #                             trm_dsstpi, kfactor_dsstpi, kFactor,  RooArgSet(Gammas, DeltaGammas, DeltaMs))
    
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
    trueid_dsstpi = RooGenericPdf("trueid_dsstpi","exp(-100.*abs(@0-5))",RooArgList(trueIDVar_B))
    
    #The low mass - time error
    terr_dsstpi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsstPi"), debug)
    
    #The low mass - total
    timeerr_dsstpi = RooProdPdf('dsstpi_timeerr', 'dsstpi_timeerr',  RooArgSet(terr_dsstpi),
                                RooFit.Conditional(RooArgSet(time_dsstpi),
                                                   RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    
        
    #------------------------------------------------- Low mass Pi ----------------------------------------------------#
    '''
    #The low mass - pi - mass B
    m = TString("Bs2DsRho")
    massB_dsrho = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, m, false, lumRatio, debug)
    
    #The low mass - pi - pidk
    #m = TString("Bs2DsRho")
    #PIDK_dsrho = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, false, debug)
        
    #The low mass - acceptance - tacc_powlaw
    tacc_dsrho = tacc

    #The low mass - resolution
    trm_dsrho = trm
    #kfactor_dsrho = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workKFactor,TString("kFactor_Bs2DsRho_both"), debug)
    #trm_kf_dsrho = RooKResModel('kresmodel_dsrho', 'kresmodel_dsrho',
    #                            trm_dsrho, kfactor_dsrho, kFactor,  RooArgSet(Gammas, DeltaGammas, DeltaMs))

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
    trueid_dsrho = RooGenericPdf("trueid_dsrho","exp(-100.*abs(@0-5))",RooArgList(trueIDVar_B))
    
    #The low mass - time error
    terr_dsrho = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsRho"), debug)
    
    #The low mass - total
    timeerr_dsrho = RooProdPdf('dsrho_timeerr', 'dsrho_timeerr',  RooArgSet(terr_dsrho),
                               RooFit.Conditional(RooArgSet(time_dsrho),
                                                            RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
                               
    '''                                                        
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
        m = TString("Bs2DsPi_")+nameDs[i]
        PIDK_signal.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, sam, lumRatio, true, debug))
        
        # The signal - MDFitter
        MDFitter_signal.append(RooProdPdf("MDFitter_signal_%s"%(nameDs2[i]),"MDFitter_signal",
                                          RooArgList(massB_signal[i], massD_signal[i], PIDK_signal[i])))
        
        timeandmass_signal.append(RooProdPdf("timeandmass_signal_%s"%(nameDs2[i]),"timeandmass_signal",RooArgList(timeerr_signal,
                                                                                                                  MDFitter_signal[i],
                                                                                                                  trueid_signal))) 
    
    #------------------------------------------------- Bd -> DsK ----------------------------------------------------#
    
        #The Bd->DsK - mass
        meanVarBd.append(RooRealVar(    "DblCBBdPDF_mean_%s"%(nameDs2[i]) ,  "mean",    myconfigfile["mean"][i]-86.8))
        sigma1VarBd.append(RooRealVar( "DblCBBdPDF_sigma1_%s"%(nameDs2[i]), "sigma1",  myconfigfile["sigma1"][i]*myconfigfile["ratio1"] ))
        sigma2VarBd.append(RooRealVar(  "DblCBBdPDF_sigma2_%s"%(nameDs2[i]), "sigma2",  myconfigfile["sigma2"][i]*myconfigfile["ratio2"] ))
    
        num_dspi.append(RooRealVar("num_dspi_%s"%(nameDs[i]),"num_dspi",myconfigfile["num_dspi"][i]*size))
        evNum += myconfigfile["num_dspi"][i]*size
        print myconfigfile["num_dspi"][i]*size
                       
        massB_dspi.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBd[i],
                                                                     sigma1VarBd[i], alpha1VarBs[i], n1VarBs[i],
                                                                     sigma2VarBd[i], alpha2VarBs[i], n2VarBs[i],
                                                                     fracVarBs[i], num_dspi[i], nameDs[i].Data(), "Bd", debug ))
        
        # The signal - MDFitter
        massD_dspi.append(massD_signal[i])
        PIDK_dspi.append(PIDK_signal[i])
        
	MDFitter_dspi.append(RooProdPdf("MDFitter_dspi_%s"%(nameDs2[i]),"MDFitter_dspi",RooArgList(massB_dspi[i], massD_dspi[i], PIDK_dspi[i])))
                               
                
        timeandmass_dspi.append(RooProdPdf("timeandmass_dspi_%s"%(nameDs2[i]),"timeandmass_dspi",RooArgList(timeerr_dspi,
                                                                                                         MDFitter_dspi[i],
                                                                                                         trueid_dspi))) #,     
    
    #-------------------------------------------------- Bd -> DPi ----------------------------------------------------#                          

        num_dpi.append(RooRealVar("num_dpi_%s"%(nameDs2[i]),"num_dpi",myconfigfile["num_dpi"][i]*size))
        evNum += myconfigfile["num_dpi"][i]*size
        print myconfigfile["num_dpi"][i]*size

        timeandmass_dpi.append(RooProdPdf("timeandmass_dpi_%s"%(nameDs2[i]),"timeandmass_dpi",RooArgList(timeerr_dpi,
                                                                                                         MDFitter_dpi,
                                                                                                         trueid_dpi)))
    
    
        
                               
          
    #------------------------------------------------- Bs -> DsK ----------------------------------------------------# 
    
        #The Bs->DsPi- mass D
        massD_dsk.append(massD_signal[i])
        
        #The Bs->DsK - MDFitter
        MDFitter_dsk.append(RooProdPdf("MDFitter_dsk_%s"%(nameDs2[i]),"MDFitter_dsk",RooArgList(massB_dsk, massD_dspi[i], PIDK_dsk)))
                                 
        num_dsk.append(RooRealVar("num_dsk_%s"%(nameDs2[i]),"num_dsk", myconfigfile["num_dsk"][i]*size))
        evNum += myconfigfile["num_dsk"][i]*size
        print myconfigfile["num_dsk"][i]*size
        
        timeandmass_dsk.append(RooProdPdf("timeandmass_dsk_%s"%(nameDs2[i]),"timeandmass_dsk",RooArgList(timeerr_dsk,
                                                                                                         MDFitter_dsk[i],
                                                                                                         trueid_dsk)))
        
    #------------------------------------------------- Lb -> LcPi ----------------------------------------------------#                                       

        num_lcpi.append(RooRealVar("num_lcpi_%s"%(nameDs2[i]),"num_lcpi", myconfigfile["num_lcpi"][i]*size))
        evNum += myconfigfile["num_lcpi"][i]*size
        print myconfigfile["num_lcpi"][i]*size

        timeandmass_lcpi.append(RooProdPdf("timeandmass_lcpi_%s"%(nameDs2[i]),"timeandmass_lcpi",RooArgList(timeerr_lcpi,
                                                                                                         MDFitter_lcpi,
                                                                                                         trueid_lcpi)))

      
    
    #------------------------------------------------- Combinatorial ----------------------------------------------------#

        #The combinatorics - mass
        num_combo.append(RooRealVar("num_combo_%s"%(nameDs2[i]),"num_combo", myconfigfile["num_combo"][i]*size))
        evNum += myconfigfile["num_combo"][i]*size
        print myconfigfile["num_combo"][i]*size

        #The combinatorics - mass B
        cB1Var.append(RooRealVar("CombBkg_slope_Bs1_%s"%(nameDs2[i]),"CombBkg_slope_Bs1", myconfigfile["cB1"][i]))
        cB2Var.append(RooRealVar("CombBkg_slope_Bs2_%s"%(nameDs2[i]),"CombBkg_slope_Bs2", myconfigfile["cB2"][i]))
        fracBsComb.append(RooRealVar("CombBkg_fracBsComb_%s"%(nameDs2[i]), "CombBkg_fracBsComb",  myconfigfile["fracBsComb"][i]))
        massB_combo.append(Bs2Dsh2011TDAnaModels.ObtainComboBs(massVar_B, cB1Var[i], cB2Var[i], fracBsComb[i], nameDs[i], debug))
        
        #The combinatorics - mass D
        cDVar.append(RooRealVar("CombBkg_slope_Ds_%s"%(nameDs2[i]),"CombBkg_slope_Ds", myconfigfile["cD"][i]))
        fracDsComb.append(RooRealVar("CombBkg_fracDsComb_%s"%(nameDs2[i]), "CombBkg_fracDsComb",  myconfigfile["fracDsComb"][i]))
        massD_combo.append(Bs2Dsh2011TDAnaModels.ObtainComboDs(massVar_D, cDVar[i], fracDsComb[i], massD_signal[i], nameDs[i], debug))
    
        #The combinatorics - MDFitter
        MDFitter_combo.append(RooProdPdf("MDFitter_combo_%s"%(nameDs2[i]),"MDFitter_combo",RooArgList(massB_combo[i], massD_combo[i], PIDK_combo)))

              
        timeandmass_combo.append(RooProdPdf("timeandmass_combo_%s"%(nameDs2[i]),"timeandmass_combo",RooArgList(timeerr_combo,
                                                                                                               MDFitter_combo[i],
                                                                                                               trueid_combo))) 
        
     
          
    #------------------------------------------------- Low mass Pi ----------------------------------------------------#

        num_dsstpi.append(RooRealVar("num_dsstpi_%s"%(nameDs2[i]),"num_dsstpi", myconfigfile["num_dsstpi"][i]*size))
        evNum += myconfigfile["num_dsstpi"][i]*size
        print myconfigfile["num_dsstpi"][i]*size
                          
                          #The low mass - mass D
        massD_dsstpi.append(massD_signal[i])
        PIDK_dsstpi.append(PIDK_signal[i])
                          
                          #The low mass - MDFitter
        MDFitter_dsstpi.append(RooProdPdf("MDFitter_dsstpi_%s"%(nameDs[i]),"MDFitter_dsstpi",
                                          RooArgList(massB_dsstpi, massD_dsstpi[i], PIDK_dsstpi[i])))
        
              
        timeandmass_dsstpi.append(RooProdPdf("timeandmass_dsstpi_%s"%(nameDs2[i]),"timeandmass_dsstpi",RooArgList(timeerr_dsstpi,
                                                                                                                  MDFitter_dsstpi[i],
                                                                                                                  trueid_dsstpi)))
                               
    #------------------------------------------------- Low mass Pi ----------------------------------------------------#
        '''
        num_dsrho.append(RooRealVar("num_dsrho_%s"%(nameDs2[i]),"num_dsrho", myconfigfile["num_dsrho"][i]*size))
        evNum += myconfigfile["num_dsrho"][i]*size
        print myconfigfile["num_dsrho"][i]*size

        #The low mass - mass D
        massD_dsrho.append(massD_signal[i])
        PIDK_dsrho.append(PIDK_signal[i])                  

        #The low mass - MDFitter
        MDFitter_dsrho.append(RooProdPdf("MDFitter_dsrho_%s"%(nameDs[i]),"MDFitter_dsrho",
                                         RooArgList(massB_dsrho, massD_dsrho[i], PIDK_dsrho[i])))


        timeandmass_dsrho.append(RooProdPdf("timeandmass_dsrho_%s"%(nameDs2[i]),"timeandmass_dsrho",RooArgList(timeerr_dsrho,
                                                                                                               MDFitter_dsrho[i],
                                                                                                               trueid_dsrho)))
       '''
        print "partial total num of events: ",evNum
    #------------------------------------------------- Total bkg ----------------------------------------------------#
    
        #Total
        pdfList = RooArgList(timeandmass_signal[i],
                             timeandmass_dpi[i],timeandmass_dsk[i], timeandmass_lcpi[i])
        pdfList.add(timeandmass_combo[i])
        pdfList.add(timeandmass_dsstpi[i])
        pdfList.add(timeandmass_dspi[i])
        #pdfList.add(timeandmass_dsrho[i])

        numList = RooArgList(num_signal[i], num_dpi[i], num_dsk[i], num_lcpi[i])
        numList.add(num_combo[i])
        numList.add(num_dsstpi[i])
        numList.add(num_dspi[i])
        #numList.add(num_dsrho[i])
        
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

            gendata.SetName("dataSetBsDsPi_both_"+nameDs2[j])

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
            legend.AddEntry(l1, "Signal B_{s}#rightarrow D_{s}#pi", "L")

            l2 = TLine()
            l2.SetLineColor(kOrange-2)
            l2.SetLineWidth(4)
            legend.AddEntry(l2, "B #rightarrow D#pi", "L")

            l3 = TLine()
            l3.SetLineColor(kRed)
            l3.SetLineWidth(4)
            legend.AddEntry(l3, "#Lambda_{b}#rightarrow #Lambda_{c}#pi", "L")

            l4 = TLine()
            l4.SetLineColor(kBlue-10)
            l4.SetLineWidth(4)
            legend.AddEntry(l4, "B_{s}#rightarrow D_{s}^{(*)}(#pi,#rho)", "L")

            l5 = TLine()
            l5.SetLineColor(kGreen+3)
            l5.SetLineWidth(4)
            legend.AddEntry(l5, "B_{s}#rightarrow D_{s}K", "L")

            l6 = TLine()
            l6.SetLineColor(kMagenta-2)
            l6.SetLineWidth(4)
            legend.AddEntry(l6, "B_{d}#rightarrow D_{s}#pi", "L")

            l7 = TLine()
            l7.SetLineColor(kBlue-6)
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
            canv_Bmass.Print("DsPi_Toys_Bmass.pdf") 

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
            canv_Dmass.Print("DsPi_Toys_Dmass.pdf")

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
            canv_PIDK.Print("DsPi_Toys_PIDK.pdf")

            gStyle.SetOptLogy(0)
            canv_Bmistag = TCanvas("canv_Bmistag","canv_Btag", 1200, 1000)
            frame_Bmistag = mistagVar_B.frame()
            frame_Bmistag.SetTitle('')
            data.plotOn(frame_Bmistag,RooFit.Binning(50))
            frame_Bmistag.Draw()
            canv_Bmistag.Print("DsPi_Toys_Bmistag.pdf")

            gStyle.SetOptLogy(0)
            canv_Bterr = TCanvas("canv_Bterr","canv_Bterr", 1200, 1000)
            frame_Bterr = terrVar_B.frame()
            frame_Bterr.SetTitle('')
            data.plotOn(frame_Bterr,RooFit.Binning(100))
            #total_pdf.plotOn(frame_Bterr)
            frame_Bterr.Draw()
            canv_Bterr.Print("DsPi_Toys_TimeErrors.pdf")

            obs = data.get()
            tagFName = TString(tagdec)+TString("_idx")
            tagF = obs.find(tagFName.Data())
            gStyle.SetOptLogy(0)
            canv_Btag = TCanvas("canv_Btag","canv_Btag", 1200, 1000)
            frame_Btag = tagF.frame()
            frame_Btag.SetTitle('')
            data.plotOn(frame_Btag,RooFit.Binning(5))
            frame_Btag.Draw()
            canv_Btag.Print("DsPi_Toys_Tag.pdf")
            
            idFName = TString(charge)+TString("_idx")
            idF = obs.find(idFName.Data())
            gStyle.SetOptLogy(0)
            canv_Bid = TCanvas("canv_Bid","canv_Bid", 1200, 1000)
            frame_Bid = idF.frame()
            frame_Bid.SetTitle('')
            data.plotOn(frame_Bid,RooFit.Binning(2))
            frame_Bid.Draw()
            canv_Bid.Print("DsPi_Toys_Charge.pdf")
            
            
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
            canv_Btime.Print("DsPi_Toys_Btime.pdf")
        if not single :
            workout.writeToFile(dir+"DsPi_Toys_Work_"+str(i)+".root")
        else :
            workout.writeToFile("Data_Toys_Single_Work_DsPi.root")

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
                   default = 'Bs2DsPiConfigForGenerator5M')

parser.add_option( '--seed',
                   dest = 'seed',
                   default = 746829245)

parser.add_option( '--size',
                   dest = 'size',
                   default = 1)

parser.add_option( '--dir',
                   dest = 'dir',
                   default = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/Gamma70_5M_2T_MD/')


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
                                
