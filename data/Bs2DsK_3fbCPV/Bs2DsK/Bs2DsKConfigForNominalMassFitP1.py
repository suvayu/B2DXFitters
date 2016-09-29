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
    configdict["IntegratedLuminosity"] = {"2011": {"Down":  0.56, "Up": 0.42}, "2012":{"Down": 0.9912, "Up": 0.9988}}
    # file name with paths to MC/data samples
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/Bs2DsK/config_Bs2DsK_newBDTG_filtered.txt"
    #settings for control plots 
    configdict["ControlPlots"] = {} 
    configdict["ControlPlots"] = { "Directory": "PlotBs2DsK_BsP1", "Extension":"pdf"} 
        
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
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [ 0.1,    1.0     ], "InputName" : "BDTGResponse_3"}
    configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_TAGDECISION_OS"}
    configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_SS_nnetKaon_DEC"}
    configdict["BasicVariables"]["MistagOS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_TAGOMEGA_OS"}
    configdict["BasicVariables"]["MistagSS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_SS_nnetKaon_PROB"}

    # tagging calibration
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.3834, "p1": 0.9720, "average": 0.3813}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4244, "p1": 1.2180, "average": 0.4097}

    HLTcut = "&&(lab0_Hlt1TrackAllL0Decision_TOS && (lab0_Hlt2IncPhiDecision_TOS ==1 || lab0_Hlt2Topo2BodyBBDTDecision_TOS == 1 || lab0_Hlt2Topo3BodyBBDTDecision_TOS == 1))"
    # additional cuts applied to data sets
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab0_P<120000&&lab2_TAU>0&&lab1_PIDmu<2"+HLTcut,            
                                               "MC" : "lab0_P<120000&&lab2_TAU>0&&lab1_M>200&&lab1_PIDK !=-1000.0"+HLTcut, "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    configdict["AdditionalCuts"]["KKPi"]   = { "Data": "lab2_FDCHI2_ORIVX > 2", "MC" : "lab2_FDCHI2_ORIVX > 2"}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    configdict["AdditionalCuts"]["PiPiPi"] = { "Data": "lab2_FDCHI2_ORIVX > 9&&lab45_MM<1700", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    
    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                     
    # order of particles: KKPi, KPiPi, PiPiPi                                
    configdict["DsChildrenPrefix"] = {"Child1":"lab3","Child2":"lab4","Child3": "lab5"}

    #weighting templates by PID eff/misID
    configdict["WeightingMassTemplates"]= { "PIDBachEff":            { "FileLabel": { "2011":"#PIDK Kaon 2011", "2012":"#PIDK Kaon 2012"},
                                                                       "Var":["nTracks","lab1_P"], "HistName":"MyKaonEff_5_mu2"},
                                            "PIDBachMisID":          { "FileLabel": { "2011":"#PIDK Pion 2011", "2012":"#PIDK Pion 2012"},
                                                                       "Var":["nTracks","lab1_P"], "HistName":"MyPionMisID_5_mu2"},
                                            "PIDBachProtonMisID":    { "FileLabel": { "2011":"#PIDK Proton 2011", "2012":"#PIDK Proton 2012"},
                                                                       "Var":["nTracks","lab1_P"], "HistName":"MyProtonEff_K5_mu2"},
                                            "PIDChildKaonPionMisID": { "FileLabel": { "2011":"#PIDK Pion 2011", "2012":"#PIDK Pion 2012"},
                                                                       "Var":["nTracks","lab3_P"], "HistName":"MyPionMisID_0"},
                                            "PIDChildProtonMisID":   { "FileLabel": { "2011":"#PIDK Proton 2011", "2012":"#PIDK Proton 2012"},
                                                                       "Var":["nTracks","lab4_P"], "HistName":"MyProtonMisID_pKm5_KPi5"},
                                            "RatioDataMC": {"FileLabel": {"2011":"#RatioDataMC 2011 PTnTr Filtered", "2012": "#RatioDataMC 2012 PTnTr Filtered"},
                                                            "Var":["lab1_PT","nTracks"], "HistName":"histRatio"},
                                            "Shift":{ "BeautyMass": -2.0, "CharmMass": 0.0} }

    
    #weighting for PID templates
    configdict["ObtainPIDTemplates"] = { "Variables":["BacPT","nTracks"], "Bins":[30,30] }

    configdict["Calibrations"] = {}
    configdict["Calibrations"]["2011"] = {}
    configdict["Calibrations"]["2011"]["Pion"]   = {}
    configdict["Calibrations"]["2011"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID5_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID5_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]   = {}
    configdict["Calibrations"]["2011"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID5_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID5_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Proton"]   = {}
    configdict["Calibrations"]["2011"]["Proton"]["Up"] = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_P_PID5_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Proton"]["Down"] = { "FileName": "root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_P_PID5_Str21r1.root"}

    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { #"FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsK_2011.root",
                                                                  "FileName":"/afs/cern.ch/user/a/adudziak/roofit/MDFitter/3fb/PIDK_combo/workspaces/work_Comb_DsK_Run1_BDTG3_BsP1.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up_2011", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["BacPT","nTracks"]}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { #"FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsK_2011.root",
                                                                    "FileName":"/afs/cern.ch/user/a/adudziak/roofit/MDFitter/3fb/PIDK_combo/workspaces/work_Comb_DsK_Run1_BDTG3_BsP1.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down_2011", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["BacPT","nTracks"]}
    
    configdict["Calibrations"]["2012"] = {}
    configdict["Calibrations"]["2012"]["Pion"]   = {}
    configdict["Calibrations"]["2012"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID5_Str21.root"}
    configdict["Calibrations"]["2012"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID5_Str21.root"}
    configdict["Calibrations"]["2012"]["Kaon"]   = {}
    configdict["Calibrations"]["2012"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID5_Str21.root"}
    configdict["Calibrations"]["2012"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID5_Str21.root"}
    configdict["Calibrations"]["2012"]["Proton"]   = {}
    configdict["Calibrations"]["2012"]["Proton"]["Up"] = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_P_PID5_Str21.root"}
    configdict["Calibrations"]["2012"]["Proton"]["Down"] = { "FileName": "root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Down_P_PID5_Str21r1.root"}

    configdict["Calibrations"]["2012"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Up"] = { #"FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsK_2012.root",
                                                                  "FileName":"/afs/cern.ch/user/a/adudziak/roofit/MDFitter/3fb/PIDK_combo/workspaces/work_Comb_DsK_Run1_BDTG3_BsP1.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up_2012", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["BacPT","nTracks"]}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Down"] = { #"FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsK_2012.root",
                                                                    "FileName":"/afs/cern.ch/user/a/adudziak/roofit/MDFitter/3fb/PIDK_combo/workspaces/work_Comb_DsK_Run1_BDTG3_BsP1.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down_2012", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["BacPT","nTracks"]}

    
    # Bs signal shapes                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5367.51}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":1.4951e+01,  "PhiPi":1.5170e+01,  "KstK":1.4965e+01,  "KPiPi":1.5357e+01,  "PiPiPi":1.5698e+01},  "Fixed":True}
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":1.0571e+01,  "PhiPi":1.0421e+01,  "KstK":1.0192e+01,  "KPiPi":1.0379e+01,  "PiPiPi":1.0353e+01},  "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":-2.1949e+00, "PhiPi":-2.2191e+00, "KstK":-2.4113e+00, "KPiPi":-2.3033e+00, "PiPiPi":-2.4350e+00}, "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":1.9928e+00,  "PhiPi":2.2044e+00,  "KstK":1.8828e+00,  "KPiPi":2.1347e+00,  "PiPiPi":2.0052e+00},  "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"NonRes":2.8475e+00,  "PhiPi":2.8782e+00,  "KstK":2.5325e+00,  "KPiPi":3.0966e+00,  "PiPiPi":2.8920e+00},  "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"NonRes":1.0686e+00,  "PhiPi":7.3809e-01,  "KstK":1.2195e+00,  "KPiPi":6.8990e-01,  "PiPiPi":9.2581e-01},  "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"NonRes":0.5,         "PhiPi":0.5,         "KstK":0.5,         "KPiPi":0.5,         "PiPiPi":0.5},         "Fixed":True}
    configdict["BsSignalShape"]["R"]       = {"Run1": {"NonRes":1.0225e+00,  "PhiPi":1.0166e+00,  "Kstk":1.0112e+00,  "KPiPi":1.0383e+00,  "PiPiPi":1.0033e+00},  "Fixed":False}

    #Ds signal shapes                                                                                                
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All":1968.49}, "Fixed":False}
    configdict["DsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":4.2549e+00,  "PhiPi":5.1372e+00,   "KstK":4.7236e+00,  "KPiPi":6.5756e+00,  "PiPiPi":9.5309e+00},  "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":7.4230e+00,  "PhiPi":5.1670e+00,   "KstK":7.4875e+00,  "KPiPi":6.8750e+00,  "PiPiPi":6.7475e+00},  "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":-2.2029e+00, "PhiPi":-1.2110e+00,  "KstK":-2.5316e+00, "KPiPi":-1.3980e+00, "PiPiPi":-1.5088e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":1.9603e+00,  "PhiPi":1.3148e+00,   "KstK":1.8138e+00,  "KPiPi":1.2792e+00,  "PiPiPi":1.6718e+00},  "Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"Run1": {"NonRes":1.3526e+00,  "PhiPi":9.2680e+00,   "KstK":9.0913e-01,  "KPiPi":6.6983e+00,  "PiPiPi":5.0000e+01},  "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"Run1": {"NonRes":1.3801e+00,  "PhiPi":3.7056e+00,   "KstK":2.7012e+00,  "KPiPi":3.3650e+00,  "PiPiPi":9.6257e-01},  "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"Run1": {"NonRes":0.50,        "PhiPi":0.50,         "KstK":0.5,         "KPiPi":0.5,         "PiPiPi":0.5},         "Fixed":True}
    configdict["DsSignalShape"]["R"]       = {"Run1": {"NonRes":1.05000000,  "PhiPi":1.0562e+00,   "KstK":1.0715e+00,  "KPiPi":1.0365e+00,  "PiPiPi":1.0837e+00}, "Fixed":False}


    # combinatorial background                                                                              
    configdict["BsCombinatorialShape"] = {}
    #configdict["BsCombinatorialShape"]["type"] = "Exponential"
    #configdict["BsCombinatorialShape"]["cB"]   = {"Run1":{"NonRes":-1.1530e-02,  "PhiPi":-9.2354e-03,  "KstK":-1.3675e-02, "KPiPi":-9.8158e-03, "PiPiPi":-1.0890e-03}, "Fixed":False}
    configdict["BsCombinatorialShape"]["type"]  = "DoubleExponential"
    configdict["BsCombinatorialShape"]["cB1"]   = {"Run1": {"NonRes":-8.5211e-03,  "PhiPi":-5.0873e-03,  "KstK":-8.3392e-03, "KPiPi":-5.0361e-03, "PiPiPi":-5.5277e-03},"Fixed": False}
    configdict["BsCombinatorialShape"]["cB2"]   = {"Run1": {"NonRes":0.0,       "PhiPi":0.0,       "KstK":0.0,      "KPiPi":0.0,         "PiPiPi":0.0},
                                                   "Fixed":True }
    configdict["BsCombinatorialShape"]["frac"]  = {"Run1": {"NonRes":4.3067e-01,   "PhiPi":6.5400e-01,   "KstK":3.7409e-01,  "KPiPi":1.0,  "PiPiPi":1.0}, "Fixed":{"KPiPi":True,
                                                                                                                                                                   "PiPiPi":True}}


    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusSignal"
    configdict["DsCombinatorialShape"]["cD"]      = {"Run1": {"NonRes":-4.4329e-03,  "PhiPi":-8.8642e-03,  "KstK":-5.2652e-03, "KPiPi":-5.0743e-03, "PiPiPi":-5.1877e-03},"Fixed":False}
    configdict["DsCombinatorialShape"]["fracD"]   = {"Run1": {"NonRes":0.88620,      "PhiPi":0.37379,     "KstK":0.59093,      "KPiPi":0.5,         "PiPiPi":0.5},"Fixed":False}


    configdict["PIDKCombinatorialShape"] = {}
    configdict["PIDKCombinatorialShape"]["type"] = "Fixed"
    configdict["PIDKCombinatorialShape"]["components"] = { "Kaon":True, "Pion":True, "Proton":True }
    configdict["PIDKCombinatorialShape"]["fracPIDK1"]   = { "Run1":{"NonRes":0.9, "PhiPi":0.9, "KstK":0.9, "KPiPi":0.8, "PiPiPi":0.8 }, "Fixed":False }
    configdict["PIDKCombinatorialShape"]["fracPIDK2"]   = { "Run1":{"NonRes":0.9, "PhiPi":0.9, "KstK":0.9, "KPiPi":0.8, "PiPiPi":0.8 }, "Fixed":False }


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
    configdict["AdditionalParameters"]["g1_f1_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":1.0, "Range":[0.0,1.0]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["g2_f1_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["g2_f2_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["g3_f1_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":0.75,"Range":[0.0,1.0]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["g5_f1_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["lumRatio_Signal_2011"] = {"Run1":{"All":{"Both":{"CentralValue":0.42718, "Range":[0.2,0.7]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Signal_2012"] = {"Run1":{"All":{"Both":{"CentralValue":0.50229, "Range":[0.2,0.7]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Signal_run1"] = {"Run1":{"All":{"Both":{"CentralValue":0.31, "Range":[0.0,1.0]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Comb_2011"] = {"Run1":{"All":{"Both":{"CentralValue":0.42718, "Range":[0.2,0.7]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Comb_2012"] = {"Run1":{"All":{"Both":{"CentralValue":0.50229, "Range":[0.2,0.7]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Comb_run1"] = {"Run1":{"All":{"Both":{"CentralValue":0.31, "Range":[0.0,1.0]}}}, "Fixed":True}



    #expected yields                                                                                                                                                              
    configdict["Yields"] = {}
    configdict["Yields"]["Bd2DPi"]            = {"2011": {"NonRes":0.9,     "PhiPi":0.0,    "KstK":0.15,   "KPiPi":0.0,    "PiPiPi":0.0},
                                                 "2012": {"NonRes":1.6,     "PhiPi":0.1,    "KstK":0.35,   "KPiPi":0.0,    "PiPiPi":0.0}, "Fixed":True}
    configdict["Yields"]["Bd2DK"]             = {"2011": {"NonRes":2.0,     "PhiPi":0.2,    "KstK":0.4,    "KPiPi":0.0,    "PiPiPi":0.0},
                                                 "2012": {"NonRes":3.8,     "PhiPi":0.5,    "KstK":0.9,    "KPiPi":0.0,    "PiPiPi":0.0}, "Fixed":True}
    configdict["Yields"]["Lb2LcPi"]           = {"2011": {"NonRes":2.5,     "PhiPi":1.0,    "KstK":0.8,    "KPiPi":0.0,    "PiPiPi":0.0},
                                                 "2012": {"NonRes":5.3,     "PhiPi":2.9,    "KstK":1.7,    "KPiPi":0.0,    "PiPiPi":0.0}, "Fixed":True}
    configdict["Yields"]["Lb2LcK"]            = {"2011": {"NonRes":5.5,     "PhiPi":1.2,    "KstK":1.8,    "KPiPi":0.0,    "PiPiPi":0.0},
                                                 "2012": {"NonRes":13.4,    "PhiPi":2.5,    "KstK":4.3,    "KPiPi":0.0,    "PiPiPi":0.0}, "Fixed":True}

    configdict["Yields"]["Bs2DsDsstKKst"]      = {"2011": {"NonRes":50.0,    "PhiPi":50.0,   "KstK":50.0,   "KPiPi":50.0,   "PiPiPi":50.0},
                                                  "2012": {"NonRes":100.0,   "PhiPi":100.0,  "KstK":100.0,  "KPiPi":100.0,  "PiPiPi":100.0}, "Fixed":False}
    configdict["Yields"]["BsLb2DsDsstPPiRho"]  = {"2011": {"NonRes":225.0,   "PhiPi":500.0,  "KstK":330.0,  "KPiPi":90.0,   "PiPiPi":260.0},
                                                  "2012": {"NonRes":450.0,   "PhiPi":1000.0, "KstK":660.0,  "KPiPi":180.0,  "PiPiPi":260.0}, "Fixed":False}
    configdict["Yields"]["CombBkg"]            = {"2011": {"NonRes":1000.0,  "PhiPi":1000.0, "KstK":1000.0, "KPiPi":1000.0, "PiPiPi":1000.0},
                                                  "2012": {"NonRes":2000.0,  "PhiPi":2000.0, "KstK":2000.0, "KPiPi":2000.0, "PiPiPi":2000.0}, "Fixed":False}
    configdict["Yields"]["Signal"]             = {"2011": {"NonRes":1000.0,  "PhiPi":1000.0, "KstK":1000.0, "KPiPi":1000.0, "PiPiPi":1000.0},
                                                  "2012": {"NonRes":2000.0,  "PhiPi":2000.0, "KstK":2000.0, "KPiPi":2000.0, "PiPiPi":2000.0}, "Fixed":False}


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
