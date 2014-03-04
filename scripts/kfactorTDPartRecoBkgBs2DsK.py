#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# ---------------------------------------------------------------------------
# coding=utf-8
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
ulimit -v $((3072 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """
Calculate correction factors (k-factors) for partially reconstructed
background to Bs⁰ → DsK.

  - B(d,s) → Ds⁽*⁾K⁽*⁾
  - Bs → Ds⁽*⁾(π,ρ)

"""
# Python standard libraries
import os
import sys
sys.path.append("../data/")

# options
import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-o', '--outfile', dest='fname',
                    default=os.environ['B2DXFITTERSROOT']+'/data/workspace/kfactor_wspace.root',
                    help='Filename with saved workspace')
parser.add_argument('--mvar', dest='mvar',
                    default='lab0_MassFitConsD_M',
                    help = 'Set mass observable')
parser.add_argument('--masslo', dest='masslo',
                    type=float, default=5320.0,
                    help='Mass window lower edge')
parser.add_argument('--masshi', dest='masshi',
                    type=float, default=5420.0,
                    help='Mass window upper edge')
parser.add_argument('--nomasswin', dest='nomasswin',
                    action='store_false', default=False,
                    help='Turn off mass window')
parser.add_argument('--configname', dest = 'configname',
                    default='Bs2DsKConfigForNominalMassFitBDTGA',
                    help='Configuration file name')
parser.add_argument('-d', '--debug', dest='debug',
                    action='store_true', default=True)

options = parser.parse_args()


# ROOT globals
import B2DXFitters
import ROOT
from ROOT import gROOT
gROOT.SetBatch(True)

# ROOT classes
from ROOT import TTree, TFile, TClass

# RooFit classes
from ROOT import RooFit
from ROOT import RooPlot, RooWorkspace, RooFitResult
from ROOT import RooArgSet, RooArgList
from ROOT import RooAbsReal, RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooAbsPdf, RooGaussian
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf
from ROOT import RooDataSet, RooDataHist
from ROOT import RooDecay, RooGaussModel, TString, TLorentzVector



# avoid memory leaks - will have to explicitly relinquish and acquire ownership
# if required, but PyROOT does not do what it thinks best without our knowing
# what it does
ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
# enable ROOT to understand Reflex dictionaries
ROOT.gSystem.Load('libCintex')
ROOT.Cintex.Enable()
# running in standalone mode, we have to load things ourselves
ROOT.gSystem.Load(os.environ['B2DXFITTERSROOT'] +
        '/standalone/libB2DXFitters')

from ROOT import MDFitterSettings
getSpecBkg4kfactor = ROOT.MassFitUtils.getSpecBkg4kfactor

# Models = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

datasetlist = os.environ['B2DXFITTERSROOT']+'/data/config_Bs2Dsh2011TDAna_Bs2DsK.txt'

PIDcut = 10
PIDmisscut= 0
pPIDcut = 5
Pcut_down = 0.0
Pcut_up = 100000000000.0
BDTGCut = 0.50
Dmass_down = 1948
Dmass_up = 1990


def get_workspace(configname, varnames, masslo, masshi, debug):
    """Get a workspace with all the datasets for partially
    reconstructed background.

    """
    myconfigfilegrabber = __import__(configname,fromlist=['getconfig']).getconfig
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

    config = TString("../data/")+TString(configname)+TString(".py")
    MDSettingsMC = MDFitterSettings("MDSettingsMC","MDFSettingsMC",config)
    MDSettingsMC.SetMassBVar(TString(varnames['mvar']))
    MDSettingsMC.SetMassDVar(TString(varnames['mdvar']))
    MDSettingsMC.SetTimeVar(TString(varnames['tvar']))
    MDSettingsMC.SetTerrVar(TString(varnames['terrvar']))
    # MDSettingsMC.SetTagVar(TString("lab0_BsTaggingTool_TAGDECISION_OS"), 0)
    # MDSettingsMC.SetTagOmegaVar(TString("lab0_BsTaggingTool_TAGOMEGA_OS"), 0)
    MDSettingsMC.SetIDVar(TString(varnames['idvar']))
    MDSettingsMC.SetPIDKVar(TString(varnames['pidkvar']))
    MDSettingsMC.SetBDTGVar(TString(varnames['bdtgvar']))
    MDSettingsMC.SetMomVar(TString(varnames['pvar']))
    MDSettingsMC.SetTrMomVar(TString(varnames['ptvar']))
    MDSettingsMC.SetTracksVar(TString(varnames['ntracksvar']))
    MDSettingsMC.SetMassBRange(masslo, masshi)
    # MDSettingsMC.SetMassDRange()
    MDSettingsMC.Print("v")

    MDRatio= 1.0-myconfigfile["lumRatio"]
    MURatio= myconfigfile["lumRatio"]

    if configname.startswith('Bs2DsK'):
        hypo = TString("BsDsK")
        ffile = TFile('dsk_treedump_mass_bin_{}_{}.root'.format(masslo, masshi), 'recreate')
    elif configname.startswith('Bs2DsPi'):
        hypo = TString("BsDsPi")
        ffile = TFile('dspi_treedump_mass_bin_{}_{}.root'.format(masslo, masshi), 'recreate')
    else:
        print 'Unknown mass hypothesis; job will crash.'
        return None

    workspace = 0
    workspace = getSpecBkg4kfactor(TString(myconfigfile["dataName"]),
                                   TString('#Kfactor MC FileName MU'),
                                   TString('#Kfactor MC TreeName'),
                                   MDSettingsMC, hypo,
                                   workspace, MURatio, ffile, debug)
    workspace = getSpecBkg4kfactor(TString(myconfigfile["dataName"]),
                                   TString('#Kfactor MC FileName MD'),
                                   TString('#Kfactor MC TreeName'),
                                   MDSettingsMC, hypo,
                                   workspace, MDRatio, ffile, debug)
    ffile.Close()

    if debug:
        print 'Dataset read from ntuples.\n', '=' * 50
        workspace.Print()
        print '=' * 50

    kFactor = GeneralUtils.GetObservable(workspace,TString("kfactorVar"), debug)
    kFactor.setRange(0.80, 1.10)

    if DsK:
        names = ["Bd2DK","Bd2DPi","Lb2LcK","Lb2LcPi","Lb2Dsstp","Lb2Dsp","Bs2DsstPi","Bs2DsRho","Bs2DsPi"]
    else:
        names = ["Bs2DsstPi","Bs2DsK","Lb2LcPi","Bd2DPi"]

    hi, lo = [], []
    dataup, datadown = [], []
    for mode in names:
        dataName = "kfactor_dataset_"+mode+"_up"
        dataup.append(GeneralUtils.GetDataSet(workspace,TString(dataName), debug))
        dataup[i].Print("v")
        print dataup[i].sumEntries()
        dataName = "kfactor_dataset_" + mode + "_down"
        datadown.append(GeneralUtils.GetDataSet(workspace,TString(dataName), debug))
        datadown[-1].Print("v")
        print datadown[-1].sumEntries()
        hi.append(-2.0)
        lo.append(2.0)

    for i in range(len(names)):
        for j in range(dataup[i].numEntries()):
            obsKF = dataup[i].get(j)
            kF = obsKF.find("kfactorVar")
            kNum = kF.getVal()
            if kNum > hi[i]:
                hi[i] = kNum
            if kNum < lo[i]:
                lo[i] = kNum
        for j in range(datadown[i].numEntries()):
            obsKF = datadown[i].get(j)
            kF = obsKF.find("kfactorVar")
            kNum = kF.getVal()
            if kNum > hi[i]:
                hi[i] = kNum
            if kNum < lo[i]:
                lo[i] = kNum

    print hi
    print lo
    maxRange = []
    minRange = []
    for i in range(len(names)):
        q = hi[i] - lo[i]
        maxRange.append(hi[i]+0.05*q)
        minRange.append(lo[i]-0.05*q)
    print maxRange
    print minRange

    plotSet = PlotSettings("plotSet","plotSet")

    histDW = []
    histUP = []
    hist   = []
    pdfKF  = []
    lumRatio = RooRealVar("lumRatio","lumRatio",myconfigfile["lumRatio"])
    for i in range(len(names)):
        kFactor.setRange(minRange[i], maxRange[i])

        name = "kFactor_"+names[i]+"_both"
        pdfKF.append(GeneralUtils.CreateHistPDF(dataup[i], datadown[i], myconfigfile["lumRatio"],
                                                kFactor, TString(name), 100, debug))
        t = TString("both")
        GeneralUtils.SaveTemplate(NULL, pdfKF[i], kFactor, TString(names[i]), t, plotSet, debug );

    workOut = RooWorkspace("workspace","workspace")
    for i in range(len(names)):
        getattr(workOut,'import')(pdfKF[i])
    workOut.Print("v")
    return workOut


if __name__ == "__main__":

    fname = options.fname
    debug = options.debug
    mvar = options.mvar
    masslo = options.masslo
    masshi = options.masshi
    nomasswin = options.nomasswin
    configname = options.configname

    varnames = {}
    varnames['mvar'] = mvar
    varnames['mdvar'] = 'lab2_MM'
    varnames['tvar'] = 'lab0_LifetimeFit_ctau'
    varnames['terrvar'] = 'lab0_LifetimeFit_ctauErr'
    varnames['idvar'] = 'lab1_ID'
    varnames['pidkvar'] = 'lab1_PIDK'
    varnames['bdtgvar'] = 'BDTGResponse_1'
    varnames['pvar'] = 'lab1_P'
    varnames['ptvar'] = 'lab1_PT'
    varnames['ntracksvar'] = 'nTracks'

    if nomasswin:
        masslo, masshi = -1, -1

    workspace = get_workspace(configname, varnames, masslo, masshi, debug)
    workspace.writeToFile(fname)
