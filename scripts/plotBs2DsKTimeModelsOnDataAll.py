#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC fit for the CP asymmetry observables        #
#   in Bs -> Ds K                                                             #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBs2DsKCPAsymmObsFitterOnData.py [-d -s ]                     #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#   Author: Manuel Schiller                                                   #
#   Author: Agnieszka Dziurda                                                 #
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

bannedtoys = [1, 4, 9, 10, 12, 19, 27, 42, 44, 46, 50, 58, 59, 60, 65, 70, 72, 76, 78, 82, 87, 96, 109, 125, 132, 134, 143, 146, 148, 166, 171, 180, 185, 186, 188, 191, 192, 195, 197, 198, 203, 206, 208, 210, 211, 212, 218, 221, 233, 238, 241, 244, 248, 251, 258, 259, 272, 273, 294, 300, 308, 323, 324, 325, 327, 330, 333, 337, 340, 349, 351, 352, 357, 359, 360, 367, 371, 372, 373, 374, 377, 382, 387, 396, 401, 404, 406, 411, 412, 425, 427, 432, 439, 443, 444, 454, 455, 457, 459, 468, 472, 477, 479, 496, 509, 513, 517, 519, 520, 522, 526, 530, 537, 538, 541, 543, 554, 555, 558, 560, 562, 564, 568, 571, 579, 584, 588, 589, 591, 596, 598, 601, 604, 607, 608, 609, 610, 611, 612, 614, 616, 619, 620, 627, 630, 632, 650, 651, 652, 653, 654, 658, 660, 661, 665, 669, 672, 673, 679, 682, 684, 689, 690, 693, 695, 698, 703, 707, 716, 722, 726, 748, 759, 762, 766, 769, 770, 777, 778, 780, 782, 783, 786, 798, 800, 804, 806, 809, 811, 827, 840, 846, 850, 856, 860, 869, 870, 876, 878, 882, 889, 895, 902, 905, 917, 919, 925, 934, 941, 942, 945, 954, 957, 959, 963, 964, 965, 968, 969, 971, 973, 974, 977, 978, 979, 984, 987, 988, 994, 995, 1000, 1004, 1008, 1015, 1023, 1034, 1037, 1052, 1067, 1070, 1073, 1074, 1075, 1080, 1082, 1083, 1097, 1104, 1109, 1110, 1112, 1117, 1127, 1130, 1133, 1134, 1144, 1147, 1152, 1156, 1157, 1176, 1183, 1195, 1199, 1206, 1207, 1222, 1232, 1234, 1235, 1237, 1246, 1253, 1266, 1272, 1276, 1280, 1286, 1287, 1291, 1296, 1298, 1307, 1309, 1310, 1315, 1318, 1319, 1328, 1332, 1334, 1336, 1340, 1341, 1348, 1351, 1352, 1354, 1360, 1368, 1371, 1372, 1377, 1384, 1386, 1390, 1397, 1399, 1408, 1411, 1413, 1426, 1428, 1434, 1439, 1444, 1446, 1448, 1457, 1458, 1463, 1466, 1467, 1472, 1475, 1477, 1478, 1483, 1485, 1494, 1496, 1507, 1509, 1511, 1515, 1516, 1517, 1518, 1519, 1520, 1524, 1536, 1539, 1540, 1542, 1545, 1547, 1551, 1554, 1555, 1558, 1561, 1564, 1569, 1570, 1572, 1595, 1596, 1602, 1604, 1606, 1607, 1622, 1623, 1624, 1628, 1633, 1640, 1650, 1654, 1656, 1660, 1666, 1677, 1683, 1684, 1686, 1694, 1696, 1697, 1703, 1713, 1717, 1741, 1745, 1747, 1751, 1759, 1764, 1766, 1771, 1776, 1778, 1780, 1787, 1791, 1795, 1805, 1812, 1813, 1816, 1817, 1819, 1828, 1838, 1841, 1845, 1847, 1858, 1862, 1865, 1871, 1876, 1886, 1887, 1888, 1893, 1894, 1899, 1905, 1907, 1914, 1921, 1924, 1927, 1933, 1934, 1935, 1938, 1944, 1950, 1973, 1976, 1978, 1980, 1986, 1990, 1995, 1997, 1999]

# MODELS
#AcceptanceFunction       =  'BdPTAcceptance'  # None/BdPTAcceptance/DTAcceptanceLHCbNote2007041
AcceptanceFunction       =  'PowLawAcceptance'

# BLINDING
Blinding =  False

param_limits = {"lower" : -3., "upper" : 3.}

# DATA FILES
saveName      = 'work_'

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------
def setConstantIfSoConfigured(var,myconfigfile):
    if var.GetName() in myconfigfile["constParams"] : var.setConstant()

#------------------------------------------------------------------------------
import threading,os,signal
from threading import *
def killme() :
    os._exit(1)
def handler(signum, frame):
    print 'Signal handler called with signal', signum
    os._exit(1)
#------------------------------------------------------------------------------
def runBdGammaFitterOnData(debug, wsname, initvars, var, probvar,pereventmistag, toys,pathToys,
                           treeToys,splitCharge,fitMeTool,configName,nokfactcorr,
                           smearaccept,accsmearfile,accsmearhist,dataName) :

    if not Blinding and not toys :
        print "RUNNING UNBLINDED!"
        #really = input('Do you really want to unblind? ')
        #if really != "yes" :
        #    exit(-1)

    #if toys :
    #    if int(pathToys.split('.')[1].split('_')[-1]) in bannedtoys :
    #        exit(-1)

    import GaudiPython
    GaudiPython.loaddict('B2DXFittersDict')
    from B2DXFitters import taggingutils, cpobservables
    GeneralModels = GaudiPython.gbl.GeneralModels
    PTResModels   = GaudiPython.gbl.PTResModels

    GeneralUtils = GaudiPython.gbl.GeneralUtils
    SFitUtils = GaudiPython.gbl.SFitUtils
    Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels
    
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay
    from ROOT import RooGaussModel, RooTruthModel,RooUnblindUniform
    from ROOT import RooAbsReal, RooDataSet, RooGaussModel
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooSimultaneous
    from ROOT import RooExponential, RooPolynomial, RooPolyVar, RooUniform
    from ROOT import RooFit, RooBDecay, RooEffProd
    from ROOT import FitMeTool, IfThreeWay, Dilution, IfThreeWayPdf
    from ROOT import CombBkgPTPdf, TagEfficiencyWeightNoCat
    from ROOT import BdPTAcceptance, TagEfficiencyWeight,PowLawAcceptance
    from ROOT import TString, Inverse, IfThreeWayCat,MistagCalibration
    from ROOT import RooUnblindCPAsymVar, RooUnblindPrecision, RooWorkspace
    from ROOT import RooNLLVar, RooMinuit, RooProfileLL, kRed, kBlue, kGreen, kOrange 
    from ROOT import TFile,TTree,RooDataHist,RooHistFunc  
    #from ROOT import TFile,TTree,RooDataHist,RooHistFunc
    from ROOT import TCanvas, TPad, RooPlot, TGraph
    from ROOT import kRed, kBlue, kGreen, kDashed, kMagenta, kBlack
    from ROOT import TLegend, TString, TLine, TH1F, TBox, TPad, TGraph,  TMarker, TGraphErrors, TLatex
    
 
    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option] 
    print "=========================================================="
 
    # tune integrator configuration
    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation','WynnEpsilon')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('maxSteps','1000')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('minSteps','0')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    # since we have finite ranges, the RooIntegrator1D is best suited to the job
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooIntegrator1D')
    #RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    #RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    #RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    #RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','20Points')
    #RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)

    dataTS = TString(dataName)
    tVarTS = TString(var)
    tProbVarTS = TString(probvar)
    tagVarTS = TString("lab0_BsTaggingTool_TAGDECISION_OS")       
    tagWeightVarTS = TString("lab0_BsTaggingTool_TAGOMEGA_OS")
    idVarTS        = TString("lab1_ID")

    if ( not toys):
        workspace = SFitUtils.ReadDataFromSWeights(TString("DsK"),dataTS, TString("#sWeights"),
                                                   myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                   tVarTS, tagVarTS, tagWeightVarTS, idVarTS, debug)
    else:
        workspace = SFitUtils.ReadDataFromSWeightsToys(TString("DsK"),TString(pathToys), TString(treeToys),
                                                       myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                       tVarTS, tagVarTS+TString("_idx"),
                                                       tagWeightVarTS, idVarTS+TString("_idx"),nokfactcorr, debug)
        
   
    workspace.Print()

    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)

    if ( not toys ):
        time   = GeneralUtils.GetObservable(workspace,tVarTS, debug)
        bTagMap    = GeneralUtils.GetObservable(workspace,tagVarTS, debug)
        mistag = GeneralUtils.GetObservable(workspace,tagWeightVarTS, debug)
        fChargeMap = GeneralUtils.GetObservable(workspace,idVarTS, debug)
    else:
        time   = GeneralUtils.GetObservable(workspace,tVarTS, debug)
        bTagMap    = GeneralUtils.GetObservable(workspace,tagVarTS+TString("_idx"), debug)
        mistag = GeneralUtils.GetObservable(workspace,tagWeightVarTS, debug)
        fChargeMap = GeneralUtils.GetObservable(workspace,idVarTS+TString("_idx"), debug)

    mistag.setRange(0,0.5)    
    mass = RooRealVar('mass', '%s mass' % bName, 5., 6.)
    timeerr = RooRealVar('timeerr', '%s decay time error' % bName, 0.04, 0.001, 0.1, 'ps')
    timeerravg = RooRealVar('timeerravg','timeerravg',0.05)    
  
    gammas = RooRealVar('Gammas', '%s average lifetime' % bName, myconfigfile["Gammas"], 0., 5., 'ps^{-1}')
    gammas.setError(0.051)
    setConstantIfSoConfigured(gammas,myconfigfile)
    deltaGammas = RooRealVar('deltaGammas', 'Lifetime difference', myconfigfile["DeltaGammas"], -1., 1., 'ps^{-1}')
    setConstantIfSoConfigured(deltaGammas,myconfigfile)

    deltaMs = RooRealVar('deltaMs', '#Delta m_{s}', myconfigfile["DeltaMs"], 5., 30., 'ps^{-1}')
    setConstantIfSoConfigured(deltaMs,myconfigfile)

    # tagging
    # -------
    tagEffSig = RooRealVar('tagEffSig', 'Signal tagging efficiency'    , myconfigfile["TagEffSig"], 0., 1.)
    setConstantIfSoConfigured(tagEffSig,myconfigfile)
    
    tagOmegaSig = RooRealVar('tagOmegaSig', 'Signal mistag rate'    , myconfigfile["TagOmegaSig"], 0., 1.)
    if not pereventmistag : setConstantIfSoConfigured(tagOmegaSig,myconfigfile)
   
    # Define the observables
    # ----------------------
    if pereventmistag : 
        observables = RooArgSet(time,bTagMap,fChargeMap,mistag)    
    else : 
        observables = RooArgSet(time,bTagMap,fChargeMap)
 
    # Data set
    #-----------------------

    if toys :
        data_pos = GeneralUtils.GetDataSet(workspace,"dataSet_time_Bs2DsK_pos", debug)#[]
        data_neg = GeneralUtils.GetDataSet(workspace,"dataSet_time_Bs2DsK_neg", debug)
        nEntries_pos = data_pos.numEntries()
        nEntries_neg = data_neg.numEntries() 
        if not splitCharge :
            data = data_pos
            data.append(data_neg)
            nEntries = data.numEntries()#[]
    else :
        data2 = GeneralUtils.GetDataSet(workspace,"dataSet_time_Bs2DsK", debug)
        nEntries = data2.numEntries()    

    # Decay time resolution model
    # ---------------------------
    if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
        trm = PTResModels.getPTResolutionModel(myconfigfile["DecayTimeResolutionModel"],
                                               time, 'Bs', debug,myconfigfile["resolutionScaleFactor"],myconfigfile["resolutionMeanBias"])
    else :
        # the decay time error is an extra observable !
        observables.add( timeerr )
        # time, mean, scale, timeerr
        #trm = RooGaussModel( 'GaussianWithLandauPEDTE', 'GaussianWithLandauPEDTE',
        #                     time, RooFit.RooConst(0.), RooFit.RooConst(1.), timeerr )
        trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', 0., 'ps' )
        trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', 1.37 )
        trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGausPEDTE',
                             time, trm_mean, trm_scale, timeerr )
    
    # Decay time acceptance function
    # ------------------------------
    if AcceptanceFunction and not (AcceptanceFunction == None or AcceptanceFunction == 'None'):
        if AcceptanceFunction == "BdPTAcceptance" :
            tacc_slope  = RooRealVar('tacc_slope'   , 'BdPTAcceptance_slope'    , myconfigfile["tacc_slope"]    , -100.0 , 100.0 )
            tacc_offset = RooRealVar('tacc_offset'  , 'BdPTAcceptance_offset'   , myconfigfile["tacc_offset"]   , -100.0 , 100.0 )
            tacc_beta   = RooRealVar('tacc_beta'    , 'BdPTAcceptance_beta'     , myconfigfile["tacc_beta"]     , -10.00 , 10.00 )
            tacc = BdPTAcceptance('BsPTAccFunction', '%s decay time acceptance function' % bName,
                                  time, tacc_beta, tacc_slope, tacc_offset)
            setConstantIfSoConfigured(tacc_slope,myconfigfile)
            setConstantIfSoConfigured(tacc_offset,myconfigfile)
            setConstantIfSoConfigured(tacc_beta,myconfigfile)
        elif AcceptanceFunction == 'PowLawAcceptance' : 
            if smearaccept :
                print 'SMEARING THE ACCEPTANCE FUNCTION FROM HISTOGRAM'
                print accsmearfile, accsmearhist 
                rfile = TFile(accsmearfile, 'read')
                hcorr = rfile.Get(accsmearhist)
                ardhist = RooDataHist('ardhist', 'DsK/DsPi acceptance ratio datahist',
                                        RooArgList(time), RooFit.Import(hcorr, False))
                accratio = RooHistFunc('accratio', 'DsK/DsPi acceptance ratio',
                                        RooArgSet(time), ardhist)
            else :
                print 'NOT SMEARING THE ACCEPTANCE FUNCTION'
                accratio = RooConstVar('accratio','accratio',1.)
            tacc_beta       = RooRealVar('tacc_beta'    , 'PowLawAcceptance_beta',      myconfigfile["tacc_beta"]       , 0.00 , 0.05) 
            tacc_exponent   = RooRealVar('tacc_exponent', 'PowLawAcceptance_exponent',  myconfigfile["tacc_exponent"]   , 1.00 , 4.00)
            tacc_offset     = RooRealVar('tacc_offset'  , 'PowLawAcceptance_offset',    myconfigfile["tacc_offset"]     , -0.2 , 0.10)
            tacc_turnon     = RooRealVar('tacc_turnon'  , 'PowLawAcceptance_turnon',    myconfigfile["tacc_turnon"]     , 0.50 , 5.00)  
            accratio.Print("v") 
            if smearaccept :
                tacc = PowLawAcceptance('BsPowLawAcceptance', '%s decay time acceptance function' % bName,
                                        tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta,accratio)
            else :
                tacc = PowLawAcceptance('BsPowLawAcceptance', '%s decay time acceptance function' % bName,
                                        tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta)
            setConstantIfSoConfigured(tacc_beta,myconfigfile)
            setConstantIfSoConfigured(tacc_exponent,myconfigfile)
            setConstantIfSoConfigured(tacc_offset,myconfigfile)
            setConstantIfSoConfigured(tacc_turnon,myconfigfile)
    else :
        tacc = None

    #sigTagWeight = RooFormulaVar('sTagEffWeight','abs(@0)*@1 + (1-abs(@0))*(1-@1)',RooArgList(bTagMap,tagEffSig))
    #sigTagWeight = TagEfficiencyWeightNoCat('sTagEffWeight','tag efficiency weight', bTagMap,tagEffSig)

#    ACPobs = cpobservables.AsymmetryObservables(myconfigfile["ArgLf"], myconfigfile["ArgLbarfbar"], myconfigfile["ModLf"])
#    ACPobs.printtable()
        

    sigC = RooRealVar('C', 'C coeff.', myconfigfile["sigC"], param_limits["lower"], param_limits["upper"])
    sigS = RooRealVar('S', 'S coeff.', myconfigfile["sigS"], param_limits["lower"], param_limits["upper"])
    sigD = RooRealVar('D', 'D coeff.', myconfigfile["sigD"], param_limits["lower"], param_limits["upper"])
    sigCbar = RooRealVar('Cbar', 'Cbar coeff.', myconfigfile["sigC"], param_limits["lower"], param_limits["upper"])
    sigSbar = RooRealVar('Sbar', 'Sbar coeff.', myconfigfile["sigSbar"], param_limits["lower"], param_limits["upper"])
    sigDbar = RooRealVar('Dbar', 'Dbar coeff.', myconfigfile["sigDbar"], param_limits["lower"], param_limits["upper"])
    setConstantIfSoConfigured(sigC,myconfigfile)
    setConstantIfSoConfigured(sigS,myconfigfile)
    setConstantIfSoConfigured(sigD,myconfigfile)
    setConstantIfSoConfigured(sigCbar,myconfigfile)
    setConstantIfSoConfigured(sigSbar,myconfigfile)
    setConstantIfSoConfigured(sigDbar,myconfigfile)

    #sigC = RooRealVar('C', 'C coeff.', 0.93233)
    #sigS = RooRealVar('S', 'S coeff.', -0.082831)
    #sigD = RooRealVar('D', 'D coeff.', -1.3475)
    #sigCbar = RooRealVar('Cbar', 'Cbar coeff.', 0.93233)
    #sigSbar = RooRealVar('Sbar', 'Sbar coeff.', 1.1580)
    #sigDbar = RooRealVar('Dbar', 'Dbar coeff.', -0.78309)

    decayPath = RooCategory('decayPath','Category for the possible decay paths')
    dP = [TString("Bs2DsNKP"),
          TString("Bs2DsPKN"),
          TString("Bsbar2DsNKP"),
          TString("Bsbar2DsPKN"),
          TString("Untagged2DsNKP"),
          TString("Untagged2DsPKN")]
    
#    for i in range(0,6):
#        print dP[i]
    decayPath.defineType(dP[0].Data())
    decayPath.defineType(dP[1].Data())
    decayPath.defineType(dP[2].Data())
    decayPath.defineType(dP[3].Data())
    decayPath.defineType(dP[4].Data())
    decayPath.defineType(dP[5].Data())
    
    bTagMap2 = RooMappedCategory('bTagMap2', 'Mapping for the b-tagging result',
                                 decayPath, 'NotMapped', 9000)
    bTagMap2.map('*Bs2*'      , 'B'       ,  1)
    bTagMap2.map('*Bsbar2*'   , 'Bbar'    , -1)
    bTagMap2.map('*Untagged2*', 'Untagged',  0)
    
    fChargeMap2 = RooMappedCategory('fChargeMap2', 'Mapping for the bachelor charge',
                                    decayPath, 'NotMapped', 9000)
    fChargeMap2.map('*KP', 'h+',  1)
    fChargeMap2.map('*KN', 'h-', -1)

    mixState = RooMappedCategory('mixState', 'mixState = bTagMap2 * fChargeMap2',
                                 decayPath, 'NotMapped', 9000)
    #mixState.map('Bs2DsNKP', "Notmixed", 1)
    #mixState.map('Bsbar2DsPKN', 'Notmixed', 1)
    #mixState.map('Bs2DsPKN', 'Mixed', -1)
    #mixState.map('Bsbar2DsNKP', 'Mixed', -1)
    #mixState.map('Untagged2DsNKP', 'Untagged', 0)
    #mixState.map('Untagged2DsPKN', 'Untagged', 0)

    Mix = [TString("Mixed"),
           TString("Unmixed"),
           TString("Untagged")]
    
    mixState.map('Bs2DsNKP', Mix[1].Data(), 1)
    mixState.map('Bsbar2DsPKN', Mix[1].Data(), 1)
    mixState.map('Bs2DsPKN', Mix[0].Data(), -1)
    mixState.map('Bsbar2DsNKP', Mix[0].Data(), -1)
    mixState.map('Untagged2*', Mix[2].Data(), 0)
    
    
    sigTagWeight = TagEfficiencyWeight('sTagEffWeight','tag efficiency weight', bTagMap2,tagEffSig)
    #sigWeightedDs  = RooFormulaVar('sigWeightedDs','0.5*((1+@0)*@1+(1-@0)*@2)',RooArgList(fChargeMap,sigD,sigDbar))
    sigWeightedDs  = IfThreeWayCat('sigWeightedDs', 'sigWeightedDs',  fChargeMap2, sigD, zero, sigDbar)
    # the following includes the minus sign in front of the sin term
    #sigWeightedSs  = RooFormulaVar('sigWeightedSs','0.5*((1+@0)*@1+(1-@0)*@2)',RooArgList(fChargeMap,sigSbar,sigS))
    sigWeightedSs  = IfThreeWayCat('sigWeightedSs', 'sigWeightedSs',  fChargeMap2, sigS, zero, sigSbar)

    #untaggedWeight = RooFormulaVar('untaggedWeight','2-abs(@0)',RooArgList(bTagMap))
    untaggedWeight = IfThreeWayCat('untaggedWeight','untaggedWeight', bTagMap2, one, two, one                  )
    if not pereventmistag : 
        #sigDilution = RooFormulaVar('sigDilution','1-2*@0',RooArgList(tagOmegaSig))
        sigDilution = Dilution(  'sigDilution',  'signal (DsPi) Dilution', tagOmegaSig                              )
    else : 
        #sigDilution = RooFormulaVar('sigDilution','1-2*@0',RooArgList(mistag))
        calibration_p1 = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"])
        calibration_p0 = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"])
        mistag_calibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',mistag,calibration_p0,calibration_p1) 
        sigDilution = Dilution(  'sigDilution',  'sigDilution',      mistag_calibrated                                )
    #mixState        = RooProduct('mixState',     'mixState',         RooArgSet(bTagMap,fChargeMap   )      ) 
    
    sigCosSin_i0    = RooProduct('sigCosSin_i0', 'sigCosSin_i0',     RooArgSet(mixState, sigDilution, sigTagWeight) )

    # Set the signal handler and a 5-second alarm
    #signal.signal(signal.SIGALRM, handler)
    #signal.alarm(120)
 
    if not splitCharge and not fitMeTool:
        sigCosh         = RooProduct('sigCosh',      'cosh coefficient', RooArgSet(untaggedWeight, sigTagWeight)        )
        sigSinh         = RooProduct('sigSinh',      'sinh coefficient', RooArgSet(sigCosh, sigWeightedDs)              )
        sigCos          = RooProduct('sigCos',       'cos coefficient',  RooArgSet(sigCosSin_i0, sigC)                  )
        sigSin          = RooProduct('sigSin',       'sin coefficient',  RooArgSet(sigCosSin_i0, sigWeightedSs,minusone)         )
    
   #     if debug :
   #         print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!' 
   #         data.Print("v")
   #         for i in range(0,nEntries) : 
   #             data.get(i).Print("v")
   #             print data.weight()
    
        tauinv          = Inverse( "tauinv","tauinv", gammas)
        time_noacc      = RooBDecay('time_signal_noacc','time_signal_noacc', time, tauinv, deltaGammas, 
                                            sigCosh, sigSinh,sigCos, sigSin,
                                            deltaMs,trm, RooBDecay.SingleSided)

        '''
        bTagMap.setBins(5,'cache')
        fChargeMap.setBins(5,'cache')
        mistag.setBins(6,'cache')
        time_noacc.setParameterizeIntegral(RooArgSet(mistag))
        '''   

        sigTimePDF      = RooEffProd('time_signal','time_signal',time_noacc,tacc)
        
        #totPDF = sigTimePDF
        nSig = RooRealVar("nSig","nSig",1000,0,data2.numEntries()+0.5*data2.numEntries())
        totPDF = RooExtendPdf("sigEPDF","sigEPDF",sigTimePDF,nSig)

        data1 = []
        range = [0,1,2,3,4,5]
        for i in range:
            namedata = TString("dataSet_time_Bs2DsK")+dP[i]
            data1.append(GeneralUtils.GetDataSet(workspace,namedata.Data()))
            
            
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(decayPath),
                              RooFit.Import(dP[0].Data(),data1[0]),
                              RooFit.Import(dP[1].Data(),data1[1]),
                              RooFit.Import(dP[2].Data(),data1[2]),
                              RooFit.Import(dP[3].Data(),data1[3]),
                              RooFit.Import(dP[4].Data(),data1[4]),
                              RooFit.Import(dP[5].Data(),data1[5]))
        
        data = combData
        nEntries = data.numEntries()
        print nEntries
        print data.GetName()

        if debug :
            print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!'
            data.Print("v")
            for i in range(0,nEntries) :
                data.get(i).Print("v")
                print data.weight()
                                                                
        
        if toys or not Blinding: #Unblind yourself
            myfitresult = totPDF.fitTo(data, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                             RooFit.Verbose(True), RooFit.SumW2Error(True))#
                                             #,RooFit.ConditionalObservables(RooArgSet(mistag)))
            myfitresult.Print("v")
            myfitresult.correlationMatrix().Print()
            myfitresult.covarianceMatrix().Print()
        else :    #Don't
            myfitresult = totPDF.fitTo(data, RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                             RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 
            par[1].Print("v")
            par[2].Print("v")
            par[3].Print("v")
            par[4].Print("v")
            if  (sigS.getVal() < param_limits["lower"] + sigS.getError() ) or \
                (sigS.getVal() > param_limits["upper"] - sigS.getError() ) :
                print "S IS CLOSE TO THE FIT LIMITS!!!!"       
            if  (sigSbar.getVal() < param_limits["lower"] + sigSbar.getError() ) or \
                (sigSbar.getVal() > param_limits["upper"] - sigSbar.getError() ) : 
                print "Sbar IS CLOSE TO THE FIT LIMITS!!!!"
            if  (sigD.getVal() < param_limits["lower"] + sigD.getError() ) or \
                (sigD.getVal() > param_limits["upper"] - sigD.getError() ) : 
                print "D IS CLOSE TO THE FIT LIMITS!!!!"       
            if  (sigDbar.getVal() < param_limits["lower"] + sigDbar.getError() ) or \
                (sigDbar.getVal() > param_limits["upper"] - sigDbar.getError() ) :
                print "Dbar IS CLOSE TO THE FIT LIMITS!!!!"     

        canvas = TCanvas('TimeCanvas', 'Propertime canvas')
        canvas.SetTitle('Fit in propertime')
        canvas.cd()
        
        #padgraphics = TPad("padgraphics","",0.005,0.355,0.995,0.995)
        #padgraphics.Draw()
        #padgraphics.cd()
        
        time.setRange(0.0,15.0)
        frame_t = time.frame()
        frame_t.SetTitle('')
        
        frame_t.GetXaxis().SetLabelSize( 0.055 )
        frame_t.GetYaxis().SetLabelSize( 0.055 )
        frame_t.GetXaxis().SetLabelFont( 132 )
        frame_t.GetYaxis().SetLabelFont( 132 )
        frame_t.GetXaxis().SetLabelOffset( 0.01 )
        frame_t.GetYaxis().SetLabelOffset( 0.01 )
        
        frame_t.GetXaxis().SetTitleSize( 0.055 )
        frame_t.GetYaxis().SetTitleSize( 0.055 )
        frame_t.GetYaxis().SetNdivisions(5)
        
        frame_t.GetXaxis().SetTitleOffset( 1.10 )
        frame_t.GetYaxis().SetTitleOffset( 1.00)
        frame_t.GetXaxis().SetTitleFont( 132 )
        frame_t.GetYaxis().SetTitleFont( 132 )
        frame_t.GetXaxis().SetTitle('#tau (B_{s} #rightarrow D_{s} K) [ps]')
        frame_t.GetYaxis().SetTitle('Candidates/(0.2 ps)')
        
        #frame_t.GetYaxis().SetRangeUser(0.001,300)
        model = totPDF
        data2.plotOn(frame_t,RooFit.Binning(74)) #,RooFit.MarkerColor(kRed))
        #data.plotOn(frame_t,
        #            RooFit.Cut("decayPath==decayPath::Bs2DsNKP || decayPath==decayPath::Bs2DsPKN || decayPath==decayPath::Bsbar2DsNKP || decayPath==decayPath::Bsbar2DsPKN || decayPath==decayPath::Untagged2DsNKP || decayPath==decayPath::Untagged2DsPKN"),
        #            RooFit.Binning(70))

        model.plotOn(frame_t,
                     RooFit.Slice(decayPath,dP[0].Data()),RooFit.Slice(decayPath,dP[1].Data()), RooFit.Slice(decayPath,dP[2].Data()),
                     RooFit.Slice(decayPath,dP[3].Data()),RooFit.Slice(decayPath,dP[4].Data()),RooFit.Slice(decayPath,dP[5].Data()),
                     #                     #RooFit.Slice(wksp.cat("fChargeMap"), "h+"),
                     #                     #RooFit.Components('sigEPDF'),
                     RooFit.LineWidth(3), RooFit.LineColor(kMagenta),
                     RooFit.Normalization( 1. )
                     )
        model.plotOn(frame_t,
                     RooFit.Slice(decayPath,dP[0].Data()),
                     #RooFit.Slice(wksp.cat("fChargeMap"), "h+"),
                     #RooFit.Components('sigEPDF'),
                     RooFit.LineWidth(1), RooFit.LineColor(kRed),
                     RooFit.Normalization( 0.108)
                     )
        model.plotOn(frame_t,
                     RooFit.Slice(decayPath,"Bs2DsPKN"),
                     #RooFit.Slice(wksp.cat("fChargeMap"), "h-"),
                     RooFit.Components('sigEPDF'),
                     RooFit.LineWidth(1), RooFit.LineColor(kBlue),
                     RooFit.Normalization( 0.0969 )
                     )
        model.plotOn(frame_t,
                     RooFit.Slice(decayPath, "Bsbar2DsNKP"),
                     RooFit.Components('sigEPDF'),
                     RooFit.LineWidth(3), RooFit.LineColor(kRed), RooFit.LineStyle(kDashed),
                     RooFit.Normalization( 0.109 ))
        model.plotOn(frame_t,
                     RooFit.Slice(decayPath, "Bsbar2DsPKN"),
                     RooFit.Components('sigEPDF'),
                     RooFit.LineWidth(3), RooFit.LineColor(kBlue), RooFit.LineStyle(kDashed),
                     RooFit.Normalization( 0.099 )
                     )
        model.plotOn(frame_t,
                     RooFit.Slice(decayPath, "Untagged2DsNKP"),
                     RooFit.Components('sigEPDF'),
                     RooFit.LineWidth(1), RooFit.LineColor(kGreen + 1),
                     RooFit.Normalization( 0.2974 )
                     )
        model.plotOn(frame_t,
                     RooFit.Slice(decayPath, "Untagged2DsPKN"),
                     #            RooFit.Slice(wksp.cat("fChargeMap"), "h-"),
                     RooFit.Components('sigEPDF'),
                     RooFit.LineWidth(3), RooFit.LineColor(kGreen + 1), RooFit.LineStyle(kDashed),
                     RooFit.Normalization( 0.2895 )
                     )
                
        frame_t.Draw()
        
        legend = TLegend( 0.1, 0.1, 0.5, 0.5 )
        legend.SetTextSize(0.05)
        legend.SetTextFont(12)
        legend.SetFillColor(4000)
        legend.SetShadowColor(0)
        legend.SetBorderSize(0)
        legend.SetTextFont(132)

        gr = TGraphErrors(10);
        gr.SetName("gr");
        gr.SetLineColor(kBlack);
        gr.SetLineWidth(2);
        gr.SetMarkerStyle(20);
        gr.SetMarkerSize(1.3);
        gr.SetMarkerColor(kBlack);
        gr.Draw("P");
        legend.AddEntry("gr","Data","lep");
        
        l11 = TLine()
        l11.SetLineColor(kMagenta)
        l11.SetLineWidth(4)
        #l11.SetLineStyle(kDashed)
        legend.AddEntry(l11, "Combined", "L")
        

        l1 = TLine()
        l1.SetLineColor(kRed)
        l1.SetLineWidth(4)
        #l1.SetLineStyle(kDashed)
        legend.AddEntry(l1, "B_{s}#rightarrow D_{s}^{-}K^{+}", "L")

        l2 = TLine()
        l2.SetLineColor(kBlue)
        l2.SetLineWidth(4)
        #l1.SetLineStyle(kDashed)
        legend.AddEntry(l2, "B_{s}#rightarrow D_{s}^{+}K^{-}", "L")

        l3 = TLine()
        l3.SetLineColor(kRed)
        l3.SetLineWidth(4)
        l3.SetLineStyle(kDashed)
        legend.AddEntry(l3, "#bar{B}_{s}#rightarrow D_{s}^{-}K^{+}", "L")
        
        l4 = TLine()
        l4.SetLineColor(kBlue)
        l4.SetLineWidth(4)
        l4.SetLineStyle(kDashed)
        legend.AddEntry(l4, "#bar{B}_{s}#rightarrow D_{s}^{+}K^{-}", "L")

        l5 = TLine()
        l5.SetLineColor(kGreen+1)
        l5.SetLineWidth(4)
        #l3.SetLineStyle(kDashed)
        legend.AddEntry(l5, "Untagged D_{s}^{-}K^{+}", "L")
        
        l6 = TLine()
        l6.SetLineColor(kGreen+1)
        l6.SetLineWidth(4)
        l6.SetLineStyle(kDashed)
        legend.AddEntry(l6, "Untagged D_{s}^{+}K^{-}", "L")
                                                        
        legend.Draw("same")
        
        from ROOT import TLatex

        myLatex = TLatex()
        myLatex.SetTextFont(132)
        myLatex.SetTextColor(1)
        myLatex.SetTextSize(0.06)
        myLatex.SetTextAlign(12)
        myLatex.SetNDC(1)
        myLatex.SetTextSize(0.06)
        myLatex.DrawLatex(0.65, 0.725,
                          "#splitline{#splitline{LHCb}{Preliminary 1 fb^{-1}}}{}")
                                        
        
        #frame_t.Draw()
        canvas.Update()

        #padpull = TPad("padpull","",0.005,0.005,0.995,0.345)
        #padpull.Draw()
        #padpull.cd()
        
        pullHist = frame_t.pullHist()

        #pullHist.GetXaxis().SetTitle('time [ps]')
        #pullHist.GetXaxis().SetTitleSize(0.075)
        
        pullHist.SetMaximum(4.00)
        pullHist.SetMinimum(-4.00)
        axisX = pullHist.GetXaxis()
        axisX.Set(100,0,15)
        axisX.SetTitle('#tau (B_{s} #rightarrow D_{s} K) [ps]')
        axisX.SetTitleSize(0.095)
        
        axisY = pullHist.GetYaxis()
        max = axisY.GetXmax()
        min = axisY.GetXmin()
        axisY.SetLabelSize(0.095)
        axisY.SetNdivisions(5)
        
        axisX = pullHist.GetXaxis()
        maxX = axisX.GetXmax()
        minX = axisX.GetXmin()
        axisX.SetLabelSize(0.095)
        
        range = max-min
        zero = max/range
        print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
        print "maxX: %s, minX: %s"%(maxX,minX)
                                                                                        
        graph = TGraph(2)
        graph.SetMaximum(max)
        graph.SetMinimum(min)
        graph.SetPoint(1,0,0)
        graph.SetPoint(2,15,0)
        graph2 = TGraph(2)
        graph2.SetMaximum(max)
        graph2.SetMinimum(min)
        graph2.SetPoint(1,0,-3)
        graph2.SetPoint(2,15,-3)
        graph2.SetLineColor(kRed)
        graph3 = TGraph(2)
        graph3.SetMaximum(max)
        graph3.SetMinimum(min)
        graph3.SetPoint(1,0,3)
        graph3.SetPoint(2,15,3)
        graph3.SetLineColor(kRed)
        
        pullHist.SetTitle("");
        
        #pullHist.Draw("AP")
        #graph.Draw("same")
        #graph2.Draw("same")
        #graph3.Draw("same")
        
        #canvas.SetLogy(True)
        canvas.Update()
        canvas.Print('time_DsK.root')
                         

        workout = RooWorkspace("workspace","workspace")
        getattr(workout,'import')(data)
        getattr(workout,'import')(totPDF)
        getattr(workout,'import')(myfitresult)
        workout.writeToFile("WS_Time_DsK.root")
                        
    elif not splitCharge :   
        sigCosh         = RooProduct('sigCosh',      'cosh coefficient', RooArgSet(untaggedWeight, sigTagWeight)        )   
        sigSinh         = RooProduct('sigSinh',      'sinh coefficient', RooArgSet(sigCosh, sigWeightedDs)              )   
        sigCos          = RooProduct('sigCos',       'cos coefficient',  RooArgSet(sigCosSin_i0, sigC)                  )   
        sigSin          = RooProduct('sigSin',       'sin coefficient',  RooArgSet(sigCosSin_i0, sigWeightedSs)         )
               
        if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
            sigTimePDF = GeneralModels.buildRooBDecayPDF(
                time, gammas, deltaGammas, deltaMs,
                sigCosh, sigSinh, sigCos, sigSin,
                trm, tacc,
                'Sig', bName, debug)
        else :
            sigTimePDF = GeneralModels.buildRooBDecayPDFWithPEDTE(
                time, timeerr, gammas, deltaGammas, deltaMs,
                sigCosh, sigSinh, sigCos, sigSin,
                terrpdf, trm, tacc,
                'Sig', bName, debug)
       
        ''' 
        workspace_mistag  = GeneralUtils.LoadWorkspace(TString("/afs/cern.ch/work/a/adudziak/public/workspace/work_dsk_toys.root"),
                                                       TString("workspace"))     
        mistag_signal     = Bs2Dsh2011TDAnaModels.GetRooKeysPdfFromWorkspace(workspace_mistag,TString("PhysBkgBsDsPiPdf_m_down_kkpi_mistag"))
        timemistag_signal = RooProdPdf("timeandmass_signal","timeandmass_signal",RooArgSet(mistag_signal),
                                                                                  RooFit.Conditional(RooArgSet(sigTimePDF),
                                                                                                     RooArgSet(time,bTagMap,fChargeMap)))
        '''
        totPDF = sigTimePDF               
        fitter = FitMeTool(debug)
    
        fitter.setObservables(observables)
        fitter.setModelPDF(totPDF)
        fitter.setData(data)
      
        s1=TString("comb")
        mode = TString("time_BsDsK")
        GeneralUtils.SaveDataSet(data, time, s1, mode);
       
        plot_init   = (wsname != None) and initvars
        plot_fitted = (wsname != None) and (not initvars)
    
        if plot_init :
            fitter.saveModelPDF(wsname)
            fitter.saveData(wsname)
       
        if toys or not Blinding: #Unblind yourself
            fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2), RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult = fitter.getFitResult()
            myfitresult.Print("v")
        else :    #Don't
            fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            myfitresult = fitter.getFitResult()
            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 
            par[1].Print("v")
            par[2].Print("v")
            par[3].Print("v")
            par[4].Print("v")        

        workout = RooWorkspace("workspace","workspace")
        getattr(workout,'import')(data)
        getattr(workout,'import')(totPDF)
        getattr(workout,'import')(myfitresult)
        workout.writeToFile("WS_Time_DsK.root")
                               
        if not toys and plot_fitted :
            fitter.saveModelPDF(wsname)
            fitter.saveData(wsname)
         
        del fitter
    else : #if we are splitting by charge
        sigCosh_pos         = RooProduct('sigCosh_pos',      'cosh coefficient', RooArgSet(untaggedWeight, sigTagWeight) )
        sigSinh_pos         = RooProduct('sigSinh_pos',      'sinh coefficient', RooArgSet(sigCosh_pos, sigD)         )
        sigCos_pos          = RooProduct('sigCos_pos',       'cos coefficient',  RooArgSet(sigCosSin_i0, sigC)        )
        sigSin_pos          = RooProduct('sigSin_pos',       'sin coefficient',  RooArgSet(sigCosSin_i0, sigS)        )
    
        sigCosh_neg         = RooProduct('sigCosh_neg',      'cosh coefficient', RooArgSet(untaggedWeight, sigTagWeight) )
        sigSinh_neg         = RooProduct('sigSinh_neg',      'sinh coefficient', RooArgSet(sigCosh_neg, sigDbar)      )
        sigCos_neg          = RooProduct('sigCos_neg',       'cos coefficient',  RooArgSet(sigCosSin_i0, sigCbar)     )
        sigSin_neg          = RooProduct('sigSin_neg',       'sin coefficient',  RooArgSet(sigCosSin_i0, sigSbar)     )

        if debug :
            print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!'
            data_pos.Print("v")
            for i in range(0,nEntries_pos) :
                data_pos.get(i).Print("v")
                print data_pos.weight()
            data_neg.Print("v")
            for i in range(0,nEntries_neg) :
                data_neg.get(i).Print("v")
                print data_neg.weight()
    
        tauinv          = Inverse( "tauinv","tauinv", gammas)
        trm             = RooGaussModel('PTRMGaussian_signal','PTRMGaussian_signal',time, zero, timeerravg)
        
        time_noacc_pos  = RooBDecay('time_signal_noacc_pos','time_signal_noacc', time, tauinv, deltaGammas,
                                            sigCosh_pos, sigSinh_pos,sigCos_pos, sigSin_pos, deltaMs,trm, RooBDecay.SingleSided)
        sigTimePDF_pos  = RooEffProd('time_signal','time_signal',time_noacc_pos,tacc)
        totPDF_pos      = sigTimePDF_pos
        
        time_noacc_neg  = RooBDecay('time_signal_noacc_neg','time_signal_noacc', time, tauinv, deltaGammas,
                                            sigCosh_neg, sigSinh_neg,sigCos_neg, sigSin_neg, deltaMs,trm, RooBDecay.SingleSided)
        sigTimePDF_neg  = RooEffProd('time_signal','time_signal',time_noacc_neg,tacc)
        totPDF_neg      = sigTimePDF_neg

        if toys or not Blinding: #Unblind yourself
            myfitresult_pos = totPDF_pos.fitTo(data_pos, RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                                         RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult_pos.Print("v")
            myfitresult_neg = totPDF_neg.fitTo(data_neg, RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                                         RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult_neg.Print("v")
        else :    #Don't
            myfitresult_pos = totPDF.fitTo(data_pos,  RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                                      RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            myfitresult_neg = totPDF.fitTo(data_neg,  RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                                      RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            print 'Matrix quality pos is',myfitresult_pos.covQual()
            par_pos = myfitresult_pos.floatParsFinal()
            par_pos[0].Print("v")
            par_pos[1].Print("v")
            par_pos[2].Print("v")

            print 'Matrix quality neg is',myfitresult_neg.covQual()
            par_neg = myfitresult_neg.floatParsFinal()
            par_neg[0].Print("v")
            par_neg[1].Print("v")
            par_neg[2].Print("v")

        workout = RooWorkspace("workspace","workspace")
        getattr(workout,'import')(data)
        getattr(workout,'import')(totPDF)
        getattr(workout,'import')(myfitresult)
        workout.writeToFile("WS_Time_DsK.root")
                         
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser(_usage)

parser.add_option('-d', '--debug',
                  dest    = 'debug',
                  default = False,
                  action  = 'store_true',
                  help    = 'print debug information while processing'
                  )
parser.add_option('-s', '--save',
                  dest    = 'wsname',
                  metavar = 'WSNAME',
                  default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/DsK_Toys_Full_Work_TimeFitResult_2kSample_1.root',
                  help    = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                  )

parser.add_option('--pathData',
                  dest    = 'dataName',
                  default = '../data/config_Bs2Dsh2011TDAna_Bs2DsK.txt'
                  )
parser.add_option('-i', '--initial-vars',
                  dest    = 'initvars',
                  default = False,
                  action  = 'store_true',
                  help    = 'save the model PDF parameters before the fit (default: after the fit)'
                  )

parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_LifetimeFit_ctau',
                   help = 'set observable '
                   )

parser.add_option( '-c', '--cutvariable',
                   dest = 'ProbVar',
                   default = 'lab1_PIDK',
                   help = 'set observable for PID '
                   )

parser.add_option( '--pereventmistag',
                   dest = 'pereventmistag',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event mistag?'
                   ) 

parser.add_option( '-t','--toys',
                   dest = 'toys',
                   action = 'store_true', 
                   default = False,
                   help = 'are we working with toys?'
                   )   

parser.add_option( '--pathToys',
                   dest = 'pathToys',
                   default = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/DsK_Toys_Full_sWeights_ForTimeFit_2kSample_1.root',
                   help = 'name of the inputfile'
                   )   

parser.add_option( '--treeToys',
                   dest = 'treeToys',
                   default = 'merged',
                   help = 'name of the workspace'
                   )  

parser.add_option( '--splitCharge',
                   dest = 'splitCharge',
                   action = 'store_true',
                   default = False) 

parser.add_option( '--fitMeTool',
                    dest = 'fitMeTool',
                    action = 'store_true',
                    default = False)

parser.add_option( '--kfactcorr',
                    dest = 'nokfactcorr',
                    action = 'store_false',
                    default = True)

parser.add_option( '--smearAccept',
                   dest = 'smearaccept',
                   action = 'store_true',
                   default = False)  

parser.add_option( '--smearAcceptFile',
                   dest = 'accsmearfile',
                   default = 'acceptance-ratio-hists.root')

parser.add_option( '--smearAcceptHist',
                   dest = 'accsmearhist',
                   default = 'haccratio_cpowerlaw')

parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsKConfigForNominalGammaFitPlot')

# -----------------------------------------------------------------------------
if __name__ == '__main__' :
    (options, args) = parser.parse_args()

    if len(args) > 0 :
        parser.print_help()
        exit(-1)

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    print options
    print "=========================================================="    

    import sys 
    sys.path.append("../data/")

    totPDF = runBdGammaFitterOnData( options.debug,
                                     options.wsname,
                                     options.initvars,
                                     options.var,
                                     options.ProbVar,
                                     options.pereventmistag,
                                     options.toys,
                                     options.pathToys,
                                     options.treeToys,
                                     options.splitCharge,
                                     options.fitMeTool,
                                     options.configName,
                                     options.nokfactcorr,
                                     options.smearaccept,
                                     options.accsmearfile,
                                     options.accsmearhist,
                                     options.dataName)
# -----------------------------------------------------------------------------

