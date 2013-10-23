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
    configdict["TagDec"]     = [-1.0,    1.0     ]
    configdict["TagOmega"]   = [0.0,     0.5     ]
    configdict["Terr"]       = [0.01,    0.1     ]
    configdict["BachCharge"] = [-1000.0, 1000.0  ]
    configdict["BDTG"]       = [0.5,     1.0     ]
                                                
    
    configdict["Bin1"]      = 20
    configdict["Bin2"]      = 20
    configdict["Bin3"]      = 10
    configdict["Var1"]      = "lab1_PT"
    configdict["Var2"]      = "nTracks"
    configdict["Var3"]      = "lab1_P"
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
    configdict["mean"]    = [5367.51,   5367.51,   5367.51,   5367.51,   5367.51]

    # Bs signal shapes without BKGCAT
    configdict["sigma1"]  = [12.222,    11.207,    14.701,    11.790,    15.168 ]
    configdict["sigma2"]  = [20.000,    16.334,    7.1295,    18.342,    7.2035 ]
    configdict["alpha1"]  = [2.0003,    1.5395,    2.0444,    1.9334,    1.8652 ]
    configdict["alpha2"]  = [-2.5949,   -2.0455,   -6.3443,   -2.1015,   -6.5390]
    configdict["n1"]      = [1.0451,    1.4229,    1.2443,    1.1107,    1.4454 ]
    configdict["n2"]      = [0.38244,   3.4832,    5.7654,    3.0889,    5.8213 ]
    configdict["frac"]    = [0.77054,   0.45624,   0.86523,   0.64398,   0.8454 ]

    # Bs signal shapes with BKGCAT
    configdict["sigma1_bc"]  = [12.503,  10.834,  12.281,  11.323,  5.4885 ]
    configdict["sigma2_bc"]  = [20.000,  15.946,  14.491,  16.853,  14.577 ] 
    configdict["alpha1_bc"]  = [2.0270,  1.5861,  1.5774,  1.8554,  0.44487]
    configdict["alpha2_bc"]  = [-1.7188, -2.1322, -1.8651, -2.1591, -2.0320]
    configdict["n1_bc"]      = [1.1609,  1.3582,  1.3714,  1.1757,  2.0140 ] 
    configdict["n2_bc"]      = [8.8094,  7.4826,  6.2258,  4.8169,  6.5445 ]
    configdict["frac_bc"]    = [0.83988, 0.42086, 0.38338, 0.55337, 0.17657]
                            
    # ratio Data/MC
    configdict["sigma1Bsfrac"] = 1.115
    configdict["sigma2Bsfrac"] = 1.255
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0

    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49 ]

    # Ds signal shapes without BKGCAT
    configdict["sigma1Ds"]  = [4.9030,   4.9945,  6.8707,  9.3307,  14.424 ]
    configdict["sigma2Ds"]  = [5.1357,   5.0709,  4.5046,  5.4919,  7.3471 ] 
    configdict["alpha1Ds"]  = [0.49086,  0.7512,  1.6112,  1.7168,  1.2159 ]
    configdict["alpha2Ds"]  = [-1.0601,  -1.0394, -1.7284, -2.9551, -4.7400]
    configdict["n1Ds"]      = [50.000,   49.999,  4.8458,  2.1616,  24.986 ]
    configdict["n2Ds"]      = [50.000,   50.000,  3.2652,  0.2775,  24.669 ]
    configdict["fracDs"]    = [0.21960,  0.36831, 0.54688, 0.52642, 0.34507]

    # Ds signal shapes with BKGCAT
    configdict["sigma1Ds_bc"]  = [10.714,  7.6749,  10.771,  12.086,  8.9754  ]
    configdict["sigma2Ds_bc"]  = [5.1475,  4.4604,  5.3184,  6.3808,  3.5813  ]
    configdict["alpha1Ds_bc"]  = [1.4270,  1.8983,  2.0725,  1.1389,  1.5035  ]
    configdict["alpha2Ds_bc"]  = [-4.9110, -2.2342, -6.3898, -5.4563, -0.38239]
    configdict["n1Ds_bc"]      = [2.5618,  2.3658,  0.86114, 69.937,  4.4700  ]
    configdict["n2Ds_bc"]      = [33.689,  1.8154,  34.830,  46.754,  69.987  ]
    configdict["fracDs_bc"]    = [0.20018, 0.42567, 0.18861, 0.21735, 0.81444 ]
                            
    # ratio Data/MC
    configdict["sigma1Dsfrac"] = 1.068
    configdict["sigma2Dsfrac"] = 1.182
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0

    # combinatorial background
    configdict["cB1"]        = [-3.4971e-03,  -5.7868e-03,  -2.9761e-03, -1.1526e-03, -2.1378e-03]
    configdict["cB2"]        = [0.0,          0.0,          0.0,         0.0,          0.0       ]
    configdict["fracBsComb"] = [4.0453e-01,   7.0573e-01,   4.7434e-01,  6.5007e-06,   3.9893e-01]
        

    configdict["cD"]        = [-2.6921e-03,  -2.2982e-03,  -1.0255e-03, -1.7924e-03, -4.7307e-03]
    configdict["fracComb"]  = [0.88988,      0.33347,      0.51897,      1.0,         1.0]
                                        

    configdict["BdDPiEvents"]  = [310.0, 4.0,  76.0,  26.0, 0.0]
    configdict["LbLcPiEvents"] = [266.0, 35.0, 63.0,  0.0,  0.0] #[292.0, 35.0, 65.0,  16.0,  0.0] 
    configdict["BsDsKEvents"] =  [40.0,  46.0, 40.0,  8.0, 21.0]
        
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
