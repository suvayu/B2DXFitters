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
    configdict["sigma1"]  = [14.240,  18.107,  12.092,  11.88,   12.504 ] #*1.252
    configdict["sigma2"]  = [9.0773,  11.925,  16.078,  18.539,  20.000 ] #*1.777
    configdict["alpha1"]  = [1.8539,  1.6328,  1.7344,  1.9468,  1.8922 ] #*1.004 
    configdict["alpha2"]  = [-1.3223, -2.3348, -1.9130, -2.1141, -2.1200] #*0.832
    configdict["n1"]      = [1.2508,  1.4973,  1.2819,  1.0945,  1.2074 ] 
    configdict["n2"]      = [1.7330,  1.8582,  4.0326,  2.8556,  2.6656 ]
    configdict["frac"]    = [0.85102, 0.46495, 0.51567, 0.65731, 0.68870]

    configdict["sigma1Bsfrac"] = 1.243 
    configdict["sigma2Bsfrac"] = 1.189
    configdict["alpha1Bsfrac"] = 1.0 
    configdict["alpha2Bsfrac"] = 1.0 
        
    

    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49 ]
    configdict["sigma1Ds"]  = [4.8865,   5.0649,  5.4377,  5.8510,  5.5906 ] #*1.167
    configdict["sigma2Ds"]  = [5.0645,   5.5344,  5.3877,  10.180,  10.073 ] #*1.096 
    configdict["alpha1Ds"]  = [0.51973,  1.1934,  0.7734,  2.8195,  1.9343 ] #*1.140
    configdict["alpha2Ds"]  = [-0.9908,  -1.1806, -1.1424, -2.2422,  -1.7027] #*1.022
    configdict["n1Ds"]      = [50.000,   4.0702,  49.999,  0.0262,  0.2633 ]
    configdict["n2Ds"]      = [50.000,   10.643,  50.000,  1.9293,  8.6233 ]
    configdict["fracDs"]    = [0.25406,  0.48465, 0.32864, 0.59958, 0.27873]

    configdict["sigma1Dsfrac"] = 1.062
    configdict["sigma2Dsfrac"] = 1.183 
    configdict["alpha1Dsfrac"] = 1.0 
    configdict["alpha2Dsfrac"] = 1.0 
        

    configdict["cB"]        = [-1.2541e-03,  -6.8338e-04,  -1.3075e-03, -1.1672e-03, -1.0871e-03]
    configdict["cD"]        = [-2.7520e-08,  -2.7273e-03,  -8.3967e-03, -1.9193e-03, -4.5455e-03] 
    configdict["fracComb"]  = [0.88620,      0.37379,      0.59093,     1.0,         1.0]          

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
