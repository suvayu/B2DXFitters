def getconfig() :

    from Bs2DsKConfigForNominalMassFitToys5M import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["nLbLcKEvts"]           = [30.0/2.0, 30.0/2.0,
                                          4.0/2.0,  4.0/2.0,
                                          8.0/2.0,  8.0/2.0,
                                          0, 0,
                                          0, 0]
    
    baselineconfig["nLbLcPiEvts"]           = [22.0/2.0, 22.0/2.0,
                                           2.0/2.0,  2.0/2.0,
                                           6.0/2.0,  6.0/2.0,
                                           0, 0,
                                           0, 0]

    baselineconfig["nBdDKEvts"]            = [30.0/2.0, 30.0/2.0,
                                          0.0,  0.0,
                                          8.0/2.0,  8.0/2.0,
                                          0.0, 0.0,
                                          0.0, 0.0]

    baselineconfig["nBdDPiEvts"]            = [28.0/2.0, 28.0/2.0,
                                           0.0/2.0,  0.0/2.0,
                                           6.0/2.0,  6.0/2.0,
                                           6.0/2.0,  6.0/2.0,
                                           0, 0]                
    
    return baselineconfig
