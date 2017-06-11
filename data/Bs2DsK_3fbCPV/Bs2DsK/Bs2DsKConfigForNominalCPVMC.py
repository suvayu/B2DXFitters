def getconfig() :

    from Bs2DsKConfigForNominalMassFit import getconfig as getconfig_nominal
    configdict = getconfig_nominal()
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661376   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.08068783069
    configdict["DeltaMs"]       = 17.757   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.391
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 70./180.*pi
    configdict["ModLf"]         = 0.372
    configdict["CPlimit"]       = {"upper":4.0, "lower":-4.0} 

    configdict["TaggingCalibration"] = {}

    configdict["ConstrainsForTaggingCalib"] = False
    configdict["FixAcceptance"] = True

    # Nominal MC Resolution and corresponding tagging parameters (DsK)
    configdict["Resolution"] = { "scaleFactor":{"p0":0.0, "p1":1.201, "p2":0.0},
                                 "meanBias":0.0,
                                 "shape": { "sigma1":2.14946e-02, "sigma2":3.67643e-02, "sigma3":6.32869e-02,
                                            "frac1":3.72147e-01, "frac2":5.65150e-01},
                                 "templates": { "fileName":"../data/workspace/MDFitter/template_Data_Terr_Bs2DsPi_BDTGA.root",
                                                "workName":"workspace",
                                                "templateName":"TimeErrorPdf_Bs2DsK"} }
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4276, "dp0": 0.0, "p1": 1.184, "dp1": 0.0,
                                              "cov": [ [1.0, 0.0, 0.0, 0.0],
                                                       [0.0, 1.0, 0.0, 0.0],
                                                       [0.0, 0.0, 1.0, 0.0],
                                                       [0.0, 0.0, 0.0, 1.0]],
#                                              "average": 0.4311, "tagEff": 0.6801705055, "aTagEff":0.0, "use":True}
                                              "average": 0.4311, "tagEff":0.63926, "aTagEff":0.0, "use":True}
#                                              "average": 0.4311, "tagEff":0.70123, "aTagEff":0.0, "use":True}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.3604, "dp0": 0.0, "p1": 0.914, "dp1": 0.0,
                                              "cov": [ [1.0, 0.0, 0.0, 0.0],
                                                       [0.0, 1.0, 0.0, 0.0],
                                                       [0.0, 0.0, 1.0, 0.0],
                                                       [0.0, 0.0, 0.0, 1.0]],
#                                              "average": 0.3597, "tagEff":0.3766009593, "aTagEff":0.0, "use":True}
                                              "average": 0.3597, "tagEff":0.37151, "aTagEff":0.0, "use":True}
#                                              "average": 0.3597, "tagEff":0.39425, "aTagEff":0.0, "use":True}


#    configdict["Acceptance"] = { "knots": [0.50, 0.75, 1.0, 1.5, 2.0, 3.0, 12.0],
#                                 "values": [5.3341e-01,6.0771e-01,8.0080e-01,9.9213e-01,1.1265e+00,1.2121e+00,1.2823e+00] }
    configdict["Acceptance"] = { "knots": [0.50, 1.0, 1.5, 2.0, 3.0, 12.0],
                                 "values": [4.7115e-01,6.6919e-01,9.3061e-01,1.0547e+00,1.1660e+00,1.2518e+00] }


    configdict["constParams"] = []
    configdict["constParams"].append('Gammas_Bs2DsK')
    configdict["constParams"].append('deltaGammas_Bs2DsK')
    configdict["constParams"].append('DeltaMs_Bs2DsK')
#    configdict["constParams"].append('C_Bs2DsK')
#    configdict["constParams"].append('Cbar_Bs2DsK')
#    configdict["constParams"].append('S_Bs2DsK')
#    configdict["constParams"].append('Sbar_Bs2DsK')
#    configdict["constParams"].append('D_Bs2DsK')
#    configdict["constParams"].append('Dbar_Bs2DsK')
    configdict["constParams"].append('tagEff_OS')
    configdict["constParams"].append('tagEff_SS')
    configdict["constParams"].append('aTagEff_OS')
    configdict["constParams"].append('aTagEff_SS')
    if configdict["FixAcceptance"] == True:
        configdict["constParams"].append('var1')
        configdict["constParams"].append('var2')
        configdict["constParams"].append('var3')
        configdict["constParams"].append('var4')
        configdict["constParams"].append('var5')
        configdict["constParams"].append('var6')
        configdict["constParams"].append('var7')
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
