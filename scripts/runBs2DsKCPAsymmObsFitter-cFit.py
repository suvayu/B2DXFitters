#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78:expandtab
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
        # 'CDS'                 - C, D, Dbar, S, Sbar
        # 'CDSConstrained'      - same as CDS, but constrain C^2+D^2+S^2 = 1
        #                         (same for bar)
        # 'CADDADS'             - C, <D>, Delta D, <S>, Delta S
        #                         (<D>=(D+Dbar)/2, Delta D=(D-Dbar)/2 etc.)
        # 'LambdaPhases'        - |lambda|, strong and weak phase
        'Bs2DsKCPObs':                  'CDS',
        'SqSumCDSConstraintWidth':      0.01,

        # BLINDING
        'Blinding':                     True,

        # PHYSICAL PARAMETERS
        'Gammad':                       0.656, # in ps^{-1}
        'Gammas':                       0.661, # in ps^{-1}
        'DeltaGammad':                  0.,    # in ps^{-1}
        'DGsOverGs':                    -0.106/0.661, # DeltaGammas / Gammas
        'DeltaMd':                      0.507, # in ps^{-1}
        'DeltaMs':                      17.719, # in ps^{-1}
        'GammaLb':                      0.719, # in ps^{-1}
        'GammaCombBkg':                 0.800, # in ps^{-1}
        'DGammaCombBkg':                0.000, # in ps^{-1}
        'CombBkg_D':                    0.000, # D parameter (common for both final states)
        # CP observables
        'StrongPhase': {
            'Bs2DsK':           20. / 180. * pi,
            'Bs2DsstK':         -160. / 180. * pi,
            'Bs2DsKst':         -160. / 180. * pi,
            'Bs2DsstKst':       20. / 180. * pi,
            'Bd2DPi':           20. / 180. * pi,
            },
        'WeakPhase': {
                'Bs2DsK':       50. / 180. * pi,
                'Bs2DsstK':     50. / 180. * pi,
                'Bs2DsKst':     50. / 180. * pi,
                'Bs2DsstKst':   50. / 180. * pi,
                'Bd2DPi':       50. / 180. * pi,
                },
        'ModLf': {
                'Bs2DsK':       0.372,
                'Bs2DsstK':     0.470,
                'Bs2DsKst':     0.372,
                'Bs2DsstKst':   0.470,
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
            'TagEff': [ # one per tagger
                {
                #'Bs': 0., 'Bd': 0.
                }
                ],
            'TagEff_f': [ # one per tagger
                { },
                ],
            'TagEff_t': [ # one per tagger
                { 'Lb': 0.0, 'CombBkg': -0.04 },
                ],
            },
    # Tagging
    'NTaggers':                         1, # 1 - only one tagger (e.g. OS), 2 - e.g. OS + SSK
    'TagEff':                   {
            'Bs2DsK': [ 0.403 ], # one per tagger
            },
    'TagOmegaSig':                      0.396,
    'MistagCalibrationParams':  {
            # format:
            # 'mode1': [ [ [p0, p1, <eta>] ]_tagger1, ... ],
            # 'mode2': ...
            # with one or two sets of calibration parameters per tagger; if
            # there are two sets, the first is for true B, the second for true
            # Bbar
            'Bs2DsK': [ [
                [ 0.392, 1.035, 0.391 ], # true B
                #[ 0.392, 1.035, 0.391 ], # true Bbar
                ] ],
            },
    # truth/Gaussian/DoubleGaussian/GaussianWithPEDTE/GaussianWithLandauPEDTE/GaussianWithScaleAndPEDTE
    'DecayTimeResolutionModel':         'TripleGaussian',
    'DecayTimeResolutionBias':          0.,
    'DecayTimeResolutionScaleFactor':   1.15,
    # average resolution for trivial resolution model ~ sigma^6 * exp(- sigma / (7 * sigma_avg))
    # you get this trivial model if you pick a resolution model with per event
    # decay time error (PEDTE), but don't specify a decay time error distribution
    'DecayTimeResolutionAvg':           0.0352, # ps
    # None/DTAcceptanceLHCbNote2007041,Spline
    'AcceptanceFunction':               'None',
    # acceptance can really be made a histogram/spline interpolation
    'StaticAcceptance':         False,
    'AcceptanceInterpolation':  False,
    # spline acceptance parameters
    'AcceptanceSplineKnots':    [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
    'AcceptanceSplineCoeffs':   {
            # first index: DATA for data fits, MC for MC/toy fits
            'MC': {
                # second index: Bs2DsK or Bs2DsPi, depending on what the
                # signal mode is
                'Bs2DsPi':      [ 5.12341e-01, 7.44868e-01, 9.95795e-01, 1.13071e+00, 1.23135e+00, 1.22716e+00 ],
                'Bs2DsK':       [ 4.97708e-01, 7.42075e-01, 9.80824e-01, 1.16280e+00, 1.24252e+00, 1.28482e+00 ],
                # alternatively, you could have per-mode acceptances:
                # 'Bs2DsK': {
                #    'Bs2DsK': [ ... ],
                #    'Bs2DsPi': [ ... ],
                #    'Lb': [ ... ],
                # }
                },
            'DATA': {
                'Bs2DsPi':      [ 4.5853e-01, 6.8963e-01, 8.8528e-01, 1.1296e+00, 1.2232e+00, 1.2277e+00 ],
                'Bs2DsK':       [
                    4.5853e-01 * 4.97708e-01 / 5.12341e-01,
                    6.8963e-01 * 7.42075e-01 / 7.44868e-01,
                    8.8528e-01 * 9.80824e-01 / 9.95795e-01,
                    1.1296e+00 * 1.16280e+00 / 1.13071e+00,
                    1.2232e+00 * 1.24252e+00 / 1.23135e+00,
                    1.2277e+00 * 1.28482e+00 / 1.22716e+00
                    ],
                }
            },

    'PerEventMistag':           True,

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

    'TrivialMistag':            False,

    'UseKFactor':               True,

    # fitter settings
    'Optimize':                 1,
    'Strategy':                 2,
    'Offset':                   True,
    'Minimizer':                [ 'Minuit', 'migrad' ],
    'NumCPU':                   1,
    'ParameteriseIntegral':     True,
    'Debug':                    False,

    # list of constant parameters
    'constParams': [
            'Gammas', 'deltaGammas', 'deltaMs',
            'Gammad', 'deltaGammad', 'deltaMd',
            'mistag', 'timeerr_bias', 'timeerr_scalefactor',
            '.+_Mistag[0-9]+Calib(B|Bbar)_p[0-9]+'
            ],
    # dictionary of constrained parameters
    'Constraints': {
            # two possible formats:
            # - 'paramname': error
            #   the parameter's value is taken to be the central value, and a
            #   Gaussian constraint with that central value and the given
            #   error is applied
            # - 'formulaname': [ 'formula', [ 'par1', 'par2', ... ], mean, error ]
            #   construct a RooFormulaVar named formulaname with formula
            #   formula, giving the arguments in the list as constructor
            #   arguments; then use a Gaussian constraint to bring the value
            #   of that formula to mean with an uncertainty of error
            },

    # mass templates
    'MassTemplateFile':         os.environ['B2DXFITTERSROOT']+'/data/workspace/WS_Mass_DsK.root',
    'MassTemplateWorkspace':    'FitMeToolWS',
    'MassInterpolation':        False,
    # fudge the default template lookup order
    'MassTemplatePolaritySearch':       [ 'both' ],
    # either one element or 6 (kkpi,kpipi,pipipi)x(up,down) in "sample" order
    'NEvents':                  [ 1731. ],
    # target S/B: None means keep default
    'S/B': None,
    # mistag template
    'MistagTemplates':  {
            # general format:
            # 'mode1': [ { dict tagger 1 }, ..., { dict tagger N } ],
            # 'mode2': ...
            # where {dict tagger i} contains properties 'File', 'Workspace',
            # 'TemplateName', 'VarName'
            'Bs2DsK': [ { 
                    'File':             os.environ['B2DXFITTERSROOT']+'/data/workspace/work_toys_dsk.root',
                    'Workspace':        'workspace',
                    'TemplateName':     'PhysBkgBsDsPiPdf_m_down_kkpi_mistag',
                    'VarName':          'lab0_BsTaggingTool_TAGOMEGA_OS',
                } ]
            },
    'MistagInterpolation':      False,
    # decay time error template
    'DecayTimeErrorTemplates': {
            # general format:
            # 'mode1': { dict },
            # 'mode2': ...
            # where { dict } contains properties 'File', 'Workspace',
            # 'TemplateName', 'VarName'
            'Bs2DsK': {
                'File':         None,
                'Workspace':    None,
                'TemplateName': None,
                'VarName':      None,
                },
            },
    'DecayTimeErrInterpolation':        False,

    # k-factor templates
    'KFactorTemplates': {
            # general format:
            # 'mode1': { dict },
            # 'mode2': ...
            # where { dict } contains properties 'File', 'Workspace',
            # 'TemplateName', 'VarName'
            },

    # verify settings and sanitise where (usually) sensible
    'Sanitise':                 True,

    # fitter on speed: binned PDFs
    'NBinsAcceptance':          300,   # if >0, bin acceptance
    'NBinsTimeKFactor':         0,     # if >0, use binned cache for k-factor integ.
    'NBinsMistag':              50,    # if >0, parametrize Mistag integral
    'NBinsProperTimeErr':       100,   # if >0, parametrize proper time int.
    'NBinsMass':                200,   # if >0, bin mass templates

    # Data file settings
    'IsToy':                    True,
    'DataFileName':             None,
    'DataWorkSpaceName':        'workspace',
    'DataSetNames':             {
            'up_kkpi':          'dataSetBsDsK_up_kkpi',
            'up_kpipi':         'dataSetBsDsK_up_kpipi',
            'up_pipipi':        'dataSetBsDsK_up_pipipi',
            'down_kkpi':        'dataSetBsDsK_down_kkpi',
            'down_kpipi':       'dataSetBsDsK_down_kpipi',
            'down_pipipi':      'dataSetBsDsK_down_pipipi'
            },
    'DataSetCuts': None,                # cut string or None
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
            #'RooFitTopSimultaneousWorkaround',
            # this will work around a problem in present RooFit versions which
            # produce different LH values if the top-level PDF is a
            # RooSimultaneous
            ],
    }

#------------------------------------------------------------------------------

from B2DXFitters.WS import WS
from B2DXFitters.utils import setConstantIfSoConfigured, printPDFTermsOnDataSet
from B2DXFitters.datasetio import readDataSet, writeDataSet, readTemplate1D
from B2DXFitters.acceptanceutils import buildSplineAcceptance
from B2DXFitters.resmodelutils import getResolutionModel
from B2DXFitters.timepdfutils import buildBDecayTimePdf
from B2DXFitters.taggingutils import (fitPolynomialAnalytically,
        getMistagBinBounds, getTrueOmegasPerCat, getEtaPerCat)

def getAcceptance(
        ws,
        config,
        mode,
        time):
    if (None == config['AcceptanceFunction'] or 'None' ==
            config['AcceptanceFunction']):
        # no acceptance function
        return None
    if 'Spline' == config['AcceptanceFunction']:
        # ok, spline based acceptance function
        kind = 'MC' if config['IsToy'] else 'DATA'
        knots = config['AcceptanceSplineKnots']
        coeffs = config['AcceptanceSplineCoeffs'][kind][config['Modes'][0]]
        if type(coeffs) == list or type(coeffs) == tuple:
            # same acceptance for all modes
            tacc, tacc_norm = buildSplineAcceptance(ws, time,
                    config['Modes'][0], knots, coeffs)
        elif type(coeffs) == dict:
            mymode = mode
            if (mymode not in coeffs):
                mymode = mode[0:2]
            if (mymode not in coeffs):
                mymode = config['Modes'][0]
            if (mymode not in coeffs):
                raise ValueError('Unable to find spline acceptance '
                        'coefficients for mode %s' % mode)
            tacc, tacc_norm = buildSplineAcceptance(ws, time, mymode, knots,
                    coeffs[mymode])
        else:
            raise TypeError('Spline acceptance coefficients have invalid type')
    else:
        raise TypeError('ERROR: unknown acceptance function: %s' %
                config['AcceptanceFunction'])
    if (0 < config['NBinsAcceptance'] and
            'Spline' != config['AcceptanceFunction']):
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
        tacc_norm = tacc
    return (tacc if 'GEN' not in config['Context'] else tacc_norm)

# read mistag distribution from file
def getMistagTemplate(
    config,     # configuration dictionary
    ws,         # workspace to import into
    mistag,     # mistag variable
    mode,       # mode to look up
    taggernr = 0 # number of tagger
    ):
    # find the entry we're interested in
    if mode not in config['MistagTemplates']:
        modenicks = {
                'Bd2DK': 'Bd2DPi',
                'Bd2DsK': 'Bd2DPi',
                'Lb2LcK': 'Bd2DPi',
                'Lb2Dsp': 'Bd2DPi',
                'Lb2Dsstp': 'Bd2DPi',
                'Lb2LcPi': 'Bd2DPi',
                }
        if mode in modenicks:
            mode = modenicks[mode]
        else:
            mode = config['Modes'][0]
    tmp = config['MistagTemplates'][mode][taggernr]
    return readTemplate1D(tmp['File'], tmp['Workspace'], tmp['VarName'],
            tmp['TemplateName'], ws, mistag, '%s_Mistag_%u_PDF' % (
                mode, taggernr))

# read decay time error distribution from file
def getDecayTimeErrorTemplate(
    config,     # configuration dictionary
    ws,         # workspace to import into
    timeerr,    # timeerr variable
    mode        # mode to look up
    ):
    # find the entry we're interested in
    if mode not in config['DecayTimeErrorTemplates']:
        modenicks = {
                }
        if mode in modenicks:
            mode = modenicks[mode]
        else:
            mode = config['Modes'][0]
    tmp = config['DecayTimeErrorTemplates'][mode]
    return readTemplate1D(tmp['File'], tmp['Workspace'], tmp['VarName'],
            tmp['TemplateName'], ws, timeerr, '%s_TimeErr_PDF' % (mode))

# load k-factor templates for all modes
def getKFactorTemplates(
    config,     # configuration dictionary
    ws,         # workspace to import into
    k   # k factor variable
    ):
    templates = {}
    for mode in config['Modes']:
        tmp = (config['KFactorTemplates'][mode] if mode in
                config['KFactorTemplates'] else None)
        if None == tmp:
            templates[mode] = (None, None)
            continue
        kcopy = WS(ws, k.clone('%s_%s' % (mode, k.GetName())))
        templates[mode] = (readTemplate1D(tmp['File'], tmp['Workspace'],
            tmp['VarName'], tmp['TemplateName'], ws, kcopy,
            '%s_kFactor_PDF' % (mode)), kcopy)
    return templates

# obtain mass template from mass fitter (2011 CONF note version)
#
# we use the very useful workspace dump produced by the mass fitter to obtain
# the pdf and yields
#
# returns a dictionary with a pair { 'pdf': pdf, 'yield': yield }
def getMassTemplateOneMode2011Conf(
    config,             # configuration dictionary
    ws,                 # workspace into which to import templates
    mass,               # mass variable
    mode,               # decay mode to load
    sname,              # sample name
    dsmass = None,      # ds mass variable
    pidk = None         # pidk variable
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
    config,             # configuration dictionary
    ws,                 # workspace into which to import templates
    mass,               # mass variable
    mode,               # decay mode to load
    sname,              # sample name
    dsmass = None,      # ds mass variable
    pidk = None         # pidk variable
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
    for polsearch in config['MassTemplatePolaritySearch']:
        if mode == config['Modes'][0]:
            pdf = fromws.pdf('SigProdPDF_%s_%s' % (polsearch, sname))
            nYield = fromws.var('nSig_%s_%s_Evts' % (polsearch, sname))
            if None != nYield: nYield = nYield.getVal()
        elif mode == 'CombBkg':
            pdf = fromws.pdf('CombBkgPDF_m_%s_%s_Tot' % (polsearch, sname))
            if None == pdf:
                pdf = fromws.pdf('PhysBkgCombBkgPdf_m_%s_%s_Tot' % (polsearch, sname))
            nYield = fromws.var('nCombBkg_%s_%s_Evts' % (polsearch, sname))
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
                '%sPdf_m_%s_%s_Tot' % (mode, polsearch, sname),
                '%sPdf_m_%s_Tot' % (mode, polsearch),
                '%sPdf_m_%s_%s_Tot' % (modemap[mode], polsearch, sname),
                '%sPdf_m_%s_Tot' % (modemap[mode], polsearch),
                # "modeless" names for single-mode DsPi toys (only in DsK, I
                # think, but we need the fallback solution at least once)
                '%sPdf_m_%s_%s_Tot' % (mode, polsearch, ''),
                '%sPdf_m_%s_%s_Tot' % (modemap[mode], polsearch, ''),
                ]
            for sfx in trysfx:
                pdf = fromws.pdf('PhysBkg%s' % sfx)
                if None != pdf:
                    break
            tryyieldsfx = [
                'n%s_%s_%s_Evts' % (mode, polsearch, sname),
                'n%s_%s_%s_Evts' % (mode.replace('Dsst', 'Dss'), polsearch, sname),
                'n%s_%s_%s_Evts' % (mode.replace('DsstP', 'Dsstp'), polsearch, sname),
                'n%s_%s_%s_Evts' % (mode.replace('DsstPi', 'DsstPiRho'), polsearch, sname),
                'n%s_%s_%s_Evts' % (modemap[mode], polsearch, sname),
                'n%s_%s_%s_Evts' % (modemap[mode].replace('Dsst', 'Dss'), polsearch, sname),
                'n%s_%s_%s_Evts' % (modemap[mode].replace('DsstP', 'Dsstp'), polsearch, sname),
                'n%s_%s_%s_Evts' % (modemap[mode].replace('DsstPi', 'DsstPiRho'), polsearch, sname),
                ]
            for sfx in tryyieldsfx:
                nYield = fromws.var(sfx)
                if None != nYield:
                    nYield = nYield.getVal()
                    break
            if None == nYield and None == pdf: continue
            if None == nYield and mode in ('Bd2DK', 'Bd2DPi', 'Lb2LcK',
                    'Lb2LcPi'):
                # Agnieszka's yield-removal for modes that were not found
                nYield = 0.
            if tryyieldsfx[0] != sfx and tryyieldsfx[1] != sfx and 0. != nYield:
                # ok, we're in one of the modes which have a shared yield and a
                # fraction, so get the fraction, and fix up the yield 
                if 'Bs2DsDsstKKst' in sfx or 'Bs2DsDssKKst' in sfx:
                    f = fromws.var('g1_f1_frac')
                    if 'Bd2DsK' == mode:
                        f = f.getVal() if None != f else 1.
                    elif 'Bs2DsKst' == mode: 
                        f = (1. - f.getVal()) if None != f else 0.
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
                nYield = (nYield * f) if (0. != f) else 0.
        if None != pdf and None != nYield: break
    # ok, we should have all we need for now
    if None == pdf or None == nYield:
        if None == pdf and 0. != nYield:
            print '@@@@ - ERROR: NO PDF FOR MODE %s SAMPLE CATEGORY %s' % (
                    mode, sname)
            return None
        if None == nYield and 0. != nYield:
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
    else:
        if 0. == nYield:
            nYield = RooRealVar('n%s_%s_Evts' % (mode, sname),
                    'n%s_%s_Evts' % (mode, sname), 0.)
    # import mass pdf and corresponding yield into our workspace
    # in the way, we rename whatever mass variable was used to the one supplied
    # by our caller
    nYield = WS(ws, nYield, [
        RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
        RooFit.Silence()])
    if 0. != nYield.getVal():
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
    else:
        # yield is zero, so put a dummy pdf there
        from ROOT import RooUniform
        pdf = RooUniform('DummyPdf_m_both_Tot', 'DummyPdf_m_both_Tot',
                RooArgSet(mass, dsmass, pidk))
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
    config,             # configuration dictionary
    ws,                 # wksp into which to import templates
    mass,               # mass variable
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
            '2011PaperDsK-Agn116': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn140': getMassTemplateOneMode2011Paper,
            '2011PaperDsPi-Agn70': getMassTemplateOneMode2011Paper,
            '2011PaperDsKDATA-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsPiDATA-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn70-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn140-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsPi-Agn70-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-MC': getMassTemplateOneMode2011Paper,
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
        effs = []
        tmpeffs = None
        for k in (modename, modename[0:2], config['Modes'][0]):
            if k in config['TagEff']:
                tmpeffs = config['TagEff'][k]
                break
        if None == tmpeffs: return None
        if len(tmpeffs) == config['NTaggers']:
            # independent effs for all taggers
            for i in xrange(0, config['NTaggers']):
                eff = WS(ws, RooRealVar(
                    '%s_TagEff%u' % (modename, i), '%s_TagEff%u' % (modename, i),
                    tmpeffs[i], 0., 1.))
                if (1. < yieldhint):
                    err = sqrt(tmpeffs[i]*(1. - tmpeffs[i]) / yieldhint)
                else:
                    err = sqrt(1. / yieldhint)
                eff.setError(err)
                effs.append(eff)
        elif (2 == len(tmpeffs) and 3 == config['NTaggers']):
            # two taggers, assume P(tag1) * P(tag2) == P(tag1, tag2)
            for i in xrange(0, 2):
                eff = WS(ws, RooRealVar(
                    '%s_TagEff%u_tot' % (modename, i),
                    '%s_TagEff%u_tot' % (modename, i),
                    tmpeffs[i], 0., 1.))
                if (1. < yieldhint):
                    err = sqrt(tmpeffs[i]*(1. - tmpeffs[i]) / yieldhint)
                else:
                    err = sqrt(1. / yieldhint)
                eff.setError(err)
                effs.append(eff)
            tmpeffs = effs
            # put together the three tag effs. to be used
            one = ws.obj('one')
            minusone = ws.obj('minusone')
            effs = [ None, None, None ]
            from ROOT import RooProduct, RooAddition
            effs[2] = WS(ws, RooProduct('%s_TagEff%u' % (modename, 2),
                '%s_TagEff%u' % (modename, 2),
                RooArgList(tmpeffs[0], tmpeffs[1])))
            effs[0] = WS(ws, RooAddition('%s_TagEff%u' % (modename, 0),
                '%s_TagEff%u' % (modename, 0),
                RooArgList(tmpeffs[0], effs[2]),
                RooArgList(one, minusone)))
            effs[1] = WS(ws, RooAddition('%s_TagEff%u' % (modename, 1),
                '%s_TagEff%u' % (modename, 1),
                RooArgList(tmpeffs[1], effs[2]),
                RooArgList(one, minusone)))
        else:
            return None
        return effs
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
        RooSimultaneous, RangeAcceptance, RooEffProd,
        RooAddition, RooProduct, Inverse, SquaredSum, CPObservable,
        MistagCalibration)
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
        config['NBinsTimeKFactor'] = 0
        config['MistagInterpolation'] = False
        config['MassInterpolation'] = False
        config['DecayTimeErrInterpolation'] = False
        config['AcceptanceCorrectionInterpolation'] = False
        config['CombineModesForEffCPObs'] = [ ]
        config['ParameteriseIntegral'] = False
    if 'Spline' == config['AcceptanceFunction']:
        config['NBinsAcceptance'] = 0
    print '########################################################################'
    print '%s config:' % name
    print
    for k in sorted(config.keys()):
        print '%-32s: %s' % (k, str(config[k]))
    print '########################################################################'
    ws = RooWorkspace('WS_%s' % name)

    zero = WS(ws, RooConstVar('zero', '0', 0.))
    one = WS(ws, RooConstVar('one', '1', 1.))
    minusone = WS(ws, RooConstVar('minusone', '-1', -1.))

    # create weight variable, if we need one
    if config['FitMode'] in ('cFitWithWeights', 'sFit'):
        weight = WS(ws, RooRealVar('weight', 'weight',
            -sys.float_info.max, sys.float_info.max))
    else:
        weight = None
    # figure out lower bound of fit range
    timelo = config['FitRanges']['time'][0]
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

    kvar = WS(ws, RooRealVar('kvar', 'k factor', 1., 0.66, 1.33))
    kvar.setConstant(True)

    deltaMs = WS(ws, RooRealVar('deltaMs', '#Delta m_{s}',
        config['DeltaMs'], 5., 30., 'ps^{-1}'))

    # tagging
    # -------
    mistag = WS(ws, RooRealVar('mistag', 'mistag observable',
        config['TagOmegaSig'], config['FitRanges']['mistag'][0],
        config['FitRanges']['mistag'][1]))

    qt = WS(ws, RooCategory('qt', 'flavour tagging result'))
    for idx in xrange(-config['NTaggers'], config['NTaggers'] + 1):
        if (idx < 0):
            label = 'Bbar_%u' % abs(idx)
        elif (idx > 0):
            label = 'B_%u' % abs(idx)
        else:
            label = 'Untagged'
        qt.defineType(label, idx)
    del label
    del idx

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

    mistagCals = { }
    for realmode in config['Modes']:
        mode = realmode
        for m in (realmode, realmode[0:2], config['Modes'][0]):
            if m in config['MistagCalibrationParams']:
                mode = m
                break
        mistagCal = []
        for itagger in xrange(0, config['NTaggers']):
            if config['PerEventMistag']:
                lmistagCal = []
                namsfx = [ 'B', 'Bbar' ]
                conf = config['MistagCalibrationParams'][mode][itagger]
                if len(conf) > 2:
                    raise NameError(('MistagCalibrationParams configurable'
                        ' slot %s/%u must not have more than two entries'
                        ' (B, Bbar)!') % (mode, itagger))
                for j in xrange(0, len(conf)):
                    if len(conf[j]) != 2 and len(conf[j]) != 3:
                        raise NameError(('MistagCalibrationParams configurable'
                            ' slot %s/%u: calibration %u must be an array of '
                            'length 2 or 3!') % (mode, itagger, j))
                    mistagcalib = RooArgList()
                    avgmistag = zero
                    if len(conf[j]) == 2 or len(conf[j]) == 3:
                        i = 0
                        for p in conf[j][0:2]:
                            v = WS(ws, RooRealVar(
                                '%s_Mistag%uCalib%s_p%u' % (mode, itagger, namsfx[j], i),
                                '%s_Mistag%uCalib%s_p%u' % (mode, itagger, namsfx[j], i),
                                p, 0., 0.5 if 0 == i else 2.0))
                            v.setConstant(False)
                            mistagcalib.add(v)
                            i = i + 1
                        del i
                    if len(conf[j]) == 3:
                        avgmistag = WS(ws, RooRealVar(
                            '%s_Mistag%uCalib%s_avgmistag' % (mode, itagger, namsfx[j]),
                            '%s_Mistag%uCalib%s_avgmistag' % (mode, itagger, namsfx[j]),
                            conf[j][2]))
                    lmistagCal.append(WS(ws, MistagCalibration(
                        '%s_%s%u%s_c' % (mode, mistag.GetName(), itagger, namsfx[j]),
                        '%s_%s%u%s_c' % (mode, mistag.GetName(), itagger, namsfx[j]),
                        mistag, mistagcalib, avgmistag)))
                    del mistagcalib
                    del avgmistag
                del namsfx
                mistagCal.append(lmistagCal)
            else:
                mistagCal.append([ mistag ])
        mistagCals[realmode] = mistagCal
        del mistagCal
    # read in templates
    if config['PerEventMistag']:
        observables.append(mistag)
        mistagtemplates = { }
        if not config['TrivialMistag']:
            for mode in config['Modes']:
                mistagtemplates[mode] = [
                        getMistagTemplate(config, ws, mistag, mode, i) for i in
                        xrange(0, config['NTaggers']) ]
                if None in mistagtemplates[mode]:
                    raise ValueErrror('ERROR: Unable to get mistag template(s)'
                            ' for mode %s' % mode)
        else:
            from ROOT import MistagDistribution
            omega0 = WS(ws, RooConstVar('omega0', 'omega0', 0.07))
            omegaf = WS(ws, RooConstVar('omegaf', 'omegaf', 0.25))
            omegaa = WS(ws, RooConstVar('omegaa', 'omegaa', config['TagOmegaSig']))
            trivialMistagPDF = [ WS(ws, MistagDistribution(
                'TrivialMistagPDF', 'TrivialMistagPDF',
                mistag, omega0, omegaa, omegaf)) ]
            for mode in config['Modes']:
                mistagtemplates[mode] = [ trivialMistagPDF for i in
                        xrange(0, config['NTaggers']) ]
                if 1 == config['NTaggers']:
                    mistagtemplates[mode] = mistagtemplates[mode][0]
    else:
        mistagtemplates = { }
        for mode in config['Modes']:
            mistagtemplates[mode] = None

    if config['UseKFactor']:
        ktemplates = getKFactorTemplates(config, ws, kvar)
    else:
        ktemplates = { }
    masstemplates = getMassTemplates(config, ws, mass, dsmass, pidk)

    # ok, since the mistagtemplate often is a RooHistPdf, we can fine-tune
    # ranges and binning to match the histogram
    if config['PerEventMistag'] and not config['TrivialMistag']:
        for mode in mistagtemplates:
            newmistagtemplate = []
            for mtt in mistagtemplates[mode]:
                if not mtt.InheritsFrom('RooHistPdf'):
                    newmistagtemplate.append(mtt)
                    continue
                hist = mtt.dataHist().createHistogram(mistag.GetName())
                ROOT.SetOwnership(hist, True)
                ax = hist.GetXaxis()
                nbins = hist.GetNbinsX()
                print 'INFO: adjusting range of %s to histogram ' \
                        'used in %s: %g to %g, was %g to %g' % \
                        (mistag.GetName(), mtt.GetName(),
                                ax.GetBinLowEdge(1), ax.GetBinUpEdge(nbins),
                                mistag.getMin(), mistag.getMax())
                mistag.setRange(ax.GetBinLowEdge(1), ax.GetBinUpEdge(nbins))
                if config['MistagInterpolation']:
                    # protect against "negative events" in sWeighted source
                    # histos
                    for i in xrange(0, nbins):
                        if hist.GetBinContent(1 + i) < 0.:
                            print "%%% WARNING: mistag template %s has "\
                                    "negative entry in bin %u: %g" % (
                                            mtt.GetName(), 1 + i,
                                            hist.GetBinContent(1 + i))
                            hist.SetBinContent(1 + i, 0.)
                    del i
                    from ROOT import RooBinned1DQuinticBase, RooAbsPdf
                    RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
                    mtt = WS(ws, RooBinned1DQuinticPdf(
                        '%s_interpol' % mtt.GetName(),
                        '%s_interpol' % mtt.GetName(),
                        hist, mistag, True))
                del ax
                del hist
                if config['NBinsMistag'] > 0 and nbins < config['NBinsMistag']:
                    print 'INFO: adjusting binning of %s to histogram ' \
                            'used in %s: %u bins, was %u bins' % \
                            (mistag.GetName(), mtt.GetName(),
                                    nbins, config['NBinsMistag'])
                    config['NBinsMistag'] = nbins
                    del nbins
                newmistagtemplate.append(mtt)
            mistagtemplates[mode] = newmistagtemplate

    # OK, get the show on the road if we are using mistag categories
    if None != config['NMistagCategories']: 
        if config['NMistagCategories'] > 0 and config['PerEventMistag']:
            if 1 != config['NTaggers']:
                print ('ERROR: Mistag calibration fits in categories only'
                        'supported for a single tagger!')
                return None
        # ok, we have to provide the machinery to convert per-event mistag to
        # mistag categories
        if None != config['MistagCategoryBinBounds']:
            if (len(config['MistagCategoryBinBounds']) != 1 +
                    config['NMistagCategories']):
                print ('ERROR: %d mistag categories requested, number of bin '
                        'bounds does not match' % config['NMistagCategories'])
                return None
        else:
            # ok, auto-tune mistag category bin bounds from mistag pdf template
            if None == mistagtemplates[config['Modes'][0]][0]:
                print ('ERROR: No mistag category bounds present, and no '
                        'mistag pdf template to tune from!')
                return None
            # all fine
            config['MistagCategoryBinBounds'] = getMistagBinBounds(
                    config, mistag, mistagtemplates[config['Modes'][0]][0])
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
            for cal in mistagCals[config['Modes'][0]][0]:
                getTrueOmegasPerCat(config, mistag, cal,
                        mistagtemplates[config['Modes'][0]][0])
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
        mistagCals = {}
        for mode in config['Modes']:
            mistagCals[mode] = [ [ mistag ] ]
        del omegas
        observables.append(tagcat)

    timepdfs = { }
 
    # Decay time error distribution
    # -----------------------------
    if 'PEDTE' in config['DecayTimeResolutionModel']:
        # decay time error is extra observable!
        observables.append(timeerr)
        if (None != config['DecayTimeErrorTemplates'] and
                len(config['DecayTimeErrorTemplates']) > 0):
            terrpdfs = { }
            for mode in config['Modes']:
                 terrpdfs[mode] = getDecayTimeErrorTemplate(
                         config, ws, timeerr, mode)
                 if None == terrpdfs[mode]:
                     print ('ERROR: Unable to get decay time error template'
                             ' for mode %s') % mode
                     return None
        else:
            print "WARNING: Using trivial decay time error PDF"
            # resolution in ps: 7*terrpdf_shape
            terrpdf_shape = WS(ws, RooConstVar('terrpdf_shape', 'terrpdf_shape',
                config['DecayTimeResolutionAvg'] / 7.))
            terrpdf_truth = WS(ws, RooTruthModel('terrpdf_truth', 'terrpdf_truth', timeerr))
            terrpdf_i0 = WS(ws, RooDecay('terrpdf_i0', 'terrpdf_i0', timeerr, terrpdf_shape,
                terrpdf_truth, RooDecay.SingleSided))
            terrpdf_i1 = WS(ws, RooPolynomial('terrpdf_i1','terrpdf_i1',
                timeerr, RooArgList(zero, zero, zero, zero, zero, zero, one), 0))
            terrpdf = WS(ws, RooProdPdf('terrpdf', 'terrpdf', terrpdf_i0, terrpdf_i1))
            terrpdfs = { }
            for mode in config['Modes']:
                terrpdfs[mode] = terrpdf
        if config['DecayTimeErrInterpolation']:
            from ROOT import RooBinned1DQuinticBase, RooAbsPdf
            RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
            obins = timeerr.getBins()
            nbins = config['NBinsProperTimeErr']
            if 0 == nbins:
                print 'ERROR: requested binned interpolation of timeerr %s %d %s' % (
                        'histograms with ', nbins, ' bins - increasing to 100 bins')
                nbins = 100
            for mode in config['Modes']:
                terrpdf = terrpdfs[mode]
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
                terrpdfs[mode] = terrpdf
            timeerr.setBins(obins)
            del obins
            del nbins
    else:
        terrpdfs = { }
        for mode in config['Modes']:
            terrpdfs[mode] = None
    
    # produce a pretty-printed yield dump in the signal region
    yielddict = {}
    totyielddict = { }
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
        tacc = getAcceptance(ws, config, mode, time)
        trm, tacc = getResolutionModel(ws, config, time, timeerr, tacc)
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
                    if type(config['Asymmetries'][k][n]) == float:
                        asyms[k] = WS(ws, RooRealVar(
                            '%s_Asym%s' % (n, k), '%s_Asym%s' % (n, k),
                            config['Asymmetries'][k][n], -1., 1.))
                        asyms[k].setError(0.25)
                    elif (type(config['Asymmetries'][k][n]) == list and
                            'TagEff' == k):
                        if (len(config['Asymmetries'][k][n]) !=
                                config['NTaggers']):
                            raise TypeError('Wrong number of asymmetries')
                        asyms[k] = [ ]
                        for asymval in config['Asymmetries'][k][n]:
                            asymstmp = WS(ws, RooRealVar(
                                '%s_Asym%s%u' % (n, k, len(asyms[k])),
                                '%s_Asym%s%u' % (n, k, len(asyms[k])),
                                asymval, -1., 1.))
                            asymstmp.setError(0.25)
                            asyms[k].append(asymstmp)
                            del asymstmp
                    else:
                        raise TypeError('Unsupported type for asymmetry')
                    break
        if (config['UseKFactor'] and config['Modes'][0] != mode and mode in
                ktemplates and (None, None) != ktemplates[mode]):
            kfactorpdf, kfactor = ktemplates[mode][0], ktemplates[mode][1]
        else:
            kfactorpdf, kfactor = None, None
        y = 0.
        for lmode in yielddict:
            if lmode.startswith(modenick): y += yielddict[lmode]
        y = max(y, 1.)
        tageff = makeTagEff(config, ws, modenick, y)
        if mode.startswith('Bs'):
            gamma, deltagamma, deltam = gammas, deltaGammas, deltaMs
        elif mode.startswith('Bd'):
            gamma, deltagamma, deltam = gammad, deltaGammad, deltaMd
        else:
            gamma, deltagamma, deltam = None, None, None
        timepdfs[mode] = buildBDecayTimePdf(myconfig, mode, ws,
                time, timeerr, qt, qf, mistagCals[mode], tageff,
                gamma, deltagamma, deltam, C, D, Dbar, S, Sbar,
                trm, tacc, terrpdfs[mode], mistagtemplates[mode],
                mistag, kfactorpdf, kfactor,
                asyms['Prod'], asyms['Det'], asyms['TagEff'])

    ########################################################################
    # Bs -> Ds Pi like modes, and Lb/CombBkg modes (non-oscillating)
    ########################################################################
    ComboLifetimePerTagCat = False
    for mode in ( 'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bs2DsstRho',
            'Bd2DsK', 'Bd2DK', 'Bd2DsPi',
            'Lb2Dsp', 'Lb2Dsstp', 'Lb2LcK', 'Lb2LcPi',
            'CombBkg'):
        if mode not in config['Modes']:
            continue
        if ('CombBkg' == mode and (
            type(config['GammaCombBkg']) != float or
            type(config['DGammaCombBkg']) != float or
            type(config['CombBkg_D']) != float)):
            # need special treatment for combinatorial BG - array of
            # lifetimes, one per tagging category
            ComboLifetimePerTagCat = True
            continue
        tacc = getAcceptance(ws, config, mode, time)
        trm, tacc = getResolutionModel(ws, config, time, timeerr, tacc)
        if mode.startswith('Bs'):
            gamma, deltagamma, deltam = gammas, deltaGammas, deltaMs
            modenick = 'Bs2DsPi'
            C, D = one, zero
        elif mode.startswith('Bd'):
            gamma, deltagamma, deltam = gammad, deltaGammad, deltaMd
            modenick = 'Bd2DsK'
            C, D = one, zero
        elif mode.startswith('Lb'):
            gamma = WS(ws, RooRealVar('GammaLb', '#Gamma_{#Lambda_{b}}',
                config['GammaLb']))
            deltagamma, deltam = zero, zero
            modenick = 'Lb'
            C, D = zero, zero
        elif mode == 'CombBkg':
            gamma = WS(ws, RooRealVar('GammaCombBkg', '#Gamma_{CombBkg}}',
                config['GammaCombBkg']))
            dGamma = WS(ws, RooRealVar('DeltaGammaCombBkg', '#Delta#Gamma_{CombBkg}}',
                config['DGammaCombBkg']))
            D = WS(ws, RooRealVar('CombBkg_D', 'CombBkg_D', config['CombBkg_D']))
            deltam = zero
            modenick = mode
            C = zero
        else:
            gamma, deltagamma, deltam = None, None, None
            modenick = mode
            C, D = zero, zero
        # figure out asymmetries to use
        asyms = { 'Prod': None, 'Det': None, 'TagEff': None }
        for k in asyms.keys():
            for n in (mode, modenick, mode.split('2')[0]):
                if n in config['Asymmetries'][k]:
                    if type(config['Asymmetries'][k][n]) == float:
                        asyms[k] = WS(ws, RooRealVar(
                            '%s_Asym%s' % (n, k), '%s_Asym%s' % (n, k),
                            config['Asymmetries'][k][n], -1., 1.))
                        asyms[k].setError(0.25)
                    elif (type(config['Asymmetries'][k][n]) == list and
                            'TagEff' == k):
                        if (len(config['Asymmetries'][k][n]) !=
                                config['NTaggers']):
                            raise TypeError('Wrong number of asymmetries')
                        asyms[k] = [ ]
                        for asymval in config['Asymmetries'][k][n]:
                            asymstmp = WS(ws, RooRealVar(
                                '%s_Asym%s%u' % (n, k, len(asyms[k])),
                                '%s_Asym%s%u' % (n, k, len(asyms[k])),
                                asymval, -1., 1.))
                            asymstmp.setError(0.25)
                            asyms[k].append(asymstmp)
                            del asymstmp
                    else:
                        raise TypeError('Unsupported type for asymmetry')
                    break
        # Bd2DsK does not need k-factor (delta(k))
        if (config['UseKFactor'] and config['Modes'][0] != mode and mode in
                ktemplates and (None, None) != ktemplates[mode]):
            kfactorpdf, kfactor = ktemplates[mode][0], ktemplates[mode][1]
        else:
            kfactorpdf, kfactor = None, None
        y = 0.
        for lmode in yielddict:
            if lmode.startswith(modenick): y += yielddict[lmode]
        y = max(y, 1.)
        tageff = makeTagEff(config, ws, modenick, y)
        timepdfs[mode] = buildBDecayTimePdf(config, mode, ws,
                time, timeerr, qt, qf, mistagCals[mode], tageff,
                gamma, deltagamma, deltam, C, D, D, zero, zero,
                trm, tacc, terrpdfs[mode], mistagtemplates[mode],
                mistag, kfactorpdf, kfactor,
                asyms['Prod'], asyms['Det'], asyms['TagEff'])
    ########################################################################
    # special treatment: CombBkg with lifetime per tagging category
    ########################################################################
    if ComboLifetimePerTagCat:
        if type(config['GammaCombBkg']) not in (list, tuple):
            raise TypeError('Wrong type for GammaCombBkg in config dict')
        if type(config['DGammaCombBkg']) not in (list, tuple):
            raise TypeError('Wrong type for DGammaCombBkg in config dict')
        if type(config['CombBkg_D']) not in (list, tuple):
            raise TypeError('Wrong type for CombBkg_D in config dict')
        if (len(config['GammaCombBkg']) != len(config['DGammaCombBkg']) or
                len(config['GammaCombBkg']) != len(config['CombBkg_D']) or
                len(config['GammaCombBkg']) != 1 + config['NTaggers']):
            raise ValueError('CombBkg lifetime parameter list(s) have wrong '
                    'length.')
        mode = 'CombBkg'
        tacc = getAcceptance(ws, config, mode, time)
        trm, tacc = getResolutionModel(ws, config, time, timeerr, tacc)
        deltam = zero
        modenick = mode
        C = zero
        # figure out asymmetries to use
        asyms = { 'Prod': None, 'Det': None, 'TagEff': None }
        for k in asyms.keys():
            for n in (mode, modenick, mode.split('2')[0]):
                if n in config['Asymmetries'][k]:
                    if type(config['Asymmetries'][k][n]) == float:
                        asyms[k] = WS(ws, RooRealVar(
                            '%s_Asym%s' % (n, k), '%s_Asym%s' % (n, k),
                            config['Asymmetries'][k][n], -1., 1.))
                        asyms[k].setError(0.25)
                    elif (type(config['Asymmetries'][k][n]) == list and
                            'TagEff' == k):
                        if (len(config['Asymmetries'][k][n]) !=
                                config['NTaggers']):
                            raise TypeError('Wrong number of asymmetries')
                        asyms[k] = [ ]
                        for asymval in config['Asymmetries'][k][n]:
                            asymstmp = WS(ws, RooRealVar(
                                '%s_Asym%s%u' % (n, k, len(asyms[k])),
                                '%s_Asym%s%u' % (n, k, len(asyms[k])),
                                asymval, -1., 1.))
                            asymstmp.setError(0.25)
                            asyms[k].append(asymstmp)
                            del asymstmp
                    else:
                        raise TypeError('Unsupported type for asymmetry')
                    break
        # CombBkg does not need k-factor (delta(k))
        kfactorpdf, kfactor = None, None
        y = 0.
        for lmode in yielddict:
            if lmode.startswith(modenick): y += yielddict[lmode]
        y = max(y, 1.)
        tageff = makeTagEff(config, ws, modenick, y)
        
        gammacombpdfs = [ ]
        for i in xrange(0, 1 + config['NTaggers']):
            gamma = WS(ws, RooRealVar('GammaCombBkg%u' % i,
                '#Gamma_{CombBkg%u}}' % i, config['GammaCombBkg'][i]))
            deltagamma = WS(ws, RooRealVar('DeltaGammaCombBkg%u' % i,
                '#Delta#Gamma_{CombBkg%u}}' %i, config['DGammaCombBkg'][i]))
            D = WS(ws, RooRealVar('CombBkg%u_D' % i, 'CombBkg%u_D' % i,
                config['CombBkg_D'][i]))
            tmptageff = [ (one if i == j else zero) for j in xrange(
                1, 1 + config['NTaggers']) ]
            gammacombpdfs.append(
                    buildBDecayTimePdf(config, '%s%u' % (mode, i), ws,
                    time, timeerr, qt, qf, mistagCals[mode], tmptageff,
                    gamma, deltagamma, deltam, C, D, D, zero, zero,
                    trm, tacc, terrpdfs[mode], mistagtemplates[mode],
                    mistag, kfactorpdf, kfactor,
                    asyms['Prod'], asyms['Det'], asyms['TagEff']))
            del tmptageff
        gammacombpdfs.append(gammacombpdfs[0])
        gammacombpdfs.pop(0)
        tmp0, tmp1 = RooArgList(), RooArgList()
        for v in gammacombpdfs: tmp0.add(v)
        for v in tageff: tmp1.add(v)
        del gammacombpdfs
        timepdfs[mode] = WS(ws, RooAddPdf('%s_TimePdf' % mode,
            '%s_TimePdf' % mode, tmp0, tmp1))
        del tmp0
        del tmp1

    obs = RooArgSet('observables')
    for o in observables:
        obs.add(WS(ws, o))
    condobs = RooArgSet('condobservables')
    for o in condobservables:
        condobs.add(WS(ws, o))
    
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
            tpdf = timepdfs[mode]
            mpdf = masstemplates[mode][sname]
            if not mode in components:
                components[mode] = [ ]
            # skip zero yield components
            if (mpdf['yield'].getVal() < 1e-3 and
                    mpdf['yield'].isConstant()):
                # if it doesn't have a yield, we might as well skip this
                # component
                continue
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
            if (mpdf['yield'].getVal() < 1e-3 and
                    mpdf['yield'].isConstant()):
                continue
            f = WS(ws, RooProduct(
                'f_%s_%s' % (mode, sname), 'f_%s_%s' % (mode, sname),
                RooArgList(mpdf['yield'], itotyield)))
            fractions.add(f)
        # remove the last fraction added, so RooFit recognises that we
        # want a normal PDF from RooAddPdf, not an extended one
        if 0 > fractions.getSize(): fractions.remove(f)
        # add all pdfs contributing yield in this sample category
        totEPDF.addPdf(WS(ws, RooAddPdf(
            '%s_EPDF' % sname, '%s_EPDF' % sname, pdfs, yields)), sname)
        totPDF.addPdf(WS(ws, RooAddPdf(
            '%s_PDF' % sname, '%s_PDF' % sname, pdfs, fractions)), sname)
    # report which modes got selected
    for mode in config['Modes']:
        print 'INFO: Mode %s components %s' % (mode, str(components[mode]))
    if '_unfixed' in totPDF.GetName():
        totPDF = WS(ws, RooProdPdf('TotPDF', 'TotPDF', RooArgList(totPDF)))
    if '_unfixed' in totEPDF.GetName():
        totEPDF = WS(ws, RooProdPdf('TotEPDF', 'TotEPDF', RooArgList(totEPDF)))
    # set variables constant if they are supposed to be constant
    setConstantIfSoConfigured(config, totEPDF)
    # apply any additional constraints
    from B2DXFitters.GaussianConstraintBuilder import GaussianConstraintBuilder
    if 'FIT' in config['Context']:
        constraintbuilder = GaussianConstraintBuilder(ws, config['Constraints'])
    else:
        constraintbuilder = GaussianConstraintBuilder(ws)

    # add other constraints we have
    for c in constraints:
        constraintbuilder.addUserConstraint(c)
    # remove constraints for modes which are not included
    constr = constraintbuilder.getSetOfConstraints()
    for mode in config['Modes']:
        # skip modes with contributions to pdf
        if len(components[mode]) > 0: continue
        again = True
        while again:
            again = False
            it = constr.fwdIterator()
            while True:
                arg = it.next()
                if None == arg: break
                if -1 != arg.GetName().find(mode):
                    constr.remove(arg)
                    again = True
                    break

    constraints = [ ]
    it = constr.fwdIterator()
    while True:
        arg = it.next()
        if None == arg: break
        constraints.append(arg)

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

    from B2DXFitters.FitResult import getDsHBlindFitResult
    print getDsHBlindFitResult(not fitConfig['IsToy'], fitConfig['Blinding'],
            fitResult)

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
        # FIXME: apparently, RooFit needs the instantiation of an SMatrix
        # below, or the chi^2 fit will be way off - this has to be understood,
        # but in the meantime, it's a workaround
        ROOT.Math.SMatrix('double', 2, 2,
                ROOT.Math.MatRepSym('double', 2))()
        calibFitResult = calib.chi2FitTo(ds,
                RooFit.YVar(omega), RooFit.Integrate(False),
                RooFit.Strategy(fitConfig['Strategy']),
                RooFit.Optimize(fitConfig['Optimize']),
                RooFit.Minimizer(*fitConfig['Minimizer']),
                RooFit.Timer(), RooFit.Save(), RooFit.Verbose())
        print getDsHBlindFitResult(not fitConfig['IsToy'], fitConfig['Blinding'],
                calibFitResult)
        anaCalibFitResult = fitPolynomialAnalytically(
                len(calibParams) - 1, anafitds)
        if (abs(anaCalibFitResult['chi2'] - calibFitResult.minNll()) /
                (0.5 * (abs(anaCalibFitResult['chi2']) +
                    abs(calibFitResult.minNll()))) >= 1e-3):
            print 'ERROR: calibration fit results of RooFit-driven and ' \
                'analytical fit do not agree - INVESTIGATE!!'
        elif None != calibplotfile:
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
    from B2DXFitters.utils import (updateConfigDict, configDictFromString,
            configDictFromFile)
    #
    # example: change Gammas in fitting:
    # fitConfig.update({'Gammas': 0.700})

    (options, args) = parser.parse_args()
    if '-' == args[0]: args.pop(0)

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
    defauldefaultfig = updateConfigDict(defaultConfig,
                configDictFromFile(personalityfile))
    updateConfigDict(defaultConfig, {'Personality': options.personality})
    del personalityfile

    generatorConfig = copy.deepcopy(defaultConfig)
    fitConfig = copy.deepcopy(defaultConfig)
    # parse fit/generator configuration options
    if None != options.fitConfigFile:
        fitConfig = updateConfigDict(fitConfig,
                configDictFromFile(options.fitConfigFile))
    if None != options.fitConfigString:
        fitConfig = updateConfigDict(fitConfig,
                configDictFromString(options.fitConfigString,
                '[command line, fit config string]'))
    if None != options.genConfigFile:
        generatorConfig = updateConfigDict(generatorConfig,
                configDictFromFile(options.genConfigFile))
    if None != options.genConfigString:
        generatorConfig = updateConfigDict(generatorConfig,
                configDictFromString(options.genConfigString,
                    '[command line, generator config string]'))
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
