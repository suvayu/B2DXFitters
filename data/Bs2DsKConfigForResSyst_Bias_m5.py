def getconfig() :

    from Bs2DsKConfigForNominalGammaFit import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["resolutionMeanBias"]    += -0.005   

    return baselineconfig
