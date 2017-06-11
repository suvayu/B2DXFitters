from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # considered decay mode
    configdict["Decay"] = "Bd2DPi"
    # PIDK for bachelor
    configdict["BachelorHypo"] = "Bd2DPi"
    configdict["CharmModes"] = {"KPiPi"} 
    # year of data taking
    configdict["YearOfDataTaking"] = {"2011","2012"} 
    # file name with paths to MC/data samples
    configdict["dataName"]   = "/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/config_Bd2DPi.txt"
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5090,    6000    ],
                                                      "Name"                   : "BeautyMass",
                                                      "InputName"              : "lab0_FitDaughtersConst_M_flat"}

    configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1904    ],
                                                      "Name"                   : "CharmMass",
                                                      "InputName"              : "lab0_FitwithoutConst_Dplus_M_flat"}

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

    configdict["BasicVariables"]["BacPIDK"]       = { "Range"                  : [-999.0,    999.0     ],
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

    configdict["BasicVariables"]["BDTG"]           = { "Range"                  : [-1, 1],
                                                       "Name"                   : "BDTG",
                                                       "InputName"              : "BDT_classifier"}

    #Additional variables not foreseen before
    configdict["AdditionalVariables"] = {}
    
    configdict["AdditionalVariables"]["BeautyPhi"]      = { "Range"                  : [ -10.,    10.     ],
                                                            "Name"                   : "BeautyPhi",
                                                            "InputName"              : "lab0_LOKI_PHI"}
    
    configdict["AdditionalVariables"]["BeautyEta"]      = { "Range"                  : [ 1.5,    10.0     ],
                                                            "Name"                   : "BeautyEta",
                                                            "InputName"              : "lab0_LOKI_ETA"}
    
    configdict["AdditionalVariables"]["BeautyPT"]      = { "Range"                  : [ 0.0,    100000     ],
                                                           "Name"                   : "BeautyPT",
                                                           "InputName"              : "lab0_PT"}

    configdict["AdditionalVariables"]["BeautyP"]      = { "Range"                  : [ 0.0,    3000000     ],
                                                          "Name"                   : "BeautyP",
                                                          "InputName"              : "lab0_P"}
    
    configdict["AdditionalVariables"]["nPV"]      = { "Range"                  : [ 0.0,    10     ],
                                                      "Name"                   : "nPV",
                                                      "InputName"              : "nPV"}
    
    # Combinatorial
    configdict["CreateCombinatorial"] = {}
    configdict["CreateCombinatorial"]["BeautyMass"] = { "All"   : { "Cut": "lab0_FitDaughtersConst_M_flat>5500.0" },
                                                        "KPiPi" : { "Cut": "lab0_FitDaughtersConst_M_flat>5500.0" }
                                                        }
    configdict["CreateCombinatorial"]["CharmMass"] = { "All"   : { "Cut": "lab0_FitDaughtersConst_M_flat>5500.0" },
                                                       "KPiPi" : { "Cut": "lab0_FitDaughtersConst_M_flat>5500.0" }
                                                       }

    # PIDK bin
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"] = {"Data": "lab1_PIDK<5.0", "MC": "lab1_PIDKcorr<5.0&&lab0_BKGCAT<60"}

    
    return configdict
