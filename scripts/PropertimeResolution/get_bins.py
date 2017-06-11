from include import *
import numpy as np

dataset = ROOT.TFile.Open("{}/dataset_M_fakeBs_{}.root".format(ws_dir, desc)).Get("dataset_M_fakeBs_{}".format(desc))
assert(isinstance(dataset, ROOT.RooAbsData))

#bin_var, cut, bin_counts  = "lab0_LifetimeFit_TAUERR", "abs(lab0_LifetimeFit_TAU) < 300.", [20, 30, 40, 50, 60, 70, 80, 90, 100]
bin_var, cuts, bin_counts = "lab1_PT", None, [5]
#bin_var, cuts, bin_counts = "lab1_P", None, [5]

if cuts:
    dataset = dataset.reduce(cuts)
taus = np.sort(np.array([dataset.get(i)[bin_var].getVal() for i in xrange(dataset.numEntries())]))
taus = taus[~np.isnan(taus)]
nTaus = float(len(taus))

def get_bins(nBins):
    finalBins = []
    for x in xrange(nBins):
        part = x/float(nBins)
        value = taus[int(part * nTaus)]
        #print("{}: {}".format(part, value))
        finalBins.append(round(value, 3))

    finalBins.append(np.ceil(taus[-1]))
    finalBins[0] = round(finalBins[0], 3)
    return finalBins

#print(get_bins(30))
print({x: get_bins(x) for x in bin_counts})
