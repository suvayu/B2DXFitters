def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # considered decay mode
    configdict["Decay"] = "Bs2DsK"
    configdict["CharmModes"] = {"NonRes","PhiPi","KstK","KPiPi","PiPiPi"} 
    # year of data taking
    configdict["YearOfDataTaking"] = {"2011"} 
    # stripping (necessary in case of PIDK shapes)
    configdict["Stripping"] = {"2011":"17"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes) 
    configdict["IntegratedLuminosity"] = {"2011": {"Down": 0.59, "Up": 0.44}}
    # file name with paths to MC/data samples
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsK.txt"
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5300,    5420    ], "InputName" : "lab0_MassFitConsD_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1930,    2015    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [1.61,    5.0     ], "InputName" : "lab1_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.3,     1.0     ], "InputName" : "BDTGResponse_1"}
    configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_TAGDECISION_OS"}
    configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_SS_nnetKaon_DEC"}
    configdict["BasicVariables"]["MistagOS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_TAGOMEGA_OS"}
    configdict["BasicVariables"]["MistagSS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_SS_nnetKaon_PROB"}

    # tagging calibration
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.3834, "p1": 0.9720, "average": 0.3813}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4244, "p1": 1.2180, "average": 0.4097}

    # additional cuts applied to data sets
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0",            "MC" : "lab2_TAU>0&&lab1_M>200", "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    configdict["AdditionalCuts"]["KKPi"]   = { "Data": "lab2_FDCHI2_ORIVX > 2", "MC" : "lab2_FDCHI2_ORIVX > 2"}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    configdict["AdditionalCuts"]["PiPiPi"] = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    
    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                     
    # order of particles: KKPi, KPiPi, PiPiPi                                
    configdict["DsChildrenPrefix"] = {"Child1":"lab5","Child2":"lab4","Child3": "lab3"}

    #weighting templates by PID eff/misID                                                                                                                                              
    configdict["WeightingMassTemplates"]= { "RatioDataMC":True }

    #Signal shapes                                                                                                                                             
    configdict["SignalShape"] = {}
    configdict["SignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["SignalShape"]["mean"]    = {"All":5367.51}
    configdict["SignalShape"]["sigma1"]  = {"2011": {"NonRes":1.0717e+01,  "PhiPi":1.1235e+01,  "KstK":1.0772e+01,  "KPiPi":1.1268e+01,  "PiPiPi":1.1391e+01}, "Fixed":False}
    configdict["SignalShape"]["sigma2"]  = {"2011": {"NonRes":1.6005e+01,  "PhiPi":1.7031e+01,  "KstK":1.5339e+01,  "KPiPi":1.9408e+01,  "PiPiPi":1.7647e+01}, "Fixed":False}
    configdict["SignalShape"]["alpha1"]  = {"2011": {"NonRes":2.2118e+00,  "PhiPi":2.2144e+00,  "KstK":2.0480e+00,  "KPiPi":2.3954e+00,  "PiPiPi":2.0930e+00}, "Fixed":True}
    configdict["SignalShape"]["alpha2"]  = {"2011": {"NonRes":-2.4185e+00, "PhiPi":-2.1918e+00, "KstK":-2.0291e+00, "KPiPi":-3.4196e+00, "PiPiPi":-2.3295e+00}, "Fixed":True}
    configdict["SignalShape"]["n1"]      = {"2011": {"NonRes":1.0019e+00,  "PhiPi":1.1193e+00,  "KstK":1.2137e+00,  "KPiPi":9.8202e-01,  "PiPiPi":1.2674e+00}, "Fixed":True}
    configdict["SignalShape"]["n2"]      = {"2011": {"NonRes":3.1469e+00,  "PhiPi":3.6097e+00,  "KstK":6.5735e+00,  "KPiPi":5.2237e-01,  "PiPiPi":4.0195e+00}, "Fixed":True}
    configdict["SignalShape"]["frac"]    = {"2011": {"NonRes":6.1755e-01,  "PhiPi":7.0166e-01,  "KstK":5.8012e-01,  "KPiPi":7.8103e-01,  "PiPiPi":7.0398e-01}, "Fixed":True}

    # Bs signal shapes                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["BsSignalShape"]["mean"]    = {"All":5367.51}
    configdict["BsSignalShape"]["sigma1"]  = {"2011": {"NonRes":1.0717e+01,  "PhiPi":1.1235e+01,  "KstK":1.0772e+01,  "KPiPi":1.1268e+01,  "PiPiPi":1.1391e+01}, "Fixed":True}
    configdict["BsSignalShape"]["sigma2"]  = {"2011": {"NonRes":1.6005e+01,  "PhiPi":1.7031e+01,  "KstK":1.5339e+01,  "KPiPi":1.9408e+01,  "PiPiPi":1.7647e+01}, "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"2011": {"NonRes":2.2118e+00,  "PhiPi":2.2144e+00,  "KstK":2.0480e+00,  "KPiPi":2.3954e+00,  "PiPiPi":2.0930e+00}, "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"2011": {"NonRes":-2.4185e+00, "PhiPi":-2.1918e+00, "KstK":-2.0291e+00, "KPiPi":-3.4196e+00, "PiPiPi":-2.3295e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"2011": {"NonRes":1.0019e+00,  "PhiPi":1.1193e+00,  "KstK":1.2137e+00,  "KPiPi":9.8202e-01,  "PiPiPi":1.2674e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"2011": {"NonRes":3.1469e+00,  "PhiPi":3.6097e+00,  "KstK":6.5735e+00,  "KPiPi":5.2237e-01,  "PiPiPi":4.0195e+00}, "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"2011": {"NonRes":6.1755e-01,  "PhiPi":7.0166e-01,  "KstK":5.8012e-01,  "KPiPi":7.8103e-01,  "PiPiPi":7.0398e-01}, "Fixed":True}

    #Ds signal shapes                                                                                                
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["DsSignalShape"]["mean"]    = {"All":1968.49}
    configdict["DsSignalShape"]["sigma1"]  = {"2011": {"NonRes":5.3468e+00,  "PhiPi":8.2412e+00,  "KstK":6.0845e+00,  "KPiPi":8.8531e+00,  "PiPiPi":8.0860e+00}, "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"2011": {"NonRes":5.1848e+00,  "PhiPi":4.4944e+00,  "KstK":5.1266e+00,  "KPiPi":5.2073e+00,  "PiPiPi":7.3773e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"2011": {"NonRes":1.2252e+00,  "PhiPi":1.9827e+00,  "KstK":1.1316e+00,  "KPiPi":1.7131e+00,  "PiPiPi":9.0639e-01}, "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"2011": {"NonRes":-1.1167e+00, "PhiPi":-3.0525e+00, "KstK":-1.3760e+00, "KPiPi":-2.5276e+00, "PiPiPi":-1.1122e+00}, "Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"2011": {"NonRes":4.6625e+00,  "PhiPi":1.4867e+00,  "KstK":1.3280e+01,  "KPiPi":2.0239e+00,  "PiPiPi":1.1486e+01}, "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"2011": {"NonRes":6.9989e+01,  "PhiPi":6.1022e-01,  "KstK":1.1017e+01,  "KPiPi":1.0860e+00,  "PiPiPi":4.0001e+01}, "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"2011": {"NonRes":4.7565e-01,  "PhiPi":3.9628e-01,  "KstK":4.0048e-01,  "KPiPi":5.5084e-01,  "PiPiPi":4.8729e-01}, "Fixed":True}

    #expected yields                                                                          
    configdict["Yields"] = {}
    configdict["Yields"]["Signal"] = {"2011": {"NonRes":500000.0,  "PhiPi":500000.0, "KstK":500000.0, "KPiPi":500000.0, "PiPiPi":500000.0} , "Fixed":False}


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
