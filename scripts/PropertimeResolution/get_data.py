import ROOT
from ROOT import RooArgList, RooArgSet, RooDataSet, RooFit, RooFormulaVar, RooRealVar, RooStats, RooWorkspace
from include import *

# Get the TTree with the data from EOS
t = ROOT.TFile.Open(in_file_name, "READ").Get("DecayTree")

if desc == desc_Prompt_MC:
    lab0_TRUETAU_range = (-1000., -0.5)
    lab0_MM_range = (4000., 6850.)
    lab2_MM_range = (1940., 2000.)
else:
    lab0_TRUETAU_range = (0., 0.02)
    lab0_MM_range = (5000., 6850.)
    lab2_MM_range = (1890., 2068.)

# All the RooFit variables we'll be needing
lab2_MM = RooRealVar("lab2_MM", "lab2_MM", lab2_MM_range[0], lab2_MM_range[1], "MeV/c^{2}")
lab2_IP_OWNPV = RooRealVar("lab2_IP_OWNPV", "lab2_IP_OWNPV", 0., 150.)
lab0_LifetimeFit_ctau0 = RooRealVar("lab0_LifetimeFit_ctau0", "lab0_LifetimeFit_ctau0", -100., 100., "mm")
lab0_TRUETAU = RooRealVar("lab0_TRUETAU", "lab0_TRUETAU", lab0_TRUETAU_range[0], lab0_TRUETAU_range[1], "ns")
lab0_LifetimeFit_ctauErr0 = RooRealVar("lab0_LifetimeFit_ctauErr0", "lab0_LifetimeFit_ctauErr0", 0.001, 1., "mm")
lab0_MM = RooRealVar("lab0_MM", "lab0_MM", lab0_MM_range[0], lab0_MM_range[1], "MeV/c^{2}")
#lab0_P = RooRealVar("lab0_P", "lab0_P", 15000., 500000., "MeV/c")
lab1_P = RooRealVar("lab1_P", "lab1_P", 0., 500000., "MeV/c")
lab1_PT = RooRealVar("lab1_PT", "lab1_PT", 0., 100000., "MeV/c")
#lab2_P = RooRealVar("lab2_P", "lab2_P", 5000., 500000., "MeV/c")
allVars = [lab2_MM, lab2_IP_OWNPV, lab0_LifetimeFit_ctau0, lab0_LifetimeFit_ctauErr0, lab0_MM, lab1_P, lab1_PT]
varSet = RooArgSet(*allVars)
if is_MC:
    varSet.add(lab0_TRUETAU)
varSetMC = RooArgSet(*allVars)
varSetMC.add(lab0_TRUETAU)

# The actual RooDataSet containing the data (this may take a while)
print("Getting the data...")
dataset = RooDataSet("data", "data", t, varSet)
print("Done!")

# Add unit-corrected LifetimeFit variables (mm -> fs)
lab0_LifetimeFit_TAU = dataset.addColumn(RooFormulaVar("lab0_LifetimeFit_TAU", "lab0_LifetimeFit_TAU", "lab0_LifetimeFit_ctau0/{}".format(speedOfLight_mm_fs), RooArgList(lab0_LifetimeFit_ctau0)))
lab0_LifetimeFit_TAU.setUnit("fs")
lab0_LifetimeFit_TAU.setMin(-500.)
lab0_LifetimeFit_TAU.setMax(50000.)
lab0_LifetimeFit_TAUERR = dataset.addColumn(RooFormulaVar("lab0_LifetimeFit_TAUERR", "lab0_LifetimeFit_TAUERR", "lab0_LifetimeFit_ctauErr0/{}".format(speedOfLight_mm_fs), RooArgList(lab0_LifetimeFit_ctauErr0)))
lab0_LifetimeFit_TAUERR.setUnit("fs")
lab0_LifetimeFit_TAUERR.setMin(  0.)
lab0_LifetimeFit_TAUERR.setMax(150.)

# Add difference between measured and true lifetime as a variable
#taudiff = dataset.addColumn(RooFormulaVar("lab0_LifetimeFit_TAU_DIFF", "lab0_LifetimeFit_TAU_DIFF",\
        #"lab0_LifetimeFit_ctau0/{}-lab0_TRUETAU/{}".format(speedOfLight_mm_fs, ns_to_fs), RooArgList(lab0_LifetimeFit_ctau0, lab0_TRUETAU)))
#taudiff.setUnit("fs")
#taudiff.setMin(-500.)
#taudiff.setMax( 1500.)

# Add log(IP) and the lifetime pull as variables
#lab2_logIP = dataset.addColumn(RooFormulaVar("log(lab2_IP_OWNPV)", "log(lab2_IP_OWNPV)", RooArgList(lab2_IP_OWNPV)))
#lab2_logIP.setMin(-10.)
#lab2_logIP.setMax(  5.)

if is_MC and not desc == desc_Prompt_MC:
    pull_formula = "(lab0_LifetimeFit_ctau0/{}-lab0_TRUETAU/{})/(lab0_LifetimeFit_ctauErr0/{})".format(speedOfLight_mm_fs, ns_to_fs, speedOfLight_mm_fs)
    args = [lab0_LifetimeFit_ctau0, lab0_TRUETAU, lab0_LifetimeFit_ctauErr0]
else:
    pull_formula = "lab0_LifetimeFit_ctau0/lab0_LifetimeFit_ctauErr0"
    args = [lab0_LifetimeFit_ctau0, lab0_LifetimeFit_ctauErr0]

tauOverTauErr = dataset.addColumn(RooFormulaVar("lab0_LifetimeFit_TAU_PULL", "lab0_LifetimeFit_TAU_PULL", pull_formula, RooArgList(*args)))
tauOverTauErr.setMin(-8.)
tauOverTauErr.setMax( 8.)

nentries = dataset.numEntries()
print('Number of entries: {}'.format(nentries))

# Get the MC from EOS
"""
f_MC = ROOT.TFile.Open("root://eoslhcb.cern.ch//eos/lhcb/user/l/lbel/TD_DsK3fb_MC/B2DX_MC_Bs_Dspi_KKpi_PTR.root", "READ")
t_MC = f_MC.Get("DecayTree")
mc_data = RooDataSet("mc", "mc", t_MC, varSetMC)
# Add difference between measured and true lifetime as a variable
taudiff = mc_data.addColumn(RooFormulaVar("lab0_LifetimeFit_TAU_DIFF", "lab0_LifetimeFit_TAU_DIFF", "lab0_LifetimeFit_TAU-(lab0_TRUETAU/{})".format(ns_to_fs), RooArgList(lab0_LifetimeFit_TAU, lab0_TRUETAU)))
taudiff.setUnit("fs")
taudiff.setMin(-1.)
taudiff.setMax( 1.)
"""

# Create the RooWorkspace
w = RooWorkspace('w')
for v in allVars: i(w, v)
if is_MC: i(w, lab0_TRUETAU)
i(w, dataset)
#i(w, mc_data)

# Save the workspace
print("Saving workspace...")
w.writeToFile('{}/w_data_{}.root'.format(ws_dir, desc))
print("Done")

