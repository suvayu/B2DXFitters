def getconfig() :

    configdict = {}

    ############################################################
    #List of observables for all the PDFs.
    #The content of this dictionary determines the observables
    #to generate for and how may taggers are present.
    ############################################################
    
    configdict["Observables"] = {}
    configdict["Observables"] = {"BeautyMass":    {"Type"  : "RooRealVar",
                                                   "Title" : "B mass (MeV/c^2)",
                                                   "Range" : [5090, 6000]},
                                 #"CharmMass":     {"Type" : "RooRealVar",
                                 #                  "Title" : "D mass (MeV/c^2)",
                                 #                  "Range" : [1835, 1903]},
                                 "BeautyTime":    {"Type" : "RooRealVar",
                                                   "Title" : "B decay time (ps)",
                                                   "Range" : [0.2, 15.0]},
                                 "BeautyTimeErr": {"Type" : "RooRealVar",
                                                   "Title" : "B decay time error (ps)",
                                                   "Range" : [0.01, 0.1]},
                                 "BacCharge":     {"Type"  : "RooCategory",
                                                   "Title" : "Bachelor charge",
                                                   "Categories": { "h+" : +1,
                                                                   "h-" : -1}},
                                 "MistagOS":      {"Type" : "RooRealVar",
                                                   "Title" : "#eta_{OS}",
                                                   "Range" : [0.0,0.5]},
                                 "MistagSS":      {"Type" : "RooRealVar",
                                                   "Title" : "#eta_{SS}",
                                                   "Range" : [0.0,0.5]},
                                 "TrueID":        {"Type" : "RooRealVar",
                                                   "Title" : "True component ID",
                                                   "Range" : [0.0,1000.0]},
                                 "TagDecOS":      {"Type"  : "RooCategory",
                                                   "Title" : "q_{t}^{OS}",
                                                   "Categories": { "B+"       : +1,
                                                                   "Untagged" : 0,
                                                                   "B-"       : -1}},
                                 "TagDecSS":      {"Type"  : "RooCategory",
                                                   "Title" : "q_{t}^{SS}",
                                                   "Categories": { "B+"       : +1,
                                                                   "Untagged" : 0,
                                                                   "B-"       : -1}}
                                 }

    ############################################################ 
    #List of mass hypotheses for bachelor
    #The content of this dictionary determines how many
    #bachelor PID bins the final dataset is splitted into
    ############################################################
    
    configdict["Hypothesys"] = ["Bd2DPi", "Bd2DK"]

    ############################################################
    #Signal decay, Charm decay mode and year of data taking
    #Splitting per magnet polarity not implemented, at the moment
    ############################################################

    configdict["Decay"] = "Bd2DPi"
    configdict["CharmModes"] = ["KPiPi"]
    configdict["Years"] = ["run1"]

    ############################################################ 
    #List of components with yields to generate.
    #The content of this dictionary determines, for each
    #PID bin and year, how many PDF components are generated.
    #If there is only signal, a TTree ready for sFit is
    #generated directly, without need for doing a (useless)
    #mass fit.
    ############################################################
    
    configdict["Components"] = {}
    configdict["Components"] = {"Signal"        : {"Bd2DPi": {"run1": {"KPiPi": [15000] } }, "Bd2DK": {"run1": {"KPiPi": [5000] } } }} #
#                                "Combinatorial" : {"Bd2DPi": {"run1": {"KPiPi": [8000] } }, "Bd2DK": {"run1": {"KPiPi": [2000] } } },
 #                               "Bd2DRho"       : {"Bd2DPi": {"run1": {"KPiPi": [8000] } }, "Bd2DK": {"run1": {"KPiPi": [2000] } } } }
                                

    ############################################################
    #"Code" to identify the True ID for each component
    ############################################################

    configdict["TrueID"] = {}
    configdict["TrueID"] = {"Signal"        : 100,
                            "Combinatorial" : 200,
                            "Bd2DRho"       : 300}

    ############################################################
    #List of PDFs for "time-independent" observables
    #Dictionary structure: observable->component->bachelor hypo->year->D mode
    ############################################################

    configdict["PDFList"] = {}
    configdict["PDFList"]["BeautyMass"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"] = {"Bd2DPi":
                                                     {"run1":
                                                      {"KPiPi":
                                                       {"Type"       : "Ipatia",
                                                        "mean"       : [5.28017e+03],
                                                        "sigma"      : [2.02063e+01],
                                                        "zeta"       : [0.0],
                                                        "fb"         : [0.0],
                                                        "l"          : [-3.20961e+00],
                                                        "a1"         : [1.42911e+00], #left
                                                        "a2"         : [1.86674e+00], #right
                                                        "n1"         : [2.74488e+00], #left
                                                        "n2"         : [3.18373e+00]} #right
                                                       }
                                                      },
                                                     "Bd2DK":
                                                     {"run1":
                                                      {"KPiPi":
                                                       {"Type"       : "Ipatia",
                                                        "mean"       : [5.32715e+03],
                                                        "sigma"      : [2.33716e+01],
                                                        "zeta"       : [0.0],
                                                        "fb"         : [0.0],
                                                        "l"          : [-9.07419e+00],
                                                        "a1"         : [2.70454e+00],
                                                        "a2"         : [7.03565e-01],
                                                        "n1"         : [3.66284e-01],
                                                        "n2"         : [2.08885e+00]}
                                                       }
                                                      }
                                                     }
    configdict["PDFList"]["BeautyMass"]["Combinatorial"] = {"Bd2DPi":
                                                            {"run1":
                                                             {"KPiPi":
                                                              {"Type":    "Exponential",
                                                               "cB"  :    [-2.27055e-03]}
                                                              }
                                                             },
                                                            "Bd2DK":
                                                            {"run1":
                                                             {"KPiPi":
                                                              {"Type":    "Exponential",
                                                               "cB"  :    [-5.08454e-03]}
                                                              }
                                                             }
                                                            }
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"] = {"Bd2DPi":
                                                      {"run1":
                                                       {"KPiPi":
                                                        {"Type"      : "JohnsonSU",
                                                         "mean"      : [4.65054e+03],
                                                         "sigma"     : [1.09666e+03],
                                                         "nu"        : [-2.04803e+00],
                                                         "tau"       : [1.32664e+00]}
                                                        }
                                                       },
                                                      "Bd2DK":
                                                      {"run1":
                                                       {"KPiPi":
                                                        {"Type": "FromWorkspace",
                                                         "File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/nominal_1stdraft/work_dspi_hlt_mcpid_signalpid_combok.root",
                                                         "Workspace" : "workspace",
                                                         "Name"      : "PhysBkgBs2DsRhoPdf_m_both_2012"
                                                         }
                                                        }
                                                       }
                                                      }

    ############################################################ 
    #Tagging calibration and mistag PDF. If "MistagPDF" : None,
    #then a average mistag is used
    ############################################################
    
    configdict["Taggers"] = {}
    for comp in configdict["Components"].iterkeys():
        configdict["Taggers"][comp] = {}
        configdict["Taggers"][comp] = {"OS" :
                                       {"Calibration":
                                        {"p0"       : [0.0],
                                         "p1"       : [1.0],
                                         "deltap0"  : [0.0],
                                         "deltap1"  : [0.0],
                                         "avgeta"   : [0.35],
                                         "tageff"   : [0.6],
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "Mock",
                                         "eta0"     : [0.0],
                                         "etaavg"   : [0.35],
                                         "f"        : [0.25]
                                         }
                                        },
                                       "SS":
                                       {"Calibration":
                                        {"p0"       : [0.0],
                                         "p1"       : [1.0],
                                         "deltap0"  : [0.0],
                                         "deltap1"  : [0.0],
                                         "avgeta"   : [0.35],
                                         "tageff"   : [0.6],
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "Mock",
                                         "eta0"     : [0.0],
                                         "etaavg"   : [0.35],
                                         "f"        : [0.25]
                                         }
                                        }
                                       }

    ############################################################ 
    #Time resolution and acceptance (there is a single dict because
    #they are strongly connected in the way they are built).
    #If "TimeErrorPDF" : None, then an average resolution model
    #is used.
    ############################################################
    
    configdict["ResolutionAcceptance"] = {}
    for comp in configdict["Components"].iterkeys():
        configdict["ResolutionAcceptance"][comp] = {}
        configdict["ResolutionAcceptance"][comp] = {"TimeErrorPDF": #None,
                                                    {"Type": "Mock",
                                                     "ResolutionAverage" : [0.5]
                                                     },
                                                    "Acceptance":
                                                    {"Type": "Spline",
                                                     "KnotPositions" : [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
                                                     "KnotCoefficients" : [ 4.5853e-01, 6.8963e-01, 8.8528e-01,
                                                                            1.1296e+00, 1.2232e+00, 1.2277e+00 ]},
                                                    #"Resolution":
                                                    #{"Type": "AverageModel",
                                                    # "Parameters": { 'sigmas': [ 0.050 ], 'fractions': [] },
                                                    # "Bias": [0.0],
                                                    # "ScaleFactor": [1.0]}
                                                    "Resolution":
                                                    {"Type": "GaussianWithPEDTE",
                                                     "Average": [0.5],
                                                     "Bias": [0.0],
                                                     "ScaleFactor": [1.0]}
                                                    }
        
    ############################################################ 
    #Production and detection asymmetries
    ############################################################
    
    configdict["ProductionAsymmetry"] = {}
    configdict["DetectionAsymmetry"] = {}
    for comp in configdict["Components"].iterkeys():
        configdict["ProductionAsymmetry"][comp] = {}
        configdict["DetectionAsymmetry"][comp] = {}
        configdict["ProductionAsymmetry"][comp] = [0.1]
        configdict["DetectionAsymmetry"][comp] = [0.1]

    ############################################################ 
    #Time PDF parameters
    ############################################################
    
    configdict["ACP"] = {}

    #Parameters from https://svnweb.cern.ch/trac/lhcb/browser/DBASE/tags/Gen/DecFiles/v27r42/dkfiles/Bd_D-pi+,Kpipi=CPVDDalitz,DecProdCut.dec)
    ModqOverp_d     =  1
    ArgqOverp_d     =  -0.746
    ModpOverq_d     =  1
    ArgpOverq_d     =  0.746
    ModAf_d         =  0.0849
    ArgAf_d         =  0.002278
    ModAbarf_d      =  0.00137
    ArgAbarf_d      =  -1.128958
    ModAfbar_d      =  0.00137
    ArgAfbar_d      =  1.3145
    ModAbarfbar_d   =  0.0849
    ArgAbarfbar_d   =  0.002278

    #Signal (use more convenient interface with ArgLf_d, ArgLbarfbar_d and ModLf_d)
    configdict["ACP"]["Signal"] = { "Gamma"                : [0.656],
                                    "DeltaGamma"           : [0.00267],
                                    "DeltaM"               : [0.510],
                                    "ArgLf"                : [ArgqOverp_d + ArgAbarf_d - ArgAf_d],
                                    "ArgLbarfbar"          : [ArgpOverq_d + ArgAfbar_d - ArgAbarfbar_d],
                                    "ModLf"                : [ModAbarf_d/ModAf_d],
                                    "ParameteriseIntegral" : True,
                                    "NBinsAcceptance"      : 0, #keep at zero if using spline acceptance!
                                    "NBinsProperTimeErr"   : 100}

    for comp in configdict["Components"].iterkeys():
        if comp != "Signal":
            #Use other interface with C, S, Sbar, D, Dbar
            #We build trivial PDFs since we don't care about background shapes in time if we use sWeights
            configdict["ACP"][comp] = { "Gamma"                 : [1.0],
                                        "DeltaGamma"            : [0.0],
                                        "DeltaM"                : [0.0],
                                        "C"                     : [0.0],
                                        "S"                     : [0.0],
                                        "Sbar"                  : [0.0],
                                        "D"                     : [0.0],
                                        "Dbar"                  : [0.0],
                                        "ParameteriseIntegral"  : True,
                                        "NBinsAcceptance"       : 0, #keep at zero if using spline acceptance!
                                        "NBinsProperTimeErr"    : 100}
    
    return configdict
