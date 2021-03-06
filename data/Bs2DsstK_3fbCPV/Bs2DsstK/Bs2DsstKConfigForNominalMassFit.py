def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bs2DsstK"
    configdict["CharmModes"] = {"NonRes", "PhiPi", "KstK", "KPiPi", "PiPiPi"}
    # year of data taking                                                                                 
    configdict["YearOfDataTaking"] = {"2012", "2011"}
    # stripping (necessary in case of PIDK shapes)                               
    configdict["Stripping"] = {"2012":"21", "2011":"21r1"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)
    configdict["IntegratedLuminosity"] = {"2011":{"Down": 0.57, "Up": 0.43}, "2012":{"Down": 0.9894, "Up": 0.9985}} 
    # file name with paths to MC/data samples                                     
    configdict["dataName"]   = "../data/Bs2DsstK_3fbCPV/Bs2DsstK/config_Bs2DsstK.txt"

    configdict["ControlPlots"] = {}
    configdict["ControlPlots"] = { "Directory": "PlotBs2DsstK", "Extension":"pdf"}

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5100,    6000    ], "InputName" : "FBs_DeltaM_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [2080,    2150    ], "InputName" : "FDsstr_DeltaM_M"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     12.0    ], "InputName" : "FBs_LF_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [1000.,   650000.0], "InputName" : "FBac_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [1000.,   45000.0 ], "InputName" : "FBac_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [1.61,    5.0     ], "InputName" : "FBac_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.,     1000.0  ], "InputName" : "FnTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "FBs_LF_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "FBac_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.025,   1.0     ], "InputName" : "FBDT_Var"}
    configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "FBs_TAGDECISION_OS"}
    configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "FBs_SS_nnetKaon_DEC"}
    configdict["BasicVariables"]["MistagOS"]      = { "Range" : [0.0,     0.5     ], "InputName" : "FBs_TAGOMEGA_OS"}
    configdict["BasicVariables"]["MistagSS"]      = { "Range" : [0.0,     0.5     ], "InputName" : "FBs_SS_nnetKaon_PROB"}

    # tagging calibration                                                                                               
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.3834, "p1": 0.9720, "average": 0.3813}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4244, "p1": 1.2180, "average": 0.4097}

    # additional cuts applied to data sets
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = {"Data": "FDs_M>1950.&&FDs_M<1990.&&FDs_FDCHI2_ORIVX>2.&&FDelta_M>111.5&&FDelta_M<181.5&&FBs_Veto==0.&&FBDT_Var>0.025",
                                              "MC":   "FDs_M>1950.&&FDs_M<1990.&&FDs_FDCHI2_ORIVX>2.&&FDelta_M>111.5&&FDelta_M<181.5&&FBs_Veto==0.&&FBDT_Var>0.025"}
    configdict["AdditionalCuts"]["NonRes"] = {"Data":"FDs_Dec==3", "MC":"FDs_Dec==3"}
    configdict["AdditionalCuts"]["PhiPi"]  = {"Data":"FDs_Dec==1", "MC":"FDs_Dec==1"}
    configdict["AdditionalCuts"]["KstK"]   = {"Data":"FDs_Dec==2", "MC":"FDs_Dec==2"}
    configdict["AdditionalCuts"]["KPiPi"]  = {"Data":"FDs_Dec==5&&FDs_FDCHI2_ORIVX>9.&&FPi_PIDK>10.&&FKp_PIDK<0.&&FKm_PIDK<0.&&FKst_M<1750.",
                                              "MC":  "FDs_Dec==5&&FDs_FDCHI2_ORIVX>9.&&FKst_M<1750."}
    configdict["AdditionalCuts"]["PiPiPi"] = {"Data":"FDs_Dec==4&&FDs_FDCHI2_ORIVX>9.&&FKp_PIDK<0.&&FKm_PIDK<0.&&FPi_PIDK<0.&&(FPhi_M<1700.&&FKst_M<1700.)", 
                                              "MC":  "FDs_Dec==4&&FDs_FDCHI2_ORIVX>9.&&(FPhi_M<1700.&&FKst_M<1700.)"}
 
    configdict["CreateCombinatorial"] = {}
    configdict["CreateCombinatorial"]["BeautyMass"] = {} 
    configdict["CreateCombinatorial"]["BeautyMass"]["All"]    = {"Cut":"FBs_DeltaM_M>5100&&FBs_DeltaM_M<6000&&FDs_M>1950.&&FDs_M<1990.&&FDs_FDCHI2_ORIVX>2.&&FDelta_M>185.&&FDelta_M<205.&&FBs_Veto==0.&&FBDT_Var>0.025&&FBac_P>1000.0&&FBac_P<650000.0&&FBac_PT>1000.0&&FBac_PT<45000.0",
                                                                 "Rho":2.5, "Mirror":"Both"}
    configdict["CreateCombinatorial"]["BeautyMass"]["NonRes"] = {"Cut":"FDs_Dec==3"}
    configdict["CreateCombinatorial"]["BeautyMass"]["PhiPi"]  = {"Cut":"FDs_Dec==1"}
    configdict["CreateCombinatorial"]["BeautyMass"]["KstK"]   = {"Cut":"FDs_Dec==2"}
    configdict["CreateCombinatorial"]["BeautyMass"]["KPiPi"]  = {"Cut":"FDs_Dec==5&&FDs_FDCHI2_ORIVX>9.&&FPi_PIDK>10.&&FKp_PIDK<0.&&FKm_PIDK<0.&&FKst_M<1750."}
    configdict["CreateCombinatorial"]["BeautyMass"]["PiPiPi"] = {"Cut":"FDs_Dec==4&&FDs_FDCHI2_ORIVX>9.&&FKp_PIDK<0.&&FKm_PIDK<0.&&FPi_PIDK<0.&&(FPhi_M<1700.&&FKst_M<1700.)"}

    #weighting for PID templates
    configdict["ObtainPIDTemplates"] = { "Variables":["BacPT","nTracks"], "Bins":[20,20] }
    #configdict["WeightingMassTemplates"]= { "RatioDataMC":True }

    #PID Calibration samples for PID shapes
    configdict["Calibrations"] = {}
    configdict["Calibrations"]["2011"] = {}
    configdict["Calibrations"]["2011"]["Pion"]   = {}
    configdict["Calibrations"]["2011"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID5_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID5_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]   = {}
    configdict["Calibrations"]["2011"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID5_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID5_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_Up_DsK_5358.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_Down_DsK_5358.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}

    #configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { "FileName":"",
    #                                                              "WorkName":"workspace", "DataName":"dataSetCombK_BeautyMass", "Type":"Workspace",
    #                                                              "WeightName":"", "PIDVarName":"BacPIDK", "Variables":["BacPT","nTracks"]}
    #configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { "FileName":"",
    #                                                              "WorkName":"workspace", "DataName":"dataSetCombK_BeautyMass", "Type":"Workspace",
    #                                                              "WeightName":"", "PIDVarN

    configdict["Calibrations"]["2012"] = {}
    configdict["Calibrations"]["2012"]["Pion"]   = {}
    configdict["Calibrations"]["2012"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID5_Str20.root"}
    configdict["Calibrations"]["2012"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID5_Str20.root"}
    configdict["Calibrations"]["2012"]["Kaon"]   = {}
    configdict["Calibrations"]["2012"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID5_Str20.root"}
    configdict["Calibrations"]["2012"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID5_Str20.root"}
    configdict["Calibrations"]["2012"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_Up_DsK_5358.root",
                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up", "Type":"Special",
                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_Down_DsK_5358.root",
                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down", "Type":"Special",
                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}

    #configdict["Calibrations"]["2012"]["Combinatorial"]["Up"] = { "FileName":"",
    #                                                              "WorkName":"workspace", "DataName":"dataSetCombK_BeautyMass", "Type":"Workspace",
    #                                                              "WeightName":"", "PIDVarName":"BacPIDK", "Variables":["BacPT","nTracks"]}
    #configdict["Calibrations"]["2012"]["Combinatorial"]["Down"] = { "FileName":"",
    #                                                              "WorkName":"workspace", "DataName":"dataSetCombK_BeautyMass", "Type":"Workspace",
    #                                                              "WeightName":"", "PIDVarName":"BacPIDK", "Variables":["BacPT","nTracks"]}

    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                               MDfit fitting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
    # Bs signal shapes
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All": 5.36878e+03}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"Run1": {"All": 2.88070e+01}, "Fixed":True}
    configdict["BsSignalShape"]["sigma2"]  = {"Run1": {"All": 1.64247e+01}, "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"Run1": {"All": 1.64214e+00}, "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"Run1": {"All":-2.96373e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"Run1": {"All": 1.26124e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"Run1": {"All": 1.00558e+00}, "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"Run1": {"All": 3.37315e-01}, "Fixed":True}
    
    # Ds signal shapes
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All": 2.11000e+03}, "Fixed":False}
    configdict["DsSignalShape"]["sigma1"]  = {"Run1": {"All": 1.20976e+01},  "Fixed":True} 
    configdict["DsSignalShape"]["sigma2"]  = {"Run1": {"All": 5.94917e+00},  "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"Run1": {"All": 1.40152e+00},  "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"Run1": {"All":-2.98478e-01}, "Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"Run1": {"All": 1.44311e+02},  "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"Run1": {"All": 2.83105e+00},  "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"Run1": {"All": 5.66652e-01},  "Fixed":True}

    # combinatorial background              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"] = "RooKeysPdf"
    configdict["BsCombinatorialShape"]["name"] = {"2012": {"NonRes": "PhysBkgCombK_BeautyMassPdf_m_both_nonres_2012",
                                                           "PhiPi":  "PhysBkgCombK_BeautyMassPdf_m_both_phipi_2012",
                                                           "KstK":   "PhysBkgCombK_BeautyMassPdf_m_both_kstk_2012",
                                                           "KPiPi":  "PhysBkgCombK_BeautyMassPdf_m_both_kpipi_2012",
                                                           "PiPiPi": "PhysBkgCombK_BeautyMassPdf_m_both_pipipi_2012"},
                                                  "2011": {"NonRes": "PhysBkgCombK_BeautyMassPdf_m_both_nonres_2011",
                                                           "PhiPi":  "PhysBkgCombK_BeautyMassPdf_m_both_phipi_2011",
                                                           "KstK":   "PhysBkgCombK_BeautyMassPdf_m_both_kstk_2011",
                                                           "KPiPi":  "PhysBkgCombK_BeautyMassPdf_m_both_kpipi_2011",
                                                           "PiPiPi": "PhysBkgCombK_BeautyMassPdf_m_both_pipipi_2011"}}

    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusSignal" 
    configdict["DsCombinatorialShape"]["cD"]    = {"Run1": {"NonRes":-0.05, "PhiPi":-0.05, "KstK":-0.05, "KPiPi":-0.05, "PiPiPi":-0.05}, "Fixed":False}
    configdict["DsCombinatorialShape"]["fracD"] = {"Run1": {"NonRes":0.5,   "PhiPi":0.5,   "KstK":0.5,   "KPiPi":1.0,   "PiPiPi":1.0},   "Fixed":{"KPiPi":True, "PiPiPi":True}}

    configdict["PIDKCombinatorialShape"] = {}
    configdict["PIDKCombinatorialShape"]["type"] = "Fixed"
    configdict["PIDKCombinatorialShape"]["components"] = { "Kaon":True, "Pion":True, "Proton":False }
    configdict["PIDKCombinatorialShape"]["fracPIDK1"]   = { "Run1":{"All":0.7}, "Fixed":False }

    configdict["Bd2Ds(st)XShape"] = {}
    configdict["Bd2Ds(st)XShape"]["type"]    = "ShiftedSignal"
    configdict["Bd2Ds(st)XShape"]["decay"]   = "Bd2DsstK"
    configdict["Bd2Ds(st)XShape"]["shift"]   = {"Run1": {"All": 86.8}, "Fixed":True}
    configdict["Bd2Ds(st)XShape"]["scale1"]  = {"Run1": {"All": 0.998944636665}, "Fixed":True}
    configdict["Bd2Ds(st)XShape"]["scale2"]  = {"Run1": {"All": 1.00022181515}, "Fixed":True}

    configdict["AdditionalParameters"] = {}
    configdict["AdditionalParameters"]["g1_f1_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":0.6, "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["g1_f2_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":0.4,  "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["g2_f1_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":0.7,  "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["g3_f1_frac"] = {"Run1":{"All":{"Both":{ "CentralValue":0.7,  "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["g3_f2_frac"] = {"Run1":{"NonRes":{"Both":{ "CentralValue":0.6,  "Range":[0.0,1.0]}},
                                                                "PhiPi":{"Both":{ "CentralValue":0.6,  "Range":[0.0,1.0]}},
                                                                "KstK":{"Both":{ "CentralValue":0.6,  "Range":[0.0,1.0]}},
                                                                "KPiPi":{"Both":{ "CentralValue":0.6,  "Range":[0.0,1.0]}},
                                                                "PiPiPi":{"Both":{ "CentralValue":0.6,  "Range":[0.0,1.0]}}}, "Fixed":False}
    configdict["AdditionalParameters"]["g4_f1_frac"] = {"Run1":{"NonRes":{"Both":{ "CentralValue":0.8, "Range":[0.5,1.0]}}, 
                                                                "PhiPi":{"Both":{ "CentralValue":0.8, "Range":[0.5,1.0]}},
                                                                "KstK":{"Both":{ "CentralValue":0.8, "Range":[0.5,1.0]}},
                                                                "KPiPi":{"Both":{ "CentralValue":0.8, "Range":[0.5,1.0]}},
                                                                "PiPiPi":{"Both":{ "CentralValue":0.8, "Range":[0.5,1.0]}}}, "Fixed":False}

    #expected yields                                                                                                                                                       
    configdict["Yields"] = {}
    #configdict["Yields"]["Bs2DsDsstRho"]   = {"Run1": {"NonRes":1000.0, "PhiPi":1000.0, "KstK":1000.0, "KPiPi":1000.0, "PiPiPi":100.0},  "Fixed":False}
    #configdict["Yields"]["Bd2DsstK"]       = {"Run1": {"NonRes":150.0,  "PhiPi":150.0,  "KstK":150.0,  "KPiPi":150.0,  "PiPiPi":150.0},  "Fixed":False}
    #configdict["Yields"]["Bs2DsstPi"]      = {"Run1": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0},  "Fixed":False}
    #configdict["Yields"]["BsBd2DsKst"]     = {"Run1": {"NonRes":100.0,  "PhiPi":100.0,  "KstK":100.0,  "KPiPi":100.0,  "PiPiPi":100.0},  "Fixed":False}
    #configdict["Yields"]["BsBd2DsstKst"]   = {"Run1": {"NonRes":700.0,  "PhiPi":700.0,  "KstK":700.0,  "KPiPi":700.0,  "PiPiPi":700.0},  "Fixed":False}
    #configdict["Yields"]["CombBkg"]        = {"Run1": {"NonRes":2000.0, "PhiPi":1500.0, "KstK":1500.0, "KPiPi":1500.0, "PiPiPi":1500.0}, "Fixed":False}
    #configdict["Yields"]["Signal"]         = {"Run1": {"NonRes":1000.0, "PhiPi":1000.0, "KstK":1000.0, "KPiPi":1000.0, "PiPiPi":1000.0}, "Fixed":False}

    configdict["Yields"]["Bs2DsDsstRho"]   = {"2012": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0},  
                                              "2011": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0}, "Fixed":False}
    configdict["Yields"]["Bd2DsstK"]       = {"2012": {"NonRes":150.0,  "PhiPi":150.0,  "KstK":100.0,  "KPiPi":50.0,   "PiPiPi":50.0},
                                              "2011": {"NonRes":150.0,  "PhiPi":150.0,  "KstK":100.0,  "KPiPi":50.0,   "PiPiPi":50.0}, "Fixed":False}
    configdict["Yields"]["Bs2DsstPi"]      = {"2012": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0},
                                              "2011": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0}, "Fixed":False}
    configdict["Yields"]["BsBd2DsKst"]     = {"2012": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0},
                                              "2011": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0}, "Fixed":False}
    configdict["Yields"]["BsBd2DsstKst"]   = {"2012": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0},
                                              "2011": {"NonRes":500.0,  "PhiPi":500.0,  "KstK":500.0,  "KPiPi":500.0,  "PiPiPi":500.0}, "Fixed":False}
    configdict["Yields"]["CombBkg"]        = {"2012": {"NonRes":5000.0, "PhiPi":5000.0, "KstK":5000.0, "KPiPi":5000.0, "PiPiPi":5000.0},
                                              "2011": {"NonRes":5000.0, "PhiPi":5000.0, "KstK":5000.0, "KPiPi":5000.0, "PiPiPi":5000.0}, "Fixed":False}
    configdict["Yields"]["Signal"]         = {"2012": {"NonRes":1000.0, "PhiPi":1000.0, "KstK":1000.0, "KPiPi":1000.0, "PiPiPi":1000.0},
                                              "2011": {"NonRes":1000.0, "PhiPi":1000.0, "KstK":1000.0, "KPiPi":1000.0, "PiPiPi":1000.0}, "Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#    
    ###                                                               MDfit plotting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#

    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = ["Sig", "CombBkg", "Bs2DsDsstRho", "BsBd2DsstKst", "Bd2DsstK"]
    configdict["PlotSettings"]["colors"] = [kRed-7, kBlue-6, kOrange, kMagenta-2, kBlue-10, kRed+1, kBlue+2]
    #configdict["PlotSettings"]["components"] = ["Sig", "CombBkg", "Bs2DsRho", "Bs2DsstRho"]
    #configdict["PlotSettings"]["colors"] = [kRed-7, kBlue-6, kBlue-10, kGreen+3]

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.7,0.9]}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.7,0.9],
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.7,0.9], 
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075}

    return configdict
