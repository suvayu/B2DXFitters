#!/usr/bin/env python
# coding=utf-8
"""Script used to run the cFit.

Personality files (python files with dictionaries) in
$B2DXFITTERSROOT/data/cFit/personality/, and a python dictionary
provided as a string on the command line can be used to configure the
fit.  The order of precedence is:

  default < personality < cli string.

"""


import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('toyseed', nargs='?',
                    help = 'Seed for toy generation')
parser.add_argument('-d', '--debug', dest = 'debug', default = False, action = 'store_true',
                    help = 'print debug information while processing')
parser.add_argument('-s', '--save', dest = 'wsname', metavar = 'WSNAME', required = True,
                    help = 'save the model PDF and generated dataset to file WS_WSNAME.root' )
parser.add_argument('-i', '--initial-vars', dest = 'initvars', default = False, action = 'store_true',
                    help = 'save the model PDF parameters before the fit (default: after the fit)')
parser.add_argument('-F', '--fit-config-string', dest = 'fitConfigString',
                    help = 'string with fit configuration changes (dictionary, takes precedence)')
parser.add_argument('-f', '--fit-config-file', dest = 'fitConfigFile',
                    help = 'name of file with fit configuration changes (dictionary)' )
parser.add_argument('-G', '--gen-config-string', dest = 'genConfigString',
                    help = 'string with generator configuration changes (dictionary, takes precedence)')
parser.add_argument('-g', '--gen-config-file', dest = 'genConfigFile',
                    help = 'name of file with generator configuration changes (dictionary)')
parser.add_argument('-p', '--personality', dest = 'personality', default = '2011Conf',
                    help = 'fitter personality (e.g. \'2011Conf\')')
parser.add_argument('--calibplotfile', dest = 'calibplotfile', default = '',
                    help = 'file name for calibration plot' )
options = parser.parse_args()


import copy, os, sys, gc

# math
from math import (pi, log)

# ROOT/RooFit
import ROOT
from ROOT import RooFit

import B2DXFitters

# set a flag if we have access to AFS (can be used in the personality files)
haveAFS = os.path.isdir('/afs') and os.path.isdir('/afs/cern.ch')

from B2DXFitters.cfit.utils import (updateConfigDict, WS)
from B2DXFitters.cfit.defaults import defaultConfig
from B2DXFitters.cfit.constants import *
from B2DXFitters.cfit.templates import (writeDataSet, readDataSet)
from B2DXFitters.cfit.ftag import getEtaPerCat
from B2DXFitters.cfit.pdfs import getMasterPDF


try:
    TOY_NUMBER = int(options.toyseed)
except ValueError:
    parser.error('The toy number is meant to be an integer ;-)!')
    raise

# apply personality
personalityfile = '{}/data/cFit/personality/{}.py' \
    .format(os.environ['B2DXFITTERSROOT'], options.personality)
try:
    lines = file(personalityfile, 'r').readlines()
except:
    parser.error('Unable to read personality {} from {}' \
                 .format(options.personality, personalityfile))
    raise
try:
    updateConfigDict(defaultConfig, {'Personality': options.personality})
    d = eval(compile(''.join(lines), personalityfile, 'eval'))
    updateConfigDict(defaultConfig, d)
    del d
except:
    print('Unknown personality \'{}\''.format(options.personality))
    raise
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
        raise
    try:
        d = eval(compile(''.join(lines), options.fitConfigFile, 'eval'))
        fitConfig = updateConfigDict(fitConfig, d)
        del d
    except:
        parser.error('Unable to parse fit configuration in file %s' %
                options.fitConfigFile)
        raise
        del lines
if None != options.fitConfigString:
    try:
        d = eval(compile(options.fitConfigString, '[command line]', 'eval'))
        fitConfig = updateConfigDict(fitConfig, d)
        del d
    except:
        parser.error('Unable to parse fit configuration in \'%s\'' %
                options.fitConfigString)
        raise
if None != options.genConfigFile:
    try:
        lines = file(options.genConfigFile, 'r').readlines();
    except:
        parser.error('Unable to read generator configuration file %s' %
                options.genConfigFile)
        raise
    try:
        d = eval(compile(''.join(lines), options.genConfigFile, 'eval'))
        generatorConfig = updateConfigDict(generatorConfig, d)
        del d
    except:
        parser.error('Unable to parse generator configuration in file %s' %
                options.genConfigFile)
        raise
    del lines
if None != options.genConfigString:
    try:
        d = eval(compile(options.genConfigString, '[command line]', 'eval'))
        generatorConfig = updateConfigDict(generatorConfig, d)
        del d
    except:
        parser.error('Unable to parse generator configuration in \'%s\'' %
                options.genConfigString)
        raise
if '' == options.calibplotfile:
    options.calibplotfile = None



# config
toy_num = TOY_NUMBER
debug = options.debug
wsname = options.wsname
initvars = options.initvars
calibplotfile = options.calibplotfile

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
    sys.exit(0)

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
