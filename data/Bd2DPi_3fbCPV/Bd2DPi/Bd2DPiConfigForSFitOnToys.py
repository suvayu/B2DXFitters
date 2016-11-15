def getconfig() :

    import math
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

    configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.4,     15.0    ],
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
    configdict["ACP"]["Signal"] = { "Gamma"                : [1.0 / 1.520, 0.1, 2.0], #Inverse lifetime from HFAG (http://www.slac.stanford.edu/xorg/hfag/osc/summer_2016/)
                                    "DeltaGamma"           : [0.0],
                                    "DeltaM"               : [0.5050, 0.01, 2.0], #Global average from HFAG (http://www.slac.stanford.edu/xorg/hfag/osc/summer_2016/)
                                    #"ArgLf"                : [ArgqOverp_d + ArgAbarf_d - ArgAf_d],
                                    #"ArgLbarfbar"          : [ArgpOverq_d + ArgAfbar_d - ArgAbarfbar_d],
                                    #"ModLf"                : [ModAbarf_d/ModAf_d],
                                    "C"                    : [1.0], #we neglect r^2 terms
                                    "S"                    : [-0.031], #from decfile
                                    "Sbar"                 : [0.029], #from decfile
                                    "D"                    : [0], #from DeltaGamma=0
                                    "Dbar"                 : [0], #from DeltaGamma=0
                                    "ParameteriseIntegral" : True,
                                    "CPlimit"              : {"upper":1.0, "lower":-1.0},
                                    "NBinsAcceptance"      : 0} #keep at zero if using spline acceptance!

    ############################################
    # Define resolution and acceptance models
    ############################################

    configdict["ResolutionAcceptance"] = {}
    configdict["ResolutionAcceptance"]["Signal"] = {}
    configdict["ResolutionAcceptance"]["Signal"] = {"TimeErrorPDF": None,
                                                    "Acceptance": #From ANA note v2
                                                    {"Type": "Spline",
                                                     "Float": True,
                                                     "KnotPositions" : [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
                                                     "KnotCoefficients" : [0.3889, 0.5754, 0.8515, 1.0649, 1.2373, 1.4149] },
                                                    "Resolution": #From ANA note v2
                                                    {"Type": "AverageModel",
                                                     "Parameters": { 'sigmas': [ 0.05491 ], 'fractions': [] },
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
    configdict["ProductionAsymmetry"]["Signal"] = [-0.0124, -1.0, 1.0] #from ANA note v2
    configdict["DetectionAsymmetry"]["Signal"] = [0.0086, -1.0, 1.0] #from arXiv:1408.0275v2 (OPPOSITE SIGN!!!)

    ############################################
    # Define taggers and their calibration
    ############################################

    configdict["Taggers"] = {}
    configdict["Taggers"]["Signal"] = {}
    configdict["Taggers"]["Signal"] = {"OS" : #From Bu, stat and syst combined
                                       {"Calibration":
                                        {"p0"       : [0.3737056, 0.01, 0.8],
                                         "p1"       : [1.028621, 0.3, 1.5],
                                         "deltap0"  : [0.011819, -0.1, 0.3],
                                         "deltap1"  : [0.043134, -0.1, 0.3],
                                         "avgeta"   : [0.347742], #<eta> on spline-corrected Bu->D0Pi
                                         "tageff"   : [0.371, 0.01, 0.99], #float in the fit
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "BuildTemplate"}
                                        },
                                       "SS": #From JpsiKst, stat and syst combined
                                       {"Calibration":
                                        {"p0"       : [0.4424049, 0.01, 0.8],
                                         "p1"       : [0.81302, 0.3, 1.5],
                                         "deltap0"  : [0.00062332, -0.1, 0.1],
                                         "deltap1"  : [0.0066248, -0.1, 0.1],
                                         "avgeta"   : [0.435], #<eta> on Bd->J/psiK*
                                         "tageff"   : [0.816, 0.01, 0.99], #float in the fit
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
    configdict["constParams"].append('.*scalefactor')
    #configdict["constParams"].append('resmodel00_sigma')

    # configdict["constParams"].append('p0_OS')
    # configdict["constParams"].append('p1_OS')
    # configdict["constParams"].append('deltap0_OS')
    # configdict["constParams"].append('deltap1_OS')

    # configdict["constParams"].append('p0_SS')
    # configdict["constParams"].append('p1_SS')
    # configdict["constParams"].append('deltap0_SS')
    # configdict["constParams"].append('deltap1_SS')

    # configdict["constParams"].append('deltaM')
    # configdict["constParams"].append('Gamma')
    # configdict["constParams"].append('resmodel00_sigma')
    # configdict["constParams"].append('ProdAsymm')
    # configdict["constParams"].append('DetAsymm')

    ############################################
    # Build gaussian constraints
    # See B2DXFitters/GaussianConstraintBuilder.py for documentation
    ############################################

    configdict["gaussCons"] = {}
    # Constraint on resolution
    configdict["gaussCons"]["resmodel00_sigma"] = 0.00038
    # Constraint on DeltaM
    configdict["gaussCons"]["deltaM"] = math.sqrt(0.0021*0.0021 + 0.0010*0.0010)
    # Constraint on Gamma (error on gamma = rel. error on lifetime * gamma)
    configdict["gaussCons"]["Gamma"] = (0.004/1.520) * (1.0/1.520)
    # Multivariate constraint for production and detection asymmetries
    # configdict["gaussCons"]["multivarAsymm"] = [ ['ProdAsymm', 'DetAsymm'], #parname
    #                                              [math.sqrt(0.0081*0.0081 + 0.0014*0.0014), 0.0046], #errors
    #                                              [ [1, -0.65], #correlation matrix
    #                                                [-0.65, 1] ]
    #                                              ]
    # Multivariate constraint for OS combination
    configdict["gaussCons"]["multivarOSCalib"] = [ ['p0_OS', 'p1_OS', 'deltap0_OS', 'deltap1_OS'], #parname
                                                    [0.00276866695767, 0.0532951796942, 0.00269475453428, 0.037310097266], #errors
                                                    [ [1,         0.14218,       -0.017668,       0.0092814],  #correlation matrix from EPM
                                                      [0.14218,         1,       0.0092814,       -0.048821],
                                                      [-0.017668, 0.0092814,             1,         0.14218],
                                                      [0.0092814,  -0.048821,      0.14218,                1] ]
                                                    ]
    #Add constraint for SS combination
    configdict["gaussCons"]["multivarSSCalib"] = [ ['p0_SS', 'p1_SS', 'deltap0_SS', 'deltap1_SS'], #parname
                                                   [0.007431465, 0.05246453784, 0.004264925, 0.08085860086], #errors
                                                   [ [1,         -0.054207,       -0.01714,       -0.0048873],  #correlation matrix from EPM
                                                     [-0.054207,         1,       -0.004997,       -0.0053978],
                                                     [-0.01714, -0.004997,             1,         -0.071635],
                                                     [-0.0048873,  -0.0053978,      -0.071635,                1] ]
                                                   ]


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
