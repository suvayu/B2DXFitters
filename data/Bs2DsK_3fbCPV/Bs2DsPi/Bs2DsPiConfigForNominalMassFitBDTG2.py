def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bs2DsPi"
    configdict["CharmModes"] = {"KstK","NonRes","PhiPi","KPiPi","PiPiPi"}
    # year of data taking                                                                                                                          
    configdict["YearOfDataTaking"] = {"2011","2012"}
    # stripping (necessary in case of PIDK shapes)                                                                                              
    configdict["Stripping"] = {"2012":"21", "2011":"21r1"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)                                                                  
    #configdict["IntegratedLuminosity"] = {"2011": {"Down": 0.59, "Up": 0.44}, "2012":{"Down": 0.9894, "Up": 0.9985}}
    configdict["IntegratedLuminosity"] = {"2011": {"Down":  0.56, "Up": 0.42}, "2012":{"Down": 0.9912, "Up": 0.9988}}
    # file name with paths to MC/data samples                                                                                                       
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/Bs2DsPi/config_Bs2DsPi.txt"
    #settings for control plots                                                                                                                                                           
    configdict["ControlPlots"] = {}
    configdict["ControlPlots"] = { "Directory": "PlotBs2DsPi_BDTG2", "Extension":"pdf"}

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5300,    5800    ], "InputName" : "lab0_MassFitConsD_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1930,    2015    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-7.0,    5.0     ], "InputName" : "lab1_PIDK"} #-7.0,6.0
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.95,     1.0     ], "InputName" : "BDTGResponse_2"}
    configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_TAGDECISION_OS"}
    configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_SS_nnetKaon_DEC"}
    configdict["BasicVariables"]["MistagOS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_TAGOMEGA_OS"}
    configdict["BasicVariables"]["MistagSS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_SS_nnetKaon_PROB"}

    # tagging calibration                                                                                               
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.375,  "p1": 0.982, "average": 0.3688}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4429, "p1": 0.977, "average": 0.4377}

    HLTcut = "&&(lab0_Hlt1TrackAllL0Decision_TOS && (lab0_Hlt2IncPhiDecision_TOS ==1 || lab0_Hlt2Topo2BodyBBDTDecision_TOS == 1 || lab0_Hlt2Topo3BodyBBDTDecision_TOS == 1))"
    # additional cuts applied to data sets                                                                                    
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0&&lab1_PIDmu<2"+HLTcut,        
                                               "MC" : "lab2_TAU>0&&lab1_M<200&&lab1_PIDK !=-1000.0"+HLTcut, "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
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
    configdict["WeightingMassTemplates"]= { "PIDBachEff":            { "FileLabel": { "2011":"#PIDK Pion 2011", "2012":"#PIDK Pion 2012"},
                                                                       "Var":["nTracks","lab1_P"], "HistName":"MyPionEff_0_mu2"},
                                            "PIDBachMisID":          { "FileLabel": { "2011":"#PIDK Kaon 2011", "2012":"#PIDK Kaon 2012"},
                                                                       "Var":["nTracks","lab1_P"], "HistName":"MyKaonMisID_0_mu2"},
                                            "PIDChildKaonPionMisID": { "FileLabel": { "2011":"#PIDK Pion 2011", "2012":"#PIDK Pion 2012"},
                                                                       "Var":["nTracks","lab3_P"], "HistName":"MyPionMisID_0"},
                                            "PIDChildProtonMisID":   { "FileLabel": { "2011":"#PIDK Proton 2011", "2012":"#PIDK Proton 2012"},
                                                                       "Var":["nTracks","lab4_P"], "HistName":"MyProtonMisID_pKm5_KPi5"},
                                            "RatioDataMC":{ "FileLabel": {"2011":"#RatioDataMC 2011 PNTr", "2012": "#RatioDataMC 2012 PNTr"},
                                                            "Var":["lab1_P","nTracks"], "HistName":"histRatio"},
                                            "Shift":{ "BeautyMass": -2.0, "CharmMass": 0.0} }


    #weighting for PID templates                                                                                                                                                          
    configdict["ObtainPIDTemplates"] = { "Variables":["BacP","nTracks"], "Bins":[30,30] }
    configdict["Calibrations"] = {}
    configdict["Calibrations"]["2011"] = {}
    configdict["Calibrations"]["2011"]["Pion"]   = {}
    configdict["Calibrations"]["2011"]["Pion"]["Up"]   = {"FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_Pi_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Pion"]["Down"] = {"FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Down_Pi_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]   = {}
    configdict["Calibrations"]["2011"]["Kaon"]["Up"]   = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_K_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]["Down"] = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Down_K_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Proton"]   = {}
    configdict["Calibrations"]["2011"]["Proton"]["Up"]   = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_P_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Proton"]["Down"] = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Down_P_PID0_Str21r1.root"}
    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsPi_Run1.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up_2011", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsPi_Run1.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down_2011", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}

    configdict["Calibrations"]["2012"] = {}
    configdict["Calibrations"]["2012"]["Pion"]   = {}
    configdict["Calibrations"]["2012"]["Pion"]["Up"]   = {"FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_Pi_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Pion"]["Down"] = {"FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Down_Pi_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Kaon"]   = {}
    configdict["Calibrations"]["2012"]["Kaon"]["Up"]   = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_K_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Kaon"]["Down"] = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Down_K_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Proton"]   = {}
    configdict["Calibrations"]["2012"]["Proton"]["Up"]   = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Up_P_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Proton"]["Down"] = { "FileName":"root://eoslhcb.cern.ch//eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/CalibrationSamples2/Calib_Dst_Down_P_PID0_Str21.root"}
    configdict["Calibrations"]["2012"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2012"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsPi_Run1.root",
                                                                     "WorkName":"workspace", "DataName":"dataCombBkg_up_2012", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/g/gtellari/public/Bs2DsK_3fb/PIDK_combo_shapes/work_Comb_DsPi_Run1.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down_2012", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                               MDfit fitting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
    # Bs signal shapes                                                                                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5367.51}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":1.6824e+01,  "PhiPi":1.6601e+01,  "KstK":1.6537e+01,  "KPiPi":1.6489e+01,  "PiPiPi":1.7204e+01},  "Fixed":True}
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":1.0962e+01,  "PhiPi":1.1395e+01,  "KstK":1.1299e+01,  "KPiPi":1.0970e+01,  "PiPiPi":1.1561e+01},  "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":-2.4265e+00, "PhiPi":-2.2224e+00, "KstK":-2.2993e+00, "KPiPi":-2.8905e+00, "PiPiPi":-2.1065e+00},  "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":2.1704e+00,  "PhiPi":2.1271e+00,  "KstK":2.0747e+00,  "KPiPi":2.1790e+00,  "PiPiPi":2.0236e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"NonRes":2.6914e+00,  "PhiPi":3.1509e+00,  "KstK":3.1136e+00,  "KPiPi":1.5628e+00,  "PiPiPi":4.0379e+00},  "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"NonRes":6.0871e-01,  "PhiPi":6.0644e-01,  "KstK":7.6784e-01,  "KPiPi":5.0557e-01,  "PiPiPi":8.1528e-01},  "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"NonRes":0.5,         "PhiPi":0.5,         "KstK":0.5,         "KPiPi":0.5,         "PiPiPi":0.5},  "Fixed":True}
    configdict["BsSignalShape"]["R"]       = {"Run1": {"NonRes":1.00,        "PhiPi":1.0,          "Kstk":1.0,        "KPiPi":1.0,         "PiPiPi":1.0}, "Fixed":False}

    #Ds signal shapes                                                                                                                                       
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All":1968.49}, "Fixed":False} 
    configdict["DsSignalShape"]["sigma1"]  = {"Run1": {"NonRes":6.4256e+00,  "PhiPi":5.1958e+00,  "KstK":4.4044e+00,  "KPiPi":7.0825e+00,  "PiPiPi":8.2159e+00}, "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"Run1": {"NonRes":4.1796e+00,  "PhiPi":5.1946e+00,  "KstK":6.7061e+00,  "KPiPi":6.0212e+00,  "PiPiPi":7.3552e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"NonRes":-2.1805e+00, "PhiPi":-1.3555e+00, "KstK":-3.0000e+00, "KPiPi":-1.7033e+00, "PiPiPi":-1.4847e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"NonRes":1.7124e+00,  "PhiPi":1.3204e+00,  "KstK":2.6063e+00,  "KPiPi":1.4677e+00,  "PiPiPi":1.2645e+00},"Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"Run1": {"NonRes":1.8626e+01,  "PhiPi":9.9998e+01,  "KstK":9.9163e+01,  "KPiPi":2.1268e+01,  "PiPiPi":9.9998e+01}, "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"Run1": {"NonRes":1.0001e+01,  "PhiPi":1.0000e+02,  "KstK":9.5636e+01,  "KPiPi":9.9748e+01,  "PiPiPi":1.0000e+02}, "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"Run1": {"NonRes":0.50,        "PhiPi":0.50,        "KstK":0.50,        "KPiPi":0.50,        "PiPiPi":0.50}, "Fixed":True}
    configdict["DsSignalShape"]["R"]       = {"Run1": {"NonRes":1.00,        "PhiPi":1.00,        "KstK":1.00,        "KPiPi":1.00,        "PiPiPi":1.00}, "Fixed":False}

    # combinatorial background                                                                                                                              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"] = "Exponential"
    configdict["BsCombinatorialShape"]["cB"]   = {"Run1":{"NonRes":-8.1530e-03,  "PhiPi":-8.2354e-03,  "KstK":-8.3675e-03, "KPiPi":-8.8158e-03, "PiPiPi":-8.0890e-03}, "Fixed":False}
    
    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "DoubleCrystalBallWithWidthRatioSharedMean"
    configdict["DsCombinatorialShape"]["sigma1"]  = {"Run1": {"NonRes":6.4256e+00,  "PhiPi":5.1958e+00,  "KstK":4.4044e+00,  "KPiPi":7.0825e+00,  "PiPiPi":8.2159e+00}, "Fixed":True}
    configdict["DsCombinatorialShape"]["sigma2"]  = {"Run1": {"NonRes":4.1796e+00,  "PhiPi":5.1946e+00,  "KstK":6.7061e+00,  "KPiPi":6.0212e+00,  "PiPiPi":7.3552e+00}, "Fixed":True}
    configdict["DsCombinatorialShape"]["alpha1"]  = {"Run1": {"NonRes":-2.1805e+00, "PhiPi":-1.3555e+00, "KstK":-3.0000e+00, "KPiPi":-1.7033e+00, "PiPiPi":-1.4847e+00}, "Fixed":True}
    configdict["DsCombinatorialShape"]["alpha2"]  = {"Run1": {"NonRes":1.7124e+00,  "PhiPi":1.3204e+00,  "KstK":2.6063e+00,  "KPiPi":1.4677e+00,  "PiPiPi":1.2645e+00},"Fixed":True}
    configdict["DsCombinatorialShape"]["n1"]      = {"Run1": {"NonRes":1.8626e+01,  "PhiPi":9.9998e+01,  "KstK":9.9163e+01,  "KPiPi":2.1268e+01,  "PiPiPi":9.9998e+01}, "Fixed":True}
    configdict["DsCombinatorialShape"]["n2"]      = {"Run1": {"NonRes":1.0001e+01,  "PhiPi":1.0000e+02,  "KstK":9.5636e+01,  "KPiPi":9.9748e+01,  "PiPiPi":1.0000e+02}, "Fixed":True}
    configdict["DsCombinatorialShape"]["frac"]    = {"Run1": {"NonRes":0.50,        "PhiPi":0.50,        "KstK":0.50,        "KPiPi":0.50,        "PiPiPi":0.50}, "Fixed":True}
    configdict["DsCombinatorialShape"]["R"]       = {"Run1": {"NonRes":1.7294e+00,  "PhiPi":1.4199e+00,   "Kstk":1.3580e+00,   "KPiPi":1.6602e+00,  "PiPiPi":2.000e+00},  "Fixed":False}

    configdict["PIDKCombinatorialShape"] = {}
    configdict["PIDKCombinatorialShape"]["type"] = "Fixed"
    configdict["PIDKCombinatorialShape"]["components"] = { "Kaon":True, "Pion":True, "Proton":False }
    configdict["PIDKCombinatorialShape"]["fracPIDK1"]   = { "Run1":{"All":0.5}, "Fixed":False }
    configdict["PIDKCombinatorialShape"]["fracPIDK2"]   = { "Run1":{"All":0.5}, "Fixed":False }


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
    configdict["AdditionalParameters"]["lumRatio_Signal_2011"] = {"Run1":{"All":{"Both":{"CentralValue":0.43, "Range":[0.2,0.7]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Signal_2012"] = {"Run1":{"All":{"Both":{"CentralValue":0.51, "Range":[0.2,0.7]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Signal_run1"] = {"Run1":{"All":{"Both":{"CentralValue":0.31, "Range":[0.0,1.0]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Comb_2011"] = {"Run1":{"All":{"Both":{"CentralValue":0.43, "Range":[0.2,0.7]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Comb_2012"] = {"Run1":{"All":{"Both":{"CentralValue":0.51, "Range":[0.2,0.7]}}}, "Fixed":True}
    configdict["AdditionalParameters"]["lumRatio_Comb_run1"] = {"Run1":{"All":{"Both":{"CentralValue":0.31, "Range":[0.0,1.0]}}}, "Fixed":True}


    #expected yields                                                                                                                                                       
    configdict["Yields"] = {}
    configdict["Yields"]["Bd2DPi"]          = {"2011": { "NonRes":146.0,   "PhiPi":7.4,     "KstK":106.5,   "KPiPi":0.0,     "PiPiPi":0.0},
                                               "2012": { "NonRes":325.0,   "PhiPi":17.8,    "KstK":262.8,   "KPiPi":0.0,     "PiPiPi":0.0},  "Fixed":True}
    configdict["Yields"]["Lb2LcPi"]         = {"2011": { "NonRes":65.0,    "PhiPi":10.0,    "KstK":19.8,    "KPiPi":0.4,     "PiPiPi":0.0},
                                               "2012": { "NonRes":154.7,   "PhiPi":25.0,    "KstK":46.2,    "KPiPi":1.3,     "PiPiPi":0.0},  "Fixed":True}
    configdict["Yields"]["Bs2DsK"]          = {"2011": { "NonRes":26.0,    "PhiPi":38.7,    "KstK":38.2,    "KPiPi":18.8,    "PiPiPi":35.2},
                                               "2012": { "NonRes":69.0,    "PhiPi":99.9,    "KstK":96.3,    "KPiPi":51.5,    "PiPiPi":96.65}, "Fixed":True}
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
