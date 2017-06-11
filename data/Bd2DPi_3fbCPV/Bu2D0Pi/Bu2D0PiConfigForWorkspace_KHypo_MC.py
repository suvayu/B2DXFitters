from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # considered decay mode
    configdict["Decay"] = "Bu2D0Pi"
    # PIDK for bachelor
    configdict["BachelorHypo"] = "Bu2D0K"
    configdict["CharmModes"] = {"KPi"} 
    # year of data taking
    configdict["YearOfDataTaking"] = {"2011","2012"} 
    # file name with paths to MC/data samples
    configdict["dataName"]   = "/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bu2D0Pi/config_Bu2D0Pi.txt"
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5090,    6000    ],
                                                      "Name"                   : "BeautyMass",
                                                      "InputName"              : "lab0_MM"}

    configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1904    ],
                                                      "Name"                   : "CharmMass",
                                                      "InputName"              : "lab2_MM"}

    configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.0002,     0.015    ],
                                                      "Bins"                   : 40,
                                                      "Name"                   : "BeautyTime",
                                                      "InputName"              : "lab0_TAU"}
    
    configdict["BasicVariables"]["BacP"]          = { "Range"                  : [2000.0,  650000.0],
                                                      "Name"                   : "BacP",
                                                      "InputName"              : "lab1_P"}

    configdict["BasicVariables"]["BacPT"]         = { "Range"                  : [400.0,   45000.0 ],
                                                      "Name"                   : "BacPT",
                                                      "InputName"              : "lab1_PT"}

    configdict["BasicVariables"]["BacPIDK"]       = { "Range"                  : [-999.0,    999.0     ],
                                                      "Name"                   : "BacPIDK",
                                                      "InputName"              : "lab1_PIDKcorr"}

    configdict["BasicVariables"]["nTracks"]       = { "Range"                  : [15.0,    1000.0  ],
                                                      "Name"                   : "nTracks",
                                                      "InputName"              : "nTracks"}

    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range"                  : [0.00001,    0.0001   ],
                                                      "Name"                   : "BeautyTimeErr",
                                                      "InputName"              : "lab0_TAUERR"}

    configdict["BasicVariables"]["BacCharge"]     = { "Range"                  : [-1000.0, 1000.0  ],
                                                      "Name"                   : "BacCharge",
                                                      "InputName"              : "lab1_ID"}

    configdict["BasicVariables"]["TagDecOSComb"]      = { "Range"                  : [-1.0,    1.0     ],
                                                          "Name"                   : "TagDecOSCharm",
                                                          "InputName"              : "lab0_TAGDECISION_OS"}

    configdict["BasicVariables"]["TagDecOSCharm"]      = { "Range"                  : [-1.0,    1.0     ],
                                                           "Name"                   : "TagDecOSCharm",
                                                           "InputName"              : "lab0_OS_Charm_DEC"}

    configdict["BasicVariables"]["TagDecSSPionBDT"]      = { "Range"                  : [-1.0,    1.0     ],
                                                             "Name"                   : "TagDecSSPionBDT",
                                                             "InputName"              : "lab0_SS_PionBDT_DEC"}

    configdict["BasicVariables"]["TagDecSSProton"]      = { "Range"                  : [-1.0,    1.0     ],
                                                            "Name"                   : "TagDecSSProton",
                                                            "InputName"              : "lab0_SS_Proton_DEC"}

    configdict["BasicVariables"]["MistagOSComb"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                          "Name"                   : "MistagOSComb",
                                                          "InputName"              : "lab0_TAGOMEGA_OS"}

    configdict["BasicVariables"]["MistagOSCharm"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                           "Name"                   : "MistagOSCharm",
                                                           "InputName"              : "lab0_OS_Charm_PROB"}

    configdict["BasicVariables"]["MistagSSPionBDT"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                             "Name"                   : "MistagSSPionBDT",
                                                             "InputName"              : "lab0_SS_PionBDT_PROB"}

    configdict["BasicVariables"]["MistagSSProton"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                            "Name"                   : "MistagSSProton",
                                                            "InputName"              : "lab0_SS_Proton_PROB"}

    #Additional variables not foreseen before
    configdict["AdditionalVariables"] = {}

    configdict["AdditionalVariables"]["BeautyID"]      = { "Range"                  : [ -1000.,    1000.     ],
                                                           "Name"                   : "BeautyID",
                                                           "InputName"              : "lab0_TRUEID"}
    
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
    configdict["CreateCombinatorial"]["BeautyMass"] = { "All"   : { "Cut": "lab0_MM>5600.0" },
                                                        "KPi"   : { "Cut": "lab0_MM>5600.0" }
                                                        }

    # PIDK bin
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"] = {"Data": "lab1_PIDK>5.0", "MC": "lab1_PIDKcorr>5.0&&lab0_BKGCAT<60"}

    
    return configdict
