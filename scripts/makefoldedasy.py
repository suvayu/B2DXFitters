import ROOT
from ROOT import *
from math import *
from array import *

# A script to make the folded asymmetry plots for DsK
#
# For the moment makes the plots for DsK toys. Needs some work to generalize
# it to make the plots for DsPi or DsK, and for data or toys or full MC.

lowertoy = 348
uppertoy = 357

runondata = True

latex_xpos_1      =  0.75
latex_xpos_2      =  0.75
latex_ypos        =  0.875
latex_string      = "LHCb"

if not runondata :
    if lowertoy == uppertoy :
        plotsuffix = "Toy_"+str(lowertoy)
    else :
        plotsuffix = "Toys_"+str(lowertoy)+"_"+str(uppertoy)
else :
    plotsuffix = 'Data'

tree = TChain("merged")
if not runondata :
    for toy in range(lowertoy,uppertoy+1) :
        tree.Add("/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M_2T/DsK_Toys_sWeights_ForTimeFit_"+str(toy)+".root")
else :
    tree.Add('/afs/cern.ch/work/g/gligorov//public/Bs2DsKPlotsForPaper/NominalFit/sWeights_BsDsK_all_both_BDTGA.root')

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
    if not runondata : 
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
    else :
        thiseventweight = tree.nSig_both_pipipi_Evts_sw +\
                          tree.nSig_both_kpipi_Evts_sw +\
                          tree.nSig_both_phipi_Evts_sw +\
                          tree.nSig_both_nonres_Evts_sw +\
                          tree.nSig_both_kstk_Evts_sw
        if tree.tagDecComb_idx < 0 and tree.lab1_ID_idx < 0 :
            histo["DpKm_fold"].Fill((tree.lab0_LifetimeFit_ctau)%modulo,thiseventweight)
        if tree.tagDecComb_idx > 0 and tree.lab1_ID_idx < 0 :
            histonorm["DpKm_fold"].Fill((tree.lab0_LifetimeFit_ctau)%modulo,thiseventweight)
        if tree.tagDecComb_idx < 0 and tree.lab1_ID_idx > 0 :
            histo["DmKp_fold"].Fill((tree.lab0_LifetimeFit_ctau)%modulo,thiseventweight)
        if tree.tagDecComb_idx > 0 and tree.lab1_ID_idx > 0 :
            histonorm["DmKp_fold"].Fill((tree.lab0_LifetimeFit_ctau)%modulo,thiseventweight)
        if tree.lab1_ID_idx < 0 :
            histo["DpKm_unfold"].Fill((tree.lab0_LifetimeFit_ctau),thiseventweight)
        else :
            histo["DmKp_unfold"].Fill((tree.lab0_LifetimeFit_ctau),thiseventweight)

for histotype in ["DpKm_fold","DmKp_fold"] :
    histo[histotype].Sumw2()
    histonorm[histotype].Sumw2()
    histosum[histotype].Sumw2()
    histodiff[histotype].Sumw2()
    histosum[histotype].Add(histo[histotype],histonorm[histotype],1.,1.)
    histodiff[histotype].Add(histo[histotype],histonorm[histotype],-1.,1.)
    histodiff[histotype].Divide(histosum[histotype])
    histodiff[histotype].GetXaxis().SetTitle("#tau modulo (2#pi/#Deltam_{s}) [ps]")
    histodiff[histotype].GetXaxis().SetTitleSize(0.07)
    histodiff[histotype].GetXaxis().SetLabelSize(0.06)
    histodiff[histotype].GetYaxis().SetTitleSize(0.07)
    histodiff[histotype].GetYaxis().SetLabelSize(0.06)
    histodiff[histotype].GetYaxis().SetTitleOffset(0.9)
for histotype in ["DpKm_unfold","DmKp_unfold"] :
    histo[histotype].Sumw2()
    histo[histotype].GetXaxis().SetTitle("#tau [ps]")

histo["DpKm_unfold"].GetYaxis().SetTitle("D^{+}_{s}K^{-} candidates")
histo["DmKp_unfold"].GetYaxis().SetTitle("D^{-}_{s}K^{+} candidates")
histo["DpKm_unfold"].SetMarkerStyle(22)
histo["DmKp_unfold"].SetMarkerStyle(25)
histodiff["DpKm_fold"].GetYaxis().SetTitle("A_{#font[12]{CP}} D^{+}_{s}K^{-}")
histodiff["DmKp_fold"].GetYaxis().SetTitle("A_{#font[12]{CP}} D^{-}_{s}K^{+}")

myLatex = TLatex()
myLatex.SetTextFont(132)
myLatex.SetTextColor(1)
myLatex.SetTextSize(0.06)
myLatex.SetTextAlign(12)
myLatex.SetNDC(kTRUE)

foldedcanvas = TCanvas("foldedcanvas","foldedcanvas",1600,600)
foldedcanvas.Divide(2)
foldedcanvas.cd(1)
histodiff["DpKm_fold"].Draw("EP")
histodiff["DpKm_fold"].GetYaxis().SetRangeUser(-0.5,0.5)
function1 = TF1("function","[0]*(0.52257*cos("+str(dms)+"*x) - 0.89737*sin("+str(dms)+"*x))",0.,modulo)
function2 = TF1("function","[0]*(0.52257*cos("+str(dms)+"*x) + 0.36351*sin("+str(dms)+"*x))",0.,modulo)
function1.SetLineWidth(2)
function2.SetLineWidth(2)
function1.SetLineColor(2)
function2.SetLineColor(2)
#function1.SetLineWidth(1.5)
#function2.SetLineWidth(1.5)
histodiff["DpKm_fold"].Fit(function2)
myLatex.DrawLatex(latex_xpos_1,latex_ypos,latex_string)
foldedcanvas.GetPad(1).Update()
foldedcanvas.cd(2)
histodiff["DmKp_fold"].Draw("EP")
histodiff["DmKp_fold"].Fit(function1)
myLatex.DrawLatex(latex_xpos_2,latex_ypos,latex_string)
histodiff["DmKp_fold"].GetYaxis().SetRangeUser(-0.5,0.5)
foldedcanvas.GetPad(2).Update()
#foldedcanvas.cd(3)
#histodiff["DpKm_fold"].Add(histodiff["DmKp_fold"],-1)
#histodiff["DpKm_fold"].DrawCopy("EP")
#myLatex.DrawLatex(latex_xpos,latex_ypos,latex_string)

foldedcanvas.SaveAs("/afs/cern.ch/work/g/gligorov//public/Bs2DsKPlotsForPaper/FoldedAsyDsK_"+plotsuffix+".pdf")
'''
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
'''
