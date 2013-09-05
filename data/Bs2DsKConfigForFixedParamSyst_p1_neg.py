def getconfig() :

    from Bs2DsKConfigForNominalGammaFitToys5M import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["calibration_p1"] -= 0.024

    return baselineconfig
