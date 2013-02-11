def getconfig() :

    from Bs2DsKConfigForNominalGammaFit import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["tacc_turnon"] += 0.064

    return baselineconfig
