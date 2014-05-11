# @file FitResultGrabberUtils.py
#
# @brief utility routines for grabbing a fit result from a specified file (this is somewhat cFit/sFit specific)
#
# @author Manuel Schiller <manuel.schiller@nikhef.nl>
# @data 2014-05-11

import B2DXFitters
import ROOT
from ROOT import RooFit

def grabResult(isData, isBlind, filename):
    from B2DXFitters.FitResult import getDsHBlindFitResult
    from ROOT import TFile, RooFitResult, TClass
    import gc
    f = TFile(filename, "READ")
    # try to read cFit style fitresult
    for key in f.GetListOfKeys():
        if not TClass.GetClass(key.GetClassName()).InheritsFrom('RooFitResult'):
            continue
        fitresult = key.ReadObj()
        ROOT.SetOwnership(fitresult, True)
        retVal = getDsHBlindFitResult(isData, isBlind, fitresult)
        del fitresult
        f.Close()
        del f
        # make sure we don't run out of memory
        gc.collect()
        return retVal
    # ok, not successful, try sFit next
    for key in f.GetListOfKeys():
        if not TClass.GetClass(key.GetClassName()).InheritsFrom('RooWorkspace'):
            continue
        ws = key.ReadObj()
        if None == ws: continue
        ROOT.SetOwnership(ws, True)
        # ok, get list of objects in the workspace, and try to get a
        # RooFitResult from it
        l = ws.allGenericObjects()
        ROOT.SetOwnership(l, True)
        while not l.empty():
            obj = l.front()
            if None == obj or not obj.InheritsFrom('RooFitResult'):
                l.pop_front()
                continue
            retVal = getDsHBlindFitResult(isData, isBlind, obj)
            del obj
            del l
            del ws
            f.Close()
            del f
            # make sure we don't run out of memory
            gc.collect()
            return retVal
    # make sure we don't run out of memory
    gc.collect()
    return None
