def getconfig() :

    from Bs2DsKConfigForNominalGammaFitToys5M import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["DeltaMs"] += 0.024

    return baselineconfig
