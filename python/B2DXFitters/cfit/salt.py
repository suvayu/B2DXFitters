"""Provides fixes and workarounds for many ROOT eccentricities.

It also adds methods tos ROOT/RooFit classes so that they support
standard Python API for common tasks (e.g. iteration), language
constructs (e.g. `if .. in ..:'), etc.

To use these fixes/features, one should import ROOT from this module
before doing anything.

  >>> from B2DXFitters.cfit import ROOT
or
  >>> from B2DXFitters.cfit.salt import ROOT

@author Suvayu Ali
@email Suvayu dot Ali at cern dot ch
@date 2014-04-27 Sun

"""


import ROOT


## General helpers
def set_attribute(clss, attr, value):
    """For all cls in clss, set cls.attr to value.

    If value is a string, treat it is as an existing cls attribute and
    remap its value to attr (cls.attr = cls.value ).

    """
    def _setter(cls, attr, value):
        if isinstance(value, str):
            value = getattr(cls, value)
        setattr(cls, attr, value)
    try:
        for cls in clss:
            _setter(cls, attr, value)
    except TypeError:
        _setter(clss, attr, value)


## Ownership fixes
# list of creators
_creators = [
    ROOT.TObject.Clone,
    ROOT.TFile.Open,
    ROOT.RooAbsReal.clone,
    ROOT.RooAbsData.correlationMatrix,
    ROOT.RooAbsData.covarianceMatrix,
    ROOT.RooAbsData.reduce,
    ROOT.RooDataSet.binnedClone
]

# add create* and plot* methods to _creators
_attrs = {}
_attrs[ROOT.RooAbsReal] = [attr for attr in vars(ROOT.RooAbsReal)
                           if attr.find('create') == 0 or attr.find('plot') == 0]
_attrs[ROOT.RooAbsData] = [attr for attr in vars(ROOT.RooAbsData)
                           if attr.find('create') == 0 or attr.find('plot') == 0]

for cls, attrs in _attrs.items():
    for attr in attrs:
        _creators.append(getattr(cls, attr))
# cleanup temporary vars
del _attrs, cls, attrs, attr

def set_ownership(methods):
    """Tell Python, caller owns returned object by setting `clsmethod._creates'"""
    set_attribute(methods, '_creates', True)

set_ownership(_creators)


## ROOT/RooFit containers of different kinds
_roofit_containers = [
    ROOT.RooAbsCollection,
    ROOT.RooLinkedList
]

_root_containers = [
    ROOT.TCollection
]

# `if <item> in <container>:' construct
set_attribute(_roofit_containers, '__contains__', 'find')
set_attribute(_root_containers, '__contains__', 'FindObject')

# iteration for all RooFit containers
set_attribute(_roofit_containers, '__iter__', 'fwdIterator')

def new_next(iterator):
    el = iterator.old_next()        # call C++ version of cls.next()
    if el: return el
    else: raise StopIteration
set_attribute(ROOT.RooFIter, 'old_next', 'next') # save C++ verion of next
set_attribute(ROOT.RooFIter, 'next', new_next)   # reassign python version
set_attribute(ROOT.RooFIter, '__next__', 'next') # python 3 compatibility
del new_next


# ## Keyword conflict in Python
# ws_import = getattr(ROOT.RooWorkspace, 'import')
