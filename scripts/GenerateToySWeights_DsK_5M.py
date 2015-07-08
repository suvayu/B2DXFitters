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
        # try to find from where script is executed, use current directory as
        # fallback
        tmp="$(dirname $0)"
        tmp=${tmp:-"$cwd"}
        # convert to absolute path
        tmp=`readlink -f "$tmp"`
        # move up until standalone/setup.sh found, or root reached
        while test \( \! -d "$tmp"/standalone \) -a -n "$tmp" -a "$tmp"\!="/"; do
            tmp=`dirname "$tmp"`
        done
        if test -d "$tmp"/standalone; then
            cd "$tmp"/standalone
            . ./setup.sh
        else
            echo `basename $0`: Unable to locate standalone/setup.sh
            exit 1
        fi
            cd "$cwd"
        unset tmp
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
import copy
gROOT.SetBatch()

from B2DXFitters import taggingutils, cpobservables
RooAbsData.setDefaultStorageType(RooAbsData.Tree)
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)
#
def printifdebug(debug,toprint) :
    if debug : print toprint
#
def buildLegend() :
    legend = TLegend( 0.70, 0.65, 0.99, 0.99 )
    legend.SetTextSize(0.03)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("Toy generator")
    #
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
    return legend
#------------------------------------------------------------------------------
def runBsDsKGenerator(  debug, single, configName, rangeDown, rangeUp,
                        seed , size, dir, savetree, genwithkfactors) :

    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()
    # 
    print "=========================================================="
    print "THE GENERATOR IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="
    #
    gInterpreter.ProcessLine('gRandom.SetSeed('+str(int(seed)*int(seed))+')')
    RooRandom.randomGenerator().SetSeed(int(seed)) 
    print "Generating toys beginning with seed",int(seed)
    size = int(size)
    print "Scaling the expected data yields by a factor",size

    Gammad       = RooRealVar('Gammad','Gammad', myconfigfile["Gammad"])                     # in ps^{-1}
    Gammas       = RooRealVar('Gammas','Gammas', myconfigfile["Gammas"])                     # in ps^{-1}
    DeltaGammad  = RooRealVar('DeltaGammad','DeltaGammad', myconfigfile["DeltaGammad"])      # in ps^{-1}
    DeltaGammas  = RooRealVar('DeltaGammas','DeltaGammas', myconfigfile["DeltaGammas"])      # in ps^{-1}
    TauInvGd     = Inverse( "TauInvGd","TauInvGd", Gammad)
    TauInvGs     = Inverse( "TauInvGs","TauInvGs", Gammas)
        
    DeltaMd      = RooRealVar('DeltaMd','DeltaMd', myconfigfile["DeltaMd"])                  # in ps^{-1}
    DeltaMs      = RooRealVar('DeltaMs','DeltaMs', myconfigfile["DeltaMs"])                  # in ps^{-1}
                        
    GammaLb      = RooRealVar('GammaLb','GammaLb',myconfigfile["GammaLb"])
    #GammaCombo   = RooRealVar('GammaCombo','GammaCombo',myconfigfile["GammaCombo"])
    TauInvLb     = Inverse( "TauInvLb","TauInvLb", GammaLb)
    #TauInvCombo  = Inverse( "TauInvCombo","TauInvCombo", GammaCombo)

    GammaCombo = []
    DeltaGammaCombo = []
    TauInvCombo = []
    ComboLabel = ["OS","SSK","OSSSK","UN"]

    for i in range(0,4):
        GammaCombo.append(RooRealVar('GammaCombo_%s'%(ComboLabel[i]),'GammaCombo_%s'%(ComboLabel[i]), myconfigfile["GammaCombo"][i]))
        DeltaGammaCombo.append(RooRealVar('DeltaGammaCombo_%s'%(ComboLabel[i]), 'DeltaGammaCombo_%s'%(ComboLabel[i]), myconfigfile["DeltaGammaCombo"][i]))
        TauInvCombo.append(Inverse("TauInvCombo_%s"%(ComboLabel[i]),"TauInvCombo_%s"%(ComboLabel[i]), GammaCombo[i]))

    # Some convenient constants when we build up the decays
    half     = RooConstVar('half','0.5',0.5)    
    zero     = RooConstVar('zero', '0', 0.)
    one      = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two      = RooConstVar('two', '2', 2.)
    # Which polarity?
    magpol = TString("both")
    lumRatio = RooRealVar("lumRatio","lumRatio", myconfigfile["lumRatio"])
    # Enforce that we are doing the 3D generation
    dim = int(3) 
    gendata = []
    data = []
    # Some names
    workName = 'workspace'
    fileNamePrefix = "DsK_Toys_"
    if genwithkfactors :
        fileNamePrefix += "WithKFactors_"
    # Read workspace with PDFs
    workspace = GeneralUtils.LoadWorkspace(TString(myconfigfile["fileName"]),TString(workName), debug)
    if debug : workspace.Print("v")
    workspaceData = GeneralUtils.LoadWorkspace(TString(myconfigfile["fileNameData"]),TString(workName), debug)
    if debug : workspaceData.Print("v")
    # 
    workTerr = GeneralUtils.LoadWorkspace(TString(myconfigfile["fileNameTerr"]),TString(workName), debug)
    if debug : workTerr.Print("v")
    workMistag = GeneralUtils.LoadWorkspace(TString(myconfigfile["fileNameMistag"]),TString(workName), debug)
    if debug : workMistag.Print("v")
    workMistagBDPi = GeneralUtils.LoadWorkspace(TString(myconfigfile["fileNameMistagBDPi"]),TString(workName), debug)
    if debug : workMistagBDPi.Print("v")
    workMistagComb = GeneralUtils.LoadWorkspace(TString(myconfigfile["fileNameMistagComb"]),TString(workName), debug)
    if debug : workMistagComb.Print("v")
    # Get the kFactor histograms, if needed
    kFactorHistosFile = TFile(myconfigfile["fileNameKFactHists"])
    kFactorHistos = {}
    for decaymode in myconfigfile["DecayModeParameters"] :
        if not myconfigfile["DecayModeParameters"][decaymode]["KFACTOR"] : continue
        kFactorHistos[decaymode] = {}
        for historange in range(myconfigfile["massRange"][0],\
                                myconfigfile["massRange"][1],\
                                myconfigfile["kFactorBinning"]) :
            thishistrange = str(historange)+"_"+str(historange+myconfigfile["kFactorBinning"])
            kFactorHistos[decaymode][thishistrange] = copy.deepcopy(kFactorHistosFile.Get("kFactor_"+decaymode+"_"+thishistrange))
    kFactorHistosFile.Close()
    # Define the observables we care about
    mVar         = 'lab0_MassFitConsD_M'
    mdVar        = 'lab2_MM'
    PIDKVar      = 'lab1_PIDK'
    tVar         = 'lab0_LifetimeFit_ctau'
    terrVar      = 'lab0_LifetimeFit_ctauErr'
    trueID       = 'lab0_TRUEID'
    charge       = 'lab1_ID'
    tagdec       = ['lab0_TAGDECISION_OS','lab0_SS_nnetKaon_DEC' ]
    tagomega     = ['lab0_TAGOMEGA_OS',   'lab0_SS_nnetKaon_PROB']
    # Now grab them from the workspace   
    timeVar_B       = GeneralUtils.GetObservable(workspace,TString(tVar), debug) 
    terrVar_B       = GeneralUtils.GetObservable(workspace,TString(terrVar), debug)
    massVar_D       = GeneralUtils.GetObservable(workspace,TString(mdVar), debug)
    PIDKVar_B       = GeneralUtils.GetObservable(workspace,TString(PIDKVar), debug)
    massVar_B       = GeneralUtils.GetObservable(workspace,TString(mVar), debug)
    trueIDVar_B     = RooRealVar(trueID,trueID,0,100)
    idVar_B         = GeneralUtils.GetCategory(workspaceData,TString(charge), debug)  

    # Tagging parameters : note that we now deal with tagging calibration
    # uncertainties exclusively from the data, so this is not handled here
    # on purpose.
    tagVar_B            = []
    mistagVar_B         = []
    mistagBs            = []
    mistagBd            = []
    mistagComb          = []
    tagList             = RooArgList() 
    mistagList          = RooArgList()
    mistagBsPDFList     = RooArgList()
    mistagBdPDFList     = RooArgList()
    mistagCombPDFList   = RooArgList()
    for i in range(0,2):
        tagVar_B.append(GeneralUtils.GetCategory(workspaceData,TString(tagdec[i]), debug))
        mistagVar_B.append(GeneralUtils.GetObservable(workspaceData,TString(tagomega[i]), debug))
        mistagList.add(mistagVar_B[i])
        printifdebug(debug,"Add mistag: "+mistagVar_B[i].GetName())
        tagList.add(tagVar_B[i])
        printifdebug(debug,"Add tag: "+tagVar_B[i].GetName())
    # Now grab the combined tagging decision
    tagDecComb   = GeneralUtils.GetCategory(workspaceData,TString("tagDecComb"), debug)
    tagOmegaComb = GeneralUtils.GetObservable(workspaceData,TString("tagOmegaComb"), debug)
    tagOmegaComb.setConstant(False)
    tagDecComb.setConstant(False)
    tagOmegaComb.setRange(0,0.5)
    #    
    calibHalf = MistagCalibration('calibHalf', 'calibHalf', tagOmegaComb, half, zero)
    calibIdentity = MistagCalibration('calibIdentity', 'calibIdentity', tagOmegaComb, zero, one)
    tagOmegaList = RooArgList(calibIdentity, calibIdentity, calibIdentity)
    tagOmegaListBd = RooArgList(calibIdentity, calibHalf, calibIdentity)
    # Get the different mistag PDFs
    for i in range(0,3):
        namePDF = TString("sigMistagPdf_")+TString(str(i+1))
        printifdebug(debug,"Getting the mistag PDFs for "+str(namePDF))
        mistagBs.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workMistag, namePDF, debug))
        mistagBs[i].SetName("sigMistagPdf_BsDsK_"+str(i))
        mistagBd.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workMistagBDPi, namePDF, debug))
        mistagBd[i].SetName("sigMistagPdf_Bd2DPi_"+str(i))
        mistagComb.append(Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workMistagComb, namePDF, debug))
        mistagComb[i].SetName("sigMistagPdf_CombBkg_"+str(i))
        mistagBsPDFList.add(mistagBs[i])
        mistagCombPDFList.add(mistagComb[i])
    # The Bd mistag is special -- why?
    mistagBdPDFList.add(mistagBd[0])
    mistagBdPDFList.add(mistagBd[1])
    mistagBdPDFList.add(mistagBd[0])
    printifdebug(debug,'name '+mistagBd[0].GetName())
    printifdebug(debug,'name '+mistagBd[1].GetName())
    # Acceptance from splines
    # First we define the bin boundaries
    binName = TString("splineBinning")
    TimeBin = RooBinning(myconfigfile["timeRange"][0],myconfigfile["timeRange"][1],binName.Data())
    for i in range(0, myconfigfile["tacc_size"]):
        TimeBin.addBoundary(myconfigfile["tacc_knots"][i])
    # 
    TimeBin.removeBoundary(myconfigfile["timeRange"][0])
    TimeBin.removeBoundary(myconfigfile["timeRange"][1])
    if debug : TimeBin.Print("v")
    timeVar_B.setBinning(TimeBin, binName.Data())
    timeVar_B.setRange(myconfigfile["timeRange"][0],myconfigfile["timeRange"][1])
    # The last splines need to be specially set in order to normalize correctly
    listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, timeVar_B)
    # Now build the list of actual spline coefficients
    tacc_list = RooArgList()
    tacc_var = []
    for i in range(0, myconfigfile["tacc_size"]):
        tacc_var.append(RooRealVar("var"+str(i+1), "var"+str(i+1), myconfigfile["tacc_values"][i]))
        printifdebug(debug,tacc_var[i].GetName())
        tacc_list.add(tacc_var[i])
    tacc_var.append(RooRealVar("var"+str(myconfigfile["tacc_size"]+1), "var"+str(myconfigfile["tacc_size"]+1), 1.0))
    len = tacc_var.__len__()
    tacc_list.add(tacc_var[len-1])
    printifdebug(debug,"n-2: "+tacc_var[len-2].GetName())
    printifdebug(debug,"n-1: "+tacc_var[len-1].GetName())
    tacc_var.append(RooAddition("var"+str(myconfigfile["tacc_size"]+2),"var"+str(myconfigfile["tacc_size"]+2),
                                RooArgList(tacc_var[len-2],tacc_var[len-1]), listCoeff))
    tacc_list.add(tacc_var[len])
    printifdebug(debug,"n: "+tacc_var[len].GetName())
    # Now make the actual spline function
    taccNoNorm = RooCubicSplineFun("splinePdf", "splinePdf", timeVar_B, "splineBinning", tacc_list)
    # An extra normalization constant
    it = tacc_list.fwdIterator()
    m = 0.
    while True:
        obj = it.next()
        if None == obj: break
        if obj.getVal() > m:
            m = obj.getVal()
    printifdebug(debug,"max: "+str(m))
    SplineConst = RooConstVar('SplineAccNormCoeff', 'SplineAccNormCoeff', 1. / m)
    tacc = RooProduct('SplineAcceptanceNormalised','SplineAcceptanceNormalised', RooArgList(taccNoNorm, SplineConst))
    # Now for the time resolution
    # There are two separate components to this : on the one hand, we define the
    # model in terms of a mean offset and scale factors which will be applied to 
    # the per-event time errors (this part is done here). Then later on we will
    # assign the templates of the time errors for the different modes from MC
    trm_mean    = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["resolutionMeanBias"], 'ps' )
    trm_scale   = RooRealVar( 'trm_sigmaSF', 'Gaussian resolution model scale factor', myconfigfile["resolutionScaleFactor"])
    if not genwithkfactors :
        # There are two scale factors here following terrVar_B : first the scale factor for the mean
        # which is just set to 1, and then the scale factor for the width
        trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGaussPEDTE', timeVar_B, trm_mean,\
                                                                                 terrVar_B, RooFit.RooConst(1.),trm_scale)
    else :
        # For generating with kFactors, we need to first generate with essentially infinite resolution
        # then we take the resulting dataset and smear aposteriori, first with the kFactors, THEN with
        # the resolution (as that has to come second)
        #
        # There is no doubt there are ''smarter'' ways to do this, but the aim here is to change the
        # minimal number of things relative to the no-k-Factors generator 
        #
        trm = RooGaussModel("QuasiPerfectResModel","QuasiPerfectResModel",  timeVar_B,
                                                                            RooFit.RooConst(0),
                                                                            RooFit.RooConst(0.0001))
    # Now the names of the Ds modes 
    nameDs = [TString("nonres"), TString("phipi"), TString("kstk"), TString("kpipi"), TString("pipipi")]
    #    
    total_pdf                   = []
    # The various mass shape parameters, B mass
    meanVarBs                   = []
    sigma1VarBs                 = []
    sigma2VarBs                 = []
    alpha1VarBs                 = []
    alpha2VarBs                 = []
    n1VarBs                     = []
    n2VarBs                     = []
    fracVarBs                   = []
    massB_Signal                = []
    # and D mass
    meanVarDs                   = []
    sigma1VarDs                 = []
    sigma2VarDs                 = []
    alpha1VarDs                 = []
    alpha2VarDs                 = []
    n1VarDs                     = []
    n2VarDs                     = []
    fracVarDs                   = []
    massD_Signal                = []
    #
    PIDK_Signal                 = []
    MDFitter_Signal             = []    
    timeandmass_Signal          = []
    #
    meanVarBd                   = []
    sigma1VarBd                 = []
    sigma2VarBd                 = []
    # Now the different backgrounds
    massB_Bd2DsK                = []
    massD_Bd2DsK                = []
    PIDK_Bd2DsK                 = []
    MDFitter_Bd2DsK             = []
    timeandmass_Bd2DsK          = []
    # Notice that for Bd->DsK and Bs->DsPi
    # we separate the PIDK shapes for each
    # decay mode, but for others this is
    # uniform (of necessity, as we gend only KKPi)
    massB_Bs2DsPi               = []
    massD_Bs2DsPi               = []
    PIDK_Bs2DsPi                = []
    MDFitter_Bs2DsPi            = []
    timeandmass_Bs2DsPi         = []
    # For all modes with a true Ds we take
    # the Ds shapes split by Ds decay mode
    # as for the signal
    massD_Lb2Dsp                = []
    MDFitter_Lb2Dsp             = []
    timeandmass_Lb2Dsp          = []
    #
    massD_Lb2Dsstp              = []
    MDFitter_Lb2Dsstp           = []
    timeandmass_Lb2Dsstp        = []
    #
    massD_LM1                   = []
    PIDK_LM1                    = []
    MDFitter_LM1                = []
    timeandmass_LM1             = []
    #
    massD_Bs2DsstPi             = []
    MDFitter_Bs2DsstPi          = []
    timeandmass_Bs2DsstPi       = []
    #
    massD_Bs2DsRho              = []
    MDFitter_Bs2DsRho           = []
    timeandmass_Bs2DsRho        = []
    #
    timeandmass_Bd2DK           = []
    timeandmass_Lb2LcK          = []
    timeandmass_Bd2DPi          = []
    timeandmass_Lb2LcPi         = []
    # The parameters for the combo
    cBVar                       = [] 
    massB_Combo                 = []     
    cDVar                       = [] 
    fracDsComb                  = [] 
    massD_Combo                 = [] 
    MDFitter_Combo              = [] 
    timeandmass_Combo           = [] 
    time_Combo_noacc            = []
    time_Combo_pertag           = []
    D_Combo                     = []
    Dbar_Combo                  = []
    sinh_Combo                  = []
    sin_Combo                   = []
    cosh_Combo                  = []
    cos_Combo                   = []
    tagEffList_Combo            = []
    fracTagCombo                = []
    otherargs_Combo             = []
    #
    num_Signal                  = []
    num_Bd2DK                   = []
    num_Bd2DPi                  = []
    num_Bd2DsK                  = []
    num_Bs2DsPi                 = []
    num_Lb2LcK                  = []
    num_Lb2LcPi                 = []
    num_Lb2Dsp                  = []
    num_Lb2Dsstp                = []
    num_Combo                   = []
    num_LM1                     = []
    num_Bs2DsstPi               = []
    num_Bs2DsRho                = []
    #
    # The counter which holds the number of events to be generated 
    evNum       = 0
    # Flags for the DecRateCoeff terms
    flag        = 0
    flag_Signal = 0
    flag_LM1    = 0
    # ------------------------------------------------ Signal Time PDF -----------------------------------------------------#
    #The signal - time acceptance (from splines)
    tacc_Signal = tacc
    #The signal - resolution
    trm_Signal  = trm
    #The signal - time error
    terr_Signal = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsK"), debug)
    #The signal - time, begin by generating the observables
    ACPobs_Signal = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"], myconfigfile["ArgLbarfbar_s"], myconfigfile["ModLf_s"])
    ACPobs_Signal.printtable()
    #
    C_Signal     = RooRealVar('C_Signal','C_Signal',ACPobs_Signal.Cf())
    S_Signal     = RooRealVar('S_Signal','S_Signal',ACPobs_Signal.Sf())
    D_Signal     = RooRealVar('D_Signal','D_Signal',ACPobs_Signal.Df())
    Sbar_Signal  = RooRealVar('Sbar_Signal','Sbar_Signal',ACPobs_Signal.Sfbar())
    Dbar_Signal  = RooRealVar('Dbar_Signal','Dbar_Signal',ACPobs_Signal.Dfbar())
    #
    tagEff_Signal = []
    tagEffList_Signal = RooArgList()
    for i in range(0,3):
        tagEff_Signal.append(RooRealVar('tagEff_Signal_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Signal"][i]))
        printifdebug(debug,tagEff_Signal[i].GetName())
        tagEffList_Signal.add(tagEff_Signal[i])
    #   
    aProd_Signal   = RooConstVar('aprod_Signal',   'aprod_Signal',   myconfigfile["aprod_Signal"])        # production asymmetry
    aDet_Signal    = RooConstVar('adet_Signal',    'adet_Signal',    myconfigfile["adet_Signal"])         # detector asymmetry
    #
    aTagEff_Signal = []
    aTagEffList_Signal = RooArgList()
    for i in range(0,3):
        aTagEff_Signal.append(RooRealVar('aTagEff_Signal_'+str(i+1), 'atageff', myconfigfile["atageff_Signal"][i]))
        printifdebug(debug,aTagEff_Signal[i].GetName())
        aTagEffList_Signal.add(aTagEff_Signal[i])
    #  
    #The Bs->DsK - mistag
    mistag_Signal = mistagBsPDFList 
    # 
    otherargs_Signal = [ tagOmegaComb, mistag_Signal, tagEffList_Signal ]
    otherargs_Signal.append(tagOmegaList)
    otherargs_Signal.append(aProd_Signal)
    otherargs_Signal.append(aDet_Signal)
    otherargs_Signal.append(aTagEffList_Signal)
    #
    cosh_Signal = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven,
                               idVar_B, tagDecComb,  one,      one,      *otherargs_Signal)
    sinh_Signal = DecRateCoeff('signal_sinh', 'signal_sinh', flag_Signal | DecRateCoeff.CPEven,
                               idVar_B, tagDecComb,  D_Signal,    Dbar_Signal, *otherargs_Signal)
    cos_Signal  = DecRateCoeff('signal_cos',  'signal_cos' , DecRateCoeff.CPOdd,
                               idVar_B, tagDecComb,  C_Signal,    C_Signal,    *otherargs_Signal)
    sin_Signal  = DecRateCoeff('signal_sin',  'signal_sin',  flag_Signal | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                               idVar_B, tagDecComb,  S_Signal, Sbar_Signal,    *otherargs_Signal)
    #
    time_Signal_noacc       = RooBDecay('time_Signal_noacc','time_Signal_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_Signal, sinh_Signal, cos_Signal, sin_Signal,
                                  DeltaMs, trm, RooBDecay.SingleSided)
    #
    time_Signal             = RooEffProd('time_Signal','time_Signal',time_Signal_noacc,tacc)
    #
    #The signal - true ID
    trueidval = myconfigfile["DecayModeParameters"]["Signal"]["TRUEID"]
    trueid_Signal = RooGenericPdf("trueid_Signal","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Bs->DsK - total time PDF
    timeerr_Signal = RooProdPdf('signal_timeerr', 'signal_timeerr',  RooArgSet(terr_Signal),
                                RooFit.Conditional(RooArgSet(time_Signal),
                                                   RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #----------------------------------------------- Bd -> DK time&mass PDF --------------------------------------------------#
    # Notice that here we build a single MDFitter_Bd2DK model upfront
    MDFitter_Bd2DK = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, TString("Bd2DK"), magpol, lumRatio, NULL, dim, debug)
    #The Bd->DK - acceptance (splines)
    tacc_Bd2DK = tacc
    #The Bd->DK - resolution
    trm_Bd2DK = trm
    #The Bd->DK - time
    tagEff_Bd2DK = []
    tagEffList_Bd2DK = RooArgList()
    for i in range(0,3):
        tagEff_Bd2DK.append(RooRealVar('tagEff_Bd2DK_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Bd2DK"][i]))
        printifdebug(debug,tagEff_Bd2DK[i].GetName())
        tagEffList_Bd2DK.add(tagEff_Bd2DK[i])
    #                               
    C_Bd2DK    = RooRealVar('C_Bd2DK', 'C coeff. dk', 1.)
    S_Bd2DK    = RooRealVar('S_Bd2DK', 'S coeff. dk', 0.)
    D_Bd2DK    = RooRealVar('D_Bd2DK', 'D coeff. dk', 0.)
    Sbar_Bd2DK    = RooRealVar('Sbar_Bd2DK', 'Sbar coeff. dk', 0.)
    Dbar_Bd2DK    = RooRealVar('Dbar_Bd2DK', 'Dbar coeff. dk', 0.)
    #
    aProd_Bd2DK   = RooConstVar('aprod_Bd2DK',   'aprod_Bd2DK',   myconfigfile["aprod_Bd2DK"])        # production asymmetry
    aDet_Bd2DK    = RooConstVar('adet_Bd2DK',    'adet_Bd2DK',    myconfigfile["adet_Bd2DK"])         # detector asymmetry
    aTagEff_Bd2DK = []
    aTagEffList_Bd2DK = RooArgList()
    for i in range(0,3):
        aTagEff_Bd2DK.append(RooRealVar('aTagEff_Bd2DK_'+str(i+1), 'atageff', myconfigfile["atageff_Bd2DK"][i]))
        printifdebug(debug,aTagEff_Bd2DK[i].GetName())
        aTagEffList_Bd2DK.add(aTagEff_Bd2DK[i])
    #    
    #The Bd->DPi - mistag
    mistag_Bd2DK = mistagBdPDFList
    #
    otherargs_Bd2DK = [ tagOmegaComb, mistag_Bd2DK, tagEffList_Bd2DK ]
    otherargs_Bd2DK.append(tagOmegaListBd)
    otherargs_Bd2DK.append(aProd_Bd2DK)
    otherargs_Bd2DK.append(aDet_Bd2DK)
    otherargs_Bd2DK.append(aTagEffList_Bd2DK)
    #                
    cosh_Bd2DK = DecRateCoeff('dk_cosh', 'dk_cosh', DecRateCoeff.CPEven,
                           idVar_B, tagDecComb,  one,      one,      *otherargs_Bd2DK)
    sinh_Bd2DK = DecRateCoeff('dk_sinh', 'dk_sinh', flag | DecRateCoeff.CPEven,
                           idVar_B, tagDecComb,  D_Bd2DK,    Dbar_Bd2DK, *otherargs_Bd2DK)
    cos_Bd2DK  = DecRateCoeff('dk_cos',  'dk_cos' , DecRateCoeff.CPOdd,
                           idVar_B, tagDecComb, C_Bd2DK,    C_Bd2DK,    *otherargs_Bd2DK)
    sin_Bd2DK  = DecRateCoeff('dk_sin',  'dk_sin',  flag | DecRateCoeff.CPOdd,
                           idVar_B, tagDecComb,  Sbar_Bd2DK, S_Bd2DK,    *otherargs_Bd2DK)
    #
    time_Bd2DK_noacc  = RooBDecay('time_Bd2DK_noacc','time_Bd2DK_noacc', timeVar_B, TauInvGd, DeltaGammad,
                         cosh_Bd2DK, sinh_Bd2DK, cos_Bd2DK, sin_Bd2DK,
                         DeltaMd, trm_Bd2DK, RooBDecay.SingleSided)
    #
    time_Bd2DK             = RooEffProd('time_Bd2DK','time_Bd2DK',time_Bd2DK_noacc, tacc_Bd2DK)
    #The Bd->DK - true ID
    trueidval = myconfigfile["DecayModeParameters"]["Bd2DK"]["TRUEID"]
    trueid_Bd2DK = RooGenericPdf("trueid_Bd2DK","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Bd->DPi - time error
    terr_Bd2DK = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bd2DK"), debug)
    #The Bd->DK - total
    timeerr_Bd2DK = RooProdPdf('dk_timeerr', 'dk_timeerr',  RooArgSet(terr_Bd2DK),
                            RooFit.Conditional(RooArgSet(time_Bd2DK),
                                               RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #---------------------------------------------- Bd -> DPi time & mass PDF -----------------------------------------------#
    # Build a single MDFitter model upfront
    MDFitter_Bd2DPi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, TString("Bd2DPi"), magpol, lumRatio, NULL, dim, debug)
    #The Bd->DPi - acceptance (splines)                                                                                                                  
    tacc_Bd2DPi = tacc
    #The Bd->DPi - resolution                                                                                                                                
    trm_Bd2DPi = trm
    #The Bd->DK - time                                                                                                                                         
    tagEff_Bd2DPi = []
    tagEffList_Bd2DPi = RooArgList()
    for i in range(0,3):
        tagEff_Bd2DPi.append(RooRealVar('tagEff_Bd2DPi_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Bd2DPi"][i]))
        printifdebug(debug,tagEff_Bd2DPi[i].GetName())
        tagEffList_Bd2DPi.add(tagEff_Bd2DPi[i])
    # Here we again have some non-trivial terms due to "physics"
    ACPobs_Bd2DPi = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_d"], myconfigfile["ArgLbarfbar_d"], myconfigfile["ModLf_d"])
    # 
    C_Bd2DPi     = RooRealVar('C_Bd2DPi','C_Bd2DPi',ACPobs_Bd2DPi.Cf())
    S_Bd2DPi     = RooRealVar('S_Bd2DPi','S_Bd2DPi',ACPobs_Bd2DPi.Sf())
    D_Bd2DPi     = RooRealVar('D_Bd2DPi','D_Bd2DPi',ACPobs_Bd2DPi.Df())
    Sbar_Bd2DPi  = RooRealVar('Sbar_Bd2DPi','Sbar_Bd2DPi',ACPobs_Bd2DPi.Sfbar())
    Dbar_Bd2DPi  = RooRealVar('Dbar_Bd2DPi','Dbar_Bd2DPi',ACPobs_Bd2DPi.Dfbar())
    #
    aProd_Bd2DPi   = RooConstVar('aprod_Bd2DPi',   'aprod_Bd2DPi',   myconfigfile["aprod_Bd2DPi"])        # production asymmetry 
    aDet_Bd2DPi    = RooConstVar('adet_Bd2DPi',    'adet_Bd2DPi',    myconfigfile["adet_Bd2DPi"])         # detector asymmetry 
    aTagEff_Bd2DPi = []
    aTagEffList_Bd2DPi = RooArgList()
    for i in range(0,3):
        aTagEff_Bd2DPi.append(RooRealVar('aTagEff_Bd2DPi_'+str(i+1), 'atageff', myconfigfile["atageff_Bd2DPi"][i]))
        printifdebug(debug,aTagEff_Bd2DPi[i].GetName())
        aTagEffList_Bd2DPi.add(aTagEff_Bd2DPi[i])
    #The Bd->DPi - mistag                                                                                                                                     
    mistag_Bd2DPi = mistagBdPDFList
    #
    otherargs_Bd2DPi = [ tagOmegaComb, mistag_Bd2DPi, tagEffList_Bd2DPi ]
    otherargs_Bd2DPi.append(tagOmegaListBd)
    otherargs_Bd2DPi.append(aProd_Bd2DPi)
    otherargs_Bd2DPi.append(aDet_Bd2DPi)
    otherargs_Bd2DPi.append(aTagEffList_Bd2DPi)
    #
    cosh_Bd2DPi = DecRateCoeff('dpi_cosh', 'dpi_cosh', DecRateCoeff.CPEven,
                           idVar_B, tagDecComb,  one,      one,      *otherargs_Bd2DPi)
    sinh_Bd2DPi = DecRateCoeff('dpi_sinh', 'dpi_sinh', flag | DecRateCoeff.CPEven,
                           idVar_B, tagDecComb,  D_Bd2DPi,    Dbar_Bd2DPi, *otherargs_Bd2DPi)
    cos_Bd2DPi  = DecRateCoeff('dpi_cos',  'dpi_cos' , DecRateCoeff.CPOdd,
                           idVar_B, tagDecComb, C_Bd2DPi,    C_Bd2DPi,    *otherargs_Bd2DPi)
    sin_Bd2DPi  = DecRateCoeff('dpi_sin',  'dpi_sin',  flag | DecRateCoeff.CPOdd,
                           idVar_B, tagDecComb,  Sbar_Bd2DPi, S_Bd2DPi,    *otherargs_Bd2DPi)
    #
    time_Bd2DPi_noacc  = RooBDecay('time_Bd2DPi_noacc','time_Bd2DPi_noacc', timeVar_B, TauInvGd, DeltaGammad,
                         cosh_Bd2DPi, sinh_Bd2DPi, cos_Bd2DPi, sin_Bd2DPi,
                         DeltaMd, trm_Bd2DPi, RooBDecay.SingleSided)
    #
    time_Bd2DPi             = RooEffProd('time_Bd2DPi','time_Bd2DPi',time_Bd2DPi_noacc, tacc_Bd2DPi)
    #The Bd->DPi - true ID                                                                                                                                    
    trueidval = myconfigfile["DecayModeParameters"]["Bd2DPi"]["TRUEID"]
    trueid_Bd2DPi = RooGenericPdf("trueid_Bd2DPi","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Bd->DPi - time error                                                                                                                                 
    terr_Bd2DPi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bd2DK"), debug)
    #The Bd->DPi - total
    timeerr_Bd2DPi = RooProdPdf('dpi_timeerr', 'dpi_timeerr',  RooArgSet(terr_Bd2DPi),
                            RooFit.Conditional(RooArgSet(time_Bd2DPi),
                                               RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #------------------------------------------------- Bd -> DsK Time PDF ----------------------------------------------------#
    #The Bd->DsK - acceptance (splines)
    tacc_Bd2DsK = tacc
    #The Bd->DsK - resolution
    trm_Bd2DsK = trm
    #The Bd->DsK - time
    tagEff_Bd2DsK = []
    tagEffList_Bd2DsK = RooArgList()
    for i in range(0,3):
        tagEff_Bd2DsK.append(RooRealVar('tagEff_Bd2DsK_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Bd2DsK"][i]))
        printifdebug(debug,tagEff_Bd2DsK[i].GetName())
        tagEffList_Bd2DsK.add(tagEff_Bd2DsK[i])
    #                            
    C_Bd2DsK    = RooRealVar('C_Bd2DsK', 'C coeff. dsk', 1.)
    S_Bd2DsK    = RooRealVar('S_Bd2DsK', 'S coeff. dsk', 0.)
    D_Bd2DsK    = RooRealVar('D_Bd2DsK', 'D coeff. dsk', 0.)
    Sbar_Bd2DsK    = RooRealVar('Sbar_Bd2DsK', 'Sbar coeff. dsk', 0.)
    Dbar_Bd2DsK    = RooRealVar('Dbar_Bd2DsK', 'Dbar coeff. dsk', 0.)
    #
    aProd_Bd2DsK   = RooConstVar('aprod_Bd2DsK',   'aprod_Bd2DsK',   myconfigfile["aprod_Bd2DsK"])        # production asymmetry
    aDet_Bd2DsK    = RooConstVar('adet_Bd2DsK',    'adet_Bd2DsK',    myconfigfile["adet_Bd2DsK"])         # detector asymmetry
    #
    aTagEff_Bd2DsK = []
    aTagEffList_Bd2DsK = RooArgList()
    for i in range(0,3):
        aTagEff_Bd2DsK.append(RooRealVar('aTagEff_Bd2DsK_'+str(i+1), 'atageff', myconfigfile["atageff_Bd2DsK"][i]))
        printifdebug(debug,aTagEff_Bd2DsK[i].GetName())
        aTagEffList_Bd2DsK.add(aTagEff_Bd2DsK[i])
    #The Bd->DsPi - mistag
    mistag_Bd2DsK = mistagBdPDFList
    #
    otherargs_Bd2DsK = [ tagOmegaComb, mistag_Bd2DsK, tagEffList_Bd2DsK ]
    otherargs_Bd2DsK.append(tagOmegaListBd)
    otherargs_Bd2DsK.append(aProd_Bd2DsK)
    otherargs_Bd2DsK.append(aDet_Bd2DsK)
    otherargs_Bd2DsK.append(aTagEffList_Bd2DsK)
    #                
    cosh_Bd2DsK = DecRateCoeff('dsk_cosh', 'dsk_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,       one,     *otherargs_Bd2DsK)
    sinh_Bd2DsK = DecRateCoeff('dsk_sinh', 'dsk_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_Bd2DsK,    Dbar_Bd2DsK, *otherargs_Bd2DsK)
    cos_Bd2DsK  = DecRateCoeff('dsk_cos',  'dsk_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb, C_Bd2DsK,    C_Bd2DsK,    *otherargs_Bd2DsK)
    sin_Bd2DsK  = DecRateCoeff('dsk_sin',  'dsk_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_Bd2DsK, S_Bd2DsK,    *otherargs_Bd2DsK)
    # 
    time_Bd2DsK_noacc    = RooBDecay('time_Bd2DsK_noacc','time_Bd2DsK_noacc', timeVar_B, TauInvGd, DeltaGammad,
                                  cosh_Bd2DsK, sinh_Bd2DsK, cos_Bd2DsK, sin_Bd2DsK,
                                  DeltaMd,trm_Bd2DsK, RooBDecay.SingleSided)
    # 
    time_Bd2DsK             = RooEffProd('time_Bd2DsK','time_Bd2DsK',time_Bd2DsK_noacc,tacc_Bd2DsK)
    #The Bd->DsK - true ID
    trueidval = myconfigfile["DecayModeParameters"]["Bd2DsK"]["TRUEID"]
    trueid_Bd2DsK = RooGenericPdf("trueid_Bd2DsK","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Bd->DsK - time error
    terr_Bd2DsK = terr_Bd2DK = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsK"), debug)
    #The Bd->DsK - total
    timeerr_Bd2DsK = RooProdPdf('dsk_timeerr', 'dsk_timeerr',  RooArgSet(terr_Bd2DsK),
                             RooFit.Conditional(RooArgSet(time_Bd2DsK),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #------------------------------------------------- Bs -> DsPi Time PDF ----------------------------------------------------#
    #The Bs->DsPi - acceptance (splines)
    tacc_Bs2DsPi = tacc
    #The Bs->DsPi - resolution
    trm_Bs2DsPi = trm
    #The Bs->DsPi - time
    tagEff_Bs2DsPi = []
    tagEffList_Bs2DsPi = RooArgList()
    for i in range(0,3):
        tagEff_Bs2DsPi.append(RooRealVar('tagEff_Bs2DsPi_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Bs2DsPi"][i]))
        printifdebug(debug,tagEff_Bs2DsPi[i].GetName())
        tagEffList_Bs2DsPi.add(tagEff_Bs2DsPi[i])
    #        
    C_Bs2DsPi    = RooRealVar('C_Bs2DsPi', 'C coeff. dspi', 1.)
    S_Bs2DsPi    = RooRealVar('S_Bs2DsPi', 'S coeff. dspi', 0.)
    D_Bs2DsPi    = RooRealVar('D_Bs2DsPi', 'D coeff. dspi', 0.)
    Sbar_Bs2DsPi    = RooRealVar('Sbar_Bs2DsPi', 'Sbar coeff. dspi', 0.)
    Dbar_Bs2DsPi    = RooRealVar('Dbar_Bs2DsPi', 'Dbar coeff. dspi', 0.)
    #
    aProd_Bs2DsPi   = RooConstVar('aprod_Bs2DsPi',   'aprod_Bs2DsPi',   myconfigfile["aprod_Bs2DsPi"])        # production asymmetry
    aDet_Bs2DsPi    = RooConstVar('adet_Bs2DsPi',    'adet_Bs2DsPi',    myconfigfile["adet_Bs2DsPi"])         # detector asymmetry
    aTagEff_Bs2DsPi = []
    aTagEffList_Bs2DsPi = RooArgList()
    for i in range(0,3):
        aTagEff_Bs2DsPi.append(RooRealVar('aTagEff_Bs2DsPi_'+str(i+1), 'atageff', myconfigfile["atageff_Bs2DsPi"][i]))
        printifdebug(debug,aTagEff_Bs2DsPi[i].GetName())
        aTagEffList_Bs2DsPi.add(aTagEff_Bs2DsPi[i])
    #                                
    mistag_Bs2DsPi = mistagBsPDFList
    # 
    otherargs_Bs2DsPi = [ tagOmegaComb, mistag_Bs2DsPi, tagEffList_Bs2DsPi ]
    otherargs_Bs2DsPi.append(tagOmegaList)
    otherargs_Bs2DsPi.append(aProd_Bs2DsPi)
    otherargs_Bs2DsPi.append(aDet_Bs2DsPi)
    otherargs_Bs2DsPi.append(aTagEffList_Bs2DsPi)
    #
    cosh_Bs2DsPi = DecRateCoeff('dspi_cosh', 'dspi_cosh', DecRateCoeff.CPEven, idVar_B, tagDecComb,
                             one,         one,         *otherargs_Bs2DsPi)
    sinh_Bs2DsPi = DecRateCoeff('dspi_sinh', 'dspi_sinh', DecRateCoeff.CPEven, idVar_B, tagDecComb,
                             D_Bs2DsPi,    Dbar_Bs2DsPi, *otherargs_Bs2DsPi)
    cos_Bs2DsPi  = DecRateCoeff('dspi_cos' , 'dspi_cos' , DecRateCoeff.CPOdd,  idVar_B, tagDecComb,
                             C_Bs2DsPi,    C_Bs2DsPi,    *otherargs_Bs2DsPi)
    sin_Bs2DsPi  = DecRateCoeff('dspi_sin' , 'dspi_sin' , DecRateCoeff.CPOdd,  idVar_B, tagDecComb,
                             Sbar_Bs2DsPi, S_Bs2DsPi,    *otherargs_Bs2DsPi)
    # 
    time_Bs2DsPi_noacc = RooBDecay('time_Bs2DsPi_noacc','time_Bs2DsPi_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                cosh_Bs2DsPi, sinh_Bs2DsPi, cos_Bs2DsPi, sin_Bs2DsPi,
                                DeltaMs, trm_Bs2DsPi, RooBDecay.SingleSided)
    #
    time_Bs2DsPi             = RooEffProd('time_Bs2DsPi','time_Bs2DsPi',time_Bs2DsPi_noacc,tacc_Bs2DsPi)
    #The Bs->DsPi - true ID
    trueidval = myconfigfile["DecayModeParameters"]["Bs2DsPi"]["TRUEID"]
    trueid_Bs2DsPi = RooGenericPdf("trueid_Bs2DsPi","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Bs->DsPi - time error
    terr_Bs2DsPi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsPi"), debug)
    #The Bs->DsPi - total
    timeerr_Bs2DsPi = RooProdPdf('dspi_timeerr', 'dspi_timeerr',  RooArgSet(terr_Bs2DsPi),
                              RooFit.Conditional(RooArgSet(time_Bs2DsPi),
                                                 RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #------------------------------------------------- Lb -> LcK Time PDF ----------------------------------------------------#
    # Build a single MDFitter instance upfront
    MDFitter_Lb2LcK = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, TString("Lb2LcK"), magpol, lumRatio, NULL, dim, debug);
    #The Lb->LcK - acceptance (splines)
    tacc_Lb2LcK = tacc
    #The Lb->LcK - resolution
    trm_Lb2LcK = trm
    #The Lb->LcK - time
    tagEff_Lb2LcK = []
    tagEffList_Lb2LcK = RooArgList()
    for i in range(0,3):
        tagEff_Lb2LcK.append(RooRealVar('tagEff_Lb2LcK_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Lb2LcK"][i]))
        printifdebug(debug,tagEff_Lb2LcK[i].GetName())
        tagEffList_Lb2LcK.add(tagEff_Lb2LcK[i])
    # 
    C_Lb2LcK    = RooRealVar('C_Lb2LcK', 'C coeff. lck', 0.)
    S_Lb2LcK    = RooRealVar('S_Lb2LcK', 'S coeff. lck', 0.)
    D_Lb2LcK    = RooRealVar('D_Lb2LcK', 'D coeff. lck', 0.)
    Sbar_Lb2LcK    = RooRealVar('Sbar_Lb2LcK', 'Sbar coeff. lck', 0.)
    Dbar_Lb2LcK    = RooRealVar('Dbar_Lb2LcK', 'Dbar coeff. lck', 0.)
    #
    aProd_Lb2LcK   = RooConstVar('aprod_Lb2LcK',   'aprod_Lb2LcK',   myconfigfile["aprod_Lb2LcK"])        # production asymmetry
    aDet_Lb2LcK    = RooConstVar('adet_Lb2LcK',    'adet_Lb2LcK',    myconfigfile["adet_Lb2LcK"])         # detector asymmetry
    aTagEff_Lb2LcK = []
    aTagEffList_Lb2LcK = RooArgList()
    for i in range(0,3):
        aTagEff_Lb2LcK.append(RooRealVar('aTagEff_Lb2LcK_'+str(i+1), 'atageff', myconfigfile["atageff_Lb2LcK"][i]))
        printifdebug(debug,aTagEff_Lb2LcK[i].GetName())
        aTagEffList_Lb2LcK.add(aTagEff_Lb2LcK[i])
    #    
    #The Lb->LcK - mistag
    mistag_Lb2LcK = mistagBdPDFList
    # 
    otherargs_Lb2LcK = [ tagOmegaComb, mistag_Lb2LcK, tagEffList_Lb2LcK ]
    otherargs_Lb2LcK.append(tagOmegaListBd)
    otherargs_Lb2LcK.append(aProd_Lb2LcK)
    otherargs_Lb2LcK.append(aDet_Lb2LcK)
    otherargs_Lb2LcK.append(aTagEffList_Lb2LcK)
    #                
    cosh_Lb2LcK = DecRateCoeff('lck_cosh', 'lck_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,       one,     *otherargs_Lb2LcK)
    sinh_Lb2LcK = DecRateCoeff('lck_sinh', 'lck_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_Lb2LcK,    Dbar_Lb2LcK, *otherargs_Lb2LcK)
    cos_Lb2LcK  = DecRateCoeff('lck_cos',  'lck_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_Lb2LcK,    C_Lb2LcK,    *otherargs_Lb2LcK)
    sin_Lb2LcK  = DecRateCoeff('lck_sin',  'lck_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_Lb2LcK, S_Lb2LcK,    *otherargs_Lb2LcK)
    # 
    time_Lb2LcK_noacc    = RooBDecay('time_Lb2LcK_noacc','time_Lb2LcK_noacc', timeVar_B, TauInvLb, zero,
                            cosh_Lb2LcK, sinh_Lb2LcK, cos_Lb2LcK, sin_Lb2LcK,
                            zero,trm_Lb2LcK, RooBDecay.SingleSided)
    #
    time_Lb2LcK             = RooEffProd('time_Lb2LcK','time_Lb2LcK',time_Lb2LcK_noacc,tacc_Lb2LcK)
    #The Lb->LcK - true ID
    trueidval = myconfigfile["DecayModeParameters"]["Lb2LcK"]["TRUEID"]
    trueid_Lb2LcK = RooGenericPdf("trueid_Lb2LcK","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Lb->LcK - time error
    terr_Lb2LcK = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2LcK"), debug)
    #The Lb->LcK - total
    timeerr_Lb2LcK = RooProdPdf('lck_timeerr', 'lck_timeerr',  RooArgSet(terr_Lb2LcK),
                             RooFit.Conditional(RooArgSet(time_Lb2LcK),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #------------------------------------------------- Lb -> LcPi Time PDF----------------------------------------------------#
    # Build a single MDFitter instance upfront
    MDFitter_Lb2LcPi = Bs2Dsh2011TDAnaModels.ObtainRooProdPdfForMDFitter(workspace, TString("Lb2LcPi"), magpol, lumRatio, NULL, dim, debug);
    #The Lb->LcPi - acceptance (splines)                                                                                                                  
    tacc_Lb2LcPi = tacc
    #The Lb->LcPi - resolution                                                                                                                               
    trm_Lb2LcPi = trm
    #The Lb->LcPi - time                                                                                                                                      
    tagEff_Lb2LcPi = []
    tagEffList_Lb2LcPi = RooArgList()
    for i in range(0,3):
        tagEff_Lb2LcPi.append(RooRealVar('tagEff_Lb2LcPi_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Lb2LcPi"][i]))
        printifdebug(debug,tagEff_Lb2LcPi[i].GetName())
        tagEffList_Lb2LcPi.add(tagEff_Lb2LcPi[i])
    #
    C_Lb2LcPi    = RooRealVar('C_Lb2LcPi', 'C coeff. lcpi', 0.)
    S_Lb2LcPi    = RooRealVar('S_Lb2LcPi', 'S coeff. lcpi', 0.)
    D_Lb2LcPi    = RooRealVar('D_Lb2LcPi', 'D coeff. lcpi', 0.)
    Sbar_Lb2LcPi    = RooRealVar('Sbar_Lb2LcPi', 'Sbar coeff. lcpi', 0.)
    Dbar_Lb2LcPi    = RooRealVar('Dbar_Lb2LcPi', 'Dbar coeff. lcpi', 0.)
    #
    aProd_Lb2LcPi   = RooConstVar('aprod_Lb2LcPi',   'aprod_Lb2LcPi',   myconfigfile["aprod_Lb2LcPi"])        # production asymmetry                                
    aDet_Lb2LcPi    = RooConstVar('adet_Lb2LcPi',    'adet_Lb2LcPi',    myconfigfile["adet_Lb2LcPi"])         # detector asymmetry                                   
    aTagEff_Lb2LcPi = []
    aTagEffList_Lb2LcPi = RooArgList()
    for i in range(0,3):
        aTagEff_Lb2LcPi.append(RooRealVar('aTagEff_Lb2LcPi_'+str(i+1), 'atageff', myconfigfile["atageff_Lb2LcPi"][i]))
        printifdebug(debug,aTagEff_Lb2LcPi[i].GetName())
        aTagEffList_Lb2LcPi.add(aTagEff_Lb2LcPi[i])
    #
    #The Lb->LcPi - mistag                                                                                                                                
    mistag_Lb2LcPi = mistagBdPDFList
    #
    otherargs_Lb2LcPi = [ tagOmegaComb, mistag_Lb2LcPi, tagEffList_Lb2LcPi ]
    otherargs_Lb2LcPi.append(tagOmegaListBd)
    otherargs_Lb2LcPi.append(aProd_Lb2LcPi)
    otherargs_Lb2LcPi.append(aDet_Lb2LcPi)
    otherargs_Lb2LcPi.append(aTagEffList_Lb2LcPi)
    #
    cosh_Lb2LcPi = DecRateCoeff('lcpi_cosh', 'lcpi_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,       one,     *otherargs_Lb2LcPi)
    sinh_Lb2LcPi = DecRateCoeff('lcpi_sinh', 'lcpi_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_Lb2LcPi,    Dbar_Lb2LcPi, *otherargs_Lb2LcPi)
    cos_Lb2LcPi  = DecRateCoeff('lcpi_cos',  'lcpi_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_Lb2LcPi,    C_Lb2LcPi,    *otherargs_Lb2LcPi)
    sin_Lb2LcPi  = DecRateCoeff('lcpi_sin',  'lcpi_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_Lb2LcPi, S_Lb2LcPi,    *otherargs_Lb2LcPi)
    #
    time_Lb2LcPi_noacc    = RooBDecay('time_Lb2LcPi_noacc','time_Lb2LcPi_noacc', timeVar_B, TauInvLb, zero,
                            cosh_Lb2LcPi, sinh_Lb2LcPi, cos_Lb2LcPi, sin_Lb2LcPi,
                            zero, trm_Lb2LcPi, RooBDecay.SingleSided)
    #
    time_Lb2LcPi             = RooEffProd('time_Lb2LcPi','time_Lb2LcPi',time_Lb2LcPi_noacc,tacc_Lb2LcPi)
    #
    #The Lb->LcK - true ID                                                                                                                                    
    trueidval = myconfigfile["DecayModeParameters"]["Lb2LcPi"]["TRUEID"]
    trueid_Lb2LcPi = RooGenericPdf("trueid_Lb2LcPi","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Lb->LcK - time error                                                                                                                                 
    terr_Lb2LcPi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2LcK"), debug)
    #The Lb->LcK - total                                                                                                                                      
    timeerr_Lb2LcPi = RooProdPdf('lcpi_timeerr', 'lcpi_timeerr',  RooArgSet(terr_Lb2LcPi),
                              RooFit.Conditional(RooArgSet(time_Lb2LcPi),
                                                 RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #------------------------------------------------- Lb -> Dsp Time/Bmass/PIDK PDF ------------------------------------------------#
    # Here we build the B/PIDK upfront, will build the D later by mode
    massB_Lb2Dsp = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Lb2Dsp"), false, lumRatio, debug)
    PIDK_Lb2Dsp = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, TString("Lb2Dsp"), magpol, lumRatio, false, debug)
    #The Lb->Dsp - acceptance 
    tacc_Lb2Dsp = tacc
    #The Lb->Dsp - resolution
    trm_Lb2Dsp = trm
    #The Lb->Dsp - time
    tagEff_Lb2Dsp = []
    tagEffList_Lb2Dsp = RooArgList()
    for i in range(0,3):
        tagEff_Lb2Dsp.append(RooRealVar('tagEff_Lb2Dsp_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Lb2Dsp"][i]))
        printifdebug(debug,tagEff_Lb2Dsp[i].GetName())
        tagEffList_Lb2Dsp.add(tagEff_Lb2Dsp[i])
    #        
    C_Lb2Dsp    = RooRealVar('C_Lb2Dsp', 'S coeff. dsp', 0.)
    S_Lb2Dsp    = RooRealVar('S_Lb2Dsp', 'S coeff. dsp', 0.)
    D_Lb2Dsp    = RooRealVar('D_Lb2Dsp', 'D coeff. dsp', 0.)
    Sbar_Lb2Dsp = RooRealVar('Sbar_Lb2Dsp', 'Sbar coeff. dsp', 0.)
    Dbar_Lb2Dsp = RooRealVar('Dbar_Lb2Dsp', 'Dbar coeff. dsp', 0.)
    #
    aProd_Lb2Dsp   = RooConstVar('aprod_Lb2Dsp',   'aprod_Lb2Dsp',   myconfigfile["aprod_Lb2Dsp"])        # production asymmetry
    aDet_Lb2Dsp    = RooConstVar('adet_Lb2Dsp',    'adet_Lb2Dsp',    myconfigfile["adet_Lb2Dsp"])         # detector asymmetry
    #
    aTagEff_Lb2Dsp = []
    aTagEffList_Lb2Dsp = RooArgList()
    for i in range(0,3):
        aTagEff_Lb2Dsp.append(RooRealVar('aTagEff_Lb2Dsp_'+str(i+1), 'atageff', myconfigfile["atageff_Lb2Dsp"][i]))
        printifdebug(debug,aTagEff_Lb2Dsp[i].GetName())
        aTagEffList_Lb2Dsp.add(aTagEff_Lb2Dsp[i])
    #The Lb->Dsp - mistag
    mistag_Lb2Dsp = mistagBdPDFList
    # 
    otherargs_Lb2Dsp = [ tagOmegaComb, mistag_Lb2Dsp, tagEffList_Lb2Dsp ]
    otherargs_Lb2Dsp.append(tagOmegaListBd)
    otherargs_Lb2Dsp.append(aProd_Lb2Dsp)
    otherargs_Lb2Dsp.append(aDet_Lb2Dsp)
    otherargs_Lb2Dsp.append(aTagEffList_Lb2Dsp)
    #                
    cosh_Lb2Dsp = DecRateCoeff('dsp_cosh', 'dsp_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,       one,             *otherargs_Lb2Dsp)
    sinh_Lb2Dsp = DecRateCoeff('dsp_sinh', 'dsp_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_Lb2Dsp,    Dbar_Lb2Dsp, *otherargs_Lb2Dsp)
    cos_Lb2Dsp  = DecRateCoeff('dsp_cos',  'dsp_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_Lb2Dsp,    C_Lb2Dsp,    *otherargs_Lb2Dsp)
    sin_Lb2Dsp  = DecRateCoeff('dsp_sin',  'dsp_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_Lb2Dsp, S_Lb2Dsp,    *otherargs_Lb2Dsp)
    #
    time_Lb2Dsp_noacc      = RooBDecay('time_Lb2Dsp_noacc','time_Lb2Dsp_noacc', timeVar_B, TauInvLb, zero,
                                  cosh_Lb2Dsp, sinh_Lb2Dsp, cos_Lb2Dsp, sinh_Lb2Dsp,
                                  zero,trm_Lb2Dsp, RooBDecay.SingleSided)
    #
    time_Lb2Dsp             = RooEffProd('time_Lb2Dsp','time_Lb2Dsp',time_Lb2Dsp_noacc,tacc_Lb2Dsp)
    #The Lb->Dsp - true ID
    trueidval = myconfigfile["DecayModeParameters"]["Lb2Dsp"]["TRUEID"]
    trueid_Lb2Dsp = RooGenericPdf("trueid_Lb2Dsp","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Lb->Dsp, Lb->Dsstp - time error
    terr_Lb2Dsp = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2Dsp"), debug)
    #The Lb->Dsp, Lb->Dsstp - total
    timeerr_Lb2Dsp = RooProdPdf('dsp_timeerr', 'dsp_timeerr',  RooArgSet(terr_Lb2Dsp),
                             RooFit.Conditional(RooArgSet(time_Lb2Dsp),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #--------------------------------------------- Lb ->  Dsstp Time/Bmass/PIDK PDF----------------------------------------------#
    # Here we build the B/PIDK upfront, will build the D later by mode
    massB_Lb2Dsstp = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Lb2Dsstp"), false, lumRatio, debug)
    PIDK_Lb2Dsstp = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, TString("Lb2Dsstp"), magpol, lumRatio, false, debug)
    #The Lb->Dsp, Lb->Dsstp - acceptance (splines)
    tacc_Lb2Dsstp = tacc
    #The Lb->Dsp, Lb->Dsstp - resolution
    trm_Lb2Dsstp = trm
    #The Lb->Dsp, Lb->Dsstp - time
    tagEff_Lb2Dsstp = []
    tagEffList_Lb2Dsstp = RooArgList()
    for i in range(0,3):
        tagEff_Lb2Dsstp.append(RooRealVar('tagEff_Lb2Dsstp_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Lb2Dsstp"][i]))
        printifdebug(debug,tagEff_Lb2Dsstp[i].GetName())
        tagEffList_Lb2Dsstp.add(tagEff_Lb2Dsstp[i])
    #
    C_Lb2Dsstp    = RooRealVar('C_Lb2Dsstp', 'S coeff. dsstp', 0.)
    S_Lb2Dsstp    = RooRealVar('S_Lb2Dsstp', 'S coeff. dsstp', 0.)
    D_Lb2Dsstp    = RooRealVar('D_Lb2Dsstp', 'D coeff. dsstp', 0.)
    Sbar_Lb2Dsstp    = RooRealVar('Sbar_Lb2Dsstp', 'Sbar coeff. dsstp', 0.)
    Dbar_Lb2Dsstp    = RooRealVar('Dbar_Lb2Dsstp', 'Dbar coeff. dsstp', 0.)
    #
    aProd_Lb2Dsstp   = RooConstVar('aprod_Lb2Dsstp',   'aprod_Lb2Dsstp',   myconfigfile["aprod_Lb2Dsstp"])        # production asymmetry
    aDet_Lb2Dsstp    = RooConstVar('adet_Lb2Dsstp',    'adet_Lb2Dsstp',    myconfigfile["adet_Lb2Dsstp"])         # detector asymmetry
    #
    aTagEff_Lb2Dsstp = []
    aTagEffList_Lb2Dsstp = RooArgList()
    for i in range(0,3):
        aTagEff_Lb2Dsstp.append(RooRealVar('aTagEff_Lb2Dsstp_'+str(i+1), 'atageff', myconfigfile["atageff_Lb2Dsstp"][i]))
        printifdebug(debug,aTagEff_Lb2Dsstp[i].GetName())
        aTagEffList_Lb2Dsstp.add(aTagEff_Lb2Dsstp[i])
    #The Lb->Dsstp - mistag
    mistag_Lb2Dsstp = mistagBdPDFList
    #
    otherargs_Lb2Dsstp = [ tagOmegaComb, mistag_Lb2Dsstp, tagEffList_Lb2Dsstp ]
    otherargs_Lb2Dsstp.append(tagOmegaListBd)
    otherargs_Lb2Dsstp.append(aProd_Lb2Dsstp)
    otherargs_Lb2Dsstp.append(aDet_Lb2Dsstp)
    otherargs_Lb2Dsstp.append(aTagEffList_Lb2Dsstp)
    # 
    cosh_Lb2Dsstp = DecRateCoeff('dsstp_cosh', 'dsstp_cosh', DecRateCoeff.CPEven,
                                idVar_B, tagDecComb,  one,       one,             *otherargs_Lb2Dsstp)
    sinh_Lb2Dsstp = DecRateCoeff('dsstp_sinh', 'dsstp_sinh', flag | DecRateCoeff.CPEven,
                                idVar_B, tagDecComb,  D_Lb2Dsstp,    Dbar_Lb2Dsstp, *otherargs_Lb2Dsstp)
    cos_Lb2Dsstp  = DecRateCoeff('dsstp_cos',  'dsstp_cos' , DecRateCoeff.CPOdd,
                               idVar_B, tagDecComb,  C_Lb2Dsstp,    C_Lb2Dsstp,    *otherargs_Lb2Dsstp)
    sin_Lb2Dsstp  = DecRateCoeff('dsstp_sin',  'dsstp_sin',  flag | DecRateCoeff.CPOdd,
                                idVar_B, tagDecComb,  Sbar_Lb2Dsstp, S_Lb2Dsstp,    *otherargs_Lb2Dsstp)
    #
    time_Lb2Dsstp_noacc      = RooBDecay('time_Lb2Dsstp_noacc','time_Lb2Dsstp_noacc', timeVar_B, TauInvLb, zero,
                                        cosh_Lb2Dsstp, sinh_Lb2Dsstp, cos_Lb2Dsstp, sinh_Lb2Dsstp,
                                        zero,trm_Lb2Dsstp, RooBDecay.SingleSided)
    #
    time_Lb2Dsstp             = RooEffProd('time_Lb2Dsstp','time_Lb2Dsstp',time_Lb2Dsstp_noacc,tacc_Lb2Dsstp)
    #The Lb->Dsstp - true ID
    trueidval = myconfigfile["DecayModeParameters"]["Lb2Dsstp"]["TRUEID"]
    trueid_Lb2Dsstp = RooGenericPdf("trueid_Lb2Dsstp","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Lb->Dsstp - time error
    terr_Lb2Dsstp = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Lb2Dsstp"), debug)
    #The Lb->Dsstp - total
    timeerr_Lb2Dsstp = RooProdPdf('dsstp_timeerr', 'dsstp_timeerr',  RooArgSet(terr_Lb2Dsstp),
                                 RooFit.Conditional(RooArgSet(time_Lb2Dsstp),
                                                    RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #------------------------------------------------- Combinatorial ----------------------------------------------------#
    #The combinatorics - PIDK
    fracPIDKComb1 = RooRealVar("CombBkg_fracPIDKComb1", "CombBkg_fracPIDKComb1",  myconfigfile["fracPIDKComb1"])
    fracPIDKComb2 = RooRealVar("CombBkg_fracPIDKComb2", "CombBkg_fracPIDKComb2",  myconfigfile["fracPIDKComb2"])
    PIDK_Combo_K  = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, TString("CombK"), magpol, lumRatio, false, debug)
    PIDK_Combo_Pi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, TString("CombPi"), magpol, lumRatio, false, debug)
    PIDK_Combo_P  = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, TString("CombP"), magpol, lumRatio, false, debug)
    PIDK_Combo = RooAddPdf("ShapePIDKAll_Combo","ShapePIDKAll_Combo",
                           RooArgList(PIDK_Combo_K, PIDK_Combo_Pi, PIDK_Combo_P), RooArgList(fracPIDKComb1, fracPIDKComb2), true)
    #The combinatorics - acceptance (splines)
    tacc_Combo = tacc
    #The combinatorics - resolution
    trm_Combo = trm
    #The combinatorics - time
    tagEff_Combo = []
    tagEffList_Combo = [] # RooArgList() 
    for j in range(0,4):
        tagEff_Combo.append([])
        tagEffList_Combo.append(RooArgList())
        for i in range(0,3):
            tagEff_Combo[j].append(RooRealVar('tagEff_Combo_%s_%s'%(str(i+1),ComboLabel[j]), 'Signal tagging efficiency', myconfigfile["tagEff_Combo_full"][j][i]))
            printifdebug(debug,tagEff_Combo[j][i].GetName())
            tagEffList_Combo[j].add(tagEff_Combo[j][i])

    # 
    C_Combo       = RooRealVar('C_Combo', 'C coeff. combo', 0.)
    S_Combo       = RooRealVar('S_Combo', 'S coeff. combo', 0.)
    Sbar_Combo    = RooRealVar('Sbar_Combo', 'Sbar coeff. combo', 0.)
    for i in range(0,4):
        D_Combo.append(RooRealVar('D_Combo_%s'%(ComboLabel[i]), 'D coeff. combo', myconfigfile["D_Combo"][i]))
        Dbar_Combo.append(D_Combo[i])
    #
    aProd_Combo   = RooConstVar('aprod_Combo',   'aprod_Combo',   myconfigfile["aprod_Combo"])        # production asymmetry
    aDet_Combo    = RooConstVar('adet_Combo',    'adet_Combo',    myconfigfile["adet_Combo"])         # detector asymmetry
    aTagEff_Combo = []
    aTagEffList_Combo = RooArgList()
    for i in range(0,3):
        aTagEff_Combo.append(RooRealVar('aTagEff_Combo_'+str(i+1), 'atageff', myconfigfile["atageff_Combo"][i]))
        printifdebug(debug,aTagEff_Combo[i].GetName())
        aTagEffList_Combo.add(aTagEff_Combo[i])
    #The combinatorics - mistag
    mistag_Combo = mistagCombPDFList
    # 
    timeComboPDFList = RooArgList()
    fracTagComboList = RooArgList()

    for i in range(0,4):
        otherargs_Combo.append([ tagOmegaComb, mistag_Combo, tagEffList_Combo[i]])
        otherargs_Combo[i].append(tagOmegaList)
        otherargs_Combo[i].append(aProd_Combo)
        otherargs_Combo[i].append(aDet_Combo)
        otherargs_Combo[i].append(aTagEffList_Combo)
        
        cosh_Combo.append(DecRateCoeff('combo_cosh_%s'%(ComboLabel[i]), 'combo_cosh_%s'%(ComboLabel[i]), DecRateCoeff.CPEven, idVar_B, 
                                       tagDecComb,  one,        one,        *otherargs_Combo[i]))

        sinh_Combo.append(DecRateCoeff('combo_sinh_%s'%(ComboLabel[i]), 'combo_sinh_%s'%(ComboLabel[i]), flag | DecRateCoeff.CPEven,
                                       idVar_B, tagDecComb,  D_Combo[i],    Dbar_Combo[i], *otherargs_Combo[i]))
        cos_Combo.append(DecRateCoeff('combo_cos_%s'%(ComboLabel[i]),  'combo_cos_%s'%(ComboLabel[i]) , DecRateCoeff.CPOdd,
                                      idVar_B, tagDecComb,  C_Combo,    C_Combo,    *otherargs_Combo[i]))
        sin_Combo.append(DecRateCoeff('combo_sin_%s'%(ComboLabel[i]),  'combo_sin_%s'%(ComboLabel[i]),  flag | DecRateCoeff.CPOdd,
                                      idVar_B, tagDecComb,  Sbar_Combo, S_Combo,    *otherargs_Combo[i]))
        # 
        time_Combo_noacc.append(RooBDecay('time_Combo_noacc_%s'%(ComboLabel[i]),'time_Combo_noacc_%s'%(ComboLabel[i]), 
                                          timeVar_B, TauInvCombo[i], DeltaGammaCombo[i],
                                          cosh_Combo[i], sinh_Combo[i], cos_Combo[i], sin_Combo[i],
                                          zero,trm_Combo, RooBDecay.SingleSided))
        #
        time_Combo_pertag.append(RooEffProd('time_Combo_%s'%(ComboLabel[i]),'time_Combo_%s'%(ComboLabel[i]),time_Combo_noacc[i], tacc_Combo))
        timeComboPDFList.add(time_Combo_pertag[i])
        print 'time combo list, adding: %s'%(time_Combo_pertag[i].GetName())
     
    for i in range(0,3):   
        fracTagCombo.append(RooRealVar('fracTagCombo_%s'%(ComboLabel[i]),'fracTagCombo_%s'%(ComboLabel[i]), myconfigfile["tagEff_Combo"][i]))
        fracTagComboList.add(fracTagCombo[i])

    time_Combo = RooAddPdf('time_Combo','time_Combo',timeComboPDFList,fracTagComboList)   
    #
    #The combinatorics - true ID
    trueidval = myconfigfile["DecayModeParameters"]["Combo"]["TRUEID"]
    trueid_Combo = RooGenericPdf("trueid_Combo","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    # 
    #The combinatorics - time error
    terr_Combo = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_CombBkg"), debug)
    #
    timeerr_Combo = RooProdPdf('combo_timeerr', 'combo_timeerr',  RooArgSet(terr_Combo),
                               RooFit.Conditional(RooArgSet(time_Combo),
                                                  RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #
    #--------------------------------------------- Low mass K Time/Bmass/PIDK PDF -----------------------------------------------#
    # Here we build the B/PIDK upfront, will build the D later by mode
    massB_LM1 = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bs2DsKst"), false, lumRatio, debug);
    #PIDK_LM1 = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, TString("Bs2DsKst"), magpol, lumRatio, false, debug);
    #The low mass - acceptance (splines)
    tacc_LM1 = tacc
    #The low mass - resolution
    trm_LM1 = trm
    #The low mass - time (with non-trivial structure)
    ACPobs_LM1 = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"], myconfigfile["ArgLbarfbar_s"], myconfigfile["ModLf_s"])
    # 
    C_LM1     = RooRealVar('C_LM1','C_LM1',ACPobs_LM1.Cf())
    S_LM1     = RooRealVar('S_LM1','S_LM1',ACPobs_LM1.Sf())
    D_LM1     = RooRealVar('D_LM1','D_LM1',ACPobs_LM1.Df())
    Sbar_LM1  = RooRealVar('Sbar_LM1','Sbar_LM1',ACPobs_LM1.Sfbar())
    Dbar_LM1  = RooRealVar('Dbar_LM1','Dbar_LM1',ACPobs_LM1.Dfbar())
    #
    tagEff_LM1 = []
    tagEffList_LM1 = RooArgList()
    for i in range(0,3):
        tagEff_LM1.append(RooRealVar('tagEff_LM1_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_LM1"][i]))
        printifdebug(debug,tagEff_LM1[i].GetName())
        tagEffList_LM1.add(tagEff_LM1[i])
    #
    aProd_LM1   = RooConstVar('aprod_LM1',   'aprod_LM1',   myconfigfile["aprod_LM1"])        # production asymmetry
    aDet_LM1    = RooConstVar('adet_LM1',    'adet_LM1',    myconfigfile["adet_LM1"])         # detector asymmetry
    aTagEff_LM1 = []
    aTagEffList_LM1 = RooArgList()
    for i in range(0,3):
        aTagEff_LM1.append(RooRealVar('aTagEff_LM1_'+str(i+1), 'atageff', myconfigfile["atageff_LM1"][i]))
        printifdebug(debug,aTagEff_LM1[i].GetName())
        aTagEffList_LM1.add(aTagEff_LM1[i])
    #The low mass - mistag
    mistag_LM1 = mistagBsPDFList
    # 
    otherargs_LM1 = [ tagOmegaComb, mistag_LM1, tagEffList_LM1 ]
    otherargs_LM1.append(tagOmegaList)
    otherargs_LM1.append(aProd_LM1)
    otherargs_LM1.append(aDet_LM1)
    otherargs_LM1.append(aTagEffList_LM1)
    #                
    cosh_LM1 = DecRateCoeff('lm1_cosh', 'lm1_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,      one,      *otherargs_LM1)
    sinh_LM1 = DecRateCoeff('lm1_sinh', 'lm1_sinh', flag_LM1 | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_LM1,    Dbar_LM1, *otherargs_LM1)
    cos_LM1  = DecRateCoeff('lm1_cos',  'lm1_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_LM1,    C_LM1,    *otherargs_LM1)
    sin_LM1  = DecRateCoeff('lm1_sin',  'lm1_sin',  flag_LM1 | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
                            idVar_B, tagDecComb,  S_LM1, Sbar_LM1,    *otherargs_LM1)
    # 
    time_LM1_noacc    = RooBDecay('time_LM1_noacc','time_LM1_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_LM1, sinh_LM1, cos_LM1, sin_LM1,
                                  DeltaMs,trm_LM1, RooBDecay.SingleSided)
    # 
    time_LM1             = RooEffProd('time_LM1','time_LM1',time_LM1_noacc,tacc_LM1)
    #The low mass - true ID
    trueidval = myconfigfile["DecayModeParameters"]["LM1"]["TRUEID"]
    trueid_LM1 = RooGenericPdf("trueid_LM1","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The low mass - time error
    terr_LM1 = terr_Signal     
    #The low mass - total
    timeerr_LM1 = RooProdPdf('lm1_timeerr', 'lm1_timeerr',  RooArgSet(terr_LM1),
                             RooFit.Conditional(RooArgSet(time_LM1),
                                                RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #------------------------------------------- Bs->Ds*Pi Time/Bmass/PIDK PDF ----------------------------------------------#
    # Here we build the B/PIDK upfront, will build the D later by mode
    massB_Bs2DsstPi = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bs2DsstPi"), false, lumRatio, debug)
    PIDK_Bs2DsstPi = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, TString("Bs2DsstPi"), magpol, lumRatio, false, debug)
    #The Ds*Pi - acceptance (splines)
    tacc_Bs2DsstPi = tacc
    #The Ds*Pi - resolution
    trm_Bs2DsstPi = trm
    #The Ds*Pi - time
    tagEff_Bs2DsstPi = []
    tagEffList_Bs2DsstPi = RooArgList()
    for i in range(0,3):
        tagEff_Bs2DsstPi.append(RooRealVar('tagEff_Bs2DsstPi_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Bs2DsstPi"][i]))
        printifdebug(debug,tagEff_Bs2DsstPi[i].GetName())
        tagEffList_Bs2DsstPi.add(tagEff_Bs2DsstPi[i])
    #        
    C_Bs2DsstPi       = RooRealVar('C_Bs2DsstPi', 'C coeff. dsstpi', 1.)
    S_Bs2DsstPi       = RooRealVar('S_Bs2DsstPi', 'S coeff. dsstpi', 0.)
    D_Bs2DsstPi       = RooRealVar('D_Bs2DsstPi', 'D coeff. dsstpi', 0.)
    Sbar_Bs2DsstPi    = RooRealVar('Sbar_Bs2DsstPi', 'Sbar coeff. dsstpi', 0.)
    Dbar_Bs2DsstPi    = RooRealVar('Dbar_Bs2DsstPi', 'Dbar coeff. dsstpi', 0.)
    #
    aProd_Bs2DsstPi   = RooConstVar('aprod_Bs2DsstPi',   'aprod_Bs2DsstPi',   myconfigfile["aprod_Bs2DsstPi"])        # production asymmetry
    aDet_Bs2DsstPi    = RooConstVar('adet_Bs2DsstPi',    'adet_Bs2DsstPi',    myconfigfile["adet_Bs2DsstPi"])         # detector asymmetry
    aTagEff_Bs2DsstPi = []
    aTagEffList_Bs2DsstPi = RooArgList()
    for i in range(0,3):
        aTagEff_Bs2DsstPi.append(RooRealVar('aTagEff_Bs2DsstPi_'+str(i+1), 'atageff', myconfigfile["atageff_Bs2DsstPi"][i]))
        printifdebug(debug,aTagEff_Bs2DsstPi[i].GetName())
        aTagEffList_Bs2DsstPi.add(aTagEff_Bs2DsstPi[i])
    #The Ds*Pi - mistag
    mistag_Bs2DsstPi = mistagBsPDFList
    #
    otherargs_Bs2DsstPi = [ tagOmegaComb, mistag_Bs2DsstPi, tagEffList_Bs2DsstPi ]
    otherargs_Bs2DsstPi.append(tagOmegaList)
    otherargs_Bs2DsstPi.append(aProd_Bs2DsstPi)
    otherargs_Bs2DsstPi.append(aDet_Bs2DsstPi)
    otherargs_Bs2DsstPi.append(aTagEffList_Bs2DsstPi)
    #
    cosh_Bs2DsstPi = DecRateCoeff('dsstpi_cosh', 'dsstpi_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,      one,      *otherargs_Bs2DsstPi)
    sinh_Bs2DsstPi = DecRateCoeff('dsstpi_sinh', 'dsstpi_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_Bs2DsstPi,    Dbar_Bs2DsstPi, *otherargs_Bs2DsstPi)
    cos_Bs2DsstPi  = DecRateCoeff('dsstpi_cos',  'dsstpi_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_Bs2DsstPi,    C_Bs2DsstPi,    *otherargs_Bs2DsstPi)
    sin_Bs2DsstPi  = DecRateCoeff('dsstpi_sin',  'dsstpi_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_Bs2DsstPi, S_Bs2DsstPi,    *otherargs_Bs2DsstPi)
    #
    time_Bs2DsstPi_noacc    = RooBDecay('time_Bs2DsstPi_noacc','time_Bs2DsstPi_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_Bs2DsstPi, sinh_Bs2DsstPi, cos_Bs2DsstPi, sin_Bs2DsstPi,
                                  DeltaMs,trm_Bs2DsstPi, RooBDecay.SingleSided)
    #
    time_Bs2DsstPi             = RooEffProd('time_Bs2DsstPi','time_Bs2DsstPi',time_Bs2DsstPi_noacc,tacc_Bs2DsstPi)
    #The Ds*Pi - true ID true
    trueidval = myconfigfile["DecayModeParameters"]["Bs2DsstPi"]["TRUEID"]
    trueid_Bs2DsstPi = RooGenericPdf("trueid_Bs2DsstPi","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The Ds*Pi - time error
    terr_Bs2DsstPi = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsstPi"), debug)
    #The Ds*Pi - total
    timeerr_Bs2DsstPi = RooProdPdf('dsstpi_timeerr', 'dsstpi_timeerr',  RooArgSet(terr_Bs2DsstPi),
                                RooFit.Conditional(RooArgSet(time_Bs2DsstPi),
                                                   RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #--------------------------------------------- Bs->DsRho Time/Bmass/PIDK PDF -----------------------------------------------#
    # Here we build the B/PIDK upfront, will build the D later by mode
    massB_Bs2DsRho = Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bs2DsRho"), false, lumRatio, debug)
    PIDK_Bs2DsRho = Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, TString("Bs2DsRho"), magpol, lumRatio, false, debug)
    #The DsRho - acceptance (splines)
    tacc_Bs2DsRho = tacc
    #The DsRho - resolution
    trm_Bs2DsRho = trm
    #The DsRho - time
    tagEff_Bs2DsRho = []
    tagEffList_Bs2DsRho = RooArgList()
    for i in range(0,3):
        tagEff_Bs2DsRho.append(RooRealVar('tagEff_Bs2DsRho_'+str(i+1), 'Signal tagging efficiency', myconfigfile["tagEff_Bs2DsRho"][i]))
        printifdebug(debug,tagEff_Bs2DsRho[i].GetName())
        tagEffList_Bs2DsRho.add(tagEff_Bs2DsRho[i])
    #    
    C_Bs2DsRho    = RooRealVar('C_Bs2DsRho', 'C coeff. dsrho', 1.)
    S_Bs2DsRho    = RooRealVar('S_Bs2DsRho', 'S coeff. dsrho', 0.)
    D_Bs2DsRho    = RooRealVar('D_Bs2DsRho', 'D coeff. dsrho', 0.)
    Sbar_Bs2DsRho    = RooRealVar('Sbar_Bs2DsRho', 'Sbar coeff. dsrho', 0.)
    Dbar_Bs2DsRho    = RooRealVar('Dbar_Bs2DsRho', 'Dbar coeff. dsrho', 0.)
    # 
    aProd_Bs2DsRho   = RooConstVar('aprod_Bs2DsRho',   'aprod_Bs2DsRho',   myconfigfile["aprod_Bs2DsRho"])        # production asymmetry
    aDet_Bs2DsRho    = RooConstVar('adet_Bs2DsRho',    'adet_Bs2DsRho',    myconfigfile["adet_Bs2DsRho"])         # detector asymmetry
    aTagEff_Bs2DsRho = []
    aTagEffList_Bs2DsRho = RooArgList()
    for i in range(0,3):
        aTagEff_Bs2DsRho.append(RooRealVar('aTagEff_Bs2DsRho_'+str(i+1), 'atageff', myconfigfile["atageff_Bs2DsRho"][i]))
        printifdebug(debug,aTagEff_Bs2DsRho[i].GetName())
        aTagEffList_Bs2DsRho.add(aTagEff_Bs2DsRho[i])
    #The DsRho - mistag
    mistag_Bs2DsRho = mistagBsPDFList
    # 
    otherargs_Bs2DsRho = [ tagOmegaComb, mistag_Bs2DsRho, tagEffList_Bs2DsRho ]
    otherargs_Bs2DsRho.append(tagOmegaList)
    otherargs_Bs2DsRho.append(aProd_Bs2DsRho)
    otherargs_Bs2DsRho.append(aDet_Bs2DsRho)
    otherargs_Bs2DsRho.append(aTagEffList_Bs2DsRho)
    # 
    cosh_Bs2DsRho = DecRateCoeff('dsrho_cosh', 'dsrho_cosh', DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  one,      one,      *otherargs_Bs2DsRho)
    sinh_Bs2DsRho = DecRateCoeff('dsrho_sinh', 'dsrho_sinh', flag | DecRateCoeff.CPEven,
                            idVar_B, tagDecComb,  D_Bs2DsRho,    Dbar_Bs2DsRho, *otherargs_Bs2DsRho)
    cos_Bs2DsRho  = DecRateCoeff('dsrho_cos',  'dsrho_cos' , DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  C_Bs2DsRho,    C_Bs2DsRho,    *otherargs_Bs2DsRho)
    sin_Bs2DsRho  = DecRateCoeff('dsrho_sin',  'dsrho_sin',  flag | DecRateCoeff.CPOdd,
                            idVar_B, tagDecComb,  Sbar_Bs2DsRho, S_Bs2DsRho,    *otherargs_Bs2DsRho)
    #
    time_Bs2DsRho_noacc    = RooBDecay('time_Bs2DsRho_noacc','time_Bs2DsRho_noacc', timeVar_B, TauInvGs, DeltaGammas,
                                  cosh_Bs2DsRho, sinh_Bs2DsRho, cos_Bs2DsRho, sin_Bs2DsRho,
                                  DeltaMs,trm_Bs2DsRho, RooBDecay.SingleSided)
    #
    time_Bs2DsRho             = RooEffProd('time_Bs2DsRho','time_Bs2DsRho',time_Bs2DsRho_noacc,tacc_Bs2DsRho)
    #The DsRho - true ID true
    trueidval = myconfigfile["DecayModeParameters"]["Bs2DsRho"]["TRUEID"]
    trueid_Bs2DsRho = RooGenericPdf("trueid_Bs2DsRho","exp(-100.*abs(@0-"+trueidval+"))",RooArgList(trueIDVar_B))
    #The DsRho - time error
    terr_Bs2DsRho = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(workTerr,TString("TimeErrorPdf_Bs2DsRho"), debug)
    #The DsRho - total
    timeerr_Bs2DsRho = RooProdPdf('dsrho_timeerr', 'dsrho_timeerr',  RooArgSet(terr_Bs2DsRho),
                               RooFit.Conditional(RooArgSet(time_Bs2DsRho),
                                                            RooArgSet(timeVar_B, idVar_B, tagDecComb, tagOmegaComb )))
    #-------------------------------------- Now build the total PDFs for all modes --------------------------------------------------#
    for i in range(0,5):
        #The signal - mass
        meanVarBs.append(RooRealVar(   "DblCBBsPDF_mean_%s"%(nameDs[i]) ,  "mean",    myconfigfile["mean"][i]    ))
        sigma1VarBs.append(RooRealVar( "DblCBBsPDF_sigma1_%s"%(nameDs[i]), "sigma1",  myconfigfile["sigma1"][i]  ))
        sigma2VarBs.append(RooRealVar( "DblCBBsPDF_sigma2_%s"%(nameDs[i]), "sigma2",  myconfigfile["sigma2"][i]  ))
        alpha1VarBs.append(RooRealVar( "DblCBBsPDF_alpha1_%s"%(nameDs[i]), "alpha1",  myconfigfile["alpha1"][i]  ))
        alpha2VarBs.append(RooRealVar( "DblCBBsPDF_alpha2_%s"%(nameDs[i]), "alpha2",  myconfigfile["alpha2"][i]  ))
        n1VarBs.append(RooRealVar(     "DblCBBsPDF_n1_%s"%(nameDs[i]),     "n1",      myconfigfile["n1"][i]      ))
        n2VarBs.append(RooRealVar(     "DblCBBsPDF_n2_%s"%(nameDs[i]),     "n2",      myconfigfile["n2"][i]      ))
        fracVarBs.append(RooRealVar(   "DblCBBsPDF_frac_%s"%(nameDs[i]),   "frac",    myconfigfile["frac"][i]    ))
        # 
        num_Signal.append(RooRealVar("num_Signal_%s"%(nameDs[i]),"num_Signal_%s"%(nameDs[i]), myconfigfile["num_Signal"][i]*size))
        evNum += myconfigfile["num_Signal"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Signal"][i]*size)+" signal events")
        #
        massB_Signal.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBs[i],
                                                                        sigma1VarBs[i], alpha1VarBs[i], n1VarBs[i],
                                                                        sigma2VarBs[i], alpha2VarBs[i], n2VarBs[i], fracVarBs[i],
                                                                        num_Signal[i], nameDs[i].Data(), "Bs", debug ))
        #The signal - mass Ds
        meanVarDs.append(RooRealVar(   "DblCBDsPDF_mean_%s"%(nameDs[i]) ,  "mean",    myconfigfile["meanDs"][i]    ))
        sigma1VarDs.append(RooRealVar( "DblCBDsPDF_sigma1_%s"%(nameDs[i]), "sigma1",  myconfigfile["sigma1Ds"][i]  ))
        sigma2VarDs.append(RooRealVar( "DblCBDsPDF_sigma2_%s"%(nameDs[i]), "sigma2",  myconfigfile["sigma2Ds"][i]  ))
        alpha1VarDs.append(RooRealVar( "DblCBDsPDF_alpha1_%s"%(nameDs[i]), "alpha1",  myconfigfile["alpha1Ds"][i]  ))
        alpha2VarDs.append(RooRealVar( "DblCBDsPDF_alpha2_%s"%(nameDs[i]), "alpha2",  myconfigfile["alpha2Ds"][i]  ))
        n1VarDs.append(RooRealVar(     "DblCBDsPDF_n1_%s"%(nameDs[i]),     "n1",      myconfigfile["n1Ds"][i]      ))
        n2VarDs.append(RooRealVar(     "DblCBDsPDF_n2_%s"%(nameDs[i]),     "n2",      myconfigfile["n2Ds"][i]      ))
        fracVarDs.append(RooRealVar(   "DblCBDsPDF_frac_%s"%(nameDs[i]),   "frac",    myconfigfile["fracDs"][i]    ))
        # 
        massD_Signal.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_D, meanVarDs[i],
                                                                        sigma1VarDs[i], alpha1VarDs[i], n1VarDs[i],
                                                                        sigma2VarDs[i], alpha2VarDs[i], n2VarDs[i], fracVarDs[i],
                                                                        num_Signal[i], nameDs[i].Data(), "Ds", debug ))
        # The signal - PIDK
        m = TString("Bs2DsK_")+nameDs[i]
        PIDK_Signal.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, magpol, lumRatio, true, debug))
        # The signal - MDFitter
        MDFitter_Signal.append(RooProdPdf("MDFitter_Signal_%s"%(nameDs[i]),"MDFitter_Signal",
                                          RooArgList(massB_Signal[i], massD_Signal[i], PIDK_Signal[i])))
        # The signal, total 
        timeandmass_Signal.append(RooProdPdf("timeandmass_Signal_%s"%(nameDs[i]),"timeandmass_Signal",RooArgList(timeerr_Signal,
                                                                                                                  MDFitter_Signal[i],
                                                                                                                  trueid_Signal))) 
        #-------------------------------------------------- Bd -> DK ----------------------------------------------------#
        num_Bd2DK.append(RooRealVar("num_Bd2DK_%s"%(nameDs[i]),"num_Bd2DK",myconfigfile["num_Bd2DK"][i]*size))
        evNum += myconfigfile["num_Bd2DK"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Bd2DK"][i]*size)+" DK events")
        #       
        timeandmass_Bd2DK.append(RooProdPdf("timeandmass_Bd2DK_%s"%(nameDs[i]),"timeandmass_Bd2DK",RooArgList(timeerr_Bd2DK,
                                                                                                      MDFitter_Bd2DK,
                                                                                                      trueid_Bd2DK))) 
        #-------------------------------------------------- Bd -> DPi ----------------------------------------------------#                          
        num_Bd2DPi.append(RooRealVar("num_Bd2DPi_%s"%(nameDs[i]),"num_Bd2DPi",myconfigfile["num_Bd2DPi"][i]*size))
        evNum += myconfigfile["num_Bd2DPi"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Bd2DPi"][i]*size)+" DPi events")
        #
        timeandmass_Bd2DPi.append(RooProdPdf("timeandmass_Bd2DPi_%s"%(nameDs[i]),"timeandmass_Bd2DPi",RooArgList(timeerr_Bd2DPi,
                                                                                                         MDFitter_Bd2DPi,
                                                                                                         trueid_Bd2DPi)))
        #------------------------------------------------- Bd -> DsK ----------------------------------------------------#
        #The Bd->DsK - mass
        meanVarBd.append(RooRealVar(    "DblCBBdPDF_mean_%s"%(nameDs[i]) ,  "mean",    myconfigfile["mean"][i]-86.8))
        sigma1VarBd.append(RooRealVar( "DblCBBdPDF_sigma1_%s"%(nameDs[i]), "sigma1",  myconfigfile["sigma1"][i]*myconfigfile["ratio1"] ))
        sigma2VarBd.append(RooRealVar(  "DblCBBdPDF_sigma2_%s"%(nameDs[i]), "sigma2",  myconfigfile["sigma2"][i]*myconfigfile["ratio2"] ))
        #    
        num_Bd2DsK.append(RooRealVar("num_Bd2DsK_%s"%(nameDs[i]),"num_Bd2DsK",myconfigfile["num_Bd2DsK"][i]*size))
        evNum += myconfigfile["num_Bd2DsK"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Bd2DsK"][i]*size)+" Bd2DsK events")
        #               
        massB_Bd2DsK.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(massVar_B, meanVarBd[i],
                                                                     sigma1VarBd[i], alpha1VarBs[i], n1VarBs[i],
                                                                     sigma2VarBd[i], alpha2VarBs[i], n2VarBs[i],
                                                                     fracVarBs[i], num_Bd2DsK[i], nameDs[i].Data(), "Bd", debug ))
        massD_Bd2DsK.append(massD_Signal[i])
        PIDK_Bd2DsK.append(PIDK_Signal[i])
        #        
        MDFitter_Bd2DsK.append(RooProdPdf("MDFitter_Bd2DsK_%s"%(nameDs[i]),"MDFitter_Bd2DsK",RooArgList(massB_Bd2DsK[i], massD_Bd2DsK[i], PIDK_Bd2DsK[i])))
        #                       
        timeandmass_Bd2DsK.append(RooProdPdf("timeandmass_Bd2DsK_%s"%(nameDs[i]),"timeandmass_Bd2DsK",RooArgList(timeerr_Bd2DsK,
                                                                                                         MDFitter_Bd2DsK[i],
                                                                                                         trueid_Bd2DsK))) #,
        #------------------------------------------------- Bs -> DsPi ----------------------------------------------------# 
        #The Bs->DsPi - mass B
        massB_Bs2DsPi.append(Bs2Dsh2011TDAnaModels.ObtainMassShape(workspace, TString("Bs2DsPi_")+nameDs[i], false, lumRatio, debug))
        #The Bs->DsPi- mass D
        massD_Bs2DsPi.append(massD_Signal[i])
        #The Bs->DsPi - PIDK
        m = TString("Bs2DsPi_")+nameDs[i]
        PIDK_Bs2DsPi.append(Bs2Dsh2011TDAnaModels.ObtainPIDKShape(workspace, m, magpol, lumRatio, true, debug))
        #The Bs->DsPi - MDFitter
        MDFitter_Bs2DsPi.append(RooProdPdf("MDFitter_Bs2DsPi_%s"%(nameDs[i]),"MDFitter_Bs2DsPi",RooArgList(massB_Bs2DsPi[i], massD_Bs2DsPi[i], PIDK_Bs2DsPi[i])))
        #                         
        num_Bs2DsPi.append(RooRealVar("num_Bs2DsPi_%s"%(nameDs[i]),"num_Bs2DsPi", myconfigfile["num_Bs2DsPi"][i]*size))
        evNum += myconfigfile["num_Bs2DsPi"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Bs2DsPi"][i]*size)+" DsPi events")
        #
        timeandmass_Bs2DsPi.append(RooProdPdf("timeandmass_Bs2DsPi_%s"%(nameDs[i]),"timeandmass_Bs2DsPi",RooArgList(timeerr_Bs2DsPi,
                                                                                                            MDFitter_Bs2DsPi[i],
                                                                                                            trueid_Bs2DsPi)))
        #------------------------------------------------- Lb -> LcK ----------------------------------------------------#
        num_Lb2LcK.append(RooRealVar("num_Lb2LcK_%s"%(nameDs[i]),"num_Lb2LcK", myconfigfile["num_Lb2LcK"][i]*size))
        evNum += myconfigfile["num_Lb2LcK"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Lb2LcK"][i]*size)+" LcK events")
        #
        timeandmass_Lb2LcK.append(RooProdPdf("timeandmass_Lb2LcK_%s"%(nameDs[i]),"timeandmass_Lb2LcK",RooArgList(timeerr_Lb2LcK,
                                                                                                         MDFitter_Lb2LcK,
                                                                                                         trueid_Lb2LcK))) 
        #------------------------------------------------- Lb -> LcPi ----------------------------------------------------#  
        num_Lb2LcPi.append(RooRealVar("num_Lb2LcPi_%s"%(nameDs[i]),"num_Lb2LcPi", myconfigfile["num_Lb2LcPi"][i]*size))
        evNum += myconfigfile["num_Lb2LcPi"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Lb2LcPi"][i]*size)+" LcPi events")
        #
        timeandmass_Lb2LcPi.append(RooProdPdf("timeandmass_Lb2LcPi_%s"%(nameDs[i]),"timeandmass_Lb2LcPi",RooArgList(timeerr_Lb2LcPi,
                                                                                                         MDFitter_Lb2LcPi,
                                                                                                         trueid_Lb2LcPi)))
        #------------------------------------------------- Lb -> Dsstp ----------------------------------------------------#
        num_Lb2Dsstp.append(RooRealVar("num_Lb2Dsstp_%s"%(nameDs[i]),"num_Lb2Dsstp", myconfigfile["num_Lb2Dsstp"][i]*size))
        evNum += myconfigfile["num_Lb2Dsstp"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Lb2Dsstp"][i]*size)+" Ds*p events")
        #The Lb->Dsp, Lb->Dsstp - mass
        massD_Lb2Dsstp.append(massD_Signal[i])
        #The Lb->Dsp, Lb->Dsstp - MDFitter
        MDFitter_Lb2Dsstp.append(RooProdPdf("MDFitter_Lb2Dsstp_%s"%(nameDs[i]),"MDFitter_Lb2Dsstp",
                                           RooArgList(massB_Lb2Dsstp, massD_Lb2Dsstp[i], PIDK_Lb2Dsstp)))
        timeandmass_Lb2Dsstp.append(RooProdPdf("timeandmass_Lb2Dsstp_%s"%(nameDs[i]),"timeandmass_Lb2Dsstp",RooArgList(timeerr_Lb2Dsstp,
                                                                                                               MDFitter_Lb2Dsstp[i],
                                                                                                               trueid_Lb2Dsstp)))
        #------------------------------------------------- Lb -> Dsp ----------------------------------------------------#
        num_Lb2Dsp.append(RooRealVar("num_Lb2Dsp_%s"%(nameDs[i]),"num_Lb2Dsp", myconfigfile["num_Lb2Dsp"][i]*size))
        evNum += myconfigfile["num_Lb2Dsp"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Lb2Dsp"][i]*size)+" Dsp events")
        #The Lb->Dsp - mass
        massD_Lb2Dsp.append(massD_Signal[i])
        #The Lb->Dsp
        MDFitter_Lb2Dsp.append(RooProdPdf("MDFitter_Lb2Dsp_%s"%(nameDs[i]),"MDFitter_Lb2Dsp",
                                       RooArgList(massB_Lb2Dsp, massD_Lb2Dsp[i], PIDK_Lb2Dsp)))
        timeandmass_Lb2Dsp.append(RooProdPdf("timeandmass_Lb2Dsp_%s"%(nameDs[i]),"timeandmass_Lb2Dsp",RooArgList(timeerr_Lb2Dsp,
                                                                                                         MDFitter_Lb2Dsp[i],
                                                                                                         trueid_Lb2Dsp)))
        #------------------------------------------------- Combinatorial ----------------------------------------------------#
        #The combinatorics - mass
        num_Combo.append(RooRealVar("num_Combo_%s"%(nameDs[i]),"num_Combo", myconfigfile["num_Combo"][i]*size))
        evNum += myconfigfile["num_Combo"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Combo"][i]*size)+" combo events")
        #The combinatorics - mass B
        cBVar.append(RooRealVar("CombBkg_slope_Bs_%s"%(nameDs[i]),"CombBkg_slope_Bs", myconfigfile["cB"][i]))
        massB_Combo.append(RooExponential("massB_Combo_%s","massB_Combo",massVar_B, cBVar[i]))
        #The combinatorics - mass D
        cDVar.append(RooRealVar("CombBkg_slope_Ds_%s"%(nameDs[i]),"CombBkg_slope_Ds", myconfigfile["cD"][i]))
        fracDsComb.append(RooRealVar("CombBkg_fracDsComb_%s"%(nameDs[i]), "CombBkg_fracDsComb",  myconfigfile["fracDsComb"][i]))
        massD_Combo.append(Bs2Dsh2011TDAnaModels.ObtainComboDs(massVar_D, cDVar[i], fracDsComb[i], massD_Signal[i], nameDs[i], debug))
        #The combinatorics - MDFitter
        MDFitter_Combo.append(RooProdPdf("MDFitter_Combo_%s"%(nameDs[i]),"MDFitter_Combo",RooArgList(massB_Combo[i], massD_Combo[i], PIDK_Combo)))
        timeandmass_Combo.append(RooProdPdf("timeandmass_Combo_%s"%(nameDs[i]),"timeandmass_Combo",RooArgList(timeerr_Combo,
                                                                                                               MDFitter_Combo[i],
                                                                                                               trueid_Combo))) 
        #------------------------------------------------- Low mass K ----------------------------------------------------#
        #The low mass - mass D
        massD_LM1.append(massD_Signal[i])
        PIDK_LM1.append(PIDK_Signal[i]) 

        #The low mass - MDFitter
        MDFitter_LM1.append(RooProdPdf("MDFitter_LM1_%s"%(nameDs[i]),"MDFitter_LM1",RooArgList(massB_LM1, massD_LM1[i], PIDK_LM1[i])))
        #
        num_LM1.append( RooRealVar("num_LM1_%s"%(nameDs[i]),"num_LM1",myconfigfile["num_LM1"][i]*size))
        evNum += myconfigfile["num_LM1"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_LM1"][i]*size)+" low mass kaon-like events")
        #
        timeandmass_LM1.append(RooProdPdf("timeandmass_LM1_%s"%(nameDs[i]),"timeandmass_LM1",RooArgList(timeerr_LM1,
                                                                                                         MDFitter_LM1[i],
                                                                                                         trueid_LM1))) 
        #------------------------------------------------- Ds*Pi ----------------------------------------------------#
        num_Bs2DsstPi.append(RooRealVar("num_Bs2DsstPi_%s"%(nameDs[i]),"num_Bs2DsstPi", myconfigfile["num_Bs2DsstPi"][i]*size))
        evNum += myconfigfile["num_Bs2DsstPi"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Bs2DsstPi"][i]*size)+" Ds*Pi events")
        #The low mass - mass D
        massD_Bs2DsstPi.append(massD_Signal[i])
        #The low mass - MDFitter
        MDFitter_Bs2DsstPi.append(RooProdPdf("MDFitter_Bs2DsstPi_%s"%(nameDs[i]),"MDFitter_Bs2DsstPi",
                                          RooArgList(massB_Bs2DsstPi, massD_Bs2DsstPi[i], PIDK_Bs2DsstPi)))
        timeandmass_Bs2DsstPi.append(RooProdPdf("timeandmass_Bs2DsstPi_%s"%(nameDs[i]),"timeandmass_Bs2DsstPi",RooArgList(timeerr_Bs2DsstPi,
                                                                                                                  MDFitter_Bs2DsstPi[i],
                                                                                                                  trueid_Bs2DsstPi)))
        #------------------------------------------------- DsRho  ----------------------------------------------------#
        num_Bs2DsRho.append(RooRealVar("num_Bs2DsRho_%s"%(nameDs[i]),"num_Bs2DsRho", myconfigfile["num_Bs2DsRho"][i]*size))
        evNum += myconfigfile["num_Bs2DsRho"][i]*size
        printifdebug(debug,"Generating "+str(myconfigfile["num_Bs2DsRho"][i]*size)+" DsRho events")
        #The low mass - mass D
        massD_Bs2DsRho.append(massD_Signal[i])
        #The low mass - MDFitter
        MDFitter_Bs2DsRho.append(RooProdPdf("MDFitter_Bs2DsRho_%s"%(nameDs[i]),"MDFitter_Bs2DsRho",
                                         RooArgList(massB_Bs2DsRho, massD_Bs2DsRho[i], PIDK_Bs2DsRho)))
        timeandmass_Bs2DsRho.append(RooProdPdf("timeandmass_Bs2DsRho_%s"%(nameDs[i]),"timeandmass_Bs2DsRho",RooArgList(timeerr_Bs2DsRho,
                                                                                                               MDFitter_Bs2DsRho[i],
                                                                                                               trueid_Bs2DsRho)))
        print "Cumulative number of events to be generated inclusive of decay mode",nameDs[i],"is",evNum
        #------------------------------------------------- Total bkg ----------------------------------------------------#
        #Total
        pdfList = RooArgList(timeandmass_Signal[i],
                             timeandmass_Bd2DK[i],timeandmass_Bd2DsK[i],timeandmass_Bs2DsPi[i],
                             timeandmass_Lb2LcK[i])
        pdfList.add(timeandmass_Lb2Dsp[i])
        pdfList.add(timeandmass_Lb2Dsstp[i])
        pdfList.add(timeandmass_Combo[i])
        pdfList.add(timeandmass_LM1[i])
        pdfList.add(timeandmass_Bs2DsstPi[i])
        pdfList.add(timeandmass_Bs2DsRho[i])
        pdfList.add(timeandmass_Bd2DPi[i])
        pdfList.add(timeandmass_Lb2LcPi[i])
        #
        numList = RooArgList(num_Signal[i], num_Bd2DK[i], num_Bd2DsK[i], num_Bs2DsPi[i], num_Lb2LcK[i])
        numList.add(num_Lb2Dsp[i])
        numList.add(num_Lb2Dsstp[i])
        numList.add(num_Combo[i])
        numList.add(num_LM1[i])
        numList.add(num_Bs2DsstPi[i])
        numList.add(num_Bs2DsRho[i])
        numList.add(num_Bd2DPi[i])
        numList.add(num_Lb2LcPi[i])
        #
        total_pdf.append(RooAddPdf("total_pdf_%s"%(nameDs[i]),"total_pdf", pdfList, numList))
                                   
    print "Number of events to be generated is",evNum

    for i in range(rangeDown,rangeUp) :

        workout = RooWorkspace(workName,workName)
        for j in range(0,5):
                
            gendata = total_pdf[j].generate(RooArgSet(massVar_B, massVar_D, PIDKVar_B,
                                                      timeVar_B, terrVar_B,
                                                      trueIDVar_B, idVar_B, tagDecComb, tagOmegaComb), 
                                            RooFit.Extended(),
                                            RooFit.NumEvents(evNum))
            if genwithkfactors :
                # In this case, we need to clone the dataset
                # and fill it with the smeared quantities
                # Iterate over gendata and smear event-by-event
                gendata_clone = gendata.emptyClone()
                for thisentry in range(0,gendata.numEntries()) :
                    thisArgSet          = gendata.get(thisentry)
                    originallifetime    = thisArgSet.getRealValue("lab0_LifetimeFit_ctau")
                    thistrueid          = str(int(round(thisArgSet.getRealValue("lab0_TRUEID"))))
                    # Find if the mode needs a smearing or not
                    for decaymode in myconfigfile["DecayModeParameters"] :
                        if thistrueid == myconfigfile["DecayModeParameters"][decaymode]["TRUEID"] : break
                    # First smear by the kFactors
                    kfactor             = 1.
                    if myconfigfile["DecayModeParameters"][decaymode]["KFACTOR"] :
                        # Get the right mass bin
                        thismass        = thisArgSet.getRealValue("lab0_MassFitConsD_M")
                        for historange in kFactorHistos[decaymode] :
                            if thismass > int(historange.split("_")[0]) and\
                               thismass < int(historange.split("_")[1]) :
                                break
                        kfactor         = kFactorHistos[decaymode][historange].GetRandom()
                    newlifetime         = originallifetime/kfactor
                    # Now smear by the resolution
                    smearing            = RooRandom.randomGenerator().Gaus(trm_mean.getVal(),\
                                                                           trm_scale.getVal()*\
                                                                           thisArgSet.getRealValue("lab0_LifetimeFit_ctauErr"))
                    newlifetime         += smearing
                    if (newlifetime < myconfigfile["timeRange"][0]) or (newlifetime > myconfigfile["timeRange"][1]) :
                        --thisentry
                        continue
                    thisArgSet.setRealValue("lab0_LifetimeFit_ctau",newlifetime)
                    gendata_clone.add(thisArgSet)
                gendata = gendata_clone
            if debug : gendata.Print("v")
            gendata.SetName("dataSetBsDsK_both_"+str(nameDs[j]))
            tree = gendata.store().tree()
            if single :
                dataName = TString("dataSetBsDsK_both_")+nameDs[j]
                data.append(SFitUtils.CopyDataForToys(tree,
                                                      TString(mVar),
                                                      TString(mdVar),
                                                      TString(PIDKVar),
                                                      TString(tVar),
                                                      TString(terrVar),
                                                      TString("tagDecComb")+TString("_idx"),
                                                      TString("tagOmegaComb"),
                                                      TString(charge)+TString("_idx"),
                                                      TString(trueID),
                                                      dataName,
                                                      debug))
            if savetree :
                outfile  = TFile(dir+fileNamePrefix+"Tree_"+str(nameDs[j])+"_"+str(i)+".root","RECREATE")
                tree.Write()
                outfile.Close()
                del tree 
            getattr(workout,'import')(gendata)
            del gendata 
        # No plotting if generating multiple toys in one job
        if not single :
            workout.writeToFile(dir+fileNamePrefix+"Work_"+str(i)+".root")
        # Else plot what we just did
        else :
            legend = buildLegend()
            gStyle.SetOptLogy(1)
            canv_Bmass = TCanvas("canv_Bmass","canv_Bmass", 1200, 1000)
            frame_Bmass = massVar_B.frame()
            frame_Bmass.SetTitle('')
            data[0].plotOn(frame_Bmass,RooFit.Binning(100))
            total_pdf.plotOn(frame_Bmass)
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_Signal"),RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_Bd2DK"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_Lb2LcK"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_LM1,timeandmass_Bd2DsK"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_Bs2DsPi"),RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_Bmass,RooFit.Components("timeandmass_Combo"),RooFit.LineColor(kMagenta-2))
            frame_Bmass.Draw()
            legend.Draw("same")
            canv_Bmass.Print(fileNamePrefix+"Plot_Bmass.pdf") 

            gStyle.SetOptLogy(1)
            canv_Dmass = TCanvas("canv_Dmass","canv_Dmass",1200, 1000)
            frame_Dmass = massVar_D.frame()
            frame_Dmass.SetTitle('')
            data[0].plotOn(frame_Dmass,RooFit.Binning(100))
            total_pdf.plotOn(frame_Dmass)
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_Signal"), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_Bd2DK"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_Lb2LcK"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_LM1,timeandmass_Bd2DsK"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_Bs2DsPi"),RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_Dmass,RooFit.Components("timeandmass_Combo"),RooFit.LineColor(kMagenta-2))
            frame_Dmass.Draw()
            legend.Draw("same")
            canv_Dmass.Print(fileNamePrefix+"Plot_Dmass.pdf")

            gStyle.SetOptLogy(1)
            canv_PIDK = TCanvas("canv_PIDK","canv_PIDK", 1200, 1000)
            frame_PIDK = PIDKVar_B.frame()
            frame_PIDK.SetTitle('')
            data[0].plotOn(frame_PIDK,RooFit.Binning(100))
            total_pdf.plotOn(frame_PIDK)
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_Signal"), RooFit.LineStyle(kDashed), RooFit.LineColor(kRed-7))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_Bd2DK"),RooFit.LineColor(kRed))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_Lb2LcK"),RooFit.LineColor(kGreen-3))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_LM1,timeandmass_Bd2DsK"),RooFit.LineColor(kBlue-10))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_Bs2DsPi"),RooFit.LineColor(kBlue-6))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_dsdsstp"),RooFit.LineColor(kOrange))
            total_pdf.plotOn(frame_PIDK,RooFit.Components("timeandmass_Combo"),RooFit.LineColor(kMagenta-2))
            frame_PIDK.Draw()
            legend.Draw("same")
            canv_PIDK.Print(fileNamePrefix+"Plot_PIDK.pdf")

            gStyle.SetOptLogy(0)
            canv_Bmistag = TCanvas("canv_Bmistag","canv_Btag", 1200, 1000)
            frame_Bmistag = mistagVar_B.frame()
            frame_Bmistag.SetTitle('')
            data[0].plotOn(frame_Bmistag,RooFit.Binning(50))
            frame_Bmistag.Draw()
            canv_Bmistag.Print(fileNamePrefix+"Plot_Bmistag.pdf")

            gStyle.SetOptLogy(0)
            canv_Bterr = TCanvas("canv_Bterr","canv_Bterr", 1200, 1000)
            frame_Bterr = terrVar_B.frame()
            frame_Bterr.SetTitle('')
            data[0].plotOn(frame_Bterr,RooFit.Binning(100))
            total_pdf.plotOn(frame_Bterr)
            frame_Bterr.Draw()
            canv_Bterr.Print(fileNamePrefix+"Plot_TimeErrors.pdf")

            obs = data[0].get()
            tagFName = TString(tagdec)+TString("_idx")
            tagF = obs.find(tagFName.Data())
            gStyle.SetOptLogy(0)
            canv_Btag = TCanvas("canv_Btag","canv_Btag", 1200, 1000)
            frame_Btag = tagF.frame()
            frame_Btag.SetTitle('')
            data[0].plotOn(frame_Btag,RooFit.Binning(5))
            frame_Btag.Draw()
            canv_Btag.Print(fileNamePrefix+"Plot_Tag.pdf")
            
            idFName = TString(charge)+TString("_idx")
            idF = obs.find(idFName.Data())
            gStyle.SetOptLogy(0)
            canv_Bid = TCanvas("canv_Bid","canv_Bid", 1200, 1000)
            frame_Bid = idF.frame()
            frame_Bid.SetTitle('')
            data[0].plotOn(frame_Bid,RooFit.Binning(2))
            frame_Bid.Draw()
            canv_Bid.Print(fileNamePrefix+"Plot_Charge.pdf")
            
            gStyle.SetOptLogy(1)
            
            canv_Btime = TCanvas("canv_Btime","canv_Btime", 1200, 1000)
            frame_Btime = timeVar_B.frame()
            frame_Btime.SetTitle('')
            data[0].plotOn(frame_Btime,RooFit.Binning(100))
            total_pdf.plotOn(frame_Btime)
            total_pdf.plotOn(frame_Btime,RooFit.Components("time_Signal"),RooFit.LineStyle(2))
            total_pdf.plotOn(frame_Btime,RooFit.Components("time_Bd2DK"),RooFit.LineStyle(2),RooFit.LineColor(2))
            total_pdf.plotOn(frame_Btime,RooFit.Components("time_Lb2LcK"),RooFit.LineStyle(1),RooFit.LineColor(3))
            total_pdf.plotOn(frame_Btime,RooFit.Components("time_Combo"),RooFit.LineStyle(1),RooFit.LineColor(1))
            frame_Btime.Draw()
            canv_Btime.Print(fileNamePrefix+"Plot_Btime.pdf")
            workout.writeToFile(fileNamePrefix+"Single_Work_DsK.root")

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

parser.add_option( '--savetree',
                   dest = 'savetree',
                   action = 'store_true',
                   default = False,
                   help = 'Save an ntuple as well as a workspace')

parser.add_option( '--genwithkfactors',
                   dest = 'genwithkfactors',
                   action = 'store_true',
                   default = False,
                   help = 'Generate with mass-dependent k-factors') 

parser.add_option( '--dir',
                   dest = 'dir',
                   default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/For1fbPaper/Gamma70_5M_2T_MD/')


# -----------------------------------------------------------------------------
if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    import sys
    sys.path.append("../data/")
    
    runBsDsKGenerator( options.debug,  options.single , options.configName,
                       int(options.rangeDown), int(options.rangeUp), 
                       options.seed, options.size, options.dir,options.savetree,
                       options.genwithkfactors)
    
# -----------------------------------------------------------------------------
                                
