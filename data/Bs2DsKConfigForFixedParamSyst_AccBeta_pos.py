def getconfig() :

    from Bs2DsKConfigForNominalGammaFit import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["tacc_beta"] += 0.0070

    return baselineconfig
