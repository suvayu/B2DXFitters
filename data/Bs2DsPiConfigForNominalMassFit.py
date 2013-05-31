def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["BMassDown"]  = 5100
    configdict["BMassUp"]    = 5800
    configdict["BMassDownData"]  = 5100
    configdict["BMassUpData"]    = 5800
        
    
    configdict["DMassDown"]  = 1948
    configdict["DMassUp"]    = 1990
    configdict["TimeDown"]   = 0.0
    configdict["TimeUp"]     = 15.0
    configdict["PDown"]      = 0.0
    configdict["PUp"]        = 100000000000.0
    configdict["PTDown"]      = 400.0
    configdict["PTUp"]        = 45000.0
    configdict["PIDDown"]      = -150.0
    configdict["PIDUp"]        = 0.0
    configdict["nTracksDown"]      = 15
    configdict["nTracksUp"]        = 1000.0
                        
    configdict["BDTGDown"]   = 0.5
    configdict["BDTGUp"]     = 1.0
    configdict["PIDBach"]    = 0
    configdict["PIDBach2"]   = 0
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsPi.txt"

    configdict["mean"]    = 5367.51
    configdict["sigma1"]  = 12.691
    configdict["sigma2"]  = 20.486
    configdict["alpha1"]  = 2.1260
    configdict["alpha2"]  = -2.0649
    configdict["n1"]      = 1.1019
    configdict["n2"]      = 5.8097
    configdict["frac"]    = 0.78044
    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["BdDPiEvents"]  = [310.0/2.0, 310.0/2.0,
                                  4.0/2.0,   4.0/2.0,
                                  76.0/2.0,  76.0/2.0,
                                  26.0/2.0,  26.0/2.0,
                                  0.0/2.0,   0.0/2.0]
    
    configdict["assumedSig"]   = [10146.7, 13952.8,
                                  10146.7, 13952.8,
                                  10146.7, 13952.8,
                                  752., 1195.,
                                  1730., 2384.]
    
    configdict["lumRatio"] =  0.44/(0.59+0.44)

    configdict["nBd2DsPi"]     = 1./30.
    configdict["nBd2DsstPi"]   = 1./30.
    configdict["nBd2DstPi"]    = 1./4.
    configdict["nBd2DRho"]     = 1./3.5
    
    return configdict
