#!/usr/bin/python

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('-w', '--wspace', dest='rfile', help='Workspace filename')
optparser.add_argument('-t', '--tuple', dest='tpfile', help='Tuple filename')
optparser.add_argument('-n', '--nokfactor', action='store_true', help='Exclude k-factor')
optparser.add_argument('-m', '--mode', help='Decay mode')
optparser.add_argument('-b', '--bins', type=int, default=500, help='No. of time bins')
optparser.add_argument('-r', '--range', dest='trange', type=float, nargs=2, help='Plot range (in ps)')
optparser.add_argument('-o', '--output', dest='plotfile', help='Output filename (pdf)')
options = optparser.parse_args()
rfile = options.rfile
tpfile = options.tpfile
nokfactor = options.nokfactor
mode = options.mode
bins = options.bins
trange = options.trange
plotfile = options.plotfile

assert(rfile and tpfile and mode)
if not plotfile:
    plotfile = '{}.pdf'.format(rfile.rsplit('.',1)[0])


from ROOT import TFile, TTree, TChain, TH1D, TList, TCanvas

# custom
import B2DXFitters
from B2DXFitters.factory import get_title_from_mode, rescale_roofit_pad
from ROOT import (RooKResModel, Inverse, RooGaussEfficiencyModel,
                  RooCubicSplineFun)

# standard
from ROOT import (RooWorkspace, RooArgSet, RooArgList, RooFit,
                  RooRealVar, RooConstVar, RooRealConstant,
                  RooProduct, RooGaussModel, RooBDecay, RooDataSet,
                  RooBinning, RooPolyVar, RooProduct)

# globals, and aliases
from ROOT import gPad, gStyle, gSystem, kRed, kBlue, kAzure, kGreen, kBlack
const = RooRealConstant.value

# setup
gStyle.SetOptStat('nemrou')
canvas = TCanvas('canvas', 'canvas', 800, 600)
canvas.Print('{}['.format(plotfile))

# read workspace
ffile = TFile.Open(rfile, 'read')
workspace = ffile.Get('workspace')

pdfs = RooArgList(workspace.allPdfs())
for i in range(pdfs.getSize()):
    name = pdfs[i].GetName()
    if name.find(mode) >= 0:
        mykpdf = pdfs[i]
assert(mykpdf)

## variables
time = RooRealVar('time', 'Time [ps]', 0.2, 15.0)
time.setBins(bins)
time.setBins(bins*3, 'cache')

kfactor = workspace.var('kfactorVar')
kfactor.setRange(0.85, 1.05)
gamma = RooRealVar('gamma', 'gamma', 0.661, 0., 3.)
kgamma = RooProduct('kgamma', 'kgamma', RooArgList(gamma, kfactor))
dGamma = RooRealVar('dGamma', 'dGamma', -0.106, -3., 3.)
dM = RooRealVar('dM', 'dM', 17.768, 0.1, 20.)
C = RooRealVar('C', 'C', 1., 0., 2.)
one = const(1.)
zero = const(0.)
tau = Inverse('tau', 'tau', gamma)
# tauk = Inverse('tauk', 'tauk', kgamma)

## acceptance
spline_knots = [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ]
spline_coeffs = [ 5.03902e-01, 7.32741e-01, 9.98736e-01,
                  1.16514e+00, 1.25167e+00, 1.28624e+00 ]
assert(len(spline_knots) == len(spline_coeffs))

# knot binning
knotbinning = RooBinning(time.getMin(), time.getMax(),
                         '{}_knotbinning'.format(mode))
for v in spline_knots:
    knotbinning.addBoundary(v)
knotbinning.removeBoundary(time.getMin())
knotbinning.removeBoundary(time.getMax())
oldbinning, lo, hi = time.getBinning(), time.getMin(), time.getMax()
time.setBinning(knotbinning, '{}_knotbinning'.format(mode))
time.setBinning(oldbinning)
time.setRange(lo, hi)
del knotbinning, oldbinning, lo, hi

# knot coefficients
coefflist = RooArgList()
for i, v in enumerate(spline_coeffs):
    coefflist.add(const(v))
i = len(spline_coeffs)
coefflist.add(one)
spline_knots.append(time.getMax())
spline_knots.reverse()
fudge = (spline_knots[0] - spline_knots[1]) / (spline_knots[2] - spline_knots[1])
lastmycoeffs = RooArgList()
lastmycoeffs.add(const(1. - fudge))
lastmycoeffs.add(const(fudge))
polyvar = RooPolyVar('{}_SplineAccCoeff{}'.format(mode, i), '',
                     coefflist.at(coefflist.getSize() - 2), lastmycoeffs)
coefflist.add(polyvar)
del i

# create the spline itself
tacc = RooCubicSplineFun('{}_SplineAcceptance'.format(mode), '', time,
                         '{}_knotbinning'.format(mode), coefflist)
del lastmycoeffs, coefflist

## model with time resolution
# when using a spline acceptance
gres = RooGaussEfficiencyModel('{}_GaussianWithPEDTE'.format(tacc.GetName()),
                               '', time, tacc, const(0.0), const(0.044))
# # otherwise
# gres = RooGaussModel('gres', '', time, const(0.0), const(0.044))
if nokfactor:
    kgres = gres
else:
    kgres = RooKResModel('kgres', '', gres, mykpdf, kfactor, RooArgSet(gamma, dM, dGamma))
model = RooBDecay('model', 'k-factor smeared model', time, tau, dGamma,
                   one, zero, C, zero, dM, kgres, RooBDecay.SingleSided)

# read ntuple
ffile_tp = TFile(tpfile, 'read')
fkeys = ffile_tp.GetListOfKeys()
keys = []
for i in range(fkeys.GetEntries()):
    keys.append(fkeys.At(i).GetName())
keys.sort()

for i in range(0,len(keys),2):
    if keys[i].find(mode) > 0:
        ntuples = (ffile_tp.Get(keys[i]), ffile_tp.Get(keys[i+1]))
        break                   # found mode

# make dataset from tree
wt = RooRealVar('wt', '', 1.0, 0.0, 1.0)
dst = RooDataSet('dst', '', RooArgSet(time, wt), RooFit.WeightVar(wt))
for tp in ntuples:
    print '{}: {}'.format(tp.GetName(), tp.GetEntries())
    tp.SetBranchStatus('*', 0)
    tp.SetBranchStatus('wt', 1)
    tp.SetBranchStatus('Bid', 1)
    tp.SetBranchStatus('hid', 1)
    tp.SetBranchStatus('time', 1)
    for i in range(tp.GetEntries()):
        tp.GetEntry(i)
        # choose decay equation (1 of 2 for Dspi)
        if (tp.Bid == 531 and tp.hid == 211):
            time.setVal(tp.time)
            dst.add(RooArgSet(time), tp.wt)
dst.Print()

# model.fitTo(dst)

# plot
tfr = time.frame()
dst.plotOn(tfr)
model.plotOn(tfr)
tfr.Draw()
mode_title = get_title_from_mode(mode)
if nokfactor:
    k_title = 'no'
else:
    k_title = 'with'
tfr.SetTitle('{} ({} #it{{k}}-factor smearing)'.format(mode_title, k_title))
tfr.GetYaxis().SetTitle('')

# FIXME: this is a hack, fix the real issue in splines
if trange:
    rescale_roofit_pad(gPad, trange[0], trange[1])

canvas.Print(plotfile)
canvas.Print('{}]'.format(plotfile))
