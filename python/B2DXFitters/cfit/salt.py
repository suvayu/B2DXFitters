"""Provides fixes and workarounds for many ROOT eccentricities.

To use the fixes, one should import ROOT from this module before doing
anything.

  >>> from B2DXFitters.cfit import ROOT
or
  >>> from B2DXFitters.cfit.salt import ROOT

@author Suvayu Ali
@email Suvayu dot Ali at cern dot ch
@date 2014-04-27 Sun

"""


import ROOT

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
    def _setter(method):
        method._creates = True
    try:
        for method in methods:
            _setter(method)
    except TypeError:
        _setter(methods)

set_ownership(_creators)


# ## Keyword conflict in Python
# ws_import = getattr(ROOT.RooWorkspace, 'import')
