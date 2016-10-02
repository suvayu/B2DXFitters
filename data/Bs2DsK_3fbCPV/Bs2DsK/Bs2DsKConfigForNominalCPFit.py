def getconfig() :

    from Bs2DsKConfigForNominalMassFit import getconfig as getconfig_nominal
    configdict = getconfig_nominal()

    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.6643   # in ps^{-1}                                                                                                                                       
    configdict["DeltaGammas"]   =  -0.083
    configdict["DeltaMs"]       = 17.757   # in ps^{-1}                                                                                                                                         
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 70./180.*pi
    configdict["ModLf"]         = 0.372
    configdict["CPlimit"]       = {"upper":4.0, "lower":-4.0}

    configdict["Resolution"] = { "scaleFactor":{"p0":0.010262, "p1":1.280, "p2":0.0},
                                 "meanBias":0.0,
                                 "shape": { "sigma1":2.14946e-02, "sigma2":3.67643e-02, "sigma3":6.32869e-02,
                                            "frac1":3.72147e-01, "frac2":5.65150e-01},
                                 "templates": { "fileName":"../data/workspace/MDFitter/template_Data_Terr_Bs2DsPi_BDTGA.root",
                                                "workName":"workspace",
                                                "templateName":"TimeErrorPdf_Bs2DsK"} }
    
    configdict["ConstrainsForTaggingCalib"] = True
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.44119, "dp0": 0.0, "p1": 1.0868, "dp1": 0.0,
                                              "cov": [ [2.903e-05, 0.0, 0.0001613, 0.0],
                                                       [0.0, 1.0, 0.0, 0.0],
                                                       [0.0001613, 0.0, 0.006101, 0.0],
                                                       [0.0, 0.0, 0.0, 1.0]],
                                              "average": 0.43744, "tagEff":0.63926, "aTagEff":0.0, "use":True}
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.37718, "dp0": 0.0, "p1": 1.1244, "dp1": 0.0,
                                              "cov": [ [5.212e-05, 0.0, 0.0002286, 0.0],
                                                       [0.0, 1.0, 0.0, 0.0],
                                                       [0.0002286, 0.0, 0.006685, 0.0],
                                                       [0.0, 0.0, 0.0, 1.0]],
                                              "average": 0.369798, "tagEff":0.37151, "aTagEff":0.0, "use":True}

    # Tagging for Single Gaussian
    #configdict["TaggingCalibration"]["SS"] = {"p0": 0.43703, "dp0": 0.0, "p1": 1.1314, "dp1": 0.0,
    #                                          "average": 0.43744, "tagEff":0.63925, "aTagEff":0.0, "use":True, }
    #configdict["TaggingCalibration"]["OS"] = {"p0": 0.36820, "dp0": 0.0, "p1": 1.1993, "dp1": 0.0,
    #                                          "average": 0.369798, "tagEff":0.37151, "aTagEff":0.0, "use":True}
    # Tagging Parameter for the second approach to check systematics                                                                                                                          
    #configdict["TaggingCalibration"]["SS"] = {"p0": 0.44907, "dp0": 0.0, "p1": 0.95005, "dp1": 0.0,
    #                                          "average": 0.43744, "tagEff":0.63926, "aTagEff":0.0, "use":True, }
    #configdict["TaggingCalibration"]["OS"] = {"p0": 0.39432, "dp0": 0.0, "p1": 0.97298, "dp1": 0.0,
    #                                          "average": 0.369798, "tagEff":0.37151, "aTagEff":0.0, "use":True}
    
    configdict["Acceptance"] = { "knots": [0.50, 1.0,  1.5, 2.0, 3.0, 12.0],
                                 "values": [0.390584697499, 0.607485250832, 0.835861005948, 1.05312639959, 1.16345973924, 1.26970499451] }


    configdict["constParams"] = []
    configdict["constParams"].append('Gammas_Bs2DsK')
    configdict["constParams"].append('deltaGammas_Bs2DsK')
    #configdict["constParams"].append('C_Bs2DsPi')
    #configdict["constParams"].append('Cbar_Bs2DsPi')
    #configdict["constParams"].append('S_Bs2DsPi')
    #configdict["constParams"].append('Sbar_Bs2DsPi')
    #configdict["constParams"].append('D_Bs2DsPi')
    #configdict["constParams"].append('Dbar_Bs2DsPi')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('DeltaMs_Bs2DsK')
    configdict["constParams"].append('var1')
    configdict["constParams"].append('var2')
    configdict["constParams"].append('var3')
    configdict["constParams"].append('var4')
    configdict["constParams"].append('var5')
    configdict["constParams"].append('var6')
    configdict["constParams"].append('tagEff_OS')
    configdict["constParams"].append('tagEff_SS')
    configdict["constParams"].append('tagEff_Both')
    configdict["constParams"].append('aTagEff_OS')
    configdict["constParams"].append('aTagEff_SS')
    configdict["constParams"].append('aTagEff_Both')
    #configdict["constParams"].append('p0_OS')
    #configdict["constParams"].append('p0_SS')
    #configdict["constParams"].append('p1_OS')
    #configdict["constParams"].append('p1_SS')
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


    return configdict
