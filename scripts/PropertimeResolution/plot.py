from include import *
import sys

plot_precision = RooFit.Precision(1e-5)

for (bIndex, b) in enumerate(bins):
    f = ROOT.TFile.Open("{}/w_Fit_bin{:03d}.root".format(fit_dir, bIndex))
    w = f.Get("w")

    dataset = w.data("dataset_M_fakeBs_{}".format(desc))

    x = w.var(xVarName)
    model = w.pdf("model_{:03d}".format(bIndex))

    bin_mean = sum(b) / 2.
    est_sigma = bin_mean * 1.3
    if options.fitModel == "gauss":
        fit_bounds = (max(-250., -2.5 * est_sigma), 1.0 * est_sigma)
        if bIndex == 0:
            fit_bounds = (-40., 10.)
    elif options.fitModel == "2gauss":
        fit_bounds = (-300., 0.75 * est_sigma)
    else:
        assert(False)

    if desc_DsPi_MC in desc or desc_DsK_MC_LTUB in desc:
        fit_bounds = (-3. * est_sigma, 3. * est_sigma)

    plot_range = (-300., 300.)

    x.setMin(fit_bounds[0])
    x.setMax(fit_bounds[1])

    frame = x.frame(*plot_range)
    dataset.plotOn(frame)
    model.plotOn(frame)

    pull_hist = frame.pullHist()

    model.plotOn(frame, RooFit.Components('gaus1'), RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(ROOT.kOrange),  plot_precision)
    if options.fitModel == "2gauss":
        model.plotOn(frame, RooFit.Components('gaus2'), RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(ROOT.kMagenta), plot_precision)
    frame.SetMinimum(0.)

    frame_pull = w.var(xVarName).frame(RooFit.Range(*plot_range), RooFit.Title(""))
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
    c.SaveAs("{}/bin{:03d}.pdf".format(fit_dir, bIndex))

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

