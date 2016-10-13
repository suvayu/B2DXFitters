def getconfig() :

    from math import pi

    configdict = {}

    configdict["Decay"] = "Bd2DPi"

    ############################################
    # Define all basic variables
    ############################################ 

    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5090,    6000    ],
                                                      "Name"                   : "BeautyMass",
                                                      "InputName"              : "lab0_FitDaughtersConst_M_flat"}

    #configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1904    ],
    #                                                 "Name"                   : "CharmMass",
    #                                                 "InputName"              : "obsMassDminus"}

    configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.2,     15.0    ],
                                                      "Bins"                   : 40,
                                                      "Name"                   : "BeautyTime",
                                                      "InputName"              : "lab0_FitDaughtersPVConst_ctau_flat"}

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

    configdict["BasicVariables"]["BacCharge"]     = { "Range"                  : [-1000.0, 1000.0  ],
                                                      "Name"                   : "BacCharge",
                                                      "InputName"              : "lab1_ID"}
    
    configdict["BasicVariables"]["TagDecOS"]      = { "Range"                  : [-1.0,    1.0     ],
                                                      "Name"                   : "TagDecOS",
                                                      "InputName"              : "lab0_TAGDECISION_OS"}

    configdict["BasicVariables"]["TagDecSS"]      = { "Range"                  : [-1.0,    1.0     ],
                                                      "Name"                   : "TagDecSS",
                                                      "InputName"              : "lab0_SS_PionBDT_DEC"}

    configdict["BasicVariables"]["MistagOS"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                      "Name"                   : "MistagOS",
                                                      "InputName"              : "lab0_TAGOMEGA_OS"}

    configdict["BasicVariables"]["MistagSS"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                      "Name"                   : "MistagSS",
                                                      "InputName"              : "lab0_SS_PionBDT_PROB"}
    
    configdict["AdditionalVariables"] = {}
    configdict["AdditionalVariables"]["TrueID"]   = { "Range"                  : [0.0, 1500.0],
                                                      "InputName"              : "TrueID" }
    

    ############################################
    # Define all CPV and decay rate parameters
    ############################################ 

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

    configdict["ACP"] = {}
    configdict["ACP"]["Signal"] = { "Gamma"                : [0.656],
                                    "DeltaGamma"           : [-0.00267],
                                    "DeltaM"               : [0.510],
                                    "ArgLf"                : [ArgqOverp_d + ArgAbarf_d - ArgAf_d],
                                    "ArgLbarfbar"          : [ArgpOverq_d + ArgAfbar_d - ArgAbarfbar_d],
                                    "ModLf"                : [ModAbarf_d/ModAf_d],
                                    "ParameteriseIntegral" : True,
                                    "CPlimit"              : {"upper":1.0, "lower":-1.0},
                                    "NBinsAcceptance"      : 0} #keep at zero if using spline acceptance!

    ############################################
    # Define resolution and acceptance models
    ############################################

    configdict["ResolutionAcceptance"] = {}
    configdict["ResolutionAcceptance"]["Signal"] = {}
    configdict["ResolutionAcceptance"]["Signal"] = {"TimeErrorPDF": None,
                                                    "Acceptance":
                                                    {"Type": "Spline",
                                                     "Float": False,
                                                     "KnotPositions" : [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
                                                     "KnotCoefficients" : [ 4.5853e-01, 6.8963e-01, 8.8528e-01,
                                                                            1.1296e+00, 1.2232e+00, 1.2277e+00 ]},
                                                    "Resolution":
                                                    {"Type": "AverageModel",
                                                     "Parameters": { 'sigmas': [ 0.050 ], 'fractions': [] },
                                                     "Bias": [0.0],
                                                     "ScaleFactor": [1.0]}
                                                    }

    ############################################
    # Define asymmetries
    ############################################
    
    configdict["ProductionAsymmetry"] = {}
    configdict["DetectionAsymmetry"] = {}
    configdict["ProductionAsymmetry"]["Signal"] = {}
    configdict["DetectionAsymmetry"]["Signal"] = {}
    configdict["ProductionAsymmetry"]["Signal"] = [-0.0058] #from arXiv:1408.0275
    configdict["DetectionAsymmetry"]["Signal"] = [0.005] #a random value, for now 

    ############################################
    # Define taggers and their calibration
    ############################################

    configdict["Taggers"] = {}
    configdict["Taggers"]["Signal"] = {}
    configdict["Taggers"]["Signal"] = {"OS" :
                                       {"Calibration":
                                        {"p0"       : [0.37795],
                                         "p1"       : [0.97541],
                                         "deltap0"  : [0.018825],
                                         "deltap1"  : [0.042438],
                                         "avgeta"   : [0.37079],
                                         "tageff"   : [0.38],
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "Mock",
                                         "eta0"     : [0.0],
                                         "etaavg"   : [0.37079],
                                         "f"        : [0.25]
                                         }
                                        },
                                       "SS":
                                       {"Calibration":
                                        {"p0"       : [0.37110],
                                         "p1"       : [1.0409],
                                         "deltap0"  : [0.0056312],
                                         "deltap1"  : [-0.0869332],
                                         "avgeta"   : [0.38693],
                                         "tageff"   : [0.80],
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "Mock",
                                         "eta0"     : [0.0],
                                         "etaavg"   : [0.38693],
                                         "f"        : [0.25]
                                         }
                                        }
                                       }

    ############################################
    # Choose parameters to fix
    ############################################
                                       
    configdict["constParams"] = []
    configdict["constParams"].append('Cf')
    configdict["constParams"].append('Cfbar')
    configdict["constParams"].append('Df')
    configdict["constParams"].append('Dfbar')
    configdict["constParams"].append('.*scalefactor')

    ############################################
    # Choose parameters to perform the
    # likelihood scan for
    ############################################

    configdict["LikelihoodScan"] = []
    configdict["LikelihoodScan"].append("Sf")
    configdict["LikelihoodScan"].append("Sfbar")

    ############################################
    # Choose initial free parameters to randomise
    ############################################

    configdict["randomiseParams"] = {}
    configdict["randomiseParams"] = {'Sf'                          : {'min': -0.04,   'max': -0.02},
                                     'Sfbar'                       : {'min': 0.02, 'max': 0.04}
                                     }
    
    return configdict
