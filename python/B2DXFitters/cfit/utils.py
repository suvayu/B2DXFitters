"""ROOT, RooFit, and cFit utilities

"""


# TODO: move WS, and GaussianConstraintBuilder here

def setConstantIfSoConfigured(config, obj, recache = {}):
    from ROOT import RooAbsArg, RooRealVar, RooConstVar, RooArgSet
    if 0 == len(recache):
        import re
        for rexp in config['constParams']:
            recache[rexp] = re.compile(rexp)
    if obj.InheritsFrom(RooRealVar.Class()):
        # set desired RooRealVar-derived objects to const
        for rexp in recache:
            if recache[rexp].match(obj.GetName()):
                obj.setConstant(True)
                break
    elif obj.InheritsFrom(RooConstVar.Class()):
        # ignore RooConstVar instances - these are constant anyway
        pass
    elif obj.InheritsFrom(RooAbsArg.Class()):
        # for everything else, descend hierarchy of RooFit objects to find
        # RooRealVars which might need to be set to constant
        v = RooArgSet()
        obj.treeNodeServerList(v)
        v.remove(obj)
        it = v.fwdIterator()
        while True:
            o = it.next()
            if None == o: break
            setConstantIfSoConfigured(config, o, recache)
    else:
        # ignore everything else
        pass


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


def updateConfigDict(configDict, updateDict):
    import sys
    for k in updateDict.keys():
        if k not in configDict:
            print 'Configuration dictionary: unknown key %s, aborting.' % k
            sys.exit(1)
    configDict.update(updateDict)
    return configDict
