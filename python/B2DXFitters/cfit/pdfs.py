"""PDF utilities

"""


from math import pi, log
import ROOT
from ROOT import RooFit

from .ftag import (getTrueOmegasPerCat, makeTagEff)
from .resolution import (getResolutionModel,
                         parameteriseResModelIntegrals)
from .acceptance import (getAcceptance, applyBinnedAcceptance,
                         applyUnbinnedAcceptance)
from .kfactor import applyKFactorSmearing
from .utils import (WS, setConstantIfSoConfigured)
from .templates import (getDecayTimeErrorTemplate, getMistagTemplate,
                        getMassTemplates, getKFactorTemplates)


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
    if None == atageff_f: atageff_f = [ zero for i in xrange(0, config['NTaggers']) ]
    if None == atageff_t: atageff_t = [ zero for i in xrange(0, config['NTaggers']) ]

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
    if config['UseKFactor']:
        timeresmodel = applyKFactorSmearing(config, ws, time, timeresmodel,
                kvar, kfactorpdf, [ Gamma ])
    if config['ParameteriseIntegral']:
        parameteriseResModelIntegrals(config, ws, timeerrpdf, timeerr, timeresmodel)

    # perform the actual k-factor smearing integral (if needed)
    # build (raw) time pdf
    tau = WS(ws, Inverse('%sTau' % Gamma.GetName(),
        '%s #tau' % Gamma.GetName(), Gamma))
    retVal = WS(ws, RooDecay('%s_RawTimePdf' % name, '%s raw time pdf' % name,
        time, tau, timeresmodel, RooDecay.SingleSided))

    paramObs = RooArgSet(qt, qf)
    if None != mistagpdf:
        paramObs.add(mistag)
    if None != timeerrpdf:
        paramObs.add(timeerr)
    
    retVal = applyDecayTimeErrPdf(config, name, ws, time, timeerr, qt, qf,
            mistag, retVal, timeerrpdf, mistagpdf)
    
    if None != mistagpdf:
        otherargs = [ mistag, RooArgList(*mistagpdf), RooArgList(*tageff),
                adet, RooArgList(*atageff_f), RooArgList(*atageff_t) ]
    else:
        otherargs = [ RooArgList(*tageff), adet, RooArgList(*atageff_f),
                RooArgList(*atageff_t) ]
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
    if None == atageff: atageff = [ zero ]
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
    if config['UseKFactor']:
        timeresmodel = applyKFactorSmearing(config, ws, time, timeresmodel,
                kvar, kfactorpdf, [ Gamma, DeltaGamma, DeltaM ])
    if config['ParameteriseIntegral']:
        parameteriseResModelIntegrals(config, ws, timeerrpdf, timeerr, timeresmodel)

    # if there is a per-event mistag distributions and we need to do things
    # correctly
    if None != mistagpdf:
        otherargs = [ mistagobs, RooArgList(*mistagpdf), RooArgList(*tageff) ]
    else:
        otherargs = [ RooArgList(*tageff) ]
    bcalib = RooArgList()
    bbarcalib = RooArgList()
    for t in mistag:
        bcalib.add(t[0])
        if len(t) > 1:
            bbarcalib.add(t[1])
    otherargs.append(bcalib)
    if (bbarcalib.getSize()):
        otherargs.append(bbarcalib)
    otherargs += [ aprod, adet, RooArgList(*atageff) ]
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

    # build (raw) time pdf
    tau = WS(ws, Inverse('%sTau' % Gamma.GetName(),
        '%s #tau' % Gamma.GetName(), Gamma))
    retVal = WS(ws, RooBDecay(
        '%s_RawTimePdf' % name, '%s raw time pdf' % name,
        time, tau, DeltaGamma,	cosh, sinh, cos, sin,
        DeltaM, timeresmodel, RooBDecay.SingleSided))

    # work out in which observables to parameterise k-factor smearing, then
    # apply it
    paramObs = RooArgSet(qt, qf)
    if None != mistagpdf:
        paramObs.add(mistagobs)
    if None != timeerrpdf:
        paramObs.add(timeerr)

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
                                '%s_Mistag%uCalib%s_p%u' % (mode, itagger, namsfx[j], i), p))
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
                mistagCal.append(mistag)
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
                mistagtemplates[modes] = [ trivialMistagPDF for i in
                        xrange(0, config['NTaggers']) ]
    else:
        mistagtemplates = None



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
    if (None != config['NMistagCategories'] and
            config['NMistagCategories'] > 0 and config['PerEventMistag']):
        if 1 != config['NTaggers']:
            print ('ERROR: Mistag calibration fits in categories only'
                    'supported for a single tagger!')
            return None
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
            if None == mistagtemplate[config['Modes'][0]][0]:
                print ('ERROR: No mistag category bounds present, and no '
                        'mistag pdf template to tune from!')
                return None
            # all fine
            config['MistagCategoryBinBounds'] = getMistagBinBounds(
                    config, mistag, mistagtemplate[config['Modes'][0]][0])
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
                        mistagtemplate[config['Modes'][0]][0])
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
                .0352 / 7.))
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
    # Bs -> Ds Pi like modes, and Lb modes (non-oscillating)
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

    ########################################################################
    # non-osciallating modes
    ########################################################################
    # CombBkg
    #for mode in ('CombBkg',):
    #    if mode not in config['Modes']:
    #        continue
    #    tacc = getAcceptance(ws, config, mode, time)
    #    trm, tacc = getResolutionModel(ws, config, time, timeerr, tacc)
    #    modenick = mode
    #    kfactorpdf, kfactor = None, None
    #    gamma = WS(ws, RooRealVar('GammaCombBkg', '#Gamma_{CombBkg}',
    #        config['GammaCombBkg']))
    #    # figure out asymmetries to use
    #    asyms = { 'Det': None, 'TagEff_f': None, 'TagEff_t': None }
    #    for k in asyms.keys():
    #        for n in (mode, modenick, mode.split('2')[0]):
    #            if n in config['Asymmetries'][k]:
    #                if type(config['Asymmetries'][k][n]) == float:
    #                    asyms[k] = WS(ws, RooRealVar(
    #                        '%s_Asym%s' % (n, k), '%s_Asym%s' % (n, k),
    #                        config['Asymmetries'][k][n], -1., 1.))
    #                    asyms[k].setError(0.25)
    #                elif (type(config['Asymmetries'][k][n]) == list and
    #                        k.startswith('TagEff')):
    #                    if (len(config['Asymmetries'][k][n]) !=
    #                            config['NTaggers']):
    #                        raise TypeError('Wrong number of asymmetries')
    #                    asyms[k] = [ ]
    #                    for asymval in config['Asymmetries'][k][n]:
    #                        asymstmp = WS(ws, RooRealVar(
    #                            '%s_Asym%s%u' % (n, k, len(asyms[k])),
    #                            '%s_Asym%s%u' % (n, k, len(asyms[k])),
    #                            asymval, -1., 1.))
    #                        asymstmp.setError(0.25)
    #                        asyms[k].append(asymstmp)
    #                        del asymstmp
    #                else:
    #                    raise TypeError('Unsupported type for asymmetry')
    #                break
    #    y = 0.
    #    for lmode in yielddict:
    #        if lmode.startswith(modenick): y += yielddict[lmode]
    #    y = max(y, 1.)
    #    tageff = makeTagEff(config, ws, modenick, y)
    #    timepdfs[mode] = buildNonOscDecayTimePdf(config, mode, ws,
    #            time, timeerr, qt, qf, mistag, tageff, gamma,
    #            trm, tacc, terrpdfs[mode], mistagtemplates[mode],
    #            kfactorpdf, kfactor,
    #            asyms['Det'], asyms['TagEff_f'], asyms['TagEff_t'])
    
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
        totPDF = WS(ws, RooAddPdf('TotPDF', 'TotPDF', RooArgList(totPDF),
            RooArgList()))
    if '_unfixed' in totEPDF.GetName():
        totEPDF = WS(ws, RooAddPdf('TotEPDF', 'TotEPDF', RooArgList(totEPDF),
            RooArgList()))
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
