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
    configdict["BDTGDown"]   = 0.9
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
    configdict["sigma1"]  = [17.491,    16.798,    20.000,    11.966,    12.200 ]
    configdict["sigma2"]  = [11.648,    10.502,    11.878,    17.411,    20.000 ]
    configdict["alpha1"]  = [1.7512,    1.8830,    1.6866,    1.8663,    1.7859 ] 
    configdict["alpha2"]  = [-2.9887,   -2.6157,   -4.5799,   -1.9002,   -2.3452]
    configdict["n1"]      = [1.3977,    1.4532,    1.3475,    1.3388,    1.5131 ]
    configdict["n2"]      = [0.73008,   1.0357,    23.223,    5.7037,    2.2048 ]
    configdict["frac"]    = [0.43226,   0.64707,   0.35637,   0.63849,   0.6922 ]

    configdict["sigma1Bsfrac"] = 1.231
    configdict["sigma2Bsfrac"] = 1.265
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
    
    configdict["sigma1Dsfrac"] = 1.115
    configdict["sigma2Dsfrac"] = 1.181
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
