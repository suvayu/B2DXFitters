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
    configdict["BDTGDown"]  = 0.7
    configdict["BDTGUp"]    = 0.9
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
    configdict["sigma1"]  = [12.160,    11.309,    18.897,    19.999,    20.00  ]
    configdict["sigma2"]  = [20.000,    15.938,    12.451,    11.537,    12.149 ]
    configdict["alpha1"]  = [1.8958,    1.4408,    1.6987,    1.6736,    1.6825 ]
    configdict["alpha2"]  = [-2.1274,   -1.9007,   -2.5680,   -3.0475,   -2.8338]
    configdict["n1"]      = [1.0199,    1.4658,    1.1823,    1.1380,    1.1893 ]
    configdict["n2"]      = [0.81799,   3.2170,    1.3729,    0.60667,   0.97876]
    configdict["frac"]    = [0.76980,   0.45614,   0.3901,    0.41735,   0.42092]

    configdict["sigma1Bsfrac"] = 1.256
    configdict["sigma2Bsfrac"] = 1.116
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0
                
        
    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331

    

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    configdict["sigma1Ds"]  = [15.703,  13.127,  5.6643,  5.7021,  14.086 ]
    configdict["sigma2Ds"]  = [5.3237,  5.3042,  7.1832,  9.7796,  7.3518 ]
    configdict["alpha1Ds"]  = [1.0636,  2.2402,  2.0148,  2.7484,  1.1540 ]
    configdict["alpha2Ds"]  = [-5.1982, -5.6413, -0.9324, -2.3461, -6.2458]
    configdict["n1Ds"]      = [13.336,  0.00001, 1.5631,  0.0009,  24.980 ]
    configdict["n2Ds"]      = [0.48506, 0.33569, 49.999,  1.2731,  16.636 ]
    configdict["fracDs"]    = [0.16490, 0.18479, 0.81112, 0.52045, 0.38730]
    
    configdict["sigma1Dsfrac"] = 1.036
    configdict["sigma2Dsfrac"] = 1.167
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0
    
    configdict["cB"]        = [-1.1297e-03,  -9.5481e-04,  -8.0575e-04, -1.4264e-03, -1.0139e-03]
    configdict["cD"]        = [-2.1050e-03,  -1.6729e-03,  -1.1154e-03, -7.9291e-04, -2.3904e-03]
    configdict["fracComb"]  = [0.91313,      0.34455,      0.30638,      1.0,         1.0]
    


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
