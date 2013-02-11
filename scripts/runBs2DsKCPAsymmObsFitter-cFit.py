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
	        export LD_PRELOAD="$k"
	        break 3
	    else
	        export LD_PRELOAD="$LD_PRELOAD":"$k"
	        break 3
	    fi
	done
    done
done

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
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
	# modes to fit for
	'Modes': [
	    'Bs2DsK',
            'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst',
	    'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bs2DsstRho',
	    'Bd2DK', 'Bd2DsK',
	    'Lb2LcK', 'Lb2Dsp', 'Lb2Dsstp',
	    'CombBkg'
	    ],
	# combine CP observables for these modes into effective CP obs.
	'CombineModesForEffCPObs': [
	    # you may want to combine these during fitting
	    'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst'
	    ],
	# fit DsK CP observables in which mode:
	# 'CDS' 		- C, D, Dbar, S, Sbar
	# 'CDSConstrained'	- same as CDS, but constrain C^2+D^2+S^2 = 1
	#			  (same for bar)
	# 'LambdaPhases'	- |lambda|, strong and weak phase
	'Bs2DsKCPObs': 			'CDS',
	'SqSumCDSConstraintWidth':	0.01,

	# BLINDING
	'Blinding':			True,

	# PHYSICAL PARAMETERS
	'Gammad':			0.656, # in ps^{-1}
	'Gammas':			0.661, # in ps^{-1}
	'DeltaGammad':			0.,    # in ps^{-1}
	'DGsOverGs':			-0.105/0.661, # DeltaGammas / Gammas
	'DeltaMd':			0.507, # in ps^{-1}
	'DeltaMs':			17.719, # in ps^{-1}
	'GammaLb':			0.719, # in ps^{-1}
	'GammaCombBkg':			0.800, # in ps^{-1}
	# CP observables
	'StrongPhase': {
	    'Bs2DsK':		20. / 180. * pi,
	    'Bs2DsstK': 	-160. / 180. * pi,
	    'Bs2DsKst': 	-160. / 180. * pi,
	    'Bs2DsstKst': 	20. / 180. * pi
	    },
	'WeakPhase': {
	    'Bs2DsK':		50. / 180. * pi,
	    'Bs2DsstK':		50. / 180. * pi,
	    'Bs2DsKst':		50. / 180. * pi,
	    'Bs2DsstKst':	50. / 180. * pi
	    },
	'ModLf': {
	    'Bs2DsK': 		0.372,
	    'Bs2DsstK': 	0.470,
	    'Bs2DsKst': 	0.372,
	    'Bs2DsstKst': 	0.470
	    },
	# asymmetries
	'Asymmetries' : {
		'Prod': {
		    #'Bs': 0., 'Bd': 0.
		    },
		'Det': {
		    #'Bs2DsK': 0.,
		    #'Bs2DsstK': 0.,
		    #'Bs2DsPi': 0.,
		    #'Bd2DK': 0.,
		    #'Lb': 0.,
		    #'CombBkg': 0.
		    },
		'TagEff': {
		    #'Bs': 0., 'Bd': 0.
		    },
		'Mistag': {
		    },
		'TagEff_f': {
		    },
		'TagEff_t': {
		    'Lb': 0.0, 'CombBkg': -0.04
		    },
		},
	# Tagging
	'TagEffSig':			0.403,
	'TagOmegaSig':			0.396,
	'TagEffBkg':			0.403,
	'MistagCalibrationParams':	[ 0.392, 1.035, 0.391 ], 

	# truth/Gaussian/DoubleGaussian/GaussianWithPEDTE/GaussianWithLandauPEDTE/GaussianWithScaleAndPEDTE
	'DecayTimeResolutionModel':	'TripleGaussian',
	'DecayTimeResolutionBias':	0.,
	'DecayTimeResolutionScaleFactor': 1.15,
	'DecayTimeErrInterpolation':	False,
	# None/BdPTAcceptance/DTAcceptanceLHCbNote2007041,PowLawAcceptance
	'AcceptanceFunction':		'PowLawAcceptance',
	'AcceptanceCorrectionFile':	os.environ['B2DXFITTERSROOT']+'/data/acceptance-ratio-hists.root',
	'AcceptanceCorrectionHistName':	'haccratio_cpowerlaw',
	'AcceptanceCorrectionInterpolation': False,
	# acceptance can really be made a histogram
	'StaticAcceptance':		False,
	# acceptance parameters BdPTAcceptance
	'BdPTAcceptance_slope':		1.09,
	'BdPTAcceptance_offset':	0.187,
	'BdPTAcceptance_beta':		0.039,
	# acceptance parameters PowLawAcceptance
	'PowLawAcceptance_turnon':	1.215,
	'PowLawAcceptance_offset':	0.0373,
	'PowLawAcceptance_expo':	1.849,
	'PowLawAcceptance_beta':	0.0363,

	'PerEventMistag': 		True,
	'TrivialMistag':		False,
	'UseKFactor':			False,

	# fitter settings
	'Optimize':			2,
	'Strategy':			2,
	'Debug':			False,

	# list of constant parameters
	'constParams': [
	    'Gammas', 'deltaGammas',
	    'Gammad', 'deltaGammad', 'deltaMd',
	    'tagOmegaSig',
            'deltaMs',
	    'MistagCalib_p0', 'MistagCalib_p1', 'MistagCalib_avgmistag',
	    ],

	# mass templates
	'MassTemplateFile':		os.environ['B2DXFITTERSROOT']+'/data/workspace/WS_Mass_DsK.root',
	'MassTemplateWorkspace':	'FitMeToolWS',
	'MassInterpolation':		False,
	# either one element or 6 (kkpi,kpipi,pipipi)x(up,down) in "sample" order
	'NEvents':			[ 1731. ],
	# mistag template
	'MistagTemplateFile':		os.environ['B2DXFITTERSROOT']+'/data/workspace/work_toys_dsk.root',
	'MistagTemplateWorkspace':	'workspace',
	'MistagTemplateName':		'PhysBkgBsDsPiPdf_m_down_kkpi_mistag',
	'MistagVarName':		'lab0_BsTaggingTool_TAGOMEGA_OS',
	'MistagInterpolation':		False,

	# k-factor templates
	# ROOT file to read
	'KFactorFile':			os.environ['B2DXFITTERSROOT']+'/data/workspace/kfactor_wspace.root',
	# workspace name
	'KFactorWorkspace':		'workspace',
	# name of variable in file
	'KFactorVarName':		'kfactorVar',
	# default is KeysPDF, list Histo modes here
	'KFactorHistogramModes':	[],

	# verify settings and sanitise where (usually) sensible
	'Sanitise':			True,

	# fitter on speed: binned PDFs
	'NBinsAcceptance':		150,  # if >0, bin acceptance
	'NBinsTimeKFactor':		200,  # if >0, use binned cache for k-factor integ.
	'NBinsMistag':			50,   # if >0, parametrize Mistag integral
	'NBinsProperTime':		50,   # if >0, parametrize proper time int.
	'NBinsMass':			0,    # if >0, bin mass templates

	# Data file settings
	'IsToy':			True,
	'DataFileName':			None,
	'DataWorkSpaceName':		'workspace',
	'DataSetNames':			{
		'up': 	{
		    'kkpi':	'dataSetBsDsK_up_kkpi',
		    'kpipi':	'dataSetBsDsK_up_kpipi',
		    'pipipi': 	'dataSetBsDsK_up_pipipi'
		    },
		'down':	{
		    'kkpi':	'dataSetBsDsK_down_kkpi',
		    'kpipi':	'dataSetBsDsK_down_kpipi',
		    'pipipi':	'dataSetBsDsK_down_pipipi'
		    }
		},
	# bug-for-bug compatibility flags
	'BugFlags': [
		# 'PdfSSbarSwapMinusOne',
		# 	swap and multiply S and Sbar in the pdf, state of
		# 	affairs before discovery of bug on 2012-09-13 
		# 'OutputCompatSSbarSwapMinusOne',
		#	with the bug from PdfSSbarSwapMinusOne fixed, the
		#	output of the fit parameters is no longer comparable to
		#	old fits - fix in the final output routine by applying
		#	that transformation during the output stage (MINUIT log
		#	output and fit results will be "wrong", though)
		],
	}

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
        val = '% 12.3g' % fv[var]
        if blind:
            val = 'XXXX.XXX'
        print '% 3u %-16s % 12.3g %12s %12.3g %s' % (
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
	v = obj.getVariables()
	ROOT.SetOwnership(v, True)
	i = v.createIterator()
	ROOT.SetOwnership(i, True)
	o = i
	while None != o:
	    o = i.Next()
	    if None != o:
		setConstantIfSoConfigured(config, o)
    else:
	if obj.GetName() in config['constParams']:
	    obj.setConstant(True)

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

# read dataset from workspace
def readDataSet(
	config,		# configuration dictionary
	ws,		# workspace to which to add data set
	time,		# variable to use for time
	mass,		# variable to use for mass
	mistag,		# variable to use for mistag
	qf,		# variable to use for final state tag
	qt,		# variable to use for tagging decision
	sample,		# variable to use as sample identifier (mag. pol., Ds decay ch.)
	rangeName = 0	# name of range to clip dataset to
	):
    from ROOT import ( TFile, RooWorkspace, RooRealVar, RooCategory,
	    RooBinningCategory, RooUniformBinning, RooMappedCategory,
	    RooDataSet, RooArgSet, RooArgList )
    import sys
    names = [
	    'lab0_LifetimeFit_ctau',
	    'lab0_MassFitConsD_M',
	    'lab0_BsTaggingTool_TAGOMEGA_OS',
	    'lab1_ID',
	    'lab0_BsTaggingTool_TAGDECISION_OS'
	    ]
    # tweak variable names for use in toys - means that we cannot accidentally
    # read data in toy configuration and vice-versa
    #
    # additional complication: toys save decay time in ps, data is in nm
    timeConvFactor = 1e9 / 2.99792458e8
    if config['IsToy']:
	names[3] = '%s_idx' % names[3]
	names[4] = '%s_idx' % names[4]
	timeConvFactor = 1.
    # open file with data sets
    f = TFile(config['DataFileName'], 'READ')
    # get workspace
    fws = f.Get(config['DataWorkSpaceName'])
    ROOT.SetOwnership(fws, True)
    # get source variables from workspace in file
    srcvars = [ fws.obj(vname) for vname in names ]
    if None in srcvars:
	print 'Unable to read all required variables from workspace'
	for v in srcvars:
	    v.Print()
	sys.exit(1)
    # set up what we need for the copying later
    srcset = RooArgSet(*srcvars)
    dstvars = [ time, mass, mistag, qf, qt ]
    dstset = RooArgSet(sample, *dstvars)
    dstvarranges = []
    for v in dstvars:
	if v.InheritsFrom('RooAbsCategory'):
	    dstvarranges.append(None)
	    continue
	if None == rangeName or 0 == rangeName:
	    dstvarranges.append(v.getBinning())
	else:
	    dstvarranges.append(v.getBinning(rangeName))
    data = RooDataSet('agglomeration', 'of positronic circuits', dstset)
    # loop over list of data set names, assigning them consecutive values of
    # sample
    ninwindow = 0
    ntotal = 0
    for pol in config['DataSetNames'].keys():
	for dsmode in config['DataSetNames'][pol].keys():
	    dsname = config['DataSetNames'][pol][dsmode]
	    # set sample index
	    sample.setLabel('%s_%s' % (pol, dsmode))
	    # handle absent names (samples) in input
	    if None == dsname: continue
	    if 0 == len(dsname): continue
	    # get dataset from workspace
            ds = fws.obj(dsname)
	    if None == ds: continue
	    sys.stdout.write('Dataset conversion and fixup: %s: progress: ' % dsname)
	    # wire the dataset into the source variables
	    ds.attachBuffers(srcset)
	    for i in xrange(0, ds.numEntries()):
		ntotal = ntotal + 1
	        ov = ds.get(i)
	        if 0 == i % 128:
	    	    sys.stdout.write('*')
		if mass.getMin() > srcvars[1].getVal() or \
			srcvars[1].getVal() > mass.getMax():
		    continue
		if time.getMin() > srcvars[0].getVal() * timeConvFactor or \
			srcvars[0].getVal() * timeConvFactor > time.getMax():
		    continue
	        # copy source to destination variables, adjusting continuous
	        # variables to categories on the fly
	        for j in xrange(0, len(srcvars)):
	    	    if dstvars[j].InheritsFrom('RooAbsCategory'):
	    	        if srcvars[j].InheritsFrom('RooAbsCategory'):
	    		    print 'cat dump %d' % srcvars[j].getIndex()
	    		    dstvars[j].setIndex(srcvars[j].getIndex())
	    	        else:
	    		    v = srcvars[j].getVal()
	    	            if v >= 1e-15:
	    		        dstvars[j].setIndex(+1)
	    	            elif v <= -1e-15:
	    		        dstvars[j].setIndex(-1)
	    	            else:
	    		        dstvars[j].setIndex(0)
	    	    else:
	    	        v = srcvars[j].getVal()
			if 0 == j:
			    v = v * timeConvFactor
			elif 2 == j:
			    if abs(srcvars[4].getVal()) < 1e-15:
			        # fix the untagged oddities in the tuples
	    	    	        v = 0.5
	    	        dstvars[j].setVal(v)
	        # fill destination dataset
	    	data.add(dstset)
		ninwindow = ninwindow + 1
	    del ds
	    sys.stdout.write(', done\n')
    # free workspace and close file
    del fws
    f.Close()
    del f
    # put the new dataset into our proper workspace
    data = WS(ws, data, [])
    # for debugging
    if config['Debug']:
	data.Print('v')
	data.table(qt).Print('v')
	data.table(qf).Print('v')
	data.table(RooArgSet(qt, qf)).Print('v')
	data.table(sample).Print('v')
    # all done, return Data to the bridge
    return data

def readAcceptanceCorrection(
	config,	# config dictionary
	ws,	# workspace into which to import correction
	time	# time
	):
    from ROOT import ( TFile, TH1, RooDataHist, RooHistPdf, RooArgList,
	    RooArgSet )
    if None == config['AcceptanceCorrectionFile'] or \
	    None == config['AcceptanceCorrectionHistName'] or \
	    '' == config['AcceptanceCorrectionFile'] or \
	    '' == config['AcceptanceCorrectionHistName']:
	return None
    f = TFile(config['AcceptanceCorrectionFile'], 'READ')
    h = f.Get(config['AcceptanceCorrectionHistName'])
    ROOT.SetOwnership(h, True)
    h.Scale(1. / h.Integral())
    if not config['AcceptanceCorrectionInterpolation']:
	dhist = RooDataHist('acc_corr_dhist', 'acc_corr_dhist',
		RooArgList(time), h)
        retVal = WS(ws, RooHistPdf('acc_corr', 'acc_corr',
	    RooArgSet(time), dhist))
        del dhist
    else:
        from ROOT import RooBinned1DQuinticBase, RooAbsPdf
        RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
	retVal = WS(ws, RooBinned1DQuinticPdf(
	    'acc_corr', 'acc_corr', h, time))
    del h
    del f
    return retVal

# read mistag distribution from file
def getMistagTemplate(
	config,	# configuration dictionary
	ws, 	# workspace to import into
	mistag	# mistag variable
	):
    from ROOT import ( TFile, RooWorkspace, RooKeysPdf, RooHistPdf,
	    RooArgList, RooDataHist, RooArgSet )
    fromfile = config['MistagTemplateFile']
    fromws = config['MistagTemplateWorkspace']
    fromvarname = config['MistagVarName']
    fromfile = TFile(fromfile, 'READ')
    workspace = fromfile.Get(fromws)
    ROOT.SetOwnership(workspace, True)
    var = workspace.var(fromvarname)
    pdf = workspace.pdf(config['MistagTemplateName'])
    # we need to jump through a few hoops to rename the dataset and variables
    # get underlying histogram
    hist = pdf.dataHist().createHistogram(var.GetName())
    ROOT.SetOwnership(hist, True)
    hist.SetNameTitle('sigMistagPdf_hist', 'sigMistagPdf_hist')
    hist.SetDirectory(None)
    # recreate datahist
    dh = RooDataHist('sigMistagPdf_dhist', 'sigMistagPdf_dhist',
	RooArgList(mistag), hist)
    del hist
    del pdf
    del var
    del workspace
    fromfile.Close()
    del fromfile
    # and finally use dh to create our pdf
    pdf = WS(ws, RooHistPdf('sigMistagPdf', 'sigMistagPdf',
	RooArgSet(mistag), dh))
    del dh
    return pdf

# Clean up work space into nicely named RooKeysPdfs for each mode
def getKFactorTemplates(
	config,	# configuration dictionary
	ws, 	# workspace to import into
	k	# k factor variable
	):
    """Clean up work space into nicely named RooKeysPdfs for each mode"""
    fromfile = config['KFactorFile']
    fromws = config['KFactorWorkspace']
    fromvarname = config['KFactorVarName']
    modes = config['Modes']
    histpdflist = config['KFactorHistogramModes']
    from ROOT import (TFile, RooWorkspace, RooHistPdf, RooKeysPdf, RooDataSet,
	    RooDataHist, RooArgSet)
    fromfile = TFile(fromfile, 'READ')
    workspace = fromfile.Get(fromws)
    ROOT.SetOwnership(workspace, True)
    var = workspace.var(fromvarname)
    dslist = {}
    for n in modes:
	thismode = {}
	for p in ('up', 'down'):
            thismode[p] = workspace.data('kfactor_dataset_%s_%s' % (n, p))
	if None == thismode['up']:
	    if None == thismode['down']:
		dslist[n] = thismode['down']
	    else:
		print '@@@@ - WARNING: No k factor template for mode %s' %n
	else:
	    # merge is we have both up and down
	    if None != thismode['down']:
		thismode['up'].append(thismode['down'])
	    dslist[n] = thismode['up']
	    dslist[n].SetName('kfactordata_merged_%s' % n)
	if n in dslist and None == dslist[n]:
	    del dslist[n]
	if n in dslist:
	    if dslist[n].numEntries() <= 0.:
		del dslist[n]
	del thismode
    allpdfs = { }
    for mode in dslist:
	kmin = ROOT.Double(0.)
	kmax = ROOT.Double(0.)
        ds = dslist[mode]
	if 0 >= ds.numEntries():
	    print '@@@ - WARNING: Empty k factor template for mode %s' % mode
	    continue
	name = ds.GetName()
	ds.getRange(var, kmin, kmax, 0.05)
	print 'k-factor %s has %u entries, range %g to %g' % (
		mode, ds.numEntries(), kmin, kmax)
	allpdfs[mode] = {}
        if mode in histpdflist or 1 == ds.numEntries():
            dhist = ds.binnedClone('%s_dhist' % name)
	    ROOT.SetOwnership(dhist, True)
	    if 1 == ds.numEntries() and kmin == kmax:
		kmin -= 1e-3
		kmax += 1e-3
	    pdf = RooHistPdf(name, name, RooArgSet(var), dhist)
            allpdfs[mode]['pdf'] = WS(ws, pdf,
		    [RooFit.RenameVariable(fromvarname, k.GetName())])
	    del dhist
        else:
	    pdf = RooKeysPdf(name, name, var, ds)
            allpdfs[mode]['pdf'] = WS(ws, pdf,
		    [RooFit.RenameVariable(fromvarname, k.GetName())])
	allpdfs[mode]['range'] = [kmin, kmax]
	del pdf
	del ds
        # should be one pdf per mode
    del dslist
    return allpdfs

# obtain mass template from mass fitter
#
# we use the very useful workspace dump produced by the mass fitter to obtain
# the pdf and yields
#
# returns a dictionary with a pair { 'pdf': pdf, 'yield': yield }
def getMassTemplateOneMode(
	config,		# configuration dictionary
	ws,		# workspace into which to import templates
	mass,		# mass variable
	mode,		# decay mode to load
	polarity,	# magnet polarity
	DsMode		# mode of Ds decay
	):
    fromfile = config['MassTemplateFile']
    fromwsname = config['MassTemplateWorkspace']
    from ROOT import ( TFile, RooWorkspace, RooAbsPdf, RooAbsCategory,
	    RooRealVar, RooArgSet, RooDataHist, RooHistPdf, RooArgList )
    import re

    # validate input (and break caller if invalid)
    if polarity not in ('up', 'down'):
	return None
    if DsMode not in ('kkpi', 'kpipi', 'pipipi'):
	return None

    # open file and read in workspace
    fromfile = TFile(fromfile, 'READ')
    if fromfile.IsZombie():
	return None
    fromws = fromfile.Get(fromwsname)
    if None == fromws:
	return None
    ROOT.SetOwnership(fromws, True)

    # ok, depending on mode, we try to load a suitable pdf
    pdf = None
    if mode == 'Bs2DsK':
	pdf = fromws.pdf('DblCBPDF%s_%s' % (polarity, DsMode))
    elif mode == 'CombBkg':
	pdf = fromws.pdf('CombBkgPDF_m_%s_%s' % (polarity, DsMode))
    else:
	# any other mode may or may not have separate samples for
	# magnet polarity, Ds decay mode, ...
	#
	# we therefore constuct a list of successively less specialised name
	# suffices so we can get the most specific pdf from the workspace
	trysfx = [
		'%sPdf_m_%s_%s' % (mode, polarity, DsMode),
		'%sPdf_m_%s_%s' % (mode.replace('2', ''), polarity, DsMode),
		'%s_m_%s_%s' % (mode, polarity, DsMode),
		'%s_m_%s_%s' % (mode.replace('2', ''), polarity, DsMode),
		'%sPdf_m_both' % mode,
		'%sPdf_m_both' % mode.replace('2', ''),
		'%s_m_both' % mode,
		'%s_m_both' % mode.replace('2', ''),
		'%sPdf_m' % mode,
		'%sPdf_m' % mode.replace('2', ''),
		'%s_m' % mode,
		'%s_m' % mode.replace('2', '')
		]
	for sfx in trysfx:
	    pdf = fromws.pdf('PhysBkg%s' % sfx)
	    if None != pdf:
		break
    # figure out name of mass variable - should start with 'lab0' and end in
    # '_M'; while we're at it, figure out how we need to scale yields due to
    # potentially different mass ranges
    massname = None
    yieldrangescaling = 1.
    if None != pdf:
        pdfvars = []
	varset = pdf.getVariables()
	ROOT.SetOwnership(varset, True)
        it = varset.createIterator()
	ROOT.SetOwnership(it, True)
        while True:
	    obj = it.Next()
	    if None == obj:
		break
	    pdfvars.append(obj)
        pdfvarnames = [ v.GetName() for v in pdfvars ]
        regex = re.compile('^lab0.*_M$')
        for n in pdfvarnames:
	    if regex.match(n):
		oldmass = varset.find(n)
    	        massname = n
	    else:
		# set anything else constant
		varset.find(n).setConstant(True)
	# mass integration factorises, so we can afford to be a little sloppier
	# when doing numerical integrations
        pdf.specialIntegratorConfig(True).setEpsAbs(1e-9)
        pdf.specialIntegratorConfig().setEpsRel(1e-9)
	pdf.specialIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('sumRule', 'Trapezoid')
	pdf.specialIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation', 'Wynn-Epsilon')
	pdf.specialIntegratorConfig().getConfigSection('RooIntegrator1D').setRealValue('minSteps', 3)
	pdf.specialIntegratorConfig().getConfigSection('RooIntegrator1D').setRealValue('maxSteps', 16)
        pdf.specialIntegratorConfig().method1D().setLabel('RooIntegrator1D')
	# figure out yield scaling due to mass ranges
	integral = pdf.createIntegral(RooArgSet(oldmass))
	ROOT.SetOwnership(integral, True)
	oldint = integral.getVal()
	oldmass.setRange(mass.getMin(), mass.getMax())
	newint = integral.getVal()
	yieldrangescaling = newint / oldint
    # ok, figure out yield
    nYield = None
    if mode == 'Bs2DsK':
	nYield = RooRealVar('nSig_%s_%s_Evts' % (polarity, DsMode),
		'nSig_%s_%s_Evts' % (polarity, DsMode),
		fromws.var('nSig_%s_%s_Evts' % (polarity, DsMode)).getVal() *
		yieldrangescaling)
    elif mode == 'CombBkg':
	nYield = RooRealVar('nCombBkg_%s_%s_Evts' % (polarity, DsMode),
		'nCombBkg_%s_%s_Evts' % (polarity, DsMode),
		fromws.var('nCombBkg_%s_%s_Evts' % (polarity, DsMode)).getVal() *
		yieldrangescaling)
    else:
	# yield for other modes are either simple and we deal with them here,
	# or we deal with them below
	nYield = fromws.var('n%s_%s_%s_Evts' % (mode, polarity, DsMode))
	if None != nYield:
	    nYield = RooRealVar(nYield.GetName(), nYield.GetTitle(),
		    nYield.getVal() * yieldrangescaling)
    if None != pdf and None == nYield:
	# fix for modes without fitted yields: insert with zero yield unless we
	# know better
	y = None
	# fixed yield modes we know about
	fixedmodes = {
		'Bd2DK': { 
		    'up':   { 'kkpi': 14., 'kpipi': 2. }, 
		    'down': { 'kkpi': 23., 'kpipi': 3. }
		    },
		'Lb2LcK': {
		    'up':   { 'kkpi': 4.1088*100./15. },
		    'down': { 'kkpi': 6.7224*100./15. },
		    },
		'Lb2Dsp': {
		    'up':   { 'kkpi': 0.5 * 46., 'kpipi': 0.5 * 5., 'pipipi': 0.5 * 10. }, 
		    'down': { 'kkpi': 0.5 * 78., 'kpipi': 0.5 * 8., 'pipipi': 0.5 * 16. }
		    },
		'Lb2Dsstp': {
		    'up':   { 'kkpi': 0.5 * 46., 'kpipi': 0.5 * 5., 'pipipi': 0.5 * 10. }, 
		    'down': { 'kkpi': 0.5 * 78., 'kpipi': 0.5 * 8., 'pipipi': 0.5 * 16. }
		    }
		}
	if (mode in fixedmodes and polarity in fixedmodes[mode] and
		DsMode in fixedmodes[mode][polarity]):
	    # it's a fixed yield mode, so set yield
	    y = fixedmodes[mode][polarity][DsMode]
        else:
	    # might be a "grouped mode"
	    group1 = ['Bd2DsK', 'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst']
	    group2 = ['Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bs2DsstRho']
	    fracGroup1 = [
		    fromws.var('g1_f%d_frac' % i).getVal() for i in xrange(1, 4) ]
	    fracGroup2 = [
		    fromws.var('g2_f%d_frac' % i).getVal() for i in xrange(1, 4) ]
	    if mode in group1:
		# get the group yield
		y = fromws.var(
			'nBs2DsDssKKst_%s_%s_Evts' % (polarity, DsMode)).getVal()
		# multiply with correct (recursive) fraction
		for i in xrange(0, 3):
		    if group1[i] == mode:
			y *= fracGroup1[i]
			break
		    else:
			y *= 1. - fracGroup1[i]
	    elif mode in group2:
		# get the group yield
		y = fromws.var(
			'nBs2DsDsstPiRho_%s_%s_Evts' % (polarity, DsMode)).getVal()
		# multiply with correct (recursive) fraction
		for i in xrange(0, 3):
		    if group2[i] == mode:
			y *= fracGroup2[i]
			break
		    else:
			y *= 1. - fracGroup2[i]
	    else: # mode not recognized
		pass
	if None == y:
	    print '@@@@ - ERROR: NO YIELD FOR MODE %s POLARITY %s DSMODE %s' % (
		    mode, polarity, DsMode)
	    nYield = None
	else:
	    nYield = RooRealVar('n%s_%s_%s_Evts' % (mode, polarity, DsMode),
		    'n%s_%s_%s_Evts' % (mode, polarity, DsMode),
		    y * yieldrangescaling)
    # ok, we should have all we need for now
    if None == pdf or None == nYield:
	print '@@@@ - ERROR: NO PDF FOR MODE %s POLARITY %s DSMODE %s' % (
		mode, polarity, DsMode)
	return None
    # import mass pdf and corresponding yield into our workspace
    # in the way, we rename whatever mass variable was used to the one supplied
    # by our caller
    nYield = WS(ws, nYield, [
	RooFit.RenameConflictNodes('_%s_%s_%s' % (mode, polarity, DsMode))])

    if None != ws.pdf(pdf.GetName()):
	# reuse pdf if it is already in the workspace - that's fine as long
	# as all parameters are fixed and the yields are not reused
	pdf = ws.pdf(pdf.GetName())
	# see if there is a binned version, if so prefer it
	if None != ws.pdf('%s_dhist_pdf' % pdf.GetName()):
	    pdf = ws.pdf('%s_dhist_pdf' % pdf.GetName())
    else:
	# ok, pdf not in workspace, so swallow it
	if None != massname:
	    pdf = WS(ws, pdf, [
		RooFit.RenameVariable(massname, mass.GetName()),
		RooFit.RenameConflictNodes('_%s_%s_%s' % (mode, polarity, DsMode))])
        else:
	    pdf = WS(ws, pdf, [
		RooFit.RenameConflictNodes('_%s_%s_%s' % (mode, polarity, DsMode))])
    if config['NBinsMass'] > 0 and not config['MassInterpolation']:
	obins = mass.getBins()
	mass.setBins(config['NBinsMass'])
        hist = pdf.createHistogram('%s_hist' % pdf.GetName(), mass)
        ROOT.SetOwnership(hist, True)
	dhist = WS(ws, RooDataHist(
		'%s_dhist' % pdf.GetName(), '%s_dhist' % pdf.GetName(),
		RooArgList(mass), hist))
	pdf = WS(ws, RooHistPdf('%s_pdf' % dhist.GetName(),
	    '%s_pdf' % dhist.GetName(), RooArgSet(mass), dhist))
	del hist
	del dhist
        mass.setBins(obins)
	del obins
    # ok, all done, return
    if config['MassInterpolation']:
        from ROOT import RooBinned1DQuinticBase
        RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
        obins = mass.getBins()
	nbins = config['NBinsMass']
	if 0 == nbins:
	    print 'ERROR: requested binned interpolation of mass %s %d %s' % (
		    'histograms with ', nbins, ' bins - increasing to 100 bins')
	    nbins = 100
        mass.setBins(nbins)
        hist = pdf.createHistogram('%s_hist' % pdf.GetName(), mass)
        ROOT.SetOwnership(hist, True)
        pdf = WS(ws, RooBinned1DQuinticPdf(
	    '%s_interpol' % pdf.GetName(),
	    '%s_interpol' % pdf.GetName(), hist, mass, True))
        del hist
        mass.setBins(obins)
	del obins
	del nbins
    if None != nYield:
	nYield.setConstant(True)
    return { 'pdf': WS(ws, pdf), 'yield': WS(ws, nYield) }

# read mass templates for specified modes
#
# returns dictionary d['mode']['polarity']['kkpi/kpipi/pipipi'] which contains
# a dictionary of pairs { 'pdf': pdf, 'yield': yield }
def getMassTemplates(
	config,					# configuration dictionary
	ws,					# wksp into which to import templates
	mass,					# mass variable
	polarities = ('up', 'down'),		# magnet polarities to read
	DsModes = ('kkpi', 'kpipi', 'pipipi')	# Ds decay modes to read
	):
    import sys
    retVal = {}
    for mode in config['Modes']:
	if mode not in retVal:
	    retVal[mode] = { 'up': {}, 'down': {} }
	for pol in polarities:
	    for DsMode in DsModes:
		tmp = getMassTemplateOneMode(
			config, ws, mass,
			mode, pol, DsMode)
		if None == tmp:
		    # break caller in case of error
		    return None
		retVal[mode][pol][DsMode] = tmp
    sample = ws.obj('sample')
    totyield = 0.
    totyields = [ 0., 0., 0., 0., 0., 0. ]
    for pol in polarities:
	for DsMode in DsModes:
	    for mode in config['Modes']:
		i = sample.lookupType('%s_%s' % (pol, DsMode)).getVal()
		totyield += retVal[mode][pol][DsMode]['yield'].getVal()
		totyields[i] += retVal[mode][pol][DsMode]['yield'].getVal()
    # scale the yields to the desired number of events
    for pol in polarities:
	for DsMode in DsModes:
            for mode in config['Modes']:
		i = sample.lookupType('%s_%s' % (pol, DsMode)).getVal()
		y = retVal[mode][pol][DsMode]['yield']
		if 6 == len(config['NEvents']):
		    y.setVal(y.getVal() * (config['NEvents'][i] / totyields[i]))
		elif 1 == len(config['NEvents']):
		    y.setVal(y.getVal() * (config['NEvents'][0] / totyield))
		else:
		    print 'ERROR: invalid length of config[\'NEvents\']!'
		    sys.exit(1)
		# make sure things stay constant
		y.setConstant(True)
    return retVal

# build non-oscillating decay time pdf
def buildNonOscDecayTimePdf(
	config,					# configuration dictionary
	name,					# 'Signal', 'DsPi', ...
	ws,					# RooWorkspace into which to put the PDF
	time, timeerr, qt, qf, mistag, tageff,	# potential observables
	Gamma,
	timeresmodel = None,			# decay time resolution model
	acceptance = None,			# acceptance function
	timeerrpdf = None,			# pdf for per event time error
	mistagpdf = None,			# pdf for per event mistag
	kfactorpdf = None,			# distribution k factor smearing
	kvar = None,				# variable k which to integrate out
	adet = None,				# detection asymmetry
	atageff_f = None,			# qf dependent tagging eff. asymm.
	atageff_t = None			# qt dependent tagging eff. asymm.
	):
    # Look in LHCb-INT-2011-051 for the conventions used
    from ROOT import ( RooConstVar, TagEfficiencyWeight, IfThreeWayCat,
	    Dilution, RooProduct, RooTruthModel, RooGaussModel, Inverse,
	    RooDecay, RooProdPdf, RooBinnedPdf, RooEffResModel, RooEffProd,
	    RooUniformBinning, RooArgSet, RooFit, RooWorkspace,
	    RooGeneralisedSmearingBase, RooAbsPdf, RooArgList,
	    NonOscTaggingPdf, FinalStateChargePdf )
    RooNumGenSmearPdf = RooGeneralisedSmearingBase(RooAbsPdf)

    # constants used
    zero = WS(ws, RooConstVar('zero', 'zero', 0.))
    one = WS(ws, RooConstVar('one', 'one', 1.))

    if None == adet: adet = zero
    if None == atageff_f: atageff_f = zero
    if None == atageff_t: atageff_t = zero

    # if no time resolution model is set, fake one
    if timeresmodel == None:
	timeresmodel = WS(ws, RooTruthModel('%s_TimeResModel' % name,
	    '%s time resolution model' % name, time))
    elif timeresmodel == 'Gaussian':
	timeresmodel = WS(ws, RooGaussModel('%s_TimeResModel' % name,
	    '%s time resolution model' % name, time, zero, timeerr))

    # apply acceptance (if needed)
    if None != acceptance and 0 < config['NBinsAcceptance']:
	if not acceptance.isBinnedDistribution(RooArgSet(time)):
	    acceptance = WS(ws, RooBinnedPdf(
		"%sBinnedAcceptance" % acceptance.GetName(),
		"%sBinnedAcceptance" % acceptance.GetName(),
		time, 'acceptanceBinning', acceptance))
	    acceptance.setForceUnitIntegral(True)
	timeresmodel = WS(ws, RooEffResModel(
	    '%s_timeacc_%s' % (timeresmodel.GetName(), acceptance.GetName()),
	    '%s plus time acceptance %s' % (timeresmodel.GetTitle(), acceptance.GetTitle()),
	    timeresmodel, acceptance))

    # perform the actual k-factor smearing integral (if needed)
    # if we have to perform k-factor smearing, we need "smeared" variants of
    # Gamma, DeltaGamma, DeltaM
    if None != kfactorpdf and None != kvar:
	kGamma = WS(ws, RooProduct('%sKGamma' % Gamma.GetName(),
	    '%s k * #Gamma' % Gamma.GetName(),
	    RooArgSet(kvar, Gamma)))
    else:
	# otherwise, we can get away with giving old variables new names
	kGamma = Gamma

    # perform the actual k-factor smearing integral (if needed)
    # build (raw) time pdf
    tau = WS(ws, Inverse('%sTau' % kGamma.GetName(),
	'%s #tau' % kGamma.GetName(), kGamma))
    rawtimepdf = WS(ws, RooDecay('%s_RawTimePdf' % name,
	'%s raw time pdf' % name, time, tau,
	timeresmodel, RooDecay.SingleSided))

    # perform the actual k-factor smearing integral (if needed)
    if None != kfactorpdf and None != kvar:
	krawtimepdf = WS(ws, RooNumGenSmearPdf('%s_kSmearedRawTimePdf' % name,
	    '%s raw time pdf smeared with k factor' % name,
	    kvar, rawtimepdf, kfactorpdf['pdf']))
	# since we fine-tune the range of the k-factor distributions, and we
	# know that the distributions are well-behaved, we can afford to be a
	# little sloppy
        krawtimepdf.convIntConfig().setEpsAbs(1e-4)
        krawtimepdf.convIntConfig().setEpsRel(1e-4)
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('extrapolation','Wynn-Epsilon')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('sumRule','Trapezoid')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('minSteps', 3)
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSteps', 16)
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
        #krawtimepdf.convIntConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
        krawtimepdf.convIntConfig().method1D().setLabel('RooIntegrator1D')
        krawtimepdf.convIntConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')	
	# set integration range
	center = WS(ws, RooConstVar(
	    '%s_kFactorCenter' % name, '%s_kFactorCenter' % name,
	    0.5 * (kfactorpdf['range'][0] + kfactorpdf['range'][1])))
	width = WS(ws, RooConstVar(
	    '%s_kFactorWidth' % name, '%s_kFactorWidth' % name,
	    0.5 * (kfactorpdf['range'][1] - kfactorpdf['range'][0])))
	krawtimepdf.setConvolutionWindow(center, width, 1.0)
	if 0 < config['NBinsTimeKFactor']:
	    kfactortimebinning = WS(ws, RooUniformBinning(     
		time.getMin(), time.getMax(), config['NBinsTimeKFactor'],
		'%s_timeBinnedCache' % name))
	    time.setBinning(kfactortimebinning, kfactortimebinning.GetName())
	    krawtimepdf.setBinnedCache(time, kfactortimebinning.GetName(),
		    RooArgSet(qt, qf))
    else:
	krawtimepdf = rawtimepdf
    
    if None != mistagpdf:
	otherargs = [ mistag, mistagpdf, tageff, adet, atageff_f, atageff_t ]
    else:
	otherargs = [ tageff, adet, atageff_f, atageff_t ]
    ourmistagpdf = WS(ws, NonOscTaggingPdf('%s_mistagPdf' % name,
	'%s_mistagPdf' % name, qf, qt, *otherargs))
    del otherargs
    krawtimepdf = WS(ws, RooProdPdf( '%s_qfqtetapdf' % krawtimepdf.GetName(),
	'%s_qfqtetapdf' % krawtimepdf.GetName(), krawtimepdf, ourmistagpdf))

    # figure out if we need a conditional pdf product for per event
    # decay time error or per event mistag
    condpdfs = [ ]
    parameterizeSet =[ ]
    if None != timeerrpdf:
	condpdfs.append(timeerrpdf)
	if 0 < config['NBinsProperTime'] and timeerrpdf.dependsOn(timeerr):
	    parameterizeSet.append(timeerr)
	    if not timeerr.hasBinning('cache'):
		timeerr.setBins(config['NBinsProperTime'], 'cache')

    if 0 < len(parameterizeSet):
	krawtimepdf.setParameterizeIntegral(RooArgSet(*parameterizeSet))

    # perform conditional pdf product if needed
    if 0 < len(condpdfs):
	noncondset = RooArgSet(time, qf, qt)
	if None != mistagpdf:
	    noncondset.add(mistag)
	retVal = WS(ws, RooProdPdf('%s_NoAccTimePdf' % name,
	    '%s no-acceptance time pdf' % name, RooArgSet(*condpdfs),
	    RooFit.Conditional(RooArgSet(krawtimepdf), noncondset)))
    else:
	retVal = krawtimepdf
    
    if None != acceptance and 0 >= config['NBinsAcceptance']:
	# do not bin acceptance
	retVal = WS(ws, RooEffProd('%s_TimePdf' % name,
	    '%s full time pdf' % name, retVal, acceptance))
    retVal.SetNameTitle('%s_TimePdf' % name, '%s full time pdf' % name)

    # return the copy of retVal which is inside the workspace
    return WS(ws, retVal)

# build B decay time pdf
def buildBDecayTimePdf(
	config,					# configuration dictionary
	name,					# 'Signal', 'DsPi', ...
	ws,					# RooWorkspace into which to put the PDF
	time, timeerr, qt, qf, mistag, tageff,	# potential observables
	Gamma, DeltaGamma, DeltaM,		# decay parameters
	C, D, Dbar, S, Sbar,			# CP parameters
	timeresmodel = None,			# decay time resolution model
	acceptance = None,			# acceptance function
	timeerrpdf = None,			# pdf for per event time error
	mistagpdf = None,			# pdf for per event mistag
	mistagobs = None,			# real mistag observable
	kfactorpdf = None,			# distribution k factor smearing
	kvar = None,				# variable k which to integrate out
	aprod = None,				# production asymmetry
	adet = None,				# detection asymmetry
	atageff = None,				# asymmetry in tagging efficiency
	amistag = None				# asymmetry in mistag
	):
    # Look in LHCb-INT-2011-051 for the conventions used
    from ROOT import ( RooConstVar, TagEfficiencyWeight, IfThreeWayCat,
	    Dilution, RooProduct, RooTruthModel, RooGaussModel, Inverse,
	    RooBDecay, RooProdPdf, RooBinnedPdf, RooEffResModel, RooEffProd,
	    RooUniformBinning, RooArgSet, RooFit, RooWorkspace,
	    RooGeneralisedSmearingBase, RooAbsPdf, RooArgList,
	    RooRealVar, FinalStateChargePdf, RooCategory, DecRateCoeff )
    RooNumGenSmearPdf = RooGeneralisedSmearingBase(RooAbsPdf)

    # constants used
    zero = WS(ws, RooConstVar('zero', 'zero', 0.))
    one = WS(ws, RooConstVar('one', 'one', 1.))

    if None == aprod: aprod = zero
    if None == adet: adet = zero
    if None == atageff: atageff = zero
    if None == amistag: amistag = zero
    if None == mistagpdf:
	mistagobs = mistag
    else:
	if None == mistagobs and mistag.InheritsFrom('RooAbsReal'):
	    mistagobs = mistag

    # if no time resolution model is set, fake one
    if timeresmodel == None:
	timeresmodel = WS(ws, RooTruthModel('%s_TimeResModel' % name,
	    '%s time resolution model' % name, time))
    elif timeresmodel == 'Gaussian':
	timeresmodel = WS(ws, RooGaussModel('%s_TimeResModel' % name,
	    '%s time resolution model' % name, time, zero, timeerr))

    # apply acceptance (if needed)
    if None != acceptance and 0 < config['NBinsAcceptance']:
	if not acceptance.isBinnedDistribution(RooArgSet(time)):
	    acceptance = WS(ws, RooBinnedPdf(
		"%sBinnedAcceptance" % acceptance.GetName(),
		"%sBinnedAcceptance" % acceptance.GetName(),
		time, 'acceptanceBinning', acceptance))
	    acceptance.setForceUnitIntegral(True)
	timeresmodel = WS(ws, RooEffResModel(
	    '%s_timeacc_%s' % (timeresmodel.GetName(), acceptance.GetName()),
	    '%s plus time acceptance %s' % (timeresmodel.GetTitle(), acceptance.GetTitle()),
	    timeresmodel, acceptance))

    # if there is a per-event mistag distributions and we need to do things
    # correctly
    if None != mistagpdf:
	otherargs = [ mistagobs, mistagpdf, tageff, mistag, aprod, adet,
		atageff, amistag ]
    else:
	otherargs = [ tageff, mistag, aprod, adet, atageff, amistag ]
    # build coefficients to go into RooBDecay
    cosh = WS(ws, DecRateCoeff('%s_cosh' % name, '%s_cosh' % name,
	DecRateCoeff.CPEven, qf, qt, one, one, *otherargs))
    sinh = WS(ws, DecRateCoeff('%s_sinh' % name, '%s_sinh' % name,
	DecRateCoeff.CPEven, qf, qt, D, Dbar, *otherargs))
    cos = WS(ws, DecRateCoeff('%s_cos' % name, '%s_cos' % name,
	DecRateCoeff.CPOdd, qf, qt, C, C, *otherargs))
    if 'PdfSSbarSwapMinusOne' in config['BugFlags']:
	sin = WS(ws, DecRateCoeff('%s_sin' % name, '%s_sin' % name,
	    DecRateCoeff.CPOdd, qf, qt, Sbar, S, *otherargs))
    else:
	sin = WS(ws, DecRateCoeff('%s_sin' % name, '%s_sin' % name,
	    DecRateCoeff.CPOdd | DecRateCoeff.Minus, qf, qt, S, Sbar, *otherargs))
    del otherargs

    # perform the actual k-factor smearing integral (if needed)
    # if we have to perform k-factor smearing, we need "smeared" variants of
    # Gamma, DeltaGamma, DeltaM
    if None != kfactorpdf and None != kvar:
	kGamma = WS(ws, RooProduct('%sKGamma' % Gamma.GetName(),
	    '%s k * #Gamma' % Gamma.GetName(),
	    RooArgSet(kvar, Gamma)))
	kDeltaGamma = WS(ws, RooProduct('%sKDeltaGamma' % DeltaGamma.GetName(),
	    '%s k * #Delta#Gamma' % DeltaGamma.GetName(),
	    RooArgSet(kvar, DeltaGamma)))
	kDeltaM = WS(ws, RooProduct('%sKDeltaM' % DeltaM.GetName(),
	    '%s k * #Delta m' % DeltaM.GetName(), RooArgSet(kvar, DeltaM)))
    else:
	# otherwise, we can get away with giving old variables new names
	kGamma, kDeltaGamma, kDeltaM = Gamma, DeltaGamma, DeltaM

    # perform the actual k-factor smearing integral (if needed)
    # build (raw) time pdf
    tau = WS(ws, Inverse('%sTau' % kGamma.GetName(),
	'%s #tau' % kGamma.GetName(), kGamma))
    rawtimepdf = WS(ws, RooBDecay(
	'%s_RawTimePdf' % name, '%s raw time pdf' % name,
	time, tau, kDeltaGamma,	cosh, sinh, cos, sin,
	kDeltaM, timeresmodel, RooBDecay.SingleSided))

    # perform the actual k-factor smearing integral (if needed)
    if None != kfactorpdf and None != kvar:
	krawtimepdf = WS(ws, RooNumGenSmearPdf('%s_kSmearedRawTimePdf' % name,
	    '%s raw time pdf smeared with k factor' % name,
	    kvar, rawtimepdf, kfactorpdf['pdf']))
	# since we fine-tune the range of the k-factor distributions, and we
	# know that the distributions are well-behaved, we can afford to be a
	# little sloppy
        krawtimepdf.convIntConfig().setEpsAbs(1e-4)
        krawtimepdf.convIntConfig().setEpsRel(1e-4)
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('extrapolation','Wynn-Epsilon')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('sumRule','Trapezoid')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('minSteps', 3)
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSteps', 16)
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
        #krawtimepdf.convIntConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
        krawtimepdf.convIntConfig().method1D().setLabel('RooIntegrator1D')
        krawtimepdf.convIntConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')	
	# set integration range
	center = WS(ws, RooConstVar(
	    '%s_kFactorCenter' % name, '%s_kFactorCenter' % name,
	    0.5 * (kfactorpdf['range'][0] + kfactorpdf['range'][1])))
	width = WS(ws, RooConstVar(
	    '%s_kFactorWidth' % name, '%s_kFactorWidth' % name,
	    0.5 * (kfactorpdf['range'][1] - kfactorpdf['range'][0])))
	krawtimepdf.setConvolutionWindow(center, width, 1.0)
	if 0 < config['NBinsTimeKFactor']:
	    kfactortimebinning = WS(ws, RooUniformBinning(     
		time.getMin(), time.getMax(), config['NBinsTimeKFactor'],
		'%s_timeBinnedCache' % name))
	    time.setBinning(kfactortimebinning, kfactortimebinning.GetName())
	    krawtimepdf.setBinnedCache(time, kfactortimebinning.GetName(),
		    RooArgSet(qt, qf))
    else:
	krawtimepdf = rawtimepdf

    # figure out if we need a conditional pdf product for per event
    # decay time error or per event mistag
    condpdfs = [ ]
    parameterizeSet =[ ]
    if None != timeerrpdf:
	condpdfs.append(timeerrpdf)
	if 0 < config['NBinsProperTime'] and timeerrpdf.dependsOn(timeerr):
	    parameterizeSet.append(timeerr)
	    if not timeerr.hasBinning('cache'):
		timeerr.setBins(config['NBinsProperTime'], 'cache')

    if 0 < len(parameterizeSet):
	krawtimepdf.setParameterizeIntegral(RooArgSet(*parameterizeSet))

    # perform conditional pdf product if needed
    if 0 < len(condpdfs):
	noncondset = RooArgSet(time, qf, qt)
	if None == mistagpdf:
	    noncondset.add(mistagobs)
	retVal = WS(ws, RooProdPdf('%s_NoAccTimePdf' % name,
	    '%s no-acceptance time pdf' % name, RooArgSet(*condpdfs),
	    RooFit.Conditional(RooArgSet(krawtimepdf), noncondset)))
    else:
	retVal = krawtimepdf
    
    if None != acceptance and 0 >= config['NBinsAcceptance']:
	# do not bin acceptance
	retVal = WS(ws, RooEffProd('%s_TimePdf' % name,
	    '%s full time pdf' % name, retVal, acceptance))
    retVal.SetNameTitle('%s_TimePdf' % name, '%s full time pdf' % name)

    # return the copy of retVal which is inside the workspace
    return WS(ws, retVal)

def combineCPObservables(config, modes, yields):
    # combine CP observables of different modes according to their respective
    # yields by forming a yield-weighted average of C, D, Dbar, S, Sbar, and
    # return a config-dictionary-like dictionary containing an effective
    # |lambda|, strong and weak phase for each of the modes
    from math import sqrt, atan2
    from B2DXFitters import cpobservables
    C, D, Dbar, S, Sbar = 0., 0., 0., 0., 0.
    # total yield
    toty = 0.
    for mode in yields:
	if mode in modes:
	    toty += yields[mode]
    # average C, ...
    for mode in modes:
	if mode not in config['Modes']:
	    continue
	ACPobs = cpobservables.AsymmetryObservables(
		config['StrongPhase'][mode] - config['WeakPhase'][mode],
		config['StrongPhase'][mode] + config['WeakPhase'][mode],
		config['ModLf'][mode])
	y = yields[mode] / toty
	C    += y * ACPobs.Cf()
	D    += y * ACPobs.Df()
	S    += y * ACPobs.Sf()
	Dbar += y * ACPobs.Dfbar()
	Sbar += y * ACPobs.Sfbar()
    # average formed, convert back to |lambda|, weak and strong phase
    ModLf    = sqrt((1. - C) / (1. + C))
    ArgLf    = atan2(S    / (1. + C * C), D    / (1. + C * C))
    ArgLfbar = atan2(Sbar / (1. + C * C), Dbar / (1. + C * C))
    StrongPhase = 0.5 * (ArgLfbar + ArgLf)
    WeakPhase   = 0.5 * (ArgLfbar - ArgLf)
    retVal = dict(config)
    for mode in modes:
	if mode not in config['Modes']:
	    continue
	retVal['ModLf'][mode] = ModLf
	retVal['StrongPhase'][mode] = StrongPhase
	retVal['WeakPhase'][mode] = WeakPhase
    return retVal

#------------------------------------------------------------------------------
def getMasterPDF(config, name, debug = False):
    from B2DXFitters import taggingutils, cpobservables

    GeneralModels = ROOT.GeneralModels
    PTResModels   = ROOT.PTResModels

    import sys
    from ROOT import (RooRealVar, RooStringVar, RooFormulaVar, RooProduct,
	    RooCategory, RooMappedCategory, RooMultiCategory, RooConstVar,
	    RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay,
	    RooGaussModel, RooTruthModel, RooWorkspace, RooAbsArg,
	    RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooExponential,
	    RooPolynomial, RooUniform, RooFit, RooUniformBinning,
	    IfThreeWayCat, Dilution, IfThreeWayCatPdf, CombBkgPTPdf,
	    BdPTAcceptance, RooSimultaneous, RangeAcceptance, RooEffProd,
	    SquaredSum, CPObservable, PowLawAcceptance, MistagCalibration)
    # fix context
    config = dict(config)
    config['Context'] = name
    # forcibly fix various settings
    if config['PerEventMistag'] and config['Sanitise']:
	if 'tagOmegaSig' in config['constParams']:
	    config['constParams'].remove('tagOmegaSig')
    if 'GEN' in name and config['Sanitise']:
	# for generation, this is both faster and more accurate
	config['NBinsAcceptance'] = 0
	config['NBinsMistag'] = 0
	config['NBinsProperTime'] = 0
	config['NBinsMass'] = 0
	config['MistagInterpolation'] = False
	config['MassInterpolation'] = False
	config['AcceptanceCorrectionInterpolation'] = False
	config['CombineModesForEffCPObs'] = [ ]
    print '########################################################################'
    print '%s config:' % name
    print
    for k in sorted(config.keys()):
        print '%-32s: %s' % (k, str(config[k]))
    print '########################################################################'
    ws = RooWorkspace('WS_%s' % name)

    zero = WS(ws, RooConstVar('zero', '0', 0.))
    one = WS(ws, RooConstVar('one', '1', 1.))

    # figure out lower bound of fit range
    timelo = 0.2
    if config['AcceptanceFunction'] == 'BdPTAcceptance':
    	timelo = config['BdPTAcceptance_offset']
    time = WS(ws, RooRealVar('time', 'decay time',
		1., timelo, 15., 'ps'))
    if config['NBinsAcceptance'] > 0:
	# provide binning for acceptance
	from ROOT import RooUniformBinning
	acceptanceBinning = WS(ws, RooUniformBinning(
	    time.getMin(), time.getMax(), config['NBinsAcceptance'],
	    'acceptanceBinning'))
	time.setBinning(acceptanceBinning, 'acceptanceBinning')
    timeerr = WS(ws, RooRealVar('timeerr', 'decay time error',
	0.05, 0.01, 0.1, 'ps'))

    mass = WS(ws, RooRealVar('mass', 'mass', 5320., 5420.))
    if config['NBinsMass'] > 0:
	mass.setBinning(RooUniformBinning(
	    mass.getMin(), mass.getMax(), config['NBinsMass']), 'massbins')
    
    gammas = WS(ws, RooRealVar('Gammas', 'B_{s} average lifetime',
	config['Gammas'], 'ps^{-1}'))
    deltaGammas = WS(ws, RooRealVar('deltaGammas', 'B_{s} Lifetime difference',
	config['DGsOverGs'] * config['Gammas'], 'ps^{-1}'))
    gammad = WS(ws, RooConstVar('Gammad', 'B_{d} average lifetime',
	config['Gammad']))
    deltaGammad = WS(ws, RooConstVar('deltaGammad', 'B_{d} Lifetime difference',
	config['DeltaGammad']))
    deltaMd = WS(ws, RooConstVar('deltaMd', '#Delta m_{d}',
	config['DeltaMd']))

    k = WS(ws, RooRealVar('k', 'k factor', 1.))
    k.setConstant(True)

    deltaMs = WS(ws, RooRealVar('deltaMs', '#Delta m_{s}',
	    config['DeltaMs'], 5., 30., 'ps^{-1}'))

    # tagging
    # -------
    tagOmegaSig = WS(ws, RooRealVar(
	    'tagOmegaSig', 'Signal mistag rate',
	    config['TagOmegaSig'], 0., 0.5))
    tagOmegaSig.setError(0.1)

    qt = WS(ws, RooCategory('qt', 'flavour tagging result'))
    qt.defineType('B'       ,  1)
    qt.defineType('Bbar'    , -1)
    qt.defineType('Untagged',  0)

    qf = WS(ws, RooCategory('qf', 'bachelor charge'))
    qf.defineType('h+',  1)
    qf.defineType('h-', -1)

    # mass pdfs/templates are split into magnet polarities (up/down) and
    # Ds final state (kkpi, kpipi, pipipi) - replicate this structure here
    # so we can do a simultaneous fit
    sample = WS(ws, RooCategory('sample', 'sample'))
    for pol in ('up', 'down'):
	for DsMode in ('kkpi', 'kpipi', 'pipipi'):
	    sample.defineType('%s_%s' % (pol, DsMode))

    # Define the observables
    # ----------------------
    observables = [ mass, time, qt, qf, sample ]
    condobservables = [ ]

    if config['PerEventMistag']:
	mistagcalib = RooArgList()
	avgmistag = zero
        if len(config['MistagCalibrationParams']) == 2 or \
		len(config['MistagCalibrationParams']) == 3:
            i = 0
    	    for p in config['MistagCalibrationParams'][0:2]:
		mistagcalib.add(WS(ws, RooRealVar(
		    'MistagCalib_p%u' % i, 'MistagCalib_p%u' % i, p)))
    	        i = i + 1
	    del i
    	    if len(config['MistagCalibrationParams']) == 3:
		avgmistag = WS(ws, RooRealVar(
		    'MistagCalib_avgmistag', 'MistagCalib_avgmistag', 
		    config['MistagCalibrationParams'][2]))
	tagOmegaSigCal = WS(ws, MistagCalibration(
	    '%s_c' % tagOmegaSig.GetName(), '%s_c' % tagOmegaSig.GetName(),
	    tagOmegaSig, mistagcalib, avgmistag))
	del mistagcalib
	del avgmistag
    else:
	tagOmegaSigCal = tagOmegaSig
    # read in templates
    if config['PerEventMistag']:
	mistagtemplate = getMistagTemplate(config, ws, tagOmegaSig)
    else:
	mistagtemplate = None
    if config['UseKFactor']:
	ktemplates = getKFactorTemplates(config, ws, k)
    else:
	ktemplates = None
    masstemplates = getMassTemplates(config, ws, mass)

    # ok, since the mistagtemplate often is a RooHistPdf, we can fine-tune
    # ranges and binning to match the histogram
    if config['PerEventMistag'] and \
	    mistagtemplate.InheritsFrom('RooHistPdf'):
	hist = mistagtemplate.dataHist().createHistogram(tagOmegaSig.GetName())
	ROOT.SetOwnership(hist, True)
	ax = hist.GetXaxis()
	nbins = hist.GetNbinsX()
	print 'INFO: adjusting range of %s to histogram ' \
		'used in %s: %g to %g, was %g to %g' % \
		(tagOmegaSig.GetName(), mistagtemplate.GetName(),
			ax.GetBinLowEdge(1), ax.GetBinUpEdge(nbins),
			tagOmegaSig.getMin(), tagOmegaSig.getMax())
	tagOmegaSig.setRange(ax.GetBinLowEdge(1), ax.GetBinUpEdge(nbins))
	if config['MistagInterpolation']:
	    # protect against "negative events" in sWeighted source histos
	    for i in xrange(0, nbins):
		if hist.GetBinContent(1 + i) < 0.:
		    print "%%% WARNING: mistag template %s has negative entry"\
			    "in bin %u: %g" % (mistagtemplate.GetName(), \
			    1 + i, hist.GetBinContent(1 + i))
		    hist.SetBinContent(1 + i, 0.)
	    del i
	    from ROOT import RooBinned1DQuinticBase, RooAbsPdf
	    RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
	    mistagtemplate = WS(ws, RooBinned1DQuinticPdf(
	        '%s_interpol' % mistagtemplate.GetName(),
	        '%s_interpol' % mistagtemplate.GetName(),
	        hist, tagOmegaSig, True))
	del ax
	del hist
	if config['NBinsMistag'] > 0 and nbins < config['NBinsMistag']:
	    print 'INFO: adjusting binning of %s to histogram ' \
		    'used in %s: %u bins, was %u bins' % \
		    (tagOmegaSig.GetName(), mistagtemplate.GetName(),
			    nbins, config['NBinsMistag'])
	    config['NBinsMistag'] = nbins
        del nbins

    timepdfs = { }

    # Decay time resolution model
    # ---------------------------
    if 'PEDTE' not in config['DecayTimeResolutionModel']:
        trm = WS(ws, PTResModels.getPTResolutionModel(
	    config['DecayTimeResolutionModel'],
	    time, 'Bs', debug,
	    config['DecayTimeResolutionScaleFactor'],
	    config['DecayTimeResolutionBias']))
    else :
        # the decay time error is an extra observable!
        observables.append(timeerr)
        # time, mean, scale, timeerr
        trm = WS(ws, RooGaussModel('GaussianWithPEDTE',
	    'GaussianWithPEDTE',
	    time, RooFit.RooConst(0.), RooFit.RooConst(1.), timeerr ))

    # Decay time acceptance function
    # ------------------------------
    if config['AcceptanceFunction'] and not (
	    config['AcceptanceFunction'] == None or
	    config['AcceptanceFunction'] == 'None'):
	acc_corr = readAcceptanceCorrection(config, ws, time)
	if 'BdPTAcceptance' == config['AcceptanceFunction']:
            tacc_slope  = WS(ws, RooRealVar('tacc_slope' , 'BdPTAcceptance_slope',
	        config['BdPTAcceptance_slope']))
            tacc_offset = WS(ws, RooRealVar('tacc_offset', 'BdPTAcceptance_offset',
	        config['BdPTAcceptance_offset']))
            tacc_beta = WS(ws, RooRealVar('tacc_beta', 'BdPTAcceptance_beta',
	        config['BdPTAcceptance_beta']))
            tacc = WS(ws, BdPTAcceptance('BsPTAccFunction',
	        'decay time acceptance function',
	        time, tacc_beta, tacc_slope, tacc_offset))
	elif 'PowLawAcceptance' == config['AcceptanceFunction']:
	    tacc_beta = WS(ws, RooRealVar('tacc_beta', 'tacc_beta',
		config['PowLawAcceptance_beta']))
	    tacc_expo = WS(ws, RooRealVar('tacc_expo', 'tacc_expo',
		config['PowLawAcceptance_expo']))
	    tacc_offset = WS(ws, RooRealVar('tacc_offset', 'tacc_offset',
		config['PowLawAcceptance_offset']))
	    tacc_turnon = WS(ws, RooRealVar('tacc_turnon', 'tacc_turnon',
		config['PowLawAcceptance_turnon']))
	    if None != acc_corr:
		tacc = WS(ws, PowLawAcceptance('PowLawAcceptance',
		    'decay time acceptance', tacc_turnon, time, tacc_offset,
		    tacc_expo, tacc_beta, acc_corr))
	    else:
		tacc = WS(ws, PowLawAcceptance('PowLawAcceptance',
		    'decay time acceptance', tacc_turnon, time, tacc_offset,
		    tacc_expo, tacc_beta))
	else:
	    print 'ERROR: unknown acceptance function: ' + config['AcceptanceFunction']
	    sys.exit(1)
	if 0 < config['NBinsAcceptance'] and config['StaticAcceptance']:
	    from ROOT import RooDataHist, RooHistPdf
	    dhist = WS(ws, RooDataHist(
		    '%s_dhist' % tacc.GetName(), '%s_dhist' % tacc.GetName(),
		    RooArgSet(time), 'acceptanceBinning'))
	    tacc.fillDataHist(dhist, RooArgSet(time), 1.)
	    dhist.SetNameTitle('%s_dhist' % tacc.GetName(), '%s_dhist' % tacc.GetName())
	    tacc = WS(ws, RooHistPdf(
		'%s_binned' % tacc.GetName(), '%s_binned' % tacc.GetName(),
		RooArgSet(time), dhist, 0))
    else:
        tacc = None
    
    # Decay time error distribution
    # -----------------------------
    if 'PEDTE' in config['DecayTimeResolutionModel']:
	# resolution in ps: 3/terrpdf_shape
        terrpdf_shape = WS(ws, RooConstVar('terrpdf_shape', 'terrpdf_shape', -60.))
        terrpdf_truth = WS(ws, RooTruthModel('terrpdf_truth', 'terrpdf_truth', timeerr))
        terrpdf_i0 = WS(ws, RooDecay('terrpdf_i0', 'terrpdf_i0', timeerr, terrpdf_shape,
                terrpdf_truth, RooDecay.SingleSided))
        terrpdf_i1 = WS(ws, RooPolynomial('terrpdf_i1','terrpdf_i1',
                timeerr, RooArgList(zero, zero, one), 0))
        terrpdf = WS(ws, RooProdPdf('terrpdf', 'terrpdf', terrpdf_i0, terrpdf_i1))
	if config['DecayTimeErrInterpolation']:
            from ROOT import RooBinned1DQuinticBase, RooAbsPdf
            RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
	    obins = timeerr.getBins()
	    nbins = config['NBinsProperTime']
	    if 0 == nbins:
	        print 'ERROR: requested binned interpolation of timeerr %s %d %s' % (
	    	    'histograms with ', nbins, ' bins - increasing to 100 bins')
	        nbins = 100
            timeerr.setBins(nbins)
            hist = terrpdf.createHistogram('%s_hist' % terrpdf.GetName(), timeerr)
            hist.Scale(1. / hist.Integral())
            ROOT.SetOwnership(hist, True)
            terrpdf = WS(ws, RooBinned1DQuinticPdf(
	        '%s_interpol' % terrpdf.GetName(),
	        '%s_interpol' % terrpdf.GetName(), hist, timeerr, True))
            del hist
            timeerr.setBins(obins)
	    del obins
	    del nbins
    else:
	terrpdf = None
    
    if config['PerEventMistag']:
	observables.append(tagOmegaSig)
	if config['TrivialMistag']:
	    from ROOT import MistagDistribution
	    omega0 = WS(ws, RooConstVar('omega0', 'omega0', 0.07))
	    omegaf = WS(ws, RooConstVar('omegaf', 'omegaf', 0.25))
	    omegaa = WS(ws, RooConstVar('omegaa', 'omegaa', config['TagOmegaSig']))
	    sigMistagPDF = WS(ws, MistagDistribution(
	        'sigMistagPDF_trivial', 'sigMistagPDF_trivial',
	        tagOmegaSigCal, omega0, omegaa, omegaf))
	else:
	    sigMistagPDF = mistagtemplate
    else:
	sigMistagPDF = None

    # produce a pretty-printed yield dump in the signal region
    yielddict = {}
    totyielddict = {'up': {}, 'down': {}}
    print
    print 'Yield dump:'
    print '%16s %35s %35s %11s' % ('', 'magnet up', 'magnet down', '')
    print '%16s %11s %11s %11s %11s %11s %11s %11s' % (
	    'mode', 'kkpi', 'kpipi', 'pipipi', 'kkpi', 'kpipi', 'pipipi', 'total')
    tottot = 0.
    for mode in config['Modes']:
        tot = 0.
        yields = ()
        for pol in ('up', 'down'):
	    for DsMode in ('kkpi', 'kpipi', 'pipipi'):
		y = masstemplates[mode][pol][DsMode]['yield'].getVal()
                yields += (y,)
                tot += y
		if DsMode not in totyielddict[pol]:
		    totyielddict[pol][DsMode] = 0.
		totyielddict[pol][DsMode] += y
        yields += (tot,)
        yields = (mode,) + yields
        print '%16s %11.5g %11.5g %11.5g %11.5g %11.5g %11.5g %11.5g' % yields
        tottot += tot
	yielddict[mode] = tot
        del tot
        del yields
        del y
    yields = ('Total',)
    for pol in ('up', 'down'):
	for DsMode in ('kkpi', 'kpipi', 'pipipi'):
	    yields += (totyielddict[pol][DsMode],)
    yields += (tottot,)
    print '%16s %11.5g %11.5g %11.5g %11.5g %11.5g %11.5g %11.5g' % yields
    print
    del yields
    del tottot
    del totyielddict
    
    # list of constraints to pass to the fitting stage
    constraints = [ ]
    ########################################################################
    # Bs -> Ds K like modes
    ########################################################################
    # create time pdfs for the remaining DsK-like modes
    #
    # signal Bs -> DsK is treated in the same way as the backgrounds
    for mode in ( 'Bs2DsK', 'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst' ):
	if mode not in config['Modes']:
	    continue
	# limits in which CP observables are allowed to vary
	limit = 3.0
	if 'Bs2DsK' == mode and config['Bs2DsKCPObs'].startswith('CDS'):
	    # calculate CP observables from the respective |lambda|, arg(lambda),
	    # arg(lambdabar)
	    ACPobs = cpobservables.AsymmetryObservables(
		    config['StrongPhase'][mode] - config['WeakPhase'][mode],
		    config['StrongPhase'][mode] + config['WeakPhase'][mode],
		    config['ModLf'][mode])
            ACPobs.printtable(mode)
	    # standard C, D, Dbar, S, Sbar parametrisation
	    myconfig = config
	    modenick = mode
	    C    = WS(ws, RooRealVar(
	        '%s_C' % mode   , '%s_C' % mode   , ACPobs.Cf()   , -limit, limit))
	    D    = WS(ws, RooRealVar(
	        '%s_D' % mode   , '%s_D' % mode   , ACPobs.Df()   , -limit, limit))
	    Dbar = WS(ws, RooRealVar(
	        '%s_Dbar' % mode, '%s_Dbar' % mode, ACPobs.Dfbar(), -limit, limit))
	    S    = WS(ws, RooRealVar(
	        '%s_S' % mode   , '%s_S' % mode   , ACPobs.Sf()   , -limit, limit))
	    Sbar = WS(ws, RooRealVar(
	        '%s_Sbar' % mode, '%s_Sbar' % mode, ACPobs.Sfbar(), -limit, limit))
	    C.setError(0.4)
	    for v in (D, Dbar, S, Sbar):
		v.setError(0.6)
	    if 'Constrained' in config['Bs2DsKCPObs']:
		# optionally constrain the squared sums to be one
		sqsum = WS(ws, SquaredSum(
		    '%s_sqsum' % mode, '%s_sqsum' % mode, C, D, S))
		sqsumbar = WS(ws, SquaredSum(
		    '%s_sqsumbar' % mode, '%s_sqsumbar' % mode, C, Dbar, Sbar))
		strength = WS(ws, RooConstVar(
		    '%s_constraintStrength' % mode,
		    '%s_constraintStrength' % mode,
		    config['SqSumCDSConstraintWidth']))
		constraints.append(
			WS(ws, RooGaussian(
			    '%s_constraint' % mode, '%s_constraint' % mode,
			    sqsum, one, strength)))
		constraints.append(
			WS(ws, RooGaussian(
			    '%s_bar_constraint' % mode, '%s_bar_constraint' % mode,
			    sqsumbar, one, strength)))
	else: # either not Bs->DsK, or we fit directly for gamma, delta, lambda
	    if mode in config['CombineModesForEffCPObs']:
		for m in config['CombineModesForEffCPObs']:
		    if m not in config['Modes']:
			continue
		    modenick = m
		myconfig = combineCPObservables(
			config, config['CombineModesForEffCPObs'], yielddict)
		ACPobs = cpobservables.AsymmetryObservables(
			myconfig['StrongPhase'][mode] - myconfig['WeakPhase'][mode],
			myconfig['StrongPhase'][mode] + myconfig['WeakPhase'][mode],
			myconfig['ModLf'][mode])
		ACPobs.printtable('effective %s' % modenick)
	    else:
		modenick = mode
		myconfig = config
	    Lambda = WS(ws, RooRealVar('%s_lambda' % modenick, '%s_lambda' % modenick,
		myconfig['ModLf'][modenick], 0., 3.0))
	    delta = WS(ws, RooRealVar('%s_delta' % modenick, '%s_delta' % modenick,
		myconfig['StrongPhase'][modenick], -3. * pi, 3. * pi))
	    phi_w = WS(ws, RooRealVar('%s_phi_w' % modenick, '%s_phi_w' % modenick,
		myconfig['WeakPhase'][modenick], -3. * pi, 3. * pi))
	    Lambda.setError(1.5)
	    delta.setError(1.5)
	    phi_w.setError(1.5)
	    C    = WS(ws, CPObservable('%s_C' % modenick, '%s_C' % modenick,
		Lambda, delta, phi_w, CPObservable.C))
	    D    = WS(ws, CPObservable('%s_D' % modenick, '%s_D' % modenick,
		Lambda, delta, phi_w, CPObservable.D))
	    S    = WS(ws, CPObservable('%s_S' % modenick, '%s_S' % modenick,
		Lambda, delta, phi_w, CPObservable.S))
	    Dbar = WS(ws, CPObservable('%s_Dbar' % modenick, '%s_Dbar' % modenick,
		Lambda, delta, phi_w, CPObservable.Dbar))
	    Sbar = WS(ws, CPObservable('%s_Sbar' % modenick, '%s_Sbar' % modenick,
		Lambda, delta, phi_w, CPObservable.Sbar))
	# figure out asymmetries to use
	asyms = { 'Prod': None, 'Det': None, 'TagEff': None, 'Mistag': None }
	for k in asyms.keys():
	    for n in (mode, modenick, mode.split('2')[0]):
		if n in config['Asymmetries'][k]:
		    asyms[k] = WS(ws, RooRealVar(
			'%s_Asym%s' % (n, k), '%s_Asym%s' % (n, k),
			config['Asymmetries'][k][n], -1., 1.))
		    asyms[k].setError(0.25)
		    break
	if config['UseKFactor'] and 'Bs2DsK' != mode and mode in ktemplates:
	    kfactorpdf, kfactor = ktemplates[mode], k
	else:
	    kfactorpdf, kfactor = None, None
        tageff = WS(ws, RooRealVar('%s_TagEff' % modenick, '%s_TagEff' % modenick,
		    config['TagEffSig'], 0., 1.))
	tageff.setError(0.25)
        timepdfs[mode] = buildBDecayTimePdf(myconfig, mode, ws,
		time, timeerr, qt, qf, tagOmegaSigCal, tageff,
		gammas, deltaGammas, deltaMs, C, D, Dbar, S, Sbar,
		trm, tacc, terrpdf, sigMistagPDF, tagOmegaSig, kfactorpdf, kfactor,
		asyms['Prod'], asyms['Det'], asyms['TagEff'], asyms['Mistag'])

    ########################################################################
    # Bs -> Ds Pi like modes
    ########################################################################
    for mode in ( 'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bs2DsstRho',
	    'Bd2DsK', 'Bd2DK' ):
	if mode not in config['Modes']:
	    continue
	if mode.startswith('Bs'):
	    gamma, deltagamma, deltam = gammas, deltaGammas, deltaMs
	    modenick = 'Bs2DsPi'
	elif mode.startswith('Bd'):
	    gamma, deltagamma, deltam = gammad, deltaGammad, deltaMd
	    modenick = 'Bd2DsK'
	else:
	    gamma, deltagamma, deltam = None, None, None
	    modenick = mode
	# figure out asymmetries to use
	asyms = { 'Prod': None, 'Det': None, 'TagEff': None, 'Mistag': None }
	for k in asyms.keys():
	    for n in (mode, modenick, mode.split('2')[0]):
		if n in config['Asymmetries'][k]:
		    asyms[k] = WS(ws, RooRealVar(
			'%s_Asym%s' % (n, k), '%s_Asym%s' % (n, k),
			config['Asymmetries'][k][n], -1., 1.))
		    asyms[k].setError(0.25)
		    break
	# Bd2DsK does not need k-factor (delta(k))
	if config['UseKFactor'] and 'Bd2DsK' != mode:
	    kfactorpdf, kfactor = ktemplates[mode], k
	else:
	    kfactorpdf, kfactor = None, None
	tageff = WS(ws, RooRealVar(
	    '%s_TagEff' % modenick, '%s_TagEff' % modenick,
	    config['TagEffSig'], 0., 1.))
	tageff.setError(0.25)
	timepdfs[mode] = buildBDecayTimePdf(config, mode, ws,
		time, timeerr, qt, qf, tagOmegaSigCal, tageff,
		gamma, deltagamma, deltam, one, zero, zero, zero, zero,
		trm, tacc, terrpdf, sigMistagPDF, tagOmegaSig, kfactorpdf, kfactor,
		asyms['Prod'], asyms['Det'], asyms['TagEff'],
		asyms['Mistag'])

    ########################################################################
    # non-osciallating modes
    ########################################################################
    # Lb->X modes first, then CombBkg
    for mode in ('Lb2Dsp', 'Lb2Dsstp', 'Lb2LcK', 'CombBkg'):
	if mode not in config['Modes']:
	    continue
	if config['UseKFactor'] and mode != 'CombBkg':
	    kfactorpdf, kfactor = ktemplates[mode], k
	else:
	    kfactorpdf, kfactor = None, None
        if mode.startswith('Lb'):
            modenick = 'Lb'
	    gamma = WS(ws, RooConstVar('GammaLb', '#Gamma_{#Lambda_{b}}',
			config['GammaLb']))
	    tageff = config['TagEffSig']
        else:
	    modenick = mode
	    gamma = WS(ws, RooConstVar('GammaCombBkg', '#Gamma_{CombBkg}',
			config['GammaCombBkg']))
            tageff = config['TagEffBkg']
	# figure out asymmetries to use
	asyms = { 'Det': None, 'TagEff_f': None, 'TagEff_t': None }
	for k in asyms.keys():
	    for n in (mode, modenick, mode.split('2')[0]):
		if n in config['Asymmetries'][k]:
		    asyms[k] = WS(ws, RooRealVar(
			'%s_Asym%s' % (n, k), '%s_Asym%s' % (n, k),
			config['Asymmetries'][k][n], -1., 1.))
		    break
        tageff = WS(ws, RooRealVar('%s_TagEff' % modenick, '%s_TagEff' % modenick,
		    tageff, 0., 1.))
	tageff.setError(0.25)
	timepdfs[mode] = buildNonOscDecayTimePdf(config, mode, ws,
		    time, timeerr, qt, qf, tagOmegaSig, tageff, gamma,
		    trm, tacc, terrpdf, sigMistagPDF, kfactorpdf, kfactor,
		    asyms['Det'], asyms['TagEff_f'], asyms['TagEff_t'])
    
    # Create the total PDF/EPDF
    # ---------------------
    #
    # gather the bits and pieces
    pdfs = RooArgList()
    for mode in config['Modes']:
	timepdf = timepdfs[mode]
	masspdf = WS(ws, RooSimultaneous(
	    '%s_MassEPDF' % mode, '%s_MassEPDF' % mode, sample))
	for pol in ('up', 'down'):
	    for dsmode in ('kkpi', 'kpipi', 'pipipi'):
		mpdf = masstemplates[mode][pol][dsmode]
		# only bother if there's yield in that component
		if (0. == abs(mpdf['yield'].getVal()) and
			mpdf['yield'].isConstant()):
		    continue
	        # mass integration factorises, so we can afford to be a little sloppier
	        # when doing numerical integrations
                mpdf['pdf'].specialIntegratorConfig(True).setEpsAbs(1e-9)
                mpdf['pdf'].specialIntegratorConfig().setEpsRel(1e-9)
		mpdf['pdf'].specialIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('sumRule', 'Trapezoid')
		mpdf['pdf'].specialIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation', 'Wynn-Epsilon')
		mpdf['pdf'].specialIntegratorConfig().getConfigSection('RooIntegrator1D').setRealValue('minSteps', 3)
		mpdf['pdf'].specialIntegratorConfig().getConfigSection('RooIntegrator1D').setRealValue('maxSteps', 16)
        	mpdf['pdf'].specialIntegratorConfig().method1D().setLabel('RooIntegrator1D')
		masspdf.addPdf(WS(ws, RooExtendPdf(
		    '%s_%s_%s_MassEPDF' % (mode, pol, dsmode),
		    '%s_%s_%s_MassEPDF' % (mode, pol, dsmode),
		    mpdf['pdf'], mpdf['yield'])),
		    '%s_%s' % (pol, dsmode))
	# multiply mass and time pdfs and add to list of pdf to be added up
	pdfs.add(WS(ws, RooProdPdf('%s_EPDF' % mode, '%s_EPDF' % mode,
	    RooArgList(timepdf, masspdf))))
    totEPDF = WS(ws, RooAddPdf('TotEPDF', 'TotEPDF', pdfs))

    # set variables constant if they are supposed to be constant
    setConstantIfSoConfigured(config, totEPDF)

    obs = RooArgSet('observables')
    for o in observables:
	obs.add(o)
    condobs = RooArgSet('condobservables')
    for o in condobservables:
	condobs.add(o)
    constr = RooArgSet('constraints')
    for c in constraints:
	constr.add(c)
    
    print 72 * '#'
    print 'Configured master pdf %s' % totEPDF.GetName()
    print
    print 'Observables:'
    for o in observables:
	print '    %s' % o.GetName()
    print
    print 'Conditional observables:'
    for o in condobservables:
	print '    %s' % o.GetName()
    print
    print 'Constraints:'
    for o in constraints:
	print '    %s' % o.GetName()
    print
    print 72 * '#'
    retVal = {
	    'ws': ws,
	    'epdf': WS(ws, totEPDF),
	    'observables': WS(ws, obs),
	    'condobservables': WS(ws, condobs),
	    'constraints': WS(ws, constr)
	    }
    return retVal

def runBsGammaFittercFit(generatorConfig, fitConfig, toy_num, debug, wsname, initvars) :
    from B2DXFitters import taggingutils, cpobservables

    GeneralModels = ROOT.GeneralModels
    PTResModels   = ROOT.PTResModels
    
    from ROOT import ( RooRealVar, RooStringVar, RooFormulaVar, RooProduct,
	    RooCategory, RooMappedCategory, RooMultiCategory, RooConstVar,
	    RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay,
	    RooGaussModel, RooTruthModel, RooWorkspace, RooAbsArg, RooAddPdf,
	    RooProdPdf, RooExtendPdf, RooGenericPdf, RooExponential,
	    RooUniform, RooFit, RooUniformBinning, TRandom3,
	    IfThreeWayCat, Dilution, IfThreeWayCatPdf, CombBkgPTPdf,
	    RooDataSet, BdPTAcceptance, RooLinkedList, RooRandom )

    # tune integrator configuration
    from ROOT import RooAbsReal
    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')

    # Instantiate and run the fitter in toy MC mode
    # (generate using the PDFs)
    pdf = getMasterPDF(generatorConfig, 'GEN', debug)

    # seed the pseudo random number generator
    rndm = TRandom3(toy_num + 1)
    RooRandom.randomGenerator().SetSeed(int(rndm.Uniform(4294967295)))
    del rndm

    cats = [ ]
    for cat in [ 'sample', 'qt', 'qf' ]:
	cats.append(pdf['ws'].obj(cat))

    if None == generatorConfig['DataFileName']:
	# generate events ourselves
	dataset = pdf['epdf'].generate(pdf['observables'], RooFit.Verbose())
        # we want our own copy of the data set to do with as we please
        ROOT.SetOwnership(dataset, True)
    else:
	# read event from external file
	dataset = readDataSet(
		generatorConfig, pdf['ws'],
		pdf['ws'].var('time'),
		pdf['ws'].var('mass'),
		pdf['ws'].var('tagOmegaSig'),
		pdf['ws'].obj('qf'),
		pdf['ws'].obj('qt'),
		pdf['ws'].obj('sample'))
	# fix fitter config yields
	fitConfig['NEvents'] = []
	sample = pdf['ws'].obj('sample')
	for pol in ('up', 'down'):
	    for dsmode in ('kkpi', 'kpipi', 'pipipi'):
		i = sample.lookupType('%s_%s' % (pol, dsmode)).getVal()
		tmpds = dataset.reduce(RooFit.Cut('sample==%d' % i))
		ROOT.SetOwnership(tmpds, True)
		fitConfig['NEvents'].append(tmpds.numEntries())
		del tmpds

    dataset.Print('v')
    for cat in cats:
	dataset.table(cat).Print('v')
    dataset.table(RooArgSet(pdf['ws'].obj('qt'), pdf['ws'].obj('qf'))).Print('v')

    # to speed things up during the fit, we sort events by qf and qt
    # this avoids "cache poisoning" by making pdf argument changes rarer
    oldds = [ dataset ]
    del dataset
    # split according to category
    for s in cats[0:3]:
	newds = [ ]
	# loop over datasets, split each in subsamples, one per category index
	for ds in oldds:
	    it = s.typeIterator()
	    while True:
		obj = it.Next()
		if None == obj:
		    break
		newds.append(ds.reduce(
		    RooFit.Cut('%s==%s' % (s.GetName(), obj.getVal()))))
		del obj
	    del it
	    for ds in newds:
		ROOT.SetOwnership(ds, True)
	# split step for current category done
	oldds = newds
	del newds
    # now merge all datasets
    while len(oldds) > 1:
	oldds[0].append(oldds[1])
	del oldds[1]
    dataset = oldds[0]
    del oldds

    del cats
    del pdf

    pdf = getMasterPDF(fitConfig, 'FIT', debug)

    dataset = dataset.reduce(RooFit.SelectVars(pdf['observables']))
    ROOT.SetOwnership(dataset, True)
    dataset = WS(pdf['ws'], dataset, [])

    plot_init   = (wsname != None) and initvars
    plot_fitted = (wsname != None) and (not initvars)

    if plot_init :
        pdf['ws'].writeToFile(wsname)
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
    if 0 < pdf['condobservables'].getSize():
	fitOpts.append(RooFit.ConditionalObservables(pdf['condobservables']))
    if 0 < pdf['constraints'].getSize():
	fitOpts.append(RooFit.ExternalConstraints(pdf['constraints']))

    fitopts = RooLinkedList()
    for o in fitOpts:
        fitopts.Add(o)

    fitResult = pdf['epdf'].fitTo(dataset, fitopts)

    printResult(fitConfig, fitResult,
	    fitConfig['Blinding'] and not fitConfig['IsToy'])

    if plot_fitted:
        pdf['ws'].writeToFile(wsname)

    del pdf

def updateConfigDict(configDict, updateDict):
    import sys
    for k in updateDict.keys():
	if k not in configDict:
	    print 'Configuration dictionary: unknown key %s, aborting.' % k
	    sys.exit(1)
    configDict.update(updateDict)
    return configDict

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
	    fitConfig = updateConfigDict(fitConfig, d)
            del d
	except:
	    parser.error('Unable to parse fit configuration in file %s' %
		    options.fitConfigFile)
        del lines
    if None != options.fitConfigString:
	try:
	    d = eval(compile(options.fitConfigString, '[command line]', 'eval'))
	    fitConfig = updateConfigDict(fitConfig, d)
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
	    generatorConfig = updateConfigDict(generatorConfig, d)
            del d
	except:
	    parser.error('Unable to parse generator configuration in file %s' %
		    options.genConfigFile)
        del lines
    if None != options.genConfigString:
	try:
	    d = eval(compile(options.genConfigString, '[command line]', 'eval'))
	    generatorConfig = updateConfigDict(generatorConfig, d)
            del d
	except:
	    parser.error('Unable to parse generator configuration in \'%s\'' %
		    options.genConfigString)
    
    runBsGammaFittercFit(
            generatorConfig,
            fitConfig,
            TOY_NUMBER,
	    options.debug,
	    options.wsname,
	    options.initvars)

    # -----------------------------------------------------------------------------
