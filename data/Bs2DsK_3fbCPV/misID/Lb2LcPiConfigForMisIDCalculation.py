def getconfig() :




    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Lb2LcPi"
    configdict["CharmModes"] = {"KstK","NonRes","PhiPi"}
    #configdict["CharmModes"] = {"KPiPi"}
    # year of data taking                                                                                                                          
    configdict["YearOfDataTaking"] = {"2011", "2012"}
    # stripping (necessary in case of PIDK shapes)                                                                                              
    configdict["Stripping"] = {"2012":"21", "2011":"21r1"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)                                                                  
    configdict["IntegratedLuminosity"] = {"2011": {"Down": 0.59, "Up": 0.44}, "2012":{"Down": 0.9894, "Up": 0.9985}}
    # file name with paths to MC/data samples                                                                                                       
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/misID/config_ExpectedEvents.txt"
    #settings for control plots                                                                                                                                                           
    configdict["ControlPlots"] = {}
    configdict["ControlPlots"] = { "Directory": "PlotLb2LcPiNewPID", "Extension":"pdf"}

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5300,    5800    ], "InputName" : "lab0_MassFitConsD_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1930,    2015    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-7.0,    6.0     ], "InputName" : "lab1_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.0,     1.0     ], "InputName" : "BDTGResponse_2"}

    # additional cuts applied to data sets                                                                                    
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0",            "MC" : "lab2_TAU>0&&lab1_M<200", "DsHypo":True}
    configdict["AdditionalCuts"]["KKPi"]   = { "Data": "", "MC":"lab34_MM<1840 && lab2_FDCHI2_ORIVX > 2 && lab2_FD_ORIVX > 0"}
    configdict["AdditionalCuts"]["NonRes"] = { "Data": "", "MC": "((!(abs(lab34_MM-1020)<20)) && (!(abs(lab45_MM-892.0) < 50.)))"}
    configdict["AdditionalCuts"]["PhiPi"]  = { "Data": "", "MC": "abs(lab34_MM-1020)<20"}
    configdict["AdditionalCuts"]["NonRes"] = { "Data": "", "MC": "((!(abs(lab34_MM-1020)<20 )) && ((abs(lab45_MM-892.0) < 50.)))"}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "", "MC" : "lab34_MM < 1750 && lab2_FDCHI2_ORIVX > 9 && lab2_FD_ORIVX > 0"}

    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                                                    
    # order of particles: KKPi, KPiPi, PiPiPi                                                                                                                                                  
    configdict["DsChildrenPrefix"] = {"Child1":"lab3","Child2":"lab4","Child3": "lab5"}


    return configdict
