"""Flavour taggin functionality and utilities needed by cFit

@author Manuel Schiller
@email manuel dot schiller at nikhef.nl
@author Suvayu Ali
@email Suvayu dot Ali at cern.ch
@date 2014-04-26 Sat (First Koningsdag in over a century!)

"""


import ROOT
from ROOT import RooFit

from .utils import WS


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


def makeTagEff(config, ws, modename, yieldhint = None,
               perCategoryTagEffsShared = True,
               perCategoryTagEffsConst = True):
    """Make a tagging efficiency for mode modename.
    
    If we're fitting per-event mistag or average mistags without mistag
    categories, this routine just builds a RooRealVar for a per-mode mistag.
    
    When fitting mistag categories, however, one also needs per-category
    tagging efficiencies to make sure the normalisation of the PDF is not
    screwed up.

    config                   -- configuration dictionary
    ws                       -- workspace
    modename                 -- mode nickname
    yieldhint                -- helps setting initial error estimate (default: None)
    perCategoryTagEffsShared -- share tageffs across modes (default: True)
    perCategoryTagEffsConst  -- set tageffs constant (default: True)

    """

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
