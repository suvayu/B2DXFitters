import ROOT
from ROOT import *
from math import *

tree = TChain("DecayTree")
tree.Add("/afs/cern.ch/work/a/adudziak/public/Bs2DsKFitTuple/MergedTree_Bs2DsX_M*_OFFLINE_DsPi.root")

dms = 17.768

modulo      = 2*pi/dms

histo      = TH1F("histo","",10,0.,modulo)
histonorm  = TH1F("histonorm","",10,0.,modulo)

histo_diff = TH1F("histo_diff","",10,0.,modulo)
histo_sum  = TH1F("histo_sum","",10,0.,modulo)

for entry in range(tree.GetEntries()):
    tree.GetEntry(entry)
    if tree.lab0_MassFitConsD_M[0] < 5330. or tree.lab0_MassFitConsD_M[0] > 5410. :
        continue        
    if tree.BDTGResponse_1 < 0.9 : continue
    if tree.lab0_TAGDECISION == 0 : continue 
    if tree.lab1_PIDK > 0 : continue
    if tree.lab1_ID < 0 :
        #histo.Fill((tree.lab0_LifetimeFit_ctau[0]*3.335641)%modulo,-tree.lab0_TRUEID/abs(tree.lab0_TRUEID))
        if tree.lab0_TAGDECISION > 0 :
            histo.Fill((tree.lab0_LifetimeFit_ctau[0]*3.335641)%modulo,1.)
        if tree.lab0_TAGDECISION < 0 :
            histonorm.Fill((tree.lab0_LifetimeFit_ctau[0]*3.335641)%modulo,1.)
    if tree.lab1_ID > 0 : 
        #histo.Fill((tree.lab0_LifetimeFit_ctau[0]*3.335641)%modulo,-tree.lab0_TRUEID/abs(tree.lab0_TRUEID))
        if tree.lab0_TAGDECISION < 0 : 
            histo.Fill((tree.lab0_LifetimeFit_ctau[0]*3.335641)%modulo,1.)
        if tree.lab0_TAGDECISION > 0 : 
            histonorm.Fill((tree.lab0_LifetimeFit_ctau[0]*3.335641)%modulo,1.)

histo.Sumw2()
histonorm.Sumw2()

histo_diff.Sumw2()
histo_sum.Sumw2()

histo_diff.Add(histo,histonorm,1.,-1.)
histo_sum.Add(histo,histonorm,1.,1.)

histo_diff.Divide(histo_sum)

histo_diff.Draw("EP")

function = TF1("function","[0]*cos("+str(dms)+"*x) + [1]",0.,modulo)

histo_diff.Fit(function)

