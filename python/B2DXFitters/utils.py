"""
@file utils.py

@author Manuel Schiller <manuel.schiller@nikhef.nl>
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

