def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # considered decay mode                                                       
    configdict["Decay"] = "Bs2DsPi"
    configdict["CharmModes"] = {"KKPi"}
    # year of data taking                                                                                                                          
    configdict["YearOfDataTaking"] = {"2011"}
    # stripping (necessary in case of PIDK shapes)                                                                                              
    configdict["Stripping"] = {"2011":"21"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes)                                                                  
    configdict["IntegratedLuminosity"] = {"2011": {"Down": 0.59, "Up": 0.44}}
    # file name with paths to MC/data samples                                                                                                       
    configdict["dataName"]   = "../data/Bs2DsK_3fbCPV/BDTG/Bs2DsPi/config_Bs2DsPi.txt"
    #settings for control plots                                                                                                                                                           
    configdict["ControlPlots"] = {}
    configdict["ControlPlots"] = { "Directory": "PlotBs2DsPi", "Extension":"pdf"}

    # basic variables                                                                                        
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5300,    5800    ], "InputName" : "lab0_MassFitConsD_M"}
#    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [5310,    5430    ], "InputName" : "lab0_MassFitConsD_M"}
    configdict["BasicVariables"]["CharmMass"]     = { "Range" : [1930,    2015    ], "InputName" : "lab2_MM"}
    configdict["BasicVariables"]["BeautyTime"]    = { "Range" : [-1000.0,     1000.0    ], "InputName" : "lab0_LifetimeFit_ctau"}
    #configdict["BasicVariables"]["BacP"]          = { "Range" : [3000.0,  650000.0], "InputName" : "lab1_P"}
    #configdict["BasicVariables"]["BacPT"]         = { "Range" : [400.0,   45000.0 ], "InputName" : "lab1_PT"}
#    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-7.0,     5.0   ], "InputName" : "lab1_PIDK"}
    configdict["BasicVariables"]["BacPIDK"]       = { "Range" : [-100000.0,   150     ], "InputName" : "lab1_PIDK"}
    #configdict["BasicVariables"]["nTracks"]       = { "Range" : [15.0,    1000.0  ], "InputName" : "nTracks"}
    #configdict["BasicVariables"]["BeautyTimeErr"] = { "Range" : [0.01,    0.1     ], "InputName" : "lab0_LifetimeFit_ctauErr"}
    #configdict["BasicVariables"]["BacCharge"]     = { "Range" : [-1000.0, 1000.0  ], "InputName" : "lab1_ID"}
    #configdict["BasicVariables"]["BDTG"]          = { "Range" : [0.3,     1.0     ], "InputName" : "BDTGResponse_1"}
    #configdict["BasicVariables"]["TagDecOS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_TAGDECISION_OS"}
    #configdict["BasicVariables"]["TagDecSS"]      = { "Range" : [-1.0,    1.0     ], "InputName" : "lab0_SS_nnetKaon_DEC"}
    #configdict["BasicVariables"]["MistagOS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_TAGOMEGA_OS"}
    #configdict["BasicVariables"]["MistagSS"]      = { "Range" : [ 0.0,    0.5     ], "InputName" : "lab0_SS_nnetKaon_PROB"}

    # tagging calibration                                                                                               
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.3834, "p1": 0.9720, "average": 0.3813}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4244, "p1": 1.2180, "average": 0.4097}

    # additional cuts applied to data sets                                                                                    
    #configdict["AdditionalCuts"] = {}
    #configdict["AdditionalCuts"]["All"]    = { "Data": "lab2_TAU>0",            "MC" : "lab2_TAU>0&&lab1_M<200", "MCID":True, "MCTRUEID":True, "BKGCAT":True, "DsHypo":True}
    #configdict["AdditionalCuts"]["KKPi"]   = { "Data": "lab2_FDCHI2_ORIVX > 2", "MC" : "lab2_FDCHI2_ORIVX > 2"}
    #configdict["AdditionalCuts"]["KPiPi"]  = { "Data": "lab2_FDCHI2_ORIVX > 9", "MC" : "lab2_FDCHI2_ORIVX > 9"}
    #configdict["AdditionalCuts"]["PiPiPi"] = { "Data": "lab2_FDCHI2_ORIVX > 9&&lab45_MM<1700", "MC" : "lab2_FDCHI2_ORIVX > 9"}

    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts                                                                                                              
    # order of particles: KKPi, KPiPi, PiPiPi                                                                                                         
    configdict["DsChildrenPrefix"] = {"Child1":"lab5","Child2":"lab4","Child3": "lab3"}

    # additional variables in data sets                                                                                                             
    configdict["AdditionalVariables"] = {}
    configdict["AdditionalVariables"]["lab0_DIRA_OWNPV"]                 =  { "Range" : [ -3.0, 2,0 ], "InputName" : "lab0_DIRA_OWNPV"}
    configdict["AdditionalVariables"]["lab0_MINIPCHI2"]                  =  { "Range" : [ -3.0, 7000,0 ], "InputName" : "lab0_MINIPCHI2"}
    configdict["AdditionalVariables"]["lab0_RFD"]                        =  { "Range" : [ -3.0, 18,0 ], "InputName" : "lab0_RFD"}
    configdict["AdditionalVariables"]["lab0_VCHI2NDOF"]                  =  { "Range" : [ -12.0, 12,0 ], "InputName" : "lab0_VCHI2NDOF"}
    configdict["AdditionalVariables"]["lab0_LifetimeFit_VCHI2NDOF"]      =  { "Range" : [ -10.0, 900,0 ], "InputName" : "lab0_LifetimeFit_VCHI2NDOF"}
    configdict["AdditionalVariables"]["lab2_DIRA_OWNPV"]                 =  { "Range" : [ -3.0, 3,0 ], "InputName" : "lab2_DIRA_OWNPV"}
    configdict["AdditionalVariables"]["lab2_DIRA_ORIVX"]                 =  { "Range" : [ -3.0, 3,0 ], "InputName" : "lab2_DIRA_ORIVX"}
    configdict["AdditionalVariables"]["lab2_MINIPCHI2"]                  =  { "Range" : [ -3.0, 180000,0 ], "InputName" : "lab2_MINIPCHI2"}
    configdict["AdditionalVariables"]["lab2_RFD"]                        =  { "Range" : [ -3.0, 20,0 ], "InputName" : "lab2_RFD"}
    configdict["AdditionalVariables"]["lab2_VCHI2NDOF"]                  =  { "Range" : [ -5.0, 12,0 ], "InputName" : "lab2_VCHI2NDOF"}
    configdict["AdditionalVariables"]["lab1_MINIPCHI2"]                  =  { "Range" : [ -3.0, 220000,0 ], "InputName" : "lab1_MINIPCHI2"}
    configdict["AdditionalVariables"]["lab1_PT"]                         =  { "Range" : [    0, 160000,0 ], "InputName" : "lab1_PT"}
    configdict["AdditionalVariables"]["lab1_CosTheta"]                   =  { "Range" : [    -3, 3,0 ], "InputName" : "lab1_CosTheta"}
    configdict["AdditionalVariables"]["lab345_MIN_PT"]                   =  { "Range" : [ -3.0, 14000,0 ], "InputName" : "lab345_MIN_PT"}
    configdict["AdditionalVariables"]["lab345_MIN_MINIPCHI2"]            =  { "Range" : [ -3.0, 28000,0 ], "InputName" : "lab345_MIN_MINIPCHI2"}
    configdict["AdditionalVariables"]["lab1345_TRACK_GhostProb"]         =  { "Range" : [ -3.0, 1,0 ], "InputName" : "lab1345_TRACK_GhostProb"}

    configdict["AdditionalVariables"]["lab0_DIRA_OWNPV_Log"]                 =  { "Range" : [ -3.0, 2,0 ], "InputName" : "lab0_DIRA_OWNPV_Log"}
    configdict["AdditionalVariables"]["lab0_LifetimeFit_VCHI2NDOF_Log"]      =  { "Range" : [ -12.0, 900,0 ], "InputName" : "lab0_LifetimeFit_VCHI2NDOF_Log"}
    configdict["AdditionalVariables"]["lab0_VCHI2NDOF_Log"]                  =  { "Range" : [ -12.0, 12,0 ], "InputName" : "lab0_VCHI2NDOF_Log"}
    configdict["AdditionalVariables"]["lab0_RFD_Log"]                        =  { "Range" : [ -3.0, 18,0 ], "InputName" : "lab0_RFD_Log"}
    configdict["AdditionalVariables"]["lab1_MINIPCHI2_Log"]                  =  { "Range" : [ -3.0, 220000,0 ], "InputName" : "lab1_MINIPCHI2_Log"}
    configdict["AdditionalVariables"]["lab1_PT_Log"]                         =  { "Range" : [    0, 160000,0 ], "InputName" : "lab1_PT_Log"}
    configdict["AdditionalVariables"]["lab2_MINIPCHI2_Log"]                  =  { "Range" : [ -3.0, 180000,0 ], "InputName" : "lab2_MINIPCHI2_Log"}
    configdict["AdditionalVariables"]["lab2_RFD_Log"]                        =  { "Range" : [ -3.0, 20,0 ], "InputName" : "lab2_RFD_Log"}
    configdict["AdditionalVariables"]["lab345_MIN_PT_Log"]                   =  { "Range" : [ -3.0, 14000,0 ], "InputName" : "lab345_MIN_PT_Log"}
    configdict["AdditionalVariables"]["lab345_MIN_MINIPCHI2_Log"]            =  { "Range" : [ -3.0, 28000,0 ], "InputName" : "lab345_MIN_MINIPCHI2_Log"}
    configdict["AdditionalVariables"]["NewBDTG_classifier"]                  =  { "Range" : [ -3.0, 28000,0 ], "InputName" : "NewBDTG_classifier"}


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
#    configdict["WeightingMassTemplates"]= { "Variables":["lab4_P","lab5_P"], "PIDBach": 0, "PIDChild": 0, "PIDProton": 5, "RatioDataMC":True }

    #weighting for PID templates                                                                                                                                                          
#    configdict["ObtainPIDTemplates"] = { "Variables":["BacPT","nTracks"], "Bins":[20,20] }
#    configdict["Calibrations"] = {}
#    configdict["Calibrations"]["2011"] = {}
#    configdict["Calibrations"]["2011"]["Pion"]   = {}
#    configdict["Calibrations"]["2011"]["Pion"]["Up"]   = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_Pi_PID0_Str20r1.root"}
#    configdict["Calibrations"]["2011"]["Pion"]["Down"] = {"FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_Pi_PID0_Str20r1.root"}
#    configdict["Calibrations"]["2011"]["Kaon"]   = {}
#    configdict["Calibrations"]["2011"]["Kaon"]["Up"]   = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Up_K_PID0_Str20r1.root"}
#    configdict["Calibrations"]["2011"]["Kaon"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/CalibrationSamples/CalibDst_Down_K_PID0_Str20r1.root"}
#    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
#    configdict["Calibrations"]["2011"]["Combinatorial"]   = {}
#    configdict["Calibrations"]["2011"]["Combinatorial"]["Up"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root",
#                                                                  "WorkName":"workspace", "DataName":"dataCombBkg_up", "Type":"Special",
#                                                                  "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
#    configdict["Calibrations"]["2011"]["Combinatorial"]["Down"] = { "FileName":"/afs/cern.ch/work/a/adudziak/public/workspace/work_Comb_DsPi_5358.root",
#                                                                    "WorkName":"workspace", "DataName":"dataCombBkg_down", "Type":"Special",
#                                                                    "WeightName":"sWeights", "PIDVarName":"lab1_PIDK", "Variables":["lab1_PT","nTracks"]}
#

    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                               MDfit fitting settings
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
    # Bs signal shapes                                                                                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5.3656e+03}, "Fixed":False}
    configdict["BsSignalShape"]["sigma1"]  = {"2011": {"KKPi":1.2859e+01},  "Fixed":False}
    configdict["BsSignalShape"]["sigma2"]  = {"2011": {"KKPi":1.9039e+01},  "Fixed":False}
#    configdict["BsSignalShape"]["mean"]    = {"Run1": {"All":5.3657e+03}, "Fixed":True}
#    configdict["BsSignalShape"]["sigma1"]  = {"2011": {"KKPi":1.9404e+01},  "Fixed":True}
#    configdict["BsSignalShape"]["sigma2"]  = {"2011": {"KKPi":1.3594e+01},  "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"2011": {"KKPi":-2.0856e+00}, "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"2011": {"KKPi":1.8947e+00},  "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"2011": {"KKPi":5.2735e+00},  "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"2011": {"KKPi":1.1497e+00},  "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"2011": {"KKPi":4.4171e-01},  "Fixed":True}


    #Ds signal shapes
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["DsSignalShape"]["mean"]    = {"Run1": {"All":1968.49}, "Fixed":False}
    configdict["DsSignalShape"]["sigma1"]  = {"2011": {"NonRes":4.3930e+00,  "PhiPi":8.7215e+00,  "KstK":7.8768e+00,  "KPiPi":6.7734e+00,  "PiPiPi":8.4187e+00}, "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"2011": {"NonRes":7.1493e+00,  "PhiPi":4.6238e+00,  "KstK":4.5946e+00,  "KPiPi":6.4937e+00,  "PiPiPi":7.2604e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"2011": {"NonRes":2.1989e+00,  "PhiPi":1.7979e+00,  "KstK":1.9708e+00,  "KPiPi":9.1754e-01,  "PiPiPi":9.4869e-01}, "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"2011": {"NonRes":-2.0186e+00, "PhiPi":-3.2123e+00, "KstK":-2.7746e+00, "KPiPi":-1.2753e+00, "PiPiPi":-1.0429e+00},"Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"2011": {"NonRes":7.9389e-01,  "PhiPi":2.6693e+00,  "KstK":2.0849e+00,  "KPiPi":9.2763e+00,  "PiPiPi":1.2886e+01}, "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"2011": {"NonRes":5.5608e+00,  "PhiPi":4.4751e-01,  "KstK":1.0774e+00,  "KPiPi":4.6466e+01,  "PiPiPi":6.9998e+01}, "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"2011": {"NonRes":0.25406,     "PhiPi":3.5389e-01,  "KstK":4.5702e-01,  "KPiPi":3.5803e-01,  "PiPiPi":4.9901e-01}, "Fixed":True}
    configdict["DsSignalShape"]["scaleSigma"] = { "2011": {"frac1": 1.16, "frac2":1.19}}

    # combinatorial background                                                                                                                              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"] = "DoubleExponential"
    configdict["BsCombinatorialShape"]["cB2"]        = {"2011": {"KKPi":0.0},  "Fixed":True }
    configdict["BsCombinatorialShape"]["cB1"]        = {"2011": {"KKPi":-6.4826e-03}, "Fixed": False}
    configdict["BsCombinatorialShape"]["frac"]  = {"2011": {"KKPi":2.7086e-01}, "Fixed":False}
#    configdict["BsCombinatorialShape"]["cB1"]        = {"2011": {"KKPi":-6.2744e-03}, "Fixed":True}
#    configdict["BsCombinatorialShape"]["frac"]  = {"2011": {"KKPi":2.7216e-01}, "Fixed":True}

    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusSignal" 
    configdict["DsCombinatorialShape"]["cD"]         = {"2011": {"NonRes":-2.7520e-03,  "PhiPi":-2.7273e-03,  "KstK":-8.3967e-03, "KPiPi":-1.9193e-03, "PiPiPi":-4.5455e-03}, 
                                                        "Fixed":False}
    configdict["DsCombinatorialShape"]["fracD"]   = {"2011": {"NonRes":0.88620,      "PhiPi":0.37379,      "KstK":0.59093,     "KPiPi":1.0,         "PiPiPi":1.0}, 
                                                         "Fixed":{"KPiPi":True,"PiPiPi":True}}


    #expected yields                                                                                                                                                       
    configdict["Yields"] = {}
    configdict["Yields"]["CombBkg"]         = {"2011": { "KKPi":1000000.0},  "Fixed":False}
    configdict["Yields"]["Signal"]          = {"2011": { "KKPi":1000000.0} , "Fixed":False}


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#    
    ###                                                               MDfit plotting settings                                                             
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#               
    from ROOT import *
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = ["Sig", "CombBkg"] #, "Bd2DPi", "Lb2LcPi", "Bs2DsDsstPiRho", "Bs2DsK"] 
    configdict["PlotSettings"]["colors"] = [kRed-7, kBlue-6] #, kOrange, kRed, kBlue-10, kGreen+3]

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9], "ScaleYSize":2.5}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.7, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    configdict["LegendSettings"]["BacPIDK"]    = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9], "ScaleYSize":1.2}

    return configdict
