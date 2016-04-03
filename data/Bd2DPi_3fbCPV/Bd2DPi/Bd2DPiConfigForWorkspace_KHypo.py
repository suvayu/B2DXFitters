from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # considered decay mode
    configdict["Decay"] = "Bd2DPi"
    configdict["Hypothesis"] = "Bd2DK"
    configdict["CharmModes"] = {"KPiPi"} 
    # year of data taking
    configdict["YearOfDataTaking"] = {"2012"} 
    # stripping (necessary in case of PIDK shapes)
    configdict["Stripping"] = {"2012":"21"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes) 
    configdict["IntegratedLuminosity"] = {"2012": {"Down": 0.59, "Up": 0.44}}
    configdict["LumRatio"] = {"2012" :
                              configdict["IntegratedLuminosity"]["2012"]["Up"] / ( configdict["IntegratedLuminosity"]["2012"]["Up"] + configdict["IntegratedLuminosity"]["2012"]["Down"] ) }
    # file name with paths to MC/data samples
    configdict["dataName"]   = "../data/Bd2DPi_3fbCPV/Bd2DPi/config_Bd2DPi.txt"
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5000,    6000    ],
                                                      "Name"                   : "BeautyMass",
                                                      "InputName"              : "lab0_FitDaughtersPVConst_M_flat"}

    configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1910    ],
                                                      "Name"                   : "CharmMass",
                                                      "InputName"              : "lab2_MM"}

    configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.2,     15.0    ],
                                                      "Bins"                   : 40,
                                                      "Name"                   : "BeautyTime",
                                                      "InputName"              : "lab0_FitDaughtersPVConst_ctau_flat"}
    
    configdict["BasicVariables"]["BacP"]          = { "Range"                  : [3000.0,  650000.0],
                                                      "Name"                   : "BacP",
                                                      "InputName"              : "lab0_FitDaughtersPVConst_P0_P_flat"}

    configdict["BasicVariables"]["BacPT"]         = { "Range"                  : [400.0,   45000.0 ],
                                                      "Name"                   : "BacPT",
                                                      "InputName"              : "lab0_FitDaughtersPVConst_P0_PT_flat"}

    configdict["BasicVariables"]["BacPIDK"]       = { "Range"                  : [1.61,    5.0     ],
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

    # PrefixID
    configdict["DsChildrenPrefix"] = { "Child1"   :"lab3",
                                       "Child2"   :"lab4",
                                       "Child3"   :"lab5"}
                                    
    return configdict
