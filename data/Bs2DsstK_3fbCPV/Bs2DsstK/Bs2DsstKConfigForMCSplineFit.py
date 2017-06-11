def getconfig() :

    from Bs2DsstKConfigForNominalMassFit import getconfig as getconfig_nominal
    configdict = getconfig_nominal()

    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.105
    configdict["DeltaMs"]       = 17.768   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.391
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 70./180.*pi
    configdict["ModLf"]         = 0.372
    configdict["CPlimit"]       = {"upper":4.0, "lower":-4.0} 

    configdict["Acceptance"] = { "knots":  [0.50,       1.0,        1.5,        2.0,        3.0,        10.0],
                                 "values": [4.5579e-01, 7.0310e-01, 8.7709e-01, 1.1351e+00, 1.0e+00, 1.0e+00] }


    configdict["constParams"] = []

    return configdict
