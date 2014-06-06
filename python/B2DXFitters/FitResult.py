"""
@file FitResult.py

@author Manuel Schiller <manuel.schiller@nikhef.nl>
@date 2014-04-03

wrap RooFitResults, and make sure you can print blinded fit results
"""

class FitResult:
    """ class to wrap RooFitResults """

    _defaultBlindingString = (
                'The Hitchhiker\'s Guide to the Galaxy has a few things to '
                'say on the subject of towels. A towel, it says, is about '
                'the most massively useful thing an interstellar hitch '
                'hiker can have.')
    _knownOptions = (
            'SameDataSet',      # if this is set, subtracted fit results
                                # have their errors calculated using the
                                # sqrt(|sigma_1^2 - sigma_2^2|) rule, and
                                # the off-diagonal elements of the
                                # covariance matrix probably don't mean
                                # much; if this is absent, the covariances
                                # are added, as usual

            'PrettyPrint',      # pretty-print the result when converting to
                                # string (not all significant digits, might
                                # have other effects in the future

	    'Systematic',	# systematic study, differences for pulls
	    			# are divided by errors of first (nominal)
				# result
            )

    def __convArgList(self, al):
        """ return a python list of RooFit objects """
        retVal = [ ]
        it = al.fwdIterator()
        obj = it.next()
        while None != obj:
            retVal.append(obj)
            obj = it.next()
        return retVal

    def __copyParams(self, al, dst, proj = lambda o: o.getVal()):
        """ tiny little helper """
        for var in al:
            if var.GetName() in self._name2Index:
                idx = self._name2Index[var.GetName()]
            else:
                idx = len(self._name2Index)
                self._name2Index[var.GetName()] = idx
                self._index2Name[idx] = var.GetName()
            dst[idx] = proj(var)

    def __init__(self, roofitresult, renamemap = { }, blindmap = { },
            options = [ 'PrettyPrint' ], blindstr = _defaultBlindingString):
        """
        convert a RooFit result to a python object

        bells and whistles:
        - can (optionally) rename some parameters; this is useful to compare
          results from different fits (and different naming conventions)
        - can (optionally) blind some parameters

        arguments:
        roofitresult    --- RooFit RooFitResult class
        renamemap       --- map of { 'oldname': 'newname' } pairs
        blindmap        --- map of (variable names/regexes, blinding width)
                            to be blinded
        blindstr        --- blinding string
        options         --- options

        further explanations:
        - blindmap = { 'Bs2DsK_(C|D|Dbar|S|Sbar)': [ -3., 3. ] } would match
          variable names Bs2DsK_C, Bs2DsK_D, Bs2DsK_Dbar, Bs2DsK_S,
          Bs2DsK_Sbar, and would cause the reported values to be a random
          value between -3. and +3 (flat distribution) from which you
          randomly add/subtract the true value.
        - the blinding applied depends only on the blinding string and the
          parameter name (after renaming)
        - blinding shifts the final parameters, but not the initial ones
          (otherwise, you could tell from the initial parameter what the
          blinding offset is)
        - options is a list of options, currently, the only supported value
          is 'SameDataSet', 'Systematic', or 'PrettyPrint'
        - in case more than one regex in blindmap matches, the longest match
          wins

        Example:

        # get RooFitResult from somewhere
        roofitresult = # ...
        # construct FitResult from it
        fitresult = FitResult(roofitresult,
                { 'C': 'Bs2DsK_C', 'D': 'Bs2DsK_D',
                  'Dbar': 'Bs2DsK_Dbar', 'S': 'Bs2DsK_S',
                  'Sbar': 'Bs2DsK'Sbar', 'DeltaMs': 'deltaMs' },
                { '^Bs2DsK_(C|D|Dbar|S|Sbar)$': [ -3.0, 3.0 ] })
        # this renames sFit variables to the cFit conventions
        # it also blinds the CP parameters with a random offset in the range
        # from -3. to 3.; the funny string is a regular expression;
        # alternatively, you can also list variable names, and things will
        # most likely work (if you don't have funny characters in your
        # names, and if variable names are not substrings of other variable
        # names)
        #
        # next, delete roofitresult!
        del roofitresult
        # print the appropriately blinded result
        print fitresult
        """
        self._name2Index = { }
        self._index2Name = { }
        self._constparam = { }
        self._initialparam = { }
        self._finalparam = { }
        self._finalparamlimlo = { }
        self._finalparamlimhi = { }
        self._blindingOffsets = { }
        self._blindingSigns = { }
        self._status = 4
        self._covQual = 0
        self._cov = { }
        self._fcn = float('nan')
        self._edm = float('nan')
        self._options = [ ]

        if None == roofitresult: return

        # copy status, covQual, FCN, EDM, options
        self._status = roofitresult.status()
        self._covQual = roofitresult.covQual()
        self._fcn = roofitresult.minNll()
        self._edm = roofitresult.edm()
        self.setOptions(options)

        # work on floating parameters
        al = self.__convArgList(roofitresult.floatParsFinal())
        self.__copyParams(al, self._finalparam)
        self.__copyParams(al, self._finalparamlimlo, lambda o: o.getMin())
        self.__copyParams(al, self._finalparamlimhi, lambda o: o.getMax())
        al = self.__convArgList(roofitresult.floatParsInit())
        self.__copyParams(al, self._initialparam)

        # get covariance matrix
        mat = roofitresult.covarianceMatrix()
        for i in xrange(0, len(self._finalparam)):
            self._cov[i] = { }
            for j in xrange(0, i + 1):
                self._cov[i][j] = mat[i][j]
                if i != j:
                    self._cov[j][i] = mat[i][j]

        # work on fixed parameters
        al = self.__convArgList(roofitresult.constPars())
        self.__copyParams(al, self._constparam)

        # rename and perform blinding (as required)
        import re, random
        newn2i = { }
        newi2n = { }
        blindres = { }
        for rexp in blindmap:
            blindres[re.compile(rexp)] = blindmap[rexp]
        rnd = random.Random()
        for name in self._name2Index:
            idx = self._name2Index[name]
            oldname = name
            newname = name if not name in renamemap else renamemap[name]
            # record the new mapping
            newn2i[newname] = idx
            newi2n[idx] = newname
            # check if the parameter is to be blinded
            # no blinding for parameters that do not float
            if not idx in self._finalparam: continue
            blind, ofs = False, [ 0., 0. ]
            mlen = 0
            for re in blindres:
                m1 = re.match(oldname)
                m2 = re.match(newname)
                if m1 or m2:
                    blind = True
                    if m1 and mlen <= (m1.end() - m1.start()):
                        ofs = [ float(blindres[re][0]),
                                float(blindres[re][1]) ]
                        mlen = m1.end() - m1.start()
                    if m2 and mlen <= (m2.end() - m2.start()):
                        ofs = [ float(blindres[re][0]),
                                float(blindres[re][1]) ]
                        mlen = m2.end() - m2.start()
            if not blind:
                self._blindingOffsets[idx] = 0.
                self._blindingSigns[idx] = 1.
                continue
            # blinding offset should be the same for variables of the
            # same name; for that reason, we concatenate the blinding
            # string and the (renamed) variable name and seed rnd with
            # it
            rnd.seed(blindstr + newname)
            # flat between -ofs and ofs
            rofs = rnd.uniform(ofs[0], ofs[1])
            sign = -1. if rnd.random() < 0.5 else 1.
            self._blindingOffsets[idx] = rofs
            self._blindingSigns[idx] = sign
            self._finalparam[idx] = rofs + sign * self._finalparam[idx]

        # put in new name-index mappings
        self._name2Index = newn2i
        self._index2Name = newi2n

    def status(self):
        """ return status """
        return self._status

    def covQual(self):
        """ return covariance quality """
        return self._covQual

    def edm(self):
        """ return edm """
        return self._edm

    def fcn(self):
        """ return function value at minimum """
        return self._fcn

    def constParams(self):
        """ return a dictionary (name, value) of constant parameters """
        retVal = { }
        for idx in self._constparam:
            retVal[self._index2Name[idx]] = self._constparam[idx]
        return retVal

    def params(self):
        """ return a dictionary (name, value) of floating parameters """
        retVal = { }
        for idx in self._finalparam:
            retVal[self._index2Name[idx]] = self._finalparam[idx]
        return retVal

    def initialParams(self):
        """ return a dictionary (name, value) of floating parameters
        (initial values) """
        retVal = { }
        for idx in self._initialparam:
            retVal[self._index2Name[idx]] = self._initialparam[idx]
        return retVal

    def errors(self):
        """ return a dictionary (name, value) of floating parameters """
        from math import sqrt
        retVal = { }
        for idx in self._cov:
            retVal[self._index2Name[idx]] = sqrt(self._cov[idx][idx])
        return retVal

    def paramLowerLimits(self):
        """
        return a dictionary (name, value) of floating parameters'
        lower limits
        """
        retVal = { }
        for idx in self._finalparamlimlo:
            retVal[self._index2Name[idx]] = self._finalparamlimlo[idx]
        return retVal

    def paramUpperLimits(self):
        """
        return a dictionary (name, value) of floating parameters'
        upper limits
        """
        retVal = { }
        for idx in self._finalparamlimhi:
            retVal[self._index2Name[idx]] = self._finalparamlimhi[idx]
        return retVal

    def pulls(self):
        """
        return a dictionary (name, value) of pulls
        
        NOTE: this returns nonsense if a parameter is blinded
        """
        from math import sqrt
        retVal = { }
        for idx in self._finalparam:
            pull = (self._finalparam[idx] - self._initialparam[idx])
            pull = pull / sqrt(self._cov[idx][idx])
            if self._blindingOffsets[idx] != 0.:
                pull = float('NaN')
            retVal[self._index2Name[idx]] = pull
        return retVal

    def options(self):
        """ return options """
        return self._options

    def setOptions(self, options):
        """ set option flags """
        for o in options:
            if not o in FitResult._knownOptions:
                raise 'Unknown option: %s' % str(o)
            if o in self._options: continue
            self._options.append(o)

    def clearOptions(self, options):
        """ clear option flags """
        for o in options:
            if not o in _knownOptions:
                raise 'Unknown option: %s' % str(o)
            if not o in self._options: continue
            self._options.remove(o)

    def __sub__(self, other):
        """
        subtract two fit results (returns self - other)

        remarks:
        - common parameters will be subtracted from each other
        - fcn is the difference in fcns
        - edm is the sum of edms
        - covQual is set to minimum of both covQuals
        - status is 0 if both input states are 0, else the larger non-zero
          input state is copied
        - if the 'SameDataSet' option is set on one of the two data sets,
          the covariances are subtracted from each other, and the absolute
          value of the differences is saved in each element
	- if the 'Systematic' option is set, the covariance matrix of the
	  first (nominal) result is kept
        - otherwise, the two covariance matrices are added
        - result has the union of options set
        - result has the blinding undone
        - limits on parameters become the most restrictive interval (maximum
          of lower limits, minimum of upper limits)
        """
        retVal = FitResult(None)
        retVal._status = max(self._status, other._status)
        if 0 == retVal._status:
            retVal._status = min(self._status, other._status)
        retVal._covQual = min(self._covQual, other._covQual)
        retVal._edm = self._edm + other._edm
        retVal._fcn = self._fcn - other._fcn
        retVal.setOptions(self._options)
        retVal.setOptions(other._options)

        # loop over floating parameters
        for sidx in self._index2Name:
            n = self._index2Name[sidx]
            idx = len(retVal._name2Index)
            if n not in other._name2Index: continue
            oidx = other._name2Index[n]
            # we verify that shared parameters are either constant in both
            # FitResults, or are both floating
            if (((sidx not in self._finalparam) or
                (oidx not in other._finalparam)) and 
                    ((sidx in self._finalparam) or
                        (oidx in other._finalparam))):
                print ('WARNING: Parameter %s constant in one FitResult, but '
                        'floating in the other' % n)
                continue
            if sidx not in self._finalparam: continue
            retVal._name2Index[n] = idx
            retVal._index2Name[idx] = n
            retVal._initialparam[idx] = 0.
            # unblind before we perform the difference
            subl = self._blindingSigns[sidx] * (self._finalparam[sidx] -
                    self._blindingOffsets[sidx]) 
            oubl = other._blindingSigns[oidx] * (other._finalparam[oidx] -
                    other._blindingOffsets[oidx]) 
            retVal._blindingOffsets[idx] = 0.
            # we copy the sign, so we don't know which is larger
            retVal._blindingSigns[idx] = self._blindingSigns[sidx]
            retVal._finalparam[idx] = retVal._blindingSigns[idx] * (subl -
                    oubl)
            retVal._finalparamlimlo[idx] = max(
                    self._finalparamlimlo[sidx],
                    other._finalparamlimlo[oidx])
            retVal._finalparamlimhi[idx] = min(
                    self._finalparamlimhi[sidx],
                    other._finalparamlimhi[oidx])

        # covariance matrix
        isSameDataSet = 'SameDataSet' in retVal._options
	isSystematic = 'Systematic' in retVal._options
        for i in xrange(0, len(retVal._index2Name)):
            n = retVal._index2Name[i]
            sidx = self._name2Index[n]
            oidx = other._name2Index[n]
            retVal._cov[i] = { }
            for j in xrange(0, i + 1):
                o = retVal._index2Name[j]
                sidy = self._name2Index[o]
                oidy = other._name2Index[o]
                val = ( (
                        abs(self._cov[sidx][sidy] - other._cov[oidx][oidy])
                        if isSameDataSet else
                        (self._cov[sidx][sidy] + other._cov[oidx][oidy])) if
			not isSystematic else self._cov[sidx][sidy])
                retVal._cov[i][j] = val
                if (i != j): retVal._cov[j][i] = val
        # loop over constant parameters
        for n in self._name2Index:
            idx = len(retVal._name2Index)
            if n not in other._name2Index: continue
            sidx = self._name2Index[n]
            oidx = other._name2Index[n]
            if (sidx not in self._constparam and oidx not in
                    other._constparam): continue
            if sidx in self._constparam: sval = self._constparam[sidx]
            else: sval = self._finalparam[sidx]
            if oidx in other._constparam: oval = other._constparam[oidx]
            else: oval = other._finalparam[oidx]
            retVal._name2Index[n] = idx
            retVal._index2Name[idx] = n
            retVal._constparam[idx] = (sval - oval)
        return retVal

    def __add__(self, other):
        """
        add (average) two fit results

        remarks:
        - common parameters will be averaged with full covariance info
        - fcn is the sum in fcns
        - edm is the sum of edms
        - covQual is set to minimum of both covQuals
        - status is 0 if both input states are 0, else the larger non-zero
          input state is copied
        - result has the union of options set
        - if at least one of the inputs was blind, so is the output
        - limits on parameters become the most restrictive interval (maximum
          of lower limits, minimum of upper limits)
        """
        retVal = FitResult(None)
        retVal._status = max(self._status, other._status)
        if 0 == retVal._status:
            retVal._status = min(self._status, other._status)
        retVal._covQual = min(self._covQual, other._covQual)
        retVal._edm = self._edm + other._edm
        retVal._fcn = self._fcn + other._fcn
        retVal.setOptions(self._options)
        retVal.setOptions(other._options)

        # loop over floating parameters
        for sidx in self._index2Name:
            n = self._index2Name[sidx]
            idx = len(retVal._name2Index)
            if n not in other._name2Index: continue
            oidx = other._name2Index[n]
            # we verify that shared parameters are either constant in both
            # FitResults, or are both floating
            if (((sidx not in self._finalparam) or
                (oidx not in other._finalparam)) and 
                    ((sidx in self._finalparam) or
                        (oidx in other._finalparam))):
                print ('WARNING: Parameter %s constant in one FitResult, but '
                        'floating in the other' % n)
                continue
            if sidx not in self._finalparam: continue
	    # also skip parameters which have ridiculously tiny errors in
	    # one of the fit results
	    if min(self._cov[sidx][sidx], other._cov[oidx][oidx]) < 1e-10:
                print ('WARNING: Parameter %s has tiny error in one FitResult, '
                        'skipping to avoid spoiling the average' % n)
		continue
            retVal._name2Index[n] = idx
            retVal._index2Name[idx] = n
            retVal._initialparam[idx] = 0.
            # unblind before we perform the difference
            subl = self._blindingSigns[sidx] * (self._finalparam[sidx] -
                    self._blindingOffsets[sidx]) 
            oubl = other._blindingSigns[oidx] * (other._finalparam[oidx] -
                    other._blindingOffsets[oidx]) 
            # we copy the sign and blinding offsef from the first argument,
            # or, if the first argument is not blinded, from the second argument
            retVal._blindingSigns[idx] = self._blindingSigns[sidx]
            retVal._blindingOffsets[idx] = self._blindingOffsets[sidx]
            if 0. == retVal._blindingOffsets[idx]:
                retVal._blindingSigns[idx] = other._blindingSigns[oidx]
                retVal._blindingOffsets[idx] = other._blindingOffsets[oidx]
            retVal._finalparam[idx] = [ subl, oubl ]
            retVal._finalparamlimlo[idx] = max(
                    self._finalparamlimlo[sidx],
                    other._finalparamlimlo[oidx])
            retVal._finalparamlimhi[idx] = min(
                    self._finalparamlimhi[sidx],
                    other._finalparamlimhi[oidx])
	# get inverse covariance matrices of two input fits
        from ROOT import TVectorD, TMatrixDSym, TDecompChol
	c = []
	for m in (self, other):
	    nn = len(m._cov)
	    c.append(TMatrixDSym(nn))
	    for i in xrange(0, nn):
		for j in xrange(0, nn):
		    c[len(c) - 1][i][j] = m._cov[i][j]
	    d = TDecompChol(c[len(c) - 1])
	    if not d.Decompose():
               raise ValueError('Cannot invert covariance matrices')
            d.Invert(c[len(c) - 1])
	# ok, now select submatrix we need
        for i in xrange(0, len(retVal._index2Name)):
            n = retVal._index2Name[i]
            sidx = self._name2Index[n]
            oidx = other._name2Index[n]
            retVal._cov[i] = { }
            for j in xrange(0, i + 1):
                o = retVal._index2Name[j]
                sidy = self._name2Index[o]
                oidy = other._name2Index[o]
                val = [ c[0][sidx][sidy], c[1][oidx][oidy] ]
                retVal._cov[i][j] = val
                if (i != j): retVal._cov[j][i] = val
	del c
        # loop over constant parameters
        for n in self._name2Index:
            idx = len(retVal._name2Index)
            if n not in other._name2Index: continue
            sidx = self._name2Index[n]
            oidx = other._name2Index[n]
            if (sidx not in self._constparam and oidx not in
                    other._constparam): continue
            if sidx in self._constparam: sval = self._constparam[sidx]
            else: sval = self._finalparam[sidx]
            if oidx in other._constparam: oval = other._constparam[oidx]
            else: oval = other._finalparam[oidx]
            retVal._name2Index[n] = idx
            retVal._index2Name[idx] = n
            # FIXME: What do we do  here? - does arithmetic average make
            # sense??!?
            retVal._constparam[idx] = 0.5 * (sval + oval)
        # perform weighted average with the "classical" formula:
        # mu = (C1^-1 + C2^-1)^-1 * (C1^-1 * mu1 + C2^-1 * mu2)
        # C =  (C1^-1 + C2^-1)^-1
        n = len(retVal._finalparam)
        v1, v2 = TVectorD(n), TVectorD(n)
        c1, c2 = TMatrixDSym(n), TMatrixDSym(n)
        for i in xrange(0, n):
            v1[i], v2[i] = retVal._finalparam[i][0], retVal._finalparam[i][1]
            for j in xrange(0, n):
                c1[i][j], c2[i][j] = retVal._cov[i][j][0], retVal._cov[i][j][1]
        c = TMatrixDSym(n)
        c = c1 + c2
        d = TDecompChol(c)
        if not d.Decompose():
            raise ValueError('Cannot invert covariance matrix')
        v1 = c1 * v1 + c2 * v2
        d.Solve(v1)
        d.Invert(c)
        # write back results (and reapply blinding)
        for i in xrange(0, n):
            retVal._finalparam[i] = (retVal._blindingOffsets[i] +
                    retVal._blindingSigns[i] * v1[i])
            for j in xrange(0, n):
                retVal._cov[i][j] = c[i][j]

        return retVal

    def __str__(self):
        """ print the fit result """
        from math import sqrt
        from sys import float_info
        retVal = ''
        formats = { 'n': '% 23.15e', 'c': '% 23.15e',
                'ns': '%23s', 'cs': '%23s' }
        if 'PrettyPrint' in self._options:
            formats = { 'n': '% 12.6g', 'c': '% 6.3f',
                    'ns': '%12s', 'cs': '%6s' }
        covCodes = { 0: 'UNAVAILABLE', 1: 'INACCURATE',
                2: 'FORCED POS. DEF.', 3: 'ACCURATE' }
        # print header
        retVal += 'FIT RESULT: FCN '
        retVal += formats['n'] % self.fcn()
        covstat = (covCodes[self.covQual()] if self.covQual() in covCodes
                else str(self.covQual()))
        retVal += ' STATUS % 2d COV %16s EDM ' % (self.status(), covstat)
        retVal += formats['n'] % self.edm()
        retVal += '\n'
        retVal += '\n'
        # start with parameters 
        retVal += '%2s %-24s %s %s %s\n\n' % ('NR', 'PARAMETER',
                formats['ns'] % 'INITIAL', formats['ns'] % 'FINAL',
                formats['ns'] % 'ERROR')
        for idx in self._finalparam:
            name = self._index2Name[idx]
            ini = self._initialparam[idx]
            fin = self._finalparam[idx]
            err = sqrt(self._cov[idx][idx])
            llo = self._finalparamlimlo[idx]
            lhi = self._finalparamlimhi[idx]
            # unblind, but DO NOT PRINT! (need it for the at/beyond limit
            # checks)
            ubl = self._blindingSigns[idx] * (self._finalparam[idx] -
                    self._blindingOffsets[idx]) 
            comment = ''
            if llo > -float_info.max or lhi < float_info.max:
                comment += ' L(%s, %s)' % (
                        formats['n'] % llo, formats['n'] % lhi)
            if 0. != self._blindingOffsets[idx]:
                comment += ' BLINDED'
            if llo >= ubl or ubl >= lhi:
                comment += ' *** AT LIMIT ***'
            retVal += '%2u %-24s %s %s %s%s\n' % (idx, name,
                    formats['n'] % ini, formats['n'] % fin, formats['n'] % err,
                    comment)
        # correlation matrix now
        retVal += '\nCORRELATION MATRIX\n\n%2s' % ''
        for idx in xrange(0, len(self._finalparam)):
            retVal += ' %s' % (formats['cs'] % ('%2u' % idx))
        retVal += '\n'
        for i in xrange(0, len(self._finalparam)):
            retVal += '%2u' % i
            for j in xrange(0, len(self._finalparam)):
                try:
                    val = (self._cov[i][j] /
                        sqrt(self._cov[i][i] * self._cov[j][j]))
                except:
                    val = float('nan')
                retVal += ' ' + formats['c'] % val
            retVal += '\n'
        # return string
        return retVal

def getDsHBlindFitResult(isData, isBlind, fitResult):
    """
    construct an object wrapping RooFitResult with the correct settings
    for the Bs -> Ds K/Pi CPV analysis which can be used to print blinded
    fit results

    isData - true if the fitResult is for Data
    isBlind - true if blinding is to be applied to data
    fitResult - RooFitResult to blind
    """
    doBlind = isData and isBlind
    # common setup: rename list, blinding specification
    renames = { 'C': 'Bs2DsK_C', 'D': 'Bs2DsK_D',
            'Dbar': 'Bs2DsK_Dbar', 'S': 'Bs2DsK_S',
            'Sbar': 'Bs2DsK_Sbar', 'DeltaMs': 'deltaMs',
            'p0_0': 'Bs2DsK_Mistag0CalibB_p0',
            'p0_1': 'Bs2DsK_Mistag1CalibB_p0',
            'p0_2': 'Bs2DsK_Mistag2CalibB_p0',
            'p1_0': 'Bs2DsK_Mistag0CalibB_p1',
            'p1_1': 'Bs2DsK_Mistag1CalibB_p1',
            'p1_2': 'Bs2DsK_Mistag2CalibB_p1',
            }
    blinds = {
            # CP parameters blinded with random offset from 13 ... 17
            '^Bs2DsK_(C|D|Dbar|S|Sbar)$': [ 13.0, 17.0 ],
	    # blind direct fits to gamma, strong and weak phase with offset 23 ... 27
	    '^Bs2DsK_(lambda|delta|phi_w)$': [ 23., 27. ],
            # everything else connected with DsK is blinded with random offset
            # from +3 ... +7 (efficiencies, calibrations, ...)
            '^Bs2DsK': [ 3.0, 7.0 ],
            }
    
    return FitResult(fitResult, renames, blinds if doBlind else { })

# vim: ft=python:sw=4:tw=76
