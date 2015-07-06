def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bs2DsstPi"
    configdict["CharmModes"] = {"KKPi"}
    # year of data taking                                                                                                                          
    configdict["YearOfDataTaking"] = {"2012","2011"}
    # stripping (necessary in case of PIDK shapes)                                                                                              
    configdict["Stripping"] = {"2012":"20", "2011":"20r1"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)                                                                  
    configdict["IntegratedLuminosity"] = {"2011":{"Down": 0.59, "Up": 0.44}, "2012":{"Down": 0.59, "Up": 0.44}}
    # file name with paths to MC/data samples                                                                                                       
    configdict["dataName"]   = "../data/config_Bs2DsstPi_old.txt"

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5100,    6000    ], "InputName" : "FBs_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1950,    1990    ], "InputName" : "FDs_M"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [0.4,     15.0    ], "InputName" : "FBs_LF_ctau"}
    configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "FBac_P"}
    configdict["BasicVariables"]["BacPT"]         = { "Range" : [1000.0,  45000.0 ], "InputName" : "FBac_PT"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [0.0,     150.0   ], "InputName" : "FBac_PIDK"}
    configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "FnTracks"}
    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "FBs_LF_ctauErr"}
    configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "FBac_ID"}
    configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.0,     1.0     ], "InputName" : "FBDT_Var"}
    configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "FBs_TAGDECISION_OS"}
    configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "FBs_SS_nnetKaon_DEC"}
    configdict["BasicVariables"]["MistagOS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "FBs_TAGOMEGA_OS"}
    configdict["BasicVariables"]["MistagSS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "FBs_SS_nnetKaon_PROB"}

    # tagging calibration                                                                                               
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.3834, "p1": 0.9720, "average": 0.3813}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4244, "p1": 1.2180, "average": 0.4097}

    # additional cuts applied to data sets
    configdict["AdditionalCuts"] = {}
    configdict["AdditionalCuts"]["All"]    = { "Data": "FDelta_R<1.0&&FDelta_M>124.&&FDelta_M<164.&&((FDsBac_M-FDs_M)<3370||(FDsBac_M-FDs_M)>3440)",
                                               "MC" : ""}

    configdict["CreateRooKeysPdfForCombinatorial"] = {}
    configdict["CreateRooKeysPdfForCombinatorial"]["BeautyMass"] = {"Cut":"FDelta_R<1.0&&FDelta_M>185.&&FDelta_M<205&&((FDsBac_M-FDs_M)<3370||(FDsBac_M-FDs_M)>3440)&&FBDT_Var>0&&FBac_PIDK<0&&FBs_M>5100&&FBs_M<6000&&FDs_M>1950&&FDs_M<1990",
                                                                    "Rho":3.5, "Mirror":"Both"}

    #weighting for PID templates                                                                                                                                                 
    configdict["ObtainPIDTemplates"] = { "Variables":["BacPT","nTracks"], "Bins":[20,20] }
    configdict["Calibrations"] = {}
    configdict["Calibrations"]["Pion"]   = { "FileNameUp":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID0_Str20.root",
                                            "FileNameDown":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID0_Str20.root",
                                             "WorkName":"RSDStCalib"}
    configdict["Calibrations"]["Kaon"]   = { "FileNameUp":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID0_Str20.root",
                                             "FileNameDown":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID0_Str20.root",
                                             "WorkName":"RSDStCalib"}
    configdict["Calibrations"]["Combinatorial"]   = { "FileNameUp":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root",
                                                      "FileNameDown":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root",
                                                      "WorkName":"workspace"}

    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                               MDfit fitting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
    # Bs signal shapes                                                                                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBallWithWidthRatio"
    configdict["BsSignalShape"]["mean"]    = {"All":5367.51}
    configdict["BsSignalShape"]["sigma1"]  = {"2012": {"KKPi":2.80080e+01},  "2011":{"KKPi":2.80080e+01}}
    configdict["BsSignalShape"]["sigma2"]  = {"2012": {"KKPi":2.00892e+01},  "2011":{"KKPi":2.00892e+01}}
    configdict["BsSignalShape"]["alpha1"]  = {"2012": {"KKPi":1.87906e+00},  "2011":{"KKPi":1.87906e+00},  "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"2012": {"KKPi":-2.45124e+00}, "2011":{"KKPi":-2.45124e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"2012": {"KKPi":1.24093e+00},  "2011":{"KKPi":1.24093e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"2012": {"KKPi":1.78009e+00},  "2011":{"KKPi":1.78009e+00}, "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"2012": {"KKPi":4.66783e-01},  "2011":{"KKPi":4.66783e-01}, "Fixed":True}

    #Ds signal shapes                                                                                                                                       
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["DsSignalShape"]["mean"]    = {"All":1968.49}
    configdict["DsSignalShape"]["sigma1"]  = {"2012": {"KKPi":4.3930e+00}, "2011":{"KKPi":4.3930e+00},  "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"2012": {"KKPi":7.1493e+00}, "2011":{"KKPi":7.1493e+00},  "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"2012": {"KKPi":2.1989e+00}, "2011":{"KKPi":2.1989e+00},  "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"2012": {"KKPi":-2.0186e+00},"2011":{"KKPi":-2.0186e+00}, "Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"2012": {"KKPi":7.9389e-01}, "2011":{"KKPi":7.9389e-01},  "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"2012": {"KKPi":5.5608e+00}, "2011":{"KKPi":5.5608e+00},  "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"2012": {"KKPi":0.25406},     "2011":{"KKPi":0.25406},     "Fixed":True}

    # combinatorial background                                                                                                                              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"] = "ExponentialPlusGauss"
    #configdict["BsCombinatorialShape"]["cB"]         = {"2012": {"KKPi":-0.00354546}, "2011":{"KKPi":-0.00354546},   "Fixed":False}
    #configdict["BsCombinatorialShape"]["fracCombB"]  = {"2012": {"KKPi":0.3},         "2011":{"KKPi":0.3},           "Fixed":True}
    #configdict["BsCombinatorialShape"]["meanComb"]   = {"2012": {"KKPi":5299.22},     "2011":{"KKPi":5299.22},       "Fixed":True}
    #configdict["BsCombinatorialShape"]["widthComb"]  = {"2012": {"KKPi":182.448},     "2011":{"KKPi":182.448},       "Fixed":True}
    configdict["BsCombinatorialShape"]["type"] = "RooKeysPdf"
    configdict["BsCombinatorialShape"]["name"] = {"2012": {"KKPi":"PhysBkgCombPi_BeautyMassPdf_m_both"},
                                                  "2011": {"KKPi":"PhysBkgCombPi_BeautyMassPdf_m_both"}}

    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusSignal" 
    configdict["DsCombinatorialShape"]["cD"]        = {"2012": {"KKPi":-2.7520e-03}, "2011": {"KKPi":-2.7520e-03}, "Fixed":False}
    configdict["DsCombinatorialShape"]["fracCombD"] = {"2012": {"KKPi":0.88620},     "2011": {"KKPi":0.88620},     "Fixed":False}

    configdict["PIDKCombinatorialShape"] = {}
    configdict["PIDKCombinatorialShape"]["type"] = "Fixed"
    configdict["PIDKCombinatorialShape"]["components"] = { "Kaon":True, "Pion":True, "Proton":False }
    configdict["PIDKCombinatorialShape"]["fracPIDK"]   = { "2011":{"fracPIDK1":0.5}, "Fixed":False }

    #expected yields                                                                                                                                                       
    configdict["Yields"] = {}
    configdict["Yields"]["Bs2DsstRho"] = {"2012": { "KKPi":20000.0} ,  "2011": { "KKPi":20000.0}, "Fixed":False}
    configdict["Yields"]["Bs2DsRho"]   = {"2012": { "KKPi":20000.0},   "2011": { "KKPi":20000.0}, "Fixed":False}
    configdict["Yields"]["CombBkg"]    = {"2012": { "KKPi":20000.0},   "2011": { "KKPi":20000.0}, "Fixed":False}
    configdict["Yields"]["Signal"]     = {"2012": { "KKPi":20000.0},   "2011": { "KKPi":20000.0}, "Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#    
    ###                                                               MDfit plotting settings                                                             
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#               
    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = ["Sig", "CombBkg", "Bs2DsRho", "Bs2DsstRho"] 
    configdict["PlotSettings"]["colors"] = [kRed-7, kBlue-6, kBlue-10, kGreen+3]

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9], "ScaleYSize":2.5}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.7, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9], "ScaleYSize":1.2}

    return configdict
