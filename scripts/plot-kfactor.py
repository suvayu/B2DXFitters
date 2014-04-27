#!/usr/bin/env python
# coding=utf-8
"""K factor plotting script.

NB: K-factors are written out as RooDataSets for later use but this
scripts makes the plots from a dumped out tree in treedump.root.

"""

# option parsing
import argparse
optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('rfile', help='ROOT file with tree dump (default) or workspace')
optparser.add_argument('-o', '--output', dest='plotfile',
                       help='Output filename (pdf)')
optparser.add_argument('-nw', '--noweights', dest='noweights',
                       action='store_true', default=False,
                       help='Make plots without weights')
optparser.add_argument('--pdf', dest='ifpdf', action='store_true',
                       default=False, help='Plot pdf or histogram')
options = optparser.parse_args()
rfile = options.rfile
plotfile = options.plotfile
noweights = options.noweights
ifpdf = options.ifpdf

if noweights:
    plotfile += '_wo_weights'

if not plotfile:
    plotfile = '{}.pdf'.format(rfile.rsplit('.',1)[0])


from ROOT import TFile, TCanvas, TH1D, TTree, TList
from ROOT import RooWorkspace, RooArgSet, RooArgList, RooFit
from ROOT import gPad, gStyle, kRed, kBlue, kAzure, kGreen, kBlack

gStyle.SetOptStat('nemrou')
canvas = TCanvas('canvas', 'canvas', 800, 600)
canvas.Print('{}['.format(plotfile))

ffile = TFile.Open(rfile, 'read')

if ifpdf:
    workspace = ffile.Get('workspace')

    kfactor = workspace.var('kfactorVar')
    kfactor.setRange(0.9, 1.1)
    pdfs = RooArgList(workspace.allPdfs())

    for i in range(pdfs.getSize()):
        fr = kfactor.frame()
        pdfs[i].plotOn(fr, RooFit.LineColor(kBlack), RooFit.FillColor(kAzure+1),
                       RooFit.DrawOption('lf')) # FIXME: doesn't draw the line!'
        fr.Draw()
        canvas.Print(plotfile)
else:
    modes = {}
    klist = ffile.GetListOfKeys()
    for item in klist:
        name = item.GetName()
        if not name.startswith('mBresn'):
            print 'MSG: Skipping, unknown object: %s' % name
            continue # ntuples are named mBresn_*
        sample = name.split('_')
        modes[sample[1]] = modes.get(sample[1],[]) + [item] # up and down for each mode

    for mode in modes:
        tlist = TList()
        for i in modes[mode]:
            tlist.Add(i.ReadObj())
            print 'MSG: Subtree name: %s' % i.GetName()
        tree = TTree.MergeTrees(tlist)
        if not tree:
            print 'MSG: Null pointer to tree!'
            continue
        tname = tree.GetName()
        tname = tname[:tname.find('_', 8)]
        tree.SetName(tname)
        vardict = {'mBdiff':'#delta m', 'kfactor':'k-factor (m/p)', 'kfactorp':'momentum k-factor (p)'}
        if tree.GetEntries() > 0:
            for var in vardict:
                hname = 'h%s_%s' % (var, tname)
                if noweights:
                    tree.Draw('%s>>%s' % (var, hname), '', 'hist')
                else:
                    tree.Draw('%s>>%s' % (var, hname), 'wMC*wRW*globalWeight', 'hist')
                # adjust labels and styles
                hist = gPad.FindObject(hname)
                hist.SetTitle('%s - %s' % (vardict[var], tname))
                hist.SetXTitle('%s' % vardict[var])
                hist.SetFillColor(kAzure+1)
                gPad.Modified()
                gPad.Update()

                # Debug
                print 'MSG: Tree %s with %d: %s' % (tname, tree.GetEntries(), var)
                canvas.Print(plotfile)
        else:
            print 'MSG: Tree %s has no entries!' % (tree.GetName())

canvas.Print('{}]'.format(plotfile))
