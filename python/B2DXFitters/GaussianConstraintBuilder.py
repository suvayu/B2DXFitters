"""
@file GaussianConstraintBuilder.py

@author Manuel Schiller <manuel.schiller@nikhef.nl>
@date 2014-04-29

@brief build Gaussian constraints
"""

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
        from WS import WS as WS
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
        from WS import WS as WS
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
        from WS import WS as WS
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
        from WS import WS as WS
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
