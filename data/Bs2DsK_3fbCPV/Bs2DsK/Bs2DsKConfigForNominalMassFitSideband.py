def getconfig() :

    from Bs2DsKConfigForNominalMassFit import getconfig as getconfig_nominal
    configdict = getconfig_nominal()

    configdict["BasicVariables"]["BeautyMass"]    = { "Range" : [6000,    7000    ], "InputName" : "lab0_MassFitConsD_M"}
