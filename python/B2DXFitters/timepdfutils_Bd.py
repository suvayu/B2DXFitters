"""
@file timepdfutils_Bd.py

@author Vincenzo Battista
@date 2016-06-03

@brief Utilities to build decay time pdfs.
       Uses the DecRateCoeff_Bd class from Dortmund.
       Based on a previous script from Manuel Schiller.
"""

import ROOT
from ROOT import RooFit
from B2DXFitters.WS import WS

# apply the acceptance to the time pdf (binned, i.e. apply to resolution model)
def applyBinnedAcceptance(config, ws, time, timeresmodel, acceptance):
    """
    apply a (binned) acceptance to a decay time pdf

    config          -- configuration dictionary
    ws              -- workspace to import generated objects into
    time            -- decay time observable
    timeresmodel    -- decay time resolution model (not acceptance corrected)
    acceptance      -- acceptance function

    returns acceptance-corrected resolution model

    relevant configuration dictionary keys:
    'NBinsAcceptance':
        0 for unbinnned acceptance, > 0 to bin acceptance to speed up
        evaluation (keep at 0 for spline acceptance!)
    """
    if None == acceptance or 0 >= config['NBinsAcceptance']:
        if config['Debug']:
            print "timepdfutils_Bd.applyBinnedAcceptance(..)=> Returning resolution without acceptance."
        return timeresmodel
    from ROOT import RooArgSet, RooBinnedPdf, RooEffResModel
    # bin the acceptance if not already binned
    if not acceptance.isBinnedDistribution(RooArgSet(time)):
        if config['Debug']:
            print "timepdfutils_Bd.applyBinnedAcceptance(..)=> Binning acceptance."
        acceptance = WS(ws, RooBinnedPdf(
            "%sBinnedAcceptance" % acceptance.GetName(),
            "%sBinnedAcceptance" % acceptance.GetName(),
            time, 'acceptanceBinning', acceptance))
        acceptance.setForceUnitIntegral(True)
    # create the acceptance-corrected resolution model
    effresmodel = WS(ws, RooEffResModel(
        '%s_timeacc_%s' % (timeresmodel.GetName(), acceptance.GetName()),
        '%s plus time acceptance %s' % (timeresmodel.GetTitle(),
            acceptance.GetTitle()), timeresmodel, acceptance))
    if config['Debug']:
        print "timepdfutils_Bd.applyBinnedAcceptance(..)=> Returning resolution multiplied by acceptance."
    return effresmodel

# apply the acceptance to the time pdf (unbinned)
def applyUnbinnedAcceptance(config, name, ws, pdf, acceptance):
    """
    apply the acceptance to the time pdf (unbinned, i.e. without fancy tricks
    for histogram or spline based acceptance)

    config      -- configuration dictionary
    name        -- prefix of the name of generated RooFit objects
    ws          -- workspace to import generated objects into
    pdf         -- decay time pdf (not acceptance corrected)
    acceptance  -- acceptance function

    returns acceptance-corrected decay time pdf

    relevant configuration dictionary keys:
    'NBinsAcceptance':
        0 for unbinnned acceptance, > 0 to bin acceptance to speed up
        evaluation (keep at 0 for spline acceptance!)
    """
    from ROOT import RooEffProd
    if None != acceptance and 0 >= config['NBinsAcceptance']:
        # do not bin acceptance
        if config['Debug']:
            print "timepdfutils_Bd.applyUnbinnedAcceptance(..)=> Multiplying pdf by acceptance."
        pdf = WS(ws, RooEffProd('%s_TimePdfUnbinnedAcceptance' % name,
            '%s full time pdf' % name, pdf, acceptance))
        return pdf
    else:
        if config['Debug']:
            print "timepdfutils_Bd.applyUnbinnedAcceptance(..)=> Returning pdf without acceptance."
        return pdf

# speed up the fit by parameterising integrals of the resolution model over
# time in the (per-event) time error (builds a table if integral values and
# interpolates)
def parameteriseResModelIntegrals(config, ws, timeerrpdf, timeerr, timeresmodel):
    """
    speed up the fit by parameterising integrals of the resolution model over
    time in the (per-event) time error (builds a table if integral values and
    interpolates)

    config          -- configuration dictionary
    ws              -- workspace to work with
    timeerrpdf      -- time error pdf
    timerr          -- time error observable
    timeresmodel    -- (time) resolution model

    configuration dictionary keys:
    'NBinsProperTimeErr':
        number of bins in which to tabulate resolution model integral, so
        evaluation can be sped up by interpolating from the table
    
    This will speed up fits considerably for per-event decay time error, since
    you don't have to normalise the time pdf for every event (because the
    decay time error changes every event, O(1k) or more), but you only have to
    evaluate the normalisation integrals for a few (O(100)) distinct values.
    Interpolating is then very fast (and typically sufficiently accurate)...
    """
    if None == timeerrpdf or 0 == config['NBinsProperTimeErr']:
        if config['Debug']:
            print "timepdfutils_Bd.parameteriseResModelIntegrals(..)=> Not doing parameterisation."
        return
    from ROOT import RooArgSet
    if not timeerr.hasBinning('cache'):
        timeerr.setBins(config['NBinsProperTimeErr'], 'cache')
    if config['Debug']:
        print "timepdfutils_Bd.parameteriseResModelIntegrals(..)=> Applying parameterisation."
    timeresmodel.setParameterizeIntegral(RooArgSet(timeerr))

# make the pdf conditional
def buildConditionalPdf(config, name, ws, time, timeerr, qt, qf, mistagobs,
        timepdf, timeerrpdf, mistagpdf):
    """
    make the pdf conditional

    config      -- configuration dictionary
    name        -- prefix to be used for new RooFit objects
    ws          -- workspace to import new objects into
    time        -- time observable
    timeerr     -- decay time error observable (or None for average decay time
                   error)
    qt          -- tagging decision (list)
    qf          -- final state charge
    mistagobs   -- mistag observable (or None for average mistag)
    timepdf     -- decay time pdf
    timeerrpdf  -- decay time error pdf (or None for av. decay time error)
    mistagpdf   -- mistag pdf (or None for average mistag)

    returns the (possibly modified) decay time error pdf (with decay time
    error multiplied on, if applicable).

    if UseProtoData = True, mistag obs and timeerr are not included in the conditional
    observables. It's up to the user to generate mistag obs/timeerr datasets separately
    from mistagpdf and timeerrpdf, and then include them as 'ProtoData' when the final
    dataset is generated from the total pdf. This trick can speed up a lot the generation.
    See 'generate' method in 'RooAbsPdf' documentation for more info about ProtoData usage.
    """
    from ROOT import RooFit, RooArgSet, RooProdPdf

    if None == timeerrpdf and None == mistagpdf:
        if config['Debug']:
            print "timepdfutils_Bd.buildConditionalPdf(..)=> No time error/mistag pdf applied."
        return timepdf

    comp_conditional_observables = RooArgSet(time, qf)
    for tag in qt:
        comp_conditional_observables.add(tag)
    
    comp_conditional_dimensions = RooArgSet()

    if None != timeerrpdf:
        if config['Debug']:
            print "timepdfutils_Bd.buildConditionalPdf(..)=> The following decay time error pdf is applied:"
            timeerrpdf.Print("v")
        comp_conditional_dimensions.add(timeerrpdf)
        if not config['UseProtoData']:
            comp_conditional_observables.add(timeerr)

    if None != mistagpdf:
        for mpdf in mistagpdf:
            if config['Debug']:
                print "timepdfutils_Bd.buildConditionalPdf(..)=> The following mistag pdf is applied:"
                mpdf.Print("v")
            comp_conditional_dimensions.add(mpdf)
        if not config['UseProtoData']:
            for mobs in mistagobs:
                comp_conditional_observables.add(mobs)

    if config['Debug']:
        print "timepdfutils_Bd.buildConditionalPdf(..)=> Conditional dimensions:"
        comp_conditional_dimensions.Print("v")
        print "timepdfutils_Bd.buildConditionalPdf(..)=> Conditional observables:"
        comp_conditional_observables.Print("v")
        
    timepdf = WS(ws, RooProdPdf('%s_TimeTimeerrPdf' % name,
                                '%s (time,timeerr) pdf' % name, comp_conditional_dimensions,
                                RooFit.Conditional(RooArgSet(timepdf), comp_conditional_observables)))

    if config['Debug']:
        print "timepdfutils_Bd.buildConditionalPdf(..)=> Done."

    return timepdf

# build B decay time pdf
def buildBDecayTimePdf(
    config,                             # configuration dictionary
    name,                               # 'Signal', 'DsPi', ...
    ws,                                 # RooWorkspace into which to put the PDF
    time, timeerr, qt, qf, mistagobs,   # potential observables
    mistagcalib,                        # mistag calibration coefficients
    Gamma, DeltaGamma, DeltaM,          # decay parameters
    C, D, Dbar, S, Sbar,                # CP parameters
    timeresmodel = None,                # decay time resolution model
    acceptance = None,                  # acceptance function
    timeerrpdf = None,                  # pdf for per event time error
    mistagpdf = None,                   # pdf for per event mistag
    aprod = None,                       # production asymmetry
    adet = None,                        # detection asymmetry
    ):
    """
    build a B decay time pdf

    parameters:
    -----------
    config          -- config dictionary
    name            -- name prefix for newly created objects
    ws              -- workspace into which to import created objects
    time            -- time observable
    timeerr         -- time error (constant for average, or per-event obs.)
    qt              -- tagging decision (list of RooCategory)
    qf              -- final state charge (RooCategory)
    mistagobs       -- mistag observable (list)
    mistagcalib     -- mistag calibration coefficients (list of p0, p1, Dp0, Dp1, <eta>, tageff, atageff as RooAbsReal)
    Gamma           -- width of decay (1/lifetime)
    DeltaGamma      -- width difference
    DeltaM          -- mass difference
    C               -- term in front of cos in RooBDecay
    D               -- term in front of sinh in RooBDecay (f final state)
    Dbar            -- term in front of sinh in RooBDecay (fbar final state)
    S               -- term in front of sin in RooBDecay (f final state)
    Sbar            -- term in front of sin in RooBDecay (fbar final state)
    timeresmodel    -- decay time resolution model (or None for delta fn)
    acceptance      -- acceptance (or None for flat efficiency(decay time))
    timeerrpdf      -- decay time error distribution (or None for average)
    mistagpdf       -- per event mistag distribution(s) (or None for average)
    aprod           -- production asymmetry (None for zero asymmetry)
    adet            -- detection asymmetry (None for zero asymmetry)

    returns:
    --------
    a time pdf built according to specification

    This routine is a rather flexible beast and can accomodate a multitude of
    use cases:

    See the classes RooBDecay (in RooFit), DecRateCoeff (B2DXFitters) and
    RooKResModel (also B2DXFitters) for details on the precise meaning and
    definition of these variables.

    relevant config dictionary keys:
    --------------------------------
    'Debug':
        print all arguments to buildBDecayTimePdf before doing anything -
        useful to see what "really goes in" when it doesn't do what it
        should...
    'ParameteriseIntegral':
        if True, save a huge amount of CPU by parametrising the resolutition
        model integral and its convolutions with the decay time pdf as a
        function of (per-event) decay time; see parameteriseResModelIntegrals
        for details

    For more information on how various bits affect the pdf built, see also
    the documentation for the following helper routines:
    applyBinnedAcceptance, applyKFactorSmearing, applyDecayTimeErrPdf,
    applyUnbinnedAcceptance, parameteriseResModelIntegrals
    """
    # Look in LHCb-INT-2011-051 for the conventions used
    from ROOT import ( RooConstVar, RooProduct, RooTruthModel, RooGaussModel,
        Inverse, RooBDecay, RooProdPdf, RooArgSet, DecRateCoeff_Bd,
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
                'mistagobs': mistagobs,
                'mistagcalib': mistagcalib,
                'Gamma': Gamma,
                'DeltaGamma': DeltaGamma,
                'DeltaM': DeltaM,
                'C': C, 'D': D, 'Dbar':Dbar, 'S': S, 'Sbar': Sbar,
                'timeresmodel': timeresmodel,
                'acceptance': acceptance,
                'timeerrpdf': timeerrpdf,
                'mistagpdf': mistagpdf,
                'aprod': aprod,
                'adet': adet,
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

    # if no time resolution model is set, fake one
    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Including resolution"
    if timeresmodel == None:
        timeresmodel = WS(ws, RooTruthModel('%s_TimeResModel' % name,
            '%s time resolution model' % name, time))
    elif timeresmodel == 'Gaussian':
        timeresmodel = WS(ws, RooGaussModel('%s_TimeResModel' % name,
            '%s time resolution model' % name, time, zero, timeerr))
    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Returning resolution"

    # apply acceptance (if needed)
    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Including acceptance"
    timeresmodel = applyBinnedAcceptance(
            config, ws, time, timeresmodel, acceptance)
    if config['ParameteriseIntegral']:
        parameteriseResModelIntegrals(config, ws, timeerrpdf, timeerr, timeresmodel)

    # manage tagging
    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Including tagging"
    otherargs = []
    for mitem in range(0,mistagobs.__len__()):
        otherargs += [ qt[mitem] ]
        otherargs += [ mistagobs[mitem] ]
        for citem in mistagcalib[mitem]:
            otherargs += [ citem ]

    # asymmetries
    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Including asymmetries"
    otherargs += [ aprod, adet ]

    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Additional arguments of DecRateCoeff_Bd:"
        print otherargs
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Number of arguments:"
        print otherargs.__len__()
    
    # build coefficients to go into RooBDecay
    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Defining CP coefficients"
    cosh = WS(ws, DecRateCoeff_Bd('%s_cosh' % name, '%s_cosh' % name,
                                  0, qf, one, one, *otherargs))
    sinh = WS(ws, DecRateCoeff_Bd('%s_sinh' % name, '%s_sinh' % name,
                                  1, qf, D, Dbar, *otherargs))
    cos = WS(ws, DecRateCoeff_Bd('%s_cos' % name, '%s_cos' % name,
                                 2, qf, C, C, *otherargs))
    sin = WS(ws, DecRateCoeff_Bd('%s_sin' % name, '%s_sin' % name,
                                 3, qf, S, Sbar, *otherargs))
    # build (raw) time pdf
    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Building time pdf"
    tau = WS(ws, Inverse('%sTau' % Gamma.GetName(),
        '%s #tau' % Gamma.GetName(), Gamma))
    retVal = WS(ws, RooBDecay(
        '%s_RawTimePdf' % name, '%s raw time pdf' % name,
        time, tau, DeltaGamma,  cosh, sinh, cos, sin,
        DeltaM, timeresmodel, RooBDecay.SingleSided))

    retVal = buildConditionalPdf(config, name, ws, time, timeerr, qt, qf,
            mistagobs, retVal, timeerrpdf, mistagpdf)
    
    # if we do not bin the acceptance, we apply it here
    retVal = applyUnbinnedAcceptance(config, name, ws, retVal, acceptance)

    retVal.SetNameTitle('%s_TimePdf' % name, '%s full time pdf' % name)

    if config['Debug']:
        print "timepdfutils_Bd.buildBDecayTimePdf(..)=> Returning decay time pdf"

    # return the copy of retVal which is inside the workspace
    return WS(ws, retVal)

