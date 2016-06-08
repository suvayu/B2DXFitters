#!/bin/sh
# --------------------------------------------------------------------------- 
# @file decRateCoeff_Bd_tut_MeanRes.py
#
# @brief Tutorial script to illustrate the usage of
#        DecRateCoeff_Bd in a pythonic way.
#        Based on previous scripts from
#        Manuel Schiller.
#       
#        Use case: average sigma_t, two per-event taggers combined, 
#                  "on the fly", realistic acceptance,
#                  asymmetries (prod, det, tageff)
#
# @usage python decRateCoeff_Bd_tut_MeanRes.py SEED
#
# @author Vincenzo Battista
# @date 2016-06-03
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

from ROOT import *
from B2DXFitters import *

import array
from array import array

# useful function for plotting
def plotAll(ds, pdf, qf, qt, time, filename):
    import os
    ROOT.gROOT.SetBatch(True)
    canv = TCanvas("canv")
    canv.Divide(3, 2)

    catname = qt.GetName()

    frame1 = time.frame(ROOT.RooFit.Title(catname+"==+1 && qf==+1"))
    frame2 = time.frame(ROOT.RooFit.Title(catname+"==0 && qf==+1"))
    frame3 = time.frame(ROOT.RooFit.Title(catname+"==-1 && qf==+1"))
    frame4 = time.frame(ROOT.RooFit.Title(catname+"==+1 && qf==-1"))
    frame5 = time.frame(ROOT.RooFit.Title(catname+"==0 && qf==-1"))
    frame6 = time.frame(ROOT.RooFit.Title(catname+"==-1 && qf==-1"))
    if None != ds:
        ds.plotOn(frame1, ROOT.RooFit.Cut(catname+"==+1 && qf==+1"))
        ds.plotOn(frame2, ROOT.RooFit.Cut(catname+"==0 && qf==+1"))
        ds.plotOn(frame3, ROOT.RooFit.Cut(catname+"==-1 && qf==+1"))
        ds.plotOn(frame4, ROOT.RooFit.Cut(catname+"==+1 && qf==-1"))
        ds.plotOn(frame5, ROOT.RooFit.Cut(catname+"==0 && qf==-1"))
        ds.plotOn(frame6, ROOT.RooFit.Cut(catname+"==-1 && qf==-1"))
    if None != pdf:
        pdf.plotOn(frame1, ROOT.RooFit.Slice(qt, "B+"), ROOT.RooFit.Slice(qf, "h+"))
        pdf.plotOn(frame2, ROOT.RooFit.Slice(qt, "Untagged"), ROOT.RooFit.Slice(qf, "h+"))
        pdf.plotOn(frame3, ROOT.RooFit.Slice(qt, "B-"), ROOT.RooFit.Slice(qf, "h+"))
        pdf.plotOn(frame4, ROOT.RooFit.Slice(qt, "B+"), ROOT.RooFit.Slice(qf, "h-"))
        pdf.plotOn(frame5, ROOT.RooFit.Slice(qt, "Untagged"), ROOT.RooFit.Slice(qf, "h-"))
        pdf.plotOn(frame6, ROOT.RooFit.Slice(qt, "B-"), ROOT.RooFit.Slice(qf, "h-"))
    canv.cd(1)
    frame1.Draw()
    canv.cd(2)
    frame2.Draw()
    canv.cd(3)
    frame3.Draw()
    canv.cd(4)
    frame4.Draw()
    canv.cd(5)
    frame5.Draw()
    canv.cd(6)
    frame6.Draw()
    canv.SaveAs(filename)
    
# start by getting seed number
import sys
SEED = None
for tmp in sys.argv:
    try:
        SEED = int(tmp)
    except ValueError:
        print ('DEBUG: argument %s is no number, trying next argument as'
            'seed') % tmp
if None == SEED:
    print 'ERROR: no seed given'
    sys.exit(1)

# then read config dictionary from a file
from B2DXFitters.utils import configDictFromFile
config = configDictFromFile('decRateCoeff_Bd_conf_MeanRes.py')

print 'CONFIGURATION'
for k in sorted(config.keys()):
    print '    %32s: %32s' % (k, config[k])

# safe settings for numerical integration (if needed)
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

# seed the Random number generator
rndm = TRandom3(SEED + 1)
RooRandom.randomGenerator().SetSeed(int(rndm.Uniform(4294967295)))
del rndm

# define some useful constants
from B2DXFitters.WS import WS

ws = RooWorkspace('ws')
one = WS(ws, RooConstVar('one', '1', 1.0))
zero = WS(ws, RooConstVar('zero', '0', 0.0))

# number of events to generate
nevts = 10000

# define time and its per-event uncertainty
time = WS(ws, RooRealVar('time', 'time [ps]', 0.2, 15.0)) 
timeerr = WS(ws, RooRealVar('timeerr', 'timeerr', 0.001, 0.100))

# define final state charge
qf = WS(ws, RooCategory('qf', 'final state charge'))
qf.defineType('h+', +1)
qf.defineType('h-', -1)

# define list of tagging decision categories
qt_os = WS(ws, RooCategory('qt_os', 'os tagging decision'))
qt_os.defineType(      'B+', +1)
qt_os.defineType('Untagged',  0)
qt_os.defineType(      'B-', -1)
qt_ss = WS(ws, RooCategory('qt_ss', 'ss tagging decision'))
qt_ss.defineType(      'B+', +1)
qt_ss.defineType('Untagged',  0)
qt_ss.defineType(      'B-', -1)
qt = [qt_os, qt_ss]

# define list of mistag observable
# HACK (1/2): be careful about lower bound on eta, since mock mistagpdf
# is zero below a certain value - generation in accept/reject would get
# stuck
mistag_os = WS(ws, RooRealVar('mistag_os', 'mistag_os', (1. + 1e-5) * max(0.0,config['TrivialMistagParams']['omega0']), 0.5))
mistag_ss = WS(ws, RooRealVar('mistag_ss', 'mistag_ss', (1. + 1e-5) * max(0.0,config['TrivialMistagParams']['omega0']), 0.5))
mistagobs = [mistag_os, mistag_ss] 

# define list of calibration parameters
p0_os = WS(ws, RooRealVar('p0_os', 'p0_os', 0.345))
p1_os = WS(ws, RooRealVar('p1_os', 'p1_os', 0.980))
deltap0_os = WS(ws, RooRealVar('deltap0_os', 'deltap0_os', 0.001))
deltap1_os = WS(ws, RooRealVar('deltap1_os', 'deltap1_os', 0.001))
avgeta_os = WS(ws, RooRealVar('avgeta_os', 'avgeta_os', 0.350))
tageff_os = WS(ws, RooRealVar('tageff_os', 'tageff_os', 0.6))
tagasymm_os = WS(ws, RooRealVar('tagasymm_os', 'tagasymm_os', 0.01))

p0_ss = WS(ws, RooRealVar('p0_ss', 'p0_ss', 0.345))
p1_ss = WS(ws, RooRealVar('p1_ss', 'p1_ss', 0.980))
deltap0_ss = WS(ws, RooRealVar('deltap0_ss', 'deltap0_ss', 0.001))
deltap1_ss = WS(ws, RooRealVar('deltap1_ss', 'deltap1_ss', 0.001))
avgeta_ss = WS(ws, RooRealVar('avgeta_ss', 'avgeta_ss', 0.350))
tageff_ss = WS(ws, RooRealVar('tageff_ss', 'tageff_ss', 0.6))
tagasymm_ss = WS(ws, RooRealVar('tagasymm_ss', 'tagasymm_ss', 0.01))

mistagcalib = [ [p0_os, p1_os, deltap0_os, deltap1_os, avgeta_os, tageff_os, tagasymm_os],
    [p0_ss, p1_ss, deltap0_ss, deltap1_ss, avgeta_ss, tageff_ss, tagasymm_ss] ]

# define various CKM and CPV stuff
Gamma  = WS(ws, RooRealVar( 'Gamma',  'Gamma',  0.656)) # ps^-1
DGamma = WS(ws, RooRealVar('DGamma', 'DGamma',  0.0)) # ps^-1
TauInvG     = Inverse( "TauInvG","TauInvG", Gamma)
Dm     = WS(ws, RooRealVar(    'Dm',     'Dm', 0.510)) # ps^-1

S = WS(ws, RooRealVar( 'S',  'S',  0.0))
Sbar = WS(ws, RooRealVar( 'Sbar',  'Sbar', 0.0))
C = WS(ws, RooRealVar( 'C',  'C',  1.0, -4.0, 4.0))
D = WS(ws, RooRealVar( 'D',  'D',  0.0))
Dbar = WS(ws, RooRealVar( 'Dbar',  'Dbar', 0.0))

# define production and detection asymmetries
aprod = WS(ws, RooRealVar('aprod', 'aprod', 0.01)) 
adet = WS(ws, RooRealVar('adet', 'adet', 0.01))

# build mock mistag pdf distributions
mistagpdfparams = {}
for sfx in ('omega0', 'omegaavg', 'f'):
    mistagpdfparams[sfx] = WS(ws, 
	RooRealVar('mistagpdf_%s' % sfx, 
	    'mistagpdf_%s' % sfx, 
	    config['TrivialMistagParams'][sfx]))
    
mistagpdf_os = WS(ws, MistagDistribution(
	'mistagpdf_os', 'mistagpdf_os',
	mistag_os, mistagpdfparams['omega0'], mistagpdfparams['omegaavg'],
	mistagpdfparams['f']))

mistagpdf_ss = WS(ws, MistagDistribution(
        'mistagpdf_ss', 'mistagpdf_ss',
        mistag_ss, mistagpdfparams['omega0'], mistagpdfparams['omegaavg'],
        mistagpdfparams['f']))

mistagpdf = [mistagpdf_os, mistagpdf_ss]

# for now, we're in the generation stage
config['Context'] = 'GEN'

# now build the PDF
from B2DXFitters.timepdfutils_Bd import buildBDecayTimePdf
from B2DXFitters.resmodelutils import getResolutionModel
from B2DXFitters.acceptanceutils import buildSplineAcceptance
from B2DXFitters.utils import setConstantIfSoConfigured

acc, accnorm = buildSplineAcceptance(ws, time, 'acceptance_GEN',
    config['SplineAcceptance']['KnotPositions'],
    config['SplineAcceptance']['KnotCoefficients'][config['Context']],
    False, True)
acc = accnorm #use normalised acceptance for generation
resmodel, acc = getResolutionModel(ws, config, time, timeerr, acc)
terrpdf = None

# build generating pdf
genpdf = buildBDecayTimePdf(
    config, 'GEN-time-pdf', ws,
    time, timeerr, qt, qf, mistagobs, mistagcalib,
    Gamma, DGamma, Dm,
    C, D, Dbar, S, Sbar,
    resmodel, acc,
    terrpdf, mistagpdf,
    aprod, adet)

# generate "proto data" for mistag and time error
proto_data = WS(ws, mistagpdf_os.generate(RooArgSet(mistag_os), nevts))
mistag_ss_data = WS(ws, mistagpdf_ss.generate(RooArgSet(mistag_ss), nevts))
proto_data.merge(mistag_ss_data)

# generate events
obs = RooArgSet(qf, qt_os, qt_ss, time) #if use proto data, don't put mistag/time error observables here!
ds = WS(ws, genpdf.generate(obs, RooFit.ProtoData(proto_data)))
ds.Print('v')
ds.table(qf).Print('v')
ds.table(qt_os).Print('v')
ds.table(qt_ss).Print('v')

# HACK (2/2): restore correct eta range after generation
ds.get().find("mistag_os").setRange(0.0,0.5)
ds.get().find("mistag_ss").setRange(0.0,0.5)

# plot generated dataset + generating pdf
#plotAll(ds,genpdf,qf,qt_os,time,"GenPdfAndDataOS_decRateCoeff_Bd_MeanRes.eps")
#plotAll(ds,genpdf,qf,qt_ss,time,"GenPdfAndDataSS_decRateCoeff_Bd_MeanRes.eps")

# use workspace for fit pdf
config['CONTEXT'] = 'FIT'

acc, accnorm = buildSplineAcceptance(ws, time, 'acceptance_FIT',
    config['SplineAcceptance']['KnotPositions'],
    config['SplineAcceptance']['KnotCoefficients'][config['Context']],
    False, True)
resmodel, acc = getResolutionModel(ws, config, time, timeerr, acc)
terrpdf = None

fitpdf = buildBDecayTimePdf(
    config, 'FIT-time-pdf', ws,
    time, timeerr, qt, qf, mistagobs, mistagcalib,
    Gamma, DGamma, Dm,
    C, D, Dbar, S, Sbar,
    resmodel, acc,
    terrpdf, mistagpdf,
    aprod, adet)

# set constant what is supposed to be constant
setConstantIfSoConfigured(config, fitpdf)

# set up fitting options
fitopts = [ RooFit.Timer(), RooFit.Save(),
            RooFit.Strategy(config['FitConfig']['Strategy']),
            RooFit.Optimize(config['FitConfig']['Optimize']),
            RooFit.Offset(config['FitConfig']['Offset']),
            RooFit.NumCPU(config['FitConfig']['NumCPU']),
            RooFit.PrintLevel(3),
            RooFit.Verbose()]

fitOpts = RooLinkedList()
for o in fitopts: fitOpts.Add(o)

# do fit
rawfitresult = fitpdf.fitTo(ds, fitOpts)
rawfitresult.Print("v")

# plot geterated dataset + fitting pdf
plotAll(ds,fitpdf,qf,qt_os,time,"FitPdfAndDataOS_decRateCoeff_Bd_MeanRes.eps")
plotAll(ds,fitpdf,qf,qt_ss,time,"FitPdfAndDataSS_decRateCoeff_Bd_MeanRes.eps")

# all done!