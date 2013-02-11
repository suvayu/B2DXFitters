#!/usr/bin/env python
# coding=utf-8
"""
Calculate correction factors (k-factors) for partially reconstructed
background to Bs⁰ → DsK.

  - B(d,s) → Ds⁽*⁾K⁽*⁾
  - Bs → Ds⁽*⁾(π,ρ)

"""

# Python standard libraries
import os
import sys
from optparse import OptionParser

# for B2DXFitters C++ classes
if 'CMTCONFIG' in os.environ:
    import GaudiPython
# ROOT globals
import ROOT
from ROOT import gROOT
gROOT.SetBatch(True)

# ROOT classes
from ROOT import TTree, TFile, TClass

# RooFit classes
from ROOT import RooFit
from ROOT import RooPlot, RooWorkspace, RooFitResult
from ROOT import RooArgSet, RooArgList
from ROOT import RooAbsReal, RooRealVar, RooRealConstant, RooFormulaVar
from ROOT import RooAbsPdf, RooGaussian
from ROOT import RooGenericPdf, RooEffProd, RooAddPdf, RooProdPdf, RooHistPdf
from ROOT import RooDataSet, RooDataHist
from ROOT import RooDecay, RooGaussModel, TString, TLorentzVector

# avoid memory leaks - will have to explicitly relinquish and acquire ownership
# if required, but PyROOT does not do what it thinks best without our knowing
# what it does
ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
if not 'CMTCONFIG' in os.environ:
    # enable ROOT to understand Reflex dictionaries
    ROOT.gSystem.Load('libCintex')
    ROOT.Cintex.Enable()
# load our own B2DXFitters library
if 'CMTCONFIG' in os.environ:
    GaudiPython.loaddict('B2DXFittersDict')
else:
    # running in standalone mode, we have to load things ourselves
    ROOT.gSystem.Load(os.environ['B2DXFITTERSROOT'] +
	    '/standalone/libB2DXFitters')

Utils = ROOT.MassFitUtils
# Models = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

datasetlist = os.environ['B2DXFITTERSROOT']+'/data/config_Bs2Dsh2011TDAna_Bs2DsK.txt'

PIDcut = 10
PIDmisscut= 0
pPIDcut = 5
Pcut_down = 0.0
Pcut_up = 100000000000.0
BDTGCut = 0.50
Dmass_down = 1948
Dmass_up = 1990


def cpp_to_pylist(cpplist):
    """Convert a C++ list (from PyROOT) to a Python list.

    NB: Calling this empties the original C++ list.

    """
    pylist = []
    for i in range(cpplist.size()):
        pylist.append(cpplist.back())
        cpplist.pop_back()
    return pylist


def get_workspace(mvarname, mass_win):
    """Get a workspace with all the datasets for partially
    reconstructed background.

    """
    ffile = TFile('treedump.root', 'recreate')

    workspace = Utils.getSpecBkg4kfactor(TString(datasetlist),
	    TString('#Kfactor MC FileName MU'),
	    TString('#Kfactor MC TreeName'),
	    PIDcut, PIDmisscut, pPIDcut, Pcut_down, Pcut_up, BDTGCut,
	    Dmass_down, Dmass_up, TString(mvarname),
	    TString('BsDsK'), 0, ffile, mass_win)
    workspace = Utils.getSpecBkg4kfactor(TString(datasetlist),
	    TString('#Kfactor MC FileName MD'),
	    TString('#Kfactor MC TreeName'),
	    PIDcut, PIDmisscut, pPIDcut, Pcut_down, Pcut_up, BDTGCut,
	    Dmass_down, Dmass_up, TString(mvarname),
	    TString('BsDsK'), workspace, ffile, mass_win)

    ffile.Close()

    if debug:
        print 'Dataset read from ntuples.\n', '=' * 50
        workspace.Print()
        print '=' * 50
    return workspace

# options
_usage = '%prog [options]'
parser = OptionParser( _usage )
parser.add_option('-o', '--outfile', dest='fname',
                  default=os.environ['B2DXFITTERSROOT']+'/data/workspace/kfactor_wspace.root',
                  help='Filename with saved workspace')
parser.add_option('--mvar', dest='mvar',
                   default='lab0_MassFitConsD_M',
                   help = 'set observable')
parser.add_option('--tvar', dest='tvar',
                   default='lab0_LifetimeFit_ctau',
                   help='set observable')
parser.add_option('--nomasswin', dest='mass_win',
                  action='store_false', default=True,
                  help='Filename with saved workspace')
parser.add_option('-d', '--debug', dest='debug',
                  action='store_true', default=False,
                  help='Filename with saved workspace')


if __name__ == "__main__":

    (options, args) = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        exit(-1)

    fname = options.fname
    mVar = options.mvar
    tVar = options.tvar
    debug = options.debug
    mass_win = options.mass_win

    workspace = get_workspace(mVar, mass_win)
    workspace.writeToFile(fname)
