import ROOT
from ROOT import *
from math import *
from array import *

gROOT.SetBatch()
gStyle.SetOptStat(0)
gStyle.SetOptFit(0)

# A script to make the folded asymmetry plots for Bd->DPi
#
# For the moment makes the plots for DPi toys. Needs some work to generalize
# it to make the plots for DsPi or DsK, and for data or toys or full MC.

lowertoy = 2000
uppertoy = 2000

usesweights = True

latex_xpos_1      =  0.5
latex_xpos_2      =  0.5
latex_ypos        =  0.85
latex_string      = "LHCb Fast Simulation"

plotsuffix = "Toys_"+str(lowertoy)+"_"+str(uppertoy)

print "==> Importing data"

tree = TChain("merged")
for toy in range(lowertoy,uppertoy+1) :
    tree.Add("root://eoslhcb.cern.ch//eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toysv3r0/OldTemplatesAllIncludedNonZeroDG/sWeights/DPi_Toys_sWeights_ForTimeFit_AllBkg_"+str(toy)+".root")

tree.Print()

dm                      = 0.51
modulo                  = 2*pi/dm

histo      = {} 
histonorm  = {} 

histodiff  = {} 
histosum   = {} 

print "==> Building histograms"

for histotype in ["DpPim_fold","DmPip_fold"] :
    histo[histotype]     = TH1F("histo"+histotype,"",10,0.,modulo)
    histonorm[histotype] = TH1F("histonorm"+histotype,"",10,0.,modulo)
    histodiff[histotype] = TH1F("histodiff"+histotype,"",10,0.,modulo)
    histosum[histotype]  = TH1F("histosum"+histotype,"",10,0.,modulo)

print "Entries to process: "+str(tree.GetEntries())
for entry in range(tree.GetEntries()):
    if entry%50000 == 0: print "...processing entry "+str(entry)+"..."
    tree.GetEntry(entry)
    if not usesweights :
        if tree.tagDecComb_idx < 0 and tree.BacCharge_idx < 0 :
            histo["DpPim_fold"].Fill((tree.BeautyTime)%modulo,1)#pow((1-2*tree.tagOmegaComb),2))
        if tree.tagDecComb_idx > 0 and tree.BacCharge_idx < 0 :
            histonorm["DpPim_fold"].Fill((tree.BeautyTime)%modulo,1)#pow((1-2*tree.tagOmegaComb),2))
        if tree.tagDecComb_idx < 0 and tree.BacCharge_idx > 0 : 
            histo["DmPip_fold"].Fill((tree.BeautyTime)%modulo,1)#pow((1-2*tree.tagOmegaComb),2))
        if tree.tagDecComb_idx > 0 and tree.BacCharge_idx > 0 : 
            histonorm["DmPip_fold"].Fill((tree.BeautyTime)%modulo,1)#pow((1-2*tree.tagOmegaComb),2))
    else :
        thiseventweight = tree.nSig_both_KPiPi_Evts_sw
        if tree.tagDecComb_idx < 0 and tree.BacCharge_idx < 0 :
            histo["DpPim_fold"].Fill((tree.BeautyTime)%modulo,thiseventweight)
        if tree.tagDecComb_idx > 0 and tree.BacCharge_idx < 0 :
            histonorm["DpPim_fold"].Fill((tree.BeautyTime)%modulo,thiseventweight)
        if tree.tagDecComb_idx < 0 and tree.BacCharge_idx > 0 :
            histo["DmPip_fold"].Fill((tree.BeautyTime)%modulo,thiseventweight)
        if tree.tagDecComb_idx > 0 and tree.BacCharge_idx > 0 :
            histonorm["DmPip_fold"].Fill((tree.BeautyTime)%modulo,thiseventweight)
    
for histotype in ["DpPim_fold","DmPip_fold"] :
    histo[histotype].Sumw2()
    histonorm[histotype].Sumw2()
    histosum[histotype].Sumw2()
    histodiff[histotype].Sumw2()
    histosum[histotype].Add(histo[histotype],histonorm[histotype],1.,1.)
    histodiff[histotype].Add(histo[histotype],histonorm[histotype],-1.,1.)
    histodiff[histotype].Divide(histosum[histotype])
    histodiff[histotype].GetXaxis().SetTitle("#tau modulo (2#pi/#Deltam_{d}) [ps]")
    #histodiff[histotype].GetXaxis().SetTitleSize(0.07)
    #histodiff[histotype].GetXaxis().SetLabelSize(0.06)
    #histodiff[histotype].GetYaxis().SetTitleSize(0.07)
    #histodiff[histotype].GetYaxis().SetLabelSize(0.06)
    #histodiff[histotype].GetYaxis().SetTitleOffset(0.9)

histodiff["DpPim_fold"].GetYaxis().SetTitle("A_{#font[12]{CP}} D^{+}#pi^{-}")
histodiff["DmPip_fold"].GetYaxis().SetTitle("A_{#font[12]{CP}} D^{-}#pi^{+}")

myLatex = TLatex()
myLatex.SetTextFont(132)
myLatex.SetTextColor(1)
myLatex.SetTextSize(0.06)
myLatex.SetTextAlign(12)
myLatex.SetNDC(kTRUE)

print "==> Making plots"

foldedcanvas1 = TCanvas("foldedcanvas1")
foldedcanvas2 = TCanvas("foldedcanvas2")
function1 = TF1("function","(1-2*[0])*(-9.99479e-01*cos("+str(dm)+"*x)+ 0.0285073 *sin("+str(dm)+"*x))",0.,modulo)
function2 = TF1("function","(1-2*[0])*(9.99479e-01*cos("+str(dm)+"*x) + 0.0307618 *sin("+str(dm)+"*x))",0.,modulo)
function1.SetLineWidth(2)
function2.SetLineWidth(2)
function1.SetLineColor(2)
function2.SetLineColor(2)
function1.SetParName(0,"<#omega>")
function2.SetParName(0,"<#omega>")

foldedcanvas1.cd()
histodiff["DpPim_fold"].Draw("EP")
#histodiff["DpPim_fold"].GetYaxis().SetRangeUser(-1.1,1.5)
histodiff["DpPim_fold"].Fit(function1)
function1.Draw("SAME")
myLatex.DrawLatex(latex_xpos_1,latex_ypos,latex_string)
foldedcanvas1.Update()

foldedcanvas2.cd()
histodiff["DmPip_fold"].Draw("EP")
#histodiff["DmPip_fold"].GetYaxis().SetRangeUser(-1.1,1.5)
histodiff["DmPip_fold"].Fit(function2)
function2.Draw("SAME")
myLatex.DrawLatex(latex_xpos_2,latex_ypos,latex_string)
foldedcanvas2.Update()

foldedcanvas1.SaveAs("/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/OldTemplatesAllIncludedNonZeroDG/AsymmPlots/FoldedAsyDPi_DpPim_"+plotsuffix+".eps")
foldedcanvas2.SaveAs("/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/OldTemplatesAllIncludedNonZeroDG/AsymmPlots/FoldedAsyDPi_DmPip_"+plotsuffix+".eps")
