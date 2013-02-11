#!/usr/bin/python
# coding=utf-8
"""K factor plotting script.

NB: K-factors are written out as RooDataSets for later use but this
scripts makes the plots from a dumped out tree in treedump.root.

"""

def cpp_to_pylist(cpplist):
    """Convert a C++ list (from PyROOT) to a Python list.

    NB: Calling this empties the original C++ list.

    """
    pylist = []
    for i in range(cpplist.size()):
        pylist.append(cpplist.back())
        cpplist.pop_back()
    return pylist


from ROOT import TFile, TCanvas, TH1D, TTree, TList
from ROOT import gPad, gStyle, kRed, kBlue, kAzure, kGreen

gStyle.SetOptStat('nemrou')

ffile = TFile.Open('treedump.root', 'update')
klist = ffile.GetListOfKeys()

canvas = TCanvas('canvas', 'canvas', 800, 600)
canvas.Print('.pdf[')

modes = {}
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
            tree.Draw('%s>>%s' % (var, hname), '', 'hist')
            # adjust labels and styles
            hist = gPad.FindObject(hname)
            hist.SetTitle('%s - %s' % (vardict[var], tname))
            hist.SetXTitle('%s' % vardict[var])
            hist.SetFillColor(kAzure+1)
            gPad.Modified()
            gPad.Update()

            # Debug
            print 'MSG: Tree %s with %d: %s' % (tname, tree.GetEntries(), var)
            canvas.Print('.pdf')
    else:
        print 'MSG: Tree %s has no entries!' % (tree.GetName())

canvas.Print('.pdf]')
