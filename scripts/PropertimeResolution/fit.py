from include import *

def format_results(var): return "{} \\pm {}".format(var.getVal(), var.getError())

ROOT.Math.MinimizerOptions.SetDefaultPrecision(1e-9)

print("Opening the workspace...")
f = ROOT.TFile.Open("{}/w_data_{}.root".format(ws_dir, desc))
if not f and desc is desc_DsPi_MC:
    f = ROOT.TFile.Open("{}/w_SWeighted_{}.root".format(ws_dir, desc_ALL))
w = f.Get("w")

if desc is desc_DsPi_MC:
    dataset = w.data("mc")
else:
    dataset = ROOT.TFile.Open("{}/dataset_M_fakeBs_{}.root".format(ws_dir, desc)).Get("dataset_M_fakeBs_{}".format(desc))
    assert(isinstance(dataset, ROOT.RooAbsData))

x = w.var(xVarName)
assert(isinstance(x, ROOT.RooAbsReal))

print("Preparing the fit shape...")
mean   = RooRealVar('mean',   'mean',  -20.0,  20.)
sigma  = RooRealVar('sigma',  'sigma',   0.1,  90.)
sigma2 = RooRealVar('sigma2', 'sigma2', 10.0, 400.)

gaus1 = RooGaussian('gaus1', 'gaus1', x, mean, sigma)
gaus2 = RooGaussian('gaus2', 'gaus2', x, mean, sigma2)

frac = RooRealVar('frac', 'frac', 0.5, 1.)

resolution = RooFormulaVar("resolution", "sqrt(frac * sigma * sigma + (1. - frac) * sigma2 * sigma2)", RooArgList(frac, sigma, sigma2))
dilution = RooFormulaVar("dilution", "frac * exp(-sigma * sigma * dms * dms / 2.) + (1. - frac) * exp(-sigma2 * sigma2 * dms * dms / 2.)", RooArgList(frac, sigma, dms, sigma2))
sigma_eff = RooFormulaVar("sigma_eff", "sqrt((-2. / (dms * dms)) * log(dilution))", RooArgList(dms, dilution))

print("Starting the fit!")
for (bIndex, b) in enumerate(bins):
    print("Fitting bin {:03d}/{:03d}".format(bIndex, len(bins)))
    bin_mean = sum(b) / 2.
    est_sigma = bin_mean * 1.3

    modelName = "model_{:03d}".format(bIndex)
    if options.fitModel == "gauss":
        model = RooAddPdf(modelName, modelName, RooArgList(gaus1), RooArgList())
        fit_bounds = (max(-250., -2.5 * est_sigma), 1.0 * est_sigma)
        if bIndex == 0:
            fit_bounds = (-40., 10.)
    elif options.fitModel == "2gauss":
        model = RooAddPdf(modelName, modelName, RooArgList(gaus1, gaus2), RooArgList(frac))
        fit_bounds = (-300., 0.75 * est_sigma)
    else:
        assert(False)

    if desc_DsPi_MC in desc or desc_DsK_MC_LTUB in desc:
        fit_bounds = (-3. * est_sigma, 3. * est_sigma)
        if bIndex == 0:
            fit_bounds = (-65., 65.)

    range_name = "R{:03d}".format(bIndex)
    x.setRange(range_name, fit_bounds[0], fit_bounds[1])

    x.setMin(fit_bounds[0])
    x.setMax(fit_bounds[1])

    mean.setVal(0.)
    sigma.setMax(est_sigma * 1.5)
    sigma.setVal(est_sigma)
    sigma.setMin(est_sigma * 0.5)
    sigma2.setVal(2. * est_sigma)
    sigma2.setMin(est_sigma * 1.5)
    frac.setMax(1.)
    frac.setVal(.8)
    frac.setMin(.5)

    p_bin_cut = "&& (lab1_P > {} && lab1_P < {})".format(*p_bin) if p_bin else ""
    pt_bin_cut = "&& (lab1_PT > {} && lab1_PT < {})".format(*pt_bin) if pt_bin else ""
    t_bin_cut = "&& (lab0_LifetimeFit_TAU > {} && lab0_LifetimeFit_TAU < {})".format(*t_bin) if t_bin else ""
    redData = dataset.reduce("lab0_LifetimeFit_TAUERR > {} && lab0_LifetimeFit_TAUERR <= {}{}{}{}".format(b[0], b[1], p_bin_cut, pt_bin_cut, t_bin_cut))
    result = model.fitTo(redData, RooFit.Range(range_name), RooFit.SumW2Error(False), RooFit.Save())
    if result:
        result.Print()

    bin_mean = redData.mean(w.var("lab0_LifetimeFit_TAUERR"))

    with open("{}/{:03d}.txt".format(fit_dir, bIndex), "w") as output:
        output.write(str(bin_mean) + "\n")
        output.write(str(mean.getVal()) + " \\pm " + str(mean.getError()) + "\n")
        output.write(str(sigma.getVal()) + " \\pm " + str(sigma.getError()) + "\n")
        output.write(str(sigma2.getVal()) + " \\pm " + str(sigma2.getError()) + "\n")
        output.write(str(frac.getVal()) + " \\pm " + str(frac.getError()) + "\n")
        output.write(str(resolution.getVal()) + " \\pm " + str(resolution.getPropagatedError(result)) + "\n")
        output.write(str(dilution.getVal()) + " \\pm " + str(dilution.getPropagatedError(result)) + "\n")
        output.write(str(sigma_eff.getVal()) + " \\pm " + str(sigma_eff.getPropagatedError(result)) + "\n")

    w = RooWorkspace("w")
    i(w, redData)
    i(w, model)
    w.writeToFile("{}/w_Fit_bin{:03d}.root".format(fit_dir, bIndex))

