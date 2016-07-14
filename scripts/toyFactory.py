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
                    "Create mistag pdf for "+tagger+" tagger, "+comp+" component"
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
                                                                     False, True)
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
def BuildTotalPDF(workspaceIn, myconfigfile, obsDict, ACPDict, tagDict, resAccDict, asymmDict, debug):

    pdf = None
    pdfDict = {}

    #Loop over bachelor mass hypotheses
    yieldCount = {}
    for hypo in myconfigfile["Hypothesys"]:
        print "Hypothesys: "+hypo
        pdfDict[hypo] = {}
        yieldCount[hypo] = {}
        #Loop over components
        for mode in myconfigfile["CharmModes"]:
            print "D decay mode: "+mode
            pdfDict[hypo][mode] = {}
            yieldCount[hypo][mode] = {}
            #Loop over D decay modes
            for comp in myconfigfile["Components"].iterkeys():
                print "Component: "+comp
                pdfDict[hypo][mode][comp] = {}
                yieldCount[hypo][mode][comp] = {}
                #Loop over observables
                for obs in myconfigfile["Observables"].iterkeys():
                    #Build PDF
                    if obs == "BeautyTime" and None!=ACPDict and None!=tagDict and None!=resAccDict and None!=asymmDict:
                        print "Observables: "+obs
                        pdfDict[hypo][mode][comp][obs] = {}
                        pdfDict[hypo][mode][comp][obs] = WS(workspaceIn, BuildTimePDF(workspaceIn,
                                                                                      myconfigfile,
                                                                                      hypo,
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
                        pdfDict[hypo][mode][comp][obs] = {}
                        pdfDict[hypo][mode][comp][obs] = WS(workspaceIn, BuildPDF(workspaceIn,
                                                                                  myconfigfile,
                                                                                  hypo,
                                                                                  comp,
                                                                                  mode,
                                                                                  obsDict[obs],
                                                                                  debug))
                        
                #Build yield
                pdfDict[hypo][mode][comp]["Yield"] = WS(workspaceIn, RooRealVar("nEvts_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                                                                "nEvts_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                                                                *myconfigfile["Components"][comp][hypo][mode]))
                yieldCount[hypo][mode][comp] = myconfigfile["Components"][comp][hypo][mode][0]
                
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
def BuildTimePDF(workspaceIn, myconfigfile, hypo, comp, mode, obsDict, ACPDict, tagDict, resAccDict, asymmDict, debug):

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
        config["NBinsProperTimeErr"] = myconfigfile["ACP"][comp]["NBinsProperTimeErr"]

        #Build time PDF
        pdf = timepdfutils_Bd.buildBDecayTimePdf(
            config,
            "TimePDF_"+comp+"_"+mode+"_"+hypo+"Hypo",
            workspaceIn,
            time, timeerr, qt, qf, mistagobs, mistagcalib,
            Gamma, DeltaGamma, DeltaM,
            C, D, Dbar, S, Sbar,
            resmodel, acc,
            terrpdf, mistagpdf,
            aprod, adet)

    return WS(workspaceIn, pdf)

#-----------------------------------------------------------------------------
def BuildPDF(workspaceIn, myconfigfile, hypo, comp, mode, obs, debug):

    pdf = None

    if obs.GetName() == "TrueID":
        mean = WS(workspaceIn, RooConstVar("mean"+comp+"_"+mode+"_"+hypo+"Hypo",
                                           "mean"+comp+"_"+mode+"_"+hypo+"Hypo",
                                           myconfigfile["TrueID"][comp]))
        sigma = WS(workspaceIn, RooConstVar("sigma"+comp+"_"+mode+"_"+hypo+"Hypo",
                                            "sigma"+comp+"_"+mode+"_"+hypo+"Hypo",
                                            1.0))
        pdf = WS(workspaceIn, RooGaussian("TrueID_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                          "TrueID_"+comp+"_"+mode+"_"+hypo+"Hypo",
                                          obs, mean, sigma))
    else:
        print "ERROR: pdfs for observables "+obs.GetName()+" not yet implemented."
        exit(-1)

    return pdf

#-----------------------------------------------------------------------------
def BuildProtoData(workspaceIn, myconfigfile, obsDict, tagDict, resAccDict, pdfDict, debug):

    if "BeautyTime" not in obsDict.keys():
        return None
    
    #Ok, we have time observable. Let's see if we need per event mistag/time error
    nevts = pdfDict["Events"]
    protoDataDict = {}

    for hypo in myconfigfile["Hypothesys"]:
        protoDataDict[hypo] = {}

        for mode in myconfigfile["CharmModes"]:
            protoDataDict[hypo][mode] = {}

            for comp in myconfigfile["Components"].iterkeys():
                protoDataDict[hypo][mode][comp] = []
                atLeast = 0

                #Check tagging
                tag = 0
                if tagDict[comp]["MistagPDF"] != None:
                    for tagger in myconfigfile["Taggers"][comp].iterkeys():
                        if "Mistag"+tagger in obsDict.keys() and "TagDec"+tagger in obsDict.keys():
                            if debug:
                                print "Generate "+str(nevts[hypo][mode][comp])+" Mistag"+tagger+" proto data from "+tagDict[comp]["MistagPDF"][tag].GetName()
                            protoDataDict[hypo][mode][comp].append( tagDict[comp]["MistagPDF"][tag].generate( RooArgSet(obsDict["Mistag"+tagger]),
                                                                                                              nevts[hypo][mode][comp] ) )
                            protoDataDict[hypo][mode][comp][atLeast].SetName(protoDataDict[hypo][mode][comp][atLeast].GetName()+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                            protoDataDict[hypo][mode][comp][atLeast].SetTitle(protoDataDict[hypo][mode][comp][atLeast].GetName()+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                            protoDataDict[hypo][mode][comp][atLeast] = WS(workspaceIn, protoDataDict[hypo][mode][comp][atLeast])
                            
                            atLeast = atLeast+1
                            tag = tag+1
                            
                #Check per-event error
                if resAccDict[comp]["TimeErrorPDF"] != None:
                    if debug:
                        print "Generate "+str(nevts[hypo][mode][comp])+" per-event time error proto data from "+resAccDict[comp]["TimeErrorPDF"].GetName()
                    protoDataDict[hypo][mode][comp].append( resAccDict[comp]["TimeErrorPDF"].generate( RooArgSet(obsDict["BeautyTimeErr"]),
                                                                                                       nevts[hypo][mode][comp] ) )
                    protoDataDict[hypo][mode][comp][atLeast].SetName(protoDataDict[hypo][mode][comp][atLeast].GetName()+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                    protoDataDict[hypo][mode][comp][atLeast].SetTitle(protoDataDict[hypo][mode][comp][atLeast].GetName()+"_"+comp+"_"+mode+"_"+hypo+"Hypo")
                    protoDataDict[hypo][mode][comp][atLeast] = WS(workspaceIn, protoDataDict[hypo][mode][comp][atLeast])
                    
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

        for mode in myconfigfile["CharmModes"]:
            protoDataMerged[hypo][mode] = {}

            for comp in myconfigfile["Components"].iterkeys():
            
                if protoDataDict[hypo][mode][comp].__len__() > 0:
                    
                    protoDataMerged[hypo][mode][comp] = {}
                    countGenObs = 0
                
                    for data in protoDataDict[hypo][mode][comp]:
                        if countGenObs == 0:
                            protoDataMerged[hypo][mode][comp] = copy.deepcopy( protoDataDict[hypo][mode][comp][countGenObs] )
                        else:
                            protoDataMerged[hypo][mode][comp].merge( protoDataDict[hypo][mode][comp][countGenObs] )
                        countGenObs = countGenObs+1
                else:
                    protoDataMerged[hypo][mode] = None
                        
    if debug:
        print "Merged proto data dictionary:"
        print protoDataMerged

    return protoDataMerged

#-----------------------------------------------------------------------------
def GenerateToys(workspaceIn, myconfigfile, observables, pdfDict, protoData, debug):

    pdf = pdfDict["PDF"]
    nevts = pdfDict["Events"]

    toyDict = {}

    #Loop over bachelor mass hypotheses
    for hypo in myconfigfile["Hypothesys"]:
        print "Hypothesys: "+hypo
        toyDict[hypo] = {}
        #Loop over D decay modes
        for mode in myconfigfile["CharmModes"]:
            print "D decay mode: "+mode
            toyDict[hypo][mode] = {}
            #Loop over components
            for comp in myconfigfile["Components"].iterkeys():
                print "Components: "+comp
                toyDict[hypo][mode][comp] = {}
                #Loop over observables
                for obs in myconfigfile["Observables"].iterkeys():
                    if obs == "BeautyTime":
                        print "Observable: "+obs
                        toyDict[hypo][mode][comp][obs] = {}
                        genset = RooArgSet(observables.find(obs),
                                           observables.find("BacCharge"))
                        if "TagDecOS" in myconfigfile["Observables"].keys():
                            genset.add( observables.find("TagDecOS") )
                        if "TagDecSS" in myconfigfile["Observables"].keys():
                            genset.add( observables.find("TagDecSS") )
                        #If we have proto data use it, otherwise set number of events to generate
                        if None != protoData:
                            toyDict[hypo][mode][comp][obs] = WS(workspaceIn, pdf[hypo][mode][comp][obs].generate(genset,
                                                                                                                 RooFit.ProtoData(protoData[hypo][mode][comp]) ) )
                        else:
                            toyDict[hypo][mode][comp][obs] = WS(workspaceIn, pdf[hypo][mode][comp][obs].generate(genset,
                                                                                                                 RooFit.NumEvents(nevts[hypo][mode][comp]) ) )
                    elif obs in ["BeautyMass", "CharmMass", "BacPIDK", "TrueID"]:
                        print "Observable: "+obs
                        genset = RooArgSet(observables.find(obs))
                        toyDict[hypo][mode][comp][obs] = {}
                        toyDict[hypo][mode][comp][obs] = WS(workspaceIn, pdf[hypo][mode][comp][obs].generate(genset,
                                                                                                             RooFit.NumEvents(nevts[hypo][mode][comp]) ) )
                    

    if debug:
        print "Toy dictionary:"
        print toyDict

    return toyDict

#-----------------------------------------------------------------------------
def BuildTotalDataset(workspaceIn, myconfigfile, toyDict, debug):

    #Build category to identify sample
    sam = RooCategory("sample","sample")
    importList = []

    #Append all datasets for a given hypothesys, D decay mode
    foundObs = False
    for hypo in toyDict.iterkeys():

        print "Hypothesys: "+hypo

        for mode in toyDict[hypo].iterkeys():

            print "D decay mode: "+mode

            sam.defineType("both_"+mode+"_"+hypo+"Hypo")

            countComp = 0
            for comp in toyDict[hypo][mode].iterkeys():

                print "Component: "+comp
                
                countObs = 0
                for obs in toyDict[hypo][mode][comp].iterkeys():

                    print "Observable: "+obs
                    print "Entries "+str(toyDict[hypo][mode][comp][obs].sumEntries())
                    if countObs == 0:
                        dataObs = copy.deepcopy( toyDict[hypo][mode][comp][obs] )
                    else:
                        dataObs.merge( toyDict[hypo][mode][comp][obs] )

                    countObs = countObs +1

                if countComp == 0:
                    dataComp = copy.deepcopy( dataObs )
                else:
                    dataComp.append( dataObs )

                countComp = countComp + 1

            dataComp.SetName("both_"+mode+"_"+hypo+"Hypo")
            dataComp.SetTitle("both_"+mode+"_"+hypo+"Hypo")
            dataComp = WS(workspaceIn, dataComp)

            if not foundObs:
                #Use this dataset to retrieve list of observables
                observables = dataComp.get()
                foundObs = True

            importList.append( RooFit.Import("both_"+mode+"_"+hypo+"Hypo", dataComp) )

    #Build total dataset
    totData = WS(workspaceIn, RooDataSet("dataSet"+myconfigfile["Decay"]+"_both_"+mode,
                                          "dataSet"+myconfigfile["Decay"]+"_both_"+mode,
                                          observables,
                                          RooFit.Index(sam),
                                          *importList))

    if debug:
        print "Total dataset:"
        print totData.Print("v")

    return totData

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def toyFactory(configName,
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

    pdfDict = BuildTotalPDF(workspaceIn, myconfigfile, obsDict, ACPDict, tagDict, resAccDict, asymmDict, debug)

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
    protoData = BuildProtoData(workspaceIn, myconfigfile, obsDict, tagDict, resAccDict, pdfDict, debug) 

    #Generate toys
    toyDict = GenerateToys(workspaceIn, myconfigfile, observables, pdfDict, protoData, debug)

    print ""
    print "=========================================================="
    print "Toy generation done. Now merge/append datasets and"
    print "save them to file."
    print "=========================================================="
    print ""
    
    totData = BuildTotalDataset(workspaceIn, myconfigfile, toyDict, debug)
    observables = totData.get()
    workspaceOut = RooWorkspace(workOut, workOut)

    if debug:
        print "Output workspace "+workOut+" content:"
        workspaceOut.Print("v")

    if saveTree:
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

            for hypo in myconfigfile["Hypothesys"]:
                for mode in myconfigfile["CharmModes"]:
                    s = "nSig_both_"+mode+"_"+hypo+"Hypo_sw"
                    weight = WS(workspaceOut, RooRealVar(s, s, 1.0))
                    observables.add(weight)
                    totData.addColumn( weight )

        fileTree = TFile.Open(outputdir+treefileOut, "RECREATE")
        tree = totData.tree()
        tree.SetName( treeOut )
        tree.Write()
        fileTree.Close()

    totData = WS(workspaceOut, totData)
    observables = WS(workspaceOut, observables)

    print ""
    print "=========================================================="
    print "Save output workspace "+workOut+" to following file:"
    print outputdir+workfileOut
    print "=========================================================="
    print ""
    workspaceOut.writeToFile( outputdir+workfileOut )
    
#-----------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'MyConfigFile',
                   help = 'configuration file name'
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
               options.outputdir,
               options.workOut,
               options.workfileOut,
               options.treeOut,
               options.treefileOut,
               options.saveTree,
               options.debug)
