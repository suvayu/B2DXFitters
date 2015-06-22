"""
@file taggingutils.py

@author Manuel Schiller <Manuel.Schiller@cern.ch>
@date 2015-06-22

@brief utilities for tagging and tagging calibration
"""
import B2DXFitters
import ROOT
from ROOT import RooFit

def getMistagBinBounds(config, mistag, mistagdistrib):
    """
    suggest a binning for turning per-event mistag into mistag categories

    This routine takes a mistag observable and a PDF or data set, and suggests
    a number of mistag category boundaries which have approximately equal
    statistics in each category.

    config          -- config dictionary
    mistag          -- mistag observable (eta)
    mistagdistrib   -- a PDF or a RooDataSet

    returns a (python) list of mistag category bin bounds

    relevant configuration dictionary keys:
    'NMistagCategories':
        number of mistag categories for which to suggest a set of bin bounds
    """
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
    """
    estimate the per-category mistag (omega_i) as starting value for the fit

    calculate true per-category omegas based on the mistagpdf and the
    calibration that goes into the generation pdf

    config      -- config dictionary
    mistagobs   -- mistag observable (eta)
    mistag      -- calibrated mistag (omega(eta))
    mistagpdf   -- mistag pdf (P(eta))

    returns a pair of average mistag omega, list of per-category mistag
    (omega) averages

    relevant config dictionary keys:
    'MistagCategoryBinBounds':
        list of mistag category bin bounds (one more entry than mistag
        categories)
    """
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
    """
    calculate overall and per-category eta averages for a given data set ds

    config      -- config dictionary
    mistagobs   -- mistag observable (eta)
    ds          -- data set

    returns a triple of (overall average eta, list of per-category eta
    averages eta_i, list of per-category weights).

    relevant config dictionary keys:
    'MistagCategoryBinBounds':
        list of mistag category bin bounds (one more entry than mistag
        categories)
    """
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

def fitPolynomialAnalytically(
        deg, datapoints, crossCheckWithTGraphErrors = False):
    """
    fits a polynomial through a list of data points
    
    degree      -- degree of polynomial to fit
    datapoints  -- [ [ x_1, y_1, sigma_y_1], ... ]
    crossCheckWithTGraphErrors -- if True, cross-check the fit result with
                   ROOT's TGraphErrors (was used when debugging the routine)
    
    fit polynomial is p(x) = sum_k p_k x^k analytically (no need for MINUIT,
    since the problem is linear in the polynomial's coefficients)

    returns a (python) dictionary with fit result(s)
    """
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

