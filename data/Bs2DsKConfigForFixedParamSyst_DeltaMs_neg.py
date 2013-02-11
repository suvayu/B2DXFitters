def getconfig() :

    from Bs2DsKConfigForNominalGammaFit import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["DeltaMs"] -= 0.043

    return baselineconfig
