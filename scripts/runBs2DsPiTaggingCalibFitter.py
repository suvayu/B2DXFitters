#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# --------------------------------------------------------------------------- 
# @file runBs2DsPiTaggingCalibFitter.py
#
# Python script to run a data or toy MC fit for tagging calibration purposes
# in Bs -> Ds Pi
#
# Author: Eduardo Rodrigues                                                 
# Date  : 14 / 06 / 2011                                                    
# - general setup of the framework
#
# @author Manuel Schiller
# @date 2012-02-15 ... ongoing
# - major changes in the framework, lots of additions and enhancements
#
# @author Chiara Farinelli
# @date ca. Aug 2012 - Mar. 2013
# - get OS tagging calibration fits to work
#
# --------------------------------------------------------------------------- 

# This file is used as both a shell script and as a Python script.

""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.

# make sure the environment is set up properly
if test -z "$CMTCONFIG"; then
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
	        LD_PRELOAD="$k"
	        break 3
	    else
	        LD_PRELOAD="$LD_PRELOAD":"$k"
	        break 3
	    fi
	done
    done
done

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((7 * 1024 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from math     import pi
import os, sys

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

# -----------------------------------------------------------------------------
# Configuration settings
#
# defaultConfig contains default settings
# generatorConfig contains settings to use during generation
# fitConfig contains settings to use during fit
#
# fitConfig and generatorConfig can be updated to suit your needs
# there are two ways: either by inserting code below (see example), or by
# using job options (which take a string or a file with python code which
# must evaluate to a dictionary)
# -----------------------------------------------------------------------------
defaultConfig = {
	'DoDsK':			True,
	'DoDsPi':			True,
	# truth/Gaussian/DoubleGaussian/GaussianWithPEDTE/GaussianWithLandauPEDTE/GaussianWithScaleAndPEDTE/TripeGaussian
	'DecayTimeResolutionModel':	'TripleGaussian',
	'DecayTimeResolutionBias':	0.,
	'DecayTimeResolutionScaleFactor': 1.,        
	# None/BdPTAcceptance/DTAcceptanceLHCbNote2007041/PowLawAcceptance
	'AcceptanceFunction':		'PowLawAcceptance',
	# acceptance parameters PowLawAcceptance
	'PowLawAcceptance_turnon':	 1.538,
	'PowLawAcceptance_offset':	-0.005,
	'PowLawAcceptance_expo':	 2.031,
	'PowLawAcceptance_beta':	 0.037,

	'PerEventMistag': 		False,
	'UseKFactor':			False,

        #parameters for Gaussian resolution models
        'ResModelGaussMeans'     : [],
        'ResModelGaussWidths'    : [],
        'ResModelGaussSFMeans'   : [],
        'ResModelGaussSFWidths'  : [],
        'ResModelGaussFractions' : [],

	# BLINDING
	'Blinding':			True,

	# PHYSICAL PARAMETERS
	'Gammad':			0.656, # in ps^{-1}
	'Gammas':			0.679, # in ps^{-1}
	'DeltaGammad':			0.,    # in ps^{-1}
	'DGsOverGs':			-0.17629, # DeltaGammas / Gammas
	'DeltaMd':			0.507, # in ps^{-1}
	'DeltaMs':			17.77, # in ps^{-1}

	# TOY PARAMETERS
	# If doing an extended likelihood fit
	'NSigEvts':			1600, # signal events
	'NBs2DsPiEvts':			26000, #800, # Bs -> Ds pi phys. bkg. events
	# Tagging
	'TagEffSig':			0.6123,
	'TagOmegaSig':			0.360933,
        'ForceAllUntagged':		False, # forcibly sets all events untagged
	# CP observables
	'StrongPhase':			0. / 180. * pi,
	'WeakPhase':			70. / 180. * pi,
	'ModLf':			0.372,
	# list of constant parameters
	'constParams': [
            'av_omega',
	    'Gammas', 'deltaGammas', #'deltaMs',
	    'tacc_turnon', 'tacc_beta', 'tacc_expo', 'tacc_offset',
	    #'tagOmegaSig',
	    'tagEffSig',
            'nBs2DsPiEvts'
	    ],
        'MistagCatBinBounds' :   None,
        'Optimize': 2,
        'Strategy': 2,
        'IsToy': True,
        'DataFileName': None,
        'TreeName': None,
        'Blinding': True,
        #bug-for-bug compatibility flags
        'BugFlags': [ ],
        'NBinsAcceptance': 0,
	'OnlyInMassWindow': False
	}

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------
# pretty-print fit results, optionally blinding all parameters
def printResult(config, result, blind = False):
    from ROOT import RooFitResult
    # read parameters and errors from fit result
    ini = result.floatParsInit()
    fin = result.floatParsFinal()
    iv = {}
    fv = {}
    fe = {}
    fbu = {}
    fbl = {}
    correl = {}
    it = ini.createIterator()
    ROOT.SetOwnership(it, True)
    while True:
        obj = it.Next()
        if None == obj: break
        iv[obj.GetName()] = obj.getVal()
    del it
    it = fin.createIterator()
    ROOT.SetOwnership(it, True)
    while True:
        obj = it.Next()
        if None == obj: break
        fv[obj.GetName()] = obj.getVal()
        fe[obj.GetName()] = obj.getError()
        fbl[obj.GetName()] = obj.getMin()
        fbu[obj.GetName()] = obj.getMax()
    del it
    for v1 in iv.keys():
	if v1 not in correl:
	    correl[v1] = {}
	for v2 in iv.keys():
	    correl[v1][v2] = result.correlation(v1, v2)
    # apply bug fixes (if needed)
    if 'OutputCompatSSbarSwapMinusOne' in config['BugFlags']:
	for vn in fv.keys():
	    if not vn.endswith('_Sbar'):
		continue
	    # swap all S and Sbar values, multiply each with minus one
	    on = vn.rstrip('_Sbar') + '_S'
	    for a in [iv, fv]:
		a[on], a[vn] = -a[vn], -a[on]
	    # swap S and Sbar bounds and errors (no multiplication with -1!)
	    for a in [fe, fbl, fbu]:
		a[on], a[vn] = a[vn], a[on]
	    # apply swapping to correlation matrix (no multiplication with -1!)
	    for wn in fv.keys():
		correl[wn][vn], correl[wn][on] = correl[wn][on], correl[wn][vn]
	    for wn in fv.keys():
		correl[vn][wn], correl[on][wn] = correl[on][wn], correl[vn][wn]
    # ok, print the result
    print ''
    print 'FIT RESULT: FCN % 12.6g STATUS % 2d COV QUAL % 2d EDM %12.6g' % (
        result.minNll(), result.status(), result.covQual(), result.edm())
    print ''
    print '%3s %-16s %12s %12s %12s' % (
        'PAR', 'NAME', 'INI. VALUE', 'FIT VALUE', 'ERROR' )
    print ''
    i = 0
    for var in sorted(fv.keys()):
        cmt = ''
        if fbl[var] >= fv[var] or fbu[var] <= fv[var]:
            cmt = '*** AT LIMIT ***'
        val = '% 12.6g' % fv[var]
        if blind:
            val = 'XXXX.XXX'
        print '% 3u %-16s % 12.6g %12s %12.6g %s' % (
            i, var, iv[var], val, fe[var], cmt )
        i = i + 1
    del i
    print ''
    print 'CORRELATION MATRIX:'
    print ''
    hdrline = '   '
    i = 0
    cov = []
    for var1 in sorted(correl.keys()):
        hdrline = hdrline + ' % 6d' % i
        line = '%3u' % i
        i = i + 1
        for var2 in sorted(correl.keys()):
    	    line = line + ' % 6.3f' % correl[var1][var2]
	cov.append(line)
    del i
    print hdrline
    for line in cov:
        print line

#------------------------------------------------------------------------------
def setConstantIfSoConfigured(config, obj):
    from ROOT import RooAbsPdf
    if obj.InheritsFrom(RooAbsPdf.Class()):
	i = obj.getVariables().iterator()
	o = i
	while None != o:
	    o = i.Next()
	    if None != o:
		setConstantIfSoConfigured(config, o)
    else:
	if obj.GetName() in config['constParams']:
	    obj.setConstant(True)

#------------------------------------------------------------------------------
# "swallow" object into a workspace, returns swallowed object
def WS(ws, obj, opts = [RooFit.RecycleConflictNodes()]):
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

#------------------------------------------------------------------------------
def getResModel(config,
                time,
                ws):
    from ROOT import RooArgList, RooGaussModel, RooAddModel, RooRealVar

    models = RooArgList()
    fractions = RooArgList()

    if len(config['ResModelGaussMeans']) != len(config['ResModelGaussWidths']):
        print 'Error: The number of means and widths of the Gaussian Resolution models are not equal'
        return None
    if len(config['ResModelGaussMeans']) > len(config['ResModelGaussFractions'])+1:
        print 'Error: Not every Gaussian Resolution model has a fraction assigned to it'
        return None
    for i in xrange(0, len(config['ResModelGaussWidths'])):
        mean  = WS(ws, RooRealVar('mean_%d' %i, 'mean_%d' %i, config['ResModelGaussMeans'][i]))
        width = WS(ws, RooRealVar('width_%d' %i, 'width_%d' %i, config['ResModelGaussWidths'][i]))
        if i < len(config['ResModelGaussSFMeans']):
            SFmean = config['ResModelGaussSFMeans'][i]
        else:
            SFmean = 1.0
        if i < len(config['ResModelGaussSFWidths']):
            SFwidth = config['ResModelGaussSFWidths'][i]
        else:
            SFwidth = 1.0
        SFmean  = WS(ws, RooRealVar('scalefactor_mean_%d' %i, 'scalefactor_mean_%d' %i, SFmean))
        SFwidth = WS(ws, RooRealVar('scalefactor_width_%d' %i, 'scalefactor_width_%d' %i, SFwidth))
        models.add(WS(ws, RooGaussModel('GaussianResModel_%d' %i, 'GaussianResModel_%d' %i,
                                        time, mean, width, SFmean, SFwidth)))
        if i < len(config['ResModelGaussFractions']):
            fractions.add(WS(ws, RooRealVar('fraction_model_%d' %i, 'fraction_model_%d' %i,
                                            config['ResModelGaussFractions'][i])))

    return WS(ws, RooAddModel('FullResolutionModel', 'FullResolutionModel', models, fractions))

#------------------------------------------------------------------------------
def readTree(config, dsname, variables, weights, qf, qt, eta):
    filename = config['DataFileName']
    treename = config['TreeName']
    catbinbounds = config['MistagCatBinBounds']
    from ROOT import TFile, TTree, RooDataSet, RooArgSet, RooRealVar, TRandom3
    import ctypes
    from math import sqrt
    # guess sWeight branch names based on category passed in with '*_idx'
    thekey = None
    nkeys = 0
    for k in variables.keys():
        if not '_idx' in k: continue
        thekey = k
        nkeys = nkeys + 1
    if not (1 < nkeys or 0 >= nkeys or None == thekey):
        if config['OnlyInMassWindow']:
	    print 'Only using events in mass window, getting rid of sample index and sweights'
            variables.pop(thekey)
            thekey = None
            nkeys = 0
    if 1 < nkeys or 0 >= nkeys or None == thekey:
	print 'No sample index branch found! Continuing, assuming MC tuples.'
	samplecat = None
	swmap = {}
    else:
        samplecat = variables[thekey]
        cit = samplecat.typeIterator()
        ROOT.SetOwnership(cit, True)
        # figure out relation between index category number and branch name for
        # sweights
        swmap = {}
        obj = cit.Next()
        while None != obj:
    	    str = obj.GetName()
    	    str = str.split('_')
    	    pol = None
    	    if 'up' in str: pol = 'up'
    	    elif 'down' in str: pol = 'down'
    	    dsmode = None
    	    for dsm in [ 'kkpi', 'kpipi', 'pipipi' ]:
    	        if dsm in str:
    	   	   dsmode = dsm
    	    	   break
    	    if None == pol or None == dsmode:
    	        print 'Could not figure out (polarity, Ds decay mode)'
    	        return None
    	    swmap[obj.getVal()] = 'nSig_%s_%s_Evts_sw' % (pol, dsmode)
    	    obj = cit.Next()
    # open root file and get tree
    f = TFile(filename, 'READ')
    if f.IsZombie():
	print 'Unable to open tuple file %s' % filename
	return None
    tree = f.Get(treename)
    if not tree.InheritsFrom('TTree'):
	print 'Object %s in file %s either not found or not a tree' % (
		treename, filename)
	return None
    # build branches
    lvars = {}
    additionalBranches = []
    if None != tree.FindLeaf('B_TRUE_DEC'):
        additionalBranches.append('B_TRUE_DEC')
    if config['OnlyInMassWindow']:
        additionalBranches.append('lab0_MassFitConsD_M')
    for k in variables.keys() + swmap.values() + additionalBranches:
        print k
	typename = tree.FindLeaf(k).GetTypeName()
	if typename in [ 'int', 'Int_t']:
	    lvars[k] = ctypes.c_int(0)
	elif typename in [ 'double', 'Double_t' ]:
	    lvars[k] = ctypes.c_double(0.)
	elif typename in [ 'float', 'Float_t' ]:
	    lvars[k] = ctypes.c_float(0.)
	else:
	    print 'Unknown type "%s" for branch "%s"' % (typename, k)
	    return None
    for k in variables.keys() + swmap.values() + additionalBranches:
	tree.SetBranchAddress(k, lvars[k])
    # create dataset to return
    if 0 == len(swmap):
        ds = RooDataSet(dsname, dsname, RooArgSet(*variables.values()))
    else:
        ds = RooDataSet(dsname, dsname, RooArgSet(weights, *variables.values()),
		weights.GetName())
    # loop over tuple
    avgmistag = 0.
    sumweights = 0.
    sumweightserr2 = 0.
    sumweightsall = 0.
    sumweightsallerr2 = 0.
    avpercat = [ ]
    sumpercat = [ ]
    if 1 < len(catbinbounds):
        for i in xrange(0, len(catbinbounds) - 1):
            avpercat.append(0.)
            sumpercat.append(0.)
    for i in xrange(0, tree.GetEntries()):
	tree.GetEntry(i)
	idx = None
	# assign values read from tuple to RooFit objects (with some
	# preprocessing)
	for k in lvars:
	    if k not in variables: continue
            # fix predicted mistag for untagged events
	    if ('TAGDECISION' in k or 'DEC' in k):
		if 0 == int(lvars[k].value):
		    etaname = None
		    if 'TAGDECISION' in k:
		        etaname = k.replace('TAGDECISION', 'TAGOMEGA')
		    elif 'TRUE_DEC' in k:
		        etaname = k.replace('TRUE_DEC', 'OST_OMEGA')
                    elif 'DEC' in k:
		        etaname = k.replace('DEC', 'OMEGA')
		    if not etaname in lvars: continue
		    lvars[etaname].value = 0.5
	    # further postprocessing
	    if ctypes.c_int == type(lvars[k]):
		# things saved as integers are assumed to be categories on the
		# RooFit side without any need for preprocessing
		variables[k].setIndex(lvars[k].value)
		if '_idx' in k:
                    # make sure only one branch fits the description
		    if None != idx:
			return None
		    idx = lvars[k].value
	    elif variables[k].InheritsFrom('RooAbsCategoryLValue'):
	        # things saved as doubles and to be saved to categories need
		# preprocessing (final state charge, tagging decisions)
		v = 0
		if lvars[k].value > 0: v = +1
		elif lvars[k].value < 0: v = - 1
		variables[k].setIndex(v)
	    else:
                # everything else goes from double to RooRealVar or similar,
		# so only the lifetime needs to have that annoying factor of c
		# (expressed in funny units) taken out
		if 'ctau' in k:
		    lvars[k].value = lvars[k].value * 1e9 / 299792458.
                elif 'TAU' in k:
		    lvars[k].value = lvars[k].value * 1e3
                if lvars[k].value < variables[k].getMin() or \
			lvars[k].value > variables[k].getMax():
                    continue
                variables[k].setVal(lvars[k].value)
        # get sWeight from right branch
	if None != idx and None != samplecat:
            # make sure it's a known sample index
	    if not idx in swmap:
		print 'Unknown sample index found in tuple'
		return None
	    weights.setVal(lvars[swmap[idx]].value)
	    # make sure the other sweights are all zero
	    nzero = 0
	    for k in swmap.values():
		if k == swmap[idx]: continue
		if 0. == abs(lvars[k].value): nzero = nzero + 1
	    if 1 + nzero != len(swmap):
		print 'mapping between sample index number and sample %s' % \
		    'label does not seem to match'
		return None
        if config['OnlyInMassWindow']:
            mass = lvars['lab0_MassFitConsD_M'].value
            if 5320. > mass or 5420. < mass:
                continue
        # get average sweighted mistag over whole data set
	if 'B_TRUE_DEC' in additionalBranches:
            sumweightsall += 1.
            sumweightsallerr2 += 1.
        else:
            sumweightsall += weights.getVal()
            sumweightsallerr2 += abs(weights.getVal())
        if 0 != qt.getIndex():
            if 'B_TRUE_DEC' in additionalBranches:
	        iswrong = 0.
		if lvars['B_OST_DEC'].value != lvars['B_TRUE_DEC'].value:
                    iswrong = 1.
                avgmistag += iswrong
                sumweights += 1.
                sumweightserr2 += 1.
	    else:
                avgmistag += eta.getVal() * weights.getVal()
                sumweights += weights.getVal()
                sumweightserr2 += abs(weights.getVal())
            for i in xrange(0, len(catbinbounds) - 1):
                if catbinbounds[i + 1] < eta.getVal(): continue
                if catbinbounds[i] > eta.getVal(): break
                if 'B_TRUE_DEC' in additionalBranches:
		    iswrong = 0.
		    if lvars['B_OST_DEC'].value != lvars['B_TRUE_DEC'].value:
                        iswrong = 1.
		    avpercat[i] += iswrong
                    sumpercat[i] += 1.
		else:
                    avpercat[i] += eta.getVal() * weights.getVal()
                    sumpercat[i] += weights.getVal()
                break
        if config['ForceAllUntagged']:
            qt.setIndex(0)
            eta.setVal(0.5)
	# put variables into dataset
        if 0 == len(swmap):
            if 'B_TRUE_DEC' in additionalBranches:
                qt.setIndex(- qt.getIndex() * qf.getIndex())
	    ds.add(RooArgSet(*variables.values()))
        else:
	    ds.add(RooArgSet(weights, *variables.values()), weights.getVal(), 0.)
    # loop over events done, return dataset
    if 0. < sumweights:
        print 'Average mistag in dataset is %g' % (avgmistag / sumweights)
    etapercat = []
    for i in xrange(0, len(catbinbounds) - 1):
        if 0. < sumpercat[i]:
            etapercat.append(avpercat[i] / sumpercat[i])
            print 'Average mistag in category %u is %g' % (i, etapercat[i])
    print
    print 'Total signal yield: %f +/- %f' % (sumweightsall,
	    sqrt(sumweightsallerr2))
    print 'Tagging efficiency: %f +/- %f' % (
           sumweights/sumweightsall,
           sumweights/sumweightsall * sqrt(
	       sumweightserr2 / sumweights / sumweights +
	       sumweightsallerr2 / sumweightsall / sumweightsall))
    return { 'dataset': ds, 'etapercat': etapercat }

#------------------------------------------------------------------------------
def buildBDecayTimePdf(
	name,					# 'Signal', 'DsPi', ...
	ws,	       			# RooWorkspace into which to put the PDF
	time, timeerr, qt, qf, mistag, tageff,	# potential observables
	Gamma, DeltaGamma, DeltaM,		# decay parameters
	C, D, Dbar, S, Sbar,			# CP parameters
	timeresmodel = None,			# decay time resolution model
	acceptance = None,			# acceptance function
	timeerrpdf = None,			# pdf for per event time error
	mistagpdf = None,			# pdf for per event mistag
	kfactorpdf = None,			# distribution k factor smearing
	kvar = None,				# variable k which to integrate out
        mistagCatBounds = None,
        mistagCatOmegas = None,

      	nBinsPerEventTimeErr = 128,	# parameterize time integral in bins of time err
	nBinsAcceptance = 0		# approximate acceptance function in bins
	):
    # Look in LHCb-INT-2011-051 for the conventions used
    from ROOT import ( RooConstVar, TagEfficiencyWeight, IfThreeWayCat,
	    Dilution, RooProduct, RooTruthModel, RooGaussModel, Inverse,
	    RooBDecay, RooProdPdf, RooBinnedPdf, RooEffHistProd, RooEffProd,
	    RooUniformBinning, RooArgSet, RooFit, RooWorkspace,
	    RooNumGenSmearPdf, TaggingCat, RooBinning, RooBinningCategory,
            RooArgList, RooCategory, DecRateCoeff, RooEffResModel, RooUniformBinning )
    from ROOT import std
    from ROOT import gPad

    if None != mistagpdf:
        mfr = mistag.frame()
        mistagpdf.plotOn(mfr)
        mfr.Draw()
        gPad.Print('mistagpdf.eps')


    # constants used
    zero = WS(ws, RooConstVar('zero', 'zero', 0.))
    one = WS(ws, RooConstVar('one', 'one', 1.))
    two = WS(ws, RooConstVar('two', 'two', 2.))
    minusone = WS(ws, RooConstVar('minusone', 'minusone', -1.))

    # if no time resolution model is set, fake one
    if timeresmodel == None:
	timeresmodel = WS(ws, RooTruthModel('%s_TimeResModel' % name,
	    '%s time resolution model' % name, time))
    elif timeresmodel == 'Gaussian':
	timeresmodel = WS(ws, RooGaussModel('%s_TimeResModel' % name,
	    '%s time resolution model' % name, time, zero, timeerr))
    if None != timeresmodel and nBinsAcceptance > 0 and None != acceptance:

        # bin acceptance
        acceptanceBinning = WS(ws, RooUniformBinning(
            time.getMin(), time.getMax(), nBinsAcceptance,
            'acceptanceBinning'))
        time.setBinning(acceptanceBinning, 'acceptanceBinning')
        if not acceptance.isBinnedDistribution(RooArgSet(time)):
            acceptance = WS(ws, RooBinnedPdf('%s_binned' % acceptance.GetName(),
                                             'binned %s' % acceptance.GetTitle(),
                                             time, 'acceptanceBinning', acceptance))
            acceptance.setForceUnitIntegral(True)
        timeresmodel = WS(ws, RooEffResModel(
            '%s_timeacc_%s' % (timeresmodel.GetName(), acceptance.GetName()),
            '%s_timeacc_%s' % (timeresmodel.GetName(), acceptance.GetName()),
            timeresmodel, acceptance))
    if None != mistagCatBounds:
        if None == mistagCatOmegas:
            bins = std.vector('double')()
            for bound in mistagCatBounds:
                bins.push_back(bound)
            binning = RooBinning(len(mistagCatBounds) - 1, bins.begin().base(),
			    'taggingCat')
            mistag.setBinning(binning, 'taggingCat')
            cat = WS(ws, RooBinningCategory('tagcat', 'tagcat',
				    mistag, 'taggingCat'))
	    realmistag = mistag
	else:
	    cat = WS(ws, RooCategory('tagcat', 'tagcat'))
            mistags = RooArgList()
            for mt in mistagCatOmegas:
	        cat.defineType(mt.GetName(), mistags.getSize())
                mistags.add(mt)
            perCatmistag = WS(ws, TaggingCat('%s_perCatmistag' % name, '%s_perCatmistag' % name,
				    qt, cat, mistags))
            perCatmistag.Print('v')
            realmistag = perCatmistag
    else:
        realmistag = mistag

#============================================================================
    # terms to go into RooBDecay
    if None != mistagpdf:
        otherargs = [ mistag, mistagpdf, tageff, realmistag, zero, zero, zero, zero ]
    else:
        otherargs = [ tageff, realmistag, zero, zero, zero, zero ]
    cosh = WS(ws, DecRateCoeff('%sCosh' % name, '%sCosh' % name,
                               DecRateCoeff.CPEven, qf, qt, one, one, *otherargs))
    sinh = WS(ws, DecRateCoeff('%sSinh' % name, '%sSinh' % name,
                             DecRateCoeff.CPEven, qf, qt, D, Dbar, *otherargs))
    cos  = WS(ws, DecRateCoeff('%sCos' % name, '%sCos' % name,
                            DecRateCoeff.CPOdd, qf, qt, C, C, *otherargs))
    sin = WS(ws, DecRateCoeff('%sSin' % name, '%sSin' % name,
                            DecRateCoeff.CPOdd | DecRateCoeff.Minus, qf, qt, S, Sbar, *otherargs))
    del otherargs


#=============================================================================


    # perform the actual k-factor smearing integral (if needed)
    # if we have to perform k-factor smearing, we need "smeared" variants of
    # Gamma, DeltaGamma, DeltaM
    if None != kfactorpdf and None != kvar:
	kGamma = WS(ws, RooProduct('%sKGamma' % name, '%s k * #Gamma' % name,
	    RooArgSet(kvar, Gamma)))
	kDeltaGamma = WS(ws, RooProduct('%sKDeltaGamma' % name,
	    '%s k * #Delta#Gamma' % name, RooArgSet(kvar, DeltaGamma)))
	kDeltaM = WS(ws, RooProduct('%sKDeltaM' % name,
	    '%s k * #Delta m' % name, RooArgSet(kvar, DeltaM)))
    else:
	# otherwise, we can get away with giving old variables new names
	kGamma, kDeltaGamma, kDeltaM = Gamma, DeltaGamma, DeltaM

    # perform the actual k-factor smearing integral (if needed)
    # build (raw) time pdf
    tau = WS(ws, Inverse('%sTau' % name, '%s #tau' % name, kGamma))
    rawtimepdf = WS(ws, RooBDecay('%s_RawTimePdf' % name,
	'%s raw time pdf' % name, time, tau, kDeltaGamma, cosh, sinh, cos, sin,
	kDeltaM, timeresmodel, RooBDecay.SingleSided))

    # perform the actual k-factor smearing integral (if needed)
    if None != kfactorpdf and None != kvar:
	krawtimepdf = WS(ws, RooNumGenSmearPdf('%s_kSmearedRawTimePdf' % name,
	    '%s raw time pdf smeared with k factor' % name,
	    kvar, rawtimepdf, kfactorpdf))
	krawtimepdf.setConvolutionWindow(one, one, 0.005)
        krawtimepdf.convIntConfig().setEpsAbs(1e-9)
        krawtimepdf.convIntConfig().setEpsRel(1e-9)
	krawtimepdf.convIntConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','WynnEpsilon')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000000)
    else:
	krawtimepdf = rawtimepdf

    # figure out if we need a conditional pdf product for per event
    # decay time error or per event realmistag
    condpdfs = [ ]
    parameterizeSet =[ ]
    if None != timeerrpdf:
	condpdfs.append(timeerrpdf)
	if 0 < nBinsPerEventTimeErr:
	    parameterizeSet.append(timeerr)
	    timeerr.setBins(nBinsPerEventTimeErr, 'cache')

    # perform conditional pdf product if needed
    if 0 < len(condpdfs):
        noncondset = RooArgSet(time, qf, qt)
        if None != mistagpdf:
            noncondset.add(mistag)
	if 0 < len(parameterizeSet):
	    krawtimepdf.setParameterizeIntegral(RooArgSet(*parameterizeSet))
	timenoaccpdf = WS(ws, RooProdPdf('%s_NoAccTimePdf' % name,
	    '%s no-acceptance time pdf', RooArgSet(*condpdfs),
	    RooFit.Conditional(RooArgSet(krawtimepdf), noncondset)))
    else:
	timenoaccpdf = krawtimepdf
    
    # apply acceptance (if needed)
    if None == acceptance:
	retVal = timenoaccpdf
    else:
        if 0 < nBinsAcceptance:
            retVal = timenoaccpdf
        else:
	    # do not bin acceptance
	    retVal = WS(ws, RooEffProd('%s_TimePdf' % name,
		'%s full time pdf' % name, timenoaccpdf, acceptance))

    # return the copy of retVal which is inside the workspace
    return retVal

def calculateAverageMistagPerCat(config, tagOmegaSig, sigMistagPDF, binbounds):
    from ROOT import RooProduct, RooArgSet
    if config['IsToy']:
        #========== product between 'tagOmegaSig' and 'sigMistagPDF' =======================
        Omega_times_mistagPDF = RooProduct('Omega_times_mistag',
            	    'Omega times per_event_mistag PDF',
            	    RooArgSet(tagOmegaSig, sigMistagPDF))
        #===== casting 'tagOmegaSig' as a RooArgSet (not automatic in python) ====
        mistagSig = RooArgSet(tagOmegaSig)
        #======== integrating 'mistag_pdf' over the different ranges =============
        oldrangemin, oldrangemax, oldval = tagOmegaSig.getMin(), tagOmegaSig.getMax(), tagOmegaSig.getVal()
        percatmistags = []
        percatweights = []
        # second argument is normalisation variable (i.e. RooFit takes care of
        # dividing by integral over pdf)
        ipdf = sigMistagPDF.createIntegral(mistagSig)
        ipdf_mistag = Omega_times_mistagPDF.createIntegral(mistagSig, mistagSig)
        for i in xrange(0, len(binbounds) - 1):
            tagOmegaSig.setRange(binbounds[i], binbounds[i + 1])
            print 'mistag bin %4u from %12.8g to %12.8g pdf avg omega %12.8g' % (
           		 i, binbounds[i], binbounds[i + 1], ipdf_mistag.getVal() )
            # save per category mistag
            percatmistags.append(ipdf_mistag.getVal())
            # save population in category (in arbitrary units)
            percatweights.append(ipdf.getVal())
        tagOmegaSig.setRange(oldrangemin, oldrangemax)
        tagOmegaSig.setVal(oldval)
        print 'all mistag bins from %12.8g to %12.8g pdf avg omega %12.8g' % (
        	oldrangemin, oldrangemax, ipdf_mistag.getVal() )
        s = 0.
        
        for i in xrange(0, len(percatmistags)):
            s += percatmistags[i] * percatweights[i]
        s /= sum(percatweights)
        print 'sum over categories                                   avg omega %12.8g' % s
    else:
        percatmistags = []
        for i in xrange(0, len(binbounds) - 1):
            percatmistags.append(.5 * (binbounds[i] + binbounds[i + 1]))
    return { 'percat': percatmistags }

#------------------------------------------------------------------------------
def getMasterPDF(config, name, debug = False):
    from B2DXFitters import taggingutils, cpobservables

    GeneralModels = GaudiPython.gbl.GeneralModels
    PTResModels   = GaudiPython.gbl.PTResModels

    from ROOT import RooGlobalFunc
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooMultiCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay
    from ROOT import RooGaussModel, RooTruthModel
    from ROOT import RooAbsReal, RooWorkspace, RooAbsArg
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf
    from ROOT import RooExponential, RooPolynomial, RooPolyVar, RooUniform
    from ROOT import RooFit, RooUniformBinning
    from ROOT import IfThreeWayCat, Dilution, IfThreeWayCatPdf
    from ROOT import BdPTAcceptance, MistagDistribution, RangeAcceptance, PowLawAcceptance
    from ROOT import RooBinnedPdf, RooEffHistProd

    ws = RooWorkspace('WS_%s' % name)

    # tune integrator configuration
    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','WynnEpsilon')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 100000)

    zero = WS(ws, RooConstVar('zero', '0', 0.))
    one = WS(ws, RooConstVar('one', '1', 1.))
    minusone = WS(ws, RooConstVar('minusone', '-1', -1.))
    two = WS(ws, RooConstVar('two', '2', 2.))

    time = WS(ws, RooRealVar('time', '%s decay time' % bName, 1., 0.2, 15., 'ps'))
    timeerr = WS(ws, RooRealVar('timeerr', '%s decay time error' % bName,
	0.04, 0.001, 0.1, 'ps'))
    
    mBs = WS(ws, RooConstVar('mBs', 'Bs mass', 5.3663))
    mBsmisrec = WS(ws, RooConstVar('mBsmisrec', 'Bs mass', 5.3663 + 0.1))
    mWidth = WS(ws, RooConstVar('mWidth', 'mWidth', 0.03))
    mWidthmisrec = WS(ws, RooConstVar('mWidthmisrec', 'mWidthmisrec', 0.07))
    
    gammas = WS(ws, RooRealVar('Gammas', '%s average lifetime' % bName,
	config['Gammas'], 0., 5., 'ps^{-1}'))
    deltaGammas = WS(ws, RooRealVar('deltaGammas', 'Lifetime difference',
	config['DGsOverGs'] * config['Gammas'], -1., 1., 'ps^{-1}'))

    if config['UseKFactor']:
	k = WS(ws, RooRealVar('k', 'k factor', 1.))
        tiny = WS(ws, RooConstVar('tiny', 'tiny', 1e-3))
        kfactorpdf = WS(ws, RooGaussian('kfactorpdf', 'kfactorpdf', k, one, tiny))
    else:
        k = kfactorpdf = None
    
    deltaMs = WS(ws, RooRealVar('deltaMs', '#Delta m_{s}',
	config['DeltaMs'], 5., 30., 'ps^{-1}'))
    
    tagEffSig = WS(ws, RooRealVar(
	    'tagEffSig', 'Signal tagging efficiency',
	    config['TagEffSig'], 0., 1.))
    tagOmegaSig = WS(ws, RooRealVar(
	    'tagOmegaSig', 'Signal mistag rate',
	    config['TagOmegaSig'], 0., 1.))
  
    qt = WS(ws, RooCategory('qt', 'flavour tagging result'))
    qt.defineType('B'       ,  1)
    qt.defineType('Bbar'    , -1)
    qt.defineType('Untagged',  0)

    qf = WS(ws, RooCategory('qf', 'bachelor charge'))
    qf.defineType('h+',  1)
    qf.defineType('h-', -1)

    # Define the observables
    # ----------------------
    observables = [ time, qt, qf ]
    condobservables = [ ]

    # List of constraints to pass to the fitting stage
    constraints = [ ]
    
    # Decay time resolution model
    # ---------------------------
    if 'PEDTE' not in config['DecayTimeResolutionModel']:
        if 'MultiGaussian' == config['DecayTimeResolutionModel']:
            trm = getResModel(config, time, ws)
        else:
            trm = WS(ws, PTResModels.getPTResolutionModel(
                config['DecayTimeResolutionModel'],
                time, 'Bs', debug,
                config['DecayTimeResolutionScaleFactor'],
                config['DecayTimeResolutionBias']))
    else :
        # the decay time error is an extra observable!
        observables.append(timeerr)
        # time, mean, scale, timeerr
        trm = WS(ws, RooGaussModel('GaussianWithLandauPEDTE',
	    'GaussianWithLandauPEDTE',
	    time, RooFit.RooConst(0.), RooFit.RooConst(1.), timeerr ))
 
    # Decay time acceptance function
    # ------------------------------
    if 'BdPTAcceptance' == config['AcceptanceFunction']:
        tacc_slope  = WS(ws, RooRealVar('tacc_slope' , 'BdPTAcceptance_slope' , 2.36))
        tacc_offset = WS(ws, RooRealVar('tacc_offset', 'BdPTAcceptance_offset', 0.2))
        tacc_beta = WS(ws, RooRealVar('tacc_beta', 'BdPTAcceptance_beta', 0.0))
        tacc = WS(ws, BdPTAcceptance('BsPTAccFunction', '%s decay time acceptance function' % bName,
                              time, tacc_beta, tacc_slope, tacc_offset))
    elif 'PowLawAcceptance' == config['AcceptanceFunction']:
        tacc_beta = WS(ws, RooRealVar('tacc_beta', 'tacc_beta',
                config['PowLawAcceptance_beta'], -0.1, 0.1))
        tacc_expo = WS(ws, RooRealVar('tacc_expo', 'tacc_expo',
		config['PowLawAcceptance_expo'], 0.5, 4.))
        tacc_offset = WS(ws, RooRealVar('tacc_offset', 'tacc_offset',
		config['PowLawAcceptance_offset'], -1., 1.))
        tacc_turnon = WS(ws, RooRealVar('tacc_turnon', 'tacc_turnon',
		config['PowLawAcceptance_turnon'], 0.5, 5.))
        tacc = WS(ws, PowLawAcceptance('PowLawAcceptance',
		    'decay time acceptance', tacc_turnon, time, tacc_offset,
		    tacc_expo, tacc_beta))
    elif None == config['AcceptanceFunction'] or 'None' == config['AcceptanceFunction']:
        tacc = None
    else:
        print 'ERROR: unknown acceptance function: ' + config['AcceptanceFunction']
        sys.exit(1)
    
    # Decay time error distribution
    # -----------------------------
    if 'PEDTE' in config['DecayTimeResolutionModel']:
        #terrpdf_mean  = WS(ws, RooConstVar( 'terrpdf_mean' , 'terrpdf_mean' ,  0.04 ))
        #terrpdf_sigma = WS(ws, RooConstVar( 'terrpdf_sigma', 'terrpdf_sigma',  0.02 ))
        #terrpdf = WS(ws, RooLandau( 'terrpdf', '%s decay time error PDF',
        #                     timeerr, terrpdf_mean, terrpdf_sigma ))

	# resolution in ps: 3/terrpdf_shape
        terrpdf_shape = WS(ws, RooConstVar('terrpdf_shape', 'terrpdf_shape', -60.))
        terrpdf_truth = WS(ws, RooTruthModel('terrpdf_truth', 'terrpdf_truth', timeerr))
        terrpdf_i0 = WS(ws, RooDecay('terrpdf_i0', 'terrpdf_i0', timeerr, terrpdf_shape,
                terrpdf_truth, RooDecay.SingleSided))
        terrpdf_i1 = WS(ws, RooPolynomial('terrpdf_i1','terrpdf_i1',
                timeerr, RooArgList(zero, zero, one), 0))
        terrpdf = WS(ws, RooProdPdf('terrpdf', 'terrpdf', terrpdf_i0, terrpdf_i1))

        #terrpdf_mean  = WS(ws, RooConstVar( 'terrpdf_mean' , 'terrpdf_mean' , 0.03 ))
        #terrpdf_sigma = WS(ws, RooConstVar( 'terrpdf_sigma', 'terrpdf_sigma', 0.01 ))
        #terrpdf = WS(ws, RooGaussian( 'terrpdf', 'terrpdf',
        #                       timeerr, terrpdf_mean, terrpdf_sigma ))
    else:
	terrpdf = None
    
    bins = config['MistagCatBinBounds']
    if None == bins or len(bins) < 2:
        bins = None
	avgmistags = None
    else:
	sigMistagOmega0 = RooConstVar('sigMistagOmega0', 'sigMistagOmega0',
			0.07)
	sigMistagOmegaAvg = RooConstVar('sigMistagOmegaAvg',
			'sigMistagOmegaAvg', config['TagOmegaSig'])
	sigMistagFracHalf = RooConstVar('sigMistagFracHalf',
			'sigMistagFracHalf', 0.25)
	sigMistagPDF = MistagDistribution('sigMistagPDF', 'sigMistagPDF',
			tagOmegaSig, sigMistagOmega0, sigMistagOmegaAvg, sigMistagFracHalf)
        avgmistags = calculateAverageMistagPerCat(config, tagOmegaSig, sigMistagPDF, bins)
        del sigMistagPDF
        del sigMistagFracHalf
        del sigMistagOmegaAvg
	del sigMistagOmega0
    if config['PerEventMistag']:
	sigMistagOmega0 = WS(ws, RooConstVar(
	    'sigMistagOmega0', 'sigMistagOmega0', 0.07))
	sigMistagOmegaAvg = WS(ws, RooConstVar(
	    'sigMistagOmegaAvg', 'sigMistagOmegaAvg', config['TagOmegaSig']))
	sigMistagFracHalf = WS(ws, RooConstVar(
	    'sigMistagFracHalf', 'sigMistagFracHalf', 0.25))
	sigMistagPDF = WS(ws, MistagDistribution('sigMistagPDF', 'sigMistagPDF',
                                                 tagOmegaSig, sigMistagOmega0, sigMistagOmegaAvg, sigMistagFracHalf))
        observables.append(tagOmegaSig)
    else:
        sigMistagPDF = None

    # tagging
    # -------
    if False == config['PerEventMistag'] and None != avgmistags:
        perCatMistag = []
	for i in xrange(0, len(avgmistags['percat'])):
	    perCatMistag.append( WS(ws, RooRealVar('OmegaCat%d' %i, 'OmegaCat%d' %i,
					    avgmistags['percat'][i], 0., 1.)))
    else:
        perCatMistag = None

    # Signal EPDF
    ArgLf       = config['StrongPhase'] - config['WeakPhase']
    ArgLbarfbar = config['StrongPhase'] + config['WeakPhase']
    ACPobs = cpobservables.AsymmetryObservables(ArgLf, ArgLbarfbar, config['ModLf'])
    ACPobs.printtable()
    sigC    = WS(ws, RooRealVar(   'C',    'C coeff.', ACPobs.Cf(), -3., 3.))
    sigS    = WS(ws, RooRealVar(   'S',    'S coeff.', ACPobs.Sf(), -3., 3.))
    sigD    = WS(ws, RooRealVar(   'D',    'D coeff.', ACPobs.Df(), -3., 3.))
    sigSbar = WS(ws, RooRealVar('Sbar', 'Sbar coeff.', ACPobs.Sfbar(), -3., 3.))
    sigDbar = WS(ws, RooRealVar('Dbar', 'Dbar coeff.', ACPobs.Dfbar(), -3., 3.))

    nSigEvts = WS(ws, RooRealVar('nSigEvts', 'nSigEvts', 0. + config['NSigEvts'], 0., 1e7))

    sigTimePDF = buildBDecayTimePdf('Sig', ws,
            time, timeerr, qt, qf, tagOmegaSig, tagEffSig,
            gammas, deltaGammas, deltaMs, sigC, sigD, sigDbar, sigS, sigSbar,
            trm, tacc, terrpdf, sigMistagPDF,
            kfactorpdf, k, bins, perCatMistag, 128, config['NBinsAcceptance'])

    sigPDF = sigTimePDF
    sigEPDF = WS(ws, RooExtendPdf('SigEPDF', 'SigEPDF', sigPDF, nSigEvts))

    # Create the Bs -> Ds Pi physical background EPDF
    nBs2DsPiEvts = WS(ws, RooRealVar(
        'nBs2DsPiEvts', 'nBs2DsPiEvts', 0. + config['NBs2DsPiEvts'], 0., 1e7))
    Bs2DsPiTimePDF = buildBDecayTimePdf('Bs2DsPi', ws,
            time, timeerr, qt, qf, tagOmegaSig, tagEffSig,
            gammas, deltaGammas, deltaMs, one, zero, zero, zero, zero,
            trm, tacc, terrpdf, sigMistagPDF,
            kfactorpdf, k, bins, perCatMistag, 128, config['NBinsAcceptance'])

    Bs2DsPiPDF = Bs2DsPiTimePDF
    Bs2DsPiEPDF = RooExtendPdf( 'Bs2DsPiEPDF', 'Bs2DsPiEPDF', Bs2DsPiPDF, nBs2DsPiEvts )

    # Create the total EPDF
    # ---------------------
    # due to RooFit being quirky, we need the PDFs for generation;
    # fitting with EPDFs works fine
    allPDFs = []
    allEPDFs = []
    fractions = []
    if config['DoDsK']:
	allPDFs.append(sigPDF)
	allEPDFs.append(sigEPDF)
	fractions.append(nSigEvts)
    if config['DoDsPi']:
	allPDFs.append(Bs2DsPiPDF)
	allEPDFs.append(Bs2DsPiEPDF)
	fractions.append(nBs2DsPiEvts)

    totPDF = WS(ws, RooAddPdf('TotPDF_t', 'Model PDF in time',
		RooArgList(*allPDFs), RooArgList(*fractions)))
    totEPDF = WS(ws, RooAddPdf('TotEPDF_t', 'Model EPDF in time',
		RooArgList(*allEPDFs)))
    
    if not config['PerEventMistag'] and None != config['MistagCatBinBounds'] \
		and len(config['MistagCatBinBounds']) > 1:
        observables.append(ws.obj('tagcat'))

    # set variables constant if they are supposed to be constant
    setConstantIfSoConfigured(config, totPDF)
    setConstantIfSoConfigured(config, totEPDF)

    retVal = {
	    'ws': ws,
	    'pdf': totPDF,
	    'epdf': totEPDF,
	    'observables': RooArgSet(*observables),
            'condobservables': RooArgSet(*condobservables),
            'constraints': RooArgSet(*constraints)
	    }
    return retVal

def runBsGammaFitterToyMC(generatorConfig, fitConfig, toy_num, debug, wsname, initvars) :
    #REMOVED: from ROOT import FitMeTool
    from B2DXFitters import taggingutils, cpobservables

    GeneralModels = GaudiPython.gbl.GeneralModels
    PTResModels   = GaudiPython.gbl.PTResModels
    
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooMultiCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay
    from ROOT import RooGaussModel, RooTruthModel
    from ROOT import RooAbsReal, RooWorkspace, RooAbsArg
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf
    from ROOT import RooExponential, RooPolynomial, RooPolyVar, RooUniform
    from ROOT import RooFit, RooUniformBinning, TRandom3, RooRandom
    from ROOT import IfThreeWayCat, Dilution, IfThreeWayCatPdf
    from ROOT import TFile
    from ROOT import BdPTAcceptance, MistagDistribution
    from ROOT import RooBinnedPdf, RooEffHistProd, RooLinkedList


    # Instantiate and run the fitter in toy MC mode
    # (generate using the PDFs)
    pdf = getMasterPDF(generatorConfig, 'GEN', debug)

    # seed the pseudo random number generator
    rndm = TRandom3(toy_num + 1)
    RooRandom.randomGenerator().SetSeed(int(rndm.Uniform(4294967295)))
    del rndm

    print '########################################################################'
    print 'generator config:'
    print
    for k in generatorConfig:
        print '%32s: %s' % (k, str(generatorConfig[k]))
    print '########################################################################'

    
    if generatorConfig['IsToy']:
        # generate events
        dataset = pdf['pdf'].generate(pdf['observables'], RooFit.Verbose())
        ROOT.SetOwnership(dataset, True)
        sweights = None
        sample = None
        etapercat = None
    else:
        sweights = WS(pdf['ws'], RooRealVar('sweights', 'sweights', 1.))
        sample = WS(pdf['ws'], RooCategory('sample', 'sample'))
        sample.defineType('kkpi_up', 0)
        sample.defineType('kkpi_down', 1)
        sample.defineType('kpipi_up', 2)
        sample.defineType('kpipi_down', 3)
        sample.defineType('pipipi_up', 4)
        sample.defineType('pipipi_down', 5)
        tmp = readTree(
	    generatorConfig, 'dataset',
            {
            'sample_idx': sample,
            'lab0_LifetimeFit_ctau': pdf['ws'].obj('time'),
            'lab1_ID': pdf['ws'].obj('qf'),
            'lab0_BsTaggingTool_TAGDECISION_OS': pdf['ws'].obj('qt'),
            'lab0_BsTaggingTool_TAGOMEGA_OS':  pdf['ws'].obj('tagOmegaSig'),
            },
            #{
            #'B_TAU': pdf['ws'].obj('time'),
            #'Bach_CHARGE': pdf['ws'].obj('qf'),
            #'B_OST_DEC': pdf['ws'].obj('qt'),
            #'B_OST_OMEGA':  pdf['ws'].obj('tagOmegaSig'),
            #},
	    sweights, pdf['ws'].obj('qf'), pdf['ws'].obj('qt'),
	    pdf['ws'].obj('tagOmegaSig'))
        dataset = tmp['dataset']
        etapercat = tmp['etapercat']
        del tmp
    ws = pdf['ws']
    qt = ws.obj('qt')
    qf = ws.obj('qf')
    dataset.table(qt).Print('v')
    dataset.table(qf).Print('v')
    dataset.table(RooArgSet(qt, qf)).Print('v')

    if generatorConfig['MistagCatBinBounds'] != None:
        cat = ws.obj('tagcat')
        if None != cat:
	    dataset.addColumn(cat)
            dstmp = dataset.reduce(RooFit.Cut('qt!=0'))
            dstmp.table(cat).Print('v')

    from ROOT import gPad

    #mfr = pdf['ws'].obj('time').frame()
    #dataset.plotOn(mfr, RooFit.Cut("qt == +1 && qf == +1"))
    #pdf['pdf'].plotOn(mfr, RooFit.Slice(qt, 'B'), RooFit.Slice(qf, 'h+'), RooFit.Cut("qt == +1 && qf == +1"))
    #mfr.Draw()
    #gPad.Print('Propertime_MC_trueTagDec.eps')

    #if None != mistagpdf:
    #mfr = pdf['ws'].obj('tagOmegaSig').frame()
    #from ROOT import TColor
    #dataset.plotOn(mfr,  RooFit.Cut("qt == +1"),RooFit.LineColor(2),RooFit.MarkerColor(2))
    #dataset.plotOn(mfr,  RooFit.Cut("qt == -1"),RooFit.LineColor(4),RooFit.MarkerColor(4))
    #mistagpdf.plotOn(mfr)
    #mfr.Draw()
    #gPad.Print('mistagMC_mixed.eps')

    # delete the fitter, create a new one with the EPDFs for fitting
    # and use the dataset just generated
    del pdf

    print '########################################################################'
    print 'fit config:'
    print
    for k in fitConfig:
        print '%32s: %s' % (k, str(fitConfig[k]))
    print '########################################################################'

    pdf2 = getMasterPDF(fitConfig, 'FIT', debug)
    if None != etapercat:
        i = 0
        for v in etapercat:
            eta = pdf2['ws'].obj('OmegaCat%u' % i)
            isconst = eta.isConstant()
            eta.setVal(v)
            eta.setConstant(isconst)
            del isconst
            del eta
            i+=1
        del i
    if None != pdf2['ws'].obj('tagcat'):
        dataset.changeObservableName('tagcat', 'tagcat')
    dataset = dataset.reduce(RooFit.SelectVars(pdf2['observables']))
    ROOT.SetOwnership(dataset, True)
    dataset = WS(pdf2['ws'], dataset, [])
    dataset.Print()
    dstmp = dataset.reduce(RooFit.Cut('qt!=0'))
    if fitConfig['MistagCatBinBounds'] != None and len(fitConfig['MistagCatBinBounds']) > 1:
        cat = pdf2['ws'].obj('tagcat')
	dstmp.table(cat).Print('v')
    if not fitConfig['IsToy']:
        nEvts = pdf2['ws'].obj('nBs2DsPiEvts')
        # special treatment: steal number of entries from data set unless
        # nEvts is negative in which case we take |nEvts|
        if nEvts.getVal() < 0:
            nEvts.setVal(-nEvts.getVal())
        else:
            if dataset.isWeighted():
                nEvts.setVal(dataset.sumEntries())
            else:
                nEvts.setVal(dataset.numEntries())

    print 72 * '#'
    print 'observables:\t\t',
    pdf2['observables'].Print()
    print 'condobservables:\t',
    pdf2['condobservables'].Print()
    print 'constraints:\t\t',
    pdf2['constraints'].Print()
    print 'dataset:\t\t',
    dataset.Print()
    ws = pdf2['ws']
    qt = ws.obj('qt')
    qf = ws.obj('qf')
    dataset.table(qt).Print('v')
    dataset.table(qf).Print('v')
    dataset.table(RooArgSet(qt, qf)).Print('v')
    print 72 * '#'

    plot_init   = (wsname != None) and initvars
    plot_fitted = (wsname != None) and (not initvars)

    if plot_init :
        #pdf2['ws'].writeToFile(wsname)
	pass

    # more recent RooFit versions need Optimize(0) to work correctly
    # with our complicated (E)PDFs
    fitOpts = [
        RooFit.Optimize(fitConfig['Optimize']),
        RooFit.Strategy(fitConfig['Strategy']),
        RooFit.Timer(), RooFit.Save(),
        # shut up Minuit in blinding mode
        RooFit.Verbose(fitConfig['IsToy'] or not fitConfig['Blinding'])
        ]
    if not fitConfig['IsToy'] and fitConfig['Blinding']:
	# make RooFit quiet as well
	from ROOT import RooMsgService
	RooMsgService.instance().setGlobalKillBelow(RooFit.WARNING)
	fitOpts.append(RooFit.PrintLevel(-1))
    if 0 < pdf2['condobservables'].getSize():
        fitOpts.append(RooFit.ConditionalObservables(pdf['condobservables']))
    if 0 < pdf2['constraints'].getSize():
        fitOpts.append(RooFit.ExternalConstraints(pdf['constraints']))
    if not fitConfig['IsToy'] and dataset.isWeighted():
        fitOpts.append(RooFit.SumW2Error(True))
                
    fitopts = RooLinkedList()
    for o in fitOpts:
        fitopts.Add(o)
                    
    fitResult = pdf2['epdf'].fitTo(dataset, fitopts)

    # create output file to store fit results in

    if toy_num > 0 :
        print 'Creating output ROOT file for toy %s ...' %toy_num 
        outputFile = TFile( 'fitresult_%04u.root' %toy_num, 'RECREATE' )
    frc = fitResult.clone()
    outputFile.WriteTObject(frc)
    del frc
    del outputFile
 
    printResult(fitConfig, fitResult,
                fitConfig['Blinding'] and not fitConfig['IsToy'])
                    
    #if plot_fitted :
    #    pdf2['ws'].writeToFile(wsname)

    del pdf2
        
#------------------------------------------------------------------------------
_usage = '%prog [options] <toy_number>'

parser = OptionParser(_usage)

parser.add_option('-d', '--debug',
	dest    = 'debug',
	default = False,
	action  = 'store_true',
	help    = 'print debug information while processing'
	)
parser.add_option('-s', '--save',
	dest    = 'wsname',
	type = 'string',
	metavar = 'WSNAME',
	help    = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
	)
parser.add_option('-i', '--initial-vars',
	dest    = 'initvars',
	default = False,
	action  = 'store_true',
	help    = 'save the model PDF parameters before the fit (default: after the fit)'
	)
parser.add_option('-F', '--fit-config-string',
	dest = 'fitConfigString',
	type = 'string',
	action = 'store',
	help = 'string with fit configuration changes (dictionary, takes precedence)'
	)
parser.add_option('-f', '--fit-config-file',
	dest = 'fitConfigFile',
	type = 'string',
	action = 'store',
	help = 'name of file with fit configuration changes (dictionary)'
	)
parser.add_option('-G', '--gen-config-string',
	dest = 'genConfigString',
	type = 'string',
	action = 'store',
	help = 'string with generator configuration changes (dictionary, takes precedence)'
	)
parser.add_option('-g', '--gen-config-file',
	dest = 'genConfigFile',
	type = 'string',
	action = 'store',
	help = 'name of file with generator configuration changes (dictionary)'
	)

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    generatorConfig = dict(defaultConfig)
    fitConfig = dict(defaultConfig)
    #
    # example: change Gammas in fitting:
    # fitConfig.update({'Gammas': 0.700})

    (options, args) = parser.parse_args()

    if len(args) != 1 :
	parser.print_help()
	exit(-1)

    try:
	TOY_NUMBER = int(args[ 0 ])
    except ValueError:
	parser.error('The toy number is meant to be an integer ;-)!')
    # parse fit/generator configuration options
    if None != options.fitConfigFile:
	try:
	    lines = file(options.fitConfigFile, 'r').readlines();
	except:
	    parser.error('Unable to read fit configuration file %s' %
		    options.fitConfigFile)
	try:
	    d = eval(compile(''.join(lines), options.fitConfigFile, 'eval'))
	    fitConfig.update(d)
            del d
	except:
	    parser.error('Unable to parse fit configuration in file %s' %
		    options.fitConfigFile)
        del lines
    if None != options.fitConfigString:
	try:
	    d = eval(compile(options.fitConfigString, '[command line]', 'eval'))
	    fitConfig.update(d)
            del d
	except:
	    parser.error('Unable to parse fit configuration in \'%s\'' %
		    options.fitConfigString)
    if None != options.genConfigFile:
	try:
	    lines = file(options.genConfigFile, 'r').readlines();
	except:
	    parser.error('Unable to read generator configuration file %s' %
		    options.genConfigFile)
	try:
	    d = eval(compile(''.join(lines), options.genConfigFile, 'eval'))
	    generatorConfig.update(d)
            del d
	except:
	    parser.error('Unable to parse generator configuration in file %s' %
		    options.genConfigFile)
        del lines
    if None != options.genConfigString:
	try:
	    d = eval(compile(options.genConfigString, '[command line]', 'eval'))
	    generatorConfig.update(d)
            del d
	except:
	    parser.error('Unable to parse generator configuration in \'%s\'' %
		    options.genConfigString)
    
    runBsGammaFitterToyMC(
            generatorConfig,
            fitConfig,
            TOY_NUMBER,
	    options.debug,
	    options.wsname,
	    options.initvars)

    # -----------------------------------------------------------------------------
