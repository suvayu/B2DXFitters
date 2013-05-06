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
    configdict["BDTGDown"]   = 0.5
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
    configdict["mean"]    = [5367.51,   5367.51,   5367.51,   5367.51,   5367.51]
    configdict["sigma1"]  = [12.222,    11.207,    14.701,    11.790,    15.168 ]
    configdict["sigma2"]  = [20.000,    16.334,    7.1295,    18.342,    7.2035 ]
    configdict["alpha1"]  = [2.0003,    1.5395,    2.0444,    1.9334,    1.8652 ]
    configdict["alpha2"]  = [-2.5949,   -2.0455,   -6.3443,   -2.1015,   -6.5390]
    configdict["n1"]      = [1.0451,    1.4229,    1.2443,    1.1107,    1.4454 ]
    configdict["n2"]      = [0.38244,   3.4832,    5.7654,    3.0889,    5.8213 ]
    configdict["frac"]    = [0.77054,   0.45624,   0.86523,   0.64398,   0.8454 ]

    configdict["sigma1Bsfrac"] = 1.246
    configdict["sigma2Bsfrac"] = 1.192
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0

    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49 ]
    configdict["sigma1Ds"]  = [4.9030,   4.9945,  6.8707,  9.3307,  14.424 ]
    configdict["sigma2Ds"]  = [5.1357,   5.0709,  4.5046,  5.4919,  7.3471 ] 
    configdict["alpha1Ds"]  = [0.49086,  0.7512,  1.6112,  1.7168,  1.2159 ]
    configdict["alpha2Ds"]  = [-1.0601,  -1.0394, -1.7284, -2.9551, -4.7400]
    configdict["n1Ds"]      = [50.000,   49.999,  4.8458,  2.1616,  24.986 ]
    configdict["n2Ds"]      = [50.000,   50.000,  3.2652,  0.2775,  24.669 ]
    configdict["fracDs"]    = [0.21960,  0.36831, 0.54688, 0.52642, 0.34507]
    
    configdict["sigma1Dsfrac"] = 1.060
    configdict["sigma2Dsfrac"] = 1.179
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0
    
    configdict["cB"]        = [-1.4273e-03,  -7.6227e-04,  -1.3216e-03, -1.3199e-03, -1.0290e-03]
    configdict["cD"]        = [-2.6921e-03,  -2.2982e-03,  -1.0255e-03, -1.7924e-03, -4.7307e-03]
    configdict["fracComb"]  = [0.88988,      0.33347,      0.51897,      1.0,         1.0]
                                        

    configdict["BdDPiEvents"]  = [260, 363,
                                  260, 363,
                                  260, 363,
                                  27*10, 38*10,
                                  0, 0]
    
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
