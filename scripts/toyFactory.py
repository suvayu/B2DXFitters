#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78:expandtab
# ---------------------------------------------------------------------------
# @file toyFactory.py
#
# @brief toy generator for B2OC TD analyses
#
# @author Vincenzo Battista
# @date 2016-06-08
#
# Generate a toy sample using a pdf with an arbitrary number of observables
# (masses, time, mistag...). For the time part, all the possible effects
# are taken into account (asymmetry, resolution, flavour tagging...).
# The CP coefficients for the time pdf are built using the
# DecRateCoeff_Bd class from Dortmund.
#
# ---------------------------------------------------------------------------
# This file is used as both a shell script and as a Python script.
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

# set ulimit to protect against bugs which crash the machine: 3G vmem max,
# no more then 8M stack
ulimit -v $((3072 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O "$0" - "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
#"
import B2DXFitters
import ROOT
from ROOT import RooFit
from ROOT import *
from B2DXFitters import *
from B2DXFitters import WS
from B2DXFitters.WS import WS

from B2DXFitters import acceptanceutils
from B2DXFitters import resmodelutils
from B2DXFitters import timepdfutils_Bd
from B2DXFitters import cpobservables

from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc

import array
from array import array

import copy

gROOT.SetBatch()

#------------------------------------------------------------
def BuildObservables(workspaceIn, myconfigfile, debug):

    obsDict = {}
    for obs in myconfigfile["Observables"].iterkeys():
        print obs
        #Take "real" variables (masses, time...)
        if myconfigfile["Observables"][obs]["Type"] == "RooRealVar":
            if debug:
                print "Building "+obs+" of RooRealVar type"
            obsDict[obs] = {}
            obsDict[obs] = WS(workspaceIn, RooRealVar(obs,
                                                       myconfigfile["Observables"][obs]["Title"],
                                                       *myconfigfile["Observables"][obs]["Range"]))

        #Take "discrete" variables (tagging decision, final state charge...)
        elif myconfigfile["Observables"][obs]["Type"] == "RooCategory":
            if debug:
                print "Building "+obs+" of RooCategory type"
            cat = RooCategory(obs, myconfigfile["Observables"][obs]["Title"])
            for label in myconfigfile["Observables"][obs]["Categories"].iterkeys():
                index = myconfigfile["Observables"][obs]["Categories"][label]
                cat.defineType(label, index)
                if debug:
                    print "..."+label
            obsDict[obs] = {}
            obsDict[obs] = WS(workspaceIn, cat)
        elif myconfigfile["Observables"][obs]["Type"] == "FromWorkspace":
            if debug:
                print "Take "+obs+" from existing workspace"
            file = TFile.Open(myconfigfile["Observables"][obs]["File"],"READ")
            w = file.Get(myconfigfile["Observables"][obs]["Workspace"])
            newobs = w.obj(myconfigfile["Observables"][obs]["Name"])
            obsDict[obs] = WS(workspaceIn, newobs)
            file.Close()

    if debug:
        print "Observables dictionary:"
        print obsDict

    return obsDict

#------------------------------------------------------------
def BuildTagging(workspaceIn, myconfigfile, obsDict, debug):

    tagDict = {}
    #Loop over components
    for comp in myconfigfile["Components"].iterkeys():
        tagDict[comp] = {}
        tagDict[comp]["Calibration"] = []
        tagDict[comp]["MistagPDF"] = []
        #Loop over taggers (OS, SS)
        for tagger in myconfigfile["Taggers"][comp].iterkeys():

            if "Mistag"+tagger in obsDict.keys() and "TagDec"+tagger in obsDict.keys():

                #Create calibration parameters (p0, p1, dp0, dp1, <eta>, tageff, atageff)
                caliblist = []
                for p in ["p0", "p1", "deltap0", "deltap1", "avgeta", "tageff", "tagasymm"]:
                    if debug:
                        print "Create "+p+" parameter for "+tagger+" tagger, "+comp+" component"
                    caliblist.append( WS(workspaceIn, RooRealVar(p+"_"+tagger+"_"+comp,
                                                                  p+"_"+tagger+"_"+comp,
                                                                  *myconfigfile["Taggers"][comp][tagger]["Calibration"][p]) ) )
                tagDict[comp]["Calibration"].append( caliblist )

                #Create mistag pdf (can be "None" for average mistag)
                if debug:
                    print "Create mistag pdf for "+tagger+" tagger, "+comp+" component"
                if myconfigfile["Taggers"][comp][tagger]["MistagPDF"] == None:
                    if debug:
                        print "No mistag pdf (average mistag)"
                    tagDict[comp]["MistagPDF"] = None
                else:
                    tagDict[comp]["MistagPDF"].append( BuildMistagPDF(workspaceIn, myconfigfile, tagger, comp, obsDict, debug) )

    if debug:
        print "Tagging dictionary:"
        print tagDict

    return tagDict

#------------------------------------------------------------
def BuildMistagPDF(workspaceIn, myconfigfile, tagger, comp, obsDict, debug):

    if "Type" in myconfigfile["Taggers"][comp][tagger]["MistagPDF"].keys():
        if myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["Type"] == "FromWorkspace":
            if debug:
                print "Take mistag pdf "+myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["Name"]+" from workspace "+myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["Workspace"]+" in file "+myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["File"]
            file = TFile.Open(myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["File"],"READ")
            w = file.Get(myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["Workspace"])
            pdf = WS(workspaceIn, w.pdf(myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["Name"]))
            file.Close()
        elif myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["Type"] == "Mock":
            if debug:
                print "Build mock mistag pdf"
            pdf = WS(workspaceIn, BuildMockMistagPDF(workspaceIn, myconfigfile, tagger, comp, obsDict, debug))
        else:
            print "ERROR: mistag pdf type "+myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["Type"]+" not supported."
            exit(-1)
    else:
        print "ERROR: error in mistag PDF building. Please check your config file."
        exit(-1)

    if debug:
        print "Mistag pdf:"
        pdf.Print("v")

    return pdf

#------------------------------------------------------------
def BuildMockMistagPDF(workspaceIn, myconfigfile, tagger, comp, obsDict, debug):

    mistag = obsDict["Mistag"+tagger]

    eta0 = WS(workspaceIn, RooRealVar("eta0_"+tagger+"_"+comp,
                                       "eta0_"+tagger+"_"+comp,
                                       *myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["eta0"]))
    etaavg = WS(workspaceIn, RooRealVar("etaavg_"+tagger+"_"+comp,
                                         "etaavg_"+tagger+"_"+comp,
                                         *myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["etaavg"]))
    f = WS(workspaceIn, RooRealVar("f_"+tagger+"_"+comp,
                                    "f_"+tagger+"_"+comp,
                                    *myconfigfile["Taggers"][comp][tagger]["MistagPDF"]["f"]))

    pdf = WS(workspaceIn, MistagDistribution("MistagPDF_"+tagger+"_"+comp,
                                             "MistagPDF_"+tagger+"_"+comp,
                                             mistag, eta0, etaavg, f))

    # the following lines were only for debugging
    # pdf = WS(workspaceIn, RooGaussian("MistagPDF_"+tagger+"_"+comp,
    #                                   "MistagPDF_"+tagger+"_"+comp,
    #                                   mistag, etaavg, f))

    return pdf

#------------------------------------------------------------
def BuildResolutionAcceptance(workspaceIn, myconfigfile, obsDict, debug):

    resAccDict = {}
    #Loop over components
    for comp in myconfigfile["Components"].iterkeys():
        resAccDict[comp] = {}

        #Build time error pdf
        resAccDict[comp]["TimeErrorPDF"] = {}
        if debug:
            "Create time error pdf for "+comp
        resAccDict[comp]["TimeErrorPDF"] = BuildTimeErrorPDF(workspaceIn, myconfigfile, comp, obsDict, debug)

        #Build acceptance
        resAccDict[comp]["Acceptance"] = {}
        acc = None
        accnorm = None
        if myconfigfile["ResolutionAcceptance"][comp]["Acceptance"] == None:
            if debug:
                print "No time acceptance applied for "+comp
            pass
        elif "Type" in myconfigfile["ResolutionAcceptance"][comp]["Acceptance"].keys():
            if myconfigfile["ResolutionAcceptance"][comp]["Acceptance"]["Type"] == "Spline":
                if debug:
                    print "Build spline acceptance for "+comp
                time = obsDict["BeautyTime"]
                acc, accnorm = acceptanceutils.buildSplineAcceptance(workspaceIn, time, "Acceptance_"+comp,
                                                                     myconfigfile["ResolutionAcceptance"][comp]["Acceptance"]["KnotPositions"],
                                                                     myconfigfile["ResolutionAcceptance"][comp]["Acceptance"]["KnotCoefficients"],
                                                                     False, debug)
                #Use normalised acceptance for generation
                acc = accnorm
            else:
                print "ERROR: acceptance type "+myconfigfile["ResolutionAcceptance"][comp]["Acceptance"]["Type"]+" not supported."
                exit(-1)
        else:
            print "ERROR: error when building acceptance for "+comp+". Please check config file."
            exit(-1)

        #Build resolution
        resAccDict[comp]["Resolution"] = {}
        resmodel = None
        if myconfigfile["ResolutionAcceptance"][comp]["Resolution"] == None:
            if debug:
                print "No time resolution (i.e. perfect resolution) applied for "+comp
                print ""
                print "WARNING: the usage of RooTruthModel is highly discouraged! Use at your own risk!"
                print "If you want to emulate a perfect resolution, a very narrow gaussian is recommended instead."
                print ""
            pass
        elif "Type" in myconfigfile["ResolutionAcceptance"][comp]["Resolution"].keys():
            #Need to build a dictionary that "getResolutionModel" understands
            config = {}
            config["AcceptanceFunction"] = myconfigfile["ResolutionAcceptance"][comp]["Acceptance"]["Type"]
            if myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["Type"] == "GaussianWithPEDTE":
                if debug:
                    print "Build gaussian with per-event decay time resolution model for "+comp
                config["Context"] = "GEN"
                config["DecayTimeResolutionModel"] = "GaussianWithPEDTE"
                config["DecayTimeResolutionBias"] = myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["Bias"][0]
                config["DecayTimeResolutionScaleFactor"] = myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["ScaleFactor"][0]
                config["DecayTimeResolutionAvg"] = myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["Average"][0]
                time = obsDict["BeautyTime"]
                terr = obsDict["BeautyTimeErr"]
                resmodel, acc = resmodelutils.getResolutionModel(workspaceIn, config, time, terr, acc)
            elif myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["Type"] == "AverageModel":
                if debug:
                    print "Build mean time resolution model for "+comp
                config["Context"] = "GEN"
                config["DecayTimeResolutionModel"] = myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["Parameters"]
                config["DecayTimeResolutionBias"] = myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["Bias"][0]
                config["DecayTimeResolutionScaleFactor"] = myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["ScaleFactor"][0]
                time = obsDict["BeautyTime"]
                resmodel, acc = resmodelutils.getResolutionModel(workspaceIn, config, time, None, acc)
            else:
                print "ERROR: resolution type "+myconfigfile["ResolutionAcceptance"][comp]["Resolution"]["Type"]+" not supported."
                exit(-1)
        else:
            print "ERROR: error when building resolution for "+comp+". Please check config file."
            exit(-1)

        #Put resolution/acceptance in dictionary
        resAccDict[comp]["Acceptance"] = acc
        resAccDict[comp]["Resolution"] = resmodel

    if debug:
            print "Resolution/acceptance dictionary:"
            print resAccDict

    return resAccDict

#------------------------------------------------------------
def BuildTimeErrorPDF(workspaceIn, myconfigfile, comp, obsDict, debug):

    pdf = None
    if myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"] == None:
        if debug:
            print "No time error pdf (mean resolution model)"
        return pdf
    elif "Type" in myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"].keys():
        if myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["Type"] == "FromWorkspace":
            if debug:
                print "Take time error pdf "+myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["Name"]+" from workspace "+myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["Workspace"]+" in file "+myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["File"]
            file = TFile.Open(myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["File"],"READ")
            w = file.Get(myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["Workspace"])
            pdf = WS(workspaceIn, w.pdf(myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["Name"]))
            file.Close()
        elif myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["Type"] == "Mock":
            if debug:
                print "Build mock time error pdf"
            pdf = WS(workspaceIn, BuildMockTimeErrorPDF(workspaceIn, myconfigfile, comp, obsDict, debug))
        else:
            print "ERROR: time error pdf type "+myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["Type"]+" not supported."
            exit(-1)
    else:
        print "ERROR: error in time error pdf building. Please check your config file."
        exit(-1)

    if debug:
        print "Time error pdf:"
        print pdf.Print("v")

    return pdf

#------------------------------------------------------------
def BuildMockTimeErrorPDF(workspaceIn, myconfigfile, comp, obsDict, debug):

    terr = obsDict["BeautyTimeErr"]

    avg = WS(workspaceIn, RooRealVar("terrshape_"+comp,
                                      "terrshape_"+comp,
                                      -1.0 * (myconfigfile["ResolutionAcceptance"][comp]["TimeErrorPDF"]["ResolutionAverage"][0]) / 7.0))
    exp = WS(workspaceIn, RooExponential("terrexp_"+comp,
                                          "terrexp_"+comp,
                                          terr, avg))
    zero = workspaceIn.obj("zero")
    one = workspaceIn.obj("one")
    poly = WS(workspaceIn, RooPolynomial("terrpoly_"+comp,
                                          "terrpoly_"+comp,
                                          terr, RooArgList(zero, zero, zero, zero, zero, zero, one), 0))

    pdf = WS(workspaceIn, RooProdPdf("TimeErrorPDF_"+comp,
                                      "TimeErrorPDF_"+comp,
                                      exp, poly))

    return pdf

#------------------------------------------------------------
def BuildAsymmetries(workspaceIn, myconfigfile, debug):

    asymmDict = {}
    for comp in myconfigfile["Components"].iterkeys():
        asymmDict[comp] = {}
        asymmDict[comp]["Production"] = {}
        asymmDict[comp]["Production"] = WS(workspaceIn, RooRealVar("AProd_"+comp,
                                                                    "AProd_"+comp,
                                                                    *myconfigfile["ProductionAsymmetry"][comp]))
        asymmDict[comp]["Detection"] = {}
        asymmDict[comp]["Detection"] = WS(workspaceIn, RooRealVar("ADet_"+comp,
                                                                   "ADet_"+comp,
                                                                   *myconfigfile["DetectionAsymmetry"][comp]))

    if debug:
        print "Asymmetry dictionary:"
        print asymmDict

    return asymmDict

#-----------------------------------------------------------------------------
def BuildTotalPDF(workspaceIn, myconfigfile, obsDict, ACPDict, tagDict, resAccDict, asymmDict, workTemplate, debug):

    pdf = None
    pdfDict = {}

    #Loop over bachelor mass hypotheses
    yieldCount = {}
    for hypo in myconfigfile["Hypothesys"]:
        print "Hypothesys: "+hypo
        pdfDict[hypo] = {}
        yieldCount[hypo] = {}
        #Loop over years of data taking
        for year in myconfigfile["Years"]:
            print "Year: "+year
            pdfDict[hypo][year] = {}
            yieldCount[hypo][year] = {}
            #Loop over D decay modes
            for mode in myconfigfile["CharmModes"]:
                print "D decay mode: "+mode
                pdfDict[hypo][year][mode] = {}
                yieldCount[hypo][year][mode] = {}
                #Loop over components
                for comp in myconfigfile["Components"].iterkeys():
                    print "Component: "+comp
                    pdfDict[hypo][year][mode][comp] = {}
                    yieldCount[hypo][year][mode][comp] = {}
                    #Loop over observables
                    for obs in myconfigfile["Observables"].iterkeys():
                        #Build PDF
                        if obs in ["BeautyMass", "CharmMass", "BacPIDK"] and myconfigfile["PDFList"][obs][comp][hypo][year][mode]["Type"] == "None":
                            pdfDict[hypo][year][mode][comp][obs] = {}
                            pdfDict[hypo][year][mode][comp][obs] = None
                            continue

                        if obs == "BeautyTime" and None!=ACPDict and None!=tagDict and None!=resAccDict and None!=asymmDict:
                            print "Observables: "+obs
                            pdfDict[hypo][year][mode][comp][obs] = {}
                            pdfDict[hypo][year][mode][comp][obs] = WS(workspaceIn, BuildTimePDF(workspaceIn,
                                                                                                myconfigfile,
                                                                                                hypo,
                                                                                                year,
                                                                                                comp,
                                                                                                mode,
                                                                                                obsDict,
                                                                                                ACPDict,
                                                                                                tagDict,
                                                                                                resAccDict,
                                                                                                asymmDict,
                                                                                                debug))
                        elif obs in ["BeautyMass", "CharmMass", "BacPIDK", "TrueID"]:

                            print "Observables: "+obs
                            pdfDict[hypo][year][mode][comp][obs] = {}
                            pdfDict[hypo][year][mode][comp][obs] = WS(workspaceIn, BuildPDF(workspaceIn,
                                                                                            myconfigfile,
                                                                                            hypo,
                                                                                            year,
                                                                                            comp,
                                                                                            mode,
                                                                                            obsDict[obs],
                                                                                            workTemplate,
                                                                                            debug))

                    pdfDict[hypo][year][mode][comp]["Yield"] = WS(workspaceIn, RooRealVar("nEvts_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                                                                          "nEvts_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                                                                          *myconfigfile["Components"][comp][hypo][year][mode]))
                    yieldCount[hypo][year][mode][comp] = myconfigfile["Components"][comp][hypo][year][mode][0]

    if debug:
        print "PDF dictionary:"
        print pdfDict
        print "Yields:"
        print yieldCount

    return {"PDF"      : pdfDict,
            "Events"   : yieldCount}

#-----------------------------------------------------------------------------
def BuildACPDict(workspaceIn, myconfigfile, debug):

    ACPDict = {}

    for comp in myconfigfile["Components"].iterkeys():

        ACPDict[comp] = {}

        if "ArgLf" in myconfigfile["ACP"][comp].keys() and "ArgLbarfbar" in myconfigfile["ACP"][comp].keys() and "ModLf" in myconfigfile["ACP"][comp].keys():

            if debug:
                print "Building CP coefficients using amplitude values"

            ACPobs = cpobservables.AsymmetryObservables(myconfigfile["ACP"][comp]["ArgLf"][0],
                                                        myconfigfile["ACP"][comp]["ArgLbarfbar"][0],
                                                        myconfigfile["ACP"][comp]["ModLf"][0])
            ACPobs.printtable()

            ACPDict[comp]["C"] = WS(workspaceIn, RooRealVar("C_"+comp, "C_"+comp, ACPobs.Cf()))
            ACPDict[comp]["S"] = WS(workspaceIn, RooRealVar("S_"+comp, "S_"+comp, ACPobs.Sf()))
            ACPDict[comp]["D"] = WS(workspaceIn, RooRealVar("D_"+comp, "D_"+comp, ACPobs.Df()))
            ACPDict[comp]["Sbar"] = WS(workspaceIn, RooRealVar("Sbar_"+comp, "Sbar_"+comp, ACPobs.Sfbar()))
            ACPDict[comp]["Dbar"] = WS(workspaceIn, RooRealVar("Dbar_"+comp, "Dbar_"+comp, ACPobs.Dfbar()))

        else:

            if debug:
                print "Building CP coefficients directly from their values"

            ACPDict[comp]["C"] = WS(workspaceIn, RooRealVar("C_"+comp, "C_"+comp, *myconfigfile["ACP"][comp]["C"]))
            ACPDict[comp]["S"] = WS(workspaceIn, RooRealVar("S_"+comp, "S_"+comp, *myconfigfile["ACP"][comp]["S"]))
            ACPDict[comp]["D"] = WS(workspaceIn, RooRealVar("D_"+comp, "D_"+comp, *myconfigfile["ACP"][comp]["D"]))
            ACPDict[comp]["Sbar"] = WS(workspaceIn, RooRealVar("Sbar_"+comp, "Sbar_"+comp, *myconfigfile["ACP"][comp]["Sbar"]))
            ACPDict[comp]["Dbar"] = WS(workspaceIn, RooRealVar("Dbar_"+comp, "Dbar_"+comp, *myconfigfile["ACP"][comp]["Dbar"]))

        #Build other decay rate parameters
        ACPDict[comp]["Gamma"] = WS(workspaceIn, RooRealVar("Gamma_"+comp,
                                                            "Gamma_"+comp,
                                                            *myconfigfile["ACP"][comp]["Gamma"]))
        ACPDict[comp]["DeltaGamma"] = WS(workspaceIn, RooRealVar("DeltaGamma_"+comp,
                                                                 "DeltaGamma_"+comp,
                                                                 *myconfigfile["ACP"][comp]["DeltaGamma"]))
        ACPDict[comp]["DeltaM"] = WS(workspaceIn, RooRealVar("DeltaM_"+comp,
                                                             "DeltaM_"+comp,
                                                             *myconfigfile["ACP"][comp]["DeltaM"]))

    if debug:
        print "CP components dictionary:"
        print ACPDict

    return ACPDict

#-----------------------------------------------------------------------------
def BuildTimePDF(workspaceIn, myconfigfile, hypo, year, comp, mode, obsDict, ACPDict, tagDict, resAccDict, asymmDict, debug):

    pdf = workspaceIn.pdf("TimePDF_"+comp)

    if not pdf:

        #Retrieve time and final state observables
        time = obsDict["BeautyTime"]
        qf = obsDict["BacCharge"]

        #Retrieve CP coefficients and decay rate parameters
        C = ACPDict[comp]["C"]
        S = ACPDict[comp]["S"]
        D = ACPDict[comp]["D"]
        Sbar = ACPDict[comp]["Sbar"]
        Dbar = ACPDict[comp]["Dbar"]
        Gamma = ACPDict[comp]["Gamma"]
        DeltaGamma = ACPDict[comp]["DeltaGamma"]
        DeltaM = ACPDict[comp]["DeltaM"]

        #Retrieve tagging
        mistagcalib = tagDict[comp]["Calibration"]
        mistagpdf = tagDict[comp]["MistagPDF"]

        qt = []
        mistagobs = []
        for tagger in myconfigfile["Taggers"][comp].iterkeys():
            if "Mistag"+tagger in obsDict.keys() and "TagDec"+tagger in obsDict.keys():
                mistagobs.append( obsDict["Mistag"+tagger] )
                qt.append( obsDict["TagDec"+tagger] )

        #Retrieve time error PDF, resolution and acceptance
        terrpdf = resAccDict[comp]["TimeErrorPDF"]
        resmodel = resAccDict[comp]["Resolution"]
        acc = resAccDict[comp]["Acceptance"]
        timeerr = None
        if "BeautyTimeErr" in obsDict.keys():
            timeerr = obsDict["BeautyTimeErr"]

        #Retrieve asymmetries
        aprod = asymmDict[comp]["Production"]
        adet = asymmDict[comp]["Detection"]

        #Build a config dict that buildBDecayTimePdf can understand
        config = {}
        config["Context"] = "GEN"
        config["Debug"] = True if debug else False
        config["ParameteriseIntegral"] = myconfigfile["ACP"][comp]["ParameteriseIntegral"]
        config["UseProtoData"] = True #this is really recommended to speed-up generation
        config["NBinsAcceptance"] = myconfigfile["ACP"][comp]["NBinsAcceptance"]
        if "NBinsProperTimeErr" in myconfigfile["ACP"][comp].keys():
             config["NBinsProperTimeErr"] = myconfigfile["ACP"][comp]["NBinsProperTimeErr"]

        #Build time PDF
        pdf = timepdfutils_Bd.buildBDecayTimePdf(
            config,
            "TimePDF_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
            workspaceIn,
            time, timeerr, qt, qf, mistagobs, mistagcalib,
            Gamma, DeltaGamma, DeltaM,
            C, D, Dbar, S, Sbar,
            resmodel, acc,
            terrpdf, mistagpdf,
            aprod, adet)

    return WS(workspaceIn, pdf)

#-----------------------------------------------------------------------------
def BuildPDF(workspaceIn, myconfigfile, hypo, year, comp, mode, obs, workTemplate, debug):

    pdf = None

    if obs.GetName() == "TrueID":
        #Build narrow gaussian around selected ID number
        mean = WS(workspaceIn, RooConstVar("mean_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                           "mean_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                           myconfigfile["TrueID"][comp]))
        sigma = WS(workspaceIn, RooConstVar("sigma_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                            "sigma_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                            1.0))
        pdf = WS(workspaceIn, RooGaussian("TrueID_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                          "TrueID_both"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                          obs, mean, sigma))
    elif obs.GetName() in ["BeautyMass", "CharmMass"]:

        print obs.GetName(), comp, hypo, year, mode
        print  myconfigfile["PDFList"][obs.GetName()][comp][hypo][year]
        mode2 = mode
        if myconfigfile["PDFList"][obs.GetName()][comp][hypo][year].has_key("All"):
            mode = "All"
        shapeType = myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Type"]
        if shapeType == "FromWorkspace":
            name =  myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Name"]
            #       work = myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Workspace"]
            #       filename = myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["File"]
            if debug:
                print "Take PDF "+name+" from workspace " #+work+" inside file "+filename
            #file = TFile.Open(filename,"READ")
            #w = file.Get(work)
            pdf = WS(workspaceIn, workTemplate.pdf(name))
            pdf.SetName(comp+"_"+obs.GetName()+"_"+mode2+"_"+year+"_"+hypo+"Hypo")
            #pdf = WS(workspaceIn, pdf) #w.obj(name) )
            #file.Close()
        else:
            pdf = BuildAnalyticalPdf(workspaceIn, shapeType, myconfigfile, hypo, year, comp, mode, obs, debug)
            pdf.SetName(comp+"_"+obs.GetName()+"_"+mode2+"_"+year+"_"+hypo+"Hypo")
            pdf = WS(workspaceIn, pdf)

    elif obs.GetName() in ["BacPIDK"]:
        mode2 = mode
        if myconfigfile["PDFList"][obs.GetName()][comp][hypo][year].has_key("All"):
            mode = "All"
        shapeType = myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Type"]
        if shapeType == "FromWorkspace":
            pdfTmp = {}
            name = {}
            for pol in ["Up","Down"]:
                name[pol] = {}
                work =  myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Workspace"]
                filename = myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["File"]
                if comp != "Combinatorial":
                    name[pol]["Merged"] = myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Name"][pol]
                else:
                    contributions = myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Contributions"]
                    for con in contributions:
                        name[pol][con] = myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Name"][pol][con]
                if debug:
                    for n in name:
                        print "Take PDF "+n+" from workspace " #+work+" inside file "+filename
                #filePDF = TFile.Open(filename,"READ")
                #workTemplate = filePDF.Get(work)
                pdfTmp[pol] = {}
                for n in name:
                    print n
                    if comp != "Combinatorial":
                        pdfTmp[pol]["Merged"] = WS(workspaceIn, workTemplate.obj(name[pol]["Merged"]) )
                    else:
                        for con in contributions:
                            pdfTmp[pol][con] = WS(workspaceIn, workTemplate.obj(name[pol][con]))
                #filePDF.Close()
            if comp == "Combinatorial":
                sizeContr = len(contributions)
                for pol in ["Up","Down"]:
                    fracList = RooArgList()
                    for i in range(0,sizeContr-1):
                        print myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Name"][pol]["fracPIDK"][i]
                        fracName = "fracPIDK"+str(i+1) + "_" + pol + "_" + mode + "_" + year
                        fracList.add(WS(workspaceIn, RooRealVar(fracName, fracName, myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode]["Name"][pol]["fracPIDK"][i])))
                    pdfList = RooArgList()
                    for con in contributions:
                        pdfList.add(pdfTmp[pol][con])
                    pdfList.Print("v")
                    fracList.Print("v")
                    namePDF = comp+"_"+obs.GetName()+"_"+mode2+"_"+pol+"_"+year+"_"+hypo+"Hypo"
                    pdfTmp[pol]["Merged"] =  WS(workspaceIn, RooAddPdf(namePDF,namePDF,pdfList, fracList))

            print pdfTmp
            namePDF = comp+"_"+obs.GetName()+"_"+mode2+"_"+year
            frac = WS(workspaceIn, RooRealVar("frac_"+year,"frac_"+year, myconfigfile["FractionsLuminosity"][year]))
            pdf = WS(workspaceIn, RooAddPdf(namePDF, namePDF, pdfTmp["Up"]["Merged"],pdfTmp["Down"]["Merged"],frac))
        else:
            pdf = BuildAnalyticalPdf(workspaceIn, shapeType, myconfigfile, hypo, year, comp, mode, obs, debug)
            pdf.SetName(comp+"_"+obs.GetName()+"_"+mode2+"_"+year+"_"+hypo+"Hypo")
            pdf = WS(workspaceIn, pdf)
    else:
        print "ERROR: pdfs for observables "+obs.GetName()+" not yet implemented."
        exit(-1)

    pdf.Print("v")
    return pdf

#-----------------------------------------------------------------------------
def BuildAnalyticalPdf(workspaceIn, shapeType, myconfigfile, hypo, year, comp, mode, obs, debug):

    ##########################################
    # Users are encouraged to add other PDFs #
    # here and commit them if required!      #
    ##########################################

    pdf = None

    #Label
    smyh_vec = GeneralUtils.GetSampleModeYearHypo(TString("both"), #Not splitting per magnet pol, at the moment
                                                  TString(mode),
                                                  TString(year),
                                                  TString(hypo),
                                                  TString("pol"), #Just need to merge polarities, I guess?
                                                  debug)
    #Should always have a 1-dimensional vector inside this function (one D mode, one year...)
    #In fact, BuildAnalyticalPdf is called for each of these at time
    smyh = smyh_vec[0]

    widthRatio = False
    sameMean = False
    #Build parameters for this PDF into internal workspace
    for param in myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode].iterkeys():
        if param != "Type" and param != "widthRatio":
            if debug:
                print "Building "+comp+"_"+obs.GetName()+"_"+param+"_"+smyh.Data()+" parameter"
            par = WS(workspaceIn, RooRealVar(comp+"_"+obs.GetName()+"_"+param+"_"+smyh.Data(),
                                             comp+"_"+obs.GetName()+"_"+param+"_"+smyh.Data(),
                                             *myconfigfile["PDFList"][obs.GetName()][comp][hypo][year][mode][param]))
            if not par:
                print "ERROR: parameter "+param+" not created. Please check!"
                exit(-1)

        elif  param == "widthRatio":
            widthRatio = param

    #Build PDF as requested
    if shapeType == "Ipatia":
        pdf = Bs2Dsh2011TDAnaModels.buildIpatiaPDF(obs,
                                                   workspaceIn,
                                                   smyh,
                                                   comp,
                                                   False, #don't shift mean
                                                   False, #don't rescale tails
                                                   debug)
    elif shapeType == "JohnsonSU":
        pdf = Bd2DhModels.buildJohnsonSUPDF(obs,
                                            workspaceIn,
                                            smyh,
                                            comp,
                                            False, #don't shift mean
                                            debug)
    elif shapeType == "DoubleCrystalBall":
        pdf = Bs2Dsh2011TDAnaModels.buildDoubleCrystalBallPDF(obs,
                                                              workspaceIn,
                                                              smyh,
                                                              comp,
                                                              widthRatio,
                                                              sameMean, #don't use "shared mean"
                                                              debug)
    elif shapeType == "Gaussian":
        pdf =  Bs2Dsh2011TDAnaModels.buildGaussPDF(obs,
                                                   workspaceIn,
                                                   smyh,
                                                   comp,
                                                   False, #don't shift mean
                                                   debug)
    elif shapeType == "DoubleGaussian":
        pdf = Bs2Dsh2011TDAnaModels.buildDoubleGaussPDF(obs,
                                                        workspaceIn,
                                                        smyh,
                                                        comp,
                                                        False, #don't use "width ratio"
                                                        False, #don't use "same mean"
                                                        False, #don't shift mean
                                                        debug)
    elif shapeType == "CrystalBallPlusGaussian":
        pdf = Bd2DhModels.buildCrystalBallPlusGaussianPDF(obs,
                                                          workspaceIn,
                                                          smyh,
                                                          comp,
                                                          False, #don't shift mean
                                                          False, #don't scale widths
                                                          debug)
    elif shapeType == "Exponential":
        pdf = Bs2Dsh2011TDAnaModels.buildExponentialPDF(obs,
                                                        workspaceIn,
                                                        smyh,
                                                        comp,
                                                        debug)
    elif shapeType == "DoubleExponential":
        pdf = Bs2Dsh2011TDAnaModels.buildDoubleExponentialPDF(obs,
                                                              workspaceIn,
                                                              smyh,
                                                              comp,
                                                              debug)
    elif shapeType == "ExponentialPlusConstant":
        pdf = Bd2DhModels.buildExponentialPlusConstantPDF(obs,
                                                          workspaceIn,
                                                          smyh,
                                                          comp,
                                                          debug)
    elif shapeType == "ExponentialPlusDoubleCrystalBall":
        pdf = Bs2Dsh2011TDAnaModels.buildExponentialPlusDoubleCrystalBallPDF(obs,
                                                                             workspaceIn,
                                                                             smyh,
                                                                             comp,
                                                                             False,
                                                                             False,
                                                                             debug)
    else:
        print "ERROR: pdf type "+shapeType+" not yet implemented."
        exit(-1)

    return pdf

#-----------------------------------------------------------------------------
def BuildProtoData(workspaceIn, myconfigfile, obsDict, tagDict, resAccDict, pdfDict, seed, debug):

    if "BeautyTime" not in obsDict.keys():
        return None

    #Setup poisson generator for yields
    poissonGen = TRandom3(seed)
    if debug:
        print "Seed to generate yields: "+str(poissonGen.GetSeed())

    #Ok, we have time observable. Let's see if we need per event mistag/time error
    nevts = pdfDict["Events"]
    protoDataDict = {}

    for hypo in myconfigfile["Hypothesys"]:
        protoDataDict[hypo] = {}

        for year in myconfigfile["Years"]:
            protoDataDict[hypo][year] = {}

            for mode in myconfigfile["CharmModes"]:
                protoDataDict[hypo][year][mode] = {}

                for comp in myconfigfile["Components"].iterkeys():
                    protoDataDict[hypo][year][mode][comp] = []
                    atLeast = 0

                    #Get random number of events to generate
                    if int(nevts[hypo][year][mode][comp]) > 0:
                        poissonNum = poissonGen.Poisson( int(nevts[hypo][year][mode][comp]) )
                    else:
                        continue

                    #Check tagging
                    tag = 0
                    if tagDict[comp]["MistagPDF"] != None:
                        for tagger in myconfigfile["Taggers"][comp].iterkeys():
                            if "Mistag"+tagger in obsDict.keys() and "TagDec"+tagger in obsDict.keys():
                                if debug:
                                    print "Generate "+str(poissonNum)+" Mistag"+tagger+" proto data from "+tagDict[comp]["MistagPDF"][tag].GetName()
                                protoDataDict[hypo][year][mode][comp].append( tagDict[comp]["MistagPDF"][tag].generate( RooArgSet(obsDict["Mistag"+tagger]),
                                                                                                                        RooFit.AutoBinned(False),
                                                                                                                        RooFit.NumEvents(poissonNum) ) )
                                protoDataDict[hypo][year][mode][comp][atLeast].SetName(protoDataDict[hypo][year][mode][comp][atLeast].GetName()+"both_"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                                protoDataDict[hypo][year][mode][comp][atLeast].SetTitle(protoDataDict[hypo][year][mode][comp][atLeast].GetName()+"both_"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                                protoDataDict[hypo][year][mode][comp][atLeast] = WS(workspaceIn, protoDataDict[hypo][year][mode][comp][atLeast])

                                atLeast = atLeast+1
                                tag = tag+1

                    #Check per-event error
                    if resAccDict[comp]["TimeErrorPDF"] != None:
                        if debug:
                            print "Generate "+str(poissonNum)+" per-event time error proto data from "+resAccDict[comp]["TimeErrorPDF"].GetName()
                        protoDataDict[hypo][year][mode][comp].append( resAccDict[comp]["TimeErrorPDF"].generate( RooArgSet(obsDict["BeautyTimeErr"]),
                                                                                                                 poissonNum ) )
                        protoDataDict[hypo][year][mode][comp][atLeast].SetName(protoDataDict[hypo][year][mode][comp][atLeast].GetName()+"both_"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                        protoDataDict[hypo][year][mode][comp][atLeast].SetTitle(protoDataDict[hypo][year][mode][comp][atLeast].GetName()+"both_"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                        protoDataDict[hypo][year][mode][comp][atLeast] = WS(workspaceIn, protoDataDict[hypo][year][mode][comp][atLeast])

                        atLeast = atLeast+1

    if atLeast == 0:
        if debug:
            print "No need for proto data"
        return None

    if debug:
        print "Proto data dictionary:"
        print protoDataDict

    #Merge datasets for a given hypo, component
    protoDataMerged = {}

    for hypo in myconfigfile["Hypothesys"]:
        protoDataMerged[hypo] = {}

        for year in myconfigfile["Years"]:
            protoDataMerged[hypo][year] = {}

            for mode in myconfigfile["CharmModes"]:
                protoDataMerged[hypo][year][mode] = {}

                for comp in myconfigfile["Components"].iterkeys():

                    if protoDataDict[hypo][year][mode][comp].__len__() > 0:

                        protoDataMerged[hypo][year][mode][comp] = {}
                        countGenObs = 0

                        for data in protoDataDict[hypo][year][mode][comp]:
                            if countGenObs == 0:
                                protoDataMerged[hypo][year][mode][comp] = copy.deepcopy( protoDataDict[hypo][year][mode][comp][countGenObs] )
                            else:
                                protoDataMerged[hypo][year][mode][comp].merge( protoDataDict[hypo][year][mode][comp][countGenObs] )
                            countGenObs = countGenObs+1

                        protoDataMerged[hypo][year][mode][comp].SetName("ProtoData_both_"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                        protoDataMerged[hypo][year][mode][comp].SetTitle("ProtoData_both_"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo")

                    else:
                        protoDataMerged[hypo][mode] = None

    if debug:
        print "Merged proto data dictionary:"
        print protoDataMerged

    return protoDataMerged

#-----------------------------------------------------------------------------
def GenerateToys(workspaceIn, myconfigfile, observables, pdfDict, protoData, seed, debug):

    pdf = pdfDict["PDF"]
    nevts = pdfDict["Events"]

    toyDict = {}

    #Setup poisson generator for yields
    poissonGen = TRandom3(seed)
    if debug:
        print "Seed to generate yields: "+str(poissonGen.GetSeed())

    #Loop over bachelor mass hypotheses
    for hypo in myconfigfile["Hypothesys"]:
        print "Hypothesys: "+hypo
        toyDict[hypo] = {}
        #Loop over years of data taking
        for year in myconfigfile["Years"]:
            print "Year: "+year
            toyDict[hypo][year] = {}
            #Loop over D decay modes
            for mode in myconfigfile["CharmModes"]:
                print "D decay mode: "+mode
                toyDict[hypo][year][mode] = {}
                #Loop over components
                for comp in myconfigfile["Components"].iterkeys():
                    print "Components: "+comp
                    toyDict[hypo][year][mode][comp] = {}

                    #Get random number of events to generate
                    if int(nevts[hypo][year][mode][comp]) > 0:
                        poissonNum = poissonGen.Poisson( int(nevts[hypo][year][mode][comp]) )
                    else:
                        toyDict[hypo][year][mode][comp][obs] = None
                        continue

                    #Loop over observables
                    for obs in myconfigfile["Observables"].iterkeys():

                        if obs == "BeautyTime":
                            print "Observable: "+obs
                            toyDict[hypo][year][mode][comp][obs] = {}
                            genset = RooArgSet(observables.find(obs),
                                               observables.find("BacCharge"))
                            if "TagDecOS" in myconfigfile["Observables"].keys():
                                genset.add( observables.find("TagDecOS") )
                            if "TagDecSS" in myconfigfile["Observables"].keys():
                                genset.add( observables.find("TagDecSS") )
                            #If we have proto data use it, otherwise only draw number of events to generate from Poisson distribution
                            if None != protoData:
                                if debug:
                                    print "Generate "+str(poissonNum)+" decay time data from "+pdf[hypo][year][mode][comp][obs].GetName()
                                toyDict[hypo][year][mode][comp][obs] = WS(workspaceIn, pdf[hypo][year][mode][comp][obs].generate(genset,
                                                                                                                                 RooFit.ProtoData(protoData[hypo][year][mode][comp]),
                                                                                                                                 RooFit.NumEvents(poissonNum)) )
                            else:
                                if debug:
                                    print "Generate "+str(poissonNum)+" decay time data from "+pdf[hypo][year][mode][comp][obs].GetName()
                                    print "No proto data used - the generation takes ages, do it at your own 'risk'"
                                toyDict[hypo][year][mode][comp][obs] = WS(workspaceIn, pdf[hypo][year][mode][comp][obs].generate(genset,
                                                                                                                                 RooFit.NumEvents(poissonNum) ) )
                        elif obs in ["BeautyMass", "CharmMass", "BacPIDK", "TrueID"]:
                            print "Observable: "+obs
                            genset = RooArgSet(observables.find(obs))
                            toyDict[hypo][year][mode][comp][obs] = {}

                            if obs == "BacPIDK":
                                if debug:
                                    print "Generate "+str(poissonNum)+" BacPIDK data from "+pdf[hypo][year][mode][comp][obs].GetName()
                                toyDict[hypo][year][mode][comp][obs] = WS(workspaceIn, pdf[hypo][year][mode][comp][obs].generate(genset,
                                                                                                                                 RooFit.AutoBinned(False),
                                                                                                                                 #RooFit.Extended(),
                                                                                                                                 RooFit.NumEvents(poissonNum) ) )
                            else:
                                if debug:
                                    print "Generate "+str(poissonNum) + " " + obs + " data from "+pdf[hypo][year][mode][comp][obs].GetName()
                                toyDict[hypo][year][mode][comp][obs] = WS(workspaceIn, pdf[hypo][year][mode][comp][obs].generate(genset,
                                                                                                                                 #RooFit.Extended(),
                                                                                                                                 RooFit.NumEvents(poissonNum) ) )

    if debug:
        print "Toy dictionary:"
        print toyDict

    return toyDict

#-----------------------------------------------------------------------------
def BuildTotalDataset(workspaceIn, myconfigfile, toyDict, debug):

    #Build category to identify sample
    sam = RooCategory("sample","sample")
    sm = []
    importList = []

    #Append all datasets for a given hypothesys, D decay mode
    foundObs = False
    idx = 0
    modesData = []

    for hypo in toyDict.iterkeys():

        print "Hypothesys: "+hypo

        for year in toyDict[hypo].iterkeys():

            print "Year: "+year

            for mode in toyDict[hypo][year].iterkeys():

                modeSmall = GeneralUtils.GetModeLower(TString(mode),debug)
                print "D decay mode: "+mode
                typeName = TString("both_")+modeSmall+TString("_")+TString(year)+TString("_")+TString(hypo)+TString("Hypo")
                sam.defineType(typeName.Data(), idx)
                sm.append(typeName)
                print typeName

                if debug:
                    print "Defined category both_"+mode+"_"+year+"_"+hypo+"Hypo with index "+str(idx)

                countComp = 0
                for comp in toyDict[hypo][year][mode].iterkeys():

                    print "Component: "+comp

                    countObs = 0
                    dataObs = None

                    for obs in toyDict[hypo][year][mode][comp].iterkeys():

                        if None == toyDict[hypo][year][mode][comp][obs]:
                            continue

                        print "Observable: "+obs
                        print "Entries "+str(toyDict[hypo][year][mode][comp][obs].sumEntries())
                        if countObs == 0:
                            dataObs = copy.deepcopy( toyDict[hypo][year][mode][comp][obs] )
                        else:
                            dataObs.merge( toyDict[hypo][year][mode][comp][obs] )

                        countObs = countObs +1

                    if None == dataObs or dataObs.numEntries() == 0:
                        continue

                    dataObs.SetName("Toy_both_"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                    dataObs.SetTitle("Toy_both_"+year+"_"+comp+"_"+mode+"_"+hypo+"Hypo")

                    if countComp == 0:
                        print "Creating data set: ", dataObs.GetName()
                        dataComp = copy.deepcopy( dataObs )
                    else:
                        print "Appending data set: ",dataObs.GetName()
                        dataComp.append( dataObs )

                    countComp = countComp + 1

                dataName = TString("dataSet")+TString(myconfigfile["Decay"]) + TString("_") + typeName
                dataComp.SetName(dataName.Data())
                dataComp.SetTitle(dataName.Data())
                dataComp = WS(workspaceIn, dataComp)

                modesData.append(dataComp)

                if not foundObs:
                    #Use this dataset to retrieve list of observables
                    observables = dataComp.get()
                    foundObs = True

                #print mode, year, hypo
                #print dataComp.GetName()
                #importList.append( RooFit.Import("both_"+mode+"_"+year+"_"+hypo+"Hypo", dataComp) )
                #print "append list"
                #print sam

                #modesData.append( WS(workspaceIn, RooDataSet("dataSet"+myconfigfile["Decay"]+"_both_"+mode+"_"+year+"_"+hypo+"Hypo",
                #                                             "dataSet"+myconfigfile["Decay"]+"_both_"+mode+"_"+year+"_"+hypo+"Hypo",
                #                                             observables
                                                             #RooFit.Index(sam),
                #                                             RooFit.Import("both_"+mode+"_"+year+"_"+hypo+"Hypo", dataComp)))) #*importList))

                idx = idx + 1


    totData = RooDataSet("totData","totData", observables, RooFit.Index(sam),RooFit.Import(sm[0].Data(),modesData[0]))
    print "[INFO] Adding data set: ",modesData[0].GetName()
    for i in range(0,len(modesData)):
        if ( i != 0 ):
            totDatatmp = RooDataSet("totData","totData", observables, RooFit.Index(sam),RooFit.Import(sm[i].Data(),modesData[i]))
            if debug:
                print "[INFO] Adding data set: ",modesData[i].GetName()
            totData.append(totDatatmp)


    if debug:
        print "Total dataset:"
        totData.Print("v")
        print "Sample categories:"
        sam.Print("v")

    return totData, modesData

#-----------------------------------------------------------------------------
def MergeYears(myconfigfile, modesData, debug):

    print "[INFO] Merge years of data taking"

    sam = RooCategory("sample","sample")
    idx = 0
    modesDataOut = []
    sm = []

    for hypo in myconfigfile["Hypothesys"]:
        for mode in myconfigfile["CharmModes"]:
            print "D decay mode: "+mode
            modeSmall = GeneralUtils.GetModeLower(TString(mode),debug)
            typeName = TString("both_")+modeSmall+TString("_run1_")+TString(hypo)+TString("Hypo")
            type2011 = TString("both_")+modeSmall+TString("_2011_")+TString(hypo)+TString("Hypo")
            type2012 = TString("both_")+modeSmall+TString("_2012_")+TString(hypo)+TString("Hypo")
            dataName = TString("dataSet")+TString(myconfigfile["Decay"]) + TString("_") + typeName

            print typeName, dataName
            sam.defineType(typeName.Data(), idx)
            sm.append(typeName)

            for data in modesData:
                if TString(data.GetName()).Contains(type2011) == True:
                    data2011 = data
                if TString(data.GetName()).Contains(type2012) == True:
                    data2012 = data

            print "Adding: ", data2011.GetName(), data2011.numEntries(),
            print "  to : ", data2012.GetName(), data2012.numEntries()

            data2011.append(data2012)
            data2011.SetName(dataName.Data())
            modesDataOut.append(data2011)

            idx  = idx + 1


    totData = RooDataSet("totData","totData", modesDataOut[0].get(), RooFit.Index(sam),RooFit.Import(sm[0].Data(),modesDataOut[0]))
    print "[INFO] Adding data set: ",modesDataOut[0].GetName()
    for i in range(0,len(modesDataOut)):
        if ( i != 0 ):
            totDatatmp = RooDataSet("totData","totData", modesDataOut[0].get(), RooFit.Index(sam),RooFit.Import(sm[i].Data(),modesDataOut[i]))
            if debug:
                print "[INFO] Adding data set: ",modesDataOut[i].GetName()
            totData.append(totDatatmp)


    if debug:
        print "Total dataset:"
        totData.Print("v")
        print "Sample categories:"
        sam.Print("v")

    return totData, modesDataOut




#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def toyFactory(configName,
               seed,
               outputdir,
               workOut,
               workfileOut,
               treeOut,
               treefileOut,
               saveTree,
               debug):

    # Safe settings for numerical integration (if needed)
    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
    RooAbsReal.defaultIntegratorConfig().getConfigSection(
        'RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection(
        'RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel(
        'RooAdaptiveGaussKronrodIntegrator1D')
    RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel(
        'RooAdaptiveGaussKronrodIntegrator1D')

    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "GENERATETOYS IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="

    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    workspaceIn = RooWorkspace("workIn", "workIn")
    one = WS(workspaceIn, RooConstVar("one", "1", 1.0))
    zero = WS(workspaceIn, RooConstVar("zero", "0", 0.0))

    print ""
    print "=========================================================="
    print "Set generation seed to "+str(seed)
    print "=========================================================="
    print ""

    gInterpreter.ProcessLine('gRandom->SetSeed('+str(int(seed))+')')
    RooRandom.randomGenerator().SetSeed(int(seed))

    print ""
    print "=========================================================="
    print "Build observables"
    print "=========================================================="
    print ""

    obsDict = BuildObservables(workspaceIn, myconfigfile, debug)

    tagDict = None
    resAccDict = None
    asymmDict = None
    ACPDict = None

    if "BeautyTime" in obsDict.keys():

        #Time is one of the observables; take care of tagging, acceptance, resolution, asymmetries, CP parameters

        print ""
        print "=========================================================="
        print "Setup tagging"
        print "=========================================================="
        print ""

        tagDict = BuildTagging(workspaceIn, myconfigfile, obsDict, debug)

        print ""
        print "=========================================================="
        print "Setup time resolution and acceptance"
        print "=========================================================="
        print ""

        resAccDict = BuildResolutionAcceptance(workspaceIn, myconfigfile, obsDict, debug)

        print ""
        print "=========================================================="
        print "Setup time production and detection asymmetries"
        print "=========================================================="
        print ""

        asymmDict = BuildAsymmetries(workspaceIn, myconfigfile, debug)

        print ""
        print "=========================================================="
        print "Setup CP coefficients and parameters"
        print "=========================================================="
        print ""

        ACPDict = BuildACPDict(workspaceIn, myconfigfile, debug)

    print ""
    print "=========================================================="
    print "Build PDF for all components/hypotheses"
    print "=========================================================="
    print ""

    workTemplate = None
    if "WorkspaceToRead" in myconfigfile.keys():
        print "Workspace with templates detected. Opening it..."
        filePDF = TFile.Open(myconfigfile["WorkspaceToRead"]["File"],"READ")
        workTemplate = filePDF.Get(myconfigfile["WorkspaceToRead"]["Workspace"])
        if debug:
            workTemplate.Print("v")
    pdfDict = BuildTotalPDF(workspaceIn, myconfigfile, obsDict, ACPDict, tagDict, resAccDict, asymmDict, workTemplate, debug)
    if "WorkspaceToRead" in myconfigfile.keys():
        filePDF.Close()

    print ""
    print "=========================================================="
    print "Start toy generation"
    print "=========================================================="
    print ""

    #Include observables
    observables = RooArgSet()
    for obs in obsDict.keys():
        if obs not in ["BeautyTimeErr", "MistagOS", "MistagSS"]:
            #We use "proto data", so we don't include now mistag and time error
            observables.add( obsDict[obs] )
    if debug:
        print "Observables for generation:"
        observables.Print("v")

    #Generate "proto data" from time error and mistag PDFs (if needed)
    protoData = BuildProtoData(workspaceIn, myconfigfile, obsDict, tagDict, resAccDict, pdfDict, int(seed), debug)

    #Generate toys
    toyDict = GenerateToys(workspaceIn, myconfigfile, observables, pdfDict, protoData, int(seed), debug)

    print toyDict
    print ""
    print "=========================================================="
    print "Toy generation done. Now merge/append datasets and"
    print "save them to file."
    print "=========================================================="
    print ""

    totData, modesData = BuildTotalDataset(workspaceIn, myconfigfile, toyDict, debug)

    if myconfigfile.has_key("MergedYears"):
        if myconfigfile["MergedYears"] == True:
            totData, modesData = MergeYears(myconfigfile, modesData, debug)

    observables = totData.get()
    observables.Print("v")
    workspaceOut = RooWorkspace(workOut, workOut)

    if debug:
        print "Output workspace "+workOut+" content:"
        workspaceOut.Print("v")

    if saveTree or myconfigfile["Components"].keys().__len__() == 1:
        print ""
        print "=========================================================="
        print "Save output tree "+treeOut+" to following file:"
        print outputdir+treefileOut
        print "=========================================================="
        print ""

        if myconfigfile["Components"].keys().__len__() == 1:
            print ""
            print "=========================================================="
            print "Only one component generated (signal?)"
            print "No need for MD fit."
            print "Producing tuple with dummy sWeight=1 for all the events"
            print "ready for the sFit."
            print "=========================================================="
            print ""

            if "2011" in myconfigfile["Years"] and "2012" in myconfigfile["Years"]:
                for hypo in myconfigfile["Hypothesys"]:
                    for mode in myconfigfile["CharmModes"]:
                        modelow = GeneralUtils.GetModeLower(TString(mode),debug)
                        s = TString("nSig_both_")+modelow+TString("_run1_")+TString(hypo)+TString("Hypo_Evts_sw")
                        weight = WS(workspaceOut, RooRealVar(s.Data(), s.Data(), 1.0))
                        observables.add(weight)
                        totData.addColumn( weight )
            else:
                for hypo in myconfigfile["Hypothesys"]:
                    for year in myconfigfile["Years"]:
                        for mode in myconfigfile["CharmModes"]:
                            modelow = GeneralUtils.GetModeLower(TString(mode),debug)
                            s = TString("nSig_both_")+modelow+TString("_")+TString(year)+TString("_")+TString(hypo)+TString("Hypo_Evts_sw")
                            weight = WS(workspaceOut, RooRealVar(s.Data(), s.Data(), 1.0))
                            observables.add(weight)
                            totData.addColumn( weight )

        fileTree = TFile.Open(outputdir+treefileOut, "RECREATE")
        tree = totData.tree()
        tree.SetName( treeOut )
        tree.Write()
        fileTree.Close()

    #totData = WS(workspaceOut, totData)
    for data in modesData:
        d = WS(workspaceOut, data)
    observables = WS(workspaceOut, observables)

    print ""
    print "=========================================================="
    print "Save output workspace "+workOut+" to following file:"
    print outputdir+workfileOut
    print "=========================================================="
    print ""
    workspaceOut.Print("v")
    workspaceOut.writeToFile( outputdir+workfileOut )

#-----------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'MyConfigFile',
                   help = 'configuration file name'
                   )
parser.add_option( '--seed',
                   dest = 'seed',
                   default = 193627,
                   help = 'seed for generation'
                   )
parser.add_option( '--outputdir',
                   dest = 'outputdir',
                   default = '',
                   help = 'output directory to store workspace/tree'
                   )

parser.add_option( '--workOut',
                   dest = 'workOut',
                   default = 'workspace',
                   help = 'output workspace name'
                   )

parser.add_option( '--workfileOut',
                   dest = 'workfileOut',
                   default = 'toyFactoryWorkFile.root',
                   help = 'output workspace file name'
                   )

parser.add_option( '--saveTree',
                   action = 'store_true',
                   dest = 'saveTree',
                   default = False,
                   help = 'save tree in addition to workspace'
                   )

parser.add_option( '--treeOut',
                   dest = 'treeOut',
                   default = 'merged',
                   help = 'output tree name'
                   )

parser.add_option( '--treefileOut',
                   dest = 'treefileOut',
                   default = 'toyFactoryTreeFile.root',
                   help = 'output tree file name'
                   )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

#-----------------------------------------------------------------------------
if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    config = options.configName
    last = config.rfind("/")
    directory = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]

    import sys
    sys.path.append(directory)

    print "Config file name: "+configName
    print "Directory: "+directory

    toyFactory(configName,
               options.seed,
               options.outputdir,
               options.workOut,
               options.workfileOut,
               options.treeOut,
               options.treefileOut,
               options.saveTree,
               options.debug)
