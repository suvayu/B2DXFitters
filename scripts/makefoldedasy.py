import ROOT
from ROOT import *
from math import *

file = TFile("/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsK_all_both.root")
tree = file.Get("merged")

dms = 17.719

modulo      = 2*pi/dms

histo      = TH1F("histo","",5,0.,modulo)
histonorm  = TH1F("histonorm","",5,0.,modulo)

histo_back      = TH1F("histo_back","",5,0.,modulo)
histonorm_back  = TH1F("histonorm_back","",5,0.,modulo)

histodiff  = TH1F("histodiff","",5,0.,modulo) 
histosum   = TH1F("histosum","",5,0.,modulo)

for entry in range(tree.GetEntries()):
    tree.GetEntry(entry)
    if tree.lab0_MassFitConsD_M > 5330. and tree.lab0_MassFitConsD_M < 5410. :
        #if tree.lab0_BsTaggingTool_TAGOMEGA_OS > 0.42 : continue
        #sweight =   tree.nSig_up_pipipi_Evts_sw + tree.nSig_down_pipipi_Evts_sw +\
        #            tree.nSig_up_kpipi_Evts_sw  + tree.nSig_down_kpipi_Evts_sw  +\
        #            tree.nSig_up_kkpi_Evts_sw   + tree.nSig_down_kkpi_Evts_sw
	    if tree.lab0_BsTaggingTool_TAGDECISION_OS < 0 :
	        histo.Fill((tree.lab0_LifetimeFit_ctau*3.335641)%modulo,1)#(1-2*tree.lab0_BsTaggingTool_TAGOMEGA_OS))
	        #if tree.lab1_ID < 0 : 
	        #    histo.Fill((tree.lab0_LifetimeFit_ctau*3.335641)%modulo,(1-2*tree.lab0_BsTaggingTool_TAGOMEGA_OS))
	        #else :
	        #    histonorm.Fill((tree.lab0_LifetimeFit_ctau*3.335641)%modulo,(1-2*tree.lab0_BsTaggingTool_TAGOMEGA_OS))
	    if tree.lab0_BsTaggingTool_TAGDECISION_OS > 0 :
	        histonorm.Fill((tree.lab0_LifetimeFit_ctau*3.335641)%modulo,1)#(1-2*tree.lab0_BsTaggingTool_TAGOMEGA_OS))
	        #if tree.lab1_ID > 0 : 
	        #    histo.Fill((tree.lab0_LifetimeFit_ctau*3.335641)%modulo,(1-2*tree.lab0_BsTaggingTool_TAGOMEGA_OS))
	        #else :
	        #    histonorm.Fill((tree.lab0_LifetimeFit_ctau*3.335641)%modulo,(1-2*tree.lab0_BsTaggingTool_TAGOMEGA_OS))
    if tree.lab0_MassFitConsD_M > 5440. and tree.lab0_MassFitConsD_M < 5530. :
        if tree.lab0_BsTaggingTool_TAGDECISION_OS < 0 :
            histo.Fill((tree.lab0_LifetimeFit_ctau*3.335641)%modulo,-1)#-(1-2*tree.lab0_BsTaggingTool_TAGOMEGA_OS))
        if tree.lab0_BsTaggingTool_TAGDECISION_OS > 0 :
            histonorm.Fill((tree.lab0_LifetimeFit_ctau*3.335641)%modulo,-1)#-(1-2*tree.lab0_BsTaggingTool_TAGOMEGA_OS))

histo.Sumw2()
histonorm.Sumw2()

histosum.Sumw2()
histodiff.Sumw2()

histosum.Add(histo,histonorm,1.,1.)
histodiff.Add(histo,histonorm,-1.,1.)

histodiff.Divide(histosum)

histodiff.GetYaxis().SetTitle("A_{mix}")
histodiff.GetXaxis().SetTitle("t modulo (2#pi/#Deltam_{s}) [ps]")

histodiff.Draw("EP")

function = TF1("function","[0]*sin(17.719*x)+[1]",0.,modulo)

histodiff.Fit(function)

myLatex = TLatex()
myLatex.SetTextFont(132)
myLatex.SetTextColor(1)
myLatex.SetTextSize(0.06)
myLatex.SetTextAlign(12)
myLatex.SetNDC(kTRUE)
myLatex.DrawLatex(0.35, 0.775, 
                       "#splitline{#splitline{LHCb Preliminary}{1.0 fb^{-1}}}{}")

gStyle.SetOptFit(0)

c1.SaveAs("FoldedAsyDsKAtWADMS.pdf")
