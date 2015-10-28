def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # considered decay mode
    configdict["Decay"] = "Bs2DsK"
    configdict["CharmModes"] = {"NonRes","PhiPi","KstK","KPiPi","PiPiPi"} 
    # year of data taking
    configdict["YearOfDataTaking"] = {"2011","2012"} 
    # stripping (necessary in case of PIDK shapes)
    configdict["Stripping"] = {"2011":"21r1","2012":"21"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes) 
    configdict["IntegratedLuminosity"] = {"2011": {"Down": 0.59, "Up": 0.44}}
    # file name with paths to MC/data samples
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/Bs2DsK/config_Bs2DsK.txt"
    #settings for control plots 
    configdict["ControlPlots"] = {} 
    configdict["ControlPlots"] = { "Directory": "PlotBs2DsK", "Extension":"C"} 
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5300,    5800    ], "InputName" : "lab0_MassFitConsD_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1930,    2015    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [1.61,    5.0     ], "InputName" : "lab1_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.3,     1.0     ], "InputName" : "BDTGResponse_1"}
    #configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_TAGDECISION_OS"}
    #configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_SS_nnetKaon_DEC"}
    #configdict["BasicVariables"]["MistagOS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_TAGOMEGA_OS"}
    #configdict["BasicVariables"]["MistagSS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_SS_nnetKaon_PROB"}

    # tagging calibration
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.3834, "p1": 0.9720, "average": 0.3813}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4244, "p1": 1.2180, "average": 0.4097}

    # additional cuts applied to data sets
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0",            "MC" : "lab2_TAU>0&&lab1_M>200", "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    configdict["AdditionalCuts"]["KKPi"]   = { "Data": "lab2_FDCHI2_ORIVX > 2", "MC" : "lab2_FDCHI2_ORIVX > 2"}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    configdict["AdditionalCuts"]["PiPiPi"] = { "Data": "lab2_FDCHI2_ORIVX > 9&&lab45_MM<1700", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    
    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                     
    # order of particles: KKPi, KPiPi, PiPiPi                                
    configdict["DsChildrenPrefix"] = {"Child1":"lab5","Child2":"lab4","Child3": "lab3"}

    #weighting templates by PID eff/misID
    configdict["WeightingMassTemplates"]= { "Variables":["lab4_P","lab5_P"], "PIDBach": 5, "PIDChild": 0, "PIDProton": 5, "RatioDataMC":True }
    
    #weighting for PID templates
    configdict["ObtainPIDTemplates"] = { "Variables":["BacPT","nTracks"], "Bins":[20,20] }

    configdict["Calibrations"] = {}
    configdict["Calibrations"]["2011"] = {}
    configdict["Calibrations"]["2011"]["Pion"]   = {}
    configdict["Calibrations"]["2011"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID5_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID5_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]   = {}
    configdict["Calibrations"]["2011"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID5_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID5_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Proton"]   = {}
    configdict["Calibrations"]["2011"]["Proton"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibLam_Up_P_PID5_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Proton"]["Down"] = { "FileName": "/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibLam_Down_P_PID5_Str21r1.root"}

    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_Up_DsK_5358.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_Down_DsK_5358.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    
    configdict["Calibrations"]["2012"] = {}
    configdict["Calibrations"]["2012"]["Pion"]   = {}
    configdict["Calibrations"]["2012"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID5_Str20.root"}
    configdict["Calibrations"]["2012"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID5_Str20.root"}
    configdict["Calibrations"]["2012"]["Kaon"]   = {}
    configdict["Calibrations"]["2012"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID5_Str20.root"}
    configdict["Calibrations"]["2012"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID5_Str20.root"}
    configdict["Calibrations"]["2012"]["Proton"]   = {}
    configdict["Calibrations"]["2012"]["Proton"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibLam_Up_P_PID5_Str21.root"}
    configdict["Calibrations"]["2012"]["Proton"]["Down"] = { "FileName": "/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibLam_Down_P_PID5_Str21.root"}

    configdict["Calibrations"]["2012"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_Up_DsK_5358.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_Down_DsK_5358.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}

    
    # Bs signal shapes                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5367.51}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":1.0717e+01,  "PhiPi":1.1235e+01,  "KstK":1.0772e+01,  "KPiPi":1.1268e+01,  "PiPiPi":1.1391e+01}, "Fixed":True}
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":1.6005e+01,  "PhiPi":1.7031e+01,  "KstK":1.5339e+01,  "KPiPi":1.9408e+01,  "PiPiPi":1.7647e+01}, "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":2.2118e+00,  "PhiPi":2.2144e+00,  "KstK":2.0480e+00,  "KPiPi":2.3954e+00,  "PiPiPi":2.0930e+00}, "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":-2.4185e+00, "PhiPi":-2.1918e+00, "KstK":-2.0291e+00, "KPiPi":-3.4196e+00, "PiPiPi":-2.3295e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"NonRes":1.0019e+00,  "PhiPi":1.1193e+00,  "KstK":1.2137e+00,  "KPiPi":9.8202e-01,  "PiPiPi":1.2674e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"NonRes":3.1469e+00,  "PhiPi":3.6097e+00,  "KstK":6.5735e+00,  "KPiPi":5.2237e-01,  "PiPiPi":4.0195e+00}, "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"NonRes":6.1755e-01,  "PhiPi":7.0166e-01,  "KstK":5.8012e-01,  "KPiPi":7.8103e-01,  "PiPiPi":7.0398e-01}, "Fixed":True}
    configdict["BsSignalShape"]["scaleSigma"] = { "Run1": {"frac1": 1.22, "frac2":1.28}}

    #Ds signal shapes                                                                                                
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All":1968.49}, "Fixed":False}
    configdict["DsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":5.3468e+00,  "PhiPi":8.2412e+00,  "KstK":6.0845e+00,  "KPiPi":8.8531e+00,  "PiPiPi":8.0860e+00}, "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":5.1848e+00,  "PhiPi":4.4944e+00,  "KstK":5.1266e+00,  "KPiPi":5.2073e+00,  "PiPiPi":7.3773e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":1.2252e+00,  "PhiPi":1.9827e+00,  "KstK":1.1316e+00,  "KPiPi":1.7131e+00,  "PiPiPi":9.0639e-01}, "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":-1.1167e+00, "PhiPi":-3.0525e+00, "KstK":-1.3760e+00, "KPiPi":-2.5276e+00, "PiPiPi":-1.1122e+00}, "Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"Run1": {"NonRes":4.6625e+00,  "PhiPi":1.4867e+00,  "KstK":1.3280e+01,  "KPiPi":2.0239e+00,  "PiPiPi":1.1486e+01}, "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"Run1": {"NonRes":6.9989e+01,  "PhiPi":6.1022e-01,  "KstK":1.1017e+01,  "KPiPi":1.0860e+00,  "PiPiPi":4.0001e+01}, "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"Run1": {"NonRes":4.7565e-01,  "PhiPi":3.9628e-01,  "KstK":4.0048e-01,  "KPiPi":5.5084e-01,  "PiPiPi":4.8729e-01}, "Fixed":True}
    configdict["DsSignalShape"]["scaleSigma"] = { "Run1": {"frac1": 1.16, "frac2":1.19}}
 
    # combinatorial background                                                                              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"] = "Exponential"
    configdict["BsCombinatorialShape"]["cB"]   = {"Run1":{"NonRes":-1.1530e-03,  "PhiPi":-9.2354e-04,  "KstK":-1.3675e-03, "KPiPi":-9.8158e-04, "PiPiPi":-1.0890e-03}, "Fixed":False}

    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]    = "ExponentialPlusSignal"
    configdict["DsCombinatorialShape"]["cD"]      = {"Run1": {"NonRes":-4.4329e-03,  "PhiPi":-8.8642e-03,  "KstK":-5.2652e-03, "KPiPi":-1.0743e-03, "PiPiPi":-1.1877e-03}, 
                                                     "Fixed":False}
    configdict["DsCombinatorialShape"]["fracD"]   = {"Run1": {"NonRes":4.3067e-01,   "PhiPi":6.5400e-01,   "KstK":3.7409e-01,  "KPiPi":1.0,         "PiPiPi":1.0},         
                                                     "Fixed":{"KPiPi":True, "PiPiPi":True}}
    
    configdict["PIDKCombinatorialShape"] = {}
    configdict["PIDKCombinatorialShape"]["type"] = "Fixed"
    configdict["PIDKCombinatorialShape"]["components"] = { "Kaon":True, "Pion":True, "Proton":True }
    configdict["PIDKCombinatorialShape"]["fracPIDK1"]   = { "2011":{"All":0.5}, "2012":{"All":0.5}, "Fixed":False }
    configdict["PIDKCombinatorialShape"]["fracPIDK2"]   = { "2011":{"All":0.5}, "2012":{"All":0.5}, "Fixed":False }

    #Bd2Dsh background                                                                                           
    #shape for BeautyMass, for CharmMass as well as BacPIDK taken by default the same as signal                                                                
    configdict["Bd2Ds(st)XShape"] = {}
    configdict["Bd2Ds(st)XShape"]["type"]    = "ShiftedSignal"
    configdict["Bd2Ds(st)XShape"]["decay"]   = "Bd2DsK"
    configdict["Bd2Ds(st)XShape"]["shift"]   = {"Run1": {"All": 86.8}, "Fixed":True}
    configdict["Bd2Ds(st)XShape"]["scale1"]  = {"Run1": {"All": 0.998944636665}, "Fixed":True}
    configdict["Bd2Ds(st)XShape"]["scale2"]  = {"Run1": {"All": 1.00022181515}, "Fixed":True}

    #                                                                                                                                                                                 
    configdict["AdditionalParameters"] = {}
    configdict["AdditionalParameters"]["g1_f1_frac"] = {"2011":{"All":{"Both":{ "CentralValue":1.0, "Range":[0.0,1.0]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["g2_f1_frac"] = {"2011":{"All":{"Both":{ "CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["g2_f2_frac"] = {"2011":{"All":{"Both":{ "CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["g3_f1_frac"] = {"2011":{"All":{"Both":{ "CentralValue":0.75,"Range":[0.0,1.0]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["g5_f1_frac"] = {"2011":{"All":{"Both":{ "CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed":False}

    #expected yields                                                                                                                                                              
    configdict["Yields"] = {}
    configdict["Yields"]["Bd2DPi"]             = {"2011": {"NonRes":14.0,    "PhiPi":0.0,    "KstK":3.0,    "KPiPi":3.0,    "PiPiPi":0.0},      "Fixed":True}
    configdict["Yields"]["Bd2DK"]              = {"2011": {"NonRes":17.0,    "PhiPi":0.0,    "KstK":5.0,    "KPiPi":0.0,    "PiPiPi":0.0},      "Fixed":True}
    configdict["Yields"]["Lb2LcPi"]            = {"2011": {"NonRes":11.0,    "PhiPi":1.0,    "KstK":3.0,    "KPiPi":0.0,    "PiPiPi":0.0},      "Fixed":True}
    configdict["Yields"]["Lb2LcK"]             = {"2011": {"NonRes":15.0,    "PhiPi":2.0,    "KstK":4.0,    "KPiPi":0.0,    "PiPiPi":0.0},      "Fixed":True}
    configdict["Yields"]["Bs2DsDsstKKst"]      = {"2011": {"NonRes":50.0,    "PhiPi":50.0,   "KstK":50.0,   "KPiPi":50.0,   "PiPiPi":50.0},     "Fixed":False}
    configdict["Yields"]["BsLb2DsDsstPPiRho"]  = {"2011": {"NonRes":225.0,   "PhiPi":500.0,  "KstK":330.0,  "KPiPi":90.0,   "PiPiPi":260.0},    "Fixed":False}
    configdict["Yields"]["CombBkg"]            = {"2011": {"NonRes":1000.0,  "PhiPi":1000.0, "KstK":1000.0, "KPiPi":1000.0, "PiPiPi":10000.0},  "Fixed":False}
    configdict["Yields"]["Signal"]             = {"2011": {"NonRes":1000.0,  "PhiPi":1000.0, "KstK":1000.0, "KPiPi":1000.0, "PiPiPi":10000.0} , "Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#            
    ###                                                               MDfit plotting settings                                                                                 
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------# 
 
    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = { "EPDF": ["Sig", "CombBkg", "Lb2LcK", "Lb2LcPi", "Bd2DK", "Bd2DPi","BsLb2DsDsstPPiRho", "Bs2DsDsstKKst"],
                                                 "PDF":  ["Sig", "CombBkg", "Lb2LcK", "Lb2LcPi", "Lb2DsDsstP", "Bs2DsDsstPiRho", "Bd2DK", "Bd2DPi","Bs2DsDsstKKst"],
                                                 "Legend": ["Sig", "CombBkg", "Lb2LcKPi", "Lb2DsDsstP", "Bs2DsDsstPiRho", "Bd2DKPi","Bs2DsDsstKKst"]}
    configdict["PlotSettings"]["colors"] = { "PDF": [kRed-7, kMagenta-2, kGreen-3, kGreen-3, kYellow-9, kBlue-6, kRed, kRed, kBlue-10],
                                             "Legend": [kRed-7, kMagenta-2, kGreen-3, kYellow-9, kBlue-6, kRed, kBlue-10]}

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9]}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66], 
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075}

    return configdict
