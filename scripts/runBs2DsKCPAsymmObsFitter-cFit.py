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
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
import os, sys, gc

# set a flag if we have access to AFS (can be used in the personality files)
haveAFS = os.path.isdir('/afs') and os.path.isdir('/afs/cern.ch')

# -----------------------------------------------------------------------------
# Configuration settings
#
# defaultConfig contains default settings
#
# the defaultConfig dictionary is updated with dictionary entries according to
# a "personality" which is loaded from a file
#
# generatorConfig contains settings to use during generation
# fitConfig contains settings to use during fit
#
# fitConfig and generatorConfig can be updated to suit your needs
# there are two ways: either by inserting code below (see example), or by
# using job options (which take a string or a file with python code which
# must evaluate to a dictionary)
# -----------------------------------------------------------------------------
defaultConfig = {
        # personality of the fit
        'Personality': '2011Conf',
        # fit mode: cFit, cFitWithWeights, sFit
        'FitMode': 'cFit',
        # modes to fit for
        'Modes': [
            'Bs2DsK',
            'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst',
            'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bs2DsstRho',
            'Bd2DK', 'Bd2DsK',
            'Lb2LcK', 'Lb2Dsp', 'Lb2Dsstp',
            'CombBkg'
            ],
        # declare sample categories we'll use
        'SampleCategories': [
            'up_kkpi', 'up_kpipi', 'up_pipipi',
            'down_kkpi', 'down_kpipi', 'down_pipipi'
            ],
        # fit ranges in various observables
        'FitRanges': {
            'time':     [0.2, 15.],
            'timeerr':  [1e-6, 0.25],
            'mistag':   [0., 0.5],
            'mass':     [5320., 5420.],
            'dsmass':   [1930., 2015.],
            'pidk':     [0., 150.]
            },
        # combine CP observables for these modes into effective CP obs.
        'CombineModesForEffCPObs': [
            # you may want to combine these during fitting
            'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst'
            ],
        # fit DsK CP observables in which mode:
        # 'CDS' 		- C, D, Dbar, S, Sbar
        # 'CDSConstrained'	- same as CDS, but constrain C^2+D^2+S^2 = 1
        #			  (same for bar)
        # 'CADDADS'		- C, <D>, Delta D, <S>, Delta S
        #			  (<D>=(D+Dbar)/2, Delta D=(D-Dbar)/2 etc.)
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
            'Bs2DsstKst': 	20. / 180. * pi,
            'Bd2DPi':           20. / 180. * pi,
            },
        'WeakPhase': {
                'Bs2DsK':	50. / 180. * pi,
                'Bs2DsstK':	50. / 180. * pi,
                'Bs2DsKst':	50. / 180. * pi,
                'Bs2DsstKst':	50. / 180. * pi,
                'Bd2DPi':       50. / 180. * pi,
                },
        'ModLf': {
                'Bs2DsK': 	0.372,
                'Bs2DsstK': 	0.470,
                'Bs2DsKst': 	0.372,
                'Bs2DsstKst': 	0.470,
                'Bd2DPi':       0.0187
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
    # first entry is for true B (and true Bbar, if no second entry exists)
    'MistagCalibrationParams':	[
            # [ p0, p1, <eta> ]
            [ 0.392, 1.035, 0.391 ], # true B
            #[ 0.392, 1.035, 0.391 ]  # true Bbar
            ], 

    # truth/Gaussian/DoubleGaussian/GaussianWithPEDTE/GaussianWithLandauPEDTE/GaussianWithScaleAndPEDTE
    'DecayTimeResolutionModel':         'TripleGaussian',
    'DecayTimeResolutionBias':          0.,
    'DecayTimeResolutionScaleFactor':   1.15,
    # None/BdPTAcceptance/DTAcceptanceLHCbNote2007041,PowLawAcceptance
    'AcceptanceFunction':		'PowLawAcceptance',
    'AcceptanceCorrectionFile':         os.environ['B2DXFITTERSROOT']+'/data/acceptance-ratio-hists.root',
    'AcceptanceCorrectionHistName':	'haccratio_cpowerlaw',
    'AcceptanceCorrectionInterpolation': False,
    # acceptance can really be made a histogram/spline interpolation
    'StaticAcceptance':		False,
    'AcceptanceInterpolation':	False,
    # acceptance parameters BdPTAcceptance
    'BdPTAcceptance_slope':	1.09,
    'BdPTAcceptance_offset':	0.187,
    'BdPTAcceptance_beta':	0.039,
    # acceptance parameters PowLawAcceptance
    'PowLawAcceptance_turnon':	1.215,
    'PowLawAcceptance_offset':	0.0373,
    'PowLawAcceptance_expo':	1.849,
    'PowLawAcceptance_beta':	0.0363,

    'PerEventMistag': 		True,

    # divide mistag into categories?
    #
    # number of categories
    'NMistagCategories':        None,
    # sorted list of category boundaries, e.g [ 0., 0.1, 0.2, 0.4, 0.5 ]
    'MistagCategoryBinBounds':  None,
    # starting values for per-category mistags
    'MistagCategoryOmegas':     None,
    # per category tagging efficiencies (N_cat_i / N_(tagged + untagged)
    'MistagCategoryTagEffs':    None,
    # parameter range if per-cat. omegas are floated
    'MistagCategoryOmegaRange': [ 0., 0.5 ],

    'TrivialMistag':		False,

    'UseKFactor':		False,

    # fitter settings
    'Optimize':			2,
    'Strategy':			2,
    'Offset':			True,
    'Minimizer':		[ 'Minuit', 'migrad' ],
    'NumCPU':			1,
    'ParameteriseIntegral':     True,
    'Debug':			False,

    # list of constant parameters
    'constParams': [
            'Gammas', 'deltaGammas', 'deltaMs',
            'Gammad', 'deltaGammad', 'deltaMd',
            'mistag', 'timeerr_bias', 'timeerr_scalefactor',
            'MistagCalibB_p0', 'MistagCalibB_p1', 'MistagCalibB_avgmistag',
            'MistagCalibBbar_p0', 'MistagCalibBbar_p1', 'MistagCalibBbar_avgmistag',
            ],

    # mass templates
    'MassTemplateFile':		os.environ['B2DXFITTERSROOT']+'/data/workspace/WS_Mass_DsK.root',
    'MassTemplateWorkspace':	'FitMeToolWS',
    'MassInterpolation':	False,
    # either one element or 6 (kkpi,kpipi,pipipi)x(up,down) in "sample" order
    'NEvents':			[ 1731. ],
    # target S/B: None means keep default
    'S/B': None,
    # mistag template
    'MistagTemplateFile':	os.environ['B2DXFITTERSROOT']+'/data/workspace/work_toys_dsk.root',
    'MistagTemplateWorkspace':	'workspace',
    'MistagTemplateName':	'PhysBkgBsDsPiPdf_m_down_kkpi_mistag',
    'MistagVarName':		'lab0_BsTaggingTool_TAGOMEGA_OS',
    'MistagInterpolation':	False,
    # decay time error template
    'DecayTimeErrorTemplateFile':       None,
    'DecayTimeErrorTemplateWorkspace':  None,
    'DecayTimeErrorTemplateName':       None,
    'DecayTimeErrorVarName':            None,
    'DecayTimeErrInterpolation':	False,

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
    'NBinsAcceptance':		300, # if >0, bin acceptance
    'NBinsTimeKFactor':		50,  # if >0, use binned cache for k-factor integ.
    'NBinsMistag':		50,  # if >0, parametrize Mistag integral
    'NBinsProperTimeErr':	100, # if >0, parametrize proper time int.
    'NBinsMass':		200, # if >0, bin mass templates

    # Data file settings
    'IsToy':			True,
    'DataFileName':		None,
    'DataWorkSpaceName':	'workspace',
    'DataSetNames':		{
            'up_kkpi':          'dataSetBsDsK_up_kkpi',
            'up_kpipi':         'dataSetBsDsK_up_kpipi',
            'up_pipipi':        'dataSetBsDsK_up_pipipi',
            'down_kkpi':	'dataSetBsDsK_down_kkpi',
            'down_kpipi':	'dataSetBsDsK_down_kpipi',
            'down_pipipi':	'dataSetBsDsK_down_pipipi'
            },
    # variable name mapping: our name -> name in dataset
    'DataSetVarNameMapping': {
            'sample':   'sample',
            'mass':     'lab0_MassFitConsD_M',
            'pidk':     'lab1_PIDK',
            'dsmass':   'lab2_MM',
            'time':     'lab0_LifetimeFit_ctau',
            'timeerr':  'lab0_LifetimeFit_ctauErr',
            'mistag':   'lab0_BsTaggingTool_TAGOMEGA_OS',
            'qf':       'lab1_ID',
            'qt':       'lab0_BsTaggingTool_TAGDECISION_OS',
            'weight':   'nSig_both_nonres_Evts_sw+nSig_both_phipi_Evts_sw+nSig_both_kstk_Evts_sw+nSig_both_kpipi_Evts_sw+nSig_both_pipipi_Evts_sw'
            },
    # write data set to file name
    'WriteDataSetFileName': None,
    'WriteDataSetTreeName': 'data',
    'QuitAfterGeneration': False,
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
            'RooFitTopSimultaneousWorkaround',
            # this will work around a problem in present RooFit versions which
            # produce different LH values if the top-level PDF is a
            # RooSimultaneous
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
    print '%3s %-24s %12s %12s %12s' % (
        'PAR', 'NAME', 'INI. VALUE', 'FIT VALUE', 'ERROR' )
    print ''
    i = 0
    for var in sorted(fv.keys()):
        cmt = ''
        if fbl[var] >= fv[var] or fbu[var] <= fv[var]:
            cmt = '*** AT LIMIT ***'
        val = '% 12.5g' % fv[var]
        if blind and 'Bs2DsK' in var:
            val = 'XXXX.XXX'
        print '% 3u %-24s % 12.5g %12s %12.5g %s' % (
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
    from ROOT import RooAbsArg, RooRealVar
    if obj.InheritsFrom(RooRealVar.Class()):
        # set desired RooRealVar-derived objects to const
        if obj.GetName() in config['constParams']:
            obj.setConstant(True)
    elif obj.InheritsFrom(RooAbsArg.Class()):
        # for everything else, descend hierarchy of RooFit objects to find
        # RooRealVars which might need to be set to constant
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
        # ignore everything else
        pass

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
    elif obj.InheritsFrom('RooArgSet'):
        if None == wsobj:
            ws.defineSet(name, obj, True)
            wsobj = ws.set(name)
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
    config,             # configuration dictionary
    ws,                 # workspace to which to add data set
    observables,        # observables
    rangeName = None	# name of range to clip dataset to
    ):
    from ROOT import ( TFile, RooWorkspace, RooRealVar, RooCategory,
        RooBinningCategory, RooUniformBinning, RooMappedCategory,
        RooDataSet, RooArgSet, RooArgList )
    import sys, math
    # local little helper routine
    def round_to_even(x):
        xfl = int(math.floor(x))
        rem = x - xfl
        if rem < 0.5: return xfl
        elif rem > 0.5: return xfl + 1
        else:
            if xfl % 2: return xfl + 1
            else: return xfl
    # another small helper routine
    def tokenize(s, delims = '+-*/()?:'):
        # FIXME: this goes wrong for numerical constants like 1.4e-3
        # proposed solution: regexp for general floating point constants,
        # replace occurences of matches with empty string
        delims = [ c for c in delims ]
        delims.insert(0, None)
        for delim in delims:
            tmp = s.split(delim)
            tmp = list(set(( s + ' ' for s in tmp)))
            s = ''.join(tmp)
        tmp = list(set(s.split(None)))
        return tmp
    # figure out which names from the mapping we need - look at the observables
    names = ()
    for n in config['DataSetVarNameMapping'].keys():
        if None != observables.find(n):
            names += (n,)
    # build RooArgSets and maps with source and destination variables
    dmap = { }
    for k in names: dmap[k] = observables.find(k)
    if None in dmap.values():
        raise NameError('Some variables not found in destination: %s' % str(dmap))
    dset = RooArgSet()
    for v in dmap.values(): dset.add(v)
    if None != dset.find('weight'):
        # RooFit insists on weight variable being first in set
        tmpset = RooArgSet()
        tmpset.add(dset.find('weight'))
        it = dset.fwdIterator()
        while True:
            obj = it.next()
            if None == obj: break
            if 'weight' == obj.GetName(): continue
            tmpset.add(obj)
        dset = tmpset
        del tmpset
        ddata = RooDataSet('agglomeration', 'of positronic circuits', dset, 'weight')
    else:
        ddata = RooDataSet('agglomeration', 'of positronic circuits', dset)
    # open file with data sets
    f = TFile(config['DataFileName'], 'READ')
    # get workspace
    fws = f.Get(config['DataWorkSpaceName'])
    ROOT.SetOwnership(fws, True)
    if None == fws or not fws.InheritsFrom('RooWorkspace'):
        # ok, no workspace, so try to read a tree of the same name and
        # synthesize a workspace
        from ROOT import RooWorkspace, RooDataSet, RooArgList
        fws = RooWorkspace(config['DataWorkSpaceName'])
        iset = RooArgSet()
        addiset = RooArgList()
        it = observables.fwdIterator()
        while True:
            obj = it.next()
            if None == obj: break
            name = config['DataSetVarNameMapping'][obj.GetName()]
            vnames = tokenize(name)
            if len(vnames) > 1 and not obj.InheritsFrom('RooAbsReal'):
                print 'Error: Formulae not supported for categories'
                return None
            if obj.InheritsFrom('RooAbsReal'):
                if 1 == len(vnames):
                    # simple case, just add variable
                    var = WS(fws, RooRealVar(name, name, -sys.float_info.max,
                        sys.float_info.max))
                    iset.addClone(var)
                else:
                    # complicated case - add a bunch of observables, and
                    # compute something in a RooFormulaVar
                    from ROOT import RooFormulaVar
                    args = RooArgList()
                    for n in vnames:
                        try:
                            # skip simple numerical factors
                            float(n)
                        except:
                            var = iset.find(n)
                            if None == var:
                                var = WS(fws, RooRealVar(n, n, -sys.float_info.max,
                                    sys.float_info.max))
                                iset.addClone(var)
                                args.add(iset.find(n))
                    var = WS(fws, RooFormulaVar(name, name, name, args))
                    addiset.addClone(var)
            else:
                for dsname in ((config['DataSetNames'], )
                        if type(config['DataSetNames']) == str else
                        config['DataSetNames']):
                    break
                leaf = f.Get(dsname).GetLeaf(name)
                if None == leaf:
                    leaf = f.Get(dsname).GetLeaf(name + '_idx')
                if leaf.GetTypeName() in (
                        'char', 'unsigned char', 'Char_t', 'UChar_t',
                        'short', 'unsigned short', 'Short_t', 'UShort_t',
                        'int', 'unsigned', 'unsigned int', 'Int_t', 'UInt_t',
                        'long', 'unsigned long', 'Long_t', 'ULong_t',
                        'Long64_t', 'ULong64_t', 'long long',
                        'unsigned long long'):
                    var = WS(fws, RooCategory(name, name))
                    tit = obj.typeIterator()
                    ROOT.SetOwnership(tit, True)
                    while True:
                        tobj = tit.Next()
                        if None == tobj: break
                        var.defineType(tobj.GetName(), tobj.getVal())
                else:
                    var = WS(fws, RooRealVar(name, name, -sys.float_info.max,
                        sys.float_info.max))
                iset.addClone(var)
        for dsname in ((config['DataSetNames'], )
               if type(config['DataSetNames']) == str else
               config['DataSetNames']):
            tmpds = WS(fws, RooDataSet(dsname, dsname,f.Get(dsname), iset), [])
            if 0 != addiset.getSize():
                # need to add columns with RooFormulaVars
                tmpds.addColumns(addiset)
            del tmpds
    # local data conversion routine
    def doIt(config, rangeName, dsname, sname, names, dmap, dset, ddata, fws):
        sdata = fws.obj(dsname)
        if None == sdata: return 0
        sset = sdata.get()
        smap = { }
        for k in names:
            smap[k] = sset.find(config['DataSetVarNameMapping'][k])
        if 'sample' in smap.keys() and None == smap['sample'] and None != sname:
            smap.pop('sample')
            dmap['sample'].setLabel(sname)
        if None in smap.values():
            raise NameError('Some variables not found in source: %s' % str(smap))
        # additional complication: toys save decay time in ps, data is in nm
        # figure out which time conversion factor to use
        timeConvFactor = 1e9 / 2.99792458e8
        meantime = sdata.mean(smap['time'])
        if (dmap['time'].getMin() <= meantime and
                meantime <= dmap['time'].getMax() and config['IsToy']):
            timeConvFactor = 1.
        # loop over all entries of data set
        ninwindow = 0
        if None != sname:
            sys.stdout.write('Dataset conversion and fixup: %s: progress: ' % sname)
        else:
            sys.stdout.write('Dataset conversion and fixup: progress: ')
        for i in xrange(0, sdata.numEntries()):
            sdata.get(i)
            if 0 == i % 128:
                sys.stdout.write('*')
            vals = { }
            for vname in smap.keys():
                obj = smap[vname]
                if obj.InheritsFrom('RooAbsReal'):
                    val = obj.getVal()
                    vals[vname] = val
                else:
                    val = obj.getIndex()
                    vals[vname] = val
            # first fixup: apply time/timeerr conversion factor
            if 'time' in dmap.keys():
                vals['time'] *= timeConvFactor
            if 'timeerr' in dmap.keys():
                vals['timeerr'] *= timeConvFactor
            # second fixup: only sign of qf is important
            if 'qf' in dmap.keys():
                vals['qf'] = 1 if vals['qf'] > 0.5 else (-1 if vals['qf'] <
                        -0.5 else 0.)
            # third fixup: untagged events are forced to 0.5 mistag
            if ('qt' in dmap.keys() and 'mistag' in dmap.keys() and 0 ==
                    vals['qt']):
                vals['mistag'] = 0.5
            # apply cuts
            inrange = True
            for vname in dmap.keys():
                if not dmap[vname].InheritsFrom('RooAbsReal'): continue
                # no need to cut on untagged events
                if 'mistag' == vname and 0 == vals['qt']: continue
                if None != rangeName and dmap[vname].hasRange(rangeName):
                    if (dmap[vname].getMin(rangeName) > vals[vname] or
                            vals[vname] >= dmap[vname].getMax(rangeName)):
                        inrange = False
                        break
                else:
                    if (dmap[vname].getMin() > vals[vname] or
                            vals[vname] >= dmap[vname].getMax()):
                        inrange = False
                        break
            # skip cuts which are not within the allowed range
            if not inrange: continue
            # copy values over, doing real-category conversions as needed
            for vname in smap.keys():
                dvar, svar = dmap[vname], vals[vname]
                if dvar.InheritsFrom('RooAbsRealLValue'):
                    if float == type(svar): dvar.setVal(svar)
                    elif int == type(svar): dvar.setVal(svar)
                elif dvar.InheritsFrom('RooAbsCategoryLValue'):
                    if int == type(svar): dvar.setIndex(svar)
                    elif float == type(svar):
                        dvar.setIndex(round_to_even(svar))
            if 'weight' in dmap:
                ddata.add(dset, vals['weight'])
            else:
                ddata.add(dset)
            ninwindow = ninwindow + 1
        del sdata
        sys.stdout.write(', done - %d events\n' % ninwindow)
        return ninwindow
    ninwindow = 0
    if type(config['DataSetNames']) == str:
        ninwindow += doIt(config, rangeName, config['DataSetNames'],
                None, names, dmap, dset, ddata, fws)
    else:
        for sname in config['DataSetNames'].keys():
            ninwindow += doIt(config, rangeName, config['DataSetNames'][sname],
                    sname, names, dmap, dset, ddata, fws)
    # free workspace and close file
    del fws
    f.Close()
    del f
    # put the new dataset into our proper workspace
    ddata = WS(ws, ddata, [])
    # for debugging
    if config['Debug']:
        ddata.Print('v')
        if 'qt' in dmap.keys():
            data.table(dmap['qt']).Print('v')
        if 'qf' in dmap.keys():
            data.table(dmap['qf']).Print('v')
        if 'qf' in dmap.keys() and 'qt' in dmap.keys():
            data.table(RooArgSet(dmap['qt'], dmap['qf'])).Print('v')
        if 'sample' in dmap.keys():
            data.table(dmap['sample']).Print('v')
    # all done, return Data to the bridge
    return ddata

def writeDataSet(dataset, filename, treename, bnamemap = {}):
    from ROOT import TFile, TTree
    import array
    f = TFile(filename, 'RECREATE')
    t = TTree(treename, treename)
    obs = dataset.get()
    # create branches
    branches = { }
    it = obs.fwdIterator()
    while True:
        obj = it.next()
        if None == obj: break
        bname = (bnamemap[obj.GetName()] if obj.GetName() in bnamemap else
                obj.GetName())
        branches[obj.GetName()] = (array.array('d', [0.]) if
                obj.InheritsFrom('RooAbsReal') else array.array('i', [0]))
        t.Branch(bname, branches[obj.GetName()], bname+('/D' if
            obj.InheritsFrom('RooAbsReal') else '/I'))
    # fill tuple
    for i in xrange(0, dataset.numEntries()):
        dataset.get(i)
        it = obs.fwdIterator()
        while True:
            obj = it.next()
            if None == obj: break
            branches[obj.GetName()][0] = (obj.getVal() if
                    obj.InheritsFrom('RooAbsReal') else obj.getIndex())
        t.Fill()
    t.Write()
    del t
    f.Close()
    del f

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
    variable.setBins(hist.GetNbinsX())
    ROOT.SetOwnership(hist, True)
    hist.SetNameTitle('%sPdf_hist' % pfx, '%sPdf_hist' % pfx)
    hist.SetDirectory(None)
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

# read mistag distribution from file
def getMistagTemplate(
    config,	# configuration dictionary
    ws, 	# workspace to import into
    mistag	# mistag variable
    ):
    return readTemplate1D(config['MistagTemplateFile'],
            config['MistagTemplateWorkspace'], config['MistagVarName'],
            config['MistagTemplateName'], ws, mistag, 'sigMistag')

# read decay time error distribution from file
def getDecayTimeErrorTemplate(
    config,	# configuration dictionary
    ws, 	# workspace to import into
    timeerr	# timeerr variable
    ):
    return readTemplate1D(config['DecayTimeErrorTemplateFile'],
            config['DecayTimeErrorTemplateWorkspace'],
            config['DecayTimeErrorVarName'],
            config['DecayTimeErrorTemplateName'], ws, timeerr, 'sigTimeErr')

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
        for s in config['SampleCategories']:
            thismode[s] = workspace.data('kfactor_dataset_%s_%s' % (n, s))
        for s in config['SampleCategories']:
            p = s.split('_')[0]
            op = 'down' if 'up' == p else 'up'
            os = '%s_%s' % (os, s.split('_')[1])
            if None != thismode[s] and None != thismode[os] and \
                    thismode[s] != thismode[os]:
                # merge up and down polarities if we have both
                thismode[s].append(thismode[os])
                thismode[s].SetName('kfactordata_merged_%s' % n)
                thismode[os] = thismode[s]
            elif None != thismode[s] and None == thismode[os]:
                # duplicate other polarity
                thismode[os] = thismode[s];
            elif None == thismode[s] and None == thismode[os]:
                print '@@@ - Error: no k factor template for mode %s' % n
        for s in config['SampleCategories']:
            # add all the samples for this mode
            dslist[n] = thismode[s]
        del thismode
        # clean up modes
        if n in dslist and None == dslist[n]:
            del dslist[n]
        elif n in dslist and None != dslist[n]:
            if dslist[n].numEntries() <= 0.:
                del dslist[n]
    allpdfs = { }
    for mode in dslist:
        ds = dslist[mode]
        if 0 >= ds.numEntries():
            print '@@@ - WARNING: Empty k factor template for mode %s' % mode
            continue
        name = ds.GetName()
        kmin = ROOT.Double(0.)
        kmax = ROOT.Double(0.)
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
                    [RooFit.RenameVariable(fromvarname, k.GetName()),
                        RooFit.Silence()])
            del dhist
        else:
            pdf = RooKeysPdf(name, name, var, ds)
            allpdfs[mode]['pdf'] = WS(ws, pdf,
                    [RooFit.RenameVariable(fromvarname, k.GetName()),
                        RooFit.Silence()])
        allpdfs[mode]['range'] = [kmin, kmax]
        del pdf
        del ds
        # should be one pdf per mode
    del dslist
    return allpdfs

# obtain mass template from mass fitter (2011 CONF note version)
#
# we use the very useful workspace dump produced by the mass fitter to obtain
# the pdf and yields
#
# returns a dictionary with a pair { 'pdf': pdf, 'yield': yield }
def getMassTemplateOneMode2011Conf(
    config,	        # configuration dictionary
    ws,                 # workspace into which to import templates
    mass,	        # mass variable
    mode,	        # decay mode to load
    sname,              # sample name
    dsmass = None,      # ds mass variable
    pidk = None	        # pidk variable
    ):
    fromfile = config['MassTemplateFile']
    fromwsname = config['MassTemplateWorkspace']
    from ROOT import ( TFile, RooWorkspace, RooAbsPdf, RooAbsCategory,
        RooRealVar, RooArgSet, RooDataHist, RooHistPdf, RooArgList )
    import re

    # validate input (and break caller if invalid)
    if sname not in config['SampleCategories']: return None

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
        pdf = fromws.pdf('DblCBPDF%s' % sname)
    elif mode == 'CombBkg':
        pdf = fromws.pdf('CombBkgPDF_m_%s' % sname)
    else:
        # any other mode may or may not have separate samples for
        # magnet polarity, Ds decay mode, ...
        #
        # we therefore constuct a list of successively less specialised name
        # suffices so we can get the most specific pdf from the workspace
        trysfx = [
            '%sPdf_m_%s' % (mode, sname),
            '%sPdf_m_%s' % (mode.replace('2', ''), sname),
            '%s_m_%s' % (mode, sname),
            '%s_m_%s' % (mode.replace('2', ''), sname),
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
            if None == obj: break
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
        oldmass.setRange('signalRegion', mass.getMin(), mass.getMax())
        iset = nset = RooArgSet(oldmass)
        integral = pdf.createIntegral(iset, nset, 'signalRegion')
        ROOT.SetOwnership(integral, True)
        yieldrangescaling = integral.getVal()
        # ok, figure out yield
        nYield = None
        if mode == 'Bs2DsK':
            nYield = RooRealVar('nSig_%s_Evts' % sname,
                    'nSig_%s_Evts' % sname,
                    fromws.var('nSig_%s_Evts' % sname).getVal() *
                    yieldrangescaling)
        elif mode == 'CombBkg':
            nYield = RooRealVar('nCombBkg_%s_Evts' % sname,
                    'nCombBkg_%s_Evts' % sname,
                    fromws.var('nCombBkg_%s_Evts' % sname).getVal() *
                    yieldrangescaling)
        else:
            # yield for other modes are either simple and we deal with them here,
            # or we deal with them below
           nYield = fromws.var('n%s_%s_Evts' % (mode, sname))
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
                        'up_kkpi': 14., 'up_kpipi': 2., 
                        'down_kkpi': 23., 'down_kpipi': 3.
                        },
                    'Lb2LcK': {
                        'up_kkpi': 4.1088*100./15.,
                        'down_kkpi': 6.7224*100./15.
                        },
                    'Lb2Dsp': {
                        'up_kkpi': 0.5 * 46., 'up_kpipi': 0.5 * 5., 'up_pipipi': 0.5 * 10., 
                        'down_kkpi': 0.5 * 78., 'down_kpipi': 0.5 * 8., 'down_pipipi': 0.5 * 16.
                        },
                    'Lb2Dsstp': {
                        'up_kkpi': 0.5 * 46., 'up_kpipi': 0.5 * 5., 'up_pipipi': 0.5 * 10.,
                        'down_kkpi': 0.5 * 78., 'down_kpipi': 0.5 * 8., 'down_pipipi': 0.5 * 16.
                        }
                    }
            if (mode in fixedmodes and sname in fixedmodes[mode]):
                # it's a fixed yield mode, so set yield
                y = fixedmodes[mode][sname]
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
                        'nBs2DsDssKKst_%s_Evts' % sname).getVal()
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
                        'nBs2DsDsstPiRho_%s_Evts' % sname).getVal()
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
                print '@@@@ - ERROR: NO YIELD FOR MODE %s SAMPLE NAME %s' % (
                        mode, sname)
                nYield = None
            else:
                nYield = RooRealVar('n%s_%s_Evts' % (mode, sname),
                        'n%s_%s_Evts' % (mode, sname),
                        y * yieldrangescaling)
    # ok, we should have all we need for now
    if None == pdf or None == nYield:
        print '@@@@ - ERROR: NO PDF FOR MODE %s SAMPLE CATEGORY %s' % (
                mode, sname)
        return None
    # import mass pdf and corresponding yield into our workspace
    # in the way, we rename whatever mass variable was used to the one supplied
    # by our caller
    nYield = WS(ws, nYield, [
        RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
        RooFit.Silence()])

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
                RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                RooFit.Silence()])
        else:
            pdf = WS(ws, pdf, [
                RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                RooFit.Silence()])
        if config['NBinsMass'] > 0 and not config['MassInterpolation']:
            obins = mass.getBins()
            mass.setBins(config['NBinsMass'])
            hist = pdf.createHistogram('%s_hist' % pdf.GetName(), mass)
            ROOT.SetOwnership(hist, True)
            dhist = WS(ws, RooDataHist(
                '%s_dhist' % pdf.GetName(), '%s_dhist' % pdf.GetName(),
                RooArgList(mass), hist), [])
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

# obtain mass template from mass fitter (2011 PAPER version)
#
# we use the very useful workspace dump produced by the mass fitter to obtain
# the pdf and yields
#
# returns a dictionary with a pair { 'pdf': pdf, 'yield': yield }
def getMassTemplateOneMode2011Paper(
    config,	        # configuration dictionary
    ws,                 # workspace into which to import templates
    mass,	        # mass variable
    mode,	        # decay mode to load
    sname,              # sample name
    dsmass = None,      # ds mass variable
    pidk = None	        # pidk variable
    ):
    fromfile = config['MassTemplateFile']
    fromwsname = config['MassTemplateWorkspace']
    from ROOT import ( TFile, RooWorkspace, RooAbsPdf, RooAbsCategory,
        RooRealVar, RooArgSet, RooDataHist, RooHistPdf, RooArgList )
    import re

    # validate input (and break caller if invalid)
    if sname not in config['SampleCategories']: return None

    # open file and read in workspace
    fromfile = TFile(fromfile, 'READ')
    if fromfile.IsZombie():
        return None
    fromws = fromfile.Get(fromwsname)
    if None == fromws:
        return None
    ROOT.SetOwnership(fromws, True)

    # ok, depending on mode, we try to load a suitable pdf
    pdf, nYield = None, None
    if mode == config['Modes'][0]:
        pdf = fromws.pdf('SigProdPDF_both_%s' % sname)
        nYield = fromws.var('nSig_both_%s_Evts' % sname)
        if None != nYield: nYield = nYield.getVal()
    elif mode == 'CombBkg':
        pdf = fromws.pdf('CombBkgPDF_m_both_%s_Tot' % sname)
        nYield = fromws.var('nCombBkg_both_%s_Evts' % sname)
        if None != nYield: nYield = nYield.getVal()
    else:
        # any other mode may or may not have separate samples for
        # magnet polarity, Ds decay mode, ...
        #
        # we therefore constuct a list of successively less specialised name
        # suffices so we can get the most specific pdf from the workspace
        modemap = {
                'Bs2DsKst': 'Bs2DsDsstKKst',
                'Bd2DsK': 'Bs2DsDsstKKst',
                'Bs2DsstPi': ('BsLb2DsDsstPPiRho' if
                    'Bs2DsK' == config['Modes'][0] else 'Bs2DsDsstPi'),
                'Bs2DsRho': ('Bs2DsDsstPiRho' if
                    'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                'Bs2DsstRho': 'Bs2DsDsstPiRho',
                'Lb2Dsp': ('Lb2DsDsstP' if
                    'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                'Lb2Dsstp': ('Lb2DsDsstP' if
                    'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                'Bs2DsPi': 'Bs2DsPi',
                'Lb2LcK': 'Lb2DsK',
                'Lb2LcPi': 'Lb2DsPi',
                'Bd2DK': 'Bd2DK',
                'Bd2DPi': 'Bd2DPi',
                'Bd2DsPi': ('Bs2DsDsstPi' if
                    'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                'Bs2DsPi': ('Bs2DsPi' if
                    'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                'Bs2DsK': 'Bs2DsK'
                }
        trysfx = [
            '%sPdf_m_both_%s_Tot' % (mode, sname),
            '%sPdf_m_both_Tot' % mode,
            '%sPdf_m_both_%s_Tot' % (modemap[mode], sname),
            '%sPdf_m_both_Tot' % modemap[mode],
            # "modeless" names for single-mode DsPi toys (only in DsK, I
            # think, but we need the fallback solution at least once)
            '%sPdf_m_both_%s_Tot' % (mode, ''),
            '%sPdf_m_both_%s_Tot' % (modemap[mode], ''),
            ]
        for sfx in trysfx:
            pdf = fromws.pdf('PhysBkg%s' % sfx)
            if None != pdf:
                break
        tryyieldsfx = [
            'n%s_both_%s_Evts' % (mode, sname),
            'n%s_both_%s_Evts' % (mode.replace('Dsst', 'Dss'), sname),
            'n%s_both_%s_Evts' % (mode.replace('DsstP', 'Dsstp'), sname),
            'n%s_both_%s_Evts' % (mode.replace('DsstPi', 'DsstPiRho'), sname),
            'n%s_both_%s_Evts' % (modemap[mode], sname),
            'n%s_both_%s_Evts' % (modemap[mode].replace('Dsst', 'Dss'), sname),
            'n%s_both_%s_Evts' % (modemap[mode].replace('DsstP', 'Dsstp'), sname),
            'n%s_both_%s_Evts' % (modemap[mode].replace('DsstPi', 'DsstPiRho'), sname),
            ]
        for sfx in tryyieldsfx:
            nYield = fromws.var(sfx)
            if None != nYield:
                nYield = nYield.getVal()
                break
        if tryyieldsfx[0] != sfx and tryyieldsfx[1] != sfx:
            # ok, we're in one of the modes which have a shared yield and a
            # fraction, so get the fraction, and fix up the yield 
            if 'Bs2DsDsstKKst' in sfx or 'Bs2DsDssKKst' in sfx:
                f = fromws.var('g1_f1_frac')
                if 'Bd2DsK' == mode:
                    f = f.getVal()
                elif 'Bs2DsKst' == mode:
                    f = 1. - f.getVal()
                else:
                    f = None
            elif ('BsLb2DsDsstPPiRho' in sfx and 'Bs2DsK' == config['Modes'][0]
                    and 'Bs2Ds' in mode):
                f = fromws.var('g2_f2_frac')
                if 'Bs2DsstPi' == mode:
                    f = f.getVal()
                elif 'Bs2DsRho' == mode:
                    f = 1. - f.getVal()
                elif 'Bs2DsPi' == mode:
                    f = fromws.var('g2_f1_frac').getVal()
                else:
                    f = None
                if None != f and 'Bs2DsPi' != mode:
                    f *= (1. - fromws.var('g2_f1_frac').getVal())
                if None != f:
                    f *= fromws.var('g5_f1_frac').getVal()
            elif ('Lb2DsDsstP' in sfx or 'Lb2DsDsstp' in sfx or
                    ('Lb2Ds' in mode and 'BsLb2DsDsstPPiRho' in sfx)):
                f = fromws.var('g3_f1_frac')
                if 'Lb2Dsp' == mode:
                    f = f.getVal()
                elif 'Lb2Dsstp' == mode:
                    f = 1. - f.getVal()
                else:
                    f = None
                if None != f and 'Bs2DsK' == config['Modes'][0]:
                    f *= (1. - fromws.var('g5_f1_frac').getVal())
            elif 'Bs2DsDsstPiRho' in sfx and 'Bs2DsPi' == config['Modes'][0]:
                f = fromws.var('g1_f1_frac')
                if 'Bs2DsstPi' == mode:
                    f = f.getVal()
                elif 'Bd2DsPi' == mode:
                    f = 1. - f.getVal()
                else:
                    f = None
            else:
                print 'ERROR: Don\'t know how to fix mode %s/%s' % (sfx, mode)
                return None
            # ok, fix the yield with the right fraction
            nYield = nYield * f
    # ok, we should have all we need for now
    if None == pdf or None == nYield:
        if None == pdf:
            print '@@@@ - ERROR: NO PDF FOR MODE %s SAMPLE CATEGORY %s' % (
                    mode, sname)
        if None == nYield:
            print '@@@@ - ERROR: NO YIELD FOR MODE %s SAMPLE CATEGORY %s' % (
                    mode, sname)
        return None
    # figure out name of mass variable - should start with 'lab0' and end in
    # '_M'; while we're at it, figure out how we need to scale yields due to
    # potentially different mass ranges
    massname, dsmassname, pidkname = None, None, None
    yieldrangescaling = 1.
    if None != pdf:
        pdfvars = []
        varset = pdf.getVariables()
        ROOT.SetOwnership(varset, True)
        it = varset.createIterator()
        ROOT.SetOwnership(it, True)
        while True:
            obj = it.Next()
            if None == obj: break
            pdfvars.append(obj)
            pdfvarnames = [ v.GetName() for v in pdfvars ]
            regex = re.compile('^lab0.*_M$')
            regex1 = re.compile('^lab2.*_M*$')
            regex2 = re.compile('^lab1.*_PIDK$')
            for n in pdfvarnames:
                if regex.match(n):
                    oldmass = varset.find(n)
                    massname = n
                if regex1.match(n):
                    olddsmass = varset.find(n)
                    dsmassname = n
                if regex2.match(n):
                    oldpidk = varset.find(n)
                    pidkname = n
            else:
                # set anything else constant
                varset.find(n).setConstant(True)
        # figure out yield scaling due to mass ranges
        oldmass.setRange('signalRegion', mass.getMin(), mass.getMax())
        iset = nset = RooArgSet(oldmass, olddsmass, oldpidk)
        integral = pdf.createIntegral(iset, nset, 'signalRegion')
        ROOT.SetOwnership(integral, True)
        yieldrangescaling = integral.getVal()
        # ok, figure out yield
        nYield = RooRealVar('n%s_%s_Evts' % (mode, sname),
                'n%s_%s_Evts' % (mode, sname), nYield * yieldrangescaling)
    # import mass pdf and corresponding yield into our workspace
    # in the way, we rename whatever mass variable was used to the one supplied
    # by our caller
    nYield = WS(ws, nYield, [
        RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
        RooFit.Silence()])

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
            fromnames = '%s,%s,%s' % (massname, dsmassname, pidkname)
            tonames = '%s,%s,%s' % (mass.GetName(), dsmass.GetName(),
                    pidk.GetName())
            if ROOT.gROOT.GetVersionInt() > 53405:
                pdf = WS(ws, pdf, [ RooFit.Silence(),
                    RooFit.RenameVariable(fromnames, tonames),
                    RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                    RooFit.Silence()])
            else:
                # work around RooFit's limitations in ROOT 5.34.05 and
                # earlier...
                tmpws = RooWorkspace()
                pdf = WS(tmpws, pdf, [ RooFit.Silence(),
                    RooFit.RenameVariable(fromnames, tonames)])
                pdf = WS(ws, pdf, [
                    RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                    RooFit.Silence()])
                del tmpws
        else:
            pdf = WS(ws, pdf, [
                RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                RooFit.Silence()])
        if config['NBinsMass'] > 0 and not config['MassInterpolation']:
            print 'WARNING: binned mass requested for %s/%s ' \
                'mass/dsmass/pidk shape - not implemented yet' % (mode, sname)
    # ok, all done, return
    if config['MassInterpolation']:
        print 'WARNING: interpolation requested for %s/%s mass/dsmass/pidk ' \
                'shape - not implemented yet' % (mode, sname)
    if None != nYield:
        nYield.setConstant(True)
    pdf = WS(ws, pdf)
    nYield = WS(ws, nYield)
    return { 'pdf': pdf, 'yield': nYield }

# read mass templates for specified modes
#
# returns dictionary d['mode']['polarity']['kkpi/kpipi/pipipi'] which contains
# a dictionary of pairs { 'pdf': pdf, 'yield': yield }
def getMassTemplates(
    config,		# configuration dictionary
    ws,			# wksp into which to import templates
    mass,		# mass variable
    dsmass = None,      # ds mass variable
    pidk = None,        # pidk variable
    snames = None       # sample names to read
    ):
    personalisedGetMassTemplateOneMode = {
            '2011Conf': getMassTemplateOneMode2011Conf,
            '2011ConfDATA': getMassTemplateOneMode2011Conf,
            '2011PaperDsK': getMassTemplateOneMode2011Paper,
            '2011PaperDsPi': getMassTemplateOneMode2011Paper,
            '2011PaperDsKDATA': getMassTemplateOneMode2011Paper,
            '2011PaperDsPiDATA': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn70': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn140': getMassTemplateOneMode2011Paper,
            '2011PaperDsPi-Agn70': getMassTemplateOneMode2011Paper,
            '2011PaperDsKDATA-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsPiDATA-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn70-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn140-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsPi-Agn70-sFit': getMassTemplateOneMode2011Paper,
            }
    import sys
    if None == snames:
        snames = config['SampleCategories']
    retVal = {}
    for mode in config['Modes']:
        for sname in snames:
            tmp = personalisedGetMassTemplateOneMode[ config['Personality'] ](
                    config, ws, mass, mode, sname, dsmass, pidk)
            if None == tmp:
                # break caller in case of error
                return None
            if mode not in retVal: retVal[mode] = {}
            retVal[mode][sname] = tmp
    sample = ws.obj('sample')
    totyield = 0.
    totyields = [ 0. for i in snames ]
    for sname in snames:
        for mode in config['Modes']:
            i = sample.lookupType('%s' % sname).getVal()
            totyield += retVal[mode][sname]['yield'].getVal()
            totyields[i] += retVal[mode][sname]['yield'].getVal()
    # scale the yields to the desired number of events
    for sname in snames:
        for mode in config['Modes']:
            i = sample.lookupType('%s' % sname).getVal()
            y = retVal[mode][sname]['yield']
            if len(config['SampleCategories']) == len(config['NEvents']):
                y.setVal(y.getVal() * (config['NEvents'][i] / totyields[i]))
            elif 1 == len(config['NEvents']):
                y.setVal(y.getVal() * (config['NEvents'][0] / totyield))
            else:
                print 'ERROR: invalid length of config[\'NEvents\']!'
                sys.exit(1)
            # make sure things stay constant
            y.setConstant(True)
    if None != config['S/B']:
        # allow users to hand-tune S/B (if desired)
        sigmode = config['Modes'][0]
        nsig, nbg = 0., 0.
        for sname in snames:
            for mode in config['Modes']:
                y = retVal[mode][sname]['yield']
                if sigmode == mode:
                    nsig += y.getVal()
                else:
                    nbg += y.getVal()
        sb = config['S/B']
        for sname in snames:
            for mode in config['Modes']:
                y = retVal[mode][pol][DsMode]['yield']
                if sigmode == mode:
                    y.setVal(sb / (1. + sb) * (nsig + nbg) * (
                        y.getVal() / nsig))
                else:
                    y.setVal(1. / (1. + sb) * (nsig + nbg) * (
                        y.getVal() / nbg))

    return retVal

# apply the acceptance to the time pdf (binned, i.e. apply to resolution model)
def applyBinnedAcceptance(config, ws, time, timeresmodel, acceptance):
    if None == acceptance or 0 >= config['NBinsAcceptance']:
        return timeresmodel
    from ROOT import RooArgSet, RooBinnedPdf, RooEffResModel
    # bin the acceptance if not already binned
    if not acceptance.isBinnedDistribution(RooArgSet(time)):
        acceptance = WS(ws, RooBinnedPdf(
            "%sBinnedAcceptance" % acceptance.GetName(),
            "%sBinnedAcceptance" % acceptance.GetName(),
            time, 'acceptanceBinning', acceptance))
        acceptance.setForceUnitIntegral(True)
    # create the acceptance-corrected resolution model
    return WS(ws, RooEffResModel(
        '%s_timeacc_%s' % (timeresmodel.GetName(), acceptance.GetName()),
        '%s plus time acceptance %s' % (timeresmodel.GetTitle(),
            acceptance.GetTitle()), timeresmodel, acceptance))

# apply the acceptance to the time pdf (unbinned)
def applyUnbinnedAcceptance(config, name, ws, pdf, acceptance):
    from ROOT import RooEffProd
    if None != acceptance and 0 >= config['NBinsAcceptance']:
        # do not bin acceptance
        return WS(ws, RooEffProd('%s_TimePdf' % name,
            '%s full time pdf' % name, pdf, acceptance))
    else:
        return pdf

# speed up the fit by parameterising integrals of the resolution model over
# time in the (per-event) time error (builds a table if integral values and
# interpolates)
def parameteriseResModelIntegrals(config, timeerrpdf, timeerr, timeresmodel):
    if None == timeerrpdf or 0 == config['NBinsProperTimeErr']:
        return
    from ROOT import RooArgSet
    if not timeerr.hasBinning('cache'):
        timeerr.setBins(config['NBinsProperTimeErr'], 'cache')
    timeresmodel.setParameterizeIntegral(RooArgSet(timeerr))

# apply the per-event time error pdf
def applyDecayTimeErrPdf(config, name, ws, time, timeerr, qt, qf, mistagobs,
        timepdf, timeerrpdf, mistagpdf):
    # no per-event time error is easy...
    if None == timeerrpdf: return timepdf
    from ROOT import RooArgSet, RooProdPdf
    noncondset = RooArgSet(time, qf, qt)
    if None != mistagpdf:
        noncondset.add(mistagobs)
    return WS(ws, RooProdPdf('%s_TimeTimeerrPdf' % name,
        '%s (time,timeerr) pdf' % name, RooArgSet(timeerrpdf),
        RooFit.Conditional(RooArgSet(timepdf), noncondset)))

# apply k-factor smearing
def applyKFactorSmearing(config, name, ws, time, timepdf, kvar, kfactorpdf, paramobs):
    if None == kfactorpdf or None == kvar:
        return timepdf
    # perform the actual k-factor smearing integral (if needed)
    from ROOT import ( RooGeneralisedSmearingBase, RooAbsPdf, RooConstVar,
            RooUniformBinning, RooArgSet )
    RooNumGenSmearPdf = RooGeneralisedSmearingBase(RooAbsPdf)
    retVal = WS(ws, RooNumGenSmearPdf('kSmeared_%s' % timepdf.GetName(),
        '%s smeared with k factor' % timepdf.GetTitle(),
        kvar, timepdf, kfactorpdf['pdf']))
    # since we fine-tune the range of the k-factor distributions, and we
    # know that the distributions are well-behaved, we can afford to be a
    # little sloppy
    retVal.convIntConfig().setEpsAbs(1e-4)
    retVal.convIntConfig().setEpsRel(1e-4)
    retVal.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('extrapolation','Wynn-Epsilon')
    retVal.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('sumRule','Trapezoid')
    retVal.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('minSteps', 3)
    retVal.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSteps', 16)
    retVal.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
    retVal.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    #retVal.convIntConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    retVal.convIntConfig().method1D().setLabel('RooIntegrator1D')
    retVal.convIntConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')	
    # set integration range
    center = WS(ws, RooConstVar(
        '%s_kFactorCenter' % name, '%s_kFactorCenter' % name,
        0.5 * (kfactorpdf['range'][0] + kfactorpdf['range'][1])))
    width = WS(ws, RooConstVar(
        '%s_kFactorWidth' % name, '%s_kFactorWidth' % name,
        0.5 * (kfactorpdf['range'][1] - kfactorpdf['range'][0])))
    retVal.setConvolutionWindow(center, width, 1.0)
    if 0 < config['NBinsTimeKFactor']:
        kfactortimebinning = WS(ws, RooUniformBinning(     
            time.getMin(), time.getMax(), config['NBinsTimeKFactor'],
            '%s_timeBinnedCache' % name))
        time.setBinning(kfactortimebinning, kfactortimebinning.GetName())
        retVal.setBinnedCache(time, kfactortimebinning.GetName(), paramobs)
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
    from ROOT import ( RooConstVar, RooProduct, RooTruthModel, RooGaussModel,
            Inverse, RooDecay, RooProdPdf, RooArgSet, NonOscTaggingPdf,
            RooArgList )

    if config['Debug']:
        print 72 * '#'
        kwargs = {
                'config': config,
                'name': name,
                'ws': ws,
                'time': time,
                'timeerr': timeerr,
                'qt': qt,
                'qf': qf,
                'mistag': mistag,
                'tageff': tageff,
                'Gamma': Gamma,
                'timeresmodel': timeresmodel,
                'acceptance': acceptance,
                'timeerrpdf': timeerrpdf,
                'mistagpdf': mistagpdf,
                'kfactorpdf': kfactorpdf,
                'kvar': kvar,
                'adet': adet,
                'atageff_f': atageff_f,
                'atageff_t': atageff_t
                }
        print 'buildNonOscDecayTimePdf('
        for kw in kwargs:
            print '\t%s = %s' % (kw, kwargs[kw])
        print '\t)'
        print 72 * '#'

    # constants used
    zero = WS(ws, RooConstVar('zero', 'zero', 0.))

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
    timeresmodel = applyBinnedAcceptance(
        config, ws, time, timeresmodel, acceptance)
    # FIXME: understand why this breaks at Optimize > 2
    if config['ParameteriseIntegral']:
        parameteriseResModelIntegrals(config, timeerrpdf, timeerr, timeresmodel)

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

    # work out in which observables to parameterise k-factor smearing, then
    # apply it
    paramObs = RooArgSet(qt, qf)
    if None != mistagpdf:
        paramObs.add(mistag)
    if None != timeerrpdf:
        paramObs.add(timeerr)
    retVal = applyKFactorSmearing(config, name, ws, time, rawtimepdf, kvar,
            kfactorpdf, paramObs)
    
    retVal = applyDecayTimeErrPdf(config, name, ws, time, timeerr, qt, qf,
            mistag, retVal, timeerrpdf, mistagpdf)
    
    if None != mistagpdf:
        otherargs = [ mistag, mistagpdf, tageff, adet, atageff_f, atageff_t ]
    else:
        otherargs = [ tageff, adet, atageff_f, atageff_t ]
    ourmistagpdf = WS(ws, NonOscTaggingPdf('%s_mistagPdf' % name,
        '%s_mistagPdf' % name, qf, qt, *otherargs))
    del otherargs

    retVal = WS(ws, RooProdPdf( '%s_qfqtetapdf' % retVal.GetName(),
        '%s_qfqtetapdf' % retVal.GetName(), retVal, ourmistagpdf))

    # if we do not bin the acceptance, we apply it here
    retVal = applyUnbinnedAcceptance(config, name, ws, retVal, acceptance)

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
    atageff = None				# asymmetry in tagging efficiency
    ):
    # Look in LHCb-INT-2011-051 for the conventions used
    from ROOT import ( RooConstVar, RooProduct, RooTruthModel, RooGaussModel,
        Inverse, RooBDecay, RooProdPdf, RooArgSet, DecRateCoeff,
        RooArgList )
    
    if config['Debug']:
        print 72 * '#'
        kwargs = {
                'config': config,
                'name': name,
                'ws': ws,
                'time': time,
                'timeerr': timeerr,
                'qt': qt,
                'qf': qf,
                'mistag': mistag,
                'tageff': tageff,
                'Gamma': Gamma,
                'DeltaGamma': DeltaGamma,
                'DeltaM': DeltaM,
                'C': C, 'D': D, 'Dbar':Dbar, 'S': S, 'Sbar': Sbar,
                'timeresmodel': timeresmodel,
                'acceptance': acceptance,
                'timeerrpdf': timeerrpdf,
                'mistagpdf': mistagpdf,
                'mistagobs': mistagobs,
                'kfactorpdf': kfactorpdf,
                'kvar': kvar,
                'aprod': aprod,
                'adet': adet,
                'atageff': atageff
                }
        print 'buildBDecayTimePdf('
        for kw in kwargs:
            print '\t%s = %s' % (kw, kwargs[kw])
        print '\t)'
        print 72 * '#'

    # constants used
    zero = WS(ws, RooConstVar('zero', 'zero', 0.))
    one = WS(ws, RooConstVar('one', 'one', 1.))

    if None == aprod: aprod = zero
    if None == adet: adet = zero
    if None == atageff: atageff = zero
    if None == mistagpdf:
        mistagobs = None
    else: # None != mistagpdf
        if None == mistagobs:
            raise NameError('mistag pdf set, but no mistag observable given')

    # if no time resolution model is set, fake one
    if timeresmodel == None:
        timeresmodel = WS(ws, RooTruthModel('%s_TimeResModel' % name,
            '%s time resolution model' % name, time))
    elif timeresmodel == 'Gaussian':
        timeresmodel = WS(ws, RooGaussModel('%s_TimeResModel' % name,
            '%s time resolution model' % name, time, zero, timeerr))

    # apply acceptance (if needed)
    timeresmodel = applyBinnedAcceptance(
            config, ws, time, timeresmodel, acceptance)
    if config['ParameteriseIntegral']:
        parameteriseResModelIntegrals(config, timeerrpdf, timeerr, timeresmodel)

    # if there is a per-event mistag distributions and we need to do things
    # correctly
    if None != mistagpdf:
        otherargs = [ mistagobs, mistagpdf, tageff ]
    else:
        otherargs = [ tageff ]
    otherargs += mistag
    otherargs += [ aprod, adet, atageff ]
    flag = 0
    if 'Bs2DsK' == name and 'CADDADS' == config['Bs2DsKCPObs']:
        flag = DecRateCoeff.AvgDelta
    # build coefficients to go into RooBDecay
    cosh = WS(ws, DecRateCoeff('%s_cosh' % name, '%s_cosh' % name,
        DecRateCoeff.CPEven, qf, qt, one, one, *otherargs))
    sinh = WS(ws, DecRateCoeff('%s_sinh' % name, '%s_sinh' % name,
        flag | DecRateCoeff.CPEven, qf, qt, D, Dbar, *otherargs))
    cos = WS(ws, DecRateCoeff('%s_cos' % name, '%s_cos' % name,
        DecRateCoeff.CPOdd, qf, qt, C, C, *otherargs))
    if 'PdfSSbarSwapMinusOne' in config['BugFlags']:
        sin = WS(ws, DecRateCoeff('%s_sin' % name, '%s_sin' % name,
            flag | DecRateCoeff.CPOdd, qf, qt, Sbar, S, *otherargs))
    else:
        sin = WS(ws, DecRateCoeff('%s_sin' % name, '%s_sin' % name,
            flag | DecRateCoeff.CPOdd | DecRateCoeff.Minus,
            qf, qt, S, Sbar, *otherargs))
    del flag
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

    # work out in which observables to parameterise k-factor smearing, then
    # apply it
    paramObs = RooArgSet(qt, qf)
    if None != mistagpdf:
        paramObs.add(mistagobs)
    if None != timeerrpdf:
        paramObs.add(timeerr)
    retVal = applyKFactorSmearing(config, name, ws, time, rawtimepdf, kvar,
            kfactorpdf, paramObs)

    retVal = applyDecayTimeErrPdf(config, name, ws, time, timeerr, qt, qf,
            mistagobs, retVal, timeerrpdf, mistagpdf)
    
    # if we do not bin the acceptance, we apply it here
    retVal = applyUnbinnedAcceptance(config, name, ws, retVal, acceptance)

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

def printPDFTermsOnDataSet(dataset, terms = []):
    print 72 * '#'
    print 'DEBUG: DUMPING TERMS FOR EACH ENTRY IN DATASET'
    print 72 * '#'
    vlist = [ v.clone(v.GetName()) for v in terms ]
    for v in vlist:
        ROOT.SetOwnership(v, True)
        v.attachDataSet(dataset)
    tmpvlist = {}
    for v in vlist: tmpvlist[v.GetName()] = v
    vlist = tmpvlist
    del tmpvlist
    notchanged = False
    while not notchanged:
        notchanged = True
        for k in dict(vlist):
            vs = vlist[k].getVariables()
            ROOT.SetOwnership(vs, True)
            it = vs.fwdIterator()
            while True:
                obj = it.next()
                if None == obj: break
                if obj.GetName() in vlist: continue
                notchanged = False
                vlist[obj.GetName()] = obj
            vs = vlist[k].getComponents()
            ROOT.SetOwnership(vs, True)
            it = vs.fwdIterator()
            while True:
                obj = it.next()
                if None == obj: break
                if obj.GetName() in vlist: continue
                notchanged = False
                vlist[obj.GetName()] = obj
        if not notchanged: break
    obs = dataset.get()
    obsdict = { }
    it = obs.fwdIterator()
    while True:
        obj = it.next()
        if None == obj: break
        obsdict[obj.GetName()] = obj
    for i in range(0, dataset.numEntries()):
        dataset.get(i)
        if dataset.isWeighted():
            s = 'DEBUG: WEIGHT %g OBSERVABLES:' % dataset.weight()
        else:
            s = 'DEBUG: OBSERVABLES:'

        for k in obsdict:
            s = ('%s %s = %g' % (s, k, obsdict[k].getVal()) if
                    obsdict[k].InheritsFrom('RooAbsReal') else
                    '%s %s = %d' % (s, k, obsdict[k].getIndex()))
        print s
        vals = {}
        for k in vlist:
            vals[k] = (vlist[k].getValV(obs) if
                    vlist[k].InheritsFrom('RooAbsReal') else vlist[k].getIndex())
        for k in sorted(vals.keys()):
            if k in obsdict: continue
            print 'DEBUG:    ===> %s = %g' % (k, vals[k])
    print 72 * '#'
    return None

#------------------------------------------------------------------------------
def getMistagBinBounds(config, mistag, mistagdistrib):
    # suggest a binning for turning per-event mistag into mistag categories;
    # mistagdistrib can be a PDF or a RooDataSet
    mistag.setBins(1000, 'MistagBinBounds')
    from ROOT import RooArgSet, RooHistPdf, RooDataHist
    if (mistagdistrib.InheritsFrom('RooAbsData') and not
            mistagdistrib.InheritsFrom('RooDataHist')):
        # ok, unbinned data set, get only tagged events, and form a binned clone
        argset = RooArgSet(mistag)
        mistagdistrib = mistagdistrib.reduce(
                RooFit.SelectVars(argset), RooFit.cut('0 != qt'))
        ROOT.SetOwnership(mistagdistrib, True)
        dhist = RooDataHist(
                '%s_binned' % mistagdistrib.GetName(),
                '%s_binned' % mistagdistrib.GetName(),
                mistagdistrib.get(), 'MistagBinBounds')
        dhist.add(mistagdistrib)
        mistagdistrib = dhist
    if mistagdistrib.InheritsFrom('RooAbsData'):
        # convert a binned dataset to a RooHistPdf
        dhist = mistagdistrib
        mistagdistrib = RooHistPdf('%s_pdf' % dhist.GetName(),
                '%s_pdf' % dhist.GetName(), RooArgSet(mistag), dhist)
    if (mistagdistrib.InheritsFrom('RooAbsPdf')):
        # use createCdf to obtain the CDF
        cdfroofit = mistagdistrib.createCdf(
                RooArgSet(mistag), RooArgSet(mistag))
        ROOT.SetOwnership(cdfroofit, True)
        def cdf(x):
            oldval = mistag.getVal()
            mistag.setVal(x)
            retVal = cdfroofit.getVal()
            mistag.setVal(oldval)
            return retVal
    if (mistagdistrib.InheritsFrom('RooHistPdf') and
            (abs(cdf(mistag.getMin())) > 1e-9 or
                abs(cdf(mistag.getMax()) - 1.) > 1e-9)):
        # createCdf does not work properly for RooHistPdf in older ROOT
        # versions because RooHistPdf does not support integrals over
        # subranges, so we have to fake this functionality until it's
        # supported by RooFit upstream
        #
        # capture histogram bin boundaries and contents
        print 'WARNING: Your version of RooFit still has buggy analytical ' \
                'integrals for RooHistPdf - activating workaround.'
        binboundlist = mistagdistrib.binBoundaries(
                mistag, mistag.getMin(), mistag.getMax())
        ROOT.SetOwnership(binboundlist, True)
        binbounds = [ v for v in binboundlist ]
        del binboundlist
        bincontents = [ ]
        oldval = mistag.getVal()
        for i in xrange(0, len(binbounds) - 1):
            mistag.setVal(0.5 * (binbounds[i] + binbounds[i + 1]))
            bincontents.append(mistagdistrib.getValV(RooArgSet(mistag)))
        mistag.setVal(oldval)
        # build CDF from histogram
        def cdf(x):
            s = 0.
            for i in xrange(0, len(binbounds) - 1):
                if x < binbounds[i]:
                    break
                elif x >= binbounds[i + 1]:
                    s += bincontents[i]
                else:
                    s += (bincontents[i] * (x - binbounds[i]) /
                                (binbounds[i + 1] - binbounds[i]))
                    break
            return s
    # find x for which f(x) = y by bisection
    def mybisect(y, f, lo, hi):
        initdx = abs(hi - lo)
        flo, fhi = f(lo) - y, f(hi) - y
        if 0. == flo: return lo
        elif 0. == fhi: return hi
        mid = .5 * (lo + hi)
        while (abs(hi - lo) > 1e-15 and abs(hi - lo) / initdx > 1e-15):
            fmid = f(mid) - y
            if 0. == fmid: break
            elif flo * fmid < 0.: hi, fhi = mid, fmid
            elif fmid * fhi < 0.: lo, flo = mid, fmid
            else: raise ValueError('no sign change in f(x) between %g and %g'
                    % (lo, hi))
            mid = .5 * (lo + hi)
        return mid
    # find binning with roughly same stats by inverting the CDF by bisection
    lo, hi, binsum = mistag.getMin(), mistag.getMax(), cdf(mistag.getMax())
    retVal = [ lo ]
    for i in xrange(1, config['NMistagCategories']):
        retVal.append(mybisect(binsum *
            float(i) / float(config['NMistagCategories']), cdf, lo, hi))
    retVal.append(hi)
    print 'INFO: suggested mistag category bounds: %s' % str(retVal)
    return retVal

def getTrueOmegasPerCat(config, mistagobs, mistag, mistagpdf):
    # calculate true per-category omegas based on the mistagpdf and the
    # calibration that goes into the generation pdf
    from ROOT import RooRealVar, RooCustomizer, RooProduct, RooArgList, RooArgSet
    eta1 = RooRealVar('eta1', 'eta1', mistagobs.getMin(),
            mistagobs.getMin(), mistagobs.getMax())
    eta2 = RooRealVar('eta2', 'eta2', mistagobs.getMax(),
            mistagobs.getMin(), mistagobs.getMax())
    prod = RooProduct('prod', 'prod', RooArgList(mistag, mistagpdf))
    oldmistagobs = mistagobs
    mistagobs = mistagobs.clone(mistagobs.GetName() + '_catclone')
    ROOT.SetOwnership(mistagobs, True)
    mistagobs.setRange(eta1, eta2)
    c = RooCustomizer(prod, 'cust')
    c.replaceArg(oldmistagobs, mistagobs)
    prod = c.build()
    ROOT.SetOwnership(prod, True)
    c = RooCustomizer(mistagpdf, 'cust2')
    c.replaceArg(oldmistagobs, mistagobs)
    pdf = c.build()
    ROOT.SetOwnership(pdf, True)
    if pdf.InheritsFrom('RooHistPdf'): pdf.forceNumInt()
    evnumer = prod.createIntegral(RooArgSet(mistagobs))
    evdenom = pdf.createIntegral(RooArgSet(mistagobs))
    totevdenom = evdenom.getVal()
    avomega = evnumer.getVal() / totevdenom
    omegas = [ ]
    for i in xrange(0, len(config['MistagCategoryBinBounds']) - 1):
        eta1.setVal(config['MistagCategoryBinBounds'][i])
        eta2.setVal(config['MistagCategoryBinBounds'][i + 1])
        omegas.append(evnumer.getVal() / evdenom.getVal())
    print 'INFO: Mistag calibration %s:' % mistag.GetName()
    print 'INFO:                Average omega (PDF): %g' % avomega
    print 'INFO:  Per category average omegas (PDF): %s' % str(omegas)
    return avomega, omegas

def getEtaPerCat(config, mistagobs, ds):
    # calculate overall and per-category eta averages for a given data set ds
    from ROOT import RooArgList, RooArgSet
    # isolate tagged events
    total = ds.sumEntries()
    argset = RooArgSet(mistagobs)
    ds = ds.reduce(RooFit.Cut('0 != qt'), RooFit.SelectVars(argset))
    ROOT.SetOwnership(ds, True)
    # set up loop over data set to get eta averages
    etasums = [ 0. for i in xrange(0, config['NMistagCategories']) ]
    weightsums = [ 0. for i in xrange(0, config['NMistagCategories']) ]
    etasum = 0.
    weightsum = 0.
    obs = ds.get()
    etavar = obs.find(mistagobs.GetName())
    isWeighted = ds.isWeighted()
    # loop over data set
    for i in xrange(0, ds.numEntries()):
        ds.get(i)
        eta = etavar.getVal()
        w = ds.weight() if isWeighted else 1.
        # calculate average eta
        etasum += w * eta
        weightsum += w
        # find category and update per-category eta averages
        for j in xrange(0, len(config['MistagCategoryBinBounds']) - 1):
            if eta < config['MistagCategoryBinBounds'][j]: break
            elif eta >= config['MistagCategoryBinBounds'][j + 1]: continue
            else:
                # found bin
                etasums[j] += w * eta
                weightsums[j] += w
                break
    # final division needed to form the eta averages
    etasum /= weightsum
    for i in xrange(0, len(etasums)):
        if 0. == etasums[i]: continue
        etasums[i] /= weightsums[i]
        weightsums[i] /= total
    print 'INFO:               Average eta (data sample): %g' % etasum
    print 'INFO: Per category average etas (data sample): %s' % str(etasums)
    print 'INFO: Per category tagging eff. (data sample): %s' % str(weightsums)
    return etasum, etasums, weightsums

def makeTagEff(
        config,                         # configuration dictionary
        ws,                             # workspace
        modename,                       # mode nickname
        yieldhint = None,               # helps setting initial error estimate
        perCategoryTagEffsShared = True,# share tageffs across modes
        perCategoryTagEffsConst = True  # set tageffs constant
        ):
    # make a tagging efficiency for mode modename
    #
    # if we're fitting per-event mistag or average mistags without mistag
    # categories, this routine just builds a RooRealVar for a per-mode mistag
    #
    # when fitting mistag categories, however, one also needs per-category
    # tagging efficiencies to make sure the normalisation of the PDF is not
    # screwed up
    from ROOT import RooRealVar, RooArgList, TaggingCat
    from math import sqrt
    if (config['PerEventMistag'] or None == config['NMistagCategories']):
        eff = WS(ws, RooRealVar(
            '%s_TagEff' % modename, '%s_TagEff' % modename,
            config['TagEffSig'], 0., 1.))
        eff.setError(0.25)
        return eff
    # ok, we're using mistag categories
    effs = config['MistagCategoryTagEffs']
    if (len(effs) != config['NMistagCategories']):
        return None
    # if the per-category tagging efficiencies are fixed anyway, we can share
    # them among modes
    if perCategoryTagEffsConst:
        perCategoryTagEffsShared = True
    efflist = RooArgList()
    for i in xrange(0, len(effs)):
        # naive initial error estimate for efficiency error:
        # efficiency numerator ~ N eps, denominator N, where N is total number
        # of events; then (assuming poisson errors on numerator and
        # denominator) the error on eps should be
        # eps * sqrt((1 + eps) / (N * eps))
        if None == yieldhint:
            yieldhint = float(sum(config['NEvents']))
        if 0. == effs[i]:
            err = sum(effs) / float(config['NMistagCategories']) / sqrt(12.)
        else:
            err = effs[i] * sqrt((1. + effs[i]) / (effs[i] * yieldhint))
        # if we float, float within limit times err
        limit = 10.
        blo, bhi = effs[i] - limit * err, effs[i] + limit * err
        blo, bhi = max(0., blo), min(1., bhi)
        if perCategoryTagEffsShared:
            eff = WS(ws, RooRealVar(
                'TagEffCat%02d' % i, 'TagEffCat%02d' % i, effs[i], blo, bhi))
        else:
            eff = WS(ws, RooRealVar(
                '%s_TagEffCat%02d' % (modename, i),
                '%s_TagEffCat%02d' % (modename, i), effs[i], blo, bhi))
        eff.setError(err)
        if perCategoryTagEffsConst: eff.setConstant(True)
        efflist.add(eff)
    qt, tagcat = ws.cat('qt'), ws.cat('tagcat')
    print ('%s_TagEff' % modename, '%s_TagEff' % modename,
            qt, tagcat, efflist, True)
    eff = WS(ws, TaggingCat(
            '%s_TagEff' % modename, '%s_TagEff' % modename,
            qt, tagcat, efflist, True))
    return eff

#------------------------------------------------------------------------------
def getMasterPDF(config, name, debug = False):
    from B2DXFitters import cpobservables

    import sys
    from ROOT import (RooRealVar, RooStringVar, RooFormulaVar, RooProduct,
        RooCategory, RooMappedCategory, RooMultiCategory, RooConstVar,
        RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay,
        RooGaussModel, RooTruthModel, RooWorkspace, RooAbsArg,
        RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooExponential,
        RooPolynomial, RooUniform, RooFit, RooUniformBinning,
        BdPTAcceptance, RooSimultaneous, RangeAcceptance, RooEffProd,
        RooAddition, RooProduct, Inverse, SquaredSum, CPObservable,
        PowLawAcceptance, MistagCalibration)
    # fix context
    config = dict(config)
    config['Context'] = name
    if config['FitMode'] not in ('cFit', 'cFitWithWeights', 'sFit'):
        print 'ERROR: Unknown fit mode %s' % config['FitMode']
        return None
    # forcibly fix various settings
    if config['PerEventMistag'] and config['Sanitise']:
        if 'mistag' in config['constParams']:
            config['constParams'].remove('mistag')
    if 'DsK' in config['Personality']:
        # fix pidk range for DsK (so we don't have to repeat it in the
        # personality every time)
        from math import log
        config['FitRanges']['pidk'] = [ log(5.), log(150.) ]
    if (config['Sanitise'] and 'sFit' == config['FitMode']):
        # only main mode, get mass ranges right
        config['Modes'] = [ config['Modes'][0] ]
        config['FitRanges']['mass'] = ( [ 5100., 5800. ] if
                '2011Conf' in config['Personality'] else [ 5300., 5800. ] )
        config['FitRanges']['dsmass'] = [ 1930., 2015. ]
    if 'GEN' in name and config['Sanitise']:
        # for generation, this is both faster and more accurate
        config['NBinsAcceptance'] = 0
        config['NBinsMistag'] = 0
        config['NBinsProperTimeErr'] = 0
        config['NBinsMass'] = 0
        config['MistagInterpolation'] = False
        config['MassInterpolation'] = False
        config['DecayTimeErrInterpolation'] = False
        config['AcceptanceCorrectionInterpolation'] = False
        config['CombineModesForEffCPObs'] = [ ]
        config['ParameteriseIntegral'] = False
    print '########################################################################'
    print '%s config:' % name
    print
    for k in sorted(config.keys()):
        print '%-32s: %s' % (k, str(config[k]))
    print '########################################################################'
    ws = RooWorkspace('WS_%s' % name)

    zero = WS(ws, RooConstVar('zero', '0', 0.))
    one = WS(ws, RooConstVar('one', '1', 1.))

    # create weight variable, if we need one
    if config['FitMode'] in ('cFitWithWeights', 'sFit'):
        weight = WS(ws, RooRealVar('weight', 'weight',
            -sys.float_info.max, sys.float_info.max))
    else:
        weight = None
    # figure out lower bound of fit range
    timelo = config['FitRanges']['time'][0]
    if config['AcceptanceFunction'] == 'BdPTAcceptance':
        timelo = max(timelo, config['BdPTAcceptance_offset'])
    time = WS(ws, RooRealVar('time', 'decay time', 1., timelo,
        config['FitRanges']['time'][1], 'ps'))
    if config['NBinsAcceptance'] > 0:
        # provide binning for acceptance
        from ROOT import RooUniformBinning
        acceptanceBinning = RooUniformBinning(
            time.getMin(), time.getMax(), config['NBinsAcceptance'],
            'acceptanceBinning')
        time.setBinning(acceptanceBinning, 'acceptanceBinning')
    timeerr = WS(ws, RooRealVar('timeerr', 'decay time error',
        config['FitRanges']['timeerr'][0], config['FitRanges']['timeerr'][1],
        'ps'))

    mass = WS(ws, RooRealVar('mass', 'mass', config['FitRanges']['mass'][0],
        config['FitRanges']['mass'][1]))
    if config['NBinsMass'] > 0:
        mass.setBinning(RooUniformBinning(
            mass.getMin(), mass.getMax(), config['NBinsMass']), 'massbins')
    if '2011Paper' in config['Personality']:
        dsmass = WS(ws, RooRealVar('dsmass', 'dsmass',
            config['FitRanges']['dsmass'][0],
            config['FitRanges']['dsmass'][1]))
        pidk = WS(ws, RooRealVar('pidk', 'pidk',
            config['FitRanges']['pidk'][0], config['FitRanges']['pidk'][1]))
    else:
        dsmass, pidk = None, None
    
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
    mistag = WS(ws, RooRealVar('mistag', 'Signal mistag rate',
        config['TagOmegaSig'], config['FitRanges']['mistag'][0],
        config['FitRanges']['mistag'][1]))

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
    for sname in config['SampleCategories']:
        sample.defineType(sname)

    # Define the observables
    # ----------------------
    observables = [ sample, qt, qf, time ]
    if 'sFit' != config['FitMode']:
        observables = observables + [ mass ]
        if '2011Paper' in config['Personality']:
            observables = [ pidk, dsmass ] + observables
    condobservables = [ ]

    if config['PerEventMistag']:
        mistagCal = []
        namsfx = [ 'B', 'Bbar' ]
        if len(config['MistagCalibrationParams']) > 2:
            raise NameError('MistagCalibrationParams configurable slot must'
                    ' not have more than two entries (B, Bbar)!')
        for j in xrange(0, len(config['MistagCalibrationParams'])):
            if len(config['MistagCalibrationParams'][j]) != 2 and \
                    len(config['MistagCalibrationParams'][j]) != 3:
                raise NameError('MistagCalibrationParams configurable slot '
                        'calibration %u must be an array of length 2 or 3!' %
                        j)
            mistagcalib = RooArgList()
            avgmistag = zero
            if len(config['MistagCalibrationParams'][j]) == 2 or \
                    len(config['MistagCalibrationParams'][j]) == 3:
                i = 0
                for p in config['MistagCalibrationParams'][j][0:2]:
                    v = WS(ws, RooRealVar(
                        'MistagCalib%s_p%u' % (namsfx[j], i),
                        'MistagCalib%s_p%u' % (namsfx[j], i), p))
                    v.setConstant(False)
                    mistagcalib.add(v)
                    i = i + 1
                del i
            if len(config['MistagCalibrationParams'][j]) == 3:
                avgmistag = WS(ws, RooRealVar(
                    'MistagCalib%s_avgmistag' % namsfx[j],
                    'MistagCalib%s_avgmistag' % namsfx[j],
                    config['MistagCalibrationParams'][j][2]))
            mistagCal.append(WS(ws, MistagCalibration(
                '%s%s_c' % (mistag.GetName(), namsfx[j]),
                '%s%s_c' % (mistag.GetName(), namsfx[j]),
                mistag, mistagcalib, avgmistag)))
            del mistagcalib
            del avgmistag
        del namsfx
    else:
        mistagCal = [ mistag ]
    # read in templates
    if config['PerEventMistag']:
        mistagtemplate = getMistagTemplate(config, ws, mistag)
    else:
        mistagtemplate = None
    if config['UseKFactor']:
        ktemplates = getKFactorTemplates(config, ws, k)
    else:
        ktemplates = None
    masstemplates = getMassTemplates(config, ws, mass, dsmass, pidk)

    # ok, since the mistagtemplate often is a RooHistPdf, we can fine-tune
    # ranges and binning to match the histogram
    if (config['PerEventMistag'] and
            mistagtemplate.InheritsFrom('RooHistPdf')):
        hist = mistagtemplate.dataHist().createHistogram(mistag.GetName())
        ROOT.SetOwnership(hist, True)
        ax = hist.GetXaxis()
        nbins = hist.GetNbinsX()
        print 'INFO: adjusting range of %s to histogram ' \
                'used in %s: %g to %g, was %g to %g' % \
                (mistag.GetName(), mistagtemplate.GetName(),
                        ax.GetBinLowEdge(1), ax.GetBinUpEdge(nbins),
                        mistag.getMin(), mistag.getMax())
        mistag.setRange(ax.GetBinLowEdge(1), ax.GetBinUpEdge(nbins))
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
                hist, mistag, True))
        del ax
        del hist
        if config['NBinsMistag'] > 0 and nbins < config['NBinsMistag']:
            print 'INFO: adjusting binning of %s to histogram ' \
                    'used in %s: %u bins, was %u bins' % \
                    (mistag.GetName(), mistagtemplate.GetName(),
                            nbins, config['NBinsMistag'])
            config['NBinsMistag'] = nbins
            del nbins

    # OK, get the show on the road if we are using mistag categories
    if (None != config['NMistagCategories'] and
            config['NMistagCategories'] > 0 and config['PerEventMistag']):
        # ok, we have to provide the machinery to convert per-event mistag to
        # mistag categories
        if (None != config['MistagCategoryBinBounds'] and
                len(config['MistagCategoryBinBounds']) != 1 +
                config['NMistagCategories']):
            print ('ERROR: %d mistag categories requested, number of bin '
                    'bounds does not match' % config['NMistagCategories'])
            return None
        if (None == config['MistagCategoryBinBounds']):
            # ok, auto-tune mistag category bin bounds from mistag pdf template
            if None == mistagtemplate:
                print ('ERROR: No mistag category bounds present, and no '
                        'mistag pdf template to tune from!')
                return None
            # all fine
            config['MistagCategoryBinBounds'] = getMistagBinBounds(
                    config, mistag, mistagtemplate)
        # create category
        from ROOT import std, RooBinning, RooBinningCategory
        bins = std.vector('double')()
        for bound in config['MistagCategoryBinBounds']:
            bins.push_back(bound)
        binning = RooBinning(bins.size() - 1,
                bins.begin().base(), 'taggingCat')
        mistag.setBinning(binning, 'taggingCat')
        tagcat = WS(ws, RooBinningCategory('tagcat', 'tagcat',
            mistag, 'taggingCat'))
        del binning
        del bins
        # print MC truth omegas for all categories and calibrations when
        # generating
        if 'GEN' in config['Context']:
            for cal in mistagCal:
                getTrueOmegasPerCat(config, mistag, cal, mistagtemplate)
    if (None != config['NMistagCategories'] and
            config['NMistagCategories'] > 0 and not config['PerEventMistag']):
        # ok, we have mistag categories
        if (None == config['MistagCategoryBinBounds'] or
                len(config['MistagCategoryBinBounds']) != 1 +
                config['NMistagCategories']):
            print ('ERROR: %d mistag categories requested, number of bin '
                    'bounds does not match' % config['NMistagCategories'])
            return None
        if (None == config['MistagCategoryBinBounds'] or
                len(config['MistagCategoryOmegas']) !=
                config['NMistagCategories']):
            print ('ERROR: %d mistag categories requested, number of '
                    'per-category omegas does not match' %
                    config['NMistagCategories'])
            return None
        if (None == config['MistagCategoryBinBounds'] or
                len(config['MistagCategoryTagEffs']) !=
                config['NMistagCategories']):
            print ('ERROR: %d mistag categories requested, number of '
                    'per-category tagging efficiencies does not match' %
                    config['NMistagCategories'])
            return None
        # verify that there is no error in MistagCategoryOmegaRange
        if (2 != len(config['MistagCategoryOmegaRange']) or
                config['MistagCategoryOmegaRange'][0] >=
                config['MistagCategoryOmegaRange'][1]):
            print 'ERROR: invalid MistagCategoryOmegaRange supplied in config!'
            return None
        # create a category for mistag categories and the per-category omegas
        from math import sqrt
        omegas = RooArgList()
        tagcat = WS(ws, RooCategory('tagcat', 'tagcat'))
        for i in xrange(0, config['NMistagCategories']):
            tagcat.defineType('cat%02d' % i, i)
            v = WS(ws, RooRealVar(
                'OmegaCat%02d' % i, 'OmegaCat%02d' % i,
                config['MistagCategoryOmegas'][i],
                *config['MistagCategoryOmegaRange']))
            # set rough and reasonable error estimate
            v.setConstant(False)
            v.setError((config['MistagCategoryBinBounds'][i + 1] -
                config['MistagCategoryBinBounds'][i]) / sqrt(12.))
            omegas.add(v)
        # ok, build the mistag
        from ROOT import TaggingCat
        mistag = WS(ws, TaggingCat('OmegaPerCat', 'OmegaPerCat',
				    qt, tagcat, omegas))
        mistagCal = [ mistag ]
        del omegas
        observables.append(tagcat)

    timepdfs = { }

    # Decay time resolution model
    # ---------------------------
    if type(config['DecayTimeResolutionModel']) == type([]):
        # ok, we got a list of: [sigma_0,sigma_1, ...] and [f0,f1,...]
        # build specified resolution model on the fly
        from ROOT import ( RooArgList, RooRealVar, RooGaussModel, RooAddModel )
        if 2 != len(config['DecayTimeResolutionModel']):
            raise TypeError('Unknown type of resolution model')
        ncomp = len(config['DecayTimeResolutionModel'][0])
        if ncomp < 1:
            raise TypeError('Unknown type of resolution model')
        if ncomp != len(config['DecayTimeResolutionModel'][1]) and \
                ncomp - 1 != len(config['DecayTimeResolutionModel'][1]):
            raise TypeError('Unknown type of resolution model')
        pdfs = RooArgList()
        fracs = RooArgList()
        i = 0
        for s in config['DecayTimeResolutionModel'][0]:
            sigma = WS(ws, RooRealVar('resmodel%02d_sigma' % i,
                'resmodel%02d_sigma' % i, s, 'ps'))
            bias = WS(ws, RooRealVar('timeerr_bias',
                'timeerr_bias', config['DecayTimeResolutionBias']))
            sf = WS(ws, RooRealVar('timeerr_scalefactor',
                'timeerr_scalefactor',
                config['DecayTimeResolutionScaleFactor'], .5, 2.))
            pdfs.add(WS(ws, RooGaussModel('resmodel%02d' % i, 'resmodel%02d' % i,
                time, bias, sigma, sf)))
            del sf
            del bias
            i += 1
        i = 0
        for s in config['DecayTimeResolutionModel'][1]:
            fracs.add(WS(ws, RooRealVar('resmodel%02d_frac' % i,
                'resmodel%02d_frac' % i, s, 'ps')))
            i += 1
        del s
        del i
        trm = WS(ws, RooAddModel('resmodel', 'resmodel', pdfs, fracs))
        del pdfs
        del fracs
        del ncomp
    elif type(config['DecayTimeResolutionModel']) == type(''):
        if 'PEDTE' not in config['DecayTimeResolutionModel']:
            PTResModels = ROOT.PTResModels
            trm = WS(ws, PTResModels.getPTResolutionModel(
                config['DecayTimeResolutionModel'],
                time, 'Bs', debug,
                config['DecayTimeResolutionScaleFactor'],
                config['DecayTimeResolutionBias']))
        else :
            from ROOT import RooRealVar, RooGaussModel
            # the decay time error is an extra observable!
            observables.append(timeerr)
            # time, mean, timeerr, scale
            bias = WS(ws, RooRealVar('timeerr_bias',
                'timeerr_bias', config['DecayTimeResolutionBias']))
            sf = WS(ws, RooRealVar('timeerr_scalefactor',
                'timeerr_scalefactor',
                config['DecayTimeResolutionScaleFactor'], .5, 2.))
            trm = WS(ws, RooGaussModel('GaussianWithPEDTE',
                'GaussianWithPEDTE', time, bias, timeerr, sf))
            del bias
            del sf
    else:
        raise TypeError('Unknown type of resolution model')

    # Decay time acceptance function
    # ------------------------------
    if (config['AcceptanceFunction'] and not (
        None == config['AcceptanceFunction'] == None or
        'None' == config['AcceptanceFunction'])):
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
        if 0 < config['NBinsAcceptance']:
            if config['StaticAcceptance']:
                from ROOT import RooDataHist, RooHistPdf
                dhist = WS(ws, RooDataHist(
                    '%s_dhist' % tacc.GetName(), '%s_dhist' % tacc.GetName(),
                    RooArgSet(time), 'acceptanceBinning'))
                tacc.fillDataHist(dhist, RooArgSet(time), 1.)
                dhist.SetNameTitle('%s_dhist' % tacc.GetName(),
                        '%s_dhist' % tacc.GetName())
                tacc = WS(ws, RooHistPdf('%s_binned' % tacc.GetName(),
                    '%s_binned' % tacc.GetName(), RooArgSet(time), dhist, 0))
            elif config['AcceptanceInterpolation']:
                from ROOT import RooBinned1DQuinticBase, RooAbsReal
                RooBinned1DQuintic = RooBinned1DQuinticBase(RooAbsReal)
                obins = time.getBins()
                time.setBins(config['NBinsAcceptance'])
                hist = tacc.createHistogram('%s_hist' % tacc, time)
                hist.Scale(1. / hist.Integral())
                ROOT.SetOwnership(hist, True)
                tacc = WS(ws, RooBinned1DQuintic(
                    '%s_binned' % tacc.GetName(), '%s_binned' % tacc.GetName(),
                    hist, time))
                time.setBins(obins)
    else:
        tacc = None
    
    # Decay time error distribution
    # -----------------------------
    if 'PEDTE' in config['DecayTimeResolutionModel']:
        if (None != config['DecayTimeErrorTemplateFile'] and
                None != config['DecayTimeErrorTemplateWorkspace'] and
                None != config['DecayTimeErrorTemplateName'] and
                None != config['DecayTimeErrorVarName']):
            terrpdf = getDecayTimeErrorTemplate(config, ws, timeerr)
        else:
            print "WARNING: Using trivial decay time error PDF"
            # resolution in ps: 7*terrpdf_shape
            terrpdf_shape = WS(ws, RooConstVar('terrpdf_shape', 'terrpdf_shape',
                .0352 / 7.))
            terrpdf_truth = WS(ws, RooTruthModel('terrpdf_truth', 'terrpdf_truth', timeerr))
            terrpdf_i0 = WS(ws, RooDecay('terrpdf_i0', 'terrpdf_i0', timeerr, terrpdf_shape,
                terrpdf_truth, RooDecay.SingleSided))
            terrpdf_i1 = WS(ws, RooPolynomial('terrpdf_i1','terrpdf_i1',
                timeerr, RooArgList(zero, zero, zero, zero, zero, zero, one), 0))
            terrpdf = WS(ws, RooProdPdf('terrpdf', 'terrpdf', terrpdf_i0, terrpdf_i1))
        if config['DecayTimeErrInterpolation']:
            from ROOT import RooBinned1DQuinticBase, RooAbsPdf
            RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
            obins = timeerr.getBins()
            nbins = config['NBinsProperTimeErr']
            if 0 == nbins:
                print 'ERROR: requested binned interpolation of timeerr %s %d %s' % (
                        'histograms with ', nbins, ' bins - increasing to 100 bins')
                nbins = 100
            if terrpdf.isBinnedDistribution(RooArgSet(timeerr)):
                if (nbins != obins):
                    print 'WARNING: changing binned interpolation of ' \
                            'timeerr to %u bins' % obins
            timeerr.setBins(nbins)
            hist = terrpdf.createHistogram('%s_hist' % terrpdf.GetName(), timeerr)
            ROOT.SetOwnership(hist, True)
            hist.Scale(1. / hist.Integral())
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
        observables.append(mistag)
        if config['TrivialMistag']:
            from ROOT import MistagDistribution
            omega0 = WS(ws, RooConstVar('omega0', 'omega0', 0.07))
            omegaf = WS(ws, RooConstVar('omegaf', 'omegaf', 0.25))
            omegaa = WS(ws, RooConstVar('omegaa', 'omegaa', config['TagOmegaSig']))
            sigMistagPDF = WS(ws, MistagDistribution(
                'sigMistagPDF_trivial', 'sigMistagPDF_trivial',
                mistag, omega0, omegaa, omegaf))
        else:
            sigMistagPDF = mistagtemplate
    else:
        sigMistagPDF = None

    # produce a pretty-printed yield dump in the signal region
    yielddict = {}
    totyielddict = {'up': {}, 'down': {}}
    print
    print 'Yield dump:'
    tmp = ('mode',)
    for i in config['SampleCategories']: tmp += (i,)
    tmp += ('total',)
    print ('%16s' + (1 + len(config['SampleCategories'])) * ' %11s') % tmp
    del tmp
    tottot = 0.
    for mode in config['Modes']:
        tot = 0.
        yields = ()
        for sname in config['SampleCategories']:
            y = masstemplates[mode][sname]['yield'].getVal()
            yields += (y,)
            tot += y
            if sname not in totyielddict:
                totyielddict[sname] = 0.
            totyielddict[sname] += y
        yields += (tot,)
        yields = (mode,) + yields
        print ('%16s' + (len(yields) - 1) * ' %11.5g') % yields
        tottot += tot
        yielddict[mode] = tot
        del tot
        del yields
        del y
    yields = ('Total',)
    for sname in config['SampleCategories']:
        yields += (totyielddict[sname],)
    yields += (tottot,)
    print ('%16s' + ((len(yields) - 1) * ' %11.5g')) % yields
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
    for mode in ( 'Bs2DsK', 'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst', 'Bd2DPi' ):
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
        elif 'Bs2DsK' == mode and 'CADDADS' == config['Bs2DsKCPObs']:
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
            D    = WS(ws, RooRealVar('%s_<D>' % mode   , '%s_<D>' % mode   ,
                0.5 * (ACPobs.Df() + ACPobs.Dfbar()), -limit, limit))
            Dbar = WS(ws, RooRealVar('%s_DeltaD' % mode, '%s_DeltaD' % mode,
                0.5 * (ACPobs.Df() - ACPobs.Dfbar()), -limit, limit))
            S    = WS(ws, RooRealVar('%s_<S>' % mode   , '%s_<S>' % mode   ,
                0.5 * (ACPobs.Sf() + ACPobs.Sfbar()), -limit, limit))
            Sbar = WS(ws, RooRealVar('%s_DeltaS' % mode, '%s_DeltaS' % mode,
                0.5 * (ACPobs.Sf() - ACPobs.Sfbar()), -limit, limit))
            C.setError(0.4)
            for v in (D, Dbar, S, Sbar):
                v.setError(0.6)
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
        asyms = { 'Prod': None, 'Det': None, 'TagEff': None }
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
        tageff = makeTagEff(config, ws, modenick)
        if mode.startswith('Bs'):
            gamma, deltagamma, deltam = gammas, deltaGammas, deltaMs
        elif mode.startswith('Bd'):
            gamma, deltagamma, deltam = gammad, deltaGammad, deltaMd
        else:
            gamma, deltagamma, deltam = None, None, None
        timepdfs[mode] = buildBDecayTimePdf(myconfig, mode, ws,
                time, timeerr, qt, qf, mistagCal, tageff,
                gamma, deltagamma, deltam, C, D, Dbar, S, Sbar,
                trm, tacc, terrpdf, sigMistagPDF, mistag, kfactorpdf, kfactor,
                asyms['Prod'], asyms['Det'], asyms['TagEff'])

    ########################################################################
    # Bs -> Ds Pi like modes
    ########################################################################
    for mode in ( 'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bs2DsstRho',
            'Bd2DsK', 'Bd2DK', 'Bd2DsPi' ):
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
        asyms = { 'Prod': None, 'Det': None, 'TagEff': None }
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
        tageff = makeTagEff(config, ws, modenick)
        timepdfs[mode] = buildBDecayTimePdf(config, mode, ws,
                time, timeerr, qt, qf, mistagCal, tageff,
                gamma, deltagamma, deltam, one, zero, zero, zero, zero,
                trm, tacc, terrpdf, sigMistagPDF, mistag, kfactorpdf, kfactor,
                asyms['Prod'], asyms['Det'], asyms['TagEff'])

    ########################################################################
    # non-osciallating modes
    ########################################################################
    # Lb->X modes first, then CombBkg
    for mode in ('Lb2Dsp', 'Lb2Dsstp', 'Lb2LcK', 'Lb2LcPi', 'CombBkg'):
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
                time, timeerr, qt, qf, mistag, tageff, gamma,
                trm, tacc, terrpdf, sigMistagPDF, kfactorpdf, kfactor,
                asyms['Det'], asyms['TagEff_f'], asyms['TagEff_t'])
    
    obs = RooArgSet('observables')
    for o in observables:
        obs.add(WS(ws, o))
    condobs = RooArgSet('condobservables')
    for o in condobservables:
        condobs.add(WS(ws, o))
    constr = RooArgSet('constraints')
    for c in constraints:
        constr.add(WS(ws, c))
    
    # Create the total PDF/EPDF
    # ---------------------
    #
    # gather the bits and pieces
    components = { }
    sfx = ('' if ('RooFitTopSimultaneousWorkaround' not in config['BugFlags']
        and 'GEN' not in config['Context']) else '_unfixed')
    totPDF = WS(ws, RooSimultaneous(
        'TotPDF%s' % sfx, 'TotPDF%s' % sfx, sample))
    if 'GEN' in config['Context']: sfx = ''
    totEPDF = WS(ws, RooSimultaneous(
        'TotEPDF%s' % sfx, 'TotEPDF%s' % sfx, sample))
    for sname in config['SampleCategories']:
        pdfs = RooArgList()
        yields = RooArgList()
        for mode in config['Modes']:
            if not mode in components:
                components[mode] = [ ]
            tpdf = timepdfs[mode]
            mpdf = masstemplates[mode][sname]
            # skip zero yield components
            if (0. == abs(mpdf['yield'].getVal()) and
                    mpdf['yield'].isConstant()):
                # if it doesn't have a yield, we might as well skip this
                # component
                continue
            else:
                if 'sFit' in config['FitMode']:
                    mtpdf = tpdf
                else:
                    mtpdf = WS(ws, RooProdPdf('%s_%s_PDF' % (mode, sname),
                        '%s_%s_PDF' % (mode, sname), mpdf['pdf'], tpdf))
                components[mode] += [ sname ]
            pdfs.add(mtpdf)
            yields.add(mpdf['yield'])
        totyield = WS(ws, RooAddition(
            '%s_totYield' % sname, '%s_totYield' % sname, yields))
        itotyield = WS(ws, Inverse('%sInv' % totyield.GetName(),
            '%sInv' % totyield.GetName(), totyield))
        fractions = RooArgList()
        for mode in config['Modes']:
            mpdf = masstemplates[mode][sname]
            if (0. == abs(mpdf['yield'].getVal()) and
                    mpdf['yield'].isConstant()):
                continue
            f = WS(ws, RooProduct(
                'f_%s_%s' % (mode, sname), 'f_%s_%s' % (mode, sname),
                RooArgList(mpdf['yield'], itotyield)))
            fractions.add(f)
        # remove the last fraction added, so RooFit recognises that we
        # want a normal PDF from RooAddPdf, not an extended one
        fractions.remove(f)
        # add all pdfs contributing yield in this sample category
        totEPDF.addPdf(WS(ws, RooAddPdf(
            '%s_EPDF' % sname, '%s_EPDF' % sname, pdfs, yields)), sname)
        totPDF.addPdf(WS(ws, RooAddPdf(
            '%s_PDF' % sname, '%s_PDF' % sname, pdfs, fractions)), sname)
    # report which modes got selected
    for mode in config['Modes']:
        print 'INFO: Mode %s components %s' % (mode, str(components[mode]))
    if '_unfixed' in totPDF.GetName():
        totPDF = WS(ws, RooAddPdf('TotPDF', 'TotPDF', RooArgList(totPDF),
            RooArgList()))
    if '_unfixed' in totEPDF.GetName():
        totEPDF = WS(ws, RooAddPdf('TotEPDF', 'TotEPDF', RooArgList(totEPDF),
            RooArgList()))
    # set variables constant if they are supposed to be constant
    setConstantIfSoConfigured(config, totEPDF)

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
    return {
            'ws': ws,
            'epdf': WS(ws, totEPDF),
            'pdf': WS(ws, totPDF),
            'observables': WS(ws, obs),
            'condobservables': WS(ws, condobs),
            'constraints': WS(ws, constr),
            'config': config,
            'weight': weight
            }

def fitPolynomialAnalytically(
        deg, datapoints, crossCheckWithTGraphErrors = False):
    # fits a polynomial through a list of data points
    #
    # degree            degree of polynomial to fit
    # datapoints        [ [ x_1, y_1, sigma_y_1], ... ]
    #
    # fit polynomial is p(x) = sum_k p_k x^k
    import ROOT, math
    from ROOT import Math, TMath, TGraphErrors, TF1
    ncoeffpol = deg + 1
    # check with ROOT's TGraphErrors, if caller wants us to
    if crossCheckWithTGraphErrors:
        gr = TGraphErrors(len(datapoints))
        i = 0
        for dp in datapoints:
            x, y, sigma = dp[0], dp[1], dp[2]
            gr.SetPoint(i, x, y)
            gr.SetPointError(i, 0., sigma)
            i = i + 1
        funcstr = '0'
        for i in xrange(0, ncoeffpol):
            funcstr = funcstr + ('+[%d]*x**%d' % (i, i))
        func = TF1('func', funcstr)
        print ''
        print 'RESULT OF PLAIN ROOT FIT TO TGRAPHERRORS'
        gr.Fit(func)
    # accumulate data points
    icov = ROOT.Math.SMatrix('double', ncoeffpol, ncoeffpol,
            ROOT.Math.MatRepSym('double', ncoeffpol))()
    rhs = ROOT.Math.SVector('double', ncoeffpol)()
    for dp in datapoints:
        x, y, sigma = dp[0], dp[1], dp[2]
        for i in xrange(0, ncoeffpol):
            rhs[i] += y * pow(x, i) / pow(sigma, 2)
            for j in xrange(0, i + 1):
                icov[i, j] = icov(i, j) + pow(x, i + j) / pow(sigma, 2)
    # data point for analytical fit accumulated
    # solve analytical fit
    cov = ROOT.Math.SMatrix('double', ncoeffpol, ncoeffpol,
            ROOT.Math.MatRepSym('double', ncoeffpol))(icov)
    if (not cov.InvertChol()):
        print ("ERROR: analytical fit for calibration parameters ' + \
            'failed - HESSE matrix singular or with negative eigenvalues!")
        return {}
    sol = ROOT.Math.SVector('double', ncoeffpol)()
    # python isn't smart enough to get the SMatrix matrix-vector
    # multiply, so we do it by hand...
    for i in xrange(0, ncoeffpol):
        tmp = 0.
        for j in xrange(0, ncoeffpol):
            tmp += cov(i, j) * rhs(j)
        sol[i] = tmp 
    # work out number of degrees of freedom
    ndf = len(datapoints) - ncoeffpol
    # get chi2
    chi2 = 0.
    for dp in datapoints: # sum over measurements i
        x, y, sigma = dp[0], dp[1], dp[2]
        # evaluate om = sum_k p_k x^k
        yy = 0.
        for i in xrange(0, ncoeffpol):
            yy += sol(ncoeffpol - 1 - i)
            if i != ncoeffpol - 1:
                yy *= x
        # chi2 += ((yy - y) / sigma_i) ^ 2
        chi2 += pow((yy - y) / sigma, 2)
    # print result
    print ''
    print ('FIT RESULT OF ANALYTICAL FIT: CHI^2 %f NDF %d '
            'CHI^2/NDF %f PROB %f') % (chi2, ndf, chi2 / float(ndf),
                    ROOT.TMath.Prob(chi2, ndf))
    print ''
    for i in xrange(0, ncoeffpol):
        print '%10s = %f +/- %f' % ('p%d' % i, sol(i),
                math.sqrt(cov(i, i)))
    print ''
    print 'CORRELATION MATRIX:'
    for i in xrange(0, ncoeffpol):
        s = ''
        for j in xrange(0, ncoeffpol):
            rho = cov(i, j) / math.sqrt(cov(i, i) * cov(j, j))
            s = s + (' % 6.3f' % rho )
        print s
    # analytical fit all done
    return {
            'ndf': ndf,
            'chi2': chi2,
            'prob': TMath.Prob(chi2, ndf),
            'polycoeffs': [ sol(i) for i in xrange(0, ncoeffpol) ],
            'polycoefferrors': [
                math.sqrt(cov(i, i)) for i in xrange(0, ncoeffpol) ],
            'covariance': [
                [ cov(i, j) for j in xrange(0, ncoeffpol) ]
                for i in xrange(0, ncoeffpol) ],
            'correlation': [
                [ cov(i, j) / math.sqrt(cov(i, i) * cov(j, j))
                    for j in xrange(0, ncoeffpol) ]
                for i in xrange(0, ncoeffpol) ]
            }

def runBsGammaFittercFit(generatorConfig, fitConfig, toy_num, debug, wsname,
        initvars, calibplotfile = None) :
    # tune integrator configuration
    from ROOT import RooAbsReal, TRandom3, RooArgSet, RooRandom, RooLinkedList
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

    pdf['ws'].Print()

    cats = [ ]
    for cat in [ 'sample', 'qt', 'qf' ]:
        if None == pdf['observables'].find(cat): continue
        cats.append(pdf['ws'].obj(cat))

    if None == generatorConfig['DataFileName']:
        dataset = pdf['epdf'].generate(pdf['observables'], RooFit.Verbose())
        ROOT.SetOwnership(dataset, True)
        if None != generatorConfig['WriteDataSetFileName']:
            writeDataSet(dataset,
                    generatorConfig['WriteDataSetFileName'],
                    generatorConfig['WriteDataSetTreeName'],
                    generatorConfig['DataSetVarNameMapping'])
    else:
        # read event from external file
        tmpset = RooArgSet(pdf['observables'])
        if None != pdf['weight']: tmpset.add(pdf['weight'])
        dataset = readDataSet(generatorConfig, pdf['ws'], tmpset)
        del tmpset
        # fix fitter config yields
        fitConfig['NEvents'] = []
        if None != pdf['observables'].find('sample'):
            sample = pdf['ws'].obj('sample')
            for sname in fitConfig['SampleCategories']:
                i = sample.lookupType(sname).getVal()
                tmpds = dataset.reduce(RooFit.Cut('sample==%d' % i))
                ROOT.SetOwnership(tmpds, True)
                fitConfig['NEvents'].append(tmpds.numEntries())
                del tmpds
                gc.collect()
        else:
            fitConfig['NEvents'].append(dataset.numEntries())

    # ok, if we are to fit in mistag categories, we need to convert per-event
    # mistag to categories now
    datasetAvgEta = None
    if (pdf['config']['PerEventMistag'] and
            None != pdf['config']['NMistagCategories'] and
            0 < pdf['config']['NMistagCategories']):
        # step 1: if there are no starting values for the per-category omegas,
        # we get them from the data now
        aveta, etas, effs = getEtaPerCat(pdf['config'],
                pdf['observables'].find('mistag'), dataset)
        # save average eta of the dataset to go into the fit workspace
        from ROOT import RooConstVar
        datasetAvgEta = RooConstVar('EtaAvg', 'EtaAvg', aveta)
        if (None == pdf['config']['MistagCategoryOmegas']):
            pdf['config']['MistagCategoryOmegas'] = etas
        if (None == pdf['config']['MistagCategoryTagEffs']):
            pdf['config']['MistagCategoryTagEffs'] = effs
        # step 2: add new column to dataset with mistag category
        tagcat = pdf['ws'].obj('tagcat')
        dataset.addColumn(tagcat)
        cats.append(tagcat)
        # step 3: copy generator values over to fitConfig (if not specified
        # explicitly by user in config options)
        for name in ('MistagCategoryOmegas', 'MistagCategoryBinBounds',
                'NMistagCategories', 'MistagCategoryTagEffs'):
            if (None == fitConfig[name]):
                fitConfig[name] = pdf['config'][name]

    # print some stats on the data set
    dataset.Print('v')
    for cat in cats:
        myds = dataset
        if 'tagcat' == cat.GetName():
            myds = dataset.reduce(RooFit.Cut('0 != qt'))
            ROOT.SetOwnership(myds, True)
        myds.table(cat).Print('v')
    dataset.table(RooArgSet(pdf['ws'].obj('qt'), pdf['ws'].obj('qf'))).Print('v')
    if generatorConfig['QuitAfterGeneration']:
        return

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
        gc.collect()
        # now merge all datasets
        while len(oldds) > 1:
            oldds[0].append(oldds[1])
            del oldds[1]
    dataset = oldds[0]
    del oldds

    del cats
    del pdf
    gc.collect()

    pdf = getMasterPDF(fitConfig, 'FIT', debug)
    # put average eta in if necessary
    if None != datasetAvgEta:
        datasetAvgEta = WS(pdf['ws'], datasetAvgEta)

    # reduce dataset to observables used in the fit
    dataset = dataset.reduce(RooFit.SelectVars(pdf['observables']))
    ROOT.SetOwnership(dataset, True)
    dataset = WS(pdf['ws'], dataset, [])
    gc.collect()

    plot_init   = (wsname != None) and initvars
    plot_fitted = (wsname != None) and (not initvars)

    pdf['ws'].Print()

    if plot_init :
        pdf['ws'].writeToFile(wsname)

    # check Optimize(1), Optimize(2) regularly against Optimize(0) to see if
    # the optimised versions work correctly for you - if the log file is not
    # identical to the one generated by Optimize(0), don't use it
    fitOpts = [
            RooFit.Optimize(fitConfig['Optimize']),
            RooFit.Strategy(fitConfig['Strategy']),
            RooFit.Minimizer(*fitConfig['Minimizer']),
            RooFit.Timer(), RooFit.Save(),
            # shut up Minuit in blinding mode
            RooFit.Verbose(fitConfig['IsToy'] or not fitConfig['Blinding'])
            ]
    if fitConfig['Offset']:
        fitOpts.append(RooFit.Offset(fitConfig['Offset']))
    if fitConfig['NumCPU'] > 1:
        fitOpts.append(RooFit.NumCPU(fitConfig['NumCPU']))
    if None != pdf['weight']:
        fitOpts.append(RooFit.SumW2Error(True))
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

    fitResult = pdf['pdf'].fitTo(dataset, fitopts)

    printResult(fitConfig, fitResult,
            fitConfig['Blinding'] and not fitConfig['IsToy'])

    # if we fit in mistag categories, do the calibration fit here
    calibws = None
    if (not pdf['config']['PerEventMistag'] and
            None != pdf['config']['NMistagCategories'] and
            0 < pdf['config']['NMistagCategories'] and
            0 == fitResult.status() and
            (3 == fitResult.covQual() or 'sFit' == fitConfig['FitMode'])):
        ROOT.gSystem.Load('libSmatrix')
        from ROOT import (RooRealVar, RooDataSet, RooArgSet, RooArgList,
                MistagCalibration, Math)
        # create data set and populate with per-category omegas;
        # also do a bit of validation on the way:
        # if fitted omega comes very close to the bounds in
        # fitConfig['MistagCategoryOmegaRange'], we skip that data point
        # we also skip data points if the uncertainty looks suspect (a factor
        # 5 below or above the average of all categories)
        averror = 0.
        varok = []
        mistagrange = fitConfig['MistagCategoryOmegaRange']
        mistagrangetol = 0.001 * (mistagrange[1] - mistagrange[0])
        for i in xrange(0, pdf['config']['NMistagCategories']):
            vname = 'OmegaCat%02d' % i
            var = fitResult.floatParsFinal().find(vname)
            if (abs(var.getVal() - mistagrange[0]) < mistagrangetol or
                    abs(var.getVal() - mistagrange[1]) < mistagrangetol or
                    var.getVal() <= mistagrange[0] or
                    var.getVal() >= mistagrange[1]):
                print ('WARNING: Skipping %s in calibration fit: touches '
                        'or is outside range!') % var.GetName()
                continue
            varok += [ vname ]
            averror += var.getError()
        averror /= float(len(varok))
        from ROOT import RooWorkspace
        calibws = RooWorkspace('calib', 'mistag calibration in categories')
        # create observables - we set a range for plotting later on
        eta = WS(calibws, RooRealVar('eta', '#eta', 0.,
            *fitConfig['MistagCategoryOmegaRange']))
        omega = WS(calibws, RooRealVar('omega', '#omega', 0.,
            *fitConfig['MistagCategoryOmegaRange']))
        # we have to tell RooFit that omega is supposed to have an uncertainty
        ds = WS(calibws, RooDataSet('mistagcalibdata', 'mistagcalibdata',
                RooArgSet(eta, omega), RooFit.StoreError(RooArgSet(omega))))
        anafitds = []
        for vname in varok:
            varinit = fitResult.floatParsInit().find(vname)
            var = fitResult.floatParsFinal().find(vname)
            errratio = var.getError() / averror
            if (0.2 > errratio or 5. < errratio):
                print ('WARNING: Skipping %s in calibration fit: uncertainty '
                        'is suspect (more than factor 5 away from average)') \
                                % vname
                continue
            eta.setVal(varinit.getVal())
            omega.setVal(var.getVal())
            omega.setError(var.getError())
            ds.add(RooArgSet(eta, omega))
            # add data point for analytical fit 
            detak = eta.getVal() - datasetAvgEta.getVal()
            om = omega.getVal()
            sigma = omega.getError()
            anafitds += [ [detak, om, sigma] ]
        # calibration polynomial
        calibParams = RooArgList()
        calibParams.add(WS(calibws, RooRealVar('p0', 'p_0',
            fitConfig['MistagCalibrationParams'][0][0], -1., 1.)))
        calibParams.add(WS(calibws, RooRealVar('p1', 'p_1',
            fitConfig['MistagCalibrationParams'][0][1], 0., 2.)))
        aveta = WS(calibws, RooRealVar('aveta', '<eta>',
            datasetAvgEta.getVal()))
        calib = WS(calibws, MistagCalibration('calib', 'calib', eta,
            calibParams, aveta))
        # fit calib to data
        calibFitResult = calib.chi2FitTo(ds, RooFit.YVar(omega),
                RooFit.Strategy(fitConfig['Strategy']),
                RooFit.Optimize(fitConfig['Optimize']),
                RooFit.Minimizer(*fitConfig['Minimizer']),
                RooFit.Timer(), RooFit.Save(), RooFit.Verbose())
        printResult(fitConfig, calibFitResult,
                fitConfig['Blinding'] and not fitConfig['IsToy'])
        anaCalibFitResult = fitPolynomialAnalytically(
                len(calibParams) - 1, anafitds)
        if None != calibplotfile:
            # dump a plot of the calibration to an eps/pdf file
            from ROOT import gROOT, gPad, RooGenericPdf, TPaveText
            isbatch = gROOT.IsBatch()
            gROOT.SetBatch(True)
            if None != gPad: gPad.Delete()
            etafr = eta.frame()
            calib.plotOn(etafr, RooFit.VisualizeError(calibFitResult))
            # ok, we need to cheat here because RooAbsReal does not have
            # paramOn which we would very much like to use, so make a
            # RooGenericPdf, and use that...
            calibpdf = RooGenericPdf('calibpdf', 'calibpdf', '@0',
                    RooArgList(calib))
            tmp = RooArgSet(calibParams)
            tmp.add(aveta)
            calib.plotOn(etafr)
            ds.plotOnXY(etafr, RooFit.YVar(omega))
            calibpdf.paramOn(etafr, RooFit.Layout(.1, 0.5, 0.9),
                    RooFit.Parameters(tmp), RooFit.ShowConstants(True))
            etafr.Draw()
            if (abs(anaCalibFitResult['chi2'] - calibFitResult.minNll()) /
                    (0.5 * (abs(anaCalibFitResult['chi2']) +
                        abs(calibFitResult.minNll()))) < 1e-3):
                # if analytical fit result and the RooFit one have about the
                # same chi^2, everything is fine, and we can use the
                # analytical fit result to obtain ndf, chi2 etc., since that
                # is much more convenient...
                text = TPaveText(0.5 * eta.getMax(), omega.getMin(),
                        .95 * eta.getMax(), 0.25 * omega.getMax())
                text.SetFillColor(ROOT.kWhite)
                text.SetBorderSize(0)
                text.AddText('#chi^{2} = %5.3f NDF = %2u' % (
                    anaCalibFitResult['chi2'], anaCalibFitResult['ndf']))
                text.AddText('#chi^{2}/NDF = %5.3f' %
                        (anaCalibFitResult['chi2'] / anaCalibFitResult['ndf']))
                text.AddText('Prob(#chi^{2}, NDF) = %5.3f' %
                        anaCalibFitResult['prob'])
                text.Draw()
            gPad.Print(calibplotfile)
            gROOT.SetBatch(isbatch)
    else:
        calibFitResult = None

    # dump fit result to a ROOT file
    from ROOT import TFile
    fitresfile = TFile('fitresult_%04d.root' % toy_num, 'RECREATE')
    fitresfile.WriteTObject(fitResult, 'fitresult_%04d' % toy_num)
    if None != calibFitResult:
        fitresfile.WriteTObject(calibFitResult, 'fitresult_calib_%04d' % toy_num)
    fitresfile.Close()
    del fitresfile

    if plot_fitted:
        pdf['ws'].writeToFile(wsname, True)
        if None != calibws:
            calibws.writeToFile(wsname, False)

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
parser.add_option('-p', '--personality',
        dest = 'personality',
        default = '2011Conf',
        type = 'string',
        action = 'store',
        help = 'fitter personality (e.g. \'2011Conf\')'
        )
parser.add_option('--calibplotfile',
        dest = 'calibplotfile',
        default = '',
        type = 'string',
        action = 'store',
        help = 'file name for calibration plot'
        )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    import copy, os
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
    
    # apply personality
    personalityfile = '%s/data/cFit/personality/%s.py' % (
            os.environ['B2DXFITTERSROOT'], options.personality)
    try:
        lines = file(personalityfile, 'r').readlines()
    except:
        parser.error('Unable to read personality %s from %s' %
               (options.personality, personalityfile))
    try:
        updateConfigDict(defaultConfig, {'Personality': options.personality})
        d = eval(compile(''.join(lines), personalityfile, 'eval'))
        updateConfigDict(defaultConfig, d)
        del d
    except:
            parser.error('Unknown personality \'%s\'' %
                    options.personality)
    del lines
    del personalityfile

    generatorConfig = copy.deepcopy(defaultConfig)
    fitConfig = copy.deepcopy(defaultConfig)
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
    if '' == options.calibplotfile:
        options.calibplotfile = None
    
    runBsGammaFittercFit(
            generatorConfig,
            fitConfig,
            TOY_NUMBER,
            options.debug,
            options.wsname,
            options.initvars,
            options.calibplotfile)

    # -----------------------------------------------------------------------------
