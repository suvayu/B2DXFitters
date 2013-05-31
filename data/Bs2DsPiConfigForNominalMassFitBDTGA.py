def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # PHYSICAL PARAMETERS
    configdict["BMassDown"]  = 5300
    configdict["BMassUp"]    = 5800
    configdict["BMassDownData"]  = 5300
    configdict["BMassUpData"]    = 5800
    configdict["BMassDownComb"]  = 5600
    configdict["BMassUpComb"]    = 7000
        
    configdict["DMassDown"]  = 1930
    configdict["DMassUp"]    = 2015
    configdict["TimeDown"]   = 0.0
    configdict["TimeUp"]     = 15.0
    configdict["PDown"]      = 3000.0
    configdict["PUp"]        = 650000.0
    configdict["PTDown"]      = 400.0
    configdict["PTUp"]        = 45000.0
    configdict["PIDDown"]      = -150.0
    configdict["PIDUp"]        = 0.0
    configdict["nTracksDown"]      = 15
    configdict["nTracksUp"]        = 1000.0
    configdict["Bin1"]      = 20
    configdict["Bin2"]      = 20
    configdict["Bin3"]      = 10
    configdict["Var1"]      = "lab1_PT"
    configdict["Var2"]      = "nTracks"
    configdict["Var3"]      = "lab1_P"
    configdict["BDTGDown"]   = 0.3
    configdict["BDTGUp"]     = 1.0
    configdict["PIDBach"]    = 0
    configdict["PIDBach2"]   = 0
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsPi.txt"
    
    configdict["fileCalib"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpPi_0.root"
    configdict["fileCalibDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownPi_0.root"
    configdict["fileCalibKaonUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpK_0.root"
    configdict["fileCalibKaonDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownK_0.root"
    configdict["workCalib"]  = "RSDStCalib"

    configdict["lumRatio"] =  0.44/(0.59+0.44)

    # 1: NonRes, 2: PhiPi, 3: KstK, 4: KPiPi, 5: PiPiPi 
    configdict["mean"]    = [5367.51, 5367.51, 5367.51, 5367.51, 5367.51]

    # Bs signal shale without BKGCAT
    configdict["sigma1"]  = [14.240,  18.107,  12.092,  11.88,   12.504 ] #*1.252
    configdict["sigma2"]  = [9.0773,  11.925,  16.078,  18.539,  20.000 ] #*1.777
    configdict["alpha1"]  = [1.8539,  1.6328,  1.7344,  1.9468,  1.8922 ] #*1.004 
    configdict["alpha2"]  = [-1.3223, -2.3348, -1.9130, -2.1141, -2.1200] #*0.832
    configdict["n1"]      = [1.2508,  1.4973,  1.2819,  1.0945,  1.2074 ] 
    configdict["n2"]      = [1.7330,  1.8582,  4.0326,  2.8556,  2.6656 ]
    configdict["frac"]    = [0.85102, 0.46495, 0.51567, 0.65731, 0.68870]

    #Bs signal shape with BKGCAT
    configdict["sigma1_bc"]  = [27.529,  17.396,  11.817,  11.400,  12.122 ] 
    configdict["sigma2_bc"]  = [12.787,  11.028,  15.076,  16.920,  17.871 ] 
    configdict["alpha1_bc"]  = [0.96505, 1.8615,  1.6457,  1.8601,  1.7911 ] 
    configdict["alpha2_bc"]  = [-5.0109, -2.6267, -1.8830, -2.1714, -1.9906] 
    configdict["n1_bc"]      = [1.7482,  1.3245,  1.3573,  1.1789,  1.3272 ]
    configdict["n2_bc"]      = [13.656,  2.1862,  6.4408,  4.6903,  7.4409 ]
    configdict["frac_bc"]    = [0.15836, 0.55406, 0.43593, 0.56224, 0.60804]

    # ratio data/MC
    configdict["sigma1Bsfrac"] = 1.145 
    configdict["sigma2Bsfrac"] = 1.255
    configdict["alpha1Bsfrac"] = 1.0 
    configdict["alpha2Bsfrac"] = 1.0 

    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49 ]

    #Ds signal shapes without BKGCAT
    configdict["sigma1Ds"]  = [4.8865,   5.0649,  5.4377,  5.8510,  5.5906 ] #*1.167
    configdict["sigma2Ds"]  = [5.0645,   5.5344,  5.3877,  10.180,  10.073 ] #*1.096 
    configdict["alpha1Ds"]  = [0.51973,  1.1934,  0.7734,  2.8195,  1.9343 ] #*1.140
    configdict["alpha2Ds"]  = [-0.9908,  -1.1806, -1.1424, -2.2422,  -1.7027] #*1.022
    configdict["n1Ds"]      = [50.000,   4.0702,  49.999,  0.0262,  0.2633 ]
    configdict["n2Ds"]      = [50.000,   10.643,  50.000,  1.9293,  8.6233 ]
    configdict["fracDs"]    = [0.25406,  0.48465, 0.32864, 0.59958, 0.27873]

    #Ds signal shapes with BKGCAT
    configdict["sigma1Ds_bc"]  = [10.905,  7.6215,  11.224,  12.219,  8.3495 ]
    configdict["sigma2Ds_bc"]  = [5.1502,  4.4422,  5.3696,  6.2851,  7.5637 ] 
    configdict["alpha1Ds_bc"]  = [1.3862,  1.8802,  1.8513,  1.1467,  0.86168] 
    configdict["alpha2Ds_bc"]  = [-5.7329, -2.2066, -5.7517, -4.5438, -1.0479]
    configdict["n1Ds_bc"]      = [2.6391,  2.5713,  1.6705,  50.000,  49.990 ]
    configdict["n2Ds_bc"]      = [34.978,  1.8122,  34.310,  32.650,  69.998 ]
    configdict["fracDs_bc"]    = [0.19791, 0.44075, 0.17541, 0.21645, 0.49615]
    
    # ratio data/MC
    configdict["sigma1Dsfrac"] = 1.074
    configdict["sigma2Dsfrac"] = 1.185 
    configdict["alpha1Dsfrac"] = 1.0 
    configdict["alpha2Dsfrac"] = 1.0 
        

    # combinatorial background
    configdict["cB1"]                = [-3.5211e-03,  -3.0873e-03,  -2.3392e-03, -1.0361e-03, -1.5277e-03]
    configdict["cB2"]                = [0.0,          0.0,          0.0,         0.0,          0.0       ]
    configdict["fracBsComb"]         = [4.3067e-01,   6.5400e-01,   3.7409e-01,  1.7420e-01,  2.2100e-01]
    
    configdict["cD"]        = [-2.7520e-03,  -2.7273e-03,  -8.3967e-03, -1.9193e-03, -4.5455e-03] 
    configdict["fracComb"]  = [0.88620,      0.37379,      0.59093,     1.0,         1.0]          

    #expected Events
    configdict["BdDPiEvents"]  = [331.0, 4.0,  81.0, 28.0, 0.0]
    configdict["LbLcPiEvents"] = [301.0, 30.0, 68.0, 0.0,  0.0] #[312.0, 38.0, 69.0, 17.0,  0.0] #[301.0, 30.0, 68.0, 0.0,  0.0]
    configdict["BsDsKEvents"]  = [42.0,  48.0, 43.0, 8.0,  22.0]
        
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
