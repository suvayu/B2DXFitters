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
    configdict["PIDBach"]    = 10
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsK.txt"

    configdict["mean"]    = 5367.51
    configdict["sigma1"]  = 10.0880
    configdict["sigma2"]  = 15.708
    configdict["alpha1"]  = 1.8086
    configdict["alpha2"]  = -1.8169
    configdict["n1"]      = 1.3830
    configdict["n2"]      = 8.8559
    configdict["frac"]    = 0.47348
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515
    
    configdict["nBs2DsDsstPiRhoEvts"]  = 6*[423]
    configdict["nLbDspEvts"]           = 6*[254]
    configdict["nLbLcKEvts"]           = 6*[43]
    configdict["nBdDKEvts"]            = 6*[43]
    
    configdict["g2_f1"] = 0.374
    configdict["g2_f2"] = 0.196
    configdict["g2_f3"] = 0.127

    return configdict
