def getconfig() :

    from Bs2DsKConfigForNominalGammaFitToys5M_WithProdDetAsy import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["aprod_Signal"] -= 0.03

    return baselineconfig
