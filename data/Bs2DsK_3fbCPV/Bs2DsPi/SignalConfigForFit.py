def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # considered decay mode
    configdict["Decay"] = "Bs2DsPi"
    configdict["CharmModes"] = {"PiPiPi"} #"NonRes","PhiPi","KstK","KPiPi","PiPiPi"} 
    # year of data taking
    configdict["YearOfDataTaking"] = {"2011"} 
    # stripping (necessary in case of PIDK shapes)
    configdict["Stripping"] = {"2011":"21r1","2012":"21"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes) 
    configdict["IntegratedLuminosity"] = {"2011": {"Down": 1.00, "Up": 1.0}, "2012":{"Down": 0.9894, "Up": 0.9985}} #0.59, 0.44
    # file name with paths to MC/data samples
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/Bs2DsPi/config_Bs2DsPi.txt"
    #settings for control plots 
    configdict["ControlPlots"] = {} 
    configdict["ControlPlots"] = { "Directory": "PlotBs2DsPi", "Extension":"pdf"} 
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5300,    5600    ], "InputName" : "lab0_MassFitConsD_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1930,    2015    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-7.0,    0.0     ], "InputName" : "lab1_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [-0.0,     1.0    ], "InputName" : "BDTGResponse_2"}

    # additional cuts applied to data sets
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0",            "MC" : "lab2_TAU>0&&lab1_M<200", "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    configdict["AdditionalCuts"]["KKPi"]   = { "Data": "lab2_FDCHI2_ORIVX > 2", "MC" : "lab2_FDCHI2_ORIVX > 2"}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    configdict["AdditionalCuts"]["PiPiPi"] = { "Data": "lab2_FDCHI2_ORIVX > 9&&lab45_MM<1700", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    
    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                     
    # order of particles: KKPi, KPiPi, PiPiPi                                
    configdict["DsChildrenPrefix"] = {"Child1":"lab3","Child2":"lab4","Child3": "lab5"}

    #weighting templates by PID eff/misID
    configdict["WeightingMassTemplates"]= { "PIDBachEff":            { "FileLabel": { "2011":"#PID Pion 2011", "2012":"#PID Pion 2012"},
                                                                       "Var":"lab1_P", "HistName":"MyPionEff_0"},
                                            "PIDBachMisID":          { "FileLabel": { "2011":"#PID Pion 2011", "2012":"#PID Pion 2012"},
                                                                       "Var":"lab1_P", "HistName":"MyPionMisID_0"},
                                            "PIDChildKaonPionMisID": { "FileLabel": { "2011":"#PID Pion 2011", "2012":"#PID Pion 2012"},
                                                                       "Var":"lab3_P", "HistName":"MyPionMisID_0"},
                                            "PIDChildProtonMisID":   { "FileLabel": { "2011":"#PID Proton 2011", "2012":"#PID Proton 2012"},
                                                                       "Var":"lab4_P", "HistName":"MyProtonMisID_pKm5_KPi5"},
                                            "RatioDataMC":True,
                                            "Shift":{ "BeautyMass": -2.0, "CharmMass": 0.0} }

    
    #weighting for PID templates
    configdict["ObtainPIDTemplates"] = { "Variables":["BacPT","nTracks"], "Bins":[20,20] }

    
    # Bs signal shapes                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5367.51}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"All":1.0717e+01}, "Fixed":False}
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"All":1.6005e+01}, "Fixed":False}
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"All":2.2118e+00}, "Fixed":False}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"All":-2.4185e+00}, "Fixed":False}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"All":10.0}, "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"All":10.0}, "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"All":0.5}, "Fixed":True}

    #Ds signal shapes                                                                                                
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All":1968.49}, "Fixed":False}
    configdict["DsSignalShape"]["sigma1"]  = {"Run1": {"KKPi":5.3468e+00,  "KPiPi":8.8531e+00,  "PiPiPi":8.0860e+00}, "Fixed":False}
    configdict["DsSignalShape"]["sigma2"]  = {"Run1": {"KKPi":5.1848e+00,  "KPiPi":5.2073e+00,  "PiPiPi":7.3773e+00}, "Fixed":False}
    #configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"KKPi":1.2252e+00,  "KPiPi":1.7131e+00,  "PiPiPi":9.0639e-01}, "Fixed":False}
    #configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"KKPi":-1.1167e+00, "KPiPi":-2.5276e+00, "PiPiPi":-1.1122e+00}, "Fixed":False}
    configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"KKPi":1.1289e+00,  "KPiPi":1.5928e+00,  "PiPiPi": 8.0885e-01}, "Fixed":False}
    configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"KKPi":-1.1200e+00, "KPiPi":-4.6258e+00, "PiPiPi":-1.2172e+00}, "Fixed":False}
    configdict["DsSignalShape"]["n1"]      = {"Run1": {"KKPi":4.6625e+00,  "KPiPi":2.0239e+00,  "PiPiPi":10.0}, "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"Run1": {"KKPi":6.9989e+01,  "KPiPi":1.0860e+00,  "PiPiPi":10.0}, "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"Run1": {"KKPi":4.7565e-01,  "KPiPi":5.5084e-01,  "PiPiPi":0.5}, "Fixed":True}

    #expected yields                                                                                                                                                              
    configdict["Yields"] = {}
    configdict["Yields"]["Signal"]  = {"2011": {"NonRes":50000.0,  "PhiPi":50000.0, "KstK":50000.0, "KPiPi":50000.0, "PiPiPi":50000.0},
                                       "2012": {"NonRes":50000.0,  "PhiPi":50000.0, "KstK":50000.0, "KPiPi":50000.0, "PiPiPi":50000.0}, "Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#            
    ###                                                               MDfit plotting settings                                                                                 
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------# 
 
    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = { "EPDF": ["Sig"],
                                                 "PDF":  ["Sig"],
                                                 "Legend": ["Sig"]}
    configdict["PlotSettings"]["colors"] = { "PDF": [kBlue+2],
                                             "Legend": [kBlue+2]}

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9]}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66], 
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075}

    return configdict
