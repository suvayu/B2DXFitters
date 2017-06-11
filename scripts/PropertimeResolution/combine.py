from include import *
from array import array

def read_value_error(f):
    return tuple(map(float, f.readline().strip().split(" \\pm ")))

myBins = []
bin_means = []
resolution = []
for (bIndex, b) in enumerate(bins):
    if bIndex == len(myBins) - 1: continue
    myBins.append(b)
    f = open("{}/{:03d}.txt".format(fit_dir, bIndex))
    bin_means.append(float(f.readline().strip()))
    mean = read_value_error(f)
    sigma = read_value_error(f)
    sigma2 = read_value_error(f)
    frac = read_value_error(f)
    myResolution = read_value_error(f)
    dilution = read_value_error(f)
    sigma_eff = read_value_error(f)
    if options.combVar == "sigma":
        resolution.append(sigma)
    elif options.combVar == "weighted_sum":
        resolution.append(myResolution)
    elif options.combVar == "eff_sigma":
        resolution.append(sigma_eff)
    else:
        assert(False)
    f.close()

c = ROOT.TCanvas("c", "c", 800, 600)
c.cd()

graph = ROOT.RooHist(myBins[0][1] - myBins[0][0])
for (b, m, v) in zip(myBins, bin_means, resolution):
    if options.centerBin:
        bin_mean = m
        lower_error = bin_mean - b[0]
        upper_error = b[1] - bin_mean
    else:
        bin_mean = sum(b) / 2.
        lower_error = upper_error = b[1] - b[0]

    graph.addBinWithXYError(bin_mean, v[0], lower_error, upper_error, v[1], v[1])

bounds = (myBins[0][0], myBins[-1][1])

graph.SetTitle("Decay-time resolution")
graph.SetMarkerStyle(ROOT.kDot)
graph.GetXaxis().SetTitle("Per-event decay-time error ({})".format('fs'))
graph.GetXaxis().SetRangeUser(0., bounds[1])
graph.GetYaxis().SetTitle("Decay-time resolution ({})".format('fs'))
graph.GetYaxis().SetTitleOffset(1.25)
graph.GetYaxis().SetRangeUser(0., bounds[1])

mean = 40.

formula = ROOT.TF1("fquad", "[0]*x*x + [1]*x + [2]", *bounds)
formula.SetParameter(0, 0.)
formula.SetParameter(1, 1.)
formula.SetParameter(2, 0.)
formula.SetLineColor(ROOT.kBlue)
fitResult_quad = graph.Fit(formula, "VS+")
fitResult_quad.Print()

formula = ROOT.TF1("flin", "[0]*x", *bounds)
formula.SetParameter(0, 1.)
formula.SetParameter(1, 0.)
formula.SetLineColor(ROOT.kRed)
fitResult_lin = graph.Fit(formula, "VS+")
fitResult_lin.Print()

formula = ROOT.TF1("flin_decor", "[0]*(x-{}) + [1]".format(mean), *bounds)
formula.SetParameter(0, 1.)
formula.SetParameter(1, 55.)
formula.SetLineColor(ROOT.kMagenta)
fitResult_lin_decor = graph.Fit(formula, "VS+")
fitResult_lin_decor.Print()

#formula = ROOT.TF1("fmodel", "sqrt([0]*[0]*x*x + [1]*[1])", *bounds)
#formula.SetParameter(0, 1.)
#formula.SetParameter(1, 0.)
#formula.SetLineColor(ROOT.kCyan)
#fitResult_model = graph.Fit(formula, "VS+")
#fitResult_model.Print()

one = ROOT.TF1("one", "x", *bounds)
one.SetLineColor(ROOT.kGreen)
old = ROOT.TF1("old", "1.37*x", *bounds)
old.SetLineColor(ROOT.kOrange)

c = ROOT.TCanvas("c", "c", 800, 600)
c.cd()

graph.Draw("APZ0")
one.Draw("SAME")
old.Draw("SAME")
ROOT.gPad.Modified()
ROOT.gPad.Update()

c.SaveAs("{}/CombinationLinear_{}.pdf".format(fit_dir, comb_desc))

with open("{}/CombinationLinear_{}.txt".format(fit_dir, comb_desc), "w") as f:
    f.write("Quadratic: ({:.3f} \\pm {:.3f}) \\delta_{{\\tau}}^2 + ({:.3f} \\pm {:.3f}) \\delta_{{\\tau}} + ({:.3f} \\pm {:.3f})\n".format(fitResult_quad.Value(0), fitResult_quad.Error(0), fitResult_quad.Value(1), fitResult_quad.Error(1), fitResult_quad.Value(2), fitResult_quad.Error(2)))
    f.write("Linear: ({:.3f} \\pm {:.3f}) \\delta_{{\\tau}} + ({:.3f} \\pm {:.3f})\n".format(fitResult_lin.Value(0), fitResult_lin.Error(0), fitResult_lin.Value(1), fitResult_lin.Error(1)))
    f.write("Linear (decorrelated): ({:.3f} \\pm {:.3f}) (\\delta_{{\\tau}} - 40 fs) + ({:.3f} \\pm {:.3f})\n".format(fitResult_lin_decor.Value(0), fitResult_lin_decor.Error(0), fitResult_lin_decor.Value(1), fitResult_lin_decor.Error(1)))

"""
# DILUTION
graph = ROOT.RooHist(myBins[0][1] - myBins[0][0])
for (b, v) in zip(myBins, dilution):
    graph.addBinWithError((b[1] + b[0]) / 2., v[0], v[1], v[1], b[1] - b[0], 1., ROOT.kFALSE)

graph.SetTitle("Dilution")
graph.SetMarkerStyle(ROOT.kDot)
graph.GetXaxis().SetTitle("Per-event decay-time error")
graph.GetXaxis().SetRangeUser(myBins[0][0], myBins[-1][1])
graph.GetYaxis().SetTitle("Dilution")
graph.GetYaxis().SetTitleOffset(1.25)
graph.GetYaxis().SetRangeUser(0., 1.)

graph.Draw("AP")
c.SaveAs("FitResults/Dilution_{}.pdf".format(desc))
"""

