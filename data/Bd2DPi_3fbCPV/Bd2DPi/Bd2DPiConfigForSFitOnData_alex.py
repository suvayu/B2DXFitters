def getconfig() :

    import math
    from math import pi

    configdict = {}

    configdict["Decay"] = "Bd2DPi"

    ############################################
    # Define all basic variables
    ############################################

    configdict["BasicVariables"] = {}
    # configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5090,    6000    ],
    #                                                   "Name"                   : "BeautyMass",
    #                                                   "InputName"              : "lab0_FitDaughtersConst_M_flat"}

    # configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1904    ],
    #                                                   "Name"                   : "CharmMass",
    #                                                   "InputName"              : "obsMassDminus"}

    configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.4,     15.0    ],
                                                      "Bins"                   : 40,
                                                      "Name"                   : "BeautyTime",
                                                      "InputName"              : "lab0_FitDaughtersPVConst_ctau_flat"}

    # configdict["BasicVariables"]["BacP"]          = { "Range"                  : [2000.0,  650000.0],
    #                                                   "Name"                   : "BacP",
    #                                                   "InputName"              : "lab0_FitDaughtersConst_P0_P_flat"}

    # configdict["BasicVariables"]["BacPT"]         = { "Range"                  : [400.0,   45000.0 ],
    #                                                   "Name"                   : "BacPT",
    #                                                   "InputName"              : "lab0_FitDaughtersConst_P0_PT_flat"}

    # configdict["BasicVariables"]["BacPIDK"]       = { "Range"                  : [-999.0, 999.0     ],
    #                                                   "Name"                   : "BacPIDK",
    #                                                   "InputName"              : "lab1_PIDK"}

    # configdict["BasicVariables"]["nTracks"]       = { "Range"                  : [15.0,    1000.0  ],
    #                                                   "Name"                   : "nTracks",
    #                                                   "InputName"              : "nTracks"}

    # configdict["BasicVariables"]["BeautyTimeErr"] = { "Range"                  : [0.01,    0.1     ],
    #                                                   "Name"                   : "BeautyTimeErr",
    #                                                   "InputName"              : "lab0_FitDaughtersPVConst_ctauErr_flat"}

    configdict["BasicVariables"]["BacCharge"]     = { "Range"                  : [-1000.0, 1000.0  ],
                                                      "Name"                   : "BacCharge",
                                                      "InputName"              : "lab1_ID"}

    configdict["BasicVariables"]["TagDecOS"]      = { "Range"                  : [-1.0, 0.0, 1.0],
                                                      "Name"                   : "TagDecOS",
                                                      "InputName"              : "lab0_TAGDECISION_OS"}

    configdict["BasicVariables"]["TagDecSS"]      = { "Range"                  : [-1.0, 0.0, 1.0],
                                                      "Name"                   : "TagDecSS",
                                                      "InputName"              : "lab0_SS_PionBDT_DEC"}

    configdict["BasicVariables"]["MistagOS"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                      "Name"                   : "MistagOS",
                                                      "InputName"              : "lab0_TAGOMEGA_OS"}

    configdict["BasicVariables"]["MistagSS"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                      "Name"                   : "MistagSS",
                                                      "InputName"              : "lab0_SS_PionBDT_PROB"}

    # configdict["BasicVariables"]["BDTG"]           = { "Range"                  : [0.05, 1],
    #                                                    "Name"                   : "BDTG",
    #                                                    "InputName"              : "BDT_classifier"}

    #Additional variables not foreseen before
    configdict["AdditionalVariables"] = {}

    # configdict["AdditionalVariables"]["BeautyPhi"]      = { "Range"                  : [ -10.,    10.     ],
    #                                                         "Name"                   : "BeautyPhi",
    #                                                         "InputName"              : "lab0_LOKI_PHI"}

    # configdict["AdditionalVariables"]["BeautyEta"]      = { "Range"                  : [ 1.5,    10.0     ],
    #                                                         "Name"                   : "BeautyEta",
    #                                                         "InputName"              : "lab0_LOKI_ETA"}

    # configdict["AdditionalVariables"]["BeautyPT"]      = { "Range"                  : [ 0.0,    100000     ],
    #                                                        "Name"                   : "BeautyPT",
    #                                                        "InputName"              : "lab0_PT"}

    # configdict["AdditionalVariables"]["nPV"]      = { "Range"                  : [ 0.0,    10     ],
    #                                                   "Name"                   : "nPV",
    #                                                   "InputName"              : "nPV"}


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
    configdict["ACP"]["Signal"] = { "Gamma"                : [0.658],
                                    "DeltaGamma"           : [0.0],
                                    "DeltaM"               : [0.51],
                                    "ArgLf"                : [ArgqOverp_d + ArgAbarf_d - ArgAf_d],
                                    "ArgLbarfbar"          : [ArgpOverq_d + ArgAfbar_d - ArgAbarfbar_d],
                                    "ModLf"                : [ModAbarf_d/ModAf_d],
                                    "ParameteriseIntegral" : True,
                                    "CPlimit"              : {"upper":2.0, "lower":-2.0},
                                    "NBinsAcceptance"      : 0} #keep at zero if using spline acceptance!

    ############################################
    # Define resolution and acceptance models
    ############################################

    p0 = 1.064
    p1 = -0.04554

    configdict["ResolutionAcceptance"] = {}
    configdict["ResolutionAcceptance"]["Signal"] = {}
    configdict["ResolutionAcceptance"]["Signal"] = {"TimeErrorPDF": None,
                                                    "Acceptance":
                                                    {"Type": "Spline",
                                                     "Float": True,
                                                     "KnotPositions" : [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
                                                     "KnotCoefficients" : [ 0.4067, 0.6005, 0.9140,
                                                                            1.1096, 1.2761, 1.4256 ]},
                                                    "Resolution":
                                                    {"Type": "AverageModel",
                                                     "Parameters": { 'sigmas': [ 0.05491 ], 'fractions': [] }, #use expectation, for now
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
    configdict["ProductionAsymmetry"]["Signal"] = [0.0]
    configdict["DetectionAsymmetry"]["Signal"] = [0.0] #???

    ############################################
    # Define taggers and their calibration
    ############################################

    configdict["Taggers"] = {}
    configdict["Taggers"]["Signal"] = {}
    configdict["Taggers"]["Signal"] = {"OS" : #Take it uncalibrated for now
                                       {"Calibration":
                                        {"p0"       : [0.37],
                                         "p1"       : [1.0],
                                         "deltap0"  : [0.0],
                                         "deltap1"  : [0.0],
                                         "avgeta"   : [0.37],
                                         "tageff"   : [0.8,0.0,1.0],
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "BuildTemplate"}
                                        },
                                       "SS": #Take it uncalibrated for now
                                       {"Calibration":
                                        {"p0"       : [0.46],
                                         "p1"       : [1.0],
                                         "deltap0"  : [0.0],
                                         "deltap1"  : [0.0],
                                         "avgeta"   : [0.46],
                                         "tageff"   : [0.8, 0.0, 1.0],
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "BuildTemplate"}
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
    #configdict["constParams"].append('Sf')
    #configdict["constParams"].append('Sfbar')
    configdict["constParams"].append('.*scalefactor')

    ############################################
    # Build gaussian constraints
    # See B2DXFitters/GaussianConstraintBuilder.py for documentation
    ############################################

    configdict["gaussCons"] = {}
    # Error on production asymmetry = add in quadrature stat. and syst. errors
    # configdict["gaussCons"]["ProdAsymm"] = math.sqrt(0.008079*0.008079 + 0.001428*0.001428)
    #Error on gamma = gamma central value * relative uncertainty on lifetime (= relative uncertainty on gamma)
    # configdict["gaussCons"]["Gamma"] = (1.0 / 1.520) * (0.004 / 1.520)
    #Error  on detection asymmetry = 1%
    # configdict["gaussCons"]["DetAsymm"] = 0.01
    #Error on Delta M
    # configdict["gaussCons"]["deltaM"] = 0.0019

    ############################################
    # Choose parameters to blind
    ############################################

    configdict["blindParams"] = []
    # configdict["blindParams"].append('Sf')
    # configdict["blindParams"].append('Sfbar')

    ############################################
    # Choose parameters to perform the
    # likelihood scan for
    ############################################

    configdict["LikelihoodScan"] = []
    #configdict["LikelihoodScan"].append("Sf")
    #configdict["LikelihoodScan"].append("Sfbar")

    return configdict
