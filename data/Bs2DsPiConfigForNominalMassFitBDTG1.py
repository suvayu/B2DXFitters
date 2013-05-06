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
    configdict["BDTGUp"]     = 0.7
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
    configdict["sigma1"]  = [ 12.124,   17.383,    10.750,    12.011,    12.504 ] #*0.742
    configdict["sigma2"]  = [ 20.000,   10.0825,   18.253,    18.517,    20.000 ] #*1.691
    configdict["alpha1"]  = [ 1.6435,   1.6836,    1.5663,    1.9311,    1.8922 ] #*1.195
    configdict["alpha2"]  = [ -1.9603,  -1.5613,   -2.3732,   -2.1825,   -2.1200] #*2.745
    configdict["n1"]      = [ 0.96277,  1.3648,    1.4180,    0.92630,   1.2074 ]
    configdict["n2"]      = [ 0.72325,  2.8707,    1.4754,    1.3457,    2.6656 ]
    configdict["frac"]    = [ 0.73958,  0.64515,   0.49407,   0.65197,   0.68870]

    configdict["sigma1Bsfrac"] = 1.123
    configdict["sigma2Bsfrac"] = 1.255
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0
        
    
    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49,  1968.49,  1968.49,  1968.49, 1968.49]
    configdict["sigma1Ds"]  = [8.7230,   5.4681,   6.0124,   6.5995,  6.1354 ] #*1.162
    configdict["sigma2Ds"]  = [4.0293,   15.432,   16.595,   17.449,  11.015 ] #*0.915
    configdict["alpha1Ds"]  = [2.2674,   5.2509,   4.0954,   3.6512,  2.2955 ] #*1.606
    configdict["alpha2Ds"]  = [-2.7370,  -2.2031,  -1.6372,  -1.8242, -2.0319] #*1.285
    configdict["n1Ds"]      = [0.00001,  49.999,   50.000,   50.000,  0.00001 ]
    configdict["n2Ds"]      = [0.00002,  50.000,   50.000,   50.000,  1.0097 ]
    configdict["fracDs"]    = [0.57153,  0.8256,   0.86570,  0.77958, 0.32642 ]

    configdict["sigma1Dsfrac"] = 1.069
    configdict["sigma2Dsfrac"] = 1.214
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0

    configdict["cB"]        = [-1.2667e-03,  -6.5033e-04,  -1.3762e-03, -1.1236e-03, -1.0994e-03]
    configdict["cD"]        = [-3.8043e-09,  -3.2070e-03,  -8.1789e-03, -2.0103e-03, -4.7851e-03]
    configdict["fracComb"]  = [0.86974,      0.35402,      0.62313,      1.0,         1.0]
            
    

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
