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
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')

ws = RooWorkspace('ws')

gamma =         WS(ws, RooRealVar('Gamma',      'Gamma',        1.0, 0.1, 2.5))
dGamma =        WS(ws, RooRealVar('dGamma',     'dGamma',       0.5, -2.0, 2.0))
SF =            WS(ws, RooConstVar('SF',        'SF',           1.37))
tau = WS(ws, Inverse('tau', 'tau', gamma))

isDsK = True
BDTGRange =    (0.3, 1.0)
MassRange =    (5700., 10000.)
TimeRange =    (0.4, 15.0) if (0.9, 1.0) != BDTGRange else (0.75, 15.0)
TimeErrRange = (0.01, 0.1)

knots = {
        (0.3, 1.0): [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
        (0.6, 1.0): [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
        (0.3, 0.9): [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
        (0.9, 1.0): [ 0.8, 1.0, 1.5, 2.0, 3.0, 12.0 ],
        }
coeffs = {
        True: { # DsK
            (0.3, 1.0): [
                4.5832e-01*5.03902e-01/5.26256e-01,
                6.8898e-01*7.32741e-01/7.40768e-01,
                8.8522e-01*9.98736e-01/1.02107e+00,
                1.1292e+00*1.16514e+00/1.13483e+00,
                1.2233e+00*1.25167e+00/1.24545e+00,
                1.2277e+00*1.28624e+00/1.23243e+00],
            (0.6, 1.0): [
                3.5794e-01*4.02721e-01/4.31571e-01,
                5.6367e-01*6.07470e-01/6.32075e-01,
                7.6897e-01*8.85530e-01/9.22715e-01,
                1.0536e+00*1.11358e+00/1.10114e+00,
                1.2016e+00*1.23842e+00/1.23988e+00,
                1.2326e+00*1.30685e+00/1.26593e+00],
            (0.3, 0.9): [
                1.6193e+00*2.12678e+00/2.17377e+00,
                2.2657e+00*2.86635e+00/2.78740e+00,
                2.4050e+00*2.94977e+00/2.96311e+00,
                2.4591e+00*2.76718e+00/2.59706e+00,
                1.9576e+00*1.99964e+00/2.01983e+00,
                6.5246e-01*1.93623e-01/3.67405e-01],
            (0.9, 1.0): [
                2.4916e-01*2.78114e-01/2.96063e-01,
                2.7606e-01*3.23047e-01/3.43090e-01,
                4.0406e-01*5.18790e-01/5.45970e-01,
                6.8334e-01*7.33678e-01/7.37678e-01,
                9.6386e-01*1.03067e+00/1.02475e+00,
                1.4528e+00*1.57981e+00/1.47536e+00],
            },
        False: { #DsPi
            (0.3, 1.0): [
                4.5832e-01, 6.8898e-01, 8.8522e-01,
                1.1292e+00, 1.2233e+00, 1.2277e+00],
            (0.6, 1.0): [
                3.5794e-01, 5.6367e-01, 7.6897e-01,
                1.0536e+00, 1.2016e+00, 1.2326e+00],
            (0.3, 0.9): [
                1.6193e+00, 2.2657e+00, 2.4050e+00,
                2.4591e+00, 1.9576e+00, 6.5246e-01],
            (0.9, 1.0): [
                2.4916e-01, 2.7606e-01, 4.0406e-01,
                6.8334e-01, 9.6386e-01, 1.4528e+00],
            },
        }

one =           WS(ws, RooConstVar('one',      'one',          1.))
zero =          WS(ws, RooConstVar('zero',     'zero',         0.))

# observable
time = WS(ws, RooRealVar('time', 'time', *TimeRange))
timeerr = WS(ws, RooRealVar('timeerr', 'timeerr', *TimeErrRange))

timeConv = 1e9 / 2.99792458e8

files = ([ '/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_MD_OFFLINE_DsK.root',
           '/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_MU_OFFLINE_DsK.root'
          ] if isDsK else
          [ '/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_MD_OFFLINE_DsPi.root',
            '/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_MU_OFFLINE_DsPi.root' ])
cuts = ('%24.16e <= lab0_MassFitConsD_M[0] && lab0_MassFitConsD_M[0] <= %24.16e && '
        '%s && %24.16e <= BDTGResponse_1 && BDTGResponse_1 <= %24.16e && '
        'lab1_P > 3e3 && lab1_P < 650e3 && lab2_MM > 1930. && lab2_MM < 2015. && '
        'lab1_PT > 400. && lab1_PT < 45e3 && nTracks > 15. && '
        'nTracks < 1000. && lab2_TAU > 0. && '
        '%24.16e <= lab0_LifetimeFit_ctau[0] && lab0_LifetimeFit_ctau[0] <= %24.16e &&'
        '%24.16e <= lab0_LifetimeFit_ctauErr[0] && lab0_LifetimeFit_ctauErr[0] <= %24.16e &&'
        'lab1_ID*lab2_ID < 0 && '
        '((1e-2*lab3_ID) * (1e-2*lab4_ID) * (1e-2*lab5_ID) * (1e-2*lab1_ID) > 0)' %
        (MassRange[0], MassRange[1], 'lab1_PIDK > 5' if isDsK else
        'lab1_PIDK < 0', BDTGRange[0], BDTGRange[1],
        TimeRange[0] / timeConv, TimeRange[1] / timeConv,
        TimeErrRange[0] / timeConv, TimeErrRange[1] / timeConv))

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

tacc, tacc_norm = accbuilder(time, knots[BDTGRange], coeffs[isDsK][BDTGRange])

ds = getDataSet(ws, cuts, files)

fr = time.frame()
ds.plotOn(fr)
fr.Draw()

# build simple fitter - fit D
# build pdf for fitting the usual way:
# - first apply decay time resolution smearing
# - then, apply acceptance
D = WS(ws, RooRealVar('D', 'D', 0., -1., 1.))

fit_resmodel = WS(ws, RooGaussEfficiencyModel(
    'fit_resmodel', 'fit_resmodel', time, tacc, zero, timeerr, SF, SF))
fit_pdf = WS(ws, RooBDecay('fit_pdf', 'fit_pdf',
    time, tau, dGamma, one, D, zero, zero, zero, fit_resmodel,
    RooBDecay.SingleSided))

# ok, fit back
timeerrargset = RooArgSet(timeerr)
for v in (D, dGamma): v.setConstant(True)
fit_pdf.fitTo(ds, RooFit.Timer(), RooFit.Verbose(), RooFit.Strategy(2),
        RooFit.Optimize(2), RooFit.Offset(), RooFit.Save(),
        RooFit.ConditionalObservables(timeerrargset))
for v in (D, dGamma): v.setConstant(False)
fit_pdf.fitTo(ds, RooFit.Timer(), RooFit.Verbose(), RooFit.Strategy(2),
        RooFit.Optimize(2), RooFit.Offset(), RooFit.Save(),
        RooFit.ConditionalObservables(timeerrargset))
fit_pdf.plotOn(fr, RooFit.ProjWData(timeerrargset, ds, True))
fr.Draw()
ROOT.gPad.SetLogy()
ROOT.gPad.Print('CombBkgLifetimeFit_%s_BDTG%g-%g.pdf' % ('DsK' if isDsK else
        'DsPi', BDTGRange[0], BDTGRange[1]))
