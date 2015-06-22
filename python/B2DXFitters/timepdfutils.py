"""
@file timepdfutils.py

@author Manuel Schiller <Manuel.Schiller@cern.ch>
@date 2015-06-21

@brief utilities to build decay time pdfs
"""
import ROOT
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
    effresmodel = WS(ws, RooEffResModel(
        '%s_timeacc_%s' % (timeresmodel.GetName(), acceptance.GetName()),
        '%s plus time acceptance %s' % (timeresmodel.GetTitle(),
            acceptance.GetTitle()), timeresmodel, acceptance))
    return effresmodel
    # FIXME: the code below does not quite work yet, to be debugged at some
    # point in the future - idea here is to have per tagging decision
    # acceptance
    #from ROOT import RooSimultaneousResModel, RooArgList
    #statemap = { -1: effresmodel, 0: effresmodel, 1: effresmodel }
    #states = RooArgList()
    #tit = ws.cat('qt').typeIterator()
    #ROOT.SetOwnership(tit, True)
    #while True:
    #    obj = tit.Next()
    #    if None == obj: break
    #    idx = obj.getVal()
    #    resmodel = statemap[idx]
    #    resmodel = resmodel.clone('%s_IDX%d' % (resmodel.GetName(), idx))
    #    states.add(resmodel)
    #del obj
    #del tit
    #simresmodel = WS(ws, RooSimultaneousResModel(
    #    '%s_simresmodel' % effresmodel.GetName(),
    #    '%s_simresmodel' % effresmodel.GetName(),
    #    ws.cat('qt'), states))
    #return simresmodel

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
        pdf = WS(ws, RooEffProd('%s_TimePdfUnbinnedAcceptance' % name,
            '%s full time pdf' % name, pdf, acceptance))
        return pdf
    else:
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
        return
    from ROOT import RooArgSet
    if not timeerr.hasBinning('cache'):
        timeerr.setBins(config['NBinsProperTimeErr'], 'cache')
    timeresmodel.setParameterizeIntegral(RooArgSet(timeerr))

# apply the per-event time error pdf
def applyDecayTimeErrPdf(config, name, ws, time, timeerr, qt, qf, mistagobs,
        timepdf, timeerrpdf, mistagpdf):
    """
    apply the per-event time error pdf

    config      -- configuration dictionary
    name        -- prefix to be used for new RooFit objects
    ws          -- workspace to import new objects into
    time        -- time observable
    timeerr     -- decay time error observable (or None for average decay time
                   error)
    qt          -- tagging decision
    qf          -- final state charge
    mistagobs   -- mistag observable (or None for average mistag)
    timepdf     -- decay time pdf
    timeerrpdf  -- decay time error pdf (or None for av. decay time error)
    mistagpdf   -- mistag pdf (or None for average mistag)

    returns the (possibly modified) decay time error pdf (with decay time
    error multiplied on, if applicable).
    """
    # no per-event time error is easy...
    if None == timeerrpdf: return timepdf
    from ROOT import RooFit, RooArgSet, RooProdPdf
    noncondset = RooArgSet(time, qf, qt)
    if None != mistagpdf:
        noncondset.add(mistagobs)
    timepdf = WS(ws, RooProdPdf('%s_TimeTimeerrPdf' % name,
        '%s (time,timeerr) pdf' % name, RooArgSet(timeerrpdf),
        RooFit.Conditional(RooArgSet(timepdf), noncondset)))
    return timepdf

# apply k-factor smearing
def applyKFactorSmearing(
        config,         # configuration dictionary
        ws,             # workspace
        time,           # time variable
        timeresmodel,   # time resolution model
        kvar,           # k factor variable
        kpdf,           # k factor distribution
        substtargets):  # quantities q to substitute k * q for
    """
    apply k-factor smearing to a resolution model

    config          -- config dictionary
    ws              -- workspace into which to import new RooFit objects
    time            -- decay time observable
    timeresmodel    -- decay time resolution model
    kvar            -- k factor variable (or None if no k-factor correction)
    kpdf            -- k factor pdf (or None if no k-factor correction)
    substtargets    -- substitution targets

    returns (effective) k-factor smeared resolution model, if applicable

    In the time pdf, you get dimensionless terms like k * time * q where q is
    Gamma, DeltaGamma, or DeltaM. It is therefore possible to make the
    k-factor correction part of the resolution model by scaling the quantities
    q with the k-factor. The advantage is that they don't change every event
    like the decay time does; this allows for fairly efficient caching, and
    there for fast evaluation.
    
    The substtargets parameter is a list of RooFit variables q_i (typically
    Gamma, DeltaGamma and DeltaM) for which k * q_i are substituted in the
    effective resolution model.

    The RooKResModel class that does the heavy lifting internally uses the
    resolution model and k-factor pdf given as input, and calculates a
    suitably weighted average (weighted by kpdf) of resolution models which
    take the k-factor into account. See the documentation the comes with the
    RooKResModel class for details.

    relevant configuration dictionary keys:
    'NBinsTimeKFactor':
        number of bins for k-factor distribution
    """
    if None == kpdf or None == kvar:
        return timeresmodel
    from ROOT import RooKResModel, RooArgSet
    paramobs = [ ]
    if config['NBinsTimeKFactor'] > 0:
        if not time.hasBinning('cache'):
            time.setBins(config['NBinsTimeKFactor'], 'cache')
        paramobs.append(time)
    retVal = WS(ws, RooKResModel(
        '%s_%sSmeared' % (timeresmodel.GetName(), kpdf.GetName()),
        '%s_%sSmeared' % (timeresmodel.GetName(), kpdf.GetName()),
        timeresmodel, kpdf, kvar, RooArgSet(*substtargets),
        RooArgSet(*paramobs)))
    return retVal

# build B decay time pdf
def buildBDecayTimePdf(
    config,                             # configuration dictionary
    name,                               # 'Signal', 'DsPi', ...
    ws,                                 # RooWorkspace into which to put the PDF
    time, timeerr, qt, qf, mistag, tageff,      # potential observables
    Gamma, DeltaGamma, DeltaM,          # decay parameters
    C, D, Dbar, S, Sbar,                # CP parameters
    timeresmodel = None,                # decay time resolution model
    acceptance = None,                  # acceptance function
    timeerrpdf = None,                  # pdf for per event time error
    mistagpdf = None,                   # pdf for per event mistag
    mistagobs = None,                   # real mistag observable
    kfactorpdf = None,                  # distribution k factor smearing
    kvar = None,                        # variable k which to integrate out
    aprod = None,                       # production asymmetry
    adet = None,                        # detection asymmetry
    atageff = None                      # asymmetry in tagging efficiency
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
    qt              -- tagging decision (RooCategory)
    qf              -- final state charge (RooCategory)
    mistag          -- mistag (either average, or calibrated omega(eta))
    tageff          -- tagging efficiency
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
    mistagobs       -- (uncalibrated) per event mistag observable (or None)
    kfactorpdf      -- k factor distribution (None for no k-factor correction)
    kvar            -- k factor variable (None for no k-factor correction)
    aprod           -- production asymmetry (None for zero asymmetry)
    adet            -- detection asymmetry (None for zero asymmetry)
    atageff         -- tagging eff. asymmetry (None, or list, 1 per tagger/cat.)

    returns:
    --------
    a time pdf built according to specification

    This routine is a rather flexible beast and can accomodate a multitude of
    use cases:
    - ideal, average or per-event decay time resolution (pdf needed for
      per-event case)
    - ideal, average, per category, or per-event mistag:
      * ideal: mistag = zero, mistagpdf = mistagobs = None
      * average: mistag = RooRealVar/RooConstVar, mistagpdf = mistagobs = None
      * per category: qt = -Ncat, ... , 0, 1, ..., Ncat, mistag = RooArgList
        of per-category average mistags (1, ..., Ncat),i
        mistagpdf = mistagobs = None (can be used for calibrations!)
      * per event: qt = -1, 0, +1, mistag = calibrated mistag omega(eta),
        mistagpdf = P(eta), mistagobs = eta
      * per event, mutually exclusive taggers: like per category, but
        mistagpdf becomes a list of pdfs as well
      * one can have as many tagging asymmetries as there are
        categories/mutually exclusive taggers (for a single one, just pass the
        RooRealVar, else a RooArgList of RooRealVars)
      * if the calibration needs to differ between B and Bbar, mistag can also
        be a list of two calibrations "[ calB, calBbar ]", or a list of
        RooArgLists (one per category/mutually exclusive tagger)
    - optionally, a k-factor correction can be applied for partially
      reconstructed or misidentified modes

    See the classes RooBDecay (in RooFit), DecRateCoeff (B2DXFitters) and
    RooKResModel (also B2DXFitters) for details on the precise meaning and
    definition of these variables.

    relevant config dictionary keys:
    --------------------------------
    'Debug':
        print all arguments to buildBDecayTimePdf before doing anything -
        useful to see what "really goes in" when it doesn't do what it
        should...
    'UseKFactor':
        if True, apply the k-factor correction, if False, k-factor correction
        can be disabled globally (useful for fast fitback look toys,
        systematic studies, etc.)
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
        time, tau, DeltaGamma,  cosh, sinh, cos, sin,
        DeltaM, timeresmodel, RooBDecay.SingleSided))

    retVal = applyDecayTimeErrPdf(config, name, ws, time, timeerr, qt, qf,
            mistagobs, retVal, timeerrpdf, mistagpdf)
    
    # if we do not bin the acceptance, we apply it here
    retVal = applyUnbinnedAcceptance(config, name, ws, retVal, acceptance)

    retVal.SetNameTitle('%s_TimePdf' % name, '%s full time pdf' % name)

    # return the copy of retVal which is inside the workspace
    return WS(ws, retVal)

