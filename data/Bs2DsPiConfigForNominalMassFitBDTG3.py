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
    configdict["BDTG"]       = [0.9,     1.0     ]
                                                
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
    configdict["sigma1"]  = [17.491,    16.798,    20.000,    11.966,    12.200 ]
    configdict["sigma2"]  = [11.648,    10.502,    11.878,    17.411,    20.000 ]
    configdict["alpha1"]  = [1.7512,    1.8830,    1.6866,    1.8663,    1.7859 ] 
    configdict["alpha2"]  = [-2.9887,   -2.6157,   -4.5799,   -1.9002,   -2.3452]
    configdict["n1"]      = [1.3977,    1.4532,    1.3475,    1.3388,    1.5131 ]
    configdict["n2"]      = [0.73008,   1.0357,    23.223,    5.7037,    2.2048 ]
    configdict["frac"]    = [0.43226,   0.64707,   0.35637,   0.63849,   0.6922 ]

    configdict["sigma1_bc"]  = [12.859,  16.759,  14.129,  17.570,  4.9011 ]
    configdict["sigma2_bc"]  = [20.000,  10.294,  6.9741,  11.200,  14.245 ]
    configdict["alpha1_bc"]  = [2.1373,  1.9485,  2.0762,  1.8450,  0.31815]
    configdict["alpha2_bc"]  = [-1.4558, -2.6688, -5.4639, -2.5372, -1.9602]
    configdict["n1_bc"]      = [1.2070,  1.3833,  1.2985,  1.3575,  2.6909 ]
    configdict["n2_bc"]      = [13.232,  2.1504,  49.988,  2.3795,  6.6993 ]
    configdict["frac_bc"]    = [0.87569, 0.64350, 0.84580, 0.48479, 0.17652]
                            

    configdict["sigma1Bsfrac"] = 1.175
    configdict["sigma2Bsfrac"] = 1.241
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0
            
    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    
    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49 ]
    configdict["sigma1Ds"]  = [12.019,   12.262,  6.8707,  6.7809,  5.6922 ]
    configdict["sigma2Ds"]  = [5.3351,   5.1593,  4.5046,  6.4308,  9.8748 ]
    configdict["alpha1Ds"]  = [1.0735,   1.4434,  1.6112,  0.8697,  1.7332 ]
    configdict["alpha2Ds"]  = [-5.4194,  -6.9800, -1.7284, -1.2763, -1.6537]
    configdict["n1Ds"]      = [49.999,   49.931,  4.8458,  13.365,  0.6453 ]
    configdict["n2Ds"]      = [12.005,   17.454,  3.2652,  50.000,  25.000 ]
    configdict["fracDs"]    = [0.14123,  0.14596, 0.54688, 0.34600, 0.31166]

    configdict["sigma1Ds_bc"]  = [11.251,  5.6928,   10.120,  9.1789,  13.159 ] 
    configdict["sigma2Ds_bc"]  = [5.2797,  2.5560,   5.1941,  5.6191,  7.1692 ]
    configdict["alpha1Ds_bc"]  = [1.1523,  1.8830,   1.3294,  1.6651,  1.2918 ]
    configdict["alpha2Ds_bc"]  = [-4.9142, -0.42475, -6.0565, -2.9147, -5.6566]
    configdict["n1Ds_bc"]      = [45.018,  3.3797,   65.814,  3.7077,  35.522 ]
    configdict["n2Ds_bc"]      = [39.588,  70.000,   43.861,  1.0673,  70.000 ]
    configdict["fracDs_bc"]    = [0.14909, 0.78655,  0.19385, 0.45885, 0.34005]
                            
    
    configdict["sigma1Dsfrac"] = 1.109
    configdict["sigma2Dsfrac"] = 1.182
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0
    
    configdict["cB1"]           = [-5.8498e-03,  -3.5736e-03,  -2.8543e-03, -1.5801e-03, -4.8317e-03]
    configdict["cB2"]           = [0.0,          0.0,          0.0,         0.0,          0.0       ]
    configdict["fracBsComb"]    = [2.4790e-01,   6.1499e-01,   1.1314e-05,  1.9249e-07,   5.1816e-01]
        
    
    configdict["cD"]        = [-2.1050e-03,  -1.6729e-03,  -1.1154e-03, -7.9291e-04, -2.3904e-03]
    configdict["fracComb"]  = [0.91313,      0.34455,      0.30638,      1.0,         1.0]
    


    configdict["BdDPiEvents"]      = [138.0, 2.0,  34.0, 14.0, 0.0]
    configdict["BdDPiEventsErr"]   = [1.0,   1.0,  1.0,  1.0, 0.0]

    configdict["LbLcPiEvents"]     = [117.0, 13.0, 26.0, 1.0,  0.0] #[129.0, 14.0, 26.0, 7.0,  0.0] 
    configdict["LbLcPiEventsErr"]  = [3.0,   1.0,  1.0,  1.0,  0.0]
    
    configdict["BsDsKEvents"]      = [20.0,  23.0, 19.0, 4.0, 10.0]
    configdict["BsDsKEventsErr"]   = [4.0,   5.0,  4.0,  2.0, 2.0 ]
    
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
