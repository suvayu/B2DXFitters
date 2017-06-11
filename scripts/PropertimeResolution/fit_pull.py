from include import *
import sys

def format_results(var): return "{} \\pm {}".format(var.getVal(), var.getError())

ROOT.Math.MinimizerOptions.SetDefaultPrecision(1e-9)

print("Opening the workspace...")
f = ROOT.TFile.Open("{}/w_data_{}.root".format(ws_dir, desc))
w = f.Get("w")

dataset = w.data("data")

x = w.var("lab0_LifetimeFit_TAU_PULL")

x_range = (-3., 3.)

frame = x.frame(*x_range)
dataset.plotOn(frame)
c = ROOT.TCanvas('c', 'c')
frame.Draw()
c.SaveAs("DataPlots/lab0_LifetimeFit_TAU_PULL_{}.pdf".format(desc))
del frame
del c

print("Preparing the fit shape...")
mean   = RooRealVar('mean',   'mean',  -0.5, 0.5)
sigma  = RooRealVar('sigma',  'sigma',  0.5, 1.5)
sigma2 = RooRealVar('sigma2', 'sigma2', 1.5, 4.)
sigma.setVal(1.5)
sigma2.setVal(4.)

gaus1 = RooGaussian('gaus1', 'gaus1', x, mean, sigma)
gaus2 = RooGaussian('gaus2', 'gaus2', x, mean, sigma2)

frac = RooRealVar('frac', 'frac', 0.5, 1.)

resolution = RooFormulaVar("resolution", "sqrt(frac * sigma * sigma + (1. - frac) * sigma2 * sigma2)", RooArgList(frac, sigma, sigma2))
dilution = RooFormulaVar("dilution", "frac * exp(-sigma * sigma * dms * dms / 2.) + (1. - frac) * exp(-sigma2 * sigma2 * dms * dms / 2.)", RooArgList(frac, sigma, dms, sigma2))
sigma_eff = RooFormulaVar("sigma_eff", "sqrt((-2. / (dms * dms)) * log(dilution))", RooArgList(dms, dilution))

print("Starting the fit!")

modelName = "model"
if options.fitModel == "gauss":
    model = RooAddPdf(modelName, modelName, RooArgList(gaus1), RooArgList())
elif options.fitModel == "2gauss":
    model = RooAddPdf(modelName, modelName, RooArgList(gaus1, gaus2), RooArgList(frac))
else:
    assert(False)


dataset2 = dataset.reduce("lab0_LifetimeFit_TAU_PULL > {} && lab0_LifetimeFit_TAU_PULL < {}".format(*x_range))
print("{} events".format(dataset2.numEntries()))

frame = w.var("lab2_MM").frame(1890., 2070.)
dataset.plotOn(frame)
c = ROOT.TCanvas('c', 'c')
frame.Draw()
c.SaveAs("DataPlots/lab2_MM_{}.pdf".format(desc))
del frame

result = model.fitTo(dataset2, RooFit.Range(*x_range), RooFit.Save())
if result:
    result.Print()

with open("{}/Fit_Pull.txt".format(fit_dir_no_bins), "w") as output:
    output.write(str(sigma.getVal()) + " \\pm " + str(sigma.getError()) + "\n")
    output.write(str(sigma2.getVal()) + " \\pm " + str(sigma2.getError()) + "\n")
    output.write(str(frac.getVal()) + " \\pm " + str(frac.getError()) + "\n")
    output.write(str(resolution.getVal()) + " \\pm " + str(resolution.getPropagatedError(result)) + "\n")
    output.write(str(dilution.getVal()) + " \\pm " + str(dilution.getPropagatedError(result)) + "\n")
    output.write(str(sigma_eff.getVal()) + " \\pm " + str(sigma_eff.getPropagatedError(result)) + "\n")

w = RooWorkspace("w")
i(w, dataset)
i(w, model)
w.writeToFile("{}/w_Fit_Pull.root".format(fit_dir_no_bins))

plot_precision = RooFit.Precision(1e-5)

frame = x.frame(*x_range)
dataset.plotOn(frame)
model.plotOn(frame)

pull_hist = frame.pullHist()

model.plotOn(frame, RooFit.Components('gaus1'), RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(ROOT.kOrange),  plot_precision)
if options.fitModel == "2gauss":
    model.plotOn(frame, RooFit.Components('gaus2'), RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(ROOT.kMagenta), plot_precision)
frame.SetMinimum(0.)

frame_pull = x.frame(RooFit.Range(*x_range), RooFit.Title(""))
frame_pull.addPlotable(pull_hist, "P")
frame_pull.SetMinimum(-5.)
frame_pull.SetMaximum( 5.)
frame_pull.GetYaxis().SetNdivisions(110)
frame_pull.GetYaxis().SetLabelSize(0.1)
frame_pull.GetYaxis().CenterTitle()
frame_pull.GetYaxis().SetTitleSize(0.17)
frame_pull.GetYaxis().SetTitleOffset(0.38)
frame_pull.GetXaxis().SetNdivisions(frame.GetXaxis().GetNdivisions())

c = ROOT.TCanvas('c', 'c')
c.Divide(2)
c.GetPad(1).SetPad(0.0,0.0,1.0,0.8)
c.GetPad(2).SetPad(0.0,0.8,1.0,1.0)
c.GetPad(1).SetLeftMargin(0.15)
c.GetPad(2).SetLeftMargin(0.15)
c.GetPad(2).SetBottomMargin(0.0)
c.GetPad(1).SetTopMargin(0.0)

c.cd(1)
frame.Draw()
c.cd(2)
frame_pull.Draw()
c.SaveAs("{}/Fit_Pull.pdf".format(fit_dir_no_bins))

del c
del dataset
del x
del model
del pull_hist
del frame
del frame_pull
del w

f.Close()
del f

