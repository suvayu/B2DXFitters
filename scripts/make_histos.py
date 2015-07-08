#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# --------------------------------------------------------------------------- 
# @file make_histos.py
#
# Python script to create residual and pull plots
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
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O "$0" - "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from math     import pi, log, sqrt, fmod
import os, sys, gc

import B2DXFitters
import ROOT
from ROOT import gROOT
gROOT.SetBatch(True)
from ROOT import RooFit
from B2DXFitters.FitResultGrabberUtils import grabResult

parser = OptionParser(usage = '%prog [options] [fit result ROOT files]')
parser.add_option('-d', '--data', action='store_true', dest='isData',
        default=None, help='files a from data fits')
parser.add_option('-t', '--toy', action='store_false', dest='isData',
        default=None, help='files are toys/MC')
parser.add_option('--unblind', action='store_false', dest='blinding',
        default=True, help='unblind data (USE WITH CARE!)')
parser.add_option('-e', '--exclude', type='string', action='append', default=[],
        dest='exclude', help='exclude the (comma separated) list of toys')
parser.add_option('--diff', action='store_true', dest='diff', default=False,
        help='diff mode (toy-by-toy differences etc., i.e. same data set)')
parser.add_option('--debug', action='store_true', dest='debug', default=False,
        help='print debugging info')
parser.add_option('--extension', action='store', dest='extension', default='pdf',
        type='string', help='graphics extension to save plots (default pdf)')
parser.add_option('--systematic', action='store_true', dest='systematic',
        default=False, help='evaluate systematic (implies --diff; list the '
        'nominal files first)')
(options, args) = parser.parse_args()
if '-' == args[0]: args.pop(0)

if options.systematic: options.diff = True

if None == options.isData:
    raise ValueError('You need to specify if you are running on DATA or TOYS (--data/--toy)')
if not options.isData: options.blinding = False
debug = options.debug
gc.collect()

# work through exclude list
exclude = []
for v in options.exclude:
    if type(v) == int:
        exclude.append(v)
    elif type(v) == str:
        for vv in v.split(','):
            exclude.append(int(vv))
    else:
        raise TypeError('unknown type in exclude list')

# convert file name to toy number
def number_exp(fname):
    if options.isData: return 0
    tmpfname = fname.split('/')
    basename = tmpfname[len(tmpfname) - 1]
    imin = basename.rfind('_')
    imax = basename.rfind('.')
    if imin >= imax:
        raise ValueError('Unable to extract toy number from filename %s' % basename)
    nstr = basename[imin+1:imax]
    return int(nstr)

print 'Running with settings:'
print '\tMode: %s%s' % (
        'DATA' if options.isData else 'TOY', ', BLINDED' if options.blinding else '')
if options.diff:
    print '\tRunning in difference mode (toy-by-toy etc.)'
if options.systematic:
    print '\tRunning in systematic mode'
print '\tExtension: .%s' % options.extension
print '\tExclude: %s' % str(exclude)
print
gc.collect()

# read all files
fitresults = {}
for fname in args:
    toynr = number_exp(fname)
    if toynr in exclude:
        print 'Excluding nr %u (%s) -- in exclude list.' % (toynr, fname)
        continue
    result = grabResult(options.isData, options.blinding, fname)
    if None == result:
        print 'Excluding nr %u (%s) -- unable to get FitResult.' % (toynr, fname)
        if toynr not in exclude: exclude.append(toynr)
        continue
    # examine fit return code
    if 0 != result.status():
        print 'Excluding nr %u (%s) -- status not zero, fit not okay.' % (toynr, fname)
        if toynr not in exclude: exclude.append(toynr)
        continue
    # check covariance matrix quality
    if 3 != result.covQual() and -1 != result.covQual():
        print 'Excluding nr %u (%s) -- covariance matrix not okay.' % (toynr, fname)
        if toynr not in exclude: exclude.append(toynr)
        continue
    # store
    if toynr not in fitresults:
        fitresults[toynr] = []
    fitresults[toynr].append(result)
exclude = sorted(exclude)
print
print 'Exclude list after reading toys:'
print '\tExclude: %s' % str(exclude)
print
gc.collect()

# verify we have the correct number of results per toy number
# (do the toy-by-toy subtraction when in diff mode while we're at it)
tmpfitresults = []
if options.systematic:
    # set up tree for systrmatic studies
    from ROOT import TFile, TTree
    import ctypes
    branches = {
        'toyID':        ctypes.c_int(),
        'C':            ctypes.c_double(),
        'S':            ctypes.c_double(),
        'Sb':           ctypes.c_double(),
        'D':            ctypes.c_double(),
        'Db':           ctypes.c_double(),
        'C_err':        ctypes.c_double(),
        'S_err':        ctypes.c_double(),
        'Sb_err':       ctypes.c_double(),
        'D_err':        ctypes.c_double(),
        'Db_err':       ctypes.c_double(),
        'C_shift':      ctypes.c_double(),
        'S_shift':      ctypes.c_double(),
        'Sb_shift':     ctypes.c_double(),
        'D_shift':      ctypes.c_double(),
        'Db_shift':     ctypes.c_double(),
        'C_shift_err':  ctypes.c_double(),
        'S_shift_err':  ctypes.c_double(),
        'Sb_shift_err': ctypes.c_double(),
        'D_shift_err':  ctypes.c_double(),
        'Db_shift_err': ctypes.c_double(),
    }
    bnamemap = { 'Bs2DsK_C': 'C', 'Bs2DsK_D': 'D', 'Bs2DsK_Dbar': 'Db',
        'Bs2DsK_S': 'S', 'Bs2DsK_Sbar': 'Sb' }
    outfile = None
for toynr in fitresults:
    if not options.diff:
        if len(fitresults[toynr]) != 1:
            raise ValueError('More than one FitResult for toy %u while '
                    'not in diff mode' % toynr)
        tmpfitresults.append(fitresults[toynr][0])
    else:
        # diff mode
        if len(fitresults[toynr]) == 1:
            print 'Excluding nr %u -- only one fitter has result.' % toynr
            if toynr not in exclude: exclude.append(toynr)
            continue
        if len(fitresults[toynr]) > 2:
            raise ValueError('More than two FitResult for toy %u, do not know '
                    'how to diff that' % toynr)
        if options.systematic:
            fitresults[toynr][0].setOptions(['Systematic'])
            fitresults[toynr][1].setOptions(['Systematic'])
        else:
            fitresults[toynr][0].setOptions(['SameDataSet'])
            fitresults[toynr][1].setOptions(['SameDataSet'])
        if options.systematic:
            if None == outfile:
                outfile = TFile('systematic.root', 'RECREATE')
                tree = TTree('resultstree', 'resultstree')
                tree.SetDirectory(outfile)
                for bname in branches:
                    tree.Branch(bname, branches[bname], '%s/%s' % (bname, 'I' if 'toyID' == bname else 'D'))
            # write tuple for Moritz...
            branches['toyID'].value = toynr
            p1, p2 = fitresults[toynr][0].params(), fitresults[toynr][1].params()
            e1, e2 = fitresults[toynr][0].errors(), fitresults[toynr][1].errors()
            for vname in p1:
                if vname in bnamemap:
                    vnmapped = bnamemap[vname]
                    branches['%s' % vnmapped].value = p1[vname]
                    branches['%s_err' % vnmapped].value = e1[vname]
                    branches['%s_shift' % vnmapped].value = p2[vname]
                    branches['%s_shift_err' % vnmapped].value = e2[vname]
            tree.Fill()
        tmpfitresults.append(fitresults[toynr][0]-fitresults[toynr][1])
if options.systematic and None != outfile:
    outfile.WriteTObject(tree)
    del tree
    outfile.Close()
    del outfile
    del branches
    del bnamemap
fitresults = tmpfitresults
del tmpfitresults
print
print 'Exclude list after diff\'ing toys:'
print '\tExclude: %s' % str(exclude)
print
gc.collect()
# ok, at this point, we have a list of (possibly diffed) fit results which we
# proceed to plot

def isphase(name):
    # look for something that looks like a phase
    for n in ('deltaMs', 'deltaMd'):
        if n in name: return False
    for n in ( 'gamma', 'delta', 'phi_w' ):
        if n in name: return True
    return False

def normalise_phase(val):
    # normalise a phase to be within -pi < phaase <= pi
    val = fmod(val, 2. * pi)
    while val > pi:
        val -= 2. * pi
    while val <= -pi:
        val += 2. * pi
    return val

# step 1: figure out ranges - need mean and sigma for that
mu, var, n, pullmu, pullvar, pulln, initial = {}, {}, {}, {}, {}, {}, {}
for r in fitresults:
    par, err, pull = r.params(), r.errors(), r.pulls()
    for vname in par:
        p, e, pu = par[vname], err[vname], pull[vname]
        # zero error or smaller is not allowed
        if e <= 0.: continue
        # neither is NaN or infinity
        skip = False
        for val in (e, p, pu):
            if val != val or (abs(val) > 1. and abs(1. / val) == 0.):
                skip = True
                break
        if skip: continue
        if isphase(vname):
            p = normalise_phase(p)
            pu = normalise_phase(pu * e) / e
        # skip outliers
        if abs(pu) > 5.: continue
        if vname not in mu:
            n[vname], mu[vname], pulln[vname], pullmu[vname] = 0., 0., 0., 0.
        # ok, start building means
        mu[vname] = (mu[vname] * n[vname] + p) / (1. + n[vname])
        n[vname] = n[vname] + 1.
        pullmu[vname] = (pullmu[vname] * pulln[vname] + pu) / (1. + pulln[vname])
        pulln[vname] = pulln[vname] + 1.
        if vname not in initial:
            initial[vname] = r.initialParams()[vname]
for r in fitresults:
    par, err, pull = r.params(), r.errors(), r.pulls()
    for vname in r.params():
        p, e, pu = par[vname], err[vname], pull[vname]
        # zero error or smaller is not allowed
        if e <= 0.: continue
        # neither is NaN or infinity
        skip = False
        for val in (e, p, pu):
            if val != val or (abs(val) > 1. and abs(1. / val) == 0.):
                skip = True
                break
        if skip: continue
        if isphase(vname):
            p = normalise_phase(p)
            pu = normalise_phase(pu * e) / e
        # skip outliers
        if abs(pu) > 5.: continue
        if vname not in var:
            n[vname], var[vname], pulln[vname], pullvar[vname] = 0., 0., 0., 0.
        # subtract means
        p, pu = p - mu[vname], pu - pullmu[vname]
        if isphase(vname):
            p = normalise_phase(p)
            pu = normalise_phase(pu * e) / e
        # ok, start building variances
        var[vname] = (var[vname] * n[vname] + p * p) / (1. + n[vname])
        n[vname] = n[vname] + 1.
        pullvar[vname] = (pullvar[vname] * pulln[vname] + pu * pu) / (1. + pulln[vname])
        pulln[vname] = pulln[vname] + 1.
gc.collect()

# step 2: create histograms
histos = { 'value': {}, 'pull': {} }
for vname in mu:
    from ROOT import TH1D
    v = mu[vname]
    sigmav = sqrt(var[vname])
    p = pullmu[vname]
    sigmap = sqrt(pullvar[vname])
    if debug:
        print 'DEBUG: Mean, sigma for %s values: %g, %g' % (vname, v, sigmav)
    hv = TH1D('%s value' % vname, '%s_value;fitted %s' % (vname, vname),
           50, v - 3. * sigmav, v + 3. * sigmav)
    hv.SetDirectory(None)
    histos['value'][vname] = hv
    if debug:
        print 'DEBUG: Mean, sigma for %s pulls: %g, %g' % (vname, p, sigmap)
    hp = TH1D('%s pull' % vname, '%s_pull;%s pull' % (vname, vname),
               50, p - 3. * sigmap, p + 3. * sigmap)
    hp.SetDirectory(None)
    histos['pull'][vname] = hp
gc.collect()

# step 3: fill histograms
for r in fitresults:
    par, err, pull = r.params(), r.errors(), r.pulls()
    for vname in r.params():
        if vname not in mu:
            n[vname], mu[vname] = 0., 0.
            pulln[vname], pullmu[vname] = 0., 0.
        p, e, pu = par[vname], err[vname], pull[vname]
        # zero error or smaller is not allowed
        if e <= 0.: continue
        # neither is NaN or infinity
        skip = False
        for val in (e, p, pu):
            if val != val or (abs(val) > 1. and abs(1. / val) == 0.):
                skip = True
                break
        if skip: continue
        if isphase(vname):
            p = normalise_phase(p)
            pu = normalise_phase(pu * e) / e
        # ok, fill
        histos['value'][vname].Fill(p)
        histos['pull'][vname].Fill(pu)
gc.collect()

# step 4: fit to plot histos, record fit results    
def fit_histo(h):
    if h.GetEntries() <= 0.:
        return
    if h.GetEntries() <= 5.:
        return h.GetMean(), 0., h.GetRMS(), 0.
    m = h.GetMaximum()
    from ROOT import TF1
    gaussian = TF1('Gaussian', 'gaus')
    gaussian.SetParameters(m, h.GetMean(), h.GetRMS())
    gaussian.SetLineColor(ROOT.kBlue)
    h.Fit(gaussian, 'ILQ')
    # return mean, meanerr, sigma, sigmaerr
    imu = gaussian.GetParNumber('Mean')
    isigma = gaussian.GetParNumber('Sigma')
    return gaussian.GetParameter(imu), gaussian.GetParError(imu), gaussian.GetParameter(isigma), gaussian.GetParError(isigma)

def rootSettings():     
    ROOT.gROOT.SetStyle('Plain')
    ROOT.gStyle.SetCanvasColor(0)
    ROOT.gStyle.SetPadColor(0)
    ROOT.gStyle.SetMarkerColor(0)
    ROOT.gStyle.SetOptStat(111111)
    ROOT.gStyle.SetOptFit(111)
    ROOT.gROOT.ForceStyle()

rootSettings()
from ROOT import TFile, gPad
outfile = TFile('diffresults.root' if options.diff else 'results.root', 'RECREATE')
results = { 'value': {}, 'pull': {} }
for t in ('value', 'pull'):
    for vname in histos[t]:
        h = histos[t][vname]
        mu, muerr, sigma, sigmaerr = fit_histo(h)
        results[t][vname] = {
                'mu': mu, 'muerr': muerr, 'sigma': sigma, 'sigmaerr': sigmaerr}
        name = h.GetName().replace(' ', '_').replace('/', '_')
        h.SetMarkerColor(ROOT.kBlack)
        h.SetMarkerStyle(21)
        h.GetYaxis().SetTitle('# of toys')
        h.SetTitle('')
        h.Draw('E1')
        gPad.Update()
        stats = h.GetListOfFunctions().FindObject('stats')
        line = stats.GetLine(0)
        line.SetTitle('')
        stats.Draw()
        h.GetListOfFunctions().Add(stats)
        stats.SetParent(h.GetListOfFunctions())
        stats.SetOptStat(111111)
        stats.Draw()
        gPad.Modified()
        gPad.Print('%s.%s' % (name, options.extension))
        outfile.WriteTObject(h)
    gPad.Clear()
outfile.Close()
del outfile
gc.collect()

# step 5: print summary
NTOYSGOOD = len(fitresults)

print
print '-----------------------------------------------------------------------------------------'
print 'Using %u toys' % NTOYSGOOD
print '-----------------------------------------------------------------------------------------'
print 'Values: %16s %12s %12s %12s %12s %12s' % \
        ('parameter', 'initial', 'mean', 'mean error', 'precision', 'prec. error')
print '-----------------------------------------------------------------------------------------'
for key, val in sorted(results['value'].iteritems()):
    tmp = [ initial[key],
            val['mu'], val['muerr'],
            val['sigma'], val['sigmaerr'] ]
    print '%24s %12.5g %12.5g %12.5g %12.5g %12.5g' % (
            key, tmp[0], tmp[1], tmp[2], tmp[3], tmp[4])
print
print 'Pulls: %17s %12s %12s %12s %12s' % \
        ('parameter', 'mean', 'mean error', 'sigma', 'sigma error')
print '----------------------------------------------------------------------------'
for key, val in sorted(results['pull'].iteritems()):
    tmp = [ val['mu'], val['muerr'],
            val['sigma'], val['sigmaerr'] ]
    print '%24s %12.5g %12.5g %12.5g %12.5g' % (
            key, tmp[0], tmp[1], tmp[2], tmp[3])
print

print 'Used %d toys' % NTOYSGOOD
print
print 'Done.'

