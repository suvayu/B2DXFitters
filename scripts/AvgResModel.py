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
ROOT.gROOT.SetBatch()

from ROOT import RooFit, RooAbsReal
RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')

# "swallow" object into a workspace, returns swallowed object
def WS(ws, obj, opts = [RooFit.RecycleConflictNodes(), RooFit.Silence()]):
    name = obj.GetName()
    wsobj = ws.obj(name)
    if obj.InheritsFrom('RooAbsArg') or obj.InheritsFrom('RooAbsData'):
        if None == wsobj:
            if len(opts) > 0:
                ws.__getattribute__('import')(obj, *opts)
            else:
                ws.__getattribute__('import')(obj)
            wsobj = ws.obj(name)
        else:
            if wsobj.Class() != obj.Class():
                raise TypeError()
    else:
        if None == wsobj:
            ws.__getattribute__('import')(obj, name)
            wsobj = ws.obj(name)
        else:
            if wsobj.Class() != obj.Class():
                raise TypeError()
    return wsobj

# read decay time error distribution from file
def getDecayTimeErrorTemplate(
    ws,         # workspace to import into
    timeerr     # timeerr variable
    ):
    from ROOT import ( TFile, RooWorkspace, RooKeysPdf, RooHistPdf,
        RooArgList, RooDataHist, RooArgSet )
    import os
    #fromfile = os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/templates_BsDsPi.root'
    #fromfile = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsK.root"
    fromfile = "/afs/cern.ch/user/a/adudziak/cmtuser/Urania_v2r1/PhysFit/B2DXFitters/scripts/template_MC_Terr_BsDsPi.root"
    fromws = 'workspace'
    fromvarname = 'lab0_LifetimeFit_ctauErr'
    fromfile = TFile(fromfile, 'READ')
    workspace = fromfile.Get(fromws)
    ROOT.SetOwnership(workspace, True)
    var = workspace.var(fromvarname)
    pdf = workspace.pdf('sigTimeErrorPdf_BsDsPi')
    # we need to jump through a few hoops to rename the dataset and variables
    # get underlying histogram
    hist = pdf.dataHist().createHistogram(var.GetName())
    timeerr.setBins(hist.GetNbinsX())
    ROOT.SetOwnership(hist, True)
    hist.SetNameTitle('sigTimeErrPdf_hist', 'sigTimeErrPdf_hist')
    hist.SetDirectory(None)
    # get bounds from var on file
    timeerr.setMin(max(timeerr.getMin(), var.getMin()))
    timeerr.setMax(max(timeerr.getMax(), var.getMax()))
    # recreate datahist
    dh = RooDataHist('sigTimeErrPdf_dhist', 'sigTimeErrPdf_dhist',
            RooArgList(timeerr), hist)
    del hist
    del pdf
    del var
    del workspace
    fromfile.Close()
    del fromfile
    # and finally use dh to create our pdf
    pdf = WS(ws, RooHistPdf('sigTimeErrPdf', 'sigTimeErrPdf',
        RooArgSet(timeerr), dh))
    del dh
    return pdf

from ROOT import RooWorkspace, RooRealVar, RooGaussian, RooProdPdf, RooArgSet, RooArgList, RooAddPdf, RooConstVar, gPad, RooProduct
ws = RooWorkspace()


sf = WS(ws, RooRealVar('sf', 'sf', 1.00))
sigma_t = WS(ws, RooRealVar('sigma_t', 'sigma_t', 1e-6, 0.25,'ps'))
sigma_t_pdf = getDecayTimeErrorTemplate(ws, sigma_t)
zero = WS(ws, RooConstVar('zero', 'zero', 0.))
t = WS(ws, RooRealVar('t','t',-.25,.25,'ps'))
scaled_sigma_t = WS(ws, RooProduct('scaled_sigma_t', 'scaled_sigma_t', RooArgList(sigma_t, sf)))
t_pdf = WS(ws, RooGaussian('t_pdf', 't_pdf', t, zero, scaled_sigma_t))
pdf = WS(ws, RooProdPdf('pdf','pdf', RooArgSet(sigma_t_pdf), RooFit.Conditional(RooArgSet(t_pdf),RooArgSet(t))))
ds=pdf.generate(RooArgSet(t,sigma_t), 250000, RooFit.Verbose())
f=sigma_t.frame()
ds.plotOn(f)
pdf.plotOn(f)
f.Draw()
gPad.Print('AvgResModel-BsDsPi-sigma_t.pdf')

a=RooArgSet(t)
ds2=ds.reduce(RooFit.SelectVars(a))
sigma_0=RooRealVar('sigma_0','sigma_0',0.020,0.,.1)
sigma_1=RooRealVar('sigma_1','sigma_1',0.035,0.,.1)
sigma_2=RooRealVar('sigma_2','sigma_2',0.060,0.,.1)
g0=RooGaussian('g0','g0',t,zero,sigma_0)
g1=RooGaussian('g1','g1',t,zero,sigma_1)
g2=RooGaussian('g2','g2',t,zero,sigma_2)
f0=RooRealVar('f0','f0',0.37,0.,1.)
f1=RooRealVar('f1','f1',0.57,0.,1.)
gpdf = RooAddPdf('gpdf','gpdf',RooArgList(g0,g1,g2),RooArgList(f0,f1),False)
gpdf.fitTo(ds2, RooFit.Offset(), RooFit.Verbose(), RooFit.Strategy(2))
f=t.frame()
ds2.plotOn(f)
gpdf.plotOn(f)
gpdf.plotOn(f,RooFit.Components('g0'),RooFit.LineWidth(2),RooFit.LineStyle(ROOT.kDashed),RooFit.LineColor(ROOT.kRed))
gpdf.plotOn(f,RooFit.Components('g1'),RooFit.LineWidth(2),RooFit.LineStyle(ROOT.kDashed),RooFit.LineColor(ROOT.kMagenta+1))
gpdf.plotOn(f,RooFit.Components('g2'),RooFit.LineWidth(2),RooFit.LineStyle(ROOT.kDashed),RooFit.LineColor(ROOT.kCyan+1))
f.Draw()
gPad.SetLogy()
gPad.Print('AvgResModel-BsDsPi-t.pdf')
