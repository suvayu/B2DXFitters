def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bd2DPi"
    configdict["CharmModes"] = {"KPiPi"}
    # year of data taking                                                                                                                          
    configdict["YearOfDataTaking"] = {"2011"}
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
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5000,    5800    ], "InputName" : "lab0_MassFitConsD_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1830,    1920    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-7.0,    6.0     ], "InputName" : "lab1_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.0,     1.0     ], "InputName" : "BDTGResponse_2"} #Stefano (use new BDTG)

    # additional cuts applied to data sets                                                                                    
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0",            "MC" : "lab2_TAU>0&&lab1_M<200", "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}

    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                              
    # order of particles: KKPi, KPiPi, PiPiPi                                                                                                         
    configdict["DsChildrenPrefix"] = {"Child1":"lab3","Child2":"lab4","Child3": "lab5"}

    #weighting templates by PID eff/misID                                                                                                                                                 
    configdict["WeightingMassTemplates"] = {} #Stefano (PID MC-reweight not applied)
    #configdict["WeightingMassTemplates"] = { "Variables":["lab4_P","lab3_P"], "PIDBach": 0, "PIDChild": 0, "PIDProton": 5, "RatioDataMC":True }

    #Stefano (add Flavour Tagging variables (for Giulia and Stefano P.)) 
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
    
    # Bs signal shapes                                                                                                                                   
    configdict["BsSignalShape"] = {} #Stefano (fit all params)
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5283.}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"KPiPi":8.6},  "Fixed":False} 
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"KPiPi":14.5},  "Fixed":False} 
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"KPiPi":0.9},  "Fixed":False}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"KPiPi":-2.1}, "Fixed":False}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"KPiPi":1.8},  "Fixed":False}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"KPiPi":5.4},  "Fixed":False}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"KPiPi":0.25},  "Fixed":False}
    
    #Ds signal shapes                                                                                                                                       
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All":1869.8}, "Fixed":False}
    configdict["DsSignalShape"]["sigma1"]  = {"Run1": {"KPiPi":10.0}, "Fixed":False}
    configdict["DsSignalShape"]["sigma2"]  = {"Run1": {"KPiPi":5.6}, "Fixed":False}
    configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"KPiPi":1.7}, "Fixed":False}
    configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"KPiPi":-3.0},"Fixed":False}
    configdict["DsSignalShape"]["n1"]      = {"Run1": {"KPiPi":1.5}, "Fixed":False}
    configdict["DsSignalShape"]["n2"]      = {"Run1": {"KPiPi":0.6}, "Fixed":False}
    configdict["DsSignalShape"]["frac"]    = {"Run1": {"KPiPi":0.41}, "Fixed":False}

    # expected yields                                                                                                                                                       
    configdict["Yields"] = {}
    configdict["Yields"]["Signal"] = {"2011":{"KPiPi":100000.0}, "2012":{"KPiPi":200000.0},  "Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#    
    ###                                                               MDfit plotting settings                                                             
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#               
    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = ["Sig"]
    configdict["PlotSettings"]["colors"] = [kBlue+2]

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9]}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66], 
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075}

    return configdict
