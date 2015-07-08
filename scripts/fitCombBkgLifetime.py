#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# ---------------------------------------------------------------------------
# @file runBs2DsKCPAsymmObsFitter-cFit.py
#
# Python script to run a data or toy MC fit for the CP asymmetry observables
# in Bs -> Ds K
# with the FitMeTool fitter
#
# cFit stands either for "complex" fit (in constrast to the sWeighted fit) or
# for Cleese fit - you pick
#
# Author: Eduardo Rodrigues
# Date  : 14 / 06 / 2011
#
# @author Manuel Schiller
# @date 2012-02-15 ... ongoing
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

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
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
import B2DXFitters
import ROOT
from ROOT import RooFit
from optparse import OptionParser
from math import pi, log
import os, sys, gc

import ROOT
from ROOT import *
from ROOT import (RooArgSet, RooArgList, RooBDecay, RooRealVar, RooConstVar,
        RooGaussModel, RooGaussian, RooGaussEfficiencyModel, RooTruthModel,
        RooEffProd, RooNumConvPdf, RooWorkspace, RooAbsReal, Inverse)
from B2DXFitters.WS import WS as WS
from B2DXFitters.FitResult import FitResult
from ROOT import (TFile, TCanvas, gROOT, TLegend, RooAbsReal, gStyle, gPad,
        TLine, TColor, TLatex, TString, RooPlot, TLatex)
gROOT.SetBatch( True )

gROOT.SetStyle('Plain')
gStyle.SetOptTitle(0)
gStyle.SetLabelFont(132, 'XYZ ')
gStyle.SetLabelFont(132)
gStyle.SetTitleFont(132, 'XYZ ')
gStyle.SetTitleFont(132)
gStyle.SetTextFont(132)
gStyle.SetStatFont(132)
gStyle.SetLabelSize(0.06, 'XYZ ')
gStyle.SetLabelSize(0.06)
gStyle.SetTitleSize(0.06, 'XYZ ')
gStyle.SetTitleSize(0.06)
gStyle.SetLabelOffset(0.004, 'XYZ ')
gStyle.SetTitleOffset(0.85, 'XYZ ')

RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')

isDsK = True
BDTGRange =    (0.3, 1.0)
MassRange =    (5700., 10000.)
TimeRange =    (0.4, 15.0) if (0.9, 1.0) != BDTGRange else (0.75, 15.0)
TimeErrRange = (0.01, 0.1)

knots = {
        (0.3, 1.0): [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
        #(0.3, 1.0): [0.5, 1.0, 1.5, 2.0, 3.0, 6.0, 8.0, 12.0],
        (0.6, 1.0): [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
        (0.3, 0.9): [ 0.5, 1.0, 1.5, 2.0, 3.0, 6.0, 11.0 ],
        (0.9, 1.0): [ 0.8, 1.0, 1.5, 2.0, 3.0, 6.0, 11.0, 14.0 ],
        }
coeffs = {
        True: { # DsK
            (0.3, 1.0): [
                4.5853e-01 * 4.97708e-01 / 5.12341e-01,
                6.8963e-01 * 7.42075e-01 / 7.44868e-01,
                8.8528e-01 * 9.80824e-01 / 9.95795e-01,
                1.1296e+00 * 1.16280e+00 / 1.13071e+00,
                1.2232e+00 * 1.24252e+00 / 1.23135e+00,
                1.2277e+00 * 1.28482e+00 / 1.22716e+00],
            (0.3, 1.0, 'polDN'): [
                4.5425e-01*4.97697e-01/5.12401e-01,
                6.8673e-01*7.42054e-01/7.44978e-01,
                8.7719e-01*9.80802e-01/9.95897e-01,
                1.0862e+00*1.16277e+00/1.13078e+00,
                1.2086e+00*1.24250e+00/1.23145e+00,
                1.1947e+00*1.28479e+00/1.22712e+00],
            (0.3, 1.0, 'polUP'): [
                4.6527e-01*4.97720e-01/5.12293e-01,
                6.9241e-01*7.42098e-01/7.44813e-01,
                8.9786e-01*9.80916e-01/9.95873e-01,
                1.1926e+00*1.16282e+00/1.13075e+00,
                1.2458e+00*1.24262e+00/1.23141e+00,
                1.2725e+00*1.28498e+00/1.22721e+00],
            (0.3, 1.0, 'TOS0'): [
                2.7277e-01*3.10195e-01/3.44103e-01,
                4.5649e-01*5.22722e-01/5.78459e-01,
                7.6173e-01*7.93059e-01/9.12020e-01,
                9.6421e-01*1.03609e+00/1.06310e+00,
                1.1212e+00*1.13156e+00/1.23382e+00,
                9.4807e-01*1.19290e+00/1.31359e+00],
                #2.9997e-01*3.02185e-01/3.61224e-01,
                #5.0033e-01*5.11076e-01/6.07496e-01,
                #8.4690e-01*7.63164e-01/9.54767e-01,
                #1.0488e+00*1.01953e+00/1.11678e+00,
                #1.2603e+00*1.07163e+00/1.28539e+00,
                #1.1126e+00*1.18135e+00/1.34230e+00,
                #1.0871e+00*1.02446e+00/1.23216e+00,
                #1.2774e+00*1.01330e+00/1.16013e+00],
            (0.3, 1.0, 'TOS1'): [
                6.0532e-01*6.07184e-01/5.88340e-01,
                8.7407e-01*8.71243e-01/8.19533e-01,
                9.6359e-01*1.09075e+00/1.03414e+00,
                1.2367e+00*1.23945e+00/1.16105e+00,
                1.2781e+00*1.30903e+00/1.23029e+00,
                1.4263e+00*1.34331e+00/1.18806e+00],
                #6.0711e-01*6.51148e-01/6.16359e-01,
                #8.7811e-01*9.33545e-01/8.58522e-01,
                #9.6139e-01*1.17116e+00/1.08197e+00,
                #1.2474e+00*1.32387e+00/1.21527e+00,
                #1.2673e+00*1.40665e+00/1.28334e+00,
                #1.3662e+00*1.39846e+00/1.27061e+00,
                #1.3101e+00*1.34481e+00/1.17796e+00,
                #9.6036e-01*1.13261e+00/1.11268e+00],
            (0.6, 1.0): [
                3.5803e-01 * 3.97923e-01 / 4.20221e-01,
                5.6367e-01 * 6.14977e-01 / 6.34584e-01,
                7.6889e-01 * 8.69428e-01 / 8.99565e-01,
                1.0537e+00 * 1.11080e+00 / 1.09470e+00,
                1.2016e+00 * 1.22906e+00 / 1.22355e+00,
                1.2320e+00 * 1.30468e+00 / 1.25746e+00],
            (0.3, 0.9): [
                1.6635e+00 * 2.47462e+00 / 2.47125e+00,
                2.3178e+00 * 3.39595e+00 / 3.23980e+00,
                2.4961e+00 * 3.47102e+00 / 3.40202e+00,
                2.4930e+00 * 3.18153e+00 / 2.97477e+00,
                2.0711e+00 * 2.44019e+00 / 2.38706e+00,
                1.3281e+00 * 1.22369e+00 / 1.32258e+00,
                1.0422e+00 * 1.01064e+00 / 1.03833e+00],
            (0.9, 1.0): [
                3.4120e-01 * 3.01689e-01 / 3.49186e-01,
                3.8462e-01 * 3.78774e-01 / 4.38532e-01,
                5.4789e-01 * 5.49996e-01 / 6.34382e-01,
                9.5219e-01 * 8.39685e-01 / 9.05328e-01,
                1.2997e+00 * 1.10835e+00 / 1.20857e+00,
                1.6461e+00 * 1.48437e+00 / 1.52741e+00,
                1.6076e+00 * 1.34585e+00 / 1.42235e+00,
                1.4345e+00 * 1.12627e+00 / 1.29029e+00],
            },
        False: { #DsPi
            (0.3, 1.0): [
                4.5853e-01, 6.8963e-01, 8.8528e-01,
                1.1296e+00, 1.2232e+00, 1.2277e+00],
            (0.3, 1.0, 'polDN'): [
                4.5425e-01, 6.8673e-01, 8.7719e-01,
                1.0862e+00, 1.2086e+00, 1.1947e+00],
            (0.3, 1.0, 'polUP'): [
                4.6527e-01, 6.9241e-01, 8.9786e-01,
                1.1926e+00, 1.2458e+00, 1.2725e+00],
            (0.3, 1.0, 'TOS0'): [
                2.7277e-01, 4.5649e-01, 7.6173e-01,
                9.6421e-01, 1.1212e+00, 9.4807e-01],
            (0.3, 1.0, 'TOS1'): [
                6.0532e-01, 8.7407e-01, 9.6359e-01,
                1.2367e+00, 1.2781e+00, 1.4263e+00],
            (0.6, 1.0): [
                3.5803e-01, 5.6367e-01, 7.6889e-01,
                1.0537e+00, 1.2016e+00, 1.2320e+00],
            (0.3, 0.9): [
                1.6635e+00, 2.3178e+00, 2.4961e+00, 2.4930e+00,
                2.0711e+00, 1.3281e+00, 1.0422e+00],
            (0.9, 1.0): [
                3.4120e-01, 3.8462e-01, 5.4789e-01, 9.5219e-01,
                1.2997e+00, 1.6461e+00, 1.6076e+00, 1.4345e+00],
            },
        }

timeConv = 1e9 / 2.99792458e8

files = ([ '/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_MD_OFFLINE_DsK.root',
           '/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_MU_OFFLINE_DsK.root'
          ] if isDsK else
          [ '/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_MD_OFFLINE_DsPi.root',
            '/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_MU_OFFLINE_DsPi.root' ])
extracuts = '1'
if len(BDTGRange) == 3:
    if 'polUP' == BDTGRange[2]:
        extracuts = '+1 == Polarity'
    elif 'polDN' == BDTGRange[2]:
        extracuts = '-1 == Polarity'
    elif 'TOS0' == BDTGRange[2]:
        extracuts = '0 == lab0_L0HadronDecision_TOS'
    elif 'TOS1' == BDTGRange[2]:
        extracuts = '1 == lab0_L0HadronDecision_TOS'

cuts = ('%24.16e <= lab0_MassFitConsD_M[0] && lab0_MassFitConsD_M[0] <= %24.16e && '
        '%s && %24.16e <= BDTGResponse_1 && BDTGResponse_1 <= %24.16e && '
        'lab1_P > 3e3 && lab1_P < 650e3 && lab2_MM > 1930. && lab2_MM < 2015. && '
        'lab1_PT > 400. && lab1_PT < 45e3 && nTracks > 15. && '
        'nTracks < 1000. && lab2_TAU > 0. && '
        '%24.16e <= lab0_LifetimeFit_ctau[0] && lab0_LifetimeFit_ctau[0] <= %24.16e &&'
        '%24.16e <= lab0_LifetimeFit_ctauErr[0] && lab0_LifetimeFit_ctauErr[0] <= %24.16e &&'
        'lab1_ID*lab2_ID < 0 && %s && '
        '((1e-2*lab3_ID) * (1e-2*lab4_ID) * (1e-2*lab5_ID) * (1e-2*lab1_ID) > 0)' %
        (MassRange[0], MassRange[1], 'lab1_PIDK > 5' if isDsK else
        'lab1_PIDK < 0', BDTGRange[0], BDTGRange[1],
        TimeRange[0] / timeConv, TimeRange[1] / timeConv,
        TimeErrRange[0] / timeConv, TimeErrRange[1] / timeConv,
        extracuts))

def getDataSet(ws, cuts, files):
    from ROOT import TChain, TTree
    import ctypes
    c = TChain('DecayTree')
    for fname in files:
        print 'DEBUG: ADDING FILE %s' % fname
        c.AddFile(fname)
    print 'DEBUG: CUTS: %s' % cuts
    t = c.CopyTree(cuts)
    ROOT.SetOwnership(t, True)
    del c
    print 'DEBUG: ENTRIES AFTER APPLYING CUTS: %u' % t.GetEntries()
    time = ws.var('time')
    timeerr = ws.var('timeerr')
    ds = WS(ws, RooDataSet('ds', 'ds', RooArgSet(time, timeerr)), [])
    for i in xrange(0, t.GetEntries()):
        t.GetEntry(i)
        variables = [ timeConv * t.GetBranch(name).GetLeaf(name).GetValue(0) for name in
                ('lab0_LifetimeFit_ctau', 'lab0_LifetimeFit_ctauErr') ]
        time.setVal(variables[0])
        timeerr.setVal(variables[1])
        ds.add(RooArgSet(time, timeerr))
    del t
    ds.Print('v')
    return ds

def accbuilder(time, knots, coeffs):
    # build acceptance function
    from copy import deepcopy
    myknots = deepcopy(knots)
    mycoeffs = deepcopy(coeffs)
    from ROOT import (RooBinning, RooArgList, RooPolyVar,
            RooCubicSplineFun)
    if (len(myknots) != len(mycoeffs) or 0 >= min(len(myknots), len(mycoeffs))):
        raise ValueError('ERROR: Spline knot position list and/or coefficient'
                'list mismatch')
    # create the knot binning
    knotbinning = WS(ws, RooBinning(time.getMin(), time.getMax(), 'knotbinning'))
    for v in myknots:
        knotbinning.addBoundary(v)
    knotbinning.removeBoundary(time.getMin())
    knotbinning.removeBoundary(time.getMax())
    knotbinning.removeBoundary(time.getMin())
    knotbinning.removeBoundary(time.getMax())
    oldbinning, lo, hi = time.getBinning(), time.getMin(), time.getMax()
    time.setBinning(knotbinning, 'knotbinning')
    time.setBinning(oldbinning)
    time.setRange(lo, hi)
    del knotbinning
    del oldbinning
    del lo
    del hi
    # create the knot coefficients
    coefflist = RooArgList()
    i = 0
    for v in mycoeffs:
        coefflist.add(WS(ws, RooRealVar('SplineAccCoeff%u' % i,
            'SplineAccCoeff%u' % i, v)))
        i = i + 1
    del mycoeffs
    coefflist.add(one)
    i = i + 1
    myknots.append(time.getMax())
    myknots.reverse()
    fudge = (myknots[0] - myknots[1]) / (myknots[2] - myknots[1])
    lastmycoeffs = RooArgList(
            WS(ws, RooConstVar('SplineAccCoeff%u_coeff0' % i,
                'SplineAccCoeff%u_coeff0' % i, 1. - fudge)),
            WS(ws, RooConstVar('SplineAccCoeff%u_coeff1' % i,
                'SplineAccCoeff%u_coeff1' % i, fudge)))
    del myknots
    coefflist.add(WS(ws, RooPolyVar(
        'SplineAccCoeff%u' % i, 'SplineAccCoeff%u' % i,
        coefflist.at(coefflist.getSize() - 2), lastmycoeffs)))
    del i
    # create the spline itself
    tacc = WS(ws, RooCubicSplineFun('SplineAcceptance', 'SplineAcceptance', time,
        'knotbinning', coefflist))
    del lastmycoeffs
    # make sure the acceptance is <= 1 for generation
    m = max([coefflist.at(j).getVal() for j in
        xrange(0, coefflist.getSize())])
    from ROOT import RooProduct
    c = WS(ws, RooConstVar('SplineAccNormCoeff', 'SplineAccNormCoeff', 0.99 / m))
    tacc_norm = WS(ws, RooProduct('SplineAcceptanceNormalised',
        'SplineAcceptanceNormalised', RooArgList(tacc, c)))
    del c
    del m
    del coefflist
    return tacc, tacc_norm

results = []
for tag in xrange(0, 4):
    ws = RooWorkspace('ws')

    gamma =         WS(ws, RooRealVar('Gamma',      'Gamma',        1.0, 0.1, 2.5))
    dGamma =        WS(ws, RooRealVar('dGamma',     'dGamma',       0.5, 0.0, 2.5))
    SF =            WS(ws, RooConstVar('SF',        'SF',           1.37))
    tau = WS(ws, Inverse('tau', 'tau', gamma))

    one =           WS(ws, RooConstVar('one',      'one',          1.))
    zero =          WS(ws, RooConstVar('zero',     'zero',         0.))

    # observable
    time = WS(ws, RooRealVar('time', '#tau(combinatorial) [ps]', *TimeRange))
    timeerr = WS(ws, RooRealVar('timeerr', 'timeerr', *TimeErrRange))

    tacc, tacc_norm = accbuilder(time, knots[BDTGRange[0:2]], coeffs[isDsK][BDTGRange])

    ds = getDataSet(ws,
            '%s && %u == abs(lab0_TAGDECISION_OS) && '
            '%u == abs(lab0_SS_nnetKaon_DEC)' % (
                cuts, 1 if 1 == (tag % 2) else 0, 1 if 1 == (tag / 2) else 0),
            files)

    fr = time.frame()
    ds.plotOn(fr)
    fr.Draw()
    gPad.SetMargin(0.15, 0.1, 0.15, 0.1)

    # build simple fitter - fit D
    # build pdf for fitting the usual way:
    # - first apply decay time resolution smearing
    # - then, apply acceptance
    D = WS(ws, RooRealVar('D', 'D', 0., -1., 1.))

    if (0.9, 1.0) == BDTGRange:
        # single gaussian for DsK for BDTG in [0.9, 1.0] because there's virtually
        # no events there
        D.setConstant(True)
        dGamma.setVal(0.)
        dGamma.setConstant(True)

    fit_resmodel = WS(ws, RooGaussEfficiencyModel(
        'fit_resmodel', 'fit_resmodel', time, tacc, zero, timeerr, SF, SF))
    fit_pdf = WS(ws, RooBDecay('fit_pdf', 'fit_pdf',
        time, tau, dGamma, one, D, zero, zero, zero, fit_resmodel,
        RooBDecay.SingleSided))

    # ok, fit back
    timeerrargset = RooArgSet(timeerr)
    if not ((0.9, 1.0) == BDTGRange):
        for i in xrange(0, 3):
            # single Gaussian first
            for v in (D, dGamma): v.setConstant(True)
            fit_pdf.fitTo(ds, RooFit.Timer(), RooFit.Verbose(), RooFit.Strategy(2),
                    RooFit.Optimize(2), RooFit.Offset(), RooFit.Save(),
                    RooFit.ConditionalObservables(timeerrargset))
            # ok, fix gamma, release D, dGamma
            for v in (D, dGamma): v.setConstant(False)
            gamma.setConstant(True)
            fit_pdf.fitTo(ds, RooFit.Timer(), RooFit.Verbose(), RooFit.Strategy(2),
                    RooFit.Optimize(2), RooFit.Offset(), RooFit.Save(),
                    RooFit.ConditionalObservables(timeerrargset))
    # release everything and fit
    if not ((0.9, 1.0) == BDTGRange):
        for v in (D, dGamma, gamma): v.setConstant(False)
    result = fit_pdf.fitTo(ds, RooFit.Timer(), RooFit.Verbose(), RooFit.Strategy(2),
            RooFit.Optimize(2), RooFit.Offset(), RooFit.Save(),
            RooFit.ConditionalObservables(timeerrargset))
    results.append(FitResult(result))
    fit_pdf.plotOn(fr, RooFit.ProjWData(timeerrargset, ds, True))
    fr.Draw()
    ROOT.gPad.SetLogy()
    tl1 = TLatex(0.65, 0.8, "LHCb")
    tl1.SetTextFont(132)
    tl1.SetTextSize(0.08)
    tl1.SetNDC(True)
    tl1.Draw()
    tagdict = { 0: 'untagged events', 1: 'OS only events',
            2: 'SSK only events', 3: 'OS+SSK events' }
    tl2 = TLatex(0.65, 0.75, tagdict[tag])
    tl2.SetTextFont(132)
    tl2.SetTextSize(0.06)
    tl2.SetNDC(True)
    tl2.Draw()
    gPad.Update()
    for ext in ('pdf', 'root'):
        ROOT.gPad.Print('CombBkgLifetimeFit_%s%s_BDTG%g-%g-TAG%u.%s' % (
            ('DsK' if isDsK else 'DsPi'),
            ('' if 2 == len(BDTGRange) else ('_%s' % BDTGRange[2])),
            BDTGRange[0], BDTGRange[1], tag, ext))
    del ws

for i in xrange(0, len(results)):
    print 72 * '*'
    print 'COMBINATORIAL LIFETIME FIT FOR TAG = %u' % i
    print 72 * '*'
    print results[i]
    print

# print out cFit friendly options
print 72 * '*'
print 'OPTIONS FOR CFIT CONFIG'
print 72 * '*'
print '\'GammaCombBkg\': %s,' % str([results[i].params()['Gamma'] for  i in xrange(0, len(results))])
print '\'DGammaCombBkg\': %s,' % str([results[i].params()['dGamma'] for  i in xrange(0, len(results))])
print '\'CombBkg_D\': %s,' % str([results[i].params()['D'] for  i in xrange(0, len(results))])
print '\'Constraints\': {'
for i in xrange(0, len(results)):
    print '\t\'multivar_CombBkg%uLifetime\': [' % i
    print '\t    [ \'CombBkg%u_D\', \'GammaCombBkg%u\', \'DeltaGammaCombBkg%u\' ],' % (i, i, i)
    print '\t    %s,' % str([ results[i].errors()[n] for n in [ 'D', 'Gamma', 'dGamma'] ])
    print '\t    [ %s,' % str([ results[i].correl()['D'][n] for n in [ 'D', 'Gamma', 'dGamma'] ])
    print '\t      %s,' % str([ results[i].correl()['Gamma'][n] for n in [ 'D', 'Gamma', 'dGamma'] ])
    print '\t      %s, ],' % str([ results[i].correl()['dGamma'][n] for n in [ 'D', 'Gamma', 'dGamma'] ])
    print '\t    ],'
print '},'
print
