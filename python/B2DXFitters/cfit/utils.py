"""ROOT, RooFit, and cFit utilities

"""


import ROOT
from ROOT import RooFit


# Hack around RooWorkspace.import() and python keyword import clash
ws_import = getattr(ROOT.RooWorkspace, 'import')


def _import_args(namespace, d = {}):
    """Import attributes from namespace to local environment.

    namespace -- namespace to import attributes from
    d         -- dictionary that is returned with attributes
                 and values (default: empty dict, leave it
                 this way unless you know what you are doing)

    Usage:
      >>> opts = parser.parse_args(['foo', '-o', 'bar'])
      >>> locals().update(_import_args(opts))

    """
    attrs = vars(namespace)
    for attr in attrs:
        d[attr] = getattr(namespace, attr)
    return d


def WS(ws, obj, opts = [RooFit.RecycleConflictNodes(), RooFit.Silence()]):
    """ "swallow" object into a workspace, returns swallowed object """
    name = obj.GetName()
    wsobj = ws.obj(name)
    if obj.InheritsFrom('RooAbsArg') or obj.InheritsFrom('RooAbsData'):
        if None == wsobj:
            if len(opts) > 0:
                ws_import(ws, obj, *opts)
            else:
                ws_import(ws, obj)
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
            ws_import(ws, obj, name)
            wsobj = ws.obj(name)
        else:
            if wsobj.Class() != obj.Class():
                raise TypeError()
    return wsobj


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


class GaussianConstraintBuilder:
    """ builds constraints from a simple dictionary """

    def __init__(self, ws, constraints = { }):
        """
        @brief build constraints from a dictionary

        @param ws               workspace in which to look up variables
        @param constraints      dictionary of constraints to apply

        The constraint dictionary can have a number of forms for the entries:
        - 'paramname': error

          the parameter's current value is taken to be the central value, and a
          Gaussian constraint with that central value and the given error is
          applied

        - 'formulaname': [ 'formulaexp', [ 'par1', 'par2', ... ], mean, error ]

          construct a RooFormulaVar named formulaname with formula
          formulaexp, giving the arguments in the list as constructor
          arguments; then use a Gaussian constraint to bring the value
          of that formula to mean with an uncertainty of error

        - 'multivarSFX' : [ ['par1', 'par2', ... ], [ err1, err2, ... ], correlmat ]
              or
          'multivarSFX' : [ ['par1', 'par2', ... ], [ covariance matrix ]

          construct a multivariate Gaussian constraint for the given list of
          parameters; the parameter's current values are taken to be their
          mean values. one can either specify errors and correlation matrix,
          or give the covariance matrix directly. SFX is a suffix to
          distinguish different multivariate gaussian constraints
        """
        self._constraintlist = [ ]
        self._ws = ws
        for k in constraints:
            arg = constraints[k]
            if type(arg) == float:
                # simple constraints
                self.addSimpleConstraint(k, arg)
            elif k.startswith('multivar'):
                self.addMultiVarConstraint(k, *arg)
            elif type(arg) == list:
                self.addFormulaVarConstraint(k, *arg)
            else:
                raise TypeError('Unknown constraint type')

    def __buildSimpleConstraint(self, ws, parname, error):
        """ build a simple Gaussian constraint """
        from ROOT import RooConstVar, RooGaussian
        par = ws.obj(parname)
        if (None == par or not par.InheritsFrom('RooAbsReal') or
                par.InheritsFrom('RooConstVar')):
            raise TypeError(
                    'ERROR: Variable %s to constrain not found' % parname)
        mean = WS(ws, RooConstVar('%s_mean' % parname, '%s_mean' % parname,
            par.getVal()))
        err = WS(ws, RooConstVar('%s_err' % parname, '%s_err' % parname,
            error))
        # re-float par (if par was set constant)
        par.setConstant(False)
        par.setError(err.getVal())
        # append to list of constraints
        return WS(ws, RooGaussian(
            '%s_constraint' % parname, '%s_constraint' % parname,
            par, mean, err))

    def __buildFormulaVarConstraint(self, ws, formulaname, formulaexpression,
            paramnamelist, mean, error):
        """ build a RooFormulaVar constraint """
        from ROOT import RooFormulaVar, RooArgList, RooConstVar, RooGaussian
        al = RooArgList()
        for arg in paramnamelist:
            al.add(ws.obj(arg))
        fvar = WS(ws, RooFormulaVar(formulaname, formulaexpression, al))
        mean = WS(ws, RooConstVar('%s_mean' % formulaname,
            '%s_mean' % formulaname, mean))
        error = WS(ws, RooConstVar('%s_err' % formulaname, '%s_err' %
            formulaname, error))
        return WS(ws, RooGaussian('%s_constraint' % formulaname,
            '%s_constraint' % formulaname, fvar, mean, error))

    def __buildMultiVarConstraint(self, ws, name, paramnamelist,
            errorsOrCovariance, correlation = None):
        """ build multivariate Gaussian constraint """
        from math import sqrt
        from ROOT import ( RooConstVar, RooArgList, TMatrixDSym,
                RooMultiVarGaussian, TDecompChol )
        params = RooArgList()
        mus = RooArgList()
        for arg in paramnamelist:
            print arg
            param = ws.obj(arg)
            params.add(param)
            mus.add(WS(ws, RooConstVar('%s_mean' % arg, '%s_mean' % arg,
                param.getVal())))
        n = len(paramnamelist)
        # build and verify covariance matrix
        cov = TMatrixDSym(n)
        if None == correlation:
            # covariance matrix given directly - copy over and verify
            mat = errorsOrCovariance
            if len(mat) != n:
                raise ValueError('Covariance matrix dimension does not match that of parameter name list')
            for i in xrange(0, n):
                cov[i][i] = mat[i][i]
                if cov[i][i] <= 0.:
                    raise ValueError('Errors must be positive')
                for j in xrange(0, i):
                    # symmetrise by force
                    el = 0.5 * (mat[i][j] + mat[j][i])
                    # check if we're too far off
                    if ((abs(el) < 1e-15 and abs(mat[i][j]-mat[j][i]) > 1e-15) or
                            (abs(el) >= 1e-15 and abs(mat[i][j]-mat[j][i]) / el > 1e-15)):
                        raise ValueError('Covariance matrix not even approximately symmetric')
                    cov[i][j] = el
                    cov[j][i] = el # ROOT's insanity requires this
            # check for valid values of correlation
            for i in xrange(0, n):
                for j in xrange(0, i):
                    if abs(cov[i][j] / sqrt(cov[i][i] * cov[j][j])) > 1.0:
                        raise ValueError('Off-diagonal elements too large to form valid correlation')
        else:
            # have errors and correlation matrix
            errors = errorsOrCovariance
            if len(errors) != n:
                raise ValueError('Error list length does not match that of parameter name list')
            for i in xrange(0, n):
                if errors[i] <= 0.:
                    raise ValueError('Errors must be positive')
                cov[i][i] = errors[i] * errors[i]
            correl = correlation
            for i in xrange(0, n):
                if abs(correl[i][i] - 1.) > 1e-15:
                    raise ValueError('Correlation matrix has invalid element on diagonal')
                for j in xrange(0, i):
                    # symmetrise by force
                    el = 0.5 * (correl[i][j] + correl[j][i])
                    # check if we're too far off
                    if ((abs(el) < 1e-15 and abs(correl[i][j]-correl[j][i]) > 1e-15) or
                            (abs(el) >= 1e-15 and abs(correl[i][j]-correl[j][i]) / el > 1e-15)):
                        raise ValueError('Correlation matrix not even approximately symmetric')
                    if abs(el) > 1.:
                        raise ValueError('Off-diagonal elements too large to form valid correlation')
                    # convert to covariance
                    el = el * sqrt(cov[i][i] * cov[j][j])
                    cov[i][j] = el
                    cov[j][i] = el # ROOT's insanity requires this
        # verify we can invert covariance matrix with Cholesky decomposition
        # (this will catch negative and zero Eigenvalues)
        isposdef = False
        while not isposdef:
            decomp = TDecompChol(cov)
            isposdef = decomp.Decompose()
            if not isposdef:
                print 'ERROR: Covariance matrix not positive definite!'
            from ROOT import TVectorD
            vv = TVectorD()
            cov.EigenVectors(vv)
            v = [ vv[i] for i in xrange(0, n) ]
            if min(v) < 1e-16 or isposdef:
                if min(v) <= 0.:
                    print 'WARNING: Attempting to fix non-postive-definiteness...'
                else:
                    print 'WARNING: Covariance matrix very close to singular, trying to regularise...'
                print 'DEBUG: Covariance matrix before fix:'
                cov.Print()
                print 'DEBUG: Eigenvalue spectrum:'
                vv.Print()
                eps = 1.1 * abs(min(v))
                if eps < 1e-9: eps = 1e-9
                print 'DEBUG: adding %e to diagonal' % eps
                for i in xrange(0, n):
                    cov[i][i] = cov[i][i] + eps
                print 'DEBUG: Covariance matrix after fix:'
                cov.Print()
        # all set up, construct final multivariate Gaussian
        mvg = WS(ws, RooMultiVarGaussian(name, name, params, mus, cov))
        # make sure we float all parameters given
        i = 0
        for arg in paramnamelist:
            param = ws.obj(arg)
            param.setConstant(False)
            param.setError(sqrt(cov[i][i]))
            i = i + 1
        # all done
        return mvg

    def addUserConstraint(self, constraint):
        """ add given constraint to list of constraints """
        self._constraintlist.append(WS(self._ws, constraint))

    def addSimpleConstraint(self, parname, error):
        """
        add a simple gaussian constraints

        parname -- parameter name to be constrained
                   (looks up parname in workspace supplied at construction,
                   using the parameter's current value as the desired mean)
        error   -- width of the Gaussian constraint
        """
        self._constraintlist.append(
                self.__buildSimpleConstraint(self._ws, parname, error))

    def addMultiVarConstraint(self, name, paramnamelist, errorsOrCovariance,
            correlation = None):
        """
        add a multivariate Gaussian constraints

        name                    -- name of constraint
        paramnamelist           -- list of variables to be constrained
        errorsOrCovariance      -- either vector of errors, or full covariance
                                   matrix
        correlation             -- correlation matrix if errorsOrCovariance is
                                   a vector of errors, None otherwise

        paramnamelist is a list of variables to be looked up in the workspace
        supplied during construction; their mean values are taken to be the
        current values of the variables named in paramnamelist
        """
        self._constraintlist.append(self.__buildMultiVarConstraint(
            self._ws, name, paramnamelist, errorsOrCovariance, correlation))

    def addFormulaVarConstraint(self, formulaname, formulaexpression,
            paramnamelist, mean, error):
        """
        allow the value of a RooFormulaVar to be constrained (e.g. to constrain averages and differences etc)

        formulaname             -- name of constraint
        formulaexpression       -- formula, e.g. '@0-@1'
        paramnamelist           -- list of parameters to be supplied
        mean                    -- desired central value of formula's value
        error                   -- desired uncertainty of formula's value

        paramnamelist is a list of variables to be looked up in the workspace
        supplied during construction
        """
        self._constraintlist.append(self.__buildFormulaVarConstraint(
            self._ws, formulaname, formulaexpression, paramnamelist, mean, error))

    def getSetOfConstraints(self):
        """ return set of constraints """
        from ROOT import RooArgSet
        argset = RooArgSet('constraints')
        for c in self._constraintlist:
            argset.add(c)
        return argset
