def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bd2DPi"
    configdict["CharmModes"] = {"KPiPi"}
    # year of data taking                                                                                                                          
    configdict["YearOfDataTaking"] = {"2011", "2012"}
    # stripping (necessary in case of PIDK shapes)                                                                                              
    configdict["Stripping"] = {"2012":"21", "2011":"21r1"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)                                                                  
    configdict["IntegratedLuminosity"] = {"2011": {"Down": 0.59, "Up": 0.44}, "2012":{"Down": 0.9894, "Up": 0.9985}}
    # file name with paths to MC/data samples                                                                                                       
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/Bd2DPi/config_Bd2DPi.txt"
    #settings for control plots                                                                                                                                                           
    configdict["ControlPlots"] = {}
    configdict["ControlPlots"] = { "Directory": "PlotBd2DPi", "Extension":"pdf"}

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5000,    6000    ], "InputName" : "lab0_MassFitConsD_M"}
    #configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5200,    6000    ], "InputName" : "lab0_MassFitConsD_M"} #Stefano: narrow
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1830,    1920    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-7.0,    6.0     ], "InputName" : "lab1_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.0,     1.0     ], "InputName" : "BDTGResponse_2"} #Stefano (use new BDTG)
    #configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_TAGDECISION_OS"}
    #configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_SS_nnetKaon_DEC"}
    #configdict["BasicVariables"]["MistagOS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_TAGOMEGA_OS"}
    #configdict["BasicVariables"]["MistagSS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_SS_nnetKaon_PROB"}

    # tagging calibration                                                                                               
    #configdict["TaggingCalibration"] = {}
    #configdict["TaggingCalibration"]["OS"] = {"p0": 0.3834, "p1": 0.9720, "average": 0.3813}
    #configdict["TaggingCalibration"]["SS"] = {"p0": 0.4244, "p1": 1.2180, "average": 0.4097}

    # additional cuts applied to data sets                                                                                    
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0",            "MC" : "lab2_TAU>0&&lab1_M<200", "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}

    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                              
    # order of particles: KKPi, KPiPi, PiPiPi                                                                                                         
    configdict["DsChildrenPrefix"] = {"Child1":"lab3","Child2":"lab4","Child3": "lab5"} #lab3 = K, lab4, lab5 = pi

    # weighting templates by PID eff/misID                                                                                                                                                 
    configdict["WeightingMassTemplates"] = {"Shift":{ "BeautyMass": -2.0, "CharmMass": 0.0} } # Stefano (PID MC-reweight not applied)
    #configdict["WeightingMassTemplates"] = { "Variables":["lab4_P","lab3_P"], "PIDBach": 0, "PIDChild": 0, "PIDProton": 5, "RatioDataMC":True }

    # Stefano (add Flavour Tagging variables (for Giulia and Stefano P.)) 
    configdict["AdditionalVariables"] = {}
    configdict["AdditionalVariables"]["tagOmegaSSPionBDT"] =  { "Range" : [ 0.0, 0.5 ], "InputName" : "lab0_SS_PionBDT_PROB"}
    configdict["AdditionalVariables"]["tagDecSSPionBDT"]   =  { "Range" : [ -1.0, 1.0 ], "InputName" : "lab0_SS_PionBDT_DEC"}
    configdict["AdditionalVariables"]["tagOmegaSSProton"]  =  { "Range" : [ 0.0, 0.5 ], "InputName" : "lab0_SS_Proton_PROB"}
    configdict["AdditionalVariables"]["tagDecSSProton"]    =  { "Range" : [ -1.0, 1.0 ], "InputName" : "lab0_SS_Proton_DEC"}
    configdict["AdditionalVariables"]["nPV"]               =  { "Range" : [ 1.0, 7.0 ], "InputName" : "nPV"}
    configdict["AdditionalVariables"]["BeautyPt"]          =  { "Range" : [ 0.0, 35000 ], "InputName" : "lab0_PT"}
    configdict["AdditionalVariables"]["BeautyPz"]          =  { "Range" : [ 0.0, 700000.0 ], "InputName" : "lab0_PZ"}
    configdict["AdditionalVariables"]["BeautyPx"]          =  { "Range" : [ -40000.0, 40000.0 ], "InputName" : "lab0_PX"}
    configdict["AdditionalVariables"]["BeautyPy"]          =  { "Range" : [ -40000.0, 40000.0 ], "InputName" : "lab0_PY"}

    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                               MDfit fitting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # Stefano: updated to 2012 MC
    # Bs signal shapes 
    # up + dw                                                                                                                                     
    configdict["BsSignalShape"] = {} 
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5280.0},     "Fixed": False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"KPiPi":12.763},  "Fixed": True} 
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"KPiPi":21.389},  "Fixed": True} 
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"KPiPi":1.9990},  "Fixed": True}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"KPiPi":-2.1618}, "Fixed": True}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"KPiPi":1.0928},  "Fixed": True}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"KPiPi":2.4010},  "Fixed": True}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"KPiPi":0.68930}, "Fixed": True}
    configdict["BsSignalShape"]["R"]       = {"Run1": {"KPiPi":1.0 },    "Fixed": False}

    # MC smeared (5000-5600 MeV)
    #configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5280.},     "Fixed": False}
    #configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"KPiPi":15.483},  "Fixed": True} 
    #configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"KPiPi":18.624},  "Fixed": True} 
    #configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"KPiPi":1.3330},  "Fixed": True}
    #configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"KPiPi":-1.2472}, "Fixed": True}
    #configdict["BsSignalShape"]["n1"]      = {"Run1": {"KPiPi":1.9093},  "Fixed": True}
    #configdict["BsSignalShape"]["n2"]      = {"Run1": {"KPiPi":5.1967},  "Fixed": True}
    #configdict["BsSignalShape"]["frac"]    = {"Run1": {"KPiPi":0.57147}, "Fixed": True}


    # Ds signal shapes  
    # up + dw                                                                                                                                     
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All":1869.8},       "Fixed": False}
    configdict["DsSignalShape"]["sigma1"]  = {"Run1": {"KPiPi":11.501},     "Fixed": True}
    configdict["DsSignalShape"]["sigma2"]  = {"Run1": {"KPiPi":6.1237},     "Fixed": True}
    configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"KPiPi":1.6382},     "Fixed": True}
    configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"KPiPi":-3.4683},    "Fixed": True}
    configdict["DsSignalShape"]["n1"]      = {"Run1": {"KPiPi":4.8678},     "Fixed": True}
    configdict["DsSignalShape"]["n2"]      = {"Run1": {"KPiPi":4.3285e-06}, "Fixed": True}
    configdict["DsSignalShape"]["frac"]    = {"Run1": {"KPiPi":0.38916},    "Fixed": True}
    configdict["DsSignalShape"]["R"]       = {"Run1": {"KPiPi":1.0 },       "Fixed": False}

    # combinatorial background                                                                                                                              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"]  = "DoubleExponential"
    configdict["BsCombinatorialShape"]["cB1"]   = {"Run1": {"KPiPi":-1.0361e-03}, "Fixed": False}
    configdict["BsCombinatorialShape"]["cB2"]   = {"Run1": {"KPiPi":-0.01},       "Fixed": False}
    configdict["BsCombinatorialShape"]["frac"]  = {"Run1": {"KPiPi":0.5},         "Fixed": False}

    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusDoubleCrystalBallWithWidthRatioSharedMean"
    configdict["DsCombinatorialShape"]["sigma1"]  = {"Run1": {"KPiPi":11.501},          "Fixed":True}
    configdict["DsCombinatorialShape"]["sigma2"]  = {"Run1": {"KPiPi":6.1237},          "Fixed":True}
    configdict["DsCombinatorialShape"]["alpha1"]  = {"Run1": {"KPiPi":1.6382},          "Fixed":True}
    configdict["DsCombinatorialShape"]["alpha2"]  = {"Run1": {"KPiPi":-3.4683},         "Fixed":True}
    configdict["DsCombinatorialShape"]["n1"]      = {"Run1": {"KPiPi":4.8678},          "Fixed":True}
    configdict["DsCombinatorialShape"]["n2"]      = {"Run1": {"KPiPi":4.3285e-06},      "Fixed":True}
    configdict["DsCombinatorialShape"]["frac"]    = {"Run1": {"KPiPi":0.38916},         "Fixed":True}
    configdict["DsCombinatorialShape"]["R"]       = {"Run1": {"KPiPi":1.5},             "Fixed":False}
    configdict["DsCombinatorialShape"]["cB"]      = {"Run1": {"KPiPi":-1.9193e-03},     "Fixed":False}
    configdict["DsCombinatorialShape"]["fracD"]   = {"Run1": {"KPiPi":0.5},             "Fixed":False}

    #configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusSignal" 
    #configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusSignal" 
    #configdict["DsCombinatorialShape"]["cD"]    = {"Run1": {"KPiPi":-3e-03},      "Fixed": False}
    #configdict["DsCombinatorialShape"]["fracD"] = {"Run1": {"KPiPi":0.5},         "Fixed": False}

    # Che cosa e'???
    configdict["AdditionalParameters"] = {}
    configdict["AdditionalParameters"]["g1_f1_frac"] = {"Run1":{"All":{"Both":{"CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed": False} 
    configdict["AdditionalParameters"]["g1_f2_frac"] = {"Run1":{"All":{"Both":{"CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed": False}

    # expected yields #Stefano: fix Bs2DsPi & Lb2LcPi 
    configdict["Yields"] = {}
    configdict["Yields"]["Bd2DK"]     = {"2011": {"KPiPi":15000.0},  "2012": {"KPiPi":30000.0},  "Fixed": False} 
    configdict["Yields"]["Bd2DRho"]   = {"2011": {"KPiPi":80000.0},  "2012": {"KPiPi":160000.0}, "Fixed": False}
    configdict["Yields"]["Bd2DstPi"]  = {"2011": {"KPiPi":60000.0},  "2012": {"KPiPi":120000.0}, "Fixed": False}
    configdict["Yields"]["Bs2DsPi"]   = {"2011": {"KPiPi":1000.0},   "2012": {"KPiPi":2000.0},   "Fixed": True}
    configdict["Yields"]["Lb2LcPi"]   = {"2011": {"KPiPi":250.0},    "2012": {"KPiPi":500.0},    "Fixed": True}
    configdict["Yields"]["CombBkg"]   = {"2011": {"KPiPi":30000.0},  "2012": {"KPiPi":60000.0},  "Fixed": False}
    configdict["Yields"]["Signal"]    = {"2011": {"KPiPi":150000.0}, "2012": {"KPiPi":300000.0}, "Fixed": False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#    
    ###                                                               MDfit plotting settings                                                             
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#               
    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = ["Sig", "CombBkg", "Bd2DK", "Lb2LcPi", "Bs2DsPi", "Bd2DRho", "Bd2DstPi"] 
    configdict["PlotSettings"]["colors"] = [kRed-7, kBlue-6, kOrange, kRed, kBlue-10, kYellow, kBlue+2]

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9], "ScaleYSize":2.5}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.7, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9], "ScaleYSize":1.2}

    return configdict
