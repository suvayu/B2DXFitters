def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bs2DsstPi"
    configdict["CharmModes"] = {"NonRes", "PhiPi", "KstK"}
    # year of data taking                                                                                 
    configdict["YearOfDataTaking"] = {"2012"} #, "2011"}
    # stripping (necessary in case of PIDK shapes)                               
    configdict["Stripping"] = {"2012":"21", "2011":"21r1"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)
    configdict["IntegratedLuminosity"] = {"2011":{"Down": 0.59, "Up": 0.44}, "2012":{"Down": 0.59, "Up": 0.44}}
    # file name with paths to MC/data samples                                     
    configdict["dataName"]   = "../data/Bs2DsstK_3fbCPV/config_Bs2DsstPi.txt"

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5100,    6000    ], "InputName" : "FBs_DeltaM_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [2080,    2150    ], "InputName" : "FDsstr_DeltaM_M"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.0,     1.e+9   ], "InputName" : "FBs_LF_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [1000.,   650000.0], "InputName" : "FBac_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [1000.,   45000.0 ], "InputName" : "FBac_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [0.0,     150,    ], "InputName" : "FBac_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.,     1000.0  ], "InputName" : "FnTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.0,     1.e+9   ], "InputName" : "FBs_LF_ctauErr"}
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
    configdict["AdditionalCuts"]["All"]    = { "Data": "FDs_M>1950.&&FDs_M<1990.&&FDs_FDCHI2_ORIVX>2.&&FDelta_M>111.5&&FDelta_M<181.5&&FBs_Veto==0.&&FBDT_Var>0.025",
                                               "MC":   "FDs_M>1950.&&FDs_M<1990.&&FDs_FDCHI2_ORIVX>2.&&FDelta_M>111.5&&FDelta_M<181.5&&FBs_Veto==0.&&FBDT_Var>0.025"}
    configdict["AdditionalCuts"]["NonRes"] = { "Data":"FDs_Dec==3", "MC":"FDs_Dec==3"}
    configdict["AdditionalCuts"]["PhiPi"]  = { "Data":"FDs_Dec==1", "MC":"FDs_Dec==1"}
    configdict["AdditionalCuts"]["KstK"]   = { "Data":"FDs_Dec==2", "MC":"FDs_Dec==2"}
 
    configdict["CreateRooKeysPdfForCombinatorial"] = {}
    configdict["CreateRooKeysPdfForCombinatorial"]["BeautyMass"] = {} 
    configdict["CreateRooKeysPdfForCombinatorial"]["BeautyMass"]["All"]    = {"Cut":"FBs_DeltaM_M>5100&&FDs_M>1950.&&FDs_M<1990.&&FDs_FDCHI2_ORIVX>2.&&FDelta_M>205.&&FDelta_M<215.&&FBs_Veto==0.&&FBDT_Var>0.025&&FBac_P>1000.0&&FBac_P<650000.0&&FBac_PT>1000.0&&FBac_PT<45000.0",
                                                                              "Rho":2.0, "Mirror":"LeftAsymRigh"}
    configdict["CreateRooKeysPdfForCombinatorial"]["BeautyMass"]["NonRes"] = {"Cut":"FDs_Dec==3"}
    configdict["CreateRooKeysPdfForCombinatorial"]["BeautyMass"]["PhiPi"]  = {"Cut":"FDs_Dec==1"}
    configdict["CreateRooKeysPdfForCombinatorial"]["BeautyMass"]["KstK"]   = {"Cut":"FDs_Dec==2"}
        
    #weighting for PID templates                                                                                                                                                    
    configdict["ObtainPIDTemplates"] = { "Variables":["BacPT","nTracks"], "Bins":[20,20] }

    #PID Calibration samples for PID shapes
    configdict["Calibrations"] = {}
    configdict["Calibrations"]["2011"] = {}
    configdict["Calibrations"]["2011"]["Pion"]   = {}
    configdict["Calibrations"]["2011"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID0_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID0_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]   = {}
    configdict["Calibrations"]["2011"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID0_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID0_Str20r1.root"}
    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { "FileName":"",
                                                                  "WorkName":"workspace", "DataName":"dataSetCombPi_BeautyMass", "Type":"Workspace",
                                                                  "WeightName":"", "PIDVarName":"BacPIDK", "Variables":["BacPT","nTracks"]}
    configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { "FileName":"",
                                                                  "WorkName":"workspace", "DataName":"dataSetCombPi_BeautyMass", "Type":"Workspace",
                                                                  "WeightName":"", "PIDVarName":"BacPIDK", "Variables":["BacPT","nTracks"]}


    configdict["Calibrations"]["2012"] = {}
    configdict["Calibrations"]["2012"]["Pion"]   = {}
    configdict["Calibrations"]["2012"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID0_Str20.root"}
    configdict["Calibrations"]["2012"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID0_Str20.root"}
    configdict["Calibrations"]["2012"]["Kaon"]   = {}
    configdict["Calibrations"]["2012"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID0_Str20.root"}
    configdict["Calibrations"]["2012"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID0_Str20.root"}
    configdict["Calibrations"]["2012"]["Combinatorial"]   = {}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Up"] = { "FileName":"",
                                                                  "WorkName":"workspace", "DataName":"dataSetCombPi_BeautyMass", "Type":"Workspace",
                                                                  "WeightName":"", "PIDVarName":"BacPIDK", "Variables":["BacPT","nTracks"]}
    configdict["Calibrations"]["2012"]["Combinatorial"]["Down"] = { "FileName":"",
                                                                  "WorkName":"workspace", "DataName":"dataSetCombPi_BeautyMass", "Type":"Workspace",
                                                                  "WeightName":"", "PIDVarName":"BacPIDK", "Variables":["BacPT","nTracks"]}



    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                               MDfit fitting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
    # Bs signal shapes
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["BsSignalShape"]["mean"]    = {"All":5.36878e+03}
    configdict["BsSignalShape"]["sigma1"]  = {"2012": {"NonRes":2.88070e+01, "PhiPi":2.88070e+01, "KstK":2.88070e+01, "KPiPi":2.88070e+01, "PiPiPi":2.88070e+01},
                                              "2011": {"NonRes":28.8, "PhiPi":28.8, "KstK":28.8, "KPiPi":28.8, "PiPiPi":28.8}, "Fixed":True}
    configdict["BsSignalShape"]["sigma2"]  = {"2012": {"NonRes":1.64247e+01, "PhiPi":1.64247e+01, "KstK":1.64247e+01, "KPiPi":1.64247e+01, "PiPiPi":1.64247e+01},
                                              "2011": {"NonRes":16.4, "PhiPi":16.4, "KstK":16.4, "KPiPi":16.4, "PiPiPi":16.4}, "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"2012": {"NonRes":1.64214e+00, "PhiPi":1.64214e+00, "KstK":1.64214e+00, "KPiPi":1.64214e+00, "PiPiPi":1.64214e+00},
                                              "2011": {"NonRes":1.64, "PhiPi":1.64, "KstK":1.64, "KPiPi":1.64, "PiPiPi":1.64}, "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"2012": {"NonRes":-2.96373e+00, "PhiPi":-2.96373e+00, "KstK":-2.96373e+00, "KPiPi":-2.96373e+00, "PiPiPi":-2.96373e+00},
                                              "2011": {"NonRes":-2.9, "PhiPi":-2.9, "KstK":-2.9, "KPiPi":-2.9, "PiPiPi":-2.9}, "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"2012": {"NonRes":1.26124e+00, "PhiPi":1.26124e+00, "KstK":1.26124e+00, "KPiPi":1.26124e+00, "PiPiPi":1.26124e+00},
                                              "2011": {"NonRes":126., "PhiPi":126., "KstK":126., "KPiPi":126., "PiPiPi":126.},  "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"2012": {"NonRes":1.00558e+00, "PhiPi":1.00558e+00, "KstK":1.00558e+00, "KPiPi":1.00558e+00, "PiPiPi":1.00558e+00},
                                              "2011": {"NonRes":1.00, "PhiPi":1.00, "KstK":1.00, "KPiPi":1.00, "PiPiPi":1.00},  "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"2012": {"NonRes":3.37315e-01, "PhiPi":3.37315e-01, "KstK":3.37315e-01, "KPiPi":3.37315e-01, "PiPiPi":3.37315e-01},
                                              "2011": {"NonRes":0.33, "PhiPi":0.33, "KstK":0.33, "KPiPi":0.33, "PiPiPi":0.33}, "Fixed":True}

    #configdict["BsSignalShape"] = {}
    #configdict["BsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    #configdict["BsSignalShape"]["mean"]    = {"All":5367.51}
    #configdict["BsSignalShape"]["sigma1"]  = {"2012": {"All":2.80080e+01},    "2011": {"All":2.80080e+01}, "Fixed":True}
    #configdict["BsSignalShape"]["sigma2"]  = {"2012": {"All":2.00892e+01},    "2011": {"All":2.00892e+01}, "Fixed":True}
    #configdict["BsSignalShape"]["alpha1"]  = {"2012": {"All":1.87906e+00},    "2011": {"All":1.87906e+00},  "Fixed":True}
    #configdict["BsSignalShape"]["alpha2"]  = {"2012": {"All":-2.45124e+00},   "2011": {"All":-2.45124e+00}, "Fixed":True}
    #configdict["BsSignalShape"]["n1"]      = {"2012": {"All":1.24093e+00},    "2011": {"All":1.24093e+00}, "Fixed":True}
    #configdict["BsSignalShape"]["n2"]      = {"2012": {"NonRes":1.00000e+01}, "2011": {"NonRes":1.00000e+01}, "Fixed":True}
    #configdict["BsSignalShape"]["frac"]    = {"2012": {"NonRes":4.66783e-01}, "2011": {"NonRes":4.66783e-01}, "Fixed":True}
    
    # Ds signal shapes
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["DsSignalShape"]["mean"]    = {"All":2.11000e+03}
    configdict["DsSignalShape"]["sigma1"]  = {"2012": {"NonRes":1.20976e+01, "PhiPi":1.20976e+01, "KstK":1.20976e+01, "KPiPi":1.20976e+01, "PiPiPi":1.20976e+01},
                                              "2011": {"NonRes":12.0, "PhiPi":12.0, "KstK":12.0, "KPiPi":12.0, "PiPiPi":12.0}, "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"2012": {"NonRes":5.94917e+00, "PhiPi":5.94917e+00, "KstK":5.94917e+00, "KPiPi":5.94917e+00, "PiPiPi":5.94917e+00},
                                              "2011": {"NonRes":5.94, "PhiPi":5.94, "KstK":5.94, "KPiPi":5.94, "PiPiPi":5.94}, "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"2012": {"NonRes":1.40152e+00, "PhiPi":1.40152e+00, "KstK":1.40152e+00, "KPiPi":1.40152e+00, "PiPiPi":1.40152e+00},
                                              "2011": {"NonRes":1.40, "PhiPi":1.40, "KstK":1.40, "KPiPi":1.40, "PiPiPi":1.40}, "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"2012": {"NonRes":-2.98478e-01, "PhiPi":-2.98478e-01, "KstK":-2.98478e-01, "KPiPi":-2.98478e-01, "PiPiPi":-2.98478e-01},
                                              "2011": {"NonRes":-0.2, "PhiPi":-0.2, "KstK":-0.2, "KPiPi":-0.2, "PiPiPi":-0.2}, "Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"2012": {"NonRes":1.44311e+02, "PhiPi":1.44311e+02, "KstK":1.44311e+02, "KPiPi":1.44311e+02, "PiPiPi":1.44311e+02},
                                              "2011": {"NonRes":144., "PhiPi":144., "KstK":144., "KPiPi":144., "PiPiPi":144.}, "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"2012": {"NonRes":2.83105e+00, "PhiPi":2.83105e+00, "KstK":2.83105e+00, "KPiPi":2.83105e+00, "PiPiPi":2.83105e+00},
                                              "2011": {"NonRes":2.83, "PhiPi":2.83, "KstK":2.83, "KPiPi":2.83, "PiPiPi":2.83}, "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"2012": {"NonRes":5.66652e-01, "PhiPi":5.66652e-01, "KstK":5.66652e-01, "KPiPi":5.66652e-01, "PiPiPi":5.66652e-01},
                                              "2011": {"NonRes":0.56, "PhiPi":0.56, "KstK":0.56, "KPiPi":0.56, "PiPiPi":0.56}, "Fixed":True}

    #configdict["DsSignalShape"] = {}
    #configdict["DsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    #configdict["DsSignalShape"]["mean"]    = {"All":2110.0}
    #configdict["DsSignalShape"]["sigma1"]  = {"2012": {"NonRes":1.2354e+01,  "PhiPi":1.2354e+01,  "KstK":1.2354e+01},  
    #                                          "2011": {"NonRes":1.2354e+01,  "PhiPi":1.2354e+01,  "KstK":1.2354e+01}, "Fixed":True}
    #configdict["DsSignalShape"]["sigma2"]  = {"2012": {"NonRes":5.8237e+00,  "PhiPi":5.8237e+00,  "KstK":5.8237e+00},
    #                                          "2011": {"NonRes":5.8237e+00,  "PhiPi":5.8237e+00,  "KstK":5.8237e+00}, "Fixed":True}
    #configdict["DsSignalShape"]["alpha1"]  = {"2012": {"NonRes":1.5841e+00,  "PhiPi":1.5841e+00,  "KstK":1.5841e+00},
    #                                          "2011": {"NonRes":1.5841e+00,  "PhiPi":1.5841e+00,  "KstK":1.5841e+00},  "Fixed":True}
    #configdict["DsSignalShape"]["alpha2"]  = {"2012": {"NonRes":-3.4618e-01, "PhiPi":-3.4618e-01, "KstK":-3.4618e-01}, 
    #                                          "2011": {"NonRes":-3.4618e-01, "PhiPi":-3.4618e-01, "KstK":-3.4618e-01}, "Fixed":True}
    #configdict["DsSignalShape"]["n1"]      = {"2012": {"NonRes":1.5304e+02,  "PhiPi":1.5304e+02,  "KstK":1.5304e+02},
    #                                          "2011": {"NonRes":1.5304e+02,  "PhiPi":1.5304e+02,  "KstK":1.5304e+02},  "Fixed":True}
    #configdict["DsSignalShape"]["n2"]      = {"2012": {"NonRes":1.3448e+00,  "PhiPi":1.3448e+00,  "KstK":1.3448e+00},  
    #                                          "2011": {"NonRes":1.3448e+00,  "PhiPi":1.3448e+00,  "KstK":1.3448e+00},  "Fixed":True}
    #configdict["DsSignalShape"]["frac"]    = {"2012": {"NonRes":5.8411e-01,  "PhiPi":5.8411e-01,  "KstK":5.8411e-01},
    #                                          "2011": {"NonRes":5.8411e-01,  "PhiPi":5.8411e-01,  "KstK":5.8411e-01}, "Fixed":True}

    # combinatorial background              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"] = "ExponentialPlusGauss"
    configdict["BsCombinatorialShape"]["cB"]         = {"2012": {"NonRes":-0.0036,     "PhiPi":-0.00317006, "KstK":-0.00368556}, 
                                                        "2011": {"NonRes":-0.0036,     "PhiPi":-0.00317006, "KstK":-0.00368556},   "Fixed":False}
    configdict["BsCombinatorialShape"]["fracCombB"]  = {"2012": {"NonRes":0.25,        "PhiPi":0.2,         "KstK":0.2}, 
                                                        "2011": {"NonRes":0.25,        "PhiPi":0.2,         "KstK":0.2},           "Fixed":True}
    configdict["BsCombinatorialShape"]["meanComb"]   = {"2012": {"NonRes":5212.03,     "PhiPi":5229.96,     "KstK":5219.37},
                                                        "2011": {"NonRes":5212.03,     "PhiPi":5229.96,     "KstK":5219.37},       "Fixed":True}
    configdict["BsCombinatorialShape"]["widthComb"]  = {"2012": {"NonRes":211.266,     "PhiPi":163.297,     "KstK":170.787},
                                                        "2011": {"NonRes":211.266,     "PhiPi":163.297,     "KstK":170.787},       "Fixed":True}
    #configdict["BsCombinatorialShape"]["type"] = "RooKeysPdf"
    #configdict["BsCombinatorialShape"]["name"] = {"2012": {"NonRes":"PhysBkgCombPi_BeautyMassPdf_m_both_nonres_2012",
    #                                                       "PhiPi": "PhysBkgCombPi_BeautyMassPdf_m_both_phipi_2012",
    #                                                       "KstK": "PhysBkgCombPi_BeautyMassPdf_m_both_kstk_2012"},
    #                                              "2011": {"NonRes":"PhysBkgCombPi_BeautyMassPdf_m_both_nonres_2011",
    #                                                       "PhiPi": "PhysBkgCombPi_BeautyMassPdf_m_both_phipi_2011",
    #                                                       "KstK": "PhysBkgCombPi_BeautyMassPdf_m_both_kstk_2011"}}

    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusSignal" 
    configdict["DsCombinatorialShape"]["cD"]        = {"2012": {"NonRes":-0.05,       "PhiPi":-0.05,       "KstK":-0.05}, 
                                                       "2011": {"NonRes":-0.05,       "PhiPi":-0.05,       "KstK":-0.05}, "Fixed":False}
    configdict["DsCombinatorialShape"]["fracCombD"] = {"2012": {"NonRes":0.5,         "PhiPi":0.5,         "KstK":0.5}, 
                                                       "2011": {"NonRes":0.5,         "PhiPi":0.5,         "KstK":0.5},     "Fixed":False}

    configdict["PIDKCombinatorialShape"] = {}
    configdict["PIDKCombinatorialShape"]["type"] = "Fixed"
    configdict["PIDKCombinatorialShape"]["components"] = { "Kaon":True, "Pion":True, "Proton":False }
    configdict["PIDKCombinatorialShape"]["fracPIDK"]   = { "2011":{"fracPIDK1_2011":0.5}, "2012":{"fracPIDK1_2012":0.5},  "Fixed":False }

    #expected yields                                                                                                                                                       
    configdict["Yields"] = {}
    configdict["Yields"]["Bs2DsstRho"] = {"2012": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0},  
                                          "2011": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0}, "Fixed":False}
    configdict["Yields"]["Bd2DsstPi"] = {"2012": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0},
                                         "2011": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0}, "Fixed":False}
    configdict["Yields"]["Bs2DsRho"]   = {"2012": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0},
                                          "2011": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0}, "Fixed":False}
    configdict["Yields"]["CombBkg"]    = {"2012": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0},
                                          "2011": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0}, "Fixed":False}
    configdict["Yields"]["Signal"]     = {"2012": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0},
                                          "2011": { "NonRes":10000.0, "PhiPi":40000.0, "KstK":20000.0}, "Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#    
    ###                                                               MDfit plotting settings                                                             
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#               

    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = ["Sig", "CombBkg", "Bd2DsstPi", "Bs2DsRho", "Bs2DsstRho"]
    configdict["PlotSettings"]["colors"] = [kRed-7, kBlue-6, kOrange, kBlue-10, kGreen+3]


    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9]}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66], 
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075}

    return configdict
