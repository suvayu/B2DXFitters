def getconfig() :

    from Bs2DsPiConfigForNominalMassFit import getconfig as getconfig_nominal
    configdict = getconfig_nominal()

    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.6568953699   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.1096968152
    configdict["DeltaMs"]       = 17.799999999   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.391
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 70./180.*pi
    configdict["ModLf"]         = 0.372
    configdict["CPlimit"]       = {"upper":4.0, "lower":-4.0} 

    configdict["TaggingCalibration"] = {}

    configdict["ConstrainsForTaggingCalib"] = False
    configdict["FixAcceptance"] = False

    # Nominal MC Resolution and corresponding tagging parameters (Dspi)
    configdict["Resolution"] = { "scaleFactor":{"p0":0.0, "p1":1.201, "p2":0.0},
                                 "meanBias":0.0,
                                 "shape": { "sigma1":2.14946e-02, "sigma2":3.67643e-02, "sigma3":6.32869e-02,
                                            "frac1":3.72147e-01, "frac2":5.65150e-01},
                                 "templates": { "fileName":"../data/workspace/MDFitter/template_Data_Terr_Bs2DsPi_BDTGA.root",
                                                "workName":"workspace",
                                                "templateName":"TimeErrorPdf_Bs2DsPi"} }
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4267, "dp0": 0.0, "p1": 1.186, "dp1": 0.0,
                                              "cov": [ [1.0, 0.0, 0.0, 0.0],
                                                       [0.0, 1.0, 0.0, 0.0],
                                                       [0.0, 0.0, 1.0, 0.0],
                                                       [0.0, 0.0, 0.0, 1.0]],
#                                              "average": 0.4314, "tagEff":0.63926, "aTagEff":0.0, "use":True}
                                              "average": 0.4314, "tagEff":0.70123, "aTagEff":0.0, "use":True}

    configdict["TaggingCalibration"]["OS"] = {"p0": 0.3607, "dp0": 0.0, "p1": 0.936, "dp1": 0.0,
                                              "cov": [ [1.0, 0.0, 0.0, 0.0],
                                                       [0.0, 1.0, 0.0, 0.0],
                                                       [0.0, 0.0, 1.0, 0.0],
                                                       [0.0, 0.0, 0.0, 1.0]],
#                                              "average": 0.3597, "tagEff":0.37151, "aTagEff":0.0, "use":True}
                                              "average": 0.3597, "tagEff":0.39425, "aTagEff":0.0, "use":True}


    configdict["Acceptance"] = { "knots": [0.50, 1.0,  1.5, 2.0, 3.0, 12.0],
                                 "values": [4.0349e-01, 5.8534e-01, 7.7696e-01, 9.1592e-01, 9.9973e-01, 1.0705e+00] }
#                                 "values": [5.6512e-01, 6.3939e-01, 9.9391e-01, 1.0961e+00, 1.0567e+00, 1.2991e+00] }


    configdict["constParams"] = []
    configdict["constParams"].append('Gammas_Bs2DsPi')
    configdict["constParams"].append('deltaGammas_Bs2DsPi')
#    configdict["constParams"].append('DeltaMs_Bs2DsPi')
    configdict["constParams"].append('C_Bs2DsPi')
    configdict["constParams"].append('Cbar_Bs2DsPi')
    configdict["constParams"].append('S_Bs2DsPi')
    configdict["constParams"].append('Sbar_Bs2DsPi')
    configdict["constParams"].append('D_Bs2DsPi')
    configdict["constParams"].append('Dbar_Bs2DsPi')
    configdict["constParams"].append('tagEff_OS')
    configdict["constParams"].append('tagEff_SS')
    configdict["constParams"].append('aTagEff_OS')
    configdict["constParams"].append('aTagEff_SS')
    configdict["constParams"].append('aTagEff_Both')

    if configdict["FixAcceptance"] == True:
        configdict["constParams"].append('var1')
        configdict["constParams"].append('var2')
        configdict["constParams"].append('var3')
        configdict["constParams"].append('var4')
        configdict["constParams"].append('var5')
        configdict["constParams"].append('var6')
    if configdict["ConstrainsForTaggingCalib"] == False:
        configdict["constParams"].append('p0_OS')
        configdict["constParams"].append('p0_SS')
        configdict["constParams"].append('p1_OS')
        configdict["constParams"].append('p1_SS')

    configdict["constParams"].append('dp0_OS')
    configdict["constParams"].append('dp0_SS')
    configdict["constParams"].append('dp1_OS')
    configdict["constParams"].append('dp1_SS')
    configdict["constParams"].append('p0_mean_OS')
    configdict["constParams"].append('p0_mean_SS')
    configdict["constParams"].append('p1_mean_OS')
    configdict["constParams"].append('p1_mean_SS')
    configdict["constParams"].append('dp0_mean_OS')
    configdict["constParams"].append('dp0_mean_SS')
    configdict["constParams"].append('dp1_mean_OS')
    configdict["constParams"].append('dp1_mean_SS')
    configdict["constParams"].append('average_OS')
    configdict["constParams"].append('average_SS')




    #configdict["constParams"].append('DeltaMs')

    return configdict
