def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["BMassDown"]  = 5100
    configdict["BMassUp"]    = 5800
    configdict["DMassDown"]  = 1948
    configdict["DMassUp"]    = 1990
    configdict["TimeDown"]   = 0.0
    configdict["TimeUp"]     = 15.0
    configdict["PDown"]      = 0.0
    configdict["PUp"]        = 100000000000.0
    configdict["BDTG"]       = 0.5
    configdict["PIDBach"]    = 0
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

    configdict["BdDPiEvents"]  = [260, 363, 27, 38, 0, 0]
    configdict["assumedSig"]   = [9180.,13005.,730.,1160.,1680.,2315.]
    configdict["nBd2DsPi"]     = 1./30.
    configdict["nBd2DsstPi"]   = 1./30.
    configdict["nBd2DstPi"]    = 1./4.
    configdict["nBd2DRho"]     = 1./3.5
    
    return configdict
