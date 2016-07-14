from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    import ROOT
    from ROOT import *

    configdict["Decay"] = "Bd2DPi"
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5090,    6000    ],
                                                      "Name"                   : "BeautyMass",
                                                      "InputName"              : "lab0_FitDaughtersConst_M_flat"}

    configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1910    ],
                                                      "Name"                   : "CharmMass",
                                                      "InputName"              : "obsMassDminus"}

    configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.2,     15.0    ],
                                                      "Bins"                   : 40,
                                                      "Name"                   : "BeautyTime",
                                                      "InputName"              : "lab0_FitDaughtersPVConst_ctau_flat"}
    
    configdict["BasicVariables"]["BacP"]          = { "Range"                  : [2000.0,  650000.0],
                                                      "Name"                   : "BacP",
                                                      "InputName"              : "lab0_FitDaughtersConst_P0_P_flat"}

    configdict["BasicVariables"]["BacPT"]         = { "Range"                  : [400.0,   45000.0 ],
                                                      "Name"                   : "BacPT",
                                                      "InputName"              : "lab0_FitDaughtersConst_P0_PT_flat"}

    configdict["BasicVariables"]["BacPIDK"]       = { "Range"                  : [-999.0, 999.0     ],
                                                      "Name"                   : "BacPIDK",
                                                      "InputName"              : "lab1_PIDK"}

    configdict["BasicVariables"]["nTracks"]       = { "Range"                  : [15.0,    1000.0  ],
                                                      "Name"                   : "nTracks",
                                                      "InputName"              : "nTracks"}

    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range"                  : [0.01,    0.1     ],
                                                      "Name"                   : "BeautyTimeErr",
                                                      "InputName"              : "lab0_FitDaughtersPVConst_ctauErr_flat"}

    configdict["BasicVariables"]["BacCharge"]     = { "Range"                  : [-1000.0, 1000.0  ],
                                                      "Name"                   : "BacCharge",
                                                      "InputName"              : "lab1_ID"}

    configdict["BasicVariables"]["TagDecOS"]      = { "Range"                  : [-1.0,    1.0     ],
                                                      "Name"                   : "TagDecOS",
                                                      "InputName"              : "obsTagOS"}

    configdict["BasicVariables"]["TagDecSS"]      = { "Range"                  : [-1.0,    1.0     ],
                                                      "Name"                   : "TagDecSS",
                                                      "InputName"              : "obsTagSSPionBDT"} 

    configdict["BasicVariables"]["MistagOS"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                      "Name"                   : "MistagOS",
                                                      "InputName"              : "obsEtaOS"}

    configdict["BasicVariables"]["MistagSS"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                      "Name"                   : "MistagSS",
                                                      "InputName"              : "obsEtaSSPionBDT"}

    # tagging calibration
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"]    = {"p0"   : 0.365517, "p1"   : 0.950216, "average"   : 0.371147,
                                                 "p0Bar": 0.376730, "p1Bar": 1.048155, "averageBar": 0.371147}
    configdict["TaggingCalibration"]["SS"]    = {"p0"   : 0.424801, "p1"   : 1.004340, "average"   : 0.414892,
                                                 "p0Bar": 0.404896, "p1Bar": 0.995879, "averageBar": 0.414892}
    configdict["TaggingCalibration"]["OS+SS"] = {"p0"   : 0.338781, "p1"   : 0.971845, "average"   : 0.338493,
                                                 "p0Bar": 0.338363, "p1Bar": 1.027861, "averageBar": 0.338493}
    
    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts   
    # order of particles: KPiPi 
    configdict["DsChildrenPrefix"] = {"Child1":"lab3","Child2":"lab4","Child3": "lab5"}
    
    configdict["constParams"] = []

    #Useful constants
    Pipeak = 5.28017e+03
    Kpeak = 5.28032e+03

    #Global variables (shared by different PDFs)
    configdict["GlobalVariables"] = {}
    configdict["GlobalVariables"]["eff_Bd2DPi_DPi"] = {}
    configdict["GlobalVariables"]["eff_Bd2DPi_DPi"] = {"Type": "RooRealVar",
                                                       "Title": "#epsilon^{D#pi}_{B_{d}#rightarrowD#pi}",
                                                       "Range": [0.978938233282, 0.8, 1.0],
                                                       "Error": 0.00402065203252
                                                       }
    configdict["GlobalVariables"]["eff_Bd2DK_DK"] = {}
    configdict["GlobalVariables"]["eff_Bd2DK_DK"] = {"Type": "RooRealVar",
                                                     "Title": "#epsilon^{DK}_{B_{d}#rightarrowDK}",
                                                     "Range": [0.63627057571, 0.5, 0.8],
                                                     "Error": 0.00652916835125
                                                     }
    configdict["GlobalVariables"]["Signal_BeautyMass_mean_both_kpipi_run1_Bd2DPiHypo"] = {}
    configdict["GlobalVariables"]["Signal_BeautyMass_mean_both_kpipi_run1_Bd2DPiHypo"] = {"Type": "RooRealVar",
                                                                                          "Title": "B mass mean (#pi sample)",
                                                                                          "Range": [Pipeak, 5.2e+03, 5.35e+03]
                                                                                   }
    configdict["GlobalVariables"]["Signal_BeautyMass_mean_both_kpipi_run1_Bd2DKHypo"] = {}
    configdict["GlobalVariables"]["Signal_BeautyMass_mean_both_kpipi_run1_Bd2DKHypo"] = {"Type": "RooRealVar",
                                                                                         "Title": "B mass mean (K sample)",
                                                                                         "Range": [Kpeak, 5.2e+03, 5.35e+03]
                                                                                         }
    configdict["GlobalVariables"]["nSig_both_kpipi_run1_Bd2DPiHypo_Evts"] = {"Type": "RooRealVar",
                                                                             "Title": "nSig_both_kpipi_run1_Bd2DPiHypo_Evts",
                                                                             "Range": [5.7022e+05,300000,600000]
                                                                             }
    configdict["GlobalVariables"]["nSig_both_kpipi_run1_Bd2DKHypo_Evts"] = {"Type": "RooFormulaVar",
                                                                            "Title": "nSig_both_kpipi_run1_Bd2DKHypo_Evts",
                                                                            "Formula": "((1-@0)/@0)*@1",
                                                                            "Dependents": ["eff_Bd2DPi_DPi", "nSig_both_kpipi_run1_Bd2DPiHypo_Evts"]
                                                                            }
    configdict["GlobalVariables"]["nBd2DK_both_kpipi_run1_Bd2DKHypo_Evts"] = {"Type": "RooRealVar",
                                                                              "Title": "nBd2DK_both_kpipi_run1_Bd2DKHypo_Evts",
                                                                              "Range": [45000,10000,100000]
                                                                              }
    configdict["GlobalVariables"]["nBd2DK_both_kpipi_run1_Bd2DPiHypo_Evts"] = {"Type": "RooFormulaVar",
                                                                               "Title": "nBd2DK_both_kpipi_run1_Bd2DPiHypo_Evts",
                                                                               "Formula": "((1-@0)/@0)*@1",
                                                                               "Dependents": ["eff_Bd2DK_DK", "nBd2DK_both_kpipi_run1_Bd2DKHypo_Evts"]
                                                                               }
    
    #PDF for each fitted component
    #Structure: decay->hypo->observable
    configdict["pdfList"] = {}
    #
    configdict["pdfList"]["Total"] = {}
    configdict["pdfList"]["Total"]["Title"] = "Total"
    configdict["pdfList"]["Total"]["Color"] = kBlue
    configdict["pdfList"]["Total"]["Style"] = kSolid
    #
    configdict["pdfList"]["Signal"] = {}
    configdict["pdfList"]["Signal"]["Title"] = "B_{d}#rightarrowD#pi"
    configdict["pdfList"]["Signal"]["Color"] = kRed
    configdict["pdfList"]["Signal"]["Style"] = kDashed
    configdict["pdfList"]["Signal"]["Bd2DPi"] = {}
    configdict["pdfList"]["Signal"]["Bd2DPi"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                                "shiftMean"  : False,
                                                                "mean"       : "Signal_BeautyMass_mean_both_kpipi_run1_Bd2DPiHypo",
                                                                "sigma"      : [2.02063e+01, 1.5e+01, 3.5e+01],
                                                                "zeta"       : [0.0],
                                                                "fb"         : [0.0],
                                                                "l"          : [-3.20961e+00],
                                                                "a1"         : [1.42911e+00, 3.0e-01, 5.0e+00], #left
                                                                "a2"         : [1.86674e+00, 3.0e-01, 5.0e+00], #right
                                                                "n1"         : [2.74488e+00, 1e+00, 5.0e+00], #left
                                                                "n2"         : [3.18373e+00, 1e+00, 5.0e+00]} #right
    
    configdict["pdfList"]["Signal"]["Bd2DK"] = {}
    configdict["pdfList"]["Signal"]["Bd2DK"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                               "shiftMean"  : True,
                                                               "mean"       : "Signal_BeautyMass_mean_both_kpipi_run1_Bd2DKHypo",
                                                               "shift"      : [5.32715e+03-Kpeak],
                                                               "sigma"      : [2.33716e+01],
                                                               "zeta"       : [0.0],
                                                               "fb"         : [0.0],
                                                               "l"          : [-9.07419e+00],
                                                               "a1"         : [2.70454e+00],
                                                               "a2"         : [7.03565e-01],
                                                               "n1"         : [3.66284e-01],
                                                               "n2"         : [2.08885e+00]}
    #
    configdict["pdfList"]["Bd2DK"] = {}
    configdict["pdfList"]["Bd2DK"]["Title"] = "B_{d}#rightarrowDK"
    configdict["pdfList"]["Bd2DK"]["Color"] = kBlack
    configdict["pdfList"]["Bd2DK"]["Style"] = kDotted
    configdict["pdfList"]["Bd2DK"]["Bd2DPi"] = {}
    configdict["pdfList"]["Bd2DK"]["Bd2DPi"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                               "shiftMean"  : True,
                                                               "mean"       : "Signal_BeautyMass_mean_both_kpipi_run1_Bd2DPiHypo",
                                                               "shift"      : [5.23927e+03-Pipeak],
                                                               "sigma"      : [3.32098e+01],
                                                               "zeta"       : [0.0],
                                                               "fb"         : [0.0],
                                                               "l"          : [-2.26752e+00],
                                                               "a1"         : [7.24481e-01],
                                                               "a2"         : [1.48520e+00],
                                                               "n1"         : [3.78680e+00],
                                                               "n2"         : [5.52277e+00]}
    configdict["pdfList"]["Bd2DK"]["Bd2DK"] = {}
    configdict["pdfList"]["Bd2DK"]["Bd2DK"]["BeautyMass"] = {"PDF"        : "Ipatia",
                                                             "shiftMean"  : False,
                                                             "mean"       : "Signal_BeautyMass_mean_both_kpipi_run1_Bd2DKHypo",
                                                             "sigma"      : [1.71444e+01],
                                                             "zeta"       : [0.0],
                                                             "fb"         : [0.0],
                                                             "l"          : [-3.61169e+00],
                                                             "a1"         : [2.66570e+00],
                                                             "a2"         : [1.0e+09],
                                                             "n1"         : [9.62144e-01],
                                                             "n2"         : [0.0]}
    #
    configdict["pdfList"]["Bd2DRho"] = {}
    configdict["pdfList"]["Bd2DRho"]["Title"] = "B_{d}#rightarrowD#rho"
    configdict["pdfList"]["Bd2DRho"]["Color"] = kMagenta
    configdict["pdfList"]["Bd2DRho"]["Style"] = kDotted
    configdict["pdfList"]["Bd2DRho"]["Bd2DPi"] = {}
    configdict["pdfList"]["Bd2DRho"]["Bd2DPi"]["BeautyMass"] = {"PDF"        : "JohnsonSU",
                                                                "shiftMean" : True,
                                                                "mean"      : "Signal_BeautyMass_mean_both_kpipi_run1_Bd2DPiHypo",
                                                                "shift"     : [4.65054e+03-Pipeak],
                                                                "sigma"     : [1.09666e+03],
                                                                "nu"        : [-2.04803e+00],
                                                                "tau"       : [1.32664e+00]}
    configdict["pdfList"]["Bd2DRho"]["Bd2DK"] = {}
    configdict["pdfList"]["Bd2DRho"]["Bd2DK"]["BeautyMass"] = {"PDF"        : "DoubleGaussian",
                                                               "shiftMean"  : True,
                                                               "sameMean"   : True,
                                                               "mean"       : "Signal_BeautyMass_mean_both_kpipi_run1_Bd2DKHypo",
                                                               "shift"      : [5.13673e+03-Kpeak],
                                                               "sigma1"     : [1.15527e+02],
                                                               "sigma2"     : [4.64867e+01],
                                                               "frac"       : [7.11930e-01]}
    #
    configdict["pdfList"]["Bd2DstPi"] = {}
    configdict["pdfList"]["Bd2DstPi"]["Title"] = "B_{d}#rightarrowD^{*}#pi"
    configdict["pdfList"]["Bd2DstPi"]["Color"] = kGreen
    configdict["pdfList"]["Bd2DstPi"]["Style"] = kDotted
    configdict["pdfList"]["Bd2DstPi"]["Bd2DPi"] = {}
    configdict["pdfList"]["Bd2DstPi"]["Bd2DPi"]["BeautyMass"] = {"PDF"         : "CrystalBallPlusGaussian",
                                                                 "shiftMean"   : True,
                                                                 "mean"        : "Signal_BeautyMass_mean_both_kpipi_run1_Bd2DPiHypo",
                                                                 "shift"       : [5100.29-Pipeak],
                                                                 "alpha"       : [-1.60828e+00],
                                                                 "n"           : [4.64802e+00],
                                                                 "sigmaCB"     : [4.06680e+01],
                                                                 "sigmaG"      : [1.79610e+01],
                                                                 "fracG"       : [1.33011e-01]}
    configdict["pdfList"]["Bd2DstPi"]["Bd2DK"] = {}
    configdict["pdfList"]["Bd2DstPi"]["Bd2DK"]["BeautyMass"] = {"PDF"        : "None"}
    #
    configdict["pdfList"]["Bs2DsPi"] = {}
    configdict["pdfList"]["Bs2DsPi"]["Title"] = "B_{s}#rightarrowD_{s}#pi"
    configdict["pdfList"]["Bs2DsPi"]["Color"] = kCyan
    configdict["pdfList"]["Bs2DsPi"]["Style"] = kDotted
    configdict["pdfList"]["Bs2DsPi"]["Bd2DPi"] = {}
    configdict["pdfList"]["Bs2DsPi"]["Bd2DPi"]["BeautyMass"] = {"PDF"        : "None"}
    configdict["pdfList"]["Bs2DsPi"]["Bd2DK"] = {}
    configdict["pdfList"]["Bs2DsPi"]["Bd2DK"]["BeautyMass"] = {"PDF"        : "None"}
    #
    configdict["pdfList"]["Bd2DKst"] = {}
    configdict["pdfList"]["Bd2DKst"]["Title"] = "B_{d}#rightarrowDK^{*}"
    configdict["pdfList"]["Bd2DKst"]["Color"] = kPink
    configdict["pdfList"]["Bd2DKst"]["Style"] = kDotted
    configdict["pdfList"]["Bd2DKst"]["Bd2DPi"] = {}
    configdict["pdfList"]["Bd2DKst"]["Bd2DPi"]["BeautyMass"] = {"PDF"       : "None"} 
    configdict["pdfList"]["Bd2DKst"]["Bd2DK"] = {}
    configdict["pdfList"]["Bd2DKst"]["Bd2DK"]["BeautyMass"] = {"PDF"        : "Gaussian",
                                                               "shiftMean"  : False,
                                                               "mean"       : [5.11176e+03, 4.9e+03, 5.2e+03],
                                                               "sigma"      : [2.43101e+01]}
    #
    configdict["pdfList"]["Comb"] = {}
    configdict["pdfList"]["Comb"]["Title"] = "Combinatorial"
    configdict["pdfList"]["Comb"]["Color"] = kBlue
    configdict["pdfList"]["Comb"]["Style"] = kDotted
    configdict["pdfList"]["Comb"]["Bd2DPi"] = {}
    configdict["pdfList"]["Comb"]["Bd2DPi"]["BeautyMass"] = { "PDF"          : "Exponential",
                                                              "Title"        : "Combinatorial",
                                                              "cB"           : [-2.27055e-03, -5.0e-03, -1.0e-03]}
    configdict["pdfList"]["Comb"]["Bd2DK"] = {}
    configdict["pdfList"]["Comb"]["Bd2DK"]["BeautyMass"] = { "PDF"          : "Exponential",
                                                             "Title"        : "Combinatorial",
                                                             "cB"           : [-5.08454e-03, -8.0e-03, -2.0e-03]}

    #Axes titles
    configdict["AxisTitle"] = {"BeautyMass": {"Bd2DPi":"D#pi mass (MeV/c^{2})",
                                              "Bd2DK":"DK mass (MeV/c^{2})"}}

    #Range
    configdict["Range"] = {"BeautyMass": {"Range": [configdict["BasicVariables"]["BeautyMass"]["Range"][0],
                                                    configdict["BasicVariables"]["BeautyMass"]["Range"][1]],
                                          "Bins": 455}}

    #Range and sample for sWeights
    configdict["sWeights"] = {"Hypo" : "Bd2DPi",
                              "Range" : {"BeautyMass" : [5180.0, 5600.0] }
                              }

    #Log scale
    configdict["LogScale"] = {"BeautyMass": {"Bd2DPi" : [1e-03, 1e+05], "Bd2DK" : [1e-01, 1e+04] } }

    #Some coordinates
    configdict["Legend"] = {"Xmin" : 0.6,
                            "Ymin" : 0.2,
                            "Xmax" : 0.89,
                            "Ymax" : 0.6}
    configdict["LHCbText"] = {"X"    : 0.89,
                              "Y"    : 0.8,
                              "Text" : "LHCb Preliminary"}
    configdict["Chi2"] = {"X"    : 0.6,
                          "Y"    : 0.7}

    #Yields
    configdict["Yields"] = {"Signal"   : {"Bd2DPi"  : "nSig_both_kpipi_run1_Bd2DPiHypo_Evts", "Bd2DK": "nSig_both_kpipi_run1_Bd2DKHypo_Evts"},
                            "Bd2DK"    : {"Bd2DPi"  : "nBd2DK_both_kpipi_run1_Bd2DPiHypo_Evts", "Bd2DK": "nBd2DK_both_kpipi_run1_Bd2DKHypo_Evts"},
                            "Bd2DRho"  : {"Bd2DPi"  : [9.1417e+04,0,500000], "Bd2DK": [10000,0,100000]},
                            "Bd2DstPi" : {"Bd2DPi"  : [6.2575e+04,0,500000], "Bd2DK": [0]},
                            "Bs2DsPi"  : {"Bd2DPi"  : [0], "Bd2DK": [0]},
                            "Bd2DKst"  : {"Bd2DPi"  : [0], "Bd2DK": [5000,0,100000]},
                            "Comb"     : {"Bd2DPi"  : [4.2389e+04,0,500000], "Bd2DK": [1500,0,100000]}}

    #Gaussian constraints
    configdict["GaussianConstraints"] = {}
    configdict["GaussianConstraints"]["Eff_Bd2DPi_DPi"] = {"Parameters" : ["eff_Bd2DPi_DPi"],
                                                           "Mean"       : [configdict["GlobalVariables"]["eff_Bd2DPi_DPi"]["Range"][0]],
                                                           "Covariance" : [configdict["GlobalVariables"]["eff_Bd2DPi_DPi"]["Error"]]}
    configdict["GaussianConstraints"]["Eff_Bd2DK_DK"] = {"Parameters" : ["eff_Bd2DK_DK"],
                                                         "Mean"       : [configdict["GlobalVariables"]["eff_Bd2DK_DK"]["Range"][0]],
                                                         "Covariance" : [configdict["GlobalVariables"]["eff_Bd2DK_DK"]["Error"]]}
    
    return configdict
