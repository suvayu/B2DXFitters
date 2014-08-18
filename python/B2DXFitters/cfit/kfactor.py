"""k-factor utilities

"""


from . import ROOT
from ROOT import RooFit

from .utils import WS


# apply k-factor smearing
def applyKFactorSmearing(
        config,         # configuration dictionary
        ws,             # workspace
        time,           # time variable
        timeresmodel,   # time resolution model
        kvar,           # k factor variable
        kpdf,           # k factor distribution
        substtargets):  # quantities q to substitute k * q for
    if None == kpdf or None == kvar:
        return timeresmodel
    from ROOT import RooKResModel, RooArgSet
    paramobs = [ ]
    if config['NBinsTimeKFactor'] > 0:
        if not time.hasBinning('cache'):
            time.setBins(config['NBinsTimeKFactor'], 'cache')
        paramobs.append(time)
    timeresmodel = WS(ws, RooKResModel(
        '%s_%sSmeared' % (timeresmodel.GetName(), kpdf.GetName()),
        '%s_%sSmeared' % (timeresmodel.GetName(), kpdf.GetName()),
        timeresmodel, kpdf, kvar, RooArgSet(*substtargets),
        RooArgSet(*paramobs)))
    return timeresmodel
