from ROOT import *

def getconfig( samplemodeyear ) :

    configdict = {}

    from math import pi
    from math import log

    import ROOT

    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5090,    6000    ],
                                                      "Name"                   : "BeautyMass",
                                                      "InputName"              : "lab0_FitDaughtersConst_M_flat"}

    #configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1910    ],
    #                                                  "Name"                   : "CharmMass",
    #                                                  "InputName"              : "lab0_FitwithoutConst_Dplus_M_flat"}

    # configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.2,     15.0    ],
    #                                                   "Bins"                   : 40,
    #                                                   "Name"                   : "BeautyTime",
    #                                                   "InputName"              : "lab0_FitDaughtersPVConst_ctau_flat"}

    #configdict["BasicVariables"]["BacP"]          = { "Range"                  : [2000.0,  650000.0],
    #                                                  "Name"                   : "BacP",
    #                                                  "InputName"              : "lab0_FitDaughtersConst_P0_P_flat"}

    #configdict["BasicVariables"]["BacPT"]         = { "Range"                  : [400.0,   45000.0 ],
    #                                                  "Name"                   : "BacPT",
    #                                                  "InputName"              : "lab0_FitDaughtersConst_P0_PT_flat"}

    #configdict["BasicVariables"]["BacPIDK"]       = { "Range"                  : [-999.0, 999.0     ],
    #                                                  "Name"                   : "BacPIDK",
    #                                                  "InputName"              : "lab1_PIDK"}

    #configdict["BasicVariables"]["nTracks"]       = { "Range"                  : [15.0,    1000.0  ],
    #                                                  "Name"                   : "nTracks",
    #                                                  "InputName"              : "nTracks"}

    #configdict["BasicVariables"]["BeautyTimeErr"] = { "Range"                  : [0.01,    0.1     ],
    #                                                  "Name"                   : "BeautyTimeErr",
    #                                                  "InputName"              : "lab0_FitDaughtersPVConst_ctauErr_flat"}

    # configdict["BasicVariables"]["BacCharge"]     = { "Range"                  : [-1000.0, 1000.0  ],
    #                                                   "Name"                   : "BacCharge",
    #                                                   "InputName"              : "lab1_ID"}

    # configdict["BasicVariables"]["TagDecOS"]      = { "Range"                  : [-1.0,    1.0     ],
    #                                                   "Name"                   : "TagDecOS",
    #                                                   "InputName"              : "obsTagOS"}

    # configdict["BasicVariables"]["TagDecSS"]      = { "Range"                  : [-1.0,    1.0     ],
    #                                                   "Name"                   : "TagDecSS",
    #                                                   "InputName"              : "obsTagSSPionBDT"}

    # configdict["BasicVariables"]["MistagOS"]      = { "Range"                  : [ 0.0,    0.5     ],
    #                                                   "Name"                   : "MistagOS",
    #                                                   "InputName"              : "obsEtaOS"}

    # configdict["BasicVariables"]["MistagSS"]      = { "Range"                  : [ 0.0,    0.5     ],
    #                                                   "Name"                   : "MistagSS",
    #                                                   "InputName"              : "obsEtaSSPionBDT"}

    configdict["AdditionalVariables"] = {}
    # configdict["AdditionalVariables"]["TrueID"]   = { "Range"                  : [0.0, 1500.0],
    #                                                   "InputName"              : "TrueID" }


    configdict["constParams"] = []

    #Useful constants
    Pipeak = 5.27849e+03
    Kpeak = 5.27907e+03

    #Global variables (shared by different PDFs)
    configdict["GlobalVariables"] = {}
    configdict["GlobalVariables"]["eff_Bd2DPi_DPi"] = {}
    configdict["GlobalVariables"]["eff_Bd2DPi_DPi"] = {"Type": "RooRealVar",
                                                       "Title": "#epsilon^{D#pi}_{B_{d}#rightarrowD#pi}",
                                                       "Range": [9.78927e-01, 0.8, 1.0],
                                                       "Error": 0.0040223022512
                                                       }
    configdict["GlobalVariables"]["eff_Bd2DK_DK"] = {}
    configdict["GlobalVariables"]["eff_Bd2DK_DK"] = {"Type": "RooRealVar",
                                                     "Title": "#epsilon^{DK}_{B_{d}#rightarrowDK}",
                                                     "Range": [6.29009e-01, 0.5, 0.8],
                                                     "Error": 0.00653026432682
                                                     }
    configdict["GlobalVariables"]["Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DPiHypo"] = {}
    configdict["GlobalVariables"]["Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DPiHypo"] = {"Type": "RooRealVar",
                                                                                             "Title": "B mass mean (#pi sample)",
                                                                                             "Range": [Pipeak, 5.2e+03, 5.35e+03]
                                                                                             }
    configdict["GlobalVariables"]["Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DKHypo"] = {}
    configdict["GlobalVariables"]["Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DKHypo"] = {"Type": "RooRealVar",
                                                                                            "Title": "B mass mean (K sample)",
                                                                                            "Range": [Kpeak, 5.2e+03, 5.35e+03]
                                                                                            }
    configdict["GlobalVariables"]["nSig_"+samplemodeyear+"_Bd2DPiHypo_Evts"] = {"Type": "RooRealVar",
                                                                                "Title": "nSig_"+samplemodeyear+"_Bd2DPiHypo_Evts",
                                                                                "Range": [5.49162e+05,300000,600000]
                                                                                }
    configdict["GlobalVariables"]["nSig_"+samplemodeyear+"_Bd2DKHypo_Evts"] = {"Type": "RooFormulaVar",
                                                                               "Title": "nSig_"+samplemodeyear+"_Bd2DKHypo_Evts",
                                                                               "Formula": "((1-@0)/@0)*@1",
                                                                               "Dependents": ["eff_Bd2DPi_DPi", "nSig_"+samplemodeyear+"_Bd2DPiHypo_Evts"]
                                                                               }
    configdict["GlobalVariables"]["nBd2DK_"+samplemodeyear+"_Bd2DKHypo_Evts"] = {"Type": "RooRealVar",
                                                                                 "Title": "nBd2DK_"+samplemodeyear+"_Bd2DKHypo_Evts",
                                                                                 "Range": [3.23144e+04,20000,50000]
                                                                                 }
    configdict["GlobalVariables"]["nBd2DK_"+samplemodeyear+"_Bd2DPiHypo_Evts"] = {"Type": "RooFormulaVar",
                                                                                  "Title": "nBd2DK_"+samplemodeyear+"_Evts",
                                                                                  "Formula": "((1-@0)/@0)*@1",
                                                                                  "Dependents": ["eff_Bd2DK_DK", "nBd2DK_"+samplemodeyear+"_Bd2DKHypo_Evts"]
                                                                                  }
    configdict["GlobalVariables"]["nBd2DKst_"+samplemodeyear+"_Bd2DKHypo_Evts"] = {"Type": "RooRealVar",
                                                                                   "Title": "nBd2DKst_"+samplemodeyear+"_Bd2DKHypo_Evts",
                                                                                   "Range": [6.06144e+03, 100, 10000],
                                                                                   }
    configdict["GlobalVariables"]["DRho_to_DKst_KHypo"] = {"Type": "RooRealVar",
                                                           "Title": "DRho_to_DKst_KHypo",
                                                           "Range": [1.15744e-01],#0.05,0.4],
                                                           "Error": 0.04
                                                           }
    configdict["GlobalVariables"]["nBd2DRho_"+samplemodeyear+"_Bd2DKHypo_Evts"] = {"Type": "RooFormulaVar",
                                                                                   "Title": "nBd2DRho_"+samplemodeyear+"_Bd2DKHypo_Evts",
                                                                                   "Formula": "@0*@1",
                                                                                   "Dependents": ["nBd2DKst_"+samplemodeyear+"_Bd2DKHypo_Evts","DRho_to_DKst_KHypo"]
                                                                                   }

    configdict["GlobalVariables"]["Signal_Ipatia_BeautyMass_a1_"+samplemodeyear+"_Bd2DPiHypo"] = {"Type": "RooRealVar",
                                                                                                  "Title": "Signal_Ipatia_BeautyMass_a1_"+samplemodeyear+"_Bd2DPiHypo",
                                                                                                  "Range": [1.56363e+00],
                                                                                                  }
    configdict["GlobalVariables"]["Signal_Ipatia_BeautyMass_a2_"+samplemodeyear+"_Bd2DPiHypo"] = {"Type": "RooRealVar",
                                                                                                  "Title": "Signal_Ipatia_BeautyMass_a2_"+samplemodeyear+"_Bd2DPiHypo",
                                                                                                  "Range": [1.77887e+00],
                                                                                                  }
    configdict["GlobalVariables"]["Signal_Ipatia_BeautyMass_n1_"+samplemodeyear+"_Bd2DPiHypo"] = {"Type": "RooRealVar",
                                                                                                  "Title": "Signal_Ipatia_BeautyMass_n1_"+samplemodeyear+"_Bd2DPiHypo",
                                                                                                  "Range": [4.04491e+00],
                                                                                                  }
    configdict["GlobalVariables"]["Signal_Ipatia_BeautyMass_n2_"+samplemodeyear+"_Bd2DPiHypo"] = {"Type": "RooRealVar",
                                                                                                  "Title": "Signal_Ipatia_BeautyMass_n2_"+samplemodeyear+"_Bd2DPiHypo",
                                                                                                  "Range": [6.62043e+00],
                                                                                                  }
    configdict["GlobalVariables"]["Signal_Ipatia_BeautyMass_ascale_"+samplemodeyear+"_Bd2DPiHypo"] = {"Type": "RooRealVar",
                                                                                                      "Title": "Signal_Ipatia_BeautyMass_ascale_"+samplemodeyear+"_Bd2DPiHypo",
                                                                                                      "Range": [1.0, 0.1, 1.9],
                                                                                                      }
    configdict["GlobalVariables"]["Signal_Ipatia_BeautyMass_nscale_"+samplemodeyear+"_Bd2DPiHypo"] = {"Type": "RooRealVar",
                                                                                                      "Title": "Signal_Ipatia_BeautyMass_nscale_"+samplemodeyear+"_Bd2DPiHypo",
                                                                                                      "Range": [1.0, 0.1, 1.9],
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
                                                                "scaleTails" : True,
                                                                "mean"       : "Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DPiHypo",
                                                                "sigma"      : [1.96756e+01, 1.5e+01, 3.5e+01],
                                                                "zeta"       : [0.0],
                                                                "fb"         : [0.0],
                                                                "l"          : [-3.14504e+00],
                                                                "a1"         : "Signal_Ipatia_BeautyMass_a1_"+samplemodeyear+"_Bd2DPiHypo", #left
                                                                "a2"         : "Signal_Ipatia_BeautyMass_a2_"+samplemodeyear+"_Bd2DPiHypo", #right
                                                                "n1"         : "Signal_Ipatia_BeautyMass_n1_"+samplemodeyear+"_Bd2DPiHypo", #left
                                                                "n2"         : "Signal_Ipatia_BeautyMass_a1_"+samplemodeyear+"_Bd2DPiHypo"}#right

    configdict["pdfList"]["Signal"]["Bd2DK"] = {}
    configdict["pdfList"]["Signal"]["Bd2DK"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                               "shiftMean"  : False,#True,
                                                               "scaleTails" : False,
                                                               "mean"       : [5.32740e+03,5.25e+03,5.45e+03],#"Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DKHypo",
                                                               #"shift"      : [5.32740e+03-Kpeak],
                                                               "sigma"      : [2.42675e+01],
                                                               "zeta"       : [0.0],
                                                               "fb"         : [0.0],
                                                               "l"          : [-5.46421e+00],
                                                               "a1"         : [3.04325e+00],
                                                               "a2"         : [6.62837e-01],
                                                               "n1"         : [6.79609e-02],
                                                               "n2"         : [2.09572e+00]}

    configdict["pdfList"]["Bd2DK"] = {}
    configdict["pdfList"]["Bd2DK"]["Title"] = "B_{d}#rightarrowDK"
    configdict["pdfList"]["Bd2DK"]["Color"] = kBlack
    configdict["pdfList"]["Bd2DK"]["Style"] = kDotted
    configdict["pdfList"]["Bd2DK"]["Bd2DPi"] = {}
    configdict["pdfList"]["Bd2DK"]["Bd2DPi"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                               "shiftMean"  : False,#True,
                                                               "scaleTails" : False,
                                                               "mean"       : [5.23938e+03,5.15e+03,5.35e+03],#"Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DPiHypo",
                                                               #"shift"      : [5.23938e+03-Pipeak],
                                                               "sigma"      : [2.59213e+01],
                                                               "zeta"       : [0.0],
                                                               "fb"         : [0.0],
                                                               "l"          : [-3.98519e+01],
                                                               "a1"         : [9.68988e-01],
                                                               "a2"         : [1.23156e+00],
                                                               "n1"         : [3.49691e+00],
                                                               "n2"         : [1.00524e+01]}
    configdict["pdfList"]["Bd2DK"]["Bd2DK"] = {}
    configdict["pdfList"]["Bd2DK"]["Bd2DK"]["BeautyMass"] = {"PDF"        : "Ipatia",
                                                             "shiftMean"  : False,
                                                             "scaleTails" : False,
                                                             "mean"       : "Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DKHypo",
                                                             "sigma"      : [1.74271e+01, 1.5e+01, 1.9e+01],
                                                             "zeta"       : [0.0],
                                                             "fb"         : [0.0],
                                                             "l"          : [-3.22645e+00],
                                                             "a1"         : [2.60724e+00],
                                                             "a2"         : [1.0e+09],
                                                             "n1"         : [1.00877e+00],
                                                             "n2"         : [0.0]}

    configdict["pdfList"]["Bd2DRho"] = {}
    configdict["pdfList"]["Bd2DRho"]["Title"] = "B_{d}#rightarrowD#rho"
    configdict["pdfList"]["Bd2DRho"]["Color"] = kMagenta
    configdict["pdfList"]["Bd2DRho"]["Style"] = kDotted
    configdict["pdfList"]["Bd2DRho"]["Bd2DPi"] = {}
    configdict["pdfList"]["Bd2DRho"]["Bd2DPi"]["BeautyMass"] = {"PDF"        : "JohnsonSU",
                                                                "shiftMean" : True,
                                                                "mean"      : "Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DPiHypo",
                                                                "shift"     : [4.71618e+03-Pipeak],
                                                                "sigma"     : [9.01304e+02],
                                                                "nu"        : [-2.01671e+00],
                                                                "tau"       : [1.29155e+00]}
    configdict["pdfList"]["Bd2DRho"]["Bd2DK"] = {}
    configdict["pdfList"]["Bd2DRho"]["Bd2DK"]["BeautyMass"] = {"PDF"        : "DoubleGaussian",
                                                               "shiftMean"  : True,
                                                               "sameMean"   : True,
                                                               "mean"       : "Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DKHypo",
                                                               "shift"      : [5.14019e+03-Kpeak],
                                                               "sigma1"     : [9.00002e+01],
                                                               "sigma2"     : [1.55484e+02],
                                                               "frac"       : [8.30742e-01]}
    #
    configdict["pdfList"]["Bd2DstPi"] = {}
    configdict["pdfList"]["Bd2DstPi"]["Title"] = "B_{d}#rightarrowD^{*}#pi"
    configdict["pdfList"]["Bd2DstPi"]["Color"] = kGreen
    configdict["pdfList"]["Bd2DstPi"]["Style"] = kDotted
    configdict["pdfList"]["Bd2DstPi"]["Bd2DPi"] = {}
    configdict["pdfList"]["Bd2DstPi"]["Bd2DPi"]["BeautyMass"] = {"PDF"         : "CrystalBallPlusGaussian",
                                                                 "shiftMean"   : True,
                                                                 "mean"        : "Signal_BeautyMass_mean_"+samplemodeyear+"_Bd2DPiHypo",
                                                                 "shift"       : [5.10033e+03-Pipeak],
                                                                 "alpha"       : [-1.63404e+00],
                                                                 "n"           : [4.65946e+00],
                                                                 "sigmaCB"     : [4.15131e+01],
                                                                 "sigmaG"      : [1.79617e+01],
                                                                 "fracG"       : [1.32304e-01]}
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
                                                               "mean"       : [5.08528e+03, 4.9e+03, 5.2e+03],
                                                               "sigma"      : [3.76140e+01, 1e+01, 6e+01]}
    #
    configdict["pdfList"]["Comb"] = {}
    configdict["pdfList"]["Comb"]["Title"] = "Combinatorial"
    configdict["pdfList"]["Comb"]["Color"] = kBlue
    configdict["pdfList"]["Comb"]["Style"] = kDotted
    configdict["pdfList"]["Comb"]["Bd2DPi"] = {}
    #configdict["pdfList"]["Comb"]["Bd2DPi"]["BeautyMass"] = { "PDF"          : "Exponential",
    #                                                          "Title"        : "Combinatorial",
    #                                                          "cB"           : [-2.27055e-03, -5.0e-03, -1.0e-03]}
    configdict["pdfList"]["Comb"]["Bd2DPi"]["BeautyMass"] = { "PDF"          : "ExponentialPlusConstant",
                                                              "Title"        : "Combinatorial",
                                                              "cB"           : [-5.59102e-03, -15.0e-03, -1.0e-03],
                                                              "fracExpo"     : [8.77658e-01,0.3,0.99]}
    configdict["pdfList"]["Comb"]["Bd2DK"] = {}
    configdict["pdfList"]["Comb"]["Bd2DK"]["BeautyMass"] = { "PDF"          : "ExponentialPlusConstant",
                                                             "Title"        : "Combinatorial",
                                                             "cB"           : [-4.15525e-03, -8.0e-03, -2.0e-03],
                                                             "fracExpo"     : [9.38575e-01,0.3,0.99]}

    #Axes titles
    configdict["AxisTitle"] = {"BeautyMass": {"Bd2DPi":"D#pi mass (MeV/c^{2})",
                                              "Bd2DK":"DK mass (MeV/c^{2})"}}

    #Range
    configdict["Range"] = {"BeautyMass": {"Range": [configdict["BasicVariables"]["BeautyMass"]["Range"][0],
                                                    configdict["BasicVariables"]["BeautyMass"]["Range"][1]],
                                          "Bins": 300}}#455}}

    #Range and sample for sWeights
    configdict["sWeights"] = {"Hypo" : "Bd2DPi",
                              "Range" : {"BeautyMass" : [5220.0, 5600.0]},
                              "Bins": 380
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
                              "Text" : "LHCb Fast Simulation"}
    configdict["Chi2"] = {"X"    : 0.6,
                          "Y"    : 0.7}

    #Yields
    configdict["Yields"] = {"Signal"   : {"Bd2DPi"  : "nSig_"+samplemodeyear+"_Bd2DPiHypo_Evts", "Bd2DK": "nSig_"+samplemodeyear+"_Bd2DKHypo_Evts"},
                            "Bd2DK"    : {"Bd2DPi"  : "nBd2DK_"+samplemodeyear+"_Bd2DPiHypo_Evts", "Bd2DK": "nBd2DK_"+samplemodeyear+"_Bd2DKHypo_Evts"},
                            "Bd2DRho"  : {"Bd2DPi"  : [7.40343e+04,0,500000], "Bd2DK": "nBd2DRho_"+samplemodeyear+"_Bd2DKHypo_Evts"},
                            "Bd2DstPi" : {"Bd2DPi"  : [6.80954e+04,0,500000], "Bd2DK": [0]},
                            "Bs2DsPi"  : {"Bd2DPi"  : [0], "Bd2DK": [0]},
                            "Bd2DKst"  : {"Bd2DPi"  : [0], "Bd2DK": "nBd2DKst_"+samplemodeyear+"_Bd2DKHypo_Evts"},
                            "Comb"     : {"Bd2DPi"  : [8.23965e+04,5000,500000], "Bd2DK": [2.40497e+04,500,100000]}}

    #Gaussian constraints
    configdict["GaussianConstraints"] = {}
    configdict["GaussianConstraints"]["Eff_Bd2DPi_DPi"] = {"Parameters" : ["eff_Bd2DPi_DPi"],
                                                           "Mean"       : [configdict["GlobalVariables"]["eff_Bd2DPi_DPi"]["Range"][0]],
                                                           "Covariance" : [configdict["GlobalVariables"]["eff_Bd2DPi_DPi"]["Error"]]}
    configdict["GaussianConstraints"]["Eff_Bd2DK_DK"] = {"Parameters" : ["eff_Bd2DK_DK"],
                                                         "Mean"       : [configdict["GlobalVariables"]["eff_Bd2DK_DK"]["Range"][0]],
                                                         "Covariance" : [configdict["GlobalVariables"]["eff_Bd2DK_DK"]["Error"]]}
    #configdict["GaussianConstraints"]["nDRho_to_DKst_KHypo"] = {"Parameters" : ["DRho_to_DKst_KHypo"],
    #                                                            "Mean"       : [configdict["GlobalVariables"]["DRho_to_DKst_KHypo"]["Range"][0]],
    #                                                            "Covariance" : [configdict["GlobalVariables"]["DRho_to_DKst_KHypo"]["Error"]]}

    #Plot of the fit to compute sWeights
    configdict["sWeightsFitPlot"] = {}
    configdict["sWeightsFitPlot"]["Total"] = {"Color" : kBlue,
                                              "Style" : kSolid,
                                              "Title" : "Total"}
    configdict["sWeightsFitPlot"]["Signal"] = {"Color" : kRed,
                                               "Style" : kDashed,
                                               "Title" : "Signal"}
    configdict["sWeightsFitPlot"]["Background"] = {"Color" : kBlack,
                                                   "Style" : kDotted,
                                                   "Title" : "Background"}

    #sWeight plot
    configdict["plotsWeights"] = {"BeautyTime" : "#tau(B_{d}#rightarrow D#pi) (ps)",
                                  "CharmMass"  : "K#pi#pi mass (MeV/c^{2})"
                                  }

    #"Code" to identify the True ID for each component
    configdict["TrueID"] = {"Signal"          : 100,
                            "Bd2DK"           : 200,
                            "Bd2DRho"         : 300,
                            "Bd2DstPi"        : 400,
                            "Bd2DKst"         : 500,
                            "Comb"            : 600}

    return configdict
