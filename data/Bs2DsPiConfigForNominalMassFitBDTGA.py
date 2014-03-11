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
    configdict["PIDK"]       = [0.0,     150.0   ]
    configdict["nTracks"]    = [15.0,    1000.0  ]

    configdict["TagDec"]     = ["lab0_TAGDECISION_OS","lab0_SS_nnetKaon_DEC"]
    configdict["lab0_TAGDECISION_OS"]  = [-1.0, 1.0]
    configdict["lab0_SS_nnetKaon_DEC"] = [-1.0, 1.0]

    configdict["TagOmega"]   = ["lab0_TAGOMEGA_OS","lab0_SS_nnetKaon_PROB"]
    configdict["lab0_TAGOMEGA_OS"]  = [0.0, 0.5]
    configdict["lab0_SS_nnetKaon_PROB"] = [0.0, 0.5]

    configdict["calibration_p0"]  = [0.3834, 0.4244]
    configdict["calibration_p1"]  = [0.9720, 1.2180]
    configdict["calibration_av"]  = [0.3813, 0.4097]
                                               
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
        
    configdict["Bin1"]       = 20
    configdict["Bin2"]       = 20
    configdict["Bin3"]       = 10
    configdict["Var1"]       = "lab1_PT"
    configdict["Var2"]       = "nTracks"
    configdict["Var3"]       = "lab1_P"
    configdict["WeightingDimensions"] = 2
    
    configdict["PIDBach"]    = 0
    configdict["PIDBach2"]   = 0
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsPi.txt"
    
    configdict["fileCalibPionUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpPi_0.root"
    configdict["fileCalibPionDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownPi_0.root"
    configdict["fileCalibKaonUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpK_0.root"
    configdict["fileCalibKaonDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownK_0.root"
    configdict["workCalibPion"]  = "RSDStCalib"
    configdict["workCalibKaon"]  = "RSDStCalib"

    configdict["lumRatioDown"] =  0.59
    configdict["lumRatioUp"] =  0.44
    configdict["lumRatio"] =  configdict["lumRatioUp"]/(configdict["lumRatioDown"]+configdict["lumRatioUp"])
    
    # 1: NonRes, 2: PhiPi, 3: KstK, 4: KPiPi, 5: PiPiPi 
    configdict["mean"]    = [5367.51, 5367.51, 5367.51, 5367.51, 5367.51]

    # Bs signal shale without BKGCAT
    configdict["sigma1_bc"]  = [1.1538e+01,  1.6598e+01,  1.1646e+01,  1.1428e+01,  1.1989e+01 ] #*1.252
    configdict["sigma2_bc"]  = [1.6181e+01,  1.1488e+01,  1.4992e+01,  1.6866e+01,  1.7588e+01] #*1.777
    configdict["alpha1_bc"]  = [1.9050e+00,  -2.0856e+00, 1.7019e+00,  1.9066e+00,  1.8497e+00 ] #*1.004 
    configdict["alpha2_bc"]  = [-2.0423e+00, 1.8947e+00,  -1.8418e+00, -2.2615e+00, -2.0560e+00] #*0.832
    configdict["n1_bc"]      = [1.1327e+00,  5.2735e+00,  1.2686e+00,  1.1585e+00,  1.2326e+00] 
    configdict["n2_bc"]      = [6.1273e+00,  1.1497e+00,  9.6571e+00,  4.1167e+00,  7.8246e+00]
    configdict["frac_bc"]    = [5.5417e-01,  4.4171e-01,  4.6731e-01,  5.9179e-01,  6.2376e-01]

    #Bs signal shape with BKGCAT
    configdict["sigma1_old"]  = [27.529,  17.396,  11.817,  11.400,  12.122 ] 
    configdict["sigma2_old"]  = [12.787,  11.028,  15.076,  16.920,  17.871 ] 
    configdict["alpha1_old"]  = [0.96505, 1.8615,  1.6457,  1.8601,  1.7911 ] 
    configdict["alpha2_old"]  = [-5.0109, -2.6267, -1.8830, -2.1714, -1.9906] 
    configdict["n1_old"]      = [1.7482,  1.3245,  1.3573,  1.1789,  1.3272 ]
    configdict["n2_old"]      = [13.656,  2.1862,  6.4408,  4.6903,  7.4409 ]
    configdict["frac_old"]    = [0.15836, 0.55406, 0.43593, 0.56224, 0.60804]

    # ratio data/MC
    configdict["sigma1Bsfrac"] = 1.22 
    configdict["sigma2Bsfrac"] = 1.28
    configdict["alpha1Bsfrac"] = 1.0 
    configdict["alpha2Bsfrac"] = 1.0 

    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49 ]

    #Ds signal shapes without BKGCAT
    configdict["sigma1Ds_bc"]  = [4.3930e+00,  8.7215e+00,  7.8768e+00,  6.7734e+00,  8.4187e+00 ] #*1.167
    configdict["sigma2Ds_bc"]  = [7.1493e+00,  4.6238e+00,  4.5946e+00,  6.4937e+00,  7.2604e+00 ] #*1.096 
    configdict["alpha1Ds_bc"]  = [2.1989e+00,  1.7979e+00,  1.9708e+00,  9.1754e-01,  9.4869e-01 ] #*1.140
    configdict["alpha2Ds_bc"]  = [-2.0186e+00, -3.2123e+00, -2.7746e+00, -1.2753e+00, -1.0429e+00] #*1.022
    configdict["n1Ds_bc"]      = [7.9389e-01,  2.6693e+00,  2.0849e+00,  9.2763e+00,  1.2886e+01 ]
    configdict["n2Ds_bc"]      = [5.5608e+00,  4.4751e-01,  1.0774e+00,  4.6466e+01,  6.9998e+01 ]
    configdict["fracDs_bc"]    = [0.25406,     3.5389e-01,  4.5702e-01,  3.5803e-01,  4.9901e-01 ]

    #Ds signal shapes with BKGCAT
    configdict["sigma1Ds_old"]  = [10.905,  7.6215,  11.224,  12.219,  8.3495 ]
    configdict["sigma2Ds_old"]  = [5.1502,  4.4422,  5.3696,  6.2851,  7.5637 ] 
    configdict["alpha1Ds_old"]  = [1.3862,  1.8802,  1.8513,  1.1467,  0.86168] 
    configdict["alpha2Ds_old"]  = [-5.7329, -2.2066, -5.7517, -4.5438, -1.0479]
    configdict["n1Ds_old"]      = [2.6391,  2.5713,  1.6705,  50.000,  49.990 ]
    configdict["n2Ds_old"]      = [34.978,  1.8122,  34.310,  32.650,  69.998 ]
    configdict["fracDs_old"]    = [0.19791, 0.44075, 0.17541, 0.21645, 0.49615]
    
    # ratio data/MC
    configdict["sigma1Dsfrac"] = 1.16
    configdict["sigma2Dsfrac"] = 1.19 
    configdict["alpha1Dsfrac"] = 1.0 
    configdict["alpha2Dsfrac"] = 1.0 
        

    # combinatorial background
    configdict["cB1"]                = [-3.5211e-03,  -3.0873e-03,  -2.3392e-03, -1.0361e-03, -1.5277e-03]
    configdict["cB2"]                = [0.0,          0.0,          0.0,         0.0,          0.0       ]
    configdict["fracBsComb"]         = [4.3067e-01,   6.5400e-01,   3.7409e-01,  1.7420e-01,  2.2100e-01]
    
    configdict["cD"]        = [-2.7520e-03,  -2.7273e-03,  -8.3967e-03, -1.9193e-03, -4.5455e-03] 
    configdict["fracComb"]  = [0.88620,      0.37379,      0.59093,     1.0,         1.0]          

    #expected Events
    configdict["BdDPiEvents"]  = [374.0, 6.0,  93.0, 30.0, 0.0]
    configdict["LbLcPiEvents"] = [290.0, 36.0, 69.0, 1.0,  0.0] #[312.0, 38.0, 69.0, 17.0,  0.0] #[301.0, 30.0, 68.0, 0.0,  0.0]
    configdict["BsDsKEvents"]  = [40.0,  47.0, 40.0, 8.0,  21.0]
        
    configdict["assumedSig"]   = [10146.7, 13952.8,
                                  10146.7, 13952.8,
                                  10146.7, 13952.8,
                                  752., 1195.,
                                  1730., 2384.] #[9180.,13005.,730.,1160.,1680.,2315.]
    configdict["nBd2DsPi"]     = 1./25. #1./30.
    configdict["nBd2DsstPi"]   = 1./25. #1./30.
    configdict["nBd2DstPi"]    = 1./4.
    configdict["nBd2DRho"]     = 1./3.5
    
    return configdict
