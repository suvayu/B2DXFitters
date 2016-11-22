def getconfig() :

    from Bs2DsKConfigForNominalMassFitFiltered import getconfig as getconfig_nominal
    configdict = getconfig_nominal()

    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Tau_H"] = 1.660999991
    configdict["Tau_L"] = 1.404999988
    configdict["Gamma_H"] = 1.0/configdict["Tau_H"]
    configdict["Gamma_L"] = 1.0/configdict["Tau_L"]
    configdict["Gammas"]  = (configdict["Gamma_H"] + configdict["Gamma_L"])/2.0
    configdict["Tau"] = 1.52231245
    configdict["DeltaGammas"] =  (configdict["Gamma_H"] - configdict["Gamma_L"])

    
    configdict["DeltaMs"]       = 0.0   # in ps^{-1}
    configdict["cos"] = 0.0
    configdict["sin"] = 0.0
    configdict["sinh"] = 0.0

    configdict["Bins"] = 1000

    
#    configdict["Acceptance"] = { "knots": [0.50, 1.0,  1.5, 2.0, 3.0, 12.0],
#                                 "values": [0.41, 0.603, 0.803, 0.93, 0.98, 1.0, 1.07] }
#    configdict["Acceptance"] = { "knots": [0.50, 0.75, 1.0,  1.5, 2.0, 3.0, 12.0],
#                                 "values": [0.41, 0.5, 0.603, 0.803, 0.93, 0.98, 1.0, 1.07] }
#    configdict["Acceptance"] = { "knots": [0.50, 1.0,  1.5, 2.0, 3.0, 6.0, 12.0],
#                                 "values": [0.41, 0.603, 0.803, 0.93, 0.98, 0.99, 1.0, 1.07] }
    configdict["Acceptance"] = { "knots": [0.50, 0.75, 1.0,  1.5, 2.0, 3.0, 6.0, 12.0],
                                 "values": [0.41, 0.5, 0.603, 0.803, 0.93, 0.98, 0.99, 1.0, 1.07] }

    configdict["Resolution"] = {"scaleFactor":1.201}

    configdict["constParams"] = []

    return configdict
