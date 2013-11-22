def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
        
    # PHYSICAL PARAMETERS
    configdict["BMass"]      = [5300,    5800    ]
    configdict["DMass"]      = [1930,    2015    ]
    configdict["Time"]       = [0.2,     15.0    ]
    configdict["Momentum"]   = [3000.0,  650000.0]
    configdict["TrMom"]      = [400.0,   45000.0 ]
    configdict["PIDK"]       = [1.61,    5.0     ]
    configdict["nTracks"]    = [15.0,    1000.0  ]

    configdict["TagDec"]     = ["lab0_TAGDECISION_OS","lab0_SS_nnetKaon_DEC"]
    configdict["lab0_TAGDECISION_OS"]  = [-1.0, 1.0]
    configdict["lab0_SS_nnetKaon_DEC"] = [-1.0, 1.0]
    
    configdict["TagOmega"]   = ["lab0_TAGOMEGA_OS","lab0_SS_nnetKaon_PROB"]
    configdict["lab0_TAGOMEGA_OS"]  = [0.0, 0.5]
    configdict["lab0_SS_nnetKaon_PROB"] = [0.0, 0.5]

    configdict["calibration_p0"]  = [0.3927, 0.4244]
    configdict["calibration_p1"]  = [0.9818, 1.2550]
    configdict["calibration_av"]  = [0.3919, 0.4097]
       
    configdict["Terr"]       = [0.01,    0.1     ]
    configdict["BachCharge"] = [-1000.0, 1000.0  ]
    configdict["BDTG"]       = [0.3,     1.0     ]

    configdict["AdditionalVariables"] = [ "lab0_SS_Kaon_PROB", "lab0_SS_Kaon_DEC", 
                                          "lab0_OS_Muon_PROB" , "lab0_OS_Muon_DEC",
                                          "lab0_OS_Electron_PROB", "lab0_OS_Electron_DEC",
                                          "lab0_OS_Kaon_PROB",  "lab0_OS_Kaon_DEC",
                                          "lab0_OS_nnetKaon_PROB", "lab0_OS_nnetKaon_DEC",
                                          "lab0_VtxCharge_PROB", "lab0_VtxCharge_DEC" ]

    configdict["lab0_SS_Kaon_PROB"]      = [ -3.0, 1,0 ]
    configdict["lab0_SS_Kaon_DEC"]       = [ -2.0, 2.0 ]
    configdict["lab0_OS_Muon_PROB"]      = [ -3.0, 1.0 ]
    configdict["lab0_OS_Muon_DEC"]       = [ -2.0, 2.0 ]
    configdict["lab0_OS_Electron_PROB"]  = [-3.0, 1.0 ]
    configdict["lab0_OS_Electron_DEC"]   = [ -2.0, 2.0 ]
    configdict["lab0_OS_Kaon_PROB"]      = [ -3.0, 1.0 ]
    configdict["lab0_OS_Kaon_DEC"]       = [ -2.0, 2.0 ]
    configdict["lab0_OS_nnetKaon_PROB"]  = [ -3.0, 1.0 ]
    configdict["lab0_OS_nnetKaon_DEC"]   = [ -2.0, 2.0 ]
    configdict["lab0_VtxCharge_PROB"]    = [-3.0, 1.0 ]
    configdict["lab0_VtxCharge_DEC"]     = [-2.0, 2.0 ]
    
    
    configdict["Bin1"]      = 20
    configdict["Bin2"]      = 20
    configdict["Bin3"]      = 10
    configdict["Var1"]      = "lab1_PT"
    configdict["Var2"]      = "nTracks"
    configdict["Var3"]       = "lab1_P"
    configdict["WeightingDimensions"] = 2
  
    configdict["PIDBach"]    = 5
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsK.txt"

    configdict["fileCalibPionUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpPi_DsK.root"
    configdict["fileCalibPionDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownPi_DsK.root"
    configdict["workCalibPion"]  = "RSDStCalib"
    configdict["fileCalibKaonUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpK_DsK.root"
    configdict["fileCalibKaonDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownK_DsK.root"
    configdict["workCalibKaon"]  = "RSDStCalib"
    configdict["fileCalibProtonUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/work_lblcpi_up_sw.root"
    configdict["fileCalibProtonDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/work_lblcpi_down_sw.root"
    configdict["workCalibProton"]  = "workspace"
    configdict["pathFileLcPi"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/sWeights_LbLcPi_both_PID10.root"
    configdict["treeNameLcPi"] = "merged"

    configdict["lumRatioDown"] =  0.59
    configdict["lumRatioUp"] =  0.44
    configdict["lumRatio"] =  configdict["lumRatioUp"]/(configdict["lumRatioDown"]+configdict["lumRatioUp"])
            

    # 1: NonRes, 2: PhiPi, 3: KstK, 4: KPiPi, 5: PiPiPi
    configdict["mean"]    = [5367.51, 5367.51, 5367.51, 5367.51, 5367.51]
    configdict["sigma1"]  = [10.309,  20.732,  11.483,  11.056,  12.882 ]
    configdict["sigma2"]  = [15.890,  11.728,  15.152,  17.855,  25.940 ]
    configdict["alpha1"]  = [1.8208,  1.6405,  1.7332,  2.1254,  2.3576 ]
    configdict["alpha2"]  = [-2.1403, -3.2621, -1.7466, -2.0608, -3.1939]
    configdict["n1"]      = [1.0888,  1.5767,  1.4976,  1.0916,  1.0079 ]
    configdict["n2"]      = [2.3937,  0.61741, 5.0902,  5.8375,  0.0010 ]
    configdict["frac"]    = [0.46161, 0.31817, 0.49794, 0.60582, 0.84837]

    configdict["sigma1_bc"]  = [18.082,  10.627,  11.417,  18.901,  19.658 ]
    configdict["sigma2_bc"]  = [10.727,  15.289,  16.858,  11.058,  11.512 ]
    configdict["alpha1_bc"]  = [2.0550,  1.6086,  2.0304,  2.0490,  1.8844 ]
    configdict["alpha2_bc"]  = [-2.9184, -1.9642, -1.9823, -3.3876, -3.0227]
    configdict["n1_bc"]      = [1.1123,  1.5879,  1.3059,  1.0988,  1.3397 ]
    configdict["n2_bc"]      = [1.3312,  5.1315,  4.2083,  0.96197,  1.2083 ]
    configdict["frac_bc"]    = [0.42743, 0.43480, 0.61540, 0.38142, 0.37901]
    

    configdict["sigma1Bsfrac"] = 1.145 
    configdict["sigma2Bsfrac"] = 1.255
    configdict["alpha1Bsfrac"] = 1.0 
    configdict["alpha2Bsfrac"] = 1.0 
    
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    
    configdict["sigma1Ds"]  = [7.6072,  12.365,  7.2695,  5.6933,  7.1100]  
    configdict["sigma2Ds"]  = [4.2208,  5.1626,  4.3215,  10.246,  13.122]
    configdict["alpha1Ds"]  = [1.8268,  1.6222,  1.6434,  2.8423,  2.1959]
    configdict["alpha2Ds"]  = [-2.5602, -6.2415, -2.0514, -2.6759, -2.3791]
    configdict["n1Ds"]      = [1.9454,  1.6567,  4.9069,  0.0001,  0.5686]
    configdict["n2Ds"]      = [0.4889,  46.494,  1.5736,  0.3507,  0.9733]
    configdict["fracDs"]    = [0.53155, 0.19015, 0.57295, 0.58468, 0.63449]

    configdict["sigma1Ds_bc"]  = [7.6526,  8.7205,  5.3844,  11.590,  11.217 ]
    configdict["sigma2Ds_bc"]  = [4.2202,  4.5795,  11.981,  6.0350,  6.8617 ]
    configdict["alpha1Ds_bc"]  = [1.9266,  1.9260,  4.8339,  1.5839,  1.0902 ]
    configdict["alpha2Ds_bc"]  = [-2.5456, -3.2773, -3.0116, -6.2018, -2.4987]
    configdict["n1Ds_bc"]      = [2.8434,  1.4224,  48.516,  1.8532,  69.861 ]
    configdict["n2Ds_bc"]      = [1.5942,  0.36197, 0.25888, 65.824,  1.0790 ]
    configdict["fracDs_bc"]    = [0.50702, 0.36627, 0.84549, 0.29362, 0.46289]

    configdict["sigma1Dsfrac"] = 1.074 
    configdict["sigma2Dsfrac"] = 1.185 
    configdict["alpha1Dsfrac"] = 1.0 
    configdict["alpha2Dsfrac"] = 1.0 
        
    configdict["cB"]        = [-1.1530e-03,  -9.2354e-04,  -1.3675e-03, -9.8158e-04, -1.0890e-03]
    configdict["cD"]        = [-4.4329e-03,  -8.8642e-03,  -5.2652e-03, -1.0743e-03, -1.1877e-03]
    configdict["fracComb"]  = [0.78490,      0.34206,      0.63593,     1.0,         1.0]
    
        
    configdict["nBs2DsDsstPiRhoEvts"]  = [180.0/2.0, 180.0/2.0,
                                          208.0/2.0, 208.0/2.0,
                                          191.0/2.0, 191.0/2.0,
                                          37.0/2.0,  37.0/2.0,
                                          98.0/2.0,  98.0/2.0
                                          ]

    configdict["nBs2DsPiEvts"]  = [180.0/2.0, 180.0/2.0,
                                   208.0/2.0, 208.0/2.0,
                                   191.0/2.0, 191.0/2.0,
                                   37.0/2.0,  37.0/2.0,
                                   98.0/2.0,  98.0/2.0
                                   ]
    
    configdict["nLbDspEvts"]           = [46,78,
                                          46,78,
                                          46,78,
                                          5,8,
                                          10,16]

    configdict["nLbLcKEvts"]           = [15.0/2.0, 15.0/2.0,
                                          2.0/2.0,  2.0/2.0,
                                          4.0/2.0,  4.0/2.0,
                                          0, 0,
                                          0, 0]
    
    configdict["nBdDKEvts"]            = [15.0/2.0, 15.0/2.0,
                                          0.0/2.0,  0.0/2.0,
                                          4.0/2.0,  4.0/2.0,
                                          0, 0,
                                          0, 0]
    
    configdict["NEWnBs2DsDsstPiRhoEvts"]  = [56*100./38.2651+80*100./38.2651, 5*100./38.2651+7*100./38.2651, 10*100./38.2651+14*100./38.2651]
    configdict["NEWnLbDspEvts"]           = [46+78,5+8,10+16]
    configdict["NEWnLbLcKEvts"]           = [8.3220*100/15+1.1299*1000/15, 0+0, 0+0] #[4.1088*100./15.,6.7221*100./15.,0,0,0,0]
    configdict["NEWnBdDKEvts"]            = [6.7238*100/15+1.0097*1000/15, 4.3334*10/15+4.4202*10/15, 0+0] #[14,23,2,3,0,0]
                
    
    configdict["g2_f1"] = 0.42761287
    configdict["g2_f2"] = 0.47275694
    configdict["g2_f3"] = 0.05205979

    return configdict
