def getconfig() :

    configdict = {}

    ############################################################
    #List of observables for all the PDFs.
    #The content of this dictionary determines the observables
    #to generate for and how may taggers are present.
    ############################################################
    
    configdict["Observables"] = {}
    configdict["Observables"] = {#"BeautyMass":    {"Type"  : "RooRealVar",
                                 #                  "Title" : "B mass (MeV/c^2)",
                                 #                  "Range" : [5090, 6000]},
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
    #Signal decay and Charm decay mode
    ############################################################

    configdict["Decay"] = "Bd2DPi"
    configdict["CharmModes"] = ["KPiPi"]

    ############################################################ 
    #List of components with yields to generate.
    #The content of this dictionary determines, for each
    #PID bin, how many PDF components are generated.
    #If there is only signal, a TTree ready for sFit is
    #generated directly, without need for doing a (useless)
    #mass fit.
    ############################################################
    
    configdict["Components"] = {}
    configdict["Components"] = {"Signal"    : {"Bd2DPi": {"KPiPi": [5000] }, "Bd2DK": {"KPiPi": [4000]}},
                                "Bd2DK"     : {"Bd2DPi": {"KPiPi" :[1000] }, "Bd2DK": {"KPiPi": [900]}},
                                "Comb"      : {"Bd2DPi": {"KPiPi": [500] }, "Bd2DK": {"KPiPi": [400]}}
                                }

    ############################################################
    #"Code" to identify the True ID for each component
    ############################################################

    configdict["TrueID"] = {}
    configdict["TrueID"] = {"Signal" : 100,
                            "Bd2DK"  : 200,
                            "Comb"   : 300}

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
        configdict["ResolutionAcceptance"][comp] = {"TimeErrorPDF":
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
