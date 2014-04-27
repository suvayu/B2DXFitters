import os,sys
import ROOT
from ROOT import *
import copy

names = ["kFactor_Bd2DK_both",
"kFactor_Bd2DPi_both",
"kFactor_Bs2DsPi_both",
"kFactor_Bs2DsRho_both",
"kFactor_Bs2DsstPi_both",
"kFactor_Lb2Dsp_both",
"kFactor_Lb2Dsstp_both",
"kFactor_Lb2LcK_both",
"kFactor_Lb2LcPi_both"]

varname = "kfactorVar"

filestoedit = [
"template_MC_KFactor_BsDsK_5300_5350.root",
"template_MC_KFactor_BsDsK_5350_5400.root",
"template_MC_KFactor_BsDsK_5400_5450.root",
"template_MC_KFactor_BsDsK_5450_5500.root",
"template_MC_KFactor_BsDsK_5500_5550.root",
"template_MC_KFactor_BsDsK_5550_5600.root",
"template_MC_KFactor_BsDsK_5600_5650.root",
"template_MC_KFactor_BsDsK_5650_5700.root",
"template_MC_KFactor_BsDsK_5700_5750.root",
"template_MC_KFactor_BsDsK_5750_5800.root"
]

histstowrite = {}
for name in names :
    histstowrite[name] = []

for filename in filestoedit :
    range_low  = (filename.split('_BsDsK_')[1].split('_')[0])
    range_high = (filename.split('_BsDsK_')[1].split('_')[1].split('.')[0])
    inputfile = TFile(filename)
    myw = inputfile.Get("workspace")
    for name in names :
        hist = myw.pdf(name).dataHist().createHistogram(varname)
        #print name,range_low,range_high,hist.GetEffectiveEntries()
        if hist.GetEntries() < 2 or hist.GetEffectiveEntries() < 3 :
            hist = histstowrite[name][-1].Clone()
        if hist.GetEffectiveEntries() < 10 :
            hist.Rebin()
            hist.Rebin()
        hist.SetName(name.replace('_both','')+"_"+range_low+"_"+range_high)
        histstowrite[name].append(copy.deepcopy(hist))
outputfile = TFile("histograms_MC_KFactor_BsDsK.root","recreate")
for histgroup in histstowrite :
    for hist in histstowrite[histgroup] :
        hist.Write()
outputfile.Close()
