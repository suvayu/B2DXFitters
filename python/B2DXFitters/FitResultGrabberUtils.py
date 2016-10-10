# @file FitResultGrabberUtils.py
#
# @brief utility routines for grabbing a fit result from a specified file (this is somewhat cFit/sFit specific)
#
# @author Manuel Schiller <manuel.schiller@nikhef.nl>
# @data 2014-05-11

import B2DXFitters
import ROOT
from ROOT import *
from ROOT import RooFit
import array
from array import array

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

def CreatePullTree(fileNamePull, rooFitResult, extGenDict = None):
    """
    create tree with fitted value, fitted error and generated (or initial) value for each
    floating variable in a fit
    
    fileNamePull -- output file
    rooFitResult -- RooFitResult object obtained from the fit

    if extGenDict != None, the generated value for each parameter is taken from an external dictionary
    of the form extGenDict = {parName : genValue, etc...}.
    This is useful when the generated value is somehow external to the code this function is used
    extGenDict can also contain only a subset of the parameters; the others are taken from rooFitResult
    """

    if None == rooFitResult:
        print "FitResultGrabberUtils.CreateToyPullTree(...)==> ERROR: RooFitResult is null."
        exit(-1)

    covqual = rooFitResult.covQual()
    status = rooFitResult.status()
    edm = rooFitResult.edm()

    print "FitResultGrabberUtils.CreateToyPullTree(...)==> Creating TTree to store fit results."
    if extGenDict != None:
        print "FitResultGrabberUtils.CreateToyPullTree(...)==> Taking (some) generated values from following dictionary:"
        print extGenDict

    initpar = rooFitResult.floatParsInit()
    floatpar = rooFitResult.floatParsFinal()

    filePull = TFile.Open(fileNamePull, "RECREATE")
    filePull.cd()
    treePull = TTree("PullTree","PullTree")
    floatlist = []
    errlist = []
    initlist = []

    for i in range(0, floatpar.getSize()):
        print "Setting " + floatpar[i].GetName() + " fitted value branch..."
        floatlist.append(array( 'f', [0] ))
        treePull.Branch(str(floatpar[i].GetName()) + "_fit", floatlist[i], str(floatpar[i].GetName()) + "_fit/F")
        floatlist[i][0] = floatpar[i].getVal()
        print "...value ", floatlist[i][0]
        
        print "Setting " + floatpar[i].GetName() + " fitted error branch..."
        errlist.append(array( 'f', [0] ))
        treePull.Branch(str(floatpar[i].GetName()) + "_err", errlist[i], str(floatpar[i].GetName()) + "_err/F")
        errlist[i][0] = floatpar[i].getError()
        print "...value ", errlist[i][0]

        print "Setting " + floatpar[i].GetName() + " generated value branch..."
        initlist.append(array( 'f', [0] ))
        treePull.Branch(str(floatpar[i].GetName()) + "_gen", initlist[i], str(floatpar[i].GetName()) + "_gen/F")
        if extGenDict == None:
            initlist[i][0] = initpar[i].getVal()
        else:
            if floatpar[i].GetName() in extGenDict.keys():
                print "...take from dictionary"
                initlist[i][0] = extGenDict[floatpar[i].GetName()]
            else:
                initlist[i][0] = initpar[i].getVal()
        print "...value ", initlist[i][0]
            

    print "Setting fit quality branches"
    covqualvar = array( 'f', [0] )
    statusvar = array( 'f', [0] )
    edmvar = array( 'f', [0] )

    treePull.Branch("CovQual", covqualvar, "CovQual/F")
    treePull.Branch("MINUITStatus", statusvar, "MINUITStatus/F")
    treePull.Branch("edm", edmvar, "edm/F")

    covqualvar[0] = covqual
    statusvar[0] = status
    edmvar[0] = edm

    treePull.Fill()

    treePull.Write("",TObject.kWriteDelete)
    filePull.ls()
    treePull.Print()
    filePull.Close()
