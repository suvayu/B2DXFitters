from include import *

from ROOT import TFile, TTree
from ROOT import RooFit, RooAddPdf, RooArgList, RooArgSet, RooCBShape, RooFormulaVar, RooGaussian, RooRealVar, RooWorkspace

print("Opening the workspace...")
f = TFile.Open("{}/w_data_{}.root".format(ws_dir, desc))
w = f.Get("w")

data_name = "dataset_M_fakeBs_{}".format(desc)
dataset = TFile.Open("{}/{}.root".format(ws_dir, data_name)).Get(data_name)
assert(isinstance(dataset, ROOT.RooAbsData))

x = w.var("lab2_MM")
frame = x.frame(1890., 2070.)
dataset.plotOn(frame)
c = ROOT.TCanvas('c', 'c')
frame.Draw()
c.SaveAs("SWeightPlots/lab2_MM_{}.pdf".format(desc))
del c
del frame
del x

x = w.var("lab0_LifetimeFit_TAU")
frame = x.frame(-500., 1000.)
dataset.plotOn(frame)
c = ROOT.TCanvas('c', 'c')
frame.Draw()
c.SaveAs("SWeightPlots/lab0_LifetimeFit_TAU_{}.pdf".format(desc))
del c
del frame
del x

x = w.var("lab0_LifetimeFit_TAU_DIFF")
frame = x.frame(-500., 1000.)
dataset.plotOn(frame)
c = ROOT.TCanvas('c', 'c')
frame.Draw()
c.SaveAs("SWeightPlots/lab0_LifetimeFit_TAU_DIFF_{}.pdf".format(desc))
del c
del frame
del x

x = w.var("lab0_LifetimeFit_TAUERR")
frame = x.frame(0., 150.)
dataset.plotOn(frame)
c = ROOT.TCanvas('c', 'c')
frame.Draw()
c.SaveAs("SWeightPlots/lab0_LifetimeFit_TAUERR_{}.pdf".format(desc))
del c
del frame
del x

cuts_bin = "lab0_LifetimeFit_ctauErr0/{0} > 23.44 && lab0_LifetimeFit_ctauErr0/{0} < 24.24".format(speedOfLight_mm_fs)
x = w.var("lab0_LifetimeFit_TAU")
frame = x.frame(-100., 300.)
dataset.reduce(cuts_bin).plotOn(frame)
c = ROOT.TCanvas('c', 'c')
frame.Draw()
c.SaveAs("SWeightPlots/lab0_LifetimeFit_TAU_bin_{}.pdf".format(desc))
del c
del frame
del x


