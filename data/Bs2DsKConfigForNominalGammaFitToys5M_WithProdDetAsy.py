def getconfig() :

    from Bs2DsKConfigForNominalGammaFitToys5M import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["aprod_Signal"] = -0.0175698 #-0.014
    baselineconfig["adet_Signal"]  = 0.0100562 #0.01 

    return baselineconfig
