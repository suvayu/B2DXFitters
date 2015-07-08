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
        RooEffProd, RooNumConvPdf, RooWorkspace, RooAbsReal, Inverse,
        RooKResModel, RooHistPdf, RooProdPdf, RooExtendPdf)
from B2DXFitters.WS import WS as WS
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')

ws = RooWorkspace('ws')

gamma =         WS(ws, RooRealVar('Gamma',      'Gamma',        0.679))
dGamma =        WS(ws, RooRealVar('dGamma',     'dGamma',      -0.060))
dMs =           WS(ws, RooRealVar('dMs',        'dMS',         17.800))
SF =            WS(ws, RooConstVar('SF',        'SF',           1.195))
tau = WS(ws, Inverse('tau', 'tau', gamma))

isDsK = True
mode = 'Bs2DsRho'
BDTGRange =    (0.3, 1.0)
MassRange =    (5300., 5800.)
TimeRange =    (0.4, 15.0) if (0.9, 1.0) != BDTGRange else (0.75, 15.0)
TimeErrRange = (0.01, 0.1)

knots = {
        (0.3, 1.0): [ 0.5, 1.0, 1.5, 2.0, 3.0, 12. ],
        (0.6, 1.0): [ 0.5, 1.0, 1.5, 2.0, 3.0 ],
        (0.3, 0.9): [ 0.5, 1.0, 1.5, 2.0, 3.0 ],
        (0.9, 1.0): [ 0.8, 1.0, 1.5, 2.0, 3.0 ],
        }
coeffs = {
        (0.3, 1.0): [ 5.03902e-01, 7.32741e-01, 9.98736e-01, 1.16514e+00, 1.25167e+00, 1.28624e+00 ],
        }

one =           WS(ws, RooConstVar('one',      'one',          1.))
zero =          WS(ws, RooConstVar('zero',     'zero',         0.))

# observable
# observable
time = WS(ws, RooRealVar('time', 'time', *TimeRange))
timeerr = WS(ws, RooRealVar('timeerr', 'timeerr', *TimeErrRange))
kFactor = WS(ws, RooRealVar('kFactor', 'kFactor', 1.0, 0.1, 2.0))
kFactor.setConstant(True)

timeConv = 1e9 / 2.99792458e8

files = {
        'Bs2DsstPi': [
            '/afs/cern.ch/work/a/adudziak/public/MCJanuary2014/MergedTree_Bs2DsstPi_Ds2KKPi_BsHypo_BDTG.root'
            ],
        'Bs2DsRho':  [
            '/afs/cern.ch/work/a/adudziak/public/MCJanuary2014/MergedTree_Bs2DsRho_Ds2KKPi_BsHypo_BDTG.root'
            ],
        }
cuts = ('%24.16e <= lab0_MassFitConsD_M[0] && lab0_MassFitConsD_M[0] <= %24.16e && '
        '%s && %24.16e <= BDTGResponse_1 && BDTGResponse_1 <= %24.16e && '
        'lab1_P > 3e3 && lab1_P < 650e3 && lab2_MM > 1930. && lab2_MM < 2015. && '
        'lab1_PT > 400. && lab1_PT < 45e3 && nTracks > 15. && '
        'nTracks < 1000. && lab2_TAU > 0. && '
        '%24.16e <= lab0_LifetimeFit_ctau[0] && lab0_LifetimeFit_ctau[0] <= %24.16e &&'
        '%24.16e <= lab0_LifetimeFit_ctauErr[0] && lab0_LifetimeFit_ctauErr[0] <= %24.16e &&'
        '321 == abs(lab1_ID) && ((321 == abs(lab3_ID) && 321 == abs(lab4_ID) && '
        '211 == abs(lab5_ID)) || (321 == abs(lab3_ID) && 211 == abs(lab4_ID) && '
        '321 == abs(lab5_ID)) || (211 == abs(lab3_ID) && 321 == abs(lab4_ID) && '
        '321 == abs(lab5_ID))) && (lab2_BKGCAT < 30 || 50 == lab2_BKGCAT) && '
        'lab0_BKGCAT < 60 && lab1_M > 200 && lab2_FDCHI2_ORIVX > 2 && '
        'lab1_ID*lab2_ID < 0 && '
        '((1e-2*lab3_ID) * (1e-2*lab4_ID) * (1e-2*lab5_ID) * (1e-2*lab1_ID) > 0)' %
        (MassRange[0], MassRange[1], '1', #'lab1_PIDK > 5' if isDsK else'lab1_PIDK < 0',
            BDTGRange[0], BDTGRange[1],
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
    from ROOT import (RooBinning, RooArgList, RooPolyVar,
            RooCubicSplineFun)
    if (0 >= len(myknots)):
        raise ValueError('ERROR: Spline knot position list empty')
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
    for i in xrange(0, len(knots)):
        coefflist.add(WS(ws, RooRealVar('SplineAccCoeff%u' % i,
            'SplineAccCoeff%u' % i, coeffs[i])))
    coefflist.add(one)
    myknots.append(time.getMax())
    myknots.reverse()
    fudge = (myknots[0] - myknots[1]) / (myknots[2] - myknots[1])
    i = coefflist.getSize()
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

def readTemplate1D(
    fromfile,           # file to read from
    fromws,             # workspace to read from
    fromvarname,        # variable name in fromws
    objname,            # object to ask for
    ws, 	        # workspace to import into
    variable,	        # variable
    pfx,                # prefix of imported objects
    binIfPDF = False    # bin if the template comes as Pdf
    ):
    # read a 1D template from a file - can either be in a workspace (either
    # PDF or data set), or a plain 1D histogram
    from ROOT import ( TFile, RooWorkspace, RooKeysPdf, RooHistPdf,
        RooArgList, RooDataHist, RooArgSet )
    ff = TFile(fromfile, 'READ')
    if (None == ff or ff.IsZombie()):
        print 'ERROR: Unable to open %s to get template for %s' % (fromfile,
                variable.GetName())
    workspace = ff.Get(fromws)
    if None != workspace and workspace.InheritsFrom('RooWorkspace'):
        # ok, we're reading from a ROOT file which contains a RooWorkspace, so
        # we try to get a PDF of a RooAbsData from it
        ROOT.SetOwnership(workspace, True)
        var = workspace.var(fromvarname)
        if (None == var):
            print ('ERROR: Unable to read %s variable %s from '
                    'workspace %s (%s)') % (variable.GetName(), fromvarname,
                            fromws, fromfile)
            return None
        pdf = workspace.pdf(objname)
        if (None == pdf):
            # try to get a data sample of that name
            data = workspace.data(objname)
            if None == data:
                print ('ERROR: Unable to read %s pdf/data %s from '
                        'workspace %s (%s)') % (variable.GetName(),
                                fromvarname, fromws, fromfile)
                return None
            if data.InheritsFrom('RooDataSet'):
                # if unbinned data set, first create a binned version
                argset = RooArgSet(var)
                data = data.reduce(RooFit.SelectVars(argset))
                ROOT.SetOwnership(data, True)
                data = data.binnedClone()
                ROOT.SetOwnership(data, True)
            # get underlying histogram
            hist = data.createHistogram(var.GetName())
            del data
        else:
            # we need to jump through a few hoops to rename the dataset and variables
            # get underlying histogram
            if (pdf.InheritsFrom('RooHistPdf')):
                hist = pdf.dataHist().createHistogram(var.GetName())
            else:
                if binIfPDF:
                    hist = pdf.createHistogram(var.GetName(), var)
                else:
                    # ok, replace var with variable
                    from ROOT import RooCustomizer
                    c = RooCustomizer(pdf, '%sPdf' % pfx);
                    c.replaceArg(var, variable)
                    pdf = c.build()
                    ROOT.SetOwnership(pdf, True)
                    pdf.SetName('%sPdf' % pfx)
                    pdf = WS(ws, pdf)
                    del var
                    del workspace
                    ff.Close()
                    del ff
                    return pdf
    else:
        # no workspace found, try to find a TH1 instead
        hist = None
        for tmp in (fromws, objname):
            hist = ff.Get(tmp)
            if (None != tmp and hist.InheritsFrom('TH1') and
                    1 == hist.GetDimension()):
                break
        if (None == hist or not hist.InheritsFrom('TH1') or
                1 != hist.GetDimension()):
            print ('ERROR: Utterly unable to find any kind of %s '
                    'variable/data in %s') % (variable.GetName(), fromfile)
            return None
    variable.setRange(
	    max(variable.getMin(),
		hist.GetXaxis().GetBinLowEdge(1)),
	    min(variable.getMax(),
		hist.GetXaxis().GetBinUpEdge(hist.GetNbinsX())))
    variable.setBins(hist.GetNbinsX())
    ROOT.SetOwnership(hist, True)
    hist.SetNameTitle('%sPdf_hist' % pfx, '%sPdf_hist' % pfx)
    hist.SetDirectory(None)
    if hist.Integral() < 1e-15:
        raise ValueError('Histogram empty!')
    # recreate datahist
    dh = RooDataHist('%sPdf_dhist' % pfx, '%sPdf_dhist' % pfx,
            RooArgList(variable), hist)
    del hist
    del pdf
    del var
    del workspace
    ff.Close()
    del ff
    # and finally use dh to create our pdf
    pdf = WS(ws, RooHistPdf('%sPdf' % pfx, '%sPdf' % pfx, RooArgSet(variable), dh))
    del dh
    return pdf

def getKFactorTemplate(ws, mode):
    return readTemplate1D(os.environ['B2DXFITTERSROOT'] +
            '/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root',
            'workspace', 'kfactorVar', 'kFactor_%s_both' % mode,
            ws, kFactor, '%s_' % mode)

def makeTimeErrPdfFromDataSet(ds):
    tmp = RooArgSet(timeerr)
    rds = ds.reduce(RooFit.SelectVars(tmp))
    ROOT.SetOwnership(rds, True)
    brds = rds.binnedClone()
    ROOT.SetOwnership(brds, True)
    del rds
    return WS(ws, RooHistPdf('timeerrpdf', 'timeerrpdf', tmp, brds))

def createHistFromDataSet(ds, var, name):
    tmp = RooArgSet(var)
    rds = ds.reduce(RooFit.SelectVars(tmp))
    ROOT.SetOwnership(rds, True)
    brds = rds.binnedClone()
    ROOT.SetOwnership(brds, True)
    del rds
    h = brds.createHistogram(name, var)
    ROOT.SetOwnership(h, True)
    del brds
    return h

tacc, tacc_norm = accbuilder(time, knots[BDTGRange], coeffs[BDTGRange])
kfactorpdf = getKFactorTemplate(ws, mode)

ds = getDataSet(ws, cuts, files[mode])

timeerrpdf = makeTimeErrPdfFromDataSet(ds)

fr = time.frame()
ds.plotOn(fr)
fr.Draw()

# build simple fitter - fit D
# build pdf for fitting the usual way:
# - first apply decay time resolution smearing
# - then, apply acceptance
fit_resmodel = WS(ws, RooGaussEfficiencyModel(
    'fit_resmodel', 'fit_resmodel', time, tacc, zero, timeerr, SF, SF))
fit_kresmodel = WS(ws, RooKResModel('fit_kresmodel', 'fit_kresmodel',
    fit_resmodel, kfactorpdf, kFactor, RooArgSet(gamma, dGamma, dMs)))
timeerr.setBins(100, 'cache')
fit_kresmodel.setParameterizeIntegral(RooArgSet(timeerr))
fit_tpdf = WS(ws, RooBDecay('fit_tpdf', 'fit_tpdf',
    time, tau, dGamma, one, zero, zero, zero, dMs, fit_kresmodel,
    RooBDecay.SingleSided))
fit_pdf = WS(ws, RooProdPdf('fit_pdf', 'fit_pdf', RooArgSet(timeerrpdf),
    RooFit.Conditional(RooArgSet(fit_tpdf), RooArgSet(time))))
y = WS(ws, RooConstVar('y', 'y', ds.numEntries()))
fit_epdf = WS(ws, RooExtendPdf('fit_epdf', 'fit_epdf', fit_pdf, y))

# ok, fit back
timeerrargset = RooArgSet(timeerr)
fit_pdf.fitTo(ds, RooFit.Timer(), RooFit.Verbose(), RooFit.Strategy(2),
        RooFit.Optimize(2), RooFit.Offset(), RooFit.Save())
fit_pdf.plotOn(fr, RooFit.ProjWData(timeerrargset, ds, True))
fr.Draw()
ROOT.gPad.SetLogy()
ROOT.gPad.Print('AccFitMC_%s_BDTG%g-%g.pdf' % (mode, BDTGRange[0], BDTGRange[1]))

h1 = fit_epdf.createHistogram('h1', time, RooFit.Extended(True))
h2 = createHistFromDataSet(ds, time, 'h2')
h1.Scale(h2.Integral() / h1.Integral())
h2.SetLineColor(kBlue)
h1.Draw('E1')
h2.Draw('E1SAME')
print 'K-S Test result: %g' % h1.KolmogorovTest(h2, '')
print 'K-S Test result with X flag: %g' % h1.KolmogorovTest(h2, 'X')
ROOT.gPad.Print('AccFitMC_%s_BDTG%g-%g-KS.pdf' % (mode, BDTGRange[0], BDTGRange[1]))

