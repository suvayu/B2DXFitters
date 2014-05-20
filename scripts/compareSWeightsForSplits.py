import os,sys
import ROOT
from ROOT import *

def getSWeight(tree,sweightstoadd) :
    accum = 0
    for key in sweightstoadd :
        accum += tree.__getattr__(key)
    return accum

#Note : file 2 should be a subset of file 1
file_1 = TFile(sys.argv[1])
file_2 = TFile(sys.argv[2])

tree_1 = file_1.Get("merged")
tree_2 = file_2.Get("merged")

sweightstoadd = ["nSig_both_nonres_Evts_sw",
                 "nSig_both_phipi_Evts_sw",
                 "nSig_both_kstk_Evts_sw",
                 "nSig_both_kpipi_Evts_sw",
                 "nSig_both_pipipi_Evts_sw"]

tree1entry = 0
migration_sig = 0
migration_bkg = 0
for thisentry in range(0,tree_2.GetEntries()) :
    tree_2.GetEntry(thisentry)
    tree_1.GetEntry(tree1entry)
    while abs(tree_1.lab1_PIDK - tree_2.lab1_PIDK) > 0.001 :
        tree1entry += 1
        tree_1.GetEntry(tree1entry)
    diff = getSWeight(tree_2,sweightstoadd)-getSWeight(tree_1,sweightstoadd)
    if getSWeight(tree_2,sweightstoadd) > 0 and getSWeight(tree_1,sweightstoadd) < 0 :
        print "Event became sig",getSWeight(tree_1,sweightstoadd),diff
        migration_sig += 1
    if getSWeight(tree_1,sweightstoadd) > 0 and getSWeight(tree_2,sweightstoadd) < 0 : 
        print "Event became bkg",getSWeight(tree_1,sweightstoadd),diff
        migration_bkg += 1
print migration_sig,migration_bkg
