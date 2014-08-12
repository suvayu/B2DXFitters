"""Utilities for decay time acceptance

"""


from B2DXFitters.WS import WS


def buildSplineAcceptance(
        ws,     # workspace into which to import
        time,   # time variable
        pfx,    # prefix to be used in names
        knots,  # knots
        coeffs, # acceptance coefficients
        floatParams = False # float acceptance parameters
        ): 
    # build acceptance function
    from copy import deepcopy
    myknots = deepcopy(knots)
    mycoeffs = deepcopy(coeffs)
    from ROOT import (RooBinning, RooArgList, RooPolyVar, RooCubicSplineFun,
            RooConstVar, RooProduct, RooRealVar)
    if (len(myknots) != len(mycoeffs) or 0 >= min(len(myknots), len(mycoeffs))):
        raise ValueError('ERROR: Spline knot position list and/or coefficient'
                'list mismatch')
    one = WS(ws, RooConstVar('one', '1', 1.0))
    # create the knot binning
    knotbinning = WS(ws, RooBinning(time.getMin(), time.getMax(),
        '%s_knotbinning' % pfx))
    for v in myknots:
        knotbinning.addBoundary(v)
    knotbinning.removeBoundary(time.getMin())
    knotbinning.removeBoundary(time.getMax())
    knotbinning.removeBoundary(time.getMin())
    knotbinning.removeBoundary(time.getMax())
    oldbinning, lo, hi = time.getBinning(), time.getMin(), time.getMax()
    time.setBinning(knotbinning, '%s_knotbinning' % pfx)
    time.setBinning(oldbinning)
    time.setRange(lo, hi)
    del knotbinning
    del oldbinning
    del lo
    del hi
    # create the knot coefficients
    coefflist = RooArgList()
    i = 0
    for v in mycoeffs:
        if floatParams:
            coefflist.add(WS(ws, RooRealVar('%s_SplineAccCoeff%u' % (pfx, i),
                '%s_SplineAccCoeff%u' % (pfx, i), v, 0., 3.)))
        else:
            coefflist.add(WS(ws, RooConstVar('%s_SplineAccCoeff%u' % (pfx, i),
                '%s_SplineAccCoeff%u' % (pfx, i), v)))
        i = i + 1
    del mycoeffs
    coefflist.add(one)
    i = i + 1
    myknots.append(time.getMax())
    myknots.reverse()
    fudge = (myknots[0] - myknots[1]) / (myknots[2] - myknots[1])
    lastmycoeffs = RooArgList(
            WS(ws, RooConstVar('%s_SplineAccCoeff%u_coeff0' % (pfx, i),
                '%s_SplineAccCoeff%u_coeff0' % (pfx, i), 1. - fudge)),
            WS(ws, RooConstVar('%s_SplineAccCoeff%u_coeff1' % (pfx, i),
                '%s_SplineAccCoeff%u_coeff1' % (pfx, i), fudge)))
    del myknots
    coefflist.add(WS(ws, RooPolyVar(
        '%s_SplineAccCoeff%u' % (pfx, i), '%s_SplineAccCoeff%u' % (pfx, i),
        coefflist.at(coefflist.getSize() - 2), lastmycoeffs)))
    del i
    print 'DEBUG: Spline Coeffs: %s' % str([ coefflist.at(i).getVal() for i in
	xrange(0, coefflist.getSize()) ])
    # create the spline itself
    tacc = WS(ws, RooCubicSplineFun('%s_SplineAcceptance' % pfx,
        '%s_SplineAcceptance' % pfx, time, '%s_knotbinning' % pfx,
        coefflist))
    del lastmycoeffs
    if not floatParams:
        # make sure the acceptance is <= 1 for generation
        m = max([coefflist.at(j).getVal() for j in
            xrange(0, coefflist.getSize())])
        c = WS(ws, RooConstVar('%s_SplineAccNormCoeff' % pfx,
            '%s_SplineAccNormCoeff' % pfx, 0.99 / m))
        tacc_norm = WS(ws, RooProduct('%s_SplineAcceptanceNormalised' % pfx,
            '%s_SplineAcceptanceNormalised' % pfx, RooArgList(tacc, c)))
        del c
        del m
    del coefflist
    return tacc, tacc_norm


def getAcceptance(
        ws,
        config,
        mode,
        time):
    if (None == config['AcceptanceFunction'] or 'None' ==
            config['AcceptanceFunction']):
        # no acceptance function
        return None
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
        tacc_norm = tacc
    elif 'PowLawAcceptance' == config['AcceptanceFunction']:
        acc_corr = readAcceptanceCorrection(config, ws, time)
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
        tacc_norm = tacc
    elif 'Spline' == config['AcceptanceFunction']:
        # ok, spline based acceptance function
        kind = 'MC' if config['IsToy'] else 'DATA'
        knots = config['AcceptanceSplineKnots']
        coeffs = config['AcceptanceSplineCoeffs'][kind][config['Modes'][0]]
        print coeffs
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
    effresmodel = WS(ws, RooEffResModel(
        '%s_timeacc_%s' % (timeresmodel.GetName(), acceptance.GetName()),
        '%s plus time acceptance %s' % (timeresmodel.GetTitle(),
            acceptance.GetTitle()), timeresmodel, acceptance))
    return effresmodel
    # FIXME: the code below does not quite work yet, to be debugged at some
    # point in the future
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
    from ROOT import RooEffProd
    if None != acceptance and 0 >= config['NBinsAcceptance']:
        # do not bin acceptance
        return WS(ws, RooEffProd('%s_TimePdfUnbinnedAcceptance' % name,
            '%s full time pdf' % name, pdf, acceptance))
    else:
        return pdf
