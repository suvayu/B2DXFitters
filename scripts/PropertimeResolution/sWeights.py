import itertools
import ROOT
from ROOT import RooArgList, RooArgSet, RooDataSet, RooFit, RooFormulaVar, RooRealVar, RooStats, RooWorkspace
from include import *

# Load the RooWorkspace
print("Opening the workspace...")
w_file = ROOT.TFile.Open('{}/w_data_{}.root'.format(ws_dir, desc))
w = w_file.Get('w')
assert(isinstance(w, RooWorkspace))

# Load the data from the RooWorkspace
print("Getting the data...")
dataset = w.data('data')
#mc_data = w.data('mc')
print("Done!")

nentries = dataset.numEntries()

import sys
#sys.exit(0)

# create fit model
##### Ds mass #############
# signal (prompt Ds) plus secondary Ds plus scattered low pt pions: DCB
# combinatorial background: exponent
mean = (1968.3, 1958.3, 1978.3)
sigma = (5.5, 3., 15.)
alpha1 = (1.34,)# 1., 2.)
alpha2 = (-1.24,)# -2., -1.)
n1 = (3.43,)
n2 = (6.67,)

print('Fitting the DsH invariant mass with a double Crystal Ball with the following parameters')
print('  mean   = {}'.format(mean))
print('  sigma  = {}'.format(sigma))
print('  alpha1 = {}'.format(alpha1))
print('  alpha2 = {}'.format(alpha2))
print('  n1     = {}'.format(n1))
print('  n2     = {}'.format(n2))

# Create a Workspace for the sFit
w = RooWorkspace('w')
i(w, dataset)

w.factory('SUM:prompt(\
                    CBShape::Signal1(lab2_MM,mean[{},{},{}], sigmas[{},{},{}], alpha1[{}], n1[{}]),\
        fracSg[0.5]*CBShape::Signal2(lab2_MM, mean, sigmas, alpha2[{}], n2[{}]))'\
            .format(*itertools.chain.from_iterable((mean, sigma, alpha1, n1, alpha2, n2))))

w.factory('Exponential::comb(lab2_MM,a1[0,-1,1])')

w.factory('SUM::model(Nprompt[%s,0,%s]*prompt,Ncomb[%s,0,%s]*comb)'%(0.5*nentries,nentries,0.5*nentries,nentries))

# Perform the sFit
model = w.pdf('model')
model.fitTo(dataset)

# Plot the sFit
Mframe = w.var('lab2_MM').frame(RooFit.Title(""))
dataset.plotOn(Mframe)
model.plotOn(Mframe)
pull_hist = Mframe.pullHist()
model.plotOn(Mframe, RooFit.Components('comb'),   RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(ROOT.kOrange))
model.plotOn(Mframe, RooFit.Components('prompt'), RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(ROOT.kMagenta))

frame_pull = w.var('lab2_MM').frame(RooFit.Title(""))
frame_pull.addPlotable(pull_hist, "P")
frame_pull.SetMinimum(-5.)
frame_pull.SetMaximum( 5.)
frame_pull.GetYaxis().SetNdivisions(110)
frame_pull.GetYaxis().SetLabelSize(0.1)
frame_pull.GetYaxis().CenterTitle()
frame_pull.GetYaxis().SetTitleSize(0.17)
frame_pull.GetYaxis().SetTitleOffset(0.38)
frame_pull.GetXaxis().SetNdivisions(Mframe.GetXaxis().GetNdivisions())

cM = ROOT.TCanvas('cM', 'cM')
cM.Divide(2)
cM.GetPad(1).SetPad(0.0,0.0,1.0,0.8)
cM.GetPad(2).SetPad(0.0,0.8,1.0,1.0)
cM.GetPad(1).SetLeftMargin(0.15)
cM.GetPad(2).SetLeftMargin(0.15)
cM.GetPad(2).SetBottomMargin(0.0)
cM.GetPad(1).SetTopMargin(0.0)

cM.cd(1)
Mframe.Draw()
cM.cd(2)
frame_pull.Draw()
cM.SaveAs('SWeightPlots/Mfit_{}.pdf'.format(desc))

cMlog=ROOT.TCanvas('cMlog','cMlog')
cMlog.SetLogy(1)
Mframe.Draw()
cMlog.SaveAs('SWeightPlots/Mfit_log_{}.pdf'.format(desc))

# Create the sWeights
mean = w.var('mean')
mean.setConstant()
sigmas = w.var('sigmas')
sigmas.setConstant()
Nprompt = w.var('Nprompt')
Ncomb = w.var('Ncomb')
sdata = RooStats.SPlot('sdata_{}'.format(desc), 'sdata_{}'.format(desc), dataset, model, RooArgList(Nprompt,Ncomb))
dataset_PromptSecScat = RooDataSet('dataset_M_fakeBs_{}'.format(desc), 'dataset_M_fakeBs_{}'.format(desc), dataset, dataset.get(), '', 'Nprompt_sw')
dataset_Comb = RooDataSet('dataset_M_Comb_{}'.format(desc), 'dataset_M_Comb_{}'.format(desc), dataset, dataset.get(), '', 'Ncomb_sw')

#prompt_weights = RooRealVar('prompt_weights_{}'.format(desc), 'prompt_weights_{}'.format(desc), 0., 1.)
dataset_Prompt_weighted = RooDataSet('dataset_fakeBs_weighted_{}'.format(desc), 'dataset_M_fakeBs_weighted_{}'.format(desc), dataset_PromptSecScat, dataset.get(), '', 'Nprompt_sw')

# Plot sWeighted logIP and bachelor momentum distribtions
"""
cIP = ROOT.TCanvas('cIP', 'cIP')
frameIP = w.var('log(lab2_IP_OWNPV)').frame()
dataset_PromptSecScat.plotOn(frameIP,RooFit.MarkerColor(ROOT.kMagenta))
dataset_Comb.plotOn(frameIP,RooFit.MarkerColor(ROOT.kOrange))
frameIP.Draw()
cIP.SaveAs('SWeightPlots/logIP_{}.pdf'.format(desc))
del frameIP
del cIP
"""

clab1_P = ROOT.TCanvas('clab1_P', 'clab1_P')
frame_lab1_P = w.var('lab1_P').frame()
dataset_PromptSecScat.plotOn(frame_lab1_P, RooFit.MarkerColor(ROOT.kMagenta))
#mc_data.plotOn(frame_lab1_P, RooFit.MarkerColor(ROOT.kOrange))
frame_lab1_P.Draw()
clab1_P.SaveAs('SWeightPlots/lab1_P_{}.pdf'.format(desc))
del frame_lab1_P
del clab1_P

clab0_MM = ROOT.TCanvas('clab0_MM', 'clab0_MM')
frame_lab0_MM = w.var('lab0_MM').frame()
dataset_PromptSecScat.plotOn(frame_lab0_MM, RooFit.MarkerColor(ROOT.kMagenta))
#mc_data.plotOn(frame_lab0_MM, RooFit.MarkerColor(ROOT.kOrange))
frame_lab0_MM.Draw()
clab0_MM.SaveAs('SWeightPlots/lab0_MM_{}.pdf'.format(desc))
del frame_lab0_MM
del clab0_MM

clab2_MM = ROOT.TCanvas('clab2_MM', 'clab2_MM')
frame_lab2_MM = w.var('lab2_MM').frame()
dataset_PromptSecScat.plotOn(frame_lab2_MM, RooFit.MarkerColor(ROOT.kMagenta))
dataset.plotOn(frame_lab2_MM, RooFit.MarkerColor(ROOT.kOrange))
frame_lab2_MM.Draw()
clab2_MM.SaveAs('SWeightPlots/lab2_MM_{}.pdf'.format(desc))
del frame_lab2_MM
del clab2_MM

# Save the sWeighted datasets into the Workspace
print("Saving datasets...")
dataset_file = ROOT.TFile.Open('{}/dataset_M_fakeBs_{}.root'.format(ws_dir, desc), 'RECREATE')
dataset_PromptSecScat.Write('dataset_M_fakeBs_{}'.format(desc))
dataset_file.Close()

dataset_file = ROOT.TFile.Open('{}/dataset_M_Comb_{}.root'.format(ws_dir, desc), 'RECREATE')
dataset_Comb.Write('dataset_M_Comb_{}'.format(desc))
dataset_file.Close()

dataset_file = ROOT.TFile.Open('{}/dataset_fakeBs_weighted_{}.root'.format(ws_dir, desc), 'RECREATE')
dataset_Prompt_weighted.Write('dataset_fakeBs_weighted_{}'.format(desc))
dataset_file.Close()

