def getconfig() :

    from Bs2DsKConfigForNominalGammaFit import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["resolutionScaleFactor"] *= 0.8 

    return baselineconfig
