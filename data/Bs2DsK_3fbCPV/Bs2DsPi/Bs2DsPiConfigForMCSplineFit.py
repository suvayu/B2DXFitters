def getconfig() :

    from Bs2DsPiConfigForNominalMassFit import getconfig as getconfig_nominal
    configdict = getconfig_nominal()

    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Tau_H"] = 1.660999991
    configdict["Tau_L"] = 1.404999988
    configdict["Gamma_H"] = 1.0/configdict["Tau_H"]
    configdict["Gamma_L"] = 1.0/configdict["Tau_L"]
    configdict["Gammas"]  = (configdict["Gamma_H"] + configdict["Gamma_L"])/2.0
    configdict["Tau"] =1.52231245
    configdict["DeltaGammas"] = configdict["Gamma_H"] -configdict["Gamma_L"]


    configdict["DeltaMs"]       = 0.0   # in ps^{-1}                                                                                                                                           
    configdict["cos"] = 0.0
    configdict["sin"] = 0.0
    configdict["sinh"] = 0.0

    configdict["Bins"] = 1000

    configdict["Acceptance"] = { "knots":  [0.50,       1.0,        1.5,        2.0,        3.0,      12.0],
                                 "values": [4.5579e-01, 7.0310e-01, 8.7709e-01, 1.1351e+00, 1.0e+00,  1.0, 1.0e+00] }
    
    configdict["Resolution"] = {"scaleFactor":1.201}

    configdict["constParams"] = []

    return configdict
