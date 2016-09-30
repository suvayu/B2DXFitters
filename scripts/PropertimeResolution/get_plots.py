from include import *
import os

f = ROOT.TFile.Open(in_file_name, "READ")
t = f.Get("DecayTree")

cuts = "lab0_LifetimeFit_ctau0 > -1. && lab0_LifetimeFit_ctau0 < 1. && lab0_LifetimeFit_ctauErr0 > 0. && lab0_LifetimeFit_ctauErr0 < 0.1"
cuts_bin = "lab0_LifetimeFit_ctau0 > -10.5 && lab0_LifetimeFit_ctau0 < 10.5 && lab0_LifetimeFit_ctauErr0/{0} > 23.44 && lab0_LifetimeFit_ctauErr0/{0} < 24.24".format(speedOfLight_mm_fs)

plots_dir = "TTreePlots/{}".format(desc)
if not os.path.isdir(plots_dir):
    os.makedirs(plots_dir)

draw_options = "E P0"

c = ROOT.TCanvas("c", "c", 800, 600)
t.Draw("lab0_LifetimeFit_ctau0", cuts, draw_options)
ROOT.gROOT.FindObject("htemp").GetXaxis().SetRangeUser(-0.005 * speedOfLight, 0.005 * speedOfLight)
c.SaveAs("{}/lab0_LifetimeFit_ctau0_mm.pdf".format(plots_dir))
del c

c = ROOT.TCanvas("c", "c", 800, 600)
t.Draw("lab0_LifetimeFit_ctau0/{}".format(speedOfLight), cuts, draw_options)
ROOT.gROOT.FindObject("htemp").GetXaxis().SetRangeUser(-0.005, 0.005)
c.SaveAs("{}/lab0_LifetimeFit_ctau0_ns.pdf".format(plots_dir))
del c

c = ROOT.TCanvas("c", "c", 800, 600)
t.Draw("lab0_LifetimeFit_ctauErr0/{}".format(speedOfLight), cuts, draw_options)
c.SaveAs("{}/lab0_LifetimeFit_ctauErr0_ns.pdf".format(plots_dir))
del c

c = ROOT.TCanvas("c", "c", 800, 600)
t.Draw("lab0_LifetimeFit_ctauErr0/{}".format(speedOfLight_mm_fs), cuts, draw_options)
c.SaveAs("{}/lab0_LifetimeFit_ctauErr0_fs.pdf".format(plots_dir))
del c

c = ROOT.TCanvas("c", "c", 800, 600)
t.Draw("lab0_LifetimeFit_ctau0/{}".format(speedOfLight), cuts_bin, draw_options)
c.SaveAs("{}/lab0_LifetimeFit_ctau0_ns_bin.pdf".format(plots_dir))
del c

c = ROOT.TCanvas("c", "c", 800, 600)
t.Draw("lab0_LifetimeFit_ctau0/{}".format(speedOfLight_mm_fs), cuts, draw_options)
c.SaveAs("{}/lab0_LifetimeFit_TAU.pdf".format(plots_dir))
del c

c = ROOT.TCanvas("c", "c", 800, 600)
t.Draw("lab1_P", "lab1_P < 250000", draw_options)
c.SaveAs("{}/lab1_P.pdf".format(plots_dir))
del c

c = ROOT.TCanvas("c", "c", 800, 600)
t.Draw("lab0_LifetimeFit_ctau0/{}".format(speedOfLight_mm_fs), cuts_bin, draw_options)
c.SaveAs("{}/lab0_LifetimeFit_TAU_bin.pdf".format(plots_dir))
del c

if is_MC:
    c = ROOT.TCanvas("c", "c", 800, 600)
    t.Draw("lab0_TRUETAU/{}".format(ns_to_fs), "", draw_options)
    c.SaveAs("{}/lab0_TRUETAU.pdf".format(plots_dir))
    del c

    c = ROOT.TCanvas("c", "c", 800, 600)
    t.Draw("lab0_LifetimeFit_ctau0/{}-lab0_TRUETAU/{}".format(speedOfLight_mm_fs, ns_to_fs), "lab0_TRUETAU > 0.", draw_options)
    c.SaveAs("{}/lab0_TAU_DIFF.pdf".format(plots_dir))
    del c

