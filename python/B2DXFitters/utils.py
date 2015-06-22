"""
@file utils.py

@author Manuel Schiller <Manuel.Schiller@cern.ch>
@date 2015-05-24

@brief various little utilities
"""

def setConstantIfSoConfigured(config, obj, recache = {}):
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
               empty dictionary ({}); if you call setConstantIfSoConfigured
               many times with the same config dictionary, you can supply your
               own empty dictionary here on the first call which will be used
               to store the compiled forms of the regular expressions used, so
               you can avoid their recompilation during subsequent calls
    
    Example: to set all asymmetries (those containing "Asym" in the RooFit
    object name) and the D parameter ('Bs2DsK_D') constant, you would use:
    @code
    configDict = { 'constParams': [ '.*Asym.*', 'Bs2DsK_D' ] }
    setConstantIfSoConfigured(configDict, mypdf)
    @endcode
    """
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

