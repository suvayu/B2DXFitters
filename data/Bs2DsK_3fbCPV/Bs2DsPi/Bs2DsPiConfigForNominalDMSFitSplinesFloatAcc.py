def getconfig() :

    from Bs2DsPiConfigForNominalMassFit import getconfig as getconfig_nominal
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

    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["SS"] = {"p0": 0.4429, "p1": 0.977, "average": 0.4377, 
                                              "tagEff":0.387, "aTagEff":0.0, "use":True, }
    configdict["TaggingCalibration"]["OS"] = {"p0": 0.375,  "p1": 0.982, "average": 0.3688, 
                                              "tagEff":0.4772, "aTagEff":0.0, "use":False}
    configdict["TaggingCalibration"]["Both"] = {"p0": 0.3397,  "p1": 0.9719, "average": 0.3385}

    configdict["Acceptance"] = { "knots": [0.50, 1.0,  1.5, 2.0, 3.0, 12.0],
                                 "values": [4.5579e-01,7.0310e-01,8.7709e-01,1.1351e+00,1.2233e+00,1.2323e+00] }

    configdict["Resolution"] = { "scaleFactor":{"p0":0.0, "p1":1.37, "p2":0.0}, 
                                 "meanBias":0.0,
                                 "shape": { "sigma1":2.14946e-02, "sigma2":3.67643e-02, "sigma3":6.32869e-02,
                                            "frac1":3.72147e-01, "frac2":5.65150e-01},
                                 "templates": { "fileName":"../data/workspace/MDFitter/template_Data_Terr_Bs2DsPi_BDTGA.root",
                                                "workName":"workspace",
                                                "templateName":"TimeErrorPdf_Bs2DsPi"} }

    #configdict["constr_p0_B"] = [0.365517, 0.424801, 0.338781]
    #configdict["constr_p1_B"] = [0.950216, 1.004340, 0.971845]
    #configdict["constr_av_B"] = [0.371147, 0.414892, 0.338493]

    #configdict["constr_p0_Bbar"] = [0.376730, 0.404896, 0.338363]
    #configdict["constr_p1_Bbar"] = [1.048155, 0.995879, 1.027861]
    #configdict["constr_av_Bbar"] = [0.371147, 0.414892, 0.338493]

    #configdict["MistagFile"]     = "../data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root"
    #configdict["MistagWork"]     = "workspace"
    #configdict["MistagTempName"] = ["sigMistagPdf_1", "sigMistagPdf_2", "sigMistagPdf_3"]


    configdict["constParams"] = []
    configdict["constParams"].append('Gammas_Bs2DsPi')
    configdict["constParams"].append('deltaGammas_Bs2DsPi')
    configdict["constParams"].append('C_Bs2DsPi')
    configdict["constParams"].append('Cbar_Bs2DsPi')
    configdict["constParams"].append('S_Bs2DsPi')
    configdict["constParams"].append('Sbar_Bs2DsPi')
    configdict["constParams"].append('D_Bs2DsPi')
    configdict["constParams"].append('Dbar_Bs2DsPi')
    configdict["constParams"].append('tagEff_OS')
    configdict["constParams"].append('tagEff_SS')
    configdict["constParams"].append('tagEff_Both')
    configdict["constParams"].append('aTagEff_OS')
    configdict["constParams"].append('aTagEff_SS')
    configdict["constParams"].append('aTagEff_Both')
    configdict["constParams"].append('p0_B_OS')
    configdict["constParams"].append('p1_B_OS')
    configdict["constParams"].append('average_B_OS')
    configdict["constParams"].append('p0_B_SS')
    configdict["constParams"].append('p1_B_SS')
    configdict["constParams"].append('average_B_SS')
    configdict["constParams"].append('p0_B_Both')
    configdict["constParams"].append('p1_B_Both')
    configdict["constParams"].append('average_B_Both')
    configdict["constParams"].append('p0_Bbar_OS')
    configdict["constParams"].append('p1_Bbar_OS')
    configdict["constParams"].append('average_Bbar_OS')
    configdict["constParams"].append('p0_Bbar_SS')
    configdict["constParams"].append('p1_Bbar_SS')
    configdict["constParams"].append('average_Bbar_SS')
    configdict["constParams"].append('p0_Bbar_Both')
    configdict["constParams"].append('p1_Bbar_Both')
    configdict["constParams"].append('average_Bbar_Both')


    #configdict["constParams"].append('DeltaMs')

    return configdict
