def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bs2DsPi"
    configdict["CharmModes"] = {"KstK","NonRes","PhiPi","KPiPi","PiPiPi"}
    # year of data taking                                                                                                                          
    configdict["YearOfDataTaking"] = {"2012"}
    # stripping (necessary in case of PIDK shapes)                                                                                              
    configdict["Stripping"] = {"2012":"21", "2011":"21r1"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)                                                                  
    configdict["IntegratedLuminosity"] = {"2011": {"Down": 0.59, "Up": 0.44}, "2012":{"Down": 0.9894, "Up": 0.9985}}
    # file name with paths to MC/data samples                                                                                                       
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/Bs2DsPi/config_Bs2DsPi.txt"
    #settings for control plots                                                                                                                                                           
    configdict["ControlPlots"] = {}
    configdict["ControlPlots"] = { "Directory": "PlotBs2DsPiNoLog", "Extension":"pdf"}

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5300,    5800    ], "InputName" : "lab0_MassFitConsD_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1930,    2015    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-7.0,    6.0     ], "InputName" : "lab1_PIDK"} #-7.0,6.0
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.0,     1.0     ], "InputName" : "BDTGResponse_2"}
    configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_TAGDECISION_OS"}
    configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_SS_nnetKaon_DEC"}
    configdict["BasicVariables"]["MistagOS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_TAGOMEGA_OS"}
    configdict["BasicVariables"]["MistagSS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_SS_nnetKaon_PROB"}

    # tagging calibration                                                                                               
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.375,  "p1": 0.982, "average": 0.3688}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4429, "p1": 0.977, "average": 0.4377}

    # additional cuts applied to data sets                                                                                    
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0",            "MC" : "lab2_TAU>0&&lab1_M<200", "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    configdict["AdditionalCuts"]["KKPi"]   = { "Data": "lab2_FDCHI2_ORIVX > 2", "MC" : "lab2_FDCHI2_ORIVX > 2"}
    configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    configdict["AdditionalCuts"]["PiPiPi"] = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}

    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                              
    # order of particles: KKPi, KPiPi, PiPiPi                                                                                                         
    configdict["DsChildrenPrefix"] = {"Child1":"lab3","Child2":"lab4","Child3": "lab5"}

    # additional variables in data sets                                                                                                             
    #configdict["AdditionalVariables"] = {}
    #configdict["AdditionalVariables"]["tagOmegaSSKaon"]      =  { "Range" : [ -3.0, 1,0 ], "InputName" : "lab0_SS_Kaon_PROB"}
    #configdict["AdditionalVariables"]["tagDecSSKaon"]        =  { "Range" : [ -2.0, 2,0 ], "InputName" : "lab0_SS_Kaon_DEC"}
    #configdict["AdditionalVariables"]["tagOmegaOSMuon"]      =  { "Range" : [ -3.0, 1,0 ], "InputName" : "lab0_OS_Muon_PROB"}
    #configdict["AdditionalVariables"]["tagDecOSMuon"]        =  { "Range" : [ -2.0, 2,0 ], "InputName" : "lab0_OS_Muon_DEC"}
    #configdict["AdditionalVariables"]["tagOmegaOSElectron"]  =  { "Range" : [ -3.0, 1,0 ], "InputName" : "lab0_OS_Electron_PROB"}
    #configdict["AdditionalVariables"]["tagDecSSElectron"]    =  { "Range" : [ -2.0, 2,0 ], "InputName" : "lab0_OS_Electron_DEC"}
    #configdict["AdditionalVariables"]["tagOmegaOSKaon"]      =  { "Range" : [ -3.0, 1,0 ], "InputName" : "lab0_OS_Kaon_PROB"}
    #configdict["AdditionalVariables"]["tagDecOSKaon"]        =  { "Range" : [ -2.0, 2,0 ], "InputName" : "lab0_OS_Kaon_DEC"}
    #configdict["AdditionalVariables"]["tagOmegaOSnnetKaon"]  =  { "Range" : [ -3.0, 1,0 ], "InputName" : "lab0_OS_nnetKaon_PROB"}
    #configdict["AdditionalVariables"]["tagDecOSnnetKaon"]    =  { "Range" : [ -2.0, 2,0 ], "InputName" : "lab0_OS_nnetKaon_DEC"}
    #configdict["AdditionalVariables"]["tagOmegaOSVtxCharge"] =  { "Range" : [ -3.0, 1,0 ], "InputName" : "lab0_VtxCharge_PROB"}
    #configdict["AdditionalVariables"]["tagDecOSVtxCharge"]   =  { "Range" : [ -2.0, 2,0 ], "InputName" : "lab0_VtxCharge_DEC" }


    #weighting templates by PID eff/misID                                                                                                                                                 
    configdict["WeightingMassTemplates"]= { ###"Variables":["lab4_P","lab3_P"], 
                                            "PIDBachEff":            { "FileLabel": { "2011":"#PID Pion 2011", "2012":"#PID Pion 2012"}, 
                                                                       "Var":"lab1_P", "HistName":"MyPionEff_0"},
                                            "PIDBachMisID":          { "FileLabel": { "2011":"#PID Kaon 2011", "2012":"#PID Kaon 2012"}, 
                                                                       "Var":"lab1_P", "HistName":"MyKaonMisID_0"},
                                            "PIDChildKaonPionMisID": { "FileLabel": { "2011":"#PID Pion 2011", "2012":"#PID Pion 2012"}, 
                                                                       "Var":"lab3_P", "HistName":"MyPionMisID_0"}, 
                                            "PIDChildProtonMisID":   { "FileLabel": { "2011":"#PID Proton 2011", "2012":"#PID Proton 2012"}, 
                                                                       "Var":"lab4_P", "HistName":"MyProtonMisID_pKm5_KPi5"}, 
                                            "RatioDataMC":{ "2011":"#RatioDataMC 2011", "2012": "#RatioDataMC 2012"},   
                                            "Shift":{ "BeautyMass": -2.0, "CharmMass": 0.0} }

    #weighting for PID templates                                                                                                                                                          
    configdict["ObtainPIDTemplates"] = { "Variables":["BacPT","nTracks"], "Bins":[20,20] }
    configdict["Calibrations"] = {}
    configdict["Calibrations"]["2011"] = {}
    configdict["Calibrations"]["2011"]["Pion"]   = {}
    configdict["Calibrations"]["2011"]["Pion"]["Up"]   = {"FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples/Calib_Dst_Up_Pi_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Pion"]["Down"] = {"FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples/Calib_Dst_Down_Pi_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]   = {}
    configdict["Calibrations"]["2011"]["Kaon"]["Up"]   = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples/Calib_Dst_Up_K_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]["Down"] = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples/Calib_Dst_Down_K_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsPi_Run1.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up_2011", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsPi_Run1.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down_2011", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    
    #configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root",
    #                                                              "WorkName":"workspace", "DataName":"dataCombBkg_up", "Type":"Special",
    #                                                              "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    #configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root",
    #                                                                "WorkName":"workspace", "DataName":"dataCombBkg_down", "Type":"Special",
    #                                                                "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}

    configdict["Calibrations"]["2012"] = {}
    configdict["Calibrations"]["2012"]["Pion"]   = {}
    configdict["Calibrations"]["2012"]["Pion"]["Up"]   = {"FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples/Calib_Dst_Up_Pi_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Pion"]["Down"] = {"FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples/Calib_Dst_Down_Pi_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Kaon"]   = {}
    configdict["Calibrations"]["2012"]["Kaon"]["Up"]   = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples/Calib_Dst_Up_K_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Kaon"]["Down"] = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples/Calib_Dst_Down_K_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2012"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsPi_Run1.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up_2012", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsPi_Run1.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down_2012", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}

    #configdict["Calibrations"]["2012"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root",
    #                                                              "WorkName":"workspace", "DataName":"dataCombBkg_up", "Type":"Special",
    #                                                              "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    #configdict["Calibrations"]["2012"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root",
    #                                                                "WorkName":"workspace", "DataName":"dataCombBkg_down", "Type":"Special",
    #                                                                "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                               MDfit fitting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
    # Bs signal shapes                                                                                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5367.51}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":1.1745e+01,  "PhiPi":1.3313e+01,  "KstK":1.2022e+01,  "KPiPi":1.6574e+01,  "PiPiPi":1.3401e+01},  "Fixed":True}
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":1.8919e+01,  "PhiPi":2.8551e+01,  "KstK":1.9637e+01,  "KPiPi":1.0991e+01,  "PiPiPi":2.6155e+01},  "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":2.1544e+00,  "PhiPi":1.9042e+00, "KstK":2.3896e+00,  "KPiPi":1.4544e+00,  "PiPiPi":1.7670e+00},  "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":-2.1990e+00, "PhiPi":-2.3863e+00,  "KstK":-2.3317e+00, "KPiPi":-2.0499e+00, "PiPiPi":-2.4384e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"NonRes":6.3740e-01,  "PhiPi":2.6165e+00,  "KstK":3.8919e-01,  "KPiPi":4.580e+00,  "PiPiPi":3.1412e+00},  "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"NonRes":2.5111e+00,  "PhiPi":1.3077e+00,  "KstK":2.1021e+00,  "KPiPi":1.9570e+00,  "PiPiPi":1.4763e+00},  "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"NonRes":5.5999e-01,  "PhiPi":8.5608e-01,  "KstK":6.0170e-01,  "KPiPi":6.1205e-01,  "PiPiPi":8.1411e-01},  "Fixed":True}
    configdict["BsSignalShape"]["R"]       = {"Run1": {"KKPi":1.00,        "KPiPi":1.0,         "PiPiPi":1.0}, "Fixed":False}

    #Ds signal shapes                                                                                                                                       
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All":1968.49}, "Fixed":False} 
    configdict["DsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":5.8071e+00,  "PhiPi":5.4743e+00,  "KstK":5.7842e+00,  "KPiPi":1.2615e+01,  "PiPiPi":9.0602e+00}, "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":5.3475e+00,  "PhiPi":5.6855e+00,  "KstK":5.7178e+00,  "KPiPi":6.6474e+00,  "PiPiPi":8.1586e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":1.0859e+00,  "PhiPi":1.0957e+00,  "KstK":1.2474e+00,  "KPiPi":1.4519e+00,  "PiPiPi":8.0038e-01}, "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":-1.1507e+00, "PhiPi":-1.0981e+00, "KstK":-1.0918e+00, "KPiPi":-3.6815e+00, "PiPiPi":-1.2015e+00},"Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"Run1": {"NonRes":8.4855e+00,  "PhiPi":6.1611e+00,  "KstK":7.8779e+00,  "KPiPi":1.6146e+01,  "PiPiPi":9.1494e+01}, "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"Run1": {"NonRes":1.2769e+01,  "PhiPi":2.0066e+01,  "KstK":3.1134e+01,  "KPiPi":7.6024e-06,  "PiPiPi":1.2168e+01}, "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"Run1": {"NonRes":4.6141e-01,     "PhiPi":4.47e-01,  "KstK":5.4861e-01,  "KPiPi":2.6988e-01,  "PiPiPi":4.1267e-01}, "Fixed":True}
    configdict["DsSignalShape"]["R"]       = {"Run1": {"KKPi":1.00,        "KPiPi":1.0,         "PiPiPi":1.0}, "Fixed":False}

    # combinatorial background                                                                                                                              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"]  = "DoubleExponential"
    configdict["BsCombinatorialShape"]["cB1"]   = {"Run1": {"NonRes":-3.5211e-02,  "PhiPi":-3.0873e-02,  "KstK":-2.3392e-02, "KPiPi":-1.0361e-02, "PiPiPi":-1.5277e-02},"Fixed": False}
    configdict["BsCombinatorialShape"]["cB2"]   = {"Run1": {"NonRes":0.0,       "PhiPi":0.0,       "KstK":0.0,      "KPiPi":0.0,         "PiPiPi":0.0}, 
                                                   "Fixed":True }
    configdict["BsCombinatorialShape"]["frac"]  = {"Run1": {"NonRes":4.3067e-01,   "PhiPi":6.5400e-01,   "KstK":3.7409e-01,  "KPiPi":0.5,         "PiPiPi":0.5}, "Fixed":False}
    
    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusDoubleCrystalBallWithWidthRatioSharedMean"
    configdict["DsCombinatorialShape"]["sigma1"]  = {"Run1": {"NonRes":5.8071e+00,  "PhiPi":5.4743e+00,  "KstK":5.7842e+00,  "KPiPi":1.2615e+01,  "PiPiPi":9.0602e+00}, "Fixed":True}
    configdict["DsCombinatorialShape"]["sigma2"]  = {"Run1": {"NonRes":5.3475e+00,  "PhiPi":5.6855e+00,  "KstK":5.7178e+00,  "KPiPi":6.6474e+00,  "PiPiPi":8.1586e+00}, "Fixed":True}
    configdict["DsCombinatorialShape"]["alpha1"]  = {"Run1": {"NonRes":1.0859e+00,  "PhiPi":1.0957e+00,  "KstK":1.2474e+00,  "KPiPi":1.4519e+00,  "PiPiPi":8.0038e-01}, "Fixed":True}
    configdict["DsCombinatorialShape"]["alpha2"]  = {"Run1": {"NonRes":-1.1507e+00, "PhiPi":-1.0981e+00, "KstK":-1.0918e+00, "KPiPi":-3.6815e+00, "PiPiPi":-1.2015e+00},"Fixed":True}
    configdict["DsCombinatorialShape"]["n1"]      = {"Run1": {"NonRes":8.4855e+00,  "PhiPi":6.1611e+00,  "KstK":7.8779e+00,  "KPiPi":1.6146e+01,  "PiPiPi":9.1494e+01}, "Fixed":True}
    configdict["DsCombinatorialShape"]["n2"]      = {"Run1": {"NonRes":1.2769e+01,  "PhiPi":2.0066e+01,  "KstK":3.1134e+01,  "KPiPi":7.6024e-06,  "PiPiPi":1.2168e+01}, "Fixed":True}
    configdict["DsCombinatorialShape"]["frac"]    = {"Run1": {"NonRes":4.6141e-01,     "PhiPi":4.47e-01,  "KstK":5.4861e-01,  "KPiPi":2.6988e-01,  "PiPiPi":4.1267e-01}, "Fixed":True}
    configdict["DsCombinatorialShape"]["R"]       = {"Run1": {"KKPi":1.50,        "KPiPi":1.5,         "PiPiPi":1.5}, "Fixed":False}
    configdict["DsCombinatorialShape"]["cB"]      = {"Run1": {"NonRes":-2.7520e-03,  "PhiPi":-2.7273e-03,  "KstK":-8.3967e-03, "KPiPi":-1.9193e-03, "PiPiPi":-4.5455e-02},"Fixed":False}
    configdict["DsCombinatorialShape"]["fracD"]   = {"Run1": {"NonRes":0.88620,      "PhiPi":0.37379,      "KstK":0.59093,     "KPiPi":0.5,         "PiPiPi":0.5},"Fixed":False}
    #configdict["DsCombinatorialShape"]["fracD"]   = {"Run1": {"NonRes":0.88620,      "PhiPi":0.37379,      "KstK":0.59093,     "KPiPi":0.5,         "PiPiPi":0.5},"Fixed":False}

    configdict["PIDKCombinatorialShape"] = {}
    configdict["PIDKCombinatorialShape"]["type"] = "Fixed"
    configdict["PIDKCombinatorialShape"]["components"] = { "Kaon":True, "Pion":True, "Proton":False }
    configdict["PIDKCombinatorialShape"]["fracPIDK1"]   = { "Run1":{"KKPi":0.8, "KPiPi":0.8, "PiPiPi":0.8 }, "Fixed":False }

    #Bd2Dsh background
    #shape for BeautyMass, for CharmMass as well as BacPIDK taken by default the same as signal 
    configdict["Bd2Ds(st)XShape"] = {}
    configdict["Bd2Ds(st)XShape"]["type"]    = "ShiftedSignal"
    configdict["Bd2Ds(st)XShape"]["decay"]   = "Bd2DsPi"
    configdict["Bd2Ds(st)XShape"]["shift"]   = {"Run1": {"All": 86.8}, "Fixed":True}
    configdict["Bd2Ds(st)XShape"]["scale1"]  = {"Run1": {"All": 1.00808721452}, "Fixed":True}
    configdict["Bd2Ds(st)XShape"]["scale2"]  = {"Run1": {"All": 1.03868673310}, "Fixed":True}

    #
    configdict["AdditionalParameters"] = {}
    configdict["AdditionalParameters"]["g1_f1_frac"] = {"Run1":{"All":{"Both":{"CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["g1_f2_frac"] = {"Run1":{"All":{"Both":{"CentralValue":0.5, "Range":[0.0,1.0]}}}, "Fixed":False}

    #expected yields                                                                                                                                                       
    configdict["Yields"] = {}
    configdict["Yields"]["Bd2DPi"]          = {"2011": { "NonRes":374.0,   "PhiPi":6.0,     "KstK":93.0,    "KPiPi":30.0,    "PiPiPi":0.0},
                                               "2012": { "NonRes":748.0,   "PhiPi":12.0,    "KstK":186.0,   "KPiPi":60.0,    "PiPiPi":0.0},  "Fixed":True}
    configdict["Yields"]["Lb2LcPi"]         = {"2011": { "NonRes":250.0,   "PhiPi":36.0,    "KstK":69.0,    "KPiPi":1.0,     "PiPiPi":0.0},
                                               "2012": { "NonRes":500.0,   "PhiPi":72.0,    "KstK":138.0,   "KPiPi":2.0,     "PiPiPi":0.0},  "Fixed":True}
    configdict["Yields"]["Bs2DsK"]          = {"2011": { "NonRes":40.0,    "PhiPi":47.0,    "KstK":40.0,    "KPiPi":8.0,     "PiPiPi":21.0},
                                               "2012": { "NonRes":80.0,    "PhiPi":94.0,    "KstK":80.0,    "KPiPi":16.0,    "PiPiPi":42.0}, "Fixed":True}
    configdict["Yields"]["Bs2DsDsstPiRho"]  = {"2011": { "NonRes":100.0,   "PhiPi":100.0,   "KstK":100.0,   "KPiPi":100.0,   "PiPiPi":100.0},
                                               "2012": { "NonRes":200.0,   "PhiPi":200.0,   "KstK":200.0,   "KPiPi":200.0,   "PiPiPi":200.0}, "Fixed":False}
    configdict["Yields"]["CombBkg"]         = {"2011": { "NonRes":10000.0, "PhiPi":10000.0, "KstK":10000.0, "KPiPi":10000.0, "PiPiPi":10000.0},
                                               "2012": { "NonRes":20000.0, "PhiPi":20000.0, "KstK":20000.0, "KPiPi":20000.0, "PiPiPi":20000.0},"Fixed":False}
    configdict["Yields"]["Signal"]          = {"2011": { "NonRes":10000.0, "PhiPi":10000.0, "KstK":10000.0, "KPiPi":10000.0, "PiPiPi":10000.0},
                                               "2012": { "NonRes":20000.0, "PhiPi":20000.0, "KstK":20000.0, "KPiPi":20000.0, "PiPiPi":20000.0},"Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#    
    ###                                                               MDfit plotting settings                                                             
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#               
    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = ["Sig", "CombBkg", "Bd2DPi", "Lb2LcPi", "Bs2DsDsstPiRho", "Bs2DsK"] 
    configdict["PlotSettings"]["colors"] = [kRed-7, kBlue-6, kOrange, kRed, kBlue-10, kGreen+3]

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9], "ScaleYSize":2.5}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.7, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.20,0.9], "ScaleYSize":1.2}

    return configdict
