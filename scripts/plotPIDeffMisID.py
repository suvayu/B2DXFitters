#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78:expandtab
# --------------------------------------------------------------------------- 
# @file plotPIDeffMisID.py
#
# @brief Plot PID efficiency and misID as a function of a given variable
#
# @author Vincenzo Battista
# @date 2016-04-18
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
from B2DXFitters import utils
from optparse import OptionParser
from math     import pi, log
from  os.path import exists

import os, sys, gc

import numpy as n

import copy

import array
from array import array

gROOT.SetBatch(True)
gStyle.SetOptStat(0)

#-------------------------------------------------------------
def getDLLName(name, configfile):
    if "DLLK" in name:
        newname = name
        return name.replace("DLLK",configfile["PIDleafPrefix"]["DLLK"])
    else:
        print "ERROR: "+str(name)+" not (yet) handled. Feel free to edit!"
        exit(-1)

#-------------------------------------------------------------
def getLaTexName(name):
    if name == "Pi" or name == "pi":
        return "#pi"
    elif name == "K":
        return "K"
    elif name == "P" or name == "p":
        return "p"
    elif name == "e":
        return "e"
    elif name == "Mu" or name == "mu":
        return "#mu"
    else:
        print "ERROR: particle name "+name+" not handled!"
        exit(-1)

#-------------------------------------------------------------
def getMCKey(name):
    if name == "Pi" or name == "pi":
        return 211
    elif name == "K":
        return 321
    elif name == "P" or name == "p":
        return 2212
    elif name == "e":
        return 11
    elif name == "Mu" or name == "mu":
        return 13
    else:
        print "ERROR: particle name "+name+" not handled!"
        exit(-1)

#-------------------------------------------------------------
def makeLHCbLabel():
    lhcbtext = TLatex()
    lhcbtext.SetTextFont(132)
    lhcbtext.SetTextColor(1)
    lhcbtext.SetTextSize(0.07)
    lhcbtext.SetTextAlign(132)
    
    return lhcbtext

#-------------------------------------------------------------
def makePlot(var, rate, rateCalib, diff, distr, distrCalib, save):

    #Create canvas
    canv = TCanvas("canv_"+str(var),"canv_"+str(var),1200,1000)
    canv.Divide(1,2)

    #Set up upper pad
    canv.cd(1)
    pad1 = canv.GetPad(1)
    pad1.cd()
    pad1.SetPad(.0, .22, 0.95, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0)

    #if var == "P":
    #    pad1.SetLogx()

    pad1.cd()

    #Get maximum/minimum between MC and calib samples
    max = rate.GetMaximum()
    if rateCalib.GetMaximum() > max:
        max = rateCalib.GetMaximum()

    rate.GetYaxis().SetRangeUser(0.0,max*2.0)
    rateCalib.GetYaxis().SetRangeUser(0.0,max*2.0)

    #Plot rates
    rate.Draw("E1")
    rateCalib.Draw("E1SAME")
    pad1.Update()

    #Scale distribution histograms to match pad coordinates
    rightMax = 1.9*distr.GetMaximum()
    rightMaxCalib = 1.9*distrCalib.GetMaximum()
    scale = pad1.GetUymax()/rightMax
    distr.Scale( pad1.GetUymax() / (1.9*distr.GetMaximum()) )
    distrCalib.Scale( pad1.GetUymax() / (1.9*distrCalib.GetMaximum()) )

    #Plot distribution of var
    distr.Draw("E1SAME")
    distrCalib.Draw("E1SAME")

    #Build right axis
    rightAxis = TGaxis(pad1.GetUxmax(),
                       pad1.GetUymin(),
                       pad1.GetUxmax(),
                       pad1.GetUymax(),
                       0,
                       rightMax,
                       510,
                       "+L")
    rightAxis.SetTitle(distr.GetYaxis().GetTitle())
    rightAxis.SetTitleOffset(1.5)
    rightAxis.SetTitleSize(0.035)
    rightAxis.SetLabelOffset(0.006)
    rightAxis.SetLabelSize(0.035)
    rightAxis.SetTickSize(0.2)
    rightAxis.SetLineColor(kBlue)
    rightAxis.SetLabelColor(kBlue)
    rightAxis.SetTitleColor(kBlue)
    rightAxis.Draw()

    #Add legend
    legend = TLegend(0.45,0.55,0.9,0.9)
    legend.AddEntry(rate,rate.GetTitle(),"LP")
    legend.AddEntry(rateCalib,rateCalib.GetTitle(),"LP")
    legend.AddEntry(distr,distr.GetTitle(),"LP")
    legend.AddEntry(distrCalib,distrCalib.GetTitle(),"LP")
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.Draw("SAME")

    #Add LHCb label
    lhcbtext = makeLHCbLabel()
    lhcbtext.DrawTextNDC(0.3,0.8,"LHCb")

    #Update upper pad
    pad1.Update()
    pad1.Draw()

    #Set up lower pad
    canv.cd(2)
    pad2 = canv.GetPad(2)
    pad2.cd()
    pad2.SetPad(.0, .005, 0.95, .3275)
    pad2.cd()
    pad2.SetBorderMode(0)
    pad2.SetBorderSize(-1)
    pad2.SetFillStyle(0)
    pad2.SetBottomMargin(0.35)
    pad2.SetTickx(0)
    pad2.SetGridx()
    pad2.SetGridy()

    #if var == "P":
    #    pad2.SetLogx()

    #diff.GetYaxis().SetRangeUser(diff.GetMinimum(1e-03)*0.8,diff.GetMaximum()*1.2)
    diff.Draw("E1")

    pad2.Update()
    pad2.Draw()
    
    #Save final canvas
    canv.Update()
    canv.SaveAs(save)
    
#-------------------------------------------------------------
#-------------------------------------------------------------
#-------------------------------------------------------------
def plotPIDeffMisID(configName,
                    outputdir,
                    particle,
                    prefix,
                    label,
                    PIDcut,
                    nickname):

    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    #Take some names from config file
    inputfileMU = myconfigfile["Tuple"][particle]["FileMU"]
    inputfileMD = myconfigfile["Tuple"][particle]["FileMD"]
    inputtree = myconfigfile["Tuple"][particle]["Tree"]

    calibfileMU = myconfigfile["Calibration"][particle]["FileMU"]
    calibfileMD = myconfigfile["Calibration"][particle]["FileMD"]
    calibpass = myconfigfile["Calibration"][particle]["Passed"+str(PIDcut)]
    calibtot = myconfigfile["Calibration"][particle]["Total"+str(PIDcut)]

    print "=========================================================="
    print "PLOTPIDEFFMISID IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="

    print ""
    print "========================================="
    print "Get input tree "+str(inputtree)
    print "========================================="
    print ""

    inputTree = TChain(inputtree)
    inputTree.Add(inputfileMU)
    inputTree.Add(inputfileMD)

    print ""
    print "========================================="
    print "Get calibration histograms"
    print "========================================="
    print ""

    calibFileMU = TFile.Open(calibfileMU,"READ")
    calibPass = calibFileMU.Get(calibpass)
    calibTot = calibFileMU.Get(calibtot)
    calibPass.Sumw2()
    calibTot.Sumw2()
    
    calibFileMD = TFile.Open(calibfileMD,"READ")
    calibPassMD = calibFileMD.Get(calibpass)
    calibTotMD = calibFileMD.Get(calibtot)
    calibPassMD.Sumw2()
    calibTotMD.Sumw2()
    
    calibPass.Add(calibPassMD)
    calibTot.Add(calibTotMD)
        
    print ""
    print "========================================="
    print "Get binning"
    print "========================================="
    print ""

    binning = []
    for var in myconfigfile["Variables"].iterkeys():
        #Cast all to float
        bins = myconfigfile["Variables"][var]["Binning"]
        for b in range(0,bins.__len__()):
            bins[b] = float(bins[b])
        #Create proper numpy array
        binning += [ n.array( bins ) ]
    print binning
    
    print ""
    print "========================================="
    print "Compute efficiency/misID"
    print "========================================="
    print ""

    effHist = []
    effHistCalib = []
    diffHist = []
    varHist = []
    varHistCalib = []

    dllName = getDLLName(PIDcut, myconfigfile)
    pidCut = prefix + "_" + dllName

    idLeaf = prefix + "_TRUEID"

    titleP = getLaTexName(particle)
    
    idCut = "TMath::Abs("+idLeaf+")=="+str(getMCKey(particle))
    if "AdditionalCuts" in myconfigfile["Tuple"][particle].keys():
        idCut += " && " + myconfigfile["Tuple"][particle]["AdditionalCuts"] 

    v=0

    #Loop over variables to plot
    for var in myconfigfile["Variables"].iterkeys():

        print "Processing "+str(var)+"..."

        #Build histogram to be filled from input tuple
        if myconfigfile["Variables"][var]["Type"] == "D":
            histEff = TH1D("effHist_"+var,
                           titleP+" "+label+", "+str(PIDcut)+" (MC)",
                           len(binning[v])-1,
                           binning[v])
            histEffDen = TH1D("effHist_"+var+"_Den",
                              titleP+" "+label+", "+str(PIDcut)+" (MC)",
                              len(binning[v])-1,
                              binning[v])
            histDiff = TH1D("diffHist_"+var,
                            "",
                            len(binning[v])-1,
                            binning[v])
            histVar = TH1D("varHist_"+var,
                           titleP+" "+myconfigfile["Variables"][var]["Title"]+" (MC)",
                           len(binning[v])-1,
                           binning[v])
        else:
            histEff =  TH1F("effHist_"+var,
                            titleP+" "+label+", "+str(PIDcut)+" (MC)",
                            len(binning[v])-1,
                            binning[v])
            histEffDen = TH1F("effHist_"+var+"_Den",
                              titleP+" "+label+", "+str(PIDcut)+" (MC)",
                              len(binning[v])-1,
                              binning[v])
            histDiff = TH1F("diffHist_"+var,
                            "",
                            len(binning[v])-1,
                            binning[v])
            histVar = TH1F("varHist_"+var,
                           titleP+" "+myconfigfile["Variables"][var]["Title"]+" (MC)",
                           len(binning[v])-1,
                           binning[v])

        #Build histograms from calibration histograms (make projections)
        if "P" in var:
            histEffCalib = calibPass.ProjectionX(myconfigfile["Variables"][var]["Title"]+"_pass")
            calibTotPr = calibTot.ProjectionX(myconfigfile["Variables"][var]["Title"]+"_tot")
        elif "ETA" in var:
            histEffCalib = calibPass.ProjectionY(myconfigfile["Variables"][var]["Title"]+"_pass")
            calibTotPr = calibTot.ProjectionY(myconfigfile["Variables"][var]["Title"]+"_tot")
        elif "nTracks" in var:
            histEffCalib = calibPass.ProjectionZ(myconfigfile["Variables"][var]["Title"]+"_pass")
            calibTotPr = calibTot.ProjectionZ(myconfigfile["Variables"][var]["Title"]+"_tot")

        histEffCalib.Sumw2()
        calibTotPr.Sumw2()

        histVarCalib = copy.deepcopy(calibTotPr)

        histEffCalib.Divide(calibTotPr)
        histEffCalib.SetTitle(titleP+" "+label+", "+str(PIDcut)+" (Calibration)")

        histVarCalib.SetTitle(titleP+" "+myconfigfile["Variables"][var]["Title"]+" (Calibration)")
        
        #Set axes titles
        histEff.GetXaxis().SetTitle(myconfigfile["Variables"][var]["Title"])
        histEff.GetYaxis().SetTitle(titleP+" "+label)

        histEffCalib.GetXaxis().SetTitle(myconfigfile["Variables"][var]["Title"])
        histEffCalib.GetYaxis().SetTitle(titleP+" "+label)

        histDiff.GetXaxis().SetTitle(myconfigfile["Variables"][var]["Title"])
        histDiff.GetYaxis().SetTitle("Pulls")

        histVar.GetXaxis().SetTitle(myconfigfile["Variables"][var]["Title"])
        histVar.GetYaxis().SetTitle("Events")

        histVarCalib.GetXaxis().SetTitle(myconfigfile["Variables"][var]["Title"])
        histVarCalib.GetYaxis().SetTitle("Events")
        
        #Some other cosmetics
        histEff.SetLineColor(kGreen+2)
        histEff.SetMarkerColor(kGreen+2)
        histEff.SetLineWidth(2)
        histEff.GetXaxis().SetLabelSize( 0.0 )
        histEff.GetYaxis().SetLabelSize( 0.035 )
        histEff.GetXaxis().SetLabelOffset( 0.0 )
        histEff.GetYaxis().SetLabelOffset( 0.006 )
        histEff.GetXaxis().SetTitleSize( 0.0 )
        histEff.GetYaxis().SetTitleSize( 0.035 )
        histEff.GetXaxis().SetTitleOffset( 0.0 )
        histEff.GetYaxis().SetTitleOffset( 1.2 )
        
        histEffCalib.SetLineColor(kRed)
        histEffCalib.SetMarkerColor(kRed)
        histEffCalib.SetLineWidth(2)
        histEffCalib.GetXaxis().SetLabelSize( 0.0 )
        histEffCalib.GetYaxis().SetLabelSize( 0.035 )
        histEffCalib.GetXaxis().SetLabelOffset( 0.0 )
        histEffCalib.GetYaxis().SetLabelOffset( 0.006 )
        histEffCalib.GetXaxis().SetTitleSize( 0.0 )
        histEffCalib.GetYaxis().SetTitleSize( 0.035 )
        histEffCalib.GetXaxis().SetTitleOffset( 0.0 )
        histEffCalib.GetYaxis().SetTitleOffset( 1.2 )

        histDiff.SetLineColor(kBlack)
        histDiff.SetMarkerColor(kBlack)
        histDiff.SetLineWidth(2)
        histDiff.GetXaxis().SetLabelSize( 0.085 )
        histDiff.GetYaxis().SetLabelSize( 0.085 )
        histDiff.GetXaxis().SetLabelOffset( 0.006 )
        histDiff.GetYaxis().SetLabelOffset( 0.006 )
        histDiff.GetXaxis().SetTitleSize( 0.085 )
        histDiff.GetYaxis().SetTitleSize( 0.085 )
        histDiff.GetXaxis().SetTitleOffset( 1.2 )
        histDiff.GetYaxis().SetTitleOffset( 1.2 )
        histDiff.GetYaxis().SetNdivisions(5)

        histVar.SetLineColor(kBlue)
        histVar.SetMarkerColor(kBlue)
        histVar.SetLineWidth(2)
        histVar.GetXaxis().SetLabelSize( 0.0 )
        histVar.GetYaxis().SetLabelSize( 0.035 )
        histVar.GetXaxis().SetLabelOffset( 0.0 )
        histVar.GetYaxis().SetLabelOffset( 0.006 )
        histVar.GetXaxis().SetTitleSize( 0.0 )
        histVar.GetYaxis().SetTitleSize( 0.035 )
        histVar.GetXaxis().SetTitleOffset( 0.0 )
        histVar.GetYaxis().SetTitleOffset( 1.2 )

        histVarCalib.SetLineColor(kBlack)
        histVarCalib.SetMarkerColor(kBlack)
        histVarCalib.SetLineWidth(2)
        histVarCalib.GetXaxis().SetLabelSize( 0.0 )
        histVarCalib.GetYaxis().SetLabelSize( 0.035 )
        histVarCalib.GetXaxis().SetLabelOffset( 0.0 )
        histVarCalib.GetYaxis().SetLabelOffset( 0.006 )
        histVarCalib.GetXaxis().SetTitleSize( 0.0 )
        histVarCalib.GetYaxis().SetTitleSize( 0.035 )
        histVarCalib.GetXaxis().SetTitleOffset( 0.0 )
        histVarCalib.GetYaxis().SetTitleOffset( 1.2 )
                                                                                
        #Handle error propagation
        histEff.Sumw2()
        histEffDen.Sumw2()
        histEffCalib.Sumw2()

        histDiff.Sumw2()

        histVar.Sumw2()

        histVarCalib.Sumw2()
        
        #Filling histograms
        if "nTracks" in var:
            varLeaf = myconfigfile["Variables"][var]["Suffix"]
        else:
            varLeaf = prefix + "_" + myconfigfile["Variables"][var]["Suffix"]
        
        print "...building efficiency/Mis-ID"
        print "=>Passed cut:"
        print pidCut+"&&"+idCut
        print "=>Total cut:"
        print idCut
        inputTree.Draw(varLeaf+">>"+histEff.GetName(),
                       pidCut+"&&"+idCut,
                       "goff")
        print "=>Passed entries:"
        print histEff.GetEntries()
        inputTree.Draw(varLeaf+">>"+histEffDen.GetName(),
                       idCut,
                       "goff")
        print "=>Total entries:"
        print histEffDen.GetEntries()
        histEff.Divide(histEffDen)
        #
        print "...building difference histogram"
        histDiff.Divide(histEff,histEffCalib,1.0,1.0)
        #
        print "...building variable distribution"
        inputTree.Draw(varLeaf+">>"+histVar.GetName(),
                       "",
                       "goff")

        histEff.GetXaxis().SetRangeUser(myconfigfile["Variables"][var]["Min"],
                                        myconfigfile["Variables"][var]["Max"])
        histEffCalib.GetXaxis().SetRangeUser(myconfigfile["Variables"][var]["Min"],
                                             myconfigfile["Variables"][var]["Max"])
        histDiff.GetXaxis().SetRangeUser(myconfigfile["Variables"][var]["Min"],
                                         myconfigfile["Variables"][var]["Max"])
        histVar.GetXaxis().SetRangeUser(myconfigfile["Variables"][var]["Min"],
                                        myconfigfile["Variables"][var]["Max"])
        histVarCalib.GetXaxis().SetRangeUser(myconfigfile["Variables"][var]["Min"],
                                             myconfigfile["Variables"][var]["Max"])
        
        effHist += [ histEff ]
        effHistCalib += [ histEffCalib ]
        diffHist += [ histDiff ]
        varHist += [ histVar ]
        varHistCalib += [ histVarCalib ]

        v = v + 1

    print "!!Loop finished!!"

    print ""
    print "========================================="
    print "Make plots"
    print "========================================="
    print ""

    v=0

    for var in myconfigfile["Variables"].iterkeys():

        #Set ranges
        minRange = myconfigfile["Variables"][var]["Min"]
        maxRange = myconfigfile["Variables"][var]["Max"]
        print "Setting histograms range from "+str(minRange)+" to "+str(maxRange)
        
        effHist[v].GetXaxis().SetRangeUser(minRange,maxRange)
        effHistCalib[v].GetXaxis().SetRangeUser(minRange,maxRange)
        diffHist[v].GetXaxis().SetRangeUser(minRange,maxRange)
        varHist[v].GetXaxis().SetRangeUser(minRange,maxRange)
        varHistCalib[v].GetXaxis().SetRangeUser(minRange,maxRange)

        #Do plot
        makePlot(var, effHist[v], effHistCalib[v], diffHist[v], varHist[v], varHistCalib[v], outputdir+nickname+"_"+var+".pdf")
        
        v = v + 1


#-------------------------------------------------------------

_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'MyConfigFile',
                   help = 'configuration file name'
                   )
parser.add_option( '--outputdir',
                   dest = 'outputdir',
                   default = 'MyOutputDir',
                   help = 'output directory to store plot(s)'
                   )
parser.add_option( '--particle',
                   dest = 'particle',
                   default = 'Pi',
                   help = 'particle to compute the efficiency/Mis-ID rate for (Pi,K,P,e,Mu)'
                   )
parser.add_option( '--prefix',
                   dest = 'prefix',
                   default = 'lab1',
                   help = 'name prefix used in the input tuple to identify the particle (lab1,lab2...)'
                   )
parser.add_option( '--label',
                   dest = 'label',
                   default = 'Efficiency',
                   help = 'label for histograms'
                   )
parser.add_option( '--PIDcut',
                   dest = 'PIDcut',
                   default = 'DLLK>5.0',
                   help = 'cut on PID'
                   )
parser.add_option( '--nickname',
                   dest = 'nickname',
                   default = 'MyWonderfulPlot',
                   help = 'label to identify plots in output file'
                   )

#-------------------------------------------------------------
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

    plotPIDeffMisID(configName,
                    options.outputdir,
                    options.particle,
                    options.prefix,
                    options.label,
                    options.PIDcut,
                    options.nickname)
