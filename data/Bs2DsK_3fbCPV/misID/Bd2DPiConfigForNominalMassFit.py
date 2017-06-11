def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bd2DPi"
    configdict["CharmModes"] = {"KstK","NonRes","PhiPi"}
    #configdict["CharmModes"] = {"KPiPi"}
    # year of data taking                                                                                                                          
    configdict["YearOfDataTaking"] = {"2011", "2012"}
    # stripping (necessary in case of PIDK shapes)                                                                                              
    configdict["Stripping"] = {"2012":"21", "2011":"21r1"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)                                                                  
    configdict["IntegratedLuminosity"] = {"2011": {"Down": 0.59, "Up": 0.44}, "2012":{"Down": 0.9894, "Up": 0.9985}}
    # file name with paths to MC/data samples                                                                                                       
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/misID/config_Bd2DPi.txt"
    #settings for control plots                                                                                                                                                           
    configdict["ControlPlots"] = {}
    configdict["ControlPlots"] = { "Directory": "PlotBd2DPi", "Extension":"pdf"}

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5200,    5800    ], "InputName" : "lab0_MassHypo_DPi_DFav"} # for KKPi
    #configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5500,    6000    ], "InputName" : "lab0_MassHypo_DPi_DSup"} # for KPiPi - double misID
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1930,    2015    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-7.0,    6.0     ], "InputName" : "lab1_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.1,     1.0     ], "InputName" : "BDTGResponse_3"}

    # additional cuts applied to data sets             
    HLTcut = "(lab0_Hlt1TrackAllL0Decision_TOS == 1 && (lab0_Hlt2IncPhiDecision_TOS ==1 || lab0_Hlt2Topo2BodyBBDTDecision_TOS == 1 || lab0_Hlt2Topo3BodyBBDTDecision_TOS == 1))";
    Bsmass = "&&lab0_MassFitConsD_M >5300 && lab0_MassFitConsD_M <5800"

    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0&&lab1_PIDmu<2&&"+HLTcut+Bsmass, 
                                               "MC" :  "lab2_TAU>0&&lab1_M<200&&"+HLTcut+Bsmass, "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    configdict["AdditionalCuts"]["KKPi"]   = { "Data": "lab2_FDCHI2_ORIVX > 2", "MC" : "lab2_FDCHI2_ORIVX > 2"}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    configdict["AdditionalCuts"]["PiPiPi"] = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                               MDfit fitting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
    # Bs signal shapes                                                                                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5270.51}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":1.6878e+01,  "PhiPi":1.5228e+01,  "KstK":1.7260e+01,  "KPiPi":1.7791e+01,  "PiPiPi":1.7955e+01},  "Fixed":False}
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":1.1200e+01,  "PhiPi":1.2361e+01,  "KstK":1.1436e+01,  "KPiPi":1.1036e+01,  "PiPiPi":1.1608e+01},  "Fixed":False}
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":-2.0314e+00, "PhiPi":-1.7275e+00, "KstK":-2.2307e+00, "KPiPi":-2.5874e+00, "PiPiPi":-2.2449e+00}, "Fixed":False}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":1.6351e+00,  "PhiPi":1.5425e+00,  "KstK":2.1032e+00,  "KPiPi":2.3644e+00,  "PiPiPi":2.0136e+00},  "Fixed":False}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"NonRes":3.6820e+00,  "PhiPi":4.4322e+00,  "KstK":2.8836e+00,  "KPiPi":1.7676e+00,  "PiPiPi":2.7271e+00},  "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"NonRes":1.5081e+00,  "PhiPi":1.5073e+00,  "KstK":6.1945e-01,  "KPiPi":3.2020e-01,  "PiPiPi":6.7857e-01},  "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"NonRes":0.5,         "PhiPi":0.5,         "KstK":0.5,         "KPiPi":0.5,         "PiPiPi":0.5},  "Fixed":True}
    configdict["BsSignalShape"]["R"]       = {"Run1": {"NonRes":1.00,        "PhiPi":1.0,          "Kstk":1.0,        "KPiPi":1.0,         "PiPiPi":1.0}, "Fixed":False}

    #configdict["BsSignalShape"]["scaleSigma"] = { "2011": {"frac1": 1.22, "frac2":1.28}} 
    # combinatorial background                                                                                                                              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"]  = "Exponential"
    configdict["BsCombinatorialShape"]["cB"]   = {"Run1": {"NonRes":-3.5211e-03,  "PhiPi":-3.0873e-03,  "KstK":-2.3392e-03, "KPiPi":-1.0361e-03, "PiPiPi":-1.5277e-03},"Fixed": False}


    #expected yields                                                                                                                                                       
    configdict["Yields"] = {}
    #configdict["Yields"]["CombBkg"]         = {"2011": { "NonRes":10000.0, "PhiPi":10000.0, "KstK":10000.0, "KPiPi":10000.0, "PiPiPi":10000.0},
    #                                           "2012": { "NonRes":20000.0, "PhiPi":20000.0, "KstK":20000.0, "KPiPi":20000.0, "PiPiPi":20000.0},"Fixed":False}
    configdict["Yields"]["Signal"]          = {"2011": { "NonRes":10000.0, "PhiPi":10000.0, "KstK":10000.0, "KPiPi":10000.0, "PiPiPi":10000.0},
                                               "2012": { "NonRes":20000.0, "PhiPi":20000.0, "KstK":20000.0, "KPiPi":20000.0, "PiPiPi":20000.0},"Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#    
    ###                                                               MDfit plotting settings                                                             
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#               
    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = ["Sig"] #, "CombBkg"] 
    configdict["PlotSettings"]["colors"] = [kRed-7, kOrange]

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.60, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.375,0.875], "ScaleYSize":1.0}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.0, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.20,0.9], "ScaleYSize":1.2}

    return configdict
