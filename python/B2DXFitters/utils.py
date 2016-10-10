"""
@file utils.py

@author Manuel Schiller <Manuel.Schiller@cern.ch>
@date 2015-05-24

@brief various little utilities
"""

def setConstantIfSoConfigured(config, obj, recache = None):
    """
    sets the desired parameters constant

    arguments:
    config --  a configuration which contains an entry 'constParams'; this
               entry contains a list of strings or regular expressions which
               should be set constant
    obj --     object on which the matching terms should be set constant; this
               is typically the top level pdf; setConstantIfSoConfigured
               recurses through the tree of RooFit objects rooted at obj, and
               finds the relevant nodes to set constant
    recache -- optional argument normally not given, default value is the
               None; if you call setConstantIfSoConfigured many times with the
               same config dictionary, you can supply your own empty dictionary
               here on the first call which will be used to store the compiled
               forms of the regular expressions used, so you can avoid their
               recompilation during subsequent calls
    
    Example: to set all asymmetries (those containing "Asym" in the RooFit
    object name) and the D parameter ('Bs2DsK_D') constant, you would use:
    @code
    configDict = { 'constParams': [ '.*Asym.*', 'Bs2DsK_D' ] }
    setConstantIfSoConfigured(configDict, mypdf)
    @endcode
    """
    from ROOT import RooAbsArg, RooRealVar, RooConstVar, RooArgSet
    if None == recache:
        recache = {}
        import re
        for rexp in config['constParams']:
            recache[rexp] = re.compile(rexp)
    if obj.InheritsFrom(RooRealVar.Class()):
        if obj.isConstant(): pass
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

def randomiseParameters(config, obj, seed, debug, dict = {}):
    """
    re-assign values to parameters taking them
    from a uniform distribution having boundaries equal to
    the parameters boundaries.
    It returns a dictionary containing of the form:
    @code
    {parameter name : value before randomisation}
    @endcode
    This is useful for pulls distributions on toys if the generation
    value is the initial value in the fit (one doesn't want to loose it...)
    This dictionary can then be given as input to the
    FitResultGrabberUtils.CreatePullTree function.
    
    Typical use-case: randomize initial guess on floating
    parameter in a fit to check stability on toys.

    config -- configuration file having the following structure:
    @code
    config['randomiseParams'] = {'parName' : {'min': min, 'max': max}}
    @endcode
    where min and max are the boundaries of the uniform distribution
    used for the generation.
    Regular expressions for parName are allowed.
    obj -- the parent structure (e.g. a RooAbsPdf)
    seed -- the seed used for the random generation
    debug -- if true, print out some information
    dict -- the returned dictionary with parameter name and initial value
    """

    from ROOT import RooAbsArg, RooRealVar, RooConstVar, RooArgSet, TRandom3

    if obj.InheritsFrom(RooRealVar.Class()):
        if obj.isConstant():
            pass
        r = TRandom3()
        r.SetSeed(seed)
        for var in config['randomiseParams'].iterkeys():
            if var == obj.GetName() and var not in dict.keys():
                dict[obj.GetName()] = {}
                dict[obj.GetName()] = obj.getVal()
                val = r.Uniform(config['randomiseParams'][var]['min'], config['randomiseParams'][var]['max'])
                if debug:
                    print "B2DXFitters.utils.randomiseParameters(..) => Parameter "+obj.GetName()
                    print "...Initial guess "+str(obj.getVal())
                    print "...New guess "+str(val)
                    obj.setVal( val )
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
            if None == o:
                break
            else:
                # randomise desired RooRealVar-derived objects
                randomiseParameters(config, o, seed, debug, dict)
    else:
        # ignore everything else
        pass


def printPDFTermsOnDataSet(dataset, terms = []):
    """
    print the values of various terms in a pdf for each entry in a data set

    dataset --  data set for which to print terms
    terms --    python list of RooFit objects whose values should be printed
                for each entry in the data set

    This routine is mostly useful to debug cases where something in the PDF
    calculation goes wrong (inside user C++ code, or because of invalid
    entries in the data sample).
    """
    import ROOT
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

def updateConfigDict(configDict, updateDict, allowOnlyKnownKeys = True):
    """
    updates a configuration dictionary with contents of a second dictionary

    configDict          -- config dictionary to update
    updateDict          -- dictionary with updates
    allowOnlyKnownKeys  -- if True, new keys in updateDict must already exist
                           in configDict for the update to succeed; this is a
                           primitive form of protection against typos in config
                           files
                           if False, any update is allowed (to allow quick and
                           dirty hacks that don't mention every possible key in
                           the initial dictionary

    returns the updated dictionary
    """
    for k in updateDict.keys():
        if allowOnlyKnownKeys and k not in configDict:
            raise KeyError(('Configuration dictionary: unknown '
                'key %s, aborting.') % k)
    configDict.update(updateDict)
    return configDict

def configDictFromString(s, where = 'unknown location'):
    """
    parses a string of python code, extracting a dictionary from it

    s       -- string to interpret as python
    where   -- origin of string (file, name of environment variable, ...)
               for error reporting

    returns dictionary
    """
    d = eval(compile(s, where, 'eval'))
    if dict != type(d):
        raise TypeError(('configuration from %s does not evaluate '
            'to dictionary') % where)
    return d

def configDictFromFile(name):
    """
    read a python dictionary from a config file

    name -- file name

    returns config dictionary
    """
    lines = file(name, 'r').readlines()
    return configDictFromString(''.join(lines), name)

def PytoTreeLeaves(type):
        """
        convert python datatype to TTree ROOT datatype
        """

        typecode = None
        if type == 'h':
            typecode = 'S'
        elif type == 'i':
            typecode = 'I'
        elif type == 'f':
            typecode = 'F'
        elif type == 'd':
            typecode = 'D'
        else:
            print "utils.PytoTreeLeaves(...) ==> ERROR: Python typecode " + type + " is not handled"
            exit(-1)
            
        return typecode


def TreeLeavesToPy(type):
        """
        convert TTree ROOT datatype to python datatype
        """
        
        typecode = None
        if type == 'S':
            typecode = 'h'
        elif type == 'I':
            typecode = 'i'
        elif type == 'F':
            typecode = 'f'
        elif type == 'D':
            typecode = 'd'
        else:
            print "utils.TreeLeavesToPy(...) ==> ERROR: TTree type " + type + " is not handled"
            exit(0)
            
        return typecode
