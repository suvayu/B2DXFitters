def getconfig() :

    from Bs2DsKConfigForNominalGammaFitToys5M_WithProdDetAsy import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["adet_Signal"] -= 0.02

    return baselineconfig
