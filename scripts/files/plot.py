#!/usr/bin/python

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('-w', '--wspace', dest='rfile', help='Workspace filename')
optparser.add_argument('-t', '--tuple', dest='tpfile', help='Tuple filename')
optparser.add_argument('-m', '--mode', dest='mode', help='Decay mode')
optparser.add_argument('-o', '--output', dest='plotfile', help='Output filename (pdf)')
options = optparser.parse_args()
rfile = options.rfile
tpfile = options.tpfile
mode = options.mode
plotfile = options.plotfile

assert(tpfile and mode)
if not plotfile:
    plotfile = '{}.pdf'.format(rfile.rsplit('.',1)[0])


from ROOT import TFile, TTree, TChain, TH1D, TList, TCanvas
from ROOT import gPad, gStyle, gSystem, kRed, kBlue, kAzure, kGreen, kBlack
from ROOT import RooWorkspace, RooArgSet, RooArgList, RooFit

import B2DXFitters
from ROOT import (RooRealVar, RooConstVar, RooRealConstant,
                  RooProduct, RooKResModel, Inverse, RooGaussModel,
                  RooBDecay, RooDataSet)
# aliases
const = RooRealConstant.value


gStyle.SetOptStat('nemrou')
canvas = TCanvas('canvas', 'canvas', 800, 600)
canvas.Print('{}['.format(plotfile))

ffile = TFile.Open(rfile, 'read')
workspace = ffile.Get('workspace')

pdfs = RooArgList(workspace.allPdfs())
for i in range(pdfs.getSize()):
    name = pdfs[i].GetName()
    if name.find(mode) >= 0:
        mykpdf = pdfs[i]
assert(mykpdf)

time = RooRealVar('time', 'Time [ps]', 0.0, 7.0)
time.setBins(500)
time.setBins(1500, 'cache')

kfactor = workspace.var('kfactorVar')
kfactor.setRange(0.85, 1.05)
gamma = RooRealVar('gamma', 'gamma', 0.661, 0., 3.)
kgamma = RooProduct('kgamma', 'kgamma', RooArgList(gamma, kfactor))
dGamma = RooRealVar('dGamma', 'dGamma', -0.106, -3., 3.)
dM = RooRealVar('dM', 'dM', 17.768, 0.1, 20.)
C = RooRealVar('C', 'C', 1., 0., 2.);
one = RooConstVar('one', 'one', 1.);
zero = RooConstVar('zero', 'zero', 0.);
tau = Inverse('tau', 'tau', gamma)
# tauk = Inverse('tauk', 'tauk', kgamma)

gres = RooGaussModel('gres', '', time, const(0.0), const(0.044))
kgres = RooKResModel('kgres', '', gres, mykpdf, kfactor, RooArgSet(gamma, dM, dGamma))
model = RooBDecay('model', 'k-factor smeared model', time, tau, dGamma,
                   one, zero, C, zero, dM, kgres, RooBDecay.SingleSided)

ffile_tp = TFile(tpfile, 'read')

## directly from ntuple
# ftmp = TFile('/tmp/tmp.root', 'recreate')
# ftree = ffile_tp.Get('tree').CopyTree('Bid == 531 && hid == 211')
# assert(ftree)

## after selection
fkeys = ffile_tp.GetListOfKeys()
keys = []
for i in range(fkeys.GetEntries()):
    keys.append(fkeys.At(i).GetName())
keys.sort()

for i in range(0,len(keys),2):
    if keys[i].find(mode) > 0:
        ntuples = (ffile_tp.Get(keys[i]), ffile_tp.Get(keys[i+1]))
        break

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
        if (tp.Bid == 531 and tp.hid == 211):
            time.setVal(tp.time)
            dst.add(RooArgSet(time), tp.wt)
dst.Print()

# model.fitTo(dst)

tfr = time.frame()
dst.plotOn(tfr)
model.plotOn(tfr)
tfr.Draw()
tfr.SetTitle('B_{s} #rightarrow D_{s}*#pi (with #it{k}-factor smearing)')
tfr.GetYaxis().SetTitle('')
canvas.Print(plotfile)
canvas.Print('{}]'.format(plotfile))
