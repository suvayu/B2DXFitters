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
from optparse import OptionParser
from math     import pi, log, sqrt, fmod
import os, sys, gc

if 'CMTCONFIG' in os.environ:
    import GaudiPython
import ROOT
# avoid memory leaks - will have to explicitly relinquish and acquire ownership
# if required, but PyROOT does not do what it thinks best without our knowing
# what it does
ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
if not 'CMTCONFIG' in os.environ:
    # enable ROOT to understand Reflex dictionaries
    ROOT.gSystem.Load('libCintex')
    ROOT.Cintex.Enable()
# load RooFit
ROOT.gSystem.Load('libRooFit')
from ROOT import RooFit
# load our own B2DXFitters library
if 'CMTCONFIG' in os.environ:
    GaudiPython.loaddict('B2DXFittersDict')
else:
    # running in standalone mode, we have to load things ourselves
    ROOT.gSystem.Load(os.environ['B2DXFITTERSROOT'] +
        '/standalone/libB2DXFitters')

# figure out if we're running from inside gdb
def in_gdb():
    import os
    proclist = dict(
        (l[0], l[1:]) for l in (
        lraw.replace('\n', '').replace('\r','').split()
        for lraw in os.popen('ps -o pid= -o ppid= -o comm=').readlines()
        )
        )
    pid = os.getpid()
    while pid in proclist:
        if 'gdb' in proclist[pid][1]: return True
        pid = proclist[pid][0]
    return False

if in_gdb():
    # when running in a debugger, we want to make sure that we do not handle
    # any signals, so the debugger can catch SIGSEGV and friends, and we can
    # poke around
    ROOT.SetSignalPolicy(ROOT.kSignalFast)
    ROOT.gEnv.SetValue('Root.Stacktrace', '0')

EXT = '.pdf'
fnamepattern = 'fitresult_[0-9][0-9][0-9][0-9].root'
exclude = []

# Load PyROOT
# -----------
pyrootpath = os.environ[ 'ROOTSYS' ]

if os.path.exists(pyrootpath):
   sys.path.append(pyrootpath + os.sep + 'bin')
   sys.path.append(pyrootpath + os.sep + 'lib')
   import ROOT
   print 'PyROOT is loaded.'
else:
   print 'Unable to find ROOT! Nothing done.'
   sys.exit(0)

ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
from ROOT import gROOT, TFile, TH1D
from ROOT import gDirectory, TStyle, TF1, TFile, TCanvas, gROOT
gROOT.SetBatch(True)

# ----------------------------------------------------------------------------
# returns 1st fitresult, vnames, initvals, vals, errs
def readRooFitResults(fnamepattern, exclude, resultsfile = None):
    from glob import iglob
    from ROOT import RooFitResult, TClass
    import gc
    nftot = 0
    nfexcl = 0
    checkexcludes = 0 < len(exclude)
    initvals = None
    vals = dict()
    errs = dict()
    vnames = None
    firstfitresult = None
    for fname in iglob(fnamepattern):
        nftot += 1
        num = number_exp(fname)
        if checkexcludes:
            if num in exclude:
	        print 'Experiment #%d excluded!' % num
		nfexcl += 1
                continue
        f = TFile(fname, 'READ')
        ROOT.SetOwnership(f, True)
        for key in f.GetListOfKeys():
	    if not TClass.GetClass(key.GetClassName()).InheritsFrom('RooFitResult'):
		continue
            obj = key.ReadObj()
	    ROOT.SetOwnership(obj, True)
            if 0 == obj.status() and 3 == obj.covQual():
                if None == vnames:
                    firstfitresult = obj.Clone()
                    ROOT.SetOwnership(firstfitresult, True)
                    if None != resultsfile:
                        print 'Saving a RooFitResult to store the initial values of the fitted parameters ...'
                        # upon write to file, ROOT will take ownership
                        resfile.WriteTObject(firstfitresult, firstfitresult.GetName())
                        ROOT.SetOwnership(firstfitresult, False)
                        print '... done.'
		    vnames = get_vars_names(obj)
                    print '--> variable names:', vnames
		    initvals = get_vars_initvals(obj)
		    for name in vnames:
	                vals[name] = []
                        errs[name] = []
		params = obj.floatParsFinal()
	        for name in vnames:
                    param = params.find(name)
                    if None == param: continue
	            val = param.getVal()
                    if isphase(name): val = normalise_phase(val)
                    vals[ name ].append(val)
                    errs[ name ].append(param.getError())
                    #print '* %s :' % name
	            #print '  %f +/- %f' % (val, param.getError())
                    #print 20*'#'
            else:
		print 'Experiment #%d excluded based on fit quality!' % num
		nfexcl += 1
            del obj
        f.Close()
	del f
        del fname
        del num
        gc.collect()
    print '-->', nftot, 'files analysed,', nfexcl, 'excluded.\n'
    return firstfitresult, vnames, initvals, vals, errs

# ----------------------------------------------------------------------------
def printMinuitQuality() :
   for r in rooFitResults:
      print r.status(), r.covQual()
      print res.Print()
      print '##############################################################'

# ----------------------------------------------------------------------------
def get_vars_names(res):
   params = res.floatParsFinal()
   size = params.getSize()
   vnames = []
   for i in range(size):
      vnames.append(params.at(i).GetName())
   return vnames

# ----------------------------------------------------------------------------
def isphase(name):
    # look for something that looks like a phase
    for n in ('deltaMs', 'deltaMd'):
	if n in name: return False
    for n in ( 'gamma', 'delta', 'phi_w' ):
	if n in name: return True
    return False

# ----------------------------------------------------------------------------
def normalise_phase(val):
    # normalise a phase to be within -pi < phaase <= pi
    val = fmod(val, 2. * pi)
    while val > pi:
	val -= 2. * pi
    while val <= -pi:
	val += 2. * pi
    return val

# ----------------------------------------------------------------------------
def get_vars_initvals(res):
   initvals   = dict()
   initparams = res.floatParsInit()
   for i in range(initparams.getSize()):
      param = initparams.at(i)
      name = param.GetName()
      val = param.getVal()
      if isphase(name): val = normalise_phase(val)
      initvals[ name ] = val
   return initvals

# ----------------------------------------------------------------------------
def rad2deg(angle):
   return angle * 180. / pi

# ----------------------------------------------------------------------------
def number_exp(fname):
   imin = fname.find('_')
   imax = fname.find('.')
   nstr = fname[imin+1:imax]
   return int(nstr)

# ----------------------------------------------------------------------------

resfile = TFile('results.root', 'RECREATE')
fitresult, vnames, initvals, vals, errs = readRooFitResults(fnamepattern, exclude, resfile)
NTOYSGOOD = len(vals[vnames[0]])

# temporary variable to contain histos to be written out to a ROOT file
# (i.e. histos for the floating parameters)
all_histos = []
histos = { }

for name in vnames:
   print 'Figure out ranges for variable ', name, '...'
   values = vals[ name ]
   errors = errs[ name ]
   v = 0.
   p = 0.
   n = 0.
   np = 0.
   for i in range(len(values)) :
      val = values[i]
      err = errors[i]
      if val != val or (abs(val) > 1. and abs(1. / val) == 0.):
	  continue
      v = v * (n / (n + 1.0)) + val / (n + 1.)
      n = n + 1.
      if err != err or (abs(err) > 1. and abs(1. / err) == 0.) or err <= 0.:
	  continue
      resid = val - initvals[name]
      if isphase(name): resid = normalise_phase(resid)
      pull = resid / err
      if abs(pull) > 5.:
        continue
      p = p * (np / (np + 1.0)) +  pull / (np + 1.)
      np = np + 1.
   v2 = 0.
   p2 = 0.
   n = 0.
   np = 0.
   for i in range(len(values)) :
      val = values[i]
      err = errors[i]
      if val != val or (abs(val) > 1. and abs(1. / val) == 0.):
	  continue
      v2 = v2 * (n / (n + 1.0)) + (val - v) * (val - v) / (n + 1.)
      n = n + 1.
      if err != err or (abs(err) > 1. and abs(1. / err) == 0.) or err <= 0.:
	  continue
      resid = val - initvals[name]
      if isphase(name): resid = normalise_phase(resid)
      pull = resid / err
      if abs(pull) > 5.:
        continue
      p2 = p2 * (np / (np + 1.0)) +  (pull - p) * (pull - p) / (np + 1.)
      np = np + 1.
   sigmav = sqrt(v2)
   sigmap = sqrt(p2)
   hv = TH1D('%s value' % name, '%s value' % name,
	   50, v - 3. * sigmav, v + 3. * sigmav)
   hv.SetDirectory(None)
   hp = TH1D('%s pull' % name, '%s pull' % name,
	       50, p - 3. * sigmap, p + 3. * sigmap)
   hp.SetDirectory(None)
   histos[name] = [hv, hp]
   all_histos.append(hv)
   all_histos.append(hp)

for name in vnames:
   h = histos[ name ]
   if not (h[0] and h[1]) : continue
   print 'Filling the fit values and pull histograms for the variable', name, '...'
   values = vals[ name ]
   errors = errs[ name ]
   for i in xrange(len(values)):
      val = values[i]
      err = errors[i]
      if val != val or (abs(val) > 1. and abs(1. / val) == 0.): continue
      if err != err or (abs(err) > 1. and abs(1. / err) == 0.) or err <= 0.: continue
      h[0].Fill(val)
      if abs(err) > 1.e-9:
         resid = val - initvals[name]
         if isphase(name): resid = normalise_phase(resid)
         pull = resid / err
         h[1].Fill(pull)
      else:
         print 'WARNING: skipped entry in pull dist. of', name,\
               'error =', err
   print '... done.'

if 'C' in vals and 'S' in vals and 'D' in vals:
    print 'Filling the histogram for |C|^2+|S|^2+|D|^2 ...'
    h_sum = TH1D('|C|^2+|S|^2+|D|^2 values', '|C|^2+|S|^2+|D|^2',
                  30, 0.0, 0.0)
    all_histos.append(h_sum)
    for i in xrange(len(vals[ 'C' ])):
       val_c = vals[ 'C' ][i]
       val_s = vals[ 'S' ][i]
       val_d = vals[ 'D' ][i]
       h_sum.Fill(val_c*val_c + val_s*val_s + val_d*val_d)
    print '... done.'

if 'C' in vals and 'Sbar' in vals and 'Dbar' in vals:
    print 'Filling the histogram for |C|^2+|Sbar|^2+|Dbar|^2 ...'
    h_sum2 = TH1D('|C|^2+|Sbar|^2+|Dbar|^2 values', '|C|^2+|Sbar|^2+|Dbar|^2',
                   30, 0.0, 0.0)
    all_histos.append(h_sum2)
    for i in range(len(vals[ 'C' ])):
       val_c = vals[ 'C' ][i]
       val_s = vals[ 'Sbar' ][i]
       val_d = vals[ 'Dbar' ][i]
       h_sum2.Fill(val_c*val_c + val_s*val_s + val_d*val_d)
    print '... done.'

print 'Saving all histograms to results.root ...'
for histo in all_histos:
   # upon write to file, ROOT will take ownership
   ROOT.SetOwnership(histo, False)
   resfile.WriteTObject(histo, histo.GetName())
print '... done.'

del resfile

def rootSettings():	
   ROOT.gROOT.SetStyle('Plain')
   ROOT.gStyle.SetCanvasColor(0)
   ROOT.gStyle.SetPadColor(0)
   ROOT.gStyle.SetMarkerColor(0)
   ROOT.gStyle.SetOptStat(111111)
   ROOT.gStyle.SetOptFit(111)
   ROOT.gROOT.ForceStyle()

# ----------------------------------------------------------------------------
def fit_histo(h):
   if h.GetEntries() <= 0.:
      return
   m = h.GetMaximum()
   gaussian = TF1('Gaussian', 'gaus')
   gaussian.SetParameters(m, h.GetMean(), h.GetRMS())
   gaussian.SetLineColor(ROOT.kBlue)
   h.Fit(gaussian, 'ILQ')

# ----------------------------------------------------------------------------
def plot_and_fit_histos(fitvars, evalvars, pullvars):
   from ROOT import gDirectory
   keys = gDirectory.GetListOfKeys()
   for k in keys:
      obj = k.ReadObj()
      if (obj.IsA().InheritsFrom('TH1')) :
         name = obj.GetName()
         print 'Fitting histo "', name, '" ...'
         fit_histo(obj)
         if 'Gamma' in name:
            make_eval_vars(obj, evalvars)
         elif 'pull' in name:
            make_pull_vars(obj, pullvars)
         else:
            make_fit_vars(obj, fitvars)
         print 'Drawing histo "', name, '" ...'
	 obj.SetMarkerColor(ROOT.kBlack)
         obj.SetMarkerStyle(21)
         if ('Gamma' in name) :
            obj.GetXaxis().SetTitle('Evaluated ' + name)
         else:
            obj.GetXaxis().SetTitle('Fitted ' + name)
         obj.GetYaxis().SetTitle('# of toys')
         obj.SetTitle('')
         obj.Draw('E1')
         c.Update()
         stats = obj.GetListOfFunctions().FindObject('stats')
         line = stats.GetLine(0)
         #if '|' in line.GetTitle():
         #print 'line=', line.GetTitle()
         line.SetTitle('')
         stats.Draw()
         obj.GetListOfFunctions().Add(stats)
         stats.SetParent(obj.GetListOfFunctions())
         #obj.GetListOfFunctions().FindObject('stats').Print()
         stats.SetOptStat(111111)
         stats.Draw()
         c.Modified()
         if ('Gamma' in name) or ('Delta' in name) :
            name = name.replace('/', '')
            name = name.replace('^', '')
            name = name.replace('(', '')
            name = name.replace(')', '')
            name = name.replace('.', '')
            name = name.replace('>=', 'ge')
            name = name.replace('=', 'eq')
            name = name.replace('+', 'plus')
            name = name.replace('-', 'minus')
            name = name.replace(', ', '-')
            c.Print(name.replace(' ', '_') + EXT)
         else:
            name = name.replace('|', '')
            name = name.replace('^', '')
            name = name.replace('+', 'plus')
            name = name.replace('(', '_')
            name = name.replace(')', '')
            c.Print(name.replace(' ', '_') + EXT)

# ----------------------------------------------------------------------------
def make_fit_vars(h, fitvars):
   title = h.GetName().replace(' value', '')
   func  = h.GetFunction('Gaussian')
   mean  = func.GetParameter(func.GetParNumber('Mean'))
   sig   = func.GetParameter(func.GetParNumber('Sigma'))
   meanerr  = func.GetParError(func.GetParNumber('Mean'))
   sigerr   = func.GetParError(func.GetParNumber('Sigma'))
   initparams = get_vars_initvals(fitresult)
   if title in initparams and h.GetEntries() > 0.:
      fitvars[ title ] = [
         initparams[title], mean, sig, meanerr, sigerr]

# ----------------------------------------------------------------------------
def make_eval_vars(h, evalvars):
   title = h.GetName()
   func  = h.GetFunction('Gaussian')
   mean  = func.GetParameter(func.GetParNumber('Mean'))
   sig   = func.GetParameter(func.GetParNumber('Sigma'))
   initparams = get_vars_initvals(fitresult)
   val_l    = initparams['arg_lam'].getVal()
   val_lbar = initparams['arg_lam_bar'].getVal()
   delta = rad2deg(0.5 * (val_l + val_lbar))
   gamma = rad2deg(0.5 * (val_lbar - val_l))
   initvals = { 'Delta': delta, 'Gamma+phi_s': gamma }
   evalvars[ title ] = (initvals[ title ], mean, sig)

# ----------------------------------------------------------------------------
def make_pull_vars(h, pullvars):
   if h.GetEntries() <= 0.:
      return
   title = h.GetName().replace(' pull', '')
   func  = h.GetFunction('Gaussian')
   mean  = func.GetParameter(func.GetParNumber('Mean'))
   sig   = func.GetParameter(func.GetParNumber('Sigma'))
   meanerr = func.GetParError(func.GetParNumber('Mean'))
   sigerr  = func.GetParError(func.GetParNumber('Sigma'))
   pullvars[ title ] = (mean, sig, meanerr, sigerr)

# ----------------------------------------------------------------------------
def print_const_vars(rootfile):
   res         = fitresult
   if None == res:
      return
   constparams = res.constPars()
   print ''
   print '--------------', ' ----------', ' ------------------------------------'
   print ('%14s %11s %s') % ('Const variable', '     Value', ' Description')
   print '--------------', ' ----------', ' ------------------------------------'
   for i in range(constparams.getSize()):
      param = constparams.at(i)
      print('%14s %11.2f  %s')\
             % (param.GetName(), param.getVal(), param.GetTitle())
      print '--------------', ' ----------', ' ------------------------------------'
   print ''
   f.Close()

# ----------------------------------------------------------------------------
def rad2deg(angle):
   return angle * 180. / pi

# ----------------------------------------------------------------------------
    
rootfile = 'results.root'

if os.path.isfile(rootfile):
   from ROOT import TCanvas
   rootSettings()
   f = TFile(rootfile, 'READ')
   c = TCanvas()
   fitvars  = dict()
   evalvars = dict()
   pullvars = dict()
   plot_and_fit_histos(fitvars, evalvars, pullvars)
   print pullvars
   #command =   'gzip -f *.eps'
   #os.system(command)

   print_const_vars(rootfile)
   
   print 'Values: %16s %12s %12s %12s %12s %12s' % \
      ('parameter', 'initial', 'mean', 'mean error', 'precision', 'prec. error')
   print '-----------------------------------------------------------------------------------------'
   for key, val in sorted(fitvars.iteritems()):
      print '%24s %12.5g %12.5g %12.5g %12.5g %12.5g' % \
         (key, val[0], val[1], val[3], val[2], val[4])
   print ''
   print 'Pulls: %17s %12s %12s %12s %12s' % \
      ('parameter', 'mean', 'mean error', 'sigma', 'sigma error')
   print '----------------------------------------------------------------------------'
   for key, val in sorted(pullvars.iteritems()):
      print '%24s %12.5g %12.5g %12.5g %12.5g' % \
         (key, val[0], val[2], val[1], val[3])
   print ''


   print '------------', ' -----------', '  ----------------------'
   for key, val in sorted(evalvars.iteritems()) :
      print('%12s %12.3f %11.3f  +/-  %5.3f')\
             % (key, val[0], val[1], val[2])
   print '------------', ' -----------', '  ----------------------'
   print ''
   print 'Used %d toys' % NTOYSGOOD
   print ''

   print 'Done.'
else:
   print 'File ' + rootfile + ' not found! Nothing done.'
    
# =============================================================================


print 'All done!'

