from optparse import OptionParser
import itertools
import ROOT
from ROOT import RooFit, RooAddPdf, RooArgList, RooArgSet, RooCBShape, RooFormulaVar, RooGaussian, RooRealVar, RooWorkspace

ROOT.gROOT.SetBatch()
ROOT.Math.MinimizerOptions.SetDefaultPrecision(1e-10)

def i(w, *args): getattr(w, "import")(*args)

ns_to_fs = 1e-6
speedOfLight = 299.792458 #mm/ns
speedOfLight_mm_fs = 299.792458 * ns_to_fs #mm/fs

descs = ["_".join(x) for x in list(itertools.product(("2011", "2012"), ("Up", "Dw"), ("KstK", "phipi", "ALL")))]
desc_Prompt_MC = "Ds_MC"
desc_DsPi_MC = "DsPi_MC"
desc_DsK_MC_LTUB = "DsK_MC_LTUB"
desc_ALL = "ALL"

desc_list = descs + [desc_Prompt_MC, desc_DsPi_MC, desc_DsK_MC_LTUB, desc_ALL]

parser = OptionParser()
parser.add_option("-p", "--pBin", dest="pBin", type="int", default=None, help="bin of bachelor momentum to use, or None to disable")
parser.add_option("-b", "--ptBin", dest="ptBin", type="int", default=None, help="bin of bachelor pT to use, or None to disable")
parser.add_option("-t", "--tBin", dest="tBin", type="int", default=None, help="bin of reconstructed lifetime to use, or None to disable")
parser.add_option("-n", "--nBins", dest="nBins", type="int", default=20, help="number of bins")
parser.add_option("-d", "--desc", dest="desc", type="choice", choices=desc_list, default="ALL", help="description of data to use")
parser.add_option("-f", "--fitModel", dest="fitModel", type="choice", choices=["gauss", "2gauss"], default="2gauss", help="how to fit the lifetime distributions")
parser.add_option("-c", "--combVar", dest="combVar", type="choice", choices=["sigma", "weighted_sum", "eff_sigma"], default="eff_sigma", help="what variable to use for combining the results")
parser.add_option("--centerBin", "--centreBin", dest="centerBin", action="store_true", default=False, help="whether to use the mean of the data as the bin center rather than the middle of the bin")

(options, args) = parser.parse_args()
nBins = options.nBins
desc = options.desc
fit_desc = desc
is_MC = desc in [desc_Prompt_MC, desc_DsPi_MC, desc_DsK_MC_LTUB]

if options.fitModel == "gauss":
    options.combVar = "sigma"

if desc is not desc_ALL:
    desc_1 = "_".join(desc.split("_")[:2])
    desc_2 = desc.split(desc_1+"_")[-1]


if desc == desc_DsPi_MC or desc == desc_DsK_MC_LTUB:
    xVarName = "lab0_LifetimeFit_TAU_DIFF"
else:
    xVarName = "lab0_LifetimeFit_TAU"

bins = {100: [0.098, 14.375, 15.836, 16.88, 17.738, 18.485, 19.162, 19.79, 20.381, 20.939, 21.475, 21.985, 22.481, 22.963, 23.428, 23.884, 24.332, 24.771, 25.204, 25.628, 26.049, 26.46, 26.867, 27.265, 27.662, 28.047, 28.435, 28.816, 29.191, 29.56, 29.923, 30.287, 30.645, 30.998, 31.345, 31.689, 32.029, 32.362, 32.694, 33.026, 33.356, 33.683, 34.006, 34.33, 34.652, 34.969, 35.288, 35.605, 35.921, 36.236, 36.552, 36.871, 37.19, 37.509, 37.826, 38.145, 38.465, 38.786, 39.11, 39.438, 39.77, 40.103, 40.441, 40.781, 41.128, 41.479, 41.834, 42.197, 42.564, 42.94, 43.321, 43.711, 44.113, 44.517, 44.935, 45.366, 45.807, 46.264, 46.734, 47.222, 47.728, 48.251, 48.799, 49.372, 49.977, 50.614, 51.286, 52.0, 52.765, 53.585, 54.474, 55.453, 56.536, 57.75, 59.142, 60.778, 62.781, 65.36, 69.008, 75.283, 150.0], 70: [0.098, 15.087, 16.744, 17.959, 18.977, 19.877, 20.704, 21.475, 22.199, 22.895, 23.558, 24.205, 24.833, 25.448, 26.049, 26.635, 27.209, 27.772, 28.324, 28.87, 29.403, 29.923, 30.442, 30.947, 31.444, 31.932, 32.41, 32.885, 33.356, 33.822, 34.284, 34.743, 35.197, 35.65, 36.102, 36.552, 37.009, 37.462, 37.917, 38.374, 38.832, 39.297, 39.77, 40.247, 40.73, 41.228, 41.733, 42.25, 42.779, 43.321, 43.882, 44.459, 45.057, 45.679, 46.33, 47.011, 47.728, 48.484, 49.287, 50.156, 51.089, 52.106, 53.225, 54.474, 55.902, 57.568, 59.578, 62.164, 65.799, 72.032, 150.0], 40: [0.098, 16.387, 18.485, 20.09, 21.475, 22.722, 23.884, 24.988, 26.049, 27.067, 28.047, 29.004, 29.923, 30.822, 31.689, 32.528, 33.356, 34.169, 34.969, 35.762, 36.552, 37.348, 38.145, 38.949, 39.77, 40.61, 41.479, 42.38, 43.321, 44.315, 45.366, 46.499, 47.728, 49.081, 50.614, 52.375, 54.474, 57.125, 60.778, 66.988, 150.0], 80: [0.098, 14.811, 16.387, 17.537, 18.485, 19.324, 20.09, 20.802, 21.475, 22.11, 22.722, 23.312, 23.884, 24.442, 24.988, 25.523, 26.049, 26.562, 27.067, 27.562, 28.047, 28.529, 29.004, 29.468, 29.923, 30.377, 30.822, 31.258, 31.689, 32.113, 32.528, 32.943, 33.356, 33.764, 34.169, 34.571, 34.969, 35.368, 35.762, 36.158, 36.552, 36.951, 37.348, 37.746, 38.145, 38.545, 38.949, 39.355, 39.77, 40.187, 40.61, 41.042, 41.479, 41.924, 42.38, 42.846, 43.321, 43.81, 44.315, 44.829, 45.366, 45.92, 46.499, 47.099, 47.728, 48.386, 49.081, 49.82, 50.614, 51.46, 52.375, 53.375, 54.474, 55.711, 57.125, 58.773, 60.778, 63.356, 66.988, 73.224, 150.0], 50: [0.098, 15.836, 17.738, 19.162, 20.381, 21.475, 22.481, 23.428, 24.332, 25.204, 26.049, 26.867, 27.662, 28.435, 29.191, 29.923, 30.645, 31.345, 32.029, 32.694, 33.356, 34.006, 34.652, 35.288, 35.921, 36.552, 37.19, 37.826, 38.465, 39.11, 39.77, 40.441, 41.128, 41.834, 42.564, 43.321, 44.113, 44.935, 45.807, 46.734, 47.728, 48.799, 49.977, 51.286, 52.765, 54.474, 56.536, 59.142, 62.781, 69.008, 150.0], 20: [10., 18.485, 21.475, 23.884, 26.049, 28.047, 29.923, 31.689, 33.356, 34.969, 36.552, 38.145, 39.77, 41.479, 43.321, 45.366, 47.728, 50.614, 54.474, 60.778, 150.0], 90: [0.098, 14.58, 16.088, 17.182, 18.078, 18.869, 19.584, 20.252, 20.88, 21.475, 22.041, 22.589, 23.119, 23.633, 24.135, 24.626, 25.107, 25.581, 26.049, 26.506, 26.956, 27.398, 27.834, 28.262, 28.691, 29.109, 29.519, 29.923, 30.327, 30.723, 31.112, 31.499, 31.878, 32.252, 32.621, 32.989, 33.356, 33.719, 34.078, 34.436, 34.794, 35.147, 35.499, 35.851, 36.201, 36.552, 36.907, 37.26, 37.613, 37.967, 38.323, 38.678, 39.038, 39.402, 39.77, 40.141, 40.515, 40.896, 41.283, 41.676, 42.075, 42.482, 42.898, 43.321, 43.755, 44.203, 44.655, 45.125, 45.61, 46.109, 46.63, 47.168, 47.728, 48.311, 48.924, 49.57, 50.254, 50.982, 51.757, 52.59, 53.492, 54.474, 55.565, 56.79, 58.193, 59.832, 61.844, 64.416, 68.051, 74.319, 150.0], 60: [0.098, 15.417, 17.182, 18.485, 19.584, 20.57, 21.475, 22.316, 23.119, 23.884, 24.626, 25.346, 26.049, 26.732, 27.398, 28.047, 28.691, 29.316, 29.923, 30.525, 31.112, 31.689, 32.252, 32.805, 33.356, 33.899, 34.436, 34.969, 35.499, 36.026, 36.552, 37.085, 37.613, 38.145, 38.678, 39.22, 39.77, 40.328, 40.896, 41.479, 42.075, 42.69, 43.321, 43.978, 44.655, 45.366, 46.109, 46.894, 47.728, 48.615, 49.57, 50.614, 51.757, 53.03, 54.474, 56.16, 58.193, 60.778, 64.416, 70.643, 150.0], 30: [0.098, 17.182, 19.584, 21.475, 23.119, 24.626, 26.049, 27.398, 28.691, 29.923, 31.112, 32.252, 33.356, 34.436, 35.499, 36.552, 37.613, 38.678, 39.77, 40.896, 42.075, 43.321, 44.655, 46.109, 47.728, 49.57, 51.757, 54.474, 58.193, 64.416, 150.0]}[nBins]

bins = [(bins[b], bins[b + 1]) for b in xrange(len(bins) - 1)]

dms = ROOT.RooRealVar("dms", "dms", 17.768 * .001, "fs^{-1}")
dms.setError(0.024 * .001)

p_bins = [(0., 10000.), (10000., 15000.), (15000., 25000.), (25000., 40000.), (40000., 500000.)]
p_bin = None
pt_bins = [(500., 850.), (850., 1150.), (1150., 1600.), (1600., 2500.), (2500., 100000.)]
pt_bin = None
t_bins = [(0., 500.), (500., 1200.), (1200., 1800.), (1800., 2500.), (2500., 10000.)]
t_bin = None

if options.pBin is not None:
    p_bin = p_bins[options.pBin]
    fit_desc = fit_desc + "_PBin{:02d}".format(options.pBin)
if options.ptBin is not None:
    pt_bin = pt_bins[options.ptBin]
    fit_desc = fit_desc + "_PtBin{:02d}".format(options.ptBin)
if options.tBin is not None:
    t_bin = t_bins[options.tBin]
    fit_desc = fit_desc + "_TrecBin{:02d}".format(options.tBin)

if options.fitModel == "gauss":
    fit_desc += "_SingleGauss"

comb_desc = fit_desc + "_" + options.combVar
if options.centerBin:
    comb_desc += "_CenterBin"

ws_dir = "Workspaces/{}".format(desc)
fit_dir_no_bins = "FitResults/{}".format(fit_desc)
fit_dir = "{}/{}Bins".format(fit_dir_no_bins, nBins)
import os
for d in [ws_dir, fit_dir]:
    if not os.path.isdir(d):
        os.makedirs(d)

if desc == desc_ALL:
    in_file_name = "root://eoslhcb.cern.ch//eos/lhcb/user/l/lbel/TD_DsK3fb_LTUB/MERGED/Bs_DsK_ALL.root"
elif desc == desc_Prompt_MC:
    in_file_name = "root://eoslhcb.cern.ch//eos/lhcb/user/l/lbel/TD_DsK3fb_MC_LTUB/PromptDsH2/PromptDsH2_PTR.root"
elif desc == desc_DsPi_MC:
    in_file_name = "root://eoslhcb.cern.ch//eos/lhcb/user/l/lbel/TD_DsK3fb_MC/B2DX_MC_Bs_Dspi_KKpi_PTR.root"
elif desc == desc_DsK_MC_LTUB:
    in_file_name = "root://eoslhcb.cern.ch//eos/lhcb/user/l/lbel/TD_DsK3fb_MC_LTUB/Bs_DsK/Bs_DsK_LTUB_Up.root"
else:
    year = desc.split("_")[0]
    fs = desc.split("_")[-1]
    mag = "Up" if "Up" in desc else "Dw"
    in_file_name = "root://eoslhcb.cern.ch//eos/lhcb/user/l/lbel/TD_DsK3fb_LTUB/MERGED/Bs_DsK_{0}_{1}_{2}.root".format(fs, year, mag)

