import ROOT
from ROOT import *
from math import *
from array import *

# A script to make the folded asymmetry plots for DsK
#
# For the moment makes the plots for DsK toys. Needs some work to generalize
# it to make the plots for DsPi or DsK, and for data or toys or full MC.

lowertoy = 338
uppertoy = 437

latex_xpos      =  0.675
latex_ypos      =  0.855
latex_string    = "#splitline{#splitline{LHCb Preliminary}{1.0 fb^{-1}}}{}"

if lowertoy == uppertoy :
    plotsuffix = "Toy_"+str(lowertoy)
else :
    plotsuffix = "Toys_"+str(lowertoy)+"_"+str(uppertoy)

tree = TChain("merged")
for toy in range(lowertoy,uppertoy+1) :
    tree.Add("/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M_2T/DsK_Toys_sWeights_ForTimeFit_"+str(toy)+".root")

dms                      = 17.768
modulo                   = 2*pi/dms
timebinning_unfolded     = array('d',[0,0.5,1.0,1.5,2.0,2.5,3.0,4.,5.,6.,7.,8.,9.,10.,15.])

histo      = {} 
histonorm  = {} 

histodiff  = {} 
histosum   = {} 

for histotype in ["DpKm_fold","DmKp_fold"] :
    histo[histotype]     = TH1F("histo"+histotype,"histo"+histotype,10,0.,modulo)
    histonorm[histotype] = TH1F("histonorm"+histotype,"histonorm"+histotype,10,0.,modulo)
    histodiff[histotype] = TH1F("histodiff"+histotype,"histodiff"+histotype,10,0.,modulo)
    histosum[histotype]  = TH1F("histosum"+histotype,"histosum"+histotype,10,0.,modulo)
for histotype in ["DpKm_unfold","DmKp_unfold"] :
    histo[histotype]     = TH1F("histo"+histotype,"histo"+histotype,timebinning_unfolded.__len__()-1,timebinning_unfolded)

for entry in range(tree.GetEntries()):
    tree.GetEntry(entry)
    if fabs(tree.lab0_TRUEID-1)<0.1 : 
        if tree.tagDecComb_idx < 0 and tree.lab1_ID_idx < 0 :
            histo["DpKm_fold"].Fill((tree.lab0_LifetimeFit_ctau)%modulo,1)#pow((1-2*tree.tagOmegaComb),2))
        if tree.tagDecComb_idx > 0 and tree.lab1_ID_idx < 0 :
            histonorm["DpKm_fold"].Fill((tree.lab0_LifetimeFit_ctau)%modulo,1)#pow((1-2*tree.tagOmegaComb),2))
        if tree.tagDecComb_idx < 0 and tree.lab1_ID_idx > 0 : 
            histo["DmKp_fold"].Fill((tree.lab0_LifetimeFit_ctau)%modulo,1)#pow((1-2*tree.tagOmegaComb),2))
        if tree.tagDecComb_idx > 0 and tree.lab1_ID_idx > 0 : 
            histonorm["DmKp_fold"].Fill((tree.lab0_LifetimeFit_ctau)%modulo,1)#pow((1-2*tree.tagOmegaComb),2))
        if tree.lab1_ID_idx < 0 :
            histo["DpKm_unfold"].Fill((tree.lab0_LifetimeFit_ctau),1)
        else :
            histo["DmKp_unfold"].Fill((tree.lab0_LifetimeFit_ctau),1)

for histotype in ["DpKm_fold","DmKp_fold"] :
    histo[histotype].Sumw2()
    histonorm[histotype].Sumw2()
    histosum[histotype].Sumw2()
    histodiff[histotype].Sumw2()
    histosum[histotype].Add(histo[histotype],histonorm[histotype],1.,1.)
    histodiff[histotype].Add(histo[histotype],histonorm[histotype],-1.,1.)
    histodiff[histotype].Divide(histosum[histotype])

    histodiff[histotype].GetXaxis().SetTitle("t modulo (2#pi/#Deltam_{s}) [ps]")
for histotype in ["DpKm_unfold","DmKp_unfold"] :
    histo[histotype].Sumw2()
    histo[histotype].GetXaxis().SetTitle("#tau [ps]")

histo["DpKm_unfold"].GetYaxis().SetTitle("D^{+}_{s}K^{-} candidates")
histo["DmKp_unfold"].GetYaxis().SetTitle("D^{-}_{s}K^{+} candidates")
histo["DpKm_unfold"].SetMarkerStyle(22)
histo["DmKp_unfold"].SetMarkerStyle(25)
histodiff["DpKm_fold"].GetYaxis().SetTitle("A_{mix} D^{+}_{s}K^{-}")
histodiff["DmKp_fold"].GetYaxis().SetTitle("A_{mix} D^{-}_{s}K^{+}")

myLatex = TLatex()
myLatex.SetTextFont(132)
myLatex.SetTextColor(1)
myLatex.SetTextSize(0.04)
myLatex.SetTextAlign(12)
myLatex.SetNDC(kTRUE)

foldedcanvas = TCanvas("foldedcanvas","foldedcanvas",1600,600)
foldedcanvas.Divide(2)
foldedcanvas.cd(1)
histodiff["DpKm_fold"].Draw("EP")
myLatex.DrawLatex(latex_xpos,latex_ypos,latex_string)
foldedcanvas.cd(2)
histodiff["DmKp_fold"].Draw("EP")
myLatex.DrawLatex(latex_xpos,latex_ypos,latex_string)

foldedcanvas.SaveAs("/afs/cern.ch/work/g/gligorov//public/Bs2DsKPlotsForPaper/FoldedAsyDsK_"+plotsuffix+".pdf")

unfoldedcanvas = TCanvas("unfoldedcanvas","unfoldedcanvas",1600,600)
unfoldedcanvas.Divide(2)
unfoldedcanvas.cd(1)
histo["DpKm_unfold"].DrawCopy("EP")
histo["DmKp_unfold"].DrawCopy("EPSAME")
unfoldedcanvas.GetPad(1).SetLogy()
myLatex.DrawLatex(latex_xpos,latex_ypos,latex_string)
unfoldedcanvas.cd(2)
histo["DmKp_unfold"].Divide(histo["DpKm_unfold"])
histo["DmKp_unfold"].GetYaxis().SetTitle("D^{-}_{s}K^{+}/D^{+}_{s}K^{-} candidates")
histo["DmKp_unfold"].GetYaxis().SetRangeUser(0.,2.0)
histo["DmKp_unfold"].Draw("EP")
myLatex.DrawLatex(latex_xpos,latex_ypos,latex_string)

unfoldedcanvas.SaveAs("/afs/cern.ch/work/g/gligorov/public/Bs2DsKPlotsForPaper/UnfoldedRatesDsK_"+plotsuffix+".pdf")
