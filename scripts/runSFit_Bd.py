#!/usr/bin/env python
# ---------------------------------------------------------------------------
# @file runSFit_Bd.py
#
# @brief run time fit for CP observables (B->DX modes) using
#        the DecRateCoeff_Bd class. Can be used on MC,
#        real sWeighted data or toy samples.
#
# @author Vincenzo Battista
# @date 2016-07-29
# ---------------------------------------------------------------------------
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.
# make sure the environment is set up properly
""":"
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
#"
import B2DXFitters
import ROOT
from B2DXFitters import *
from ROOT import *

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc
import copy

from B2DXFitters import taggingutils, cpobservables
from B2DXFitters.timepdfutils_Bd import buildBDecayTimePdf
from B2DXFitters.resmodelutils import getResolutionModel
from B2DXFitters.acceptanceutils import buildSplineAcceptance
from B2DXFitters.WS import WS as WS

gROOT.SetBatch()

#------------------------------------------------------------------------------
def setConstantIfSoConfigured(var,myconfigfile) :
    if var.GetName() in myconfigfile["constParams"]:
        var.setConstant()
        print "[INFO] Parameter: %s set to be constant with value %lf" %(var.GetName(),var.getValV())
    else:
        print "[INFO] Parameter: %s floats in the fit" %(var.GetName())
        print "[INFO]   ",var.Print()

# ------------------------------------------------------------------------------
def getCPparameters(ws, myconfigfile, UniformBlinding):

    if "ModLf" in myconfigfile["ACP"]["Signal"].keys():

        print "[INFO] Building CP parameters using amplitude values"

        if "ArgLf" and "ArgLbarfbar" in myconfigfile["ACP"]["Signal"].keys():

            ACPobs = cpobservables.AsymmetryObservables(myconfigfile["ACP"]["Signal"]["ArgLf"][0],
                                                        myconfigfile["ACP"]["Signal"]["ArgLbarfbar"][0],
                                                        myconfigfile["ACP"]["Signal"]["ModLf"][0])

        elif "StrongPhase" and "WeakPhase" in myconfigfile["ACP"]["Signal"].keys():

            ArgLf = myconfigfile["ACP"]["Signal"]["StrongPhase"][0]-myconfigfile["ACP"]["Signal"]["WeakPhase"][0]
            ArgLbarfbar = myconfigfile["ACP"]["Signal"]["StrongPhase"][0]+myconfigfile["ACP"]["Signal"]["WeakPhase"][0]
            ACPobs = cpobservables.AsymmetryObservables(ArgLf,
                                                        ArgLbarfbar,
                                                        myconfigfile["ACP"]["Signal"]["ModLf"][0])

        ACPobs.printtable()
        Cf = ACPobs.Cf()
        Sf = ACPobs.Sf()
        Df = ACPobs.Df()
        Sfbar = ACPobs.Sfbar()
        Dfbar = ACPobs.Dfbar()

    elif "C" and "S" and "D" and "Sbar" and "Dbar" in myconfigfile["ACP"]["Signal"].keys():

        print "[INFO] Building CP parameters directly from their values"

        Cf = myconfigfile["ACP"]["Signal"]["C"][0]
        Sf = myconfigfile["ACP"]["Signal"]["S"][0]
        Df = myconfigfile["ACP"]["Signal"]["D"][0]
        Sfbar = myconfigfile["ACP"]["Signal"]["Sbar"][0]
        Dfbar = myconfigfile["ACP"]["Signal"]["Dbar"][0]

    limit = [-3.0, 3.0]
    if myconfigfile["ACP"]["Signal"].has_key("CPlimit"):
        limit[0] = myconfigfile["ACP"]["Signal"]["CPlimit"]["lower"]
        limit[1] = myconfigfile["ACP"]["Signal"]["CPlimit"]["upper"]

    sigC = RooRealVar('Cf', 'C_{f}', Cf, limit[0], limit[1])
    sigS = RooRealVar('Sf', 'S_{f}', Sf, limit[0], limit[1])
    sigS_blind = RooUnblindUniform('Sf_blind', 'S_{f} (blind)', 'CPV_3invfb_Bd2DPi_S', 1.0, sigS)
    sigD = RooRealVar('Df', 'D_{f}', Df, limit[0], limit[1])
    sigSbar = RooRealVar('Sfbar', 'S_{#bar f}', Sfbar, limit[0], limit[1])
    sigSbar_blind = RooUnblindUniform('Sfbar_blind', 'S_{#bar f} (blind)', 'CPV_3invfb_Bd2DPi_Sbar', 1.0, sigSbar)
    sigDbar = RooRealVar('Dfbar', 'D_{#bar f}', Dfbar, limit[0], limit[1])
    setConstantIfSoConfigured(sigC, myconfigfile)
    setConstantIfSoConfigured(sigS, myconfigfile)
    setConstantIfSoConfigured(sigD, myconfigfile)
    setConstantIfSoConfigured(sigSbar, myconfigfile)
    setConstantIfSoConfigured(sigDbar, myconfigfile)
    sigC = WS(ws, sigC)
    sigD = WS(ws, sigD)
    sigDbar = WS(ws, sigDbar)

    if not UniformBlinding:
        sigS = WS(ws, sigS)
        sigSbar = WS(ws, sigSbar)
        return sigC, sigS, sigD, sigSbar, sigDbar
    else:
        sigS_blind = WS(ws, sigS_blind)
        sigSbar_blind = WS(ws, sigSbar_blind)
        return sigC, sigS_blind, sigD, sigSbar_blind, sigDbar

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def runSFit(debug, wsname,
            pereventmistag, tagfromdata, noftcalib, pereventterr,
            toys, pathName, fileNamePull, treeName, outputdir,
            MC, workMC,
            configName, scan,
            binned, plotsWeights, noweight,
            sample, mode, year, hypo, merge, unblind, randomise, superimpose,
            seed, preselection, UniformBlinding, extended, fitresultFileName):

    if MC and not noweight:
        print "ERROR: cannot use sWeighted MC sample (for now)"
        exit(-1)

    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    #Modify config dict such that buildBDecayTimePdf can understand it
    myconfigfile["Context"] = "FIT"
    myconfigfile["Debug"] = True if debug else False
    myconfigfile["UseProtoData"] = True
    myconfigfile["ParameteriseIntegral"] = myconfigfile["ACP"]["Signal"]["ParameteriseIntegral"]
    myconfigfile["NBinsAcceptance"] = myconfigfile["ACP"]["Signal"]["NBinsAcceptance"]
    if "NBinsProperTimeErr" in myconfigfile["ACP"]["Signal"].keys():
        myconfigfile["NBinsProperTimeErr"] = myconfigfile["ACP"]["Signal"]["NBinsProperTimeErr"]

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="

    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation','Wynn-Epsilon')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('maxSteps','1000')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('minSteps','0')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)

    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings",False)
    MDSettings = mdt.getConfig()
    MDSettings.Print("v")

    ws = RooWorkspace("intWork","intWork")
    decay = TString(myconfigfile["Decay"])

    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)

    if not MC:

        print ""
        print "=========================================================="
        print "Get input workspace with data"
        print "=========================================================="
        print ""

        workspace = []
        workspaceW = []

        workspace.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings,
                                                        TString(sample), TString(mode), TString(year), TString(hypo), merge,
                                                        False, toys, False, False, debug))
        workspaceW.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings,
                                                         TString(sample), TString(mode), TString(year), TString(hypo), merge,
                                                         True, toys, False, True, debug))

        print ""
        print "=========================================================="
        print "Create dataset and observables"
        print "=========================================================="
        print ""

        nameData = TString("dataSet_time")
        nameDataWA = TString("dataSet_time_weighted")

        if preselection != "":
            data_temp = GeneralUtils.GetDataSet(workspace[0], nameData, debug)
            dataWA_temp = GeneralUtils.GetDataSet(workspaceW[0], nameDataWA, debug)

            data_temp.SetName(nameDataWA.Data() + "_temp")
            dataWA_temp.SetName(nameData.Data())
            data_temp.SetName(nameDataWA.Data())

            print "Applying following preselection to reduce dataset:"
            print preselection

            # The unweighted set can be weighted after the cut because sWeights appears in the obs list. The weighted
            # set is unweighted after the cut instead. That's why dataWA is obtained from data and vice-versa (and that's
            # why the names given above are swapped ;-)
            dataWA = WS(ws, RooDataSet(data_temp.GetName(), dataWA_temp.GetTitle(), data_temp, data_temp.get(), preselection, "sWeights"))
            data = WS(ws, RooDataSet(dataWA_temp.GetName(), data_temp.GetTitle(), dataWA_temp, dataWA_temp.get(), preselection))

            print "Entries (unweighted set):"
            print "...before cut: " + str(data_temp.numEntries()) + ", sum of weights " + str(data_temp.sumEntries())
            print "...after cut: " + str(data.numEntries()) + ", sum of weights " + str(data.sumEntries())
            print "Entries (weighted set):"
            print "...before cut: " + str(dataWA_temp.numEntries()) + ", sum of weights " + str(dataWA_temp.sumEntries())
            print "...after cut: " + str(dataWA.numEntries()) + ", sum of weights " + str(dataWA.sumEntries())
        else:
            print "No additional preselection"
            data = WS(ws, GeneralUtils.GetDataSet(workspace[0], nameData, debug))
            dataWA = WS(ws, GeneralUtils.GetDataSet(workspaceW[0], nameDataWA, debug))

        data.Print("v")
        dataWA.Print("v")
        data.Print()
        dataWA.Print()

    else:

        print ""
        print "========================================="
        print "Get input workspace "+str(workMC)+" from:"
        print str(pathName)
        print "========================================="
        print ""
        workspaceMC = GeneralUtils.LoadWorkspace(TString(pathName), TString(workMC), debug)

        print ""
        print "========================================="
        print "Get dataset from:"
        print str(workMC)
        print "========================================="
        print ""

        modeTS = TString(mode)
        sampleTS = TString(sample)
        yearTS = TString(year)
        hypoTS = TString(hypo)

        datasetTS = TString("dataSetMC_")+decay+TString("_")
        print "Dataset name prefix:"
        print datasetTS.Data()

        if merge == "pol" or merge == "both":
            sampleTS = TString("both")
        if merge == "year" or merge == "both":
            yearTS = TString("run1")

        sam = WS(ws, RooCategory("sample","sample"))

        from B2DXFitters.mdfitutils import getObservables  as getObservables
        observables = getObservables(MDSettings, workspaceMC, False, debug)
        data_temp = GeneralUtils.GetDataSet(workspaceMC, observables, sam, datasetTS, sampleTS, modeTS, yearTS, hypoTS, merge, debug )
        if preselection != "":
            print "Applying following preselection to reduce dataset:"
            print preselection
            data = RooDataSet(data_temp.GetName(), data_temp.GetTitle(), data_temp, data_temp.get(), preselection)
            print "Entries:"
            print "...before cut: " + str(data_temp.sumEntries())
            print "...after cut: " + str(data.sumEntries())
        else:
            print "No additional preselection"
            data = data_temp

        data = WS(ws, data)
        dataWA = data
        print "Dataset entries:"
        print data.sumEntries()

    obs = dataWA.get()
    time = WS(ws, obs.find(MDSettings.GetTimeVarOutName().Data()))
    if pereventterr:
        terr = WS(ws, obs.find(MDSettings.GetTerrVarOutName().Data()))
    else:
        terr = None
    id = WS(ws, obs.find(MDSettings.GetIDVarOutName().Data()))
    observables = RooArgSet(time,id)

    #canvw = TCanvas("canvw")
    #framew = time.frame()
    #dataWA.plotOn(framew)
    #framew.Draw()
    #canvw.SaveAs("TESTWDATASET.pdf")

    #canv = TCanvas("canv")
    #frame = time.frame()
    #data.plotOn(frame)
    #frame.Draw()
    #canv.SaveAs("TESTDATASET.pdf")

    #testfile = TFile("TESTFILE.root","RECREATE")
    #testtree = data.tree()
    #testtree.Write()
    #testfile.ls()
    #testfile.Close()

    #exit(0)

    tag = []
    mistag = []
    for t in range(0,MDSettings.GetNumTagVar()):
        tag.append( WS(ws, obs.find(MDSettings.GetTagVarOutName(t).Data())) )
        mistag.append( WS(ws, obs.find(MDSettings.GetTagOmegaVarOutName(t).Data())) )
        #mistag[t].setRange(0.0,0.5)

    if plotsWeights:
        name = TString("sfit")
        obs2 = data.get()
        weight2 = obs2.find("sWeights")
        swpdf = GeneralUtils.CreateHistPDF(data, weight2, name, 100, debug)
        GeneralUtils.SaveTemplate(data, swpdf, weight2, outputdir+name)
        exit(0)

    print ""
    print "=========================================================="
    print "Define some physical parameters"
    print "=========================================================="
    print ""

    gamma = WS(ws, RooRealVar('Gamma', '#Gamma', *(myconfigfile["ACP"]["Signal"]["Gamma"] + ['ps^{-1}']) ))
    #setConstantIfSoConfigured(ws.obj(gamma.GetName()),myconfigfile)
    deltaGamma = WS(ws, RooRealVar('deltaGamma', '#Delta#Gamma', *(myconfigfile["ACP"]["Signal"]["DeltaGamma"] + ['ps^{-1}'])))
    #setConstantIfSoConfigured(ws.obj(deltaGamma.GetName()),myconfigfile)
    deltaM = WS(ws, RooRealVar('deltaM', '#Delta m', *(myconfigfile["ACP"]["Signal"]["DeltaM"] + ['ps^{-1}']) ))
    #setConstantIfSoConfigured(ws.obj(deltaM.GetName()),myconfigfile)

    print ""
    print "=========================================================="
    print "Build decay time resolution/error and acceptance"
    print "=========================================================="
    print ""

    if myconfigfile["ResolutionAcceptance"]["Signal"]["Acceptance"] != None:
        myconfigfile["AcceptanceFunction"] = myconfigfile["ResolutionAcceptance"]["Signal"]["Acceptance"]["Type"]
        acc, accnorm = buildSplineAcceptance(ws, time, 'Acceptance',
                                             myconfigfile["ResolutionAcceptance"]["Signal"]["Acceptance"]["KnotPositions"],
                                             myconfigfile["ResolutionAcceptance"]["Signal"]["Acceptance"]["KnotCoefficients"],
                                             False if myconfigfile["ResolutionAcceptance"]["Signal"]["Acceptance"]["Float"] == False else True,
                                             debug)
        if debug:
            print "Acceptance function:"
            acc.Print("v")

    else:
        print "[INFO] Using flat acceptance (no acceptance)"
        myconfigfile["AcceptanceFunction"] = None
        acc = None
        accnorm = None

    if myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"] == None:
        if debug:
            print "No time resolution (i.e. perfect resolution) applied"
            print ""
            print "WARNING: the usage of RooTruthModel is highly discouraged! Use at your own risk!"
            print "If you want to emulate a perfect resolution, a very narrow gaussian is recommended instead."
            print ""
        resmodel = None
    elif "Type" in myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"].keys():
        if myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["Type"] == "AverageModel":
            print "[INFO] Using mean resolution"
            terrpdf = None
            myconfigfile["DecayTimeResolutionModel"] = myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["Parameters"]
            myconfigfile["DecayTimeResolutionBias"] = myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["Bias"][0]
            myconfigfile["DecayTimeResolutionScaleFactor"] = myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["ScaleFactor"][0]
        elif myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["Type"] == "GaussianWithPEDTE":
            print "[INFO] Using per-event time resolution"
            myconfigfile["DecayTimeResolutionModel"] = "GaussianWithPEDTE"
            myconfigfile["DecayTimeResolutionBias"] = myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["Bias"][0]
            myconfigfile["DecayTimeResolutionScaleFactor"] = myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["ScaleFactor"][0]
            myconfigfile["DecayTimeResolutionAvg"] = myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["Average"][0]
            observables.add( terr )
            if myconfigfile["ResolutionAcceptance"]["Signal"]["TimeErrorPDF"]["Type"] == "FromWorkspace":
                print "[INFO] Taking time error PDF from workspace"
                terrWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["ResolutionAcceptance"]["Signal"]["TimeErrorPDF"]["File"]),
                                                      TString(myconfigfile["ResolutionAcceptance"]["Signal"]["TimeErrorPDF"]["Workspace"]), debug)
                terrpdf = WS(ws, GeneralUtils.CreateHistPDF(dataWA, terr, TString(myconfigfile["ResolutionAcceptance"]["Signal"]["TimeErrorPDF"]["Name"]), 20, debug))
                if debug:
                    print "Time-error PDF:"
                    terrpdf.Print("v")
            elif myconfigfile["ResolutionAcceptance"]["Signal"]["TimeErrorPDF"]["Type"] == "Mock":
                print "[INFO] Building mock time error PDF"
                avg = WS(ws, RooRealVar("TimeErrAvg",
                                        "TimeErrAvg",
                                        -1.0 * (myconfigfile["ResolutionAcceptance"]["Signal"]["TimeErrorPDF"]["ResolutionAverage"][0]) / 7.0))
                exp = WS(ws, RooExponential("TimeErrExp",
                                            "TimeErrExp",
                                            terr, avg))
                poly = WS(ws, RooPolynomial("TimeErrPoly",
                                            "TimeErrPoly",
                                            terr, RooArgList(zero, zero, zero, zero, zero, zero, one), 0))
                terrpdf = WS(ws, RooProdPdf("TimeErrorPDF"
                                            "TimeErrorPDF",
                                            exp, poly))
                if debug:
                    print "Time-error PDF:"
                    terrpdf.Print("v")
            else:
                print "ERROR: time error pdf type "+myconfigfile["ResolutionAcceptance"]["Signal"]["TimeErrorPDF"]["Type"]+" not supported."
                exit(-1)
        else:
            print "ERROR: resolution type "+myconfigfile["ResolutionAcceptance"]["Signal"]["Resolution"]["Type"]+" not supported."
            exit(-1)

    resmodel, acc = getResolutionModel(ws, myconfigfile, time, terr, acc)
    if debug:
        print "Resolution model:"
        resmodel.Print("v")

    print ""
    print "=========================================================="
    print "Build tagging"
    print "=========================================================="
    print ""

    mistagcalib = []
    mistagpdfparams = {}
    mistagpdf = []

    # Build mistag pdfs on the fly if required (at least one tagger wants it)
    if pereventmistag:
        for t in range(0, MDSettings.GetNumTagVar()):
            nametag = "OS"
            if "SS" in MDSettings.GetTagVarOutName(t).Data():
                nametag = "SS"
            if "Type" in myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"].keys():
                if myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["Type"] == "BuildTemplate":
                    print "[INFO] Building mistag templates directly from data"
                    mistagpdflist = WS(ws, SFitUtils.CreateDifferentMistagTemplates(dataWA, MDSettings, 50, True, debug) )
                    break
    else:
        mistagpdf = None

    #Build all tagging stuff
    for t in range(0,MDSettings.GetNumTagVar()):
        nametag = "OS"
        if "SS" in MDSettings.GetTagVarOutName(t).Data():
            nametag = "SS"
        print "[INFO] Creating calibration parameters for "+nametag+" tagger"

        etamean = copy.deepcopy(myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["avgeta"])
        tageff = copy.deepcopy(myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["tageff"])

        if tagfromdata:
            print "[INFO] Computing <eta> and tagging efficiency directly from dataset. Overwriting values in configfile"
            if noweight:
                etamean[0] = data.mean(obs.find(MDSettings.GetTagOmegaVarOutName(t).Data()), MDSettings.GetTagVarOutName(t).Data()+"!=0")
                etasigma = data.sigma(obs.find(MDSettings.GetTagOmegaVarOutName(t).Data()), MDSettings.GetTagVarOutName(t).Data()+"!=0")
                numdata = RooDataSet("numdata"+str(t), "numdata", data, data.get(), MDSettings.GetTagVarOutName(t).Data()+"!=0")
                num = float( numdata.numEntries() )
                den = float( data.numEntries() )
                import uncertainties, math
                from uncertainties import ufloat
                tagefferr = ufloat(num, math.sqrt(num)) / ufloat(den, math.sqrt(den))
                tagefferr = tagefferr.std_dev
            else:
                etamean[0] = dataWA.mean(obs.find(MDSettings.GetTagOmegaVarOutName(t).Data()), MDSettings.GetTagVarOutName(t).Data()+"!=0")
                etasigma = dataWA.sigma(obs.find(MDSettings.GetTagOmegaVarOutName(t).Data()), MDSettings.GetTagVarOutName(t).Data()+"!=0")
                numdata = RooDataSet("numdata"+str(t), "numdata", data, data.get(), MDSettings.GetTagVarOutName(t).Data()+"!=0", "sWeights")
                num = numdata.sumEntries()
                den = dataWA.sumEntries()
                import uncertainties, math
                from uncertainties import ufloat
                tagefferr = ufloat(num, math.sqrt(num)) / ufloat(den, math.sqrt(den))
                tagefferr = tagefferr.std_dev
            del numdata
            tageff[0] = float( num / den )
            print "[INFO] New <eta>: "+str( etamean[0] )+" +- "+str( etasigma )
            print "[INFO] Config file <eta>: "+str( myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["avgeta"][0] )
            print "[INFO] New tagging efficiency: "+str( tageff[0] )+" +- "+str( tagefferr )
            print "[INFO] Config file tagging efficiency: "+str( myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["tageff"][0] )

        p0 = copy.deepcopy(myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["p0"])
        p1 = copy.deepcopy(myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["p1"])
        deltap0 = copy.deepcopy(myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["deltap0"])
        deltap1 = copy.deepcopy(myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["deltap1"])

        if noftcalib:
            print "[INFO] Using uncalibrated tagger: p0=<eta>, p1=1, deltap0=deltap1=0"
            p0[0] = etamean[0]
            p1[0] = 1.0
            deltap0[0] = 0.0
            deltap1[0] = 0.0

        thiscalib = []
        thiscalib.append( WS(ws, RooRealVar('p0_'+nametag,
                                            'p_{0}'+nametag,
                                            *p0)) )
        thiscalib.append( WS(ws, RooRealVar('p1_'+nametag,
                                            'p_{1}'+nametag,
                                            *p1)) )
        thiscalib.append( WS(ws, RooRealVar('deltap0_'+nametag,
                                            '#Delta p_{0}'+nametag,
                                            *deltap0)) )
        thiscalib.append( WS(ws, RooRealVar('deltap1_'+nametag,
                                            '#Delta p_{1}'+nametag,
                                            *deltap1)) )
        thiscalib.append( WS(ws, RooRealVar('avgeta_'+nametag,
                                            '<#eta>'+nametag,
                                            *etamean )) )
        thiscalib.append( WS(ws, RooRealVar('tageff_'+nametag,
                                            '#varepsilon_{tag}'+nametag,
                                            *tageff)) )
        thiscalib.append( WS(ws, RooRealVar('tagasymm_'+nametag,
                                            'a_{tag}'+nametag,
                                            *myconfigfile["Taggers"]["Signal"][nametag]["Calibration"]["tagasymm"])) )

        #for par in thiscalib:
        #    setConstantIfSoConfigured(ws.obj(par.GetName()),myconfigfile)

        mistagcalib.append( thiscalib )

        if pereventmistag:

            print "[INFO] Using per-event mistag for "+nametag+" tagger"

            observables.add( tag[t] )
            observables.add( mistag[t] )

            if "Type" in myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"].keys():
                if myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["Type"] == "Mock":
                    print "[INFO] Building mock mistag PDF for "+nametag+" tagger"
                    mistagpdfparams[nametag] = {}
                    mistagpdfparams[nametag]["eta0"] = WS(ws, RooRealVar("eta0_"+nametag,
                                                                         "eta0_"+nametag,
                                                                         *myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["eta0"]))
                    mistagpdfparams[nametag]["etaavg"] = WS(ws, RooRealVar("etaavg_"+nametag,
                                                                           "etaavg_"+nametag,
                                                                           *myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["etaavg"]))
                    mistagpdfparams[nametag]["f"] = WS(ws, RooRealVar("f_"+nametag,
                                                                  "f_"+nametag,
                                                                      *myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["f"]))
                    mistagpdf.append( WS(ws, MistagDistribution("MistagPDF_"+nametag,
                                                                "MistagPDF_"+nametag,
                                                                mistag[t],
                                                                mistagpdfparams[nametag]["eta0"],
                                                                mistagpdfparams[nametag]["etaavg"],
                                                                mistagpdfparams[nametag]["f"])))

                elif myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["Type"] == "Gaussian":
                    print "[INFO] Building gaussian mistag PDF for "+nametag+" tagger"
                    mistagpdfparams[nametag] = {}
                    mistagpdfparams[nametag]["mean"] = WS(ws, RooRealVar("mean_"+nametag,
                                                                         "mean_"+nametag,
                                                                         myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["mean"]))
                    mistagpdfparams[nametag]["sigma"] = WS(ws, RooRealVar("sigma_"+nametag,
                                                                          "sigma_"+nametag,
                                                                          myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["sigma"]))
                    mistagpdf.append( WS(ws, RooGaussian("MistagPDF_"+nametag,
                                                         "MistagPDF_"+nametag,
                                                         mistag[t],
                                                         mistagpdfparams[nametag]["mean"],
                                                         mistagpdfparams[nametag]["sigma"])))

                elif myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["Type"] == "FromWorkspace":
                    print "[INFO] Taking mistag PDF for "+nametag+" tagger from workspace"
                    mistagWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["File"]),
                                                            TString(myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["Workspace"]), debug)
                    mistagpdf.append( WS(ws, Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(mistagWork,
                                                                                              TString(myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["Name"]), debug) ) )

                elif myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["Type"] == "BuildTemplate":
                    print "[INFO] Build mistag template on the fly as histogram PDF"
                    mistagpdf.append( mistagpdflist[t] )


                else:
                    print "ERROR: mistag pdf type "+myconfigfile["Taggers"]["Signal"][nametag]["MistagPDF"]["Type"]+" not supported."
                    exit(-1)

            else:
                print "ERROR: error in mistag PDF building. Please check your config file."
                exit(-1)

        else:
            mistagpdf = None

    print ""
    print "=========================================================="
    print "Build CP parameters"
    print "=========================================================="
    print ""

    C, S, D, Sbar, Dbar = getCPparameters(ws, myconfigfile, UniformBlinding)

    print ""
    print "=========================================================="
    print "Build production/detection asymmetries"
    print "=========================================================="
    print ""

    aProd = zero
    aDet = zero

    if myconfigfile.has_key("ProductionAsymmetry"):
        aProd = WS(ws, RooRealVar('ProdAsymm','a_{prod}',*myconfigfile["ProductionAsymmetry"]["Signal"]))
    if myconfigfile.has_key("DetectionAsymmetry") :
        aDet = WS(ws, RooRealVar('DetAsymm','a_{det}', *myconfigfile["DetectionAsymmetry"]["Signal"]))

    genValDict = {}

    if "gaussCons" in myconfigfile.keys():

        print ""
        print "=========================================================="
        print "Build Gaussian constraints"
        print "=========================================================="
        print ""

        if toys:
            #Sample mean of gaussian constraint
            for parname in myconfigfile["gaussCons"].iterkeys():
                if type(myconfigfile["gaussCons"][parname]) != list:
                    #Build single gaussian for univariate constraints
                    par = ws.var(parname)
                    gaussGen = TRandom3(int(seed))
                    mean = par.getVal()
                    par.setVal( gaussGen.Gaus( mean, myconfigfile["gaussCons"][parname] ) )
                    if debug:
                        print "Sampling mean of "+parname+" constraint (from univariate gaussian)"
                        print "Config file value: "+str(mean)
                        print "New sampled value: "+str(par.getVal())
                        print "Seed: "+str(seed)
                    par = WS(ws, par)
                    genValDict[parname] = {}
                    genValDict[parname] = mean
                else:
                    #Build multivariate gaussian for multivariate constraints
                    from B2DXFitters.utils import BuildMultivarGaussFromCorrMat
                    mvg, params = BuildMultivarGaussFromCorrMat(ws,
                                                                parname+"_forResampling",
                                                                myconfigfile["gaussCons"][parname][0],
                                                                myconfigfile["gaussCons"][parname][1],
                                                                myconfigfile["gaussCons"][parname][2],
                                                                False)
                    #Generate new set of correlated parameters
                    gInterpreter.ProcessLine('gRandom->SetSeed('+str(int(seed))+')')
                    RooRandom.randomGenerator().SetSeed(int(seed))
                    randVals = mvg.generate(params,
                                            RooFit.NumEvents(1))
                    #Update values in the workspace
                    for parname in myconfigfile["gaussCons"][parname][0]:
                        par = ws.var(parname)
                        oldval = par.getVal()
                        par.setVal( randVals.get().find(parname).getVal() )
                        if debug:
                            print "Sampling mean of "+parname+" constraint (from multivariate gaussian)"
                            print "Config file value: "+str(oldval)
                            print "New sampled value: "+str(par.getVal())
                            print "Seed: "+str(seed)
                        par = WS(ws, par)
                        genValDict[parname] = {}
                        genValDict[parname] = oldval

        #Build actual constraints
        from B2DXFitters.GaussianConstraintBuilder import GaussianConstraintBuilder
        constraintbuilder = GaussianConstraintBuilder(ws, myconfigfile["gaussCons"])
        constList = constraintbuilder.getSetOfConstraints()
        constList.Print("v")

    print ""
    print "=========================================================="
    print "Build total time PDF"
    print "=========================================================="
    print ""

    totPDF_temp = buildBDecayTimePdf(
        myconfigfile, 'time_signal', ws,
        time, terr, tag, id, mistag, mistagcalib,
        gamma, deltaGamma, deltaM,
        C, D, Dbar, S, Sbar,
        resmodel, acc,
        terrpdf, mistagpdf,
        aProd, aDet)

    if extended:
        print "[INFO] Performing extended maximum likelihood fit"
        Nsgn = WS(ws, RooRealVar("Nsgn", "N_{sgn}", 500000, 0, 1e+09))
        totPDF = WS(ws, RooExtendPdf(totPDF_temp.GetName()+"_ext", totPDF_temp.GetTitle()+" extended", totPDF_temp, Nsgn))
    else:
        totPDF = totPDF_temp

    #Fix "internal" time pdf parameters (if required)
    from B2DXFitters.utils import setConstantIfSoConfigured as fixParams
    fixParams(myconfigfile, totPDF)

    if randomise:

        print ""
        print "=========================================================="
        print "Randomise initial parameters"
        print "=========================================================="
        print ""

        #Randomise initial guess of the parameters according to a uniform distributions
        from B2DXFitters.utils import randomiseParameters as ranPar
        ranPar(myconfigfile, totPDF, int(seed), debug, genValDict)

    if scan:

        print ""
        print "=========================================================="
        print "Perfom likelihood scan"
        print "=========================================================="
        print ""

        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(1002)

        nll = RooNLLVar("nll","-log(sig)", totPDF, dataWA, RooFit.NumCPU(4), RooFit.Silence(True))

        for par in myconfigfile["LikelihoodScan"]:

            if debug:
                print "[INFO] Producing profile likelihood plot for " + par

            param = ws.obj(par)
            pll  = RooProfileLL("pll_" + par, "pll_" + par, nll, RooArgSet(param))
            h = pll.createHistogram("h_" + par, param, RooFit.Binning(200))
            h.SetLineColor(kRed)
            h.SetLineWidth(2)
            h.SetTitle("Likelihood Function - " + par)
            like = TCanvas("like", "like", 1200, 800)
            like.cd()
            h.Draw()
            like.Update()
            n = TString(outputdir + "likelihood_" + par + "_scan.pdf")
            like.SaveAs(n.Data())

        exit(0)

    print ""
    print "=========================================================="
    print "Perfom maximum likelihood fit"
    print "=========================================================="
    print ""

    # lines for debugging
    # sigyeld = RooRealVar("sigyield", "sigyield", 500000, 1000, 10000000)
    # pdfextend = RooExtendPdf("pdfExtend", "pdfExtend", totPDF, sigyeld)

    if binned:
        print "[INFO] RooDataSet is binned"
        time.setBins(250)
        terr.setBins(20)
        dataWA_binned = RooDataHist("dataWA_binned", "dataWA_binned", observables, dataWA)
        data_binned = RooDataHist("data_binned", "data_binned", observables, data)

    if not superimpose:

        if toys or MC or unblind:  # Unblind yourself
            MinosArgset = RooArgSet(S, Sbar)
            fitOpts_temp = [RooFit.Save(1),
                            RooFit.NumCPU(1),
                            RooFit.Offset(True),
                            RooFit.Strategy(2),
                            RooFit.Minimizer("Minuit2", "migrad"),
                            RooFit.SumW2Error(False),
                            RooFit.Minos(MinosArgset),
                            # RooFit.Minos(False),#RooFit.Minos(True),
                            RooFit.Optimize(True),
                            RooFit.Hesse(True),
                            # RooFit.Extended(False),
                            RooFit.PrintLevel(1),
                            RooFit.Warnings(False),
                            RooFit.PrintEvalErrors(-1)]
            if "gaussCons" in myconfigfile.keys():
                fitOpts_temp.append(RooFit.ExternalConstraints(constList))
            fitOpts = RooLinkedList()
            for cmd in fitOpts_temp:
                fitOpts.Add(cmd)
            if binned:
                print "[INFO] Fitting binned dataset"
                if not noweight:
                    print "[INFO] Fitting weighted dataset"
                    myfitresult = totPDF.fitTo(dataWA_binned, fitOpts)
                else:
                    print "[INFO] Fitting unweighted dataset"
                    myfitresult = totPDF.fitTo(data_binned, fitOpts)
            else:
                print "[INFO] Fitting unbinned dataset"
                if not noweight:
                    print "[INFO] Fitting weighted dataset"
                    myfitresult = totPDF.fitTo(dataWA, fitOpts)
                else:
                    print "[INFO] Fitting unweighted dataset"
                    myfitresult = totPDF.fitTo(data, fitOpts)
            myfitresult.Print("v")
            myfitresult.correlationMatrix().Print()
            myfitresult.covarianceMatrix().Print()
        else:  # Don't
            fitOpts_temp = [RooFit.NumCPU(8),
                            RooFit.Offset(True),
                            RooFit.Extended(False),
                            RooFit.Minimizer("Minuit2", "migrad"),
                            RooFit.Optimize(True),
                            RooFit.Hesse(True),
                            #RooFit.Minos(True),
                            RooFit.Save(1),
                            RooFit.Strategy(2),
                            RooFit.SumW2Error(False),
                            #RooFit.Extended(False),
                            RooFit.PrintLevel(1),
                            RooFit.Warnings(False),
                            RooFit.PrintEvalErrors(-1)]
            # at this stage we have to take car that either mistag pdf's are set or the
            # mistag observables are give as conditional observables. The following
            # commented lines were a workaround for a specific scenario - however, this
            # should be attacked in a more clever way later
            # if mistagpdf == None:
            #     cond_argset = RooArgSet(mistag[0],mistag[1])
            #     fitOpts_temp += [RooFit.ConditionalObservables(cond_argset)]
            if "gaussCons" in myconfigfile.keys():
                fitOpts_temp.append( RooFit.ExternalConstraints(constList) )
            fitOpts = RooLinkedList()
            for cmd in fitOpts_temp:
                fitOpts.Add(cmd)
            if binned:
                print "[INFO] Fitting binned dataset"
                if not noweight:
                    print "[INFO] Fitting weighted dataset"
                    myfitresult = totPDF.fitTo(dataWA_binned, fitOpts)
                else:
                    print "[INFO] Fitting unweighted dataset"
                    myfitresult = totPDF.fitTo(data_binned, fitOpts)
            else:
                print "[INFO] Fitting unbinned dataset"
                if not noweight:
                    print "[INFO] Fitting weighted dataset"
                    myfitresult = totPDF.fitTo(dataWA, fitOpts)
                else:
                    print "[INFO] Fitting unweighted dataset"
                    myfitresult = totPDF.fitTo(data, fitOpts)

            print '[INFO Result] Matrix quality is', myfitresult.covQual()
            par = myfitresult.floatParsFinal()
            const = myfitresult.constPars()
            print "[INFO Result] Status: ", myfitresult.status()
            print "[INFO Result] -------------- Constant parameters ------------- "
            for i in range(0, const.getSize()):
                print "[INFO Result] parameter %s  set to be  %0.4lf" % (const[i].GetName(), const[i].getValV())

            print "[INFO Result] -------------- Floated parameters ------------- "

            for i in range(0, par.getSize()):
                name = par[i].GetName()
                bdone = False
                for bp in myconfigfile["blindParams"]:
                    if bp == name:
                        print "[INFO Result] parameter %s = (XXX +/- %0.4lf)" % (name, par[i].getError())
                        bdone = True
                        break
                if not bdone:
                    print "[INFO Result] parameter %s = (%0.4lf +/- %0.4lf)" % (name, par[i].getVal(), par[i].getError())

            print "[INFO Result] -------------- Correlation matrix --------------"
            cor = myfitresult.correlationMatrix()
            cor.Print("v")
            print "[INFO Result] -------------- Covariance matrix --------------"
            cov = myfitresult.covarianceMatrix()
            cov.Print("v")

            # Plot matrices
            from B2DXFitters.FitResultGrabberUtils import PlotResultMatrix
            PlotResultMatrix(myfitresult, "covariance", outputdir+"sFit_CovarianceMatrix.pdf")
            PlotResultMatrix(myfitresult, "correlation", outputdir+"sFit_CorrelationMatrix.pdf")

        if toys:

            if myfitresult.status() != 0:
                print "ERROR: fit quality is bad. Not saving pull tree."
            else:
                print ""
                print "=========================================================="
                print "Save tree with fit result for pull plots"
                print "=========================================================="
                print ""

                from B2DXFitters.FitResultGrabberUtils import CreatePullTree
                if genValDict == {}:
                    genValDict = None
                CreatePullTree(fileNamePull, myfitresult, genValDict)

    dataWA.Print("v")
    totPDF.Print("v")

    fitresultFile = TFile(fitresultFileName,"RECREATE")
    myfitresult.Write()
    fitresultFile.Close()

    print ""
    print "========================================="
    print "Pretty-printing fit results"
    print "========================================="
    print ""
    from B2DXFitters import FitResultGrabberUtils
    FitResultGrabberUtils.PrintLatexTable(myfitresult)

    workout = RooWorkspace("workspace", "workspace")
    getattr(workout, 'import')(data)
    getattr(workout, 'import')(dataWA)
    getattr(workout, 'import')(totPDF)
    if not superimpose:
        getattr(workout, 'import')(myfitresult)
    workout.writeToFile(wsname)


#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser(_usage)

parser.add_option('-d', '--debug',
                  dest    = 'debug',
                  default = False,
                  action  = 'store_true',
                  help    = 'print debug information while processing'
                  )
parser.add_option('--extended',
                  dest    = 'extended',
                  default = False,
                  action  = 'store_true',
                  help    = 'add extended term to likelihood'
                  )
parser.add_option('-s', '--save',
                  dest    = 'wsname',
                  metavar = 'WSNAME',
                  default = 'WS_Time_DsPi.root',
                  help    = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                  )
parser.add_option( '--pereventmistag',
                   dest = 'pereventmistag',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event mistag?'
                   )
parser.add_option( '--tagfromdata',
                   dest = 'tagfromdata',
                   default = False,
                   action = 'store_true',
                   help = 'Compute <eta> and tagging efficiency on the fly from dataset'
                   )
parser.add_option( '--noftcalib',
                   dest = 'noftcalib',
                   default = False,
                   action = 'store_true',
                   help = 'Use uncalibrated taggers'
                   )
parser.add_option( '--pereventterr',
                   dest = 'pereventterr',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event time errors?'
                   )
parser.add_option( '-t','--toys',
                   dest = 'toys',
                   action = 'store_true',
                   default = False,
                   help = 'are we working with toys?'
                   )
parser.add_option( '--MC',
                   dest = 'MC',
                   action = 'store_true',
                   default = False,
                   help = 'are we working with MC?'
                   )
parser.add_option( '--workMC',
                   dest = 'workMC',
                   default = 'workspace',
                   help = 'name of the workspace containing MC sample'
                   )
parser.add_option( '--fileName',
                   dest = 'fileName',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsPi_all_both.root',
                   help = 'name of the inputfile'
                   )
parser.add_option( '--fileNamePull',
                   dest = 'fileNamePull',
                   default = 'PullTree.root',
                   help = 'name of the file to store fit result for pull plots'
                   )
parser.add_option( '--fileNameFitresult',
                   dest = 'fileNameFitresult',
                   default='FitResult.root',
                   help = 'name of the file to store fit result'
                   )
parser.add_option( '--treeName',
                   dest = 'treeName',
                   default = 'merged',
                   help = 'name of the workspace'
                   )
parser.add_option( '--scan',
                   dest = 'scan',
                   default = False,
                   action = 'store_true'
                   )
parser.add_option( '--cat',
                   dest = 'cat',
                   default = False,
                   action = 'store_true'
                   )
parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsPiConfigForNominalDMSFit')
parser.add_option( '--plotsWeights',
                   dest = 'plotsWeights',
                   default = False,
                   action = 'store_true'
                   )
parser.add_option( '--noweight',
                   dest = 'noweight',
                   default = False,
                   action = 'store_true'
                   )
parser.add_option( '-p', '--pol','--polarity',
                   dest = 'pol',
                   metavar = 'POL',
                   default = 'down',
                   help = 'Sample: choose up or down '
                   )
parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'kkpi',
                   help = 'Mode: choose all, kkpi, kpipi, pipipi, nonres, kstk, phipi, 3modeskkpi'
                   )
parser.add_option( '--merge',
                   dest = 'merge',
                   default = "",
                   help = 'for merging magnet polarities use: --merge pol, for merging years of data taking use: --merge year, for merging both use: --merge both'
                   )
parser.add_option( '--binned',
                   dest = 'binned',
                   default = False,
                   action = 'store_true',
                   help = 'binned data Set'
                   )
parser.add_option( '--unblind',
                   dest = 'unblind',
                   default = False,
                   action = 'store_true',
                   help = 'unblind results'
                   )
parser.add_option( '--randomise',
                   dest = 'randomise',
                   default = False,
                   action = 'store_true',
                   help = 'randomise initial values of floating parameters'
                   )
parser.add_option( '--superimpose',
                   dest = 'superimpose',
                   default = False,
                   action = 'store_true',
                   help = 'do not do fit (save not fitted pdf for plotting)'
                   )
parser.add_option( '--seed',
                   dest = 'seed',
                   default = 4534209875,
                   help = 'seed for initial parameter randomisation'
                   )
parser.add_option( '--year',
                   dest = 'year',
                   default = "",
                   help = 'year of data taking can be: 2011, 2012, run1')
parser.add_option( '--hypo',
                   dest = 'hypo',
                   default = "",
                   help = 'bachelor mass hypothesys (leave empty if not used)')
parser.add_option( '--outputdir',
                   dest = 'outputdir',
                   default = "",
                   help = 'output directory to store plots (if any)')
parser.add_option( '--preselection',
                   dest = 'preselection',
                   default = "",
                   help = 'additional preselection to apply on dataset'
                   )
parser.add_option( '--UniformBlinding',
                   dest = 'UniformBlinding',
                   default = False,
                   action='store_true',
                   help = 'the RooUnblindUniform is used for S and Sbar'
                   )

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

    config = options.configName
    last = config.rfind("/")
    directory = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]

    #configMD = options.configNameMD
    #last = configMD.rfind("/")
    #configNameMD = configMD[last+1:]
    #p = configNameMD.rfind(".")
    #configNameMD = configNameMD[:p]

    import sys
    sys.path.append(directory)


    runSFit( options.debug,
             options.wsname,
             options.pereventmistag,
             options.tagfromdata,
             options.noftcalib,
             options.pereventterr,
             options.toys,
             options.fileName,
             options.fileNamePull,
             options.treeName,
             options.outputdir,
             options.MC,
             options.workMC,
             configName,
             #configNameMD,
             options.scan,
             options.binned,
             options.plotsWeights,
             options.noweight,
             options.pol,
             options.mode,
             options.year,
             options.hypo,
             options.merge,
             options.unblind,
             options.randomise,
             options.superimpose,
             options.seed,
             options.preselection,
             options.UniformBlinding,
             options.extended,
             options.fileNameFitresult)

# -----------------------------------------------------------------------------
