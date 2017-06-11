# Bs→DsK Propertime Resolution studies

This is documentation related to the Propertime Resolution scripts written by Lennaert Bel for the time-dependent Bs→DsK analysis.

---
## Requirements
* ROOT 6 with `pyroot` (Python 2 or 3). I'ved used `ROOT 6.06/02` to perform my analysis;
* Access to `eos`.

All the requirements should be fulfilled on `lxplus` after setting up `DaVinci` (or a similar project).

---
## Terms
 * `LTUB` Lifetime-unbiased
 * `lab_0` The _Ds_ + bachelor combination
 * `lab_1` The bachelor
 * `lab_2` The _Ds_
 * `lab_3`, `lab_4`, `lab_5` The _Ds_ daughters
 * `lab2_MM` The _Ds_ invariant mass, in `MeV`
 * `lab0_LifetimeFit_*` A variable obtained by refitting the PV without the _Ds_ daughter tracks
 * `lab0_LifetimeFit_ctau0` The reconstructed decay time, in `mm`
 * `lab0_LifetimeFit_ctauErr0` The per-event decay-time error, in `mm`
 * `lab0_LifetimeFit_TAU` (`lab0_LifetimeFit_TAUERR`) The decay time (error), in `fs`

---
## Script files

You should have a copy of the following files:
  - `combine.py`
  - `data_plots.py`
  - `fit.py`
  - `fit_pull.py`
  - `get_bins.py`
  - `get_data.py`
  - `get_plots.py`
  - `include.py`
  - `plot.py`
  - `sWeightPlots.py`
  - `sWeights.py`

The files are described below, in the recommended order of running them. Most scripts support options, described below.

##### `include.py`
This file contains preprocessing instructions for all the other files and is not supposed to be run standalone.
##### `get_data.py`
Takes the data from the grid locations as described in `include.py` and store them in the `Workspaces` directory.
##### `get_plots.py`
Creates plot directly from the grid data, for cross-checking purposes, and store them in the `TTreePlots` directory.
##### `data_plots.py`
Create plots from the `RooDataSet`s made by `get_data.py` and save them in the `DataPlots` directory.
##### `sWeights.py`
Make _sWeights_ to the _Ds_ mass (`lab2_MM`), storing the resulting datasets in `Workspaces`. Also create some related plots in the `SWeightPlots` directory.
##### `get_bins.py`
Figures out a recommended binning scheme from the _sWeighted_ data, for a particular variable. Text output must be manually copied into `include.py`.
##### `sWeightPlots.py`
Create additional _sWeight_-related plots in the `SWeightPlots` directory.
##### `fit_pull.py`
Perform a fit to the lifetime pull distribution (lifetime divided by per-event error), saving the results and plots in the `FitResults` directory.
##### `fit.py`
Perform fits to individual per-event decay-time error bins. The results are stored in the `FitResults` directory.
##### `plot.py`
Create plots from the fits done by `fit.py`, storing them next to the fit results.
##### `combine.py`
Combine the results of the individual fits, and perform a fit to them. The results are also stored in the `FitResults` directory.

---
## Options
The options are as follows:
 * `-d` Description of the data subset to be used. The default is `ALL`. Can be one of the following MC samples:
   * `Ds_MC` (prompt _Ds_ MC);
   * `DsK_MC` (lifetime unbiased signal Bs→DsK MC);
   * `DsPi_MC` (lifetime biased signal Bs→Dsπ MC).

   Or the following format for data samples:
   * `ALL` (for all data combined);
   * `Y_M_F`, where `Y` is the year of data taking (`2011` or `2012`), `M` is the magnet polarity (`Up` or `Dw`), and `F` is the final state to consider (`KstK`, `phipi`, or `ALL` for everything combined).
 * `-n` Number of per-event decay-time errors to use. The default is 20. Can be any integer for which a binning specifiction is present in `include.py`.
 * `-f` Fit model. Can be `gauss` for single-Gauss fits, or `2gauss` (default) for double-Gauss fits.
 * `-c` Combination variable (only for `combine.py`). What variable to use for combining results from double-Gauss fits. Can be `sigma` (take the width of the narrow Gauss), `weighted_sum` (take the weighted-square-sum of the two widths), or `eff_sigma` (use an effective width obtained by combining the width using the diffusion).
 * `-p` The index of the bachelor momentum bin to use. Can be any integer for which a momentum bin is present in `include.py`.
 * `-b` The index of the bachelor transverse momentum bin to use. Can be any integer for which a transverse momentum bin is present in `include.py`.
 * `-t` The index of the decay-time bin to use. Can be any integer for which a decay-time bin is present in `include.py`.

The bin index options `-p`, `-b`, and `-t` can be conveniently run inside a `bash` loop, as follows:
```bash
for t in $(seq 0 4); do    # run for t = 0, 1, 2, 3, 4
  python fit.py -t$t       # run for the specified decay-time bin
done
```

---
## Directories
 * `DataPlots` Contains plots taken from the `RooDataSet`s produced with `get_data.py`.
 * `FitResults` Contains results and plots produced by `fit.py`, `plot.py`, and `combine.py`. The root and text files contain the fit results, where the contents of the text files are, in order,
   * The per-event error bin mean from data
   * The (shared) mean of the Gausses
   * The sigma of the first Gauss
   * The sigma of the second Gauss
   * The size of the first Gauss (the second Gauss has 1 – this number)
   * The weighted-square-sum of the two sigmas, `sqrt(f * sigma_1 * sigma_1 + (1-f) * sigma_2 * sigma_2)`
   * The dilution
   * The two sigmas, combined using the dilution
 * `SWeightPlots` Contains plots from the _sWeighting_ procedure, as well as data plots produced on the data after applying weights.
 * `TTreePlots` Contains plots taken directly from the tuples on `eos`.
 * `Workspaces` Contains the root objects with the data.
