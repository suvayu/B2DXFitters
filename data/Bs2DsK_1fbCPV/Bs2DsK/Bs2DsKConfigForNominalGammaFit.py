def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.661 #0.661   # in ps^{-1}
    configdict["DeltaGammas"] = -0.105 #-0.105
    configdict["DeltaMs"]     =  17.768   # in ps^{-1}
    configdict["StrongPhase"] = -40. / 180. * pi
    configdict["WeakPhase"]   = 100. / 180. * pi
    configdict["ArgLf"]       = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"] = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]       = 0.372
    
    configdict["calibration_p0"]  = [0.3834, 0.4244]
    configdict["calibration_p1"]  = [0.9720, 1.2180]
    configdict["calibration_av"]  = [0.3813, 0.4097]

    configdict["constr_p0_B"] = [0.365517, 0.424801, 0.338781]
    configdict["constr_p1_B"] = [0.950216, 1.004340, 0.971845]
    configdict["constr_av_B"] = [0.371147, 0.414892, 0.338493]

    configdict["constr_p0_Bbar"] = [0.376730, 0.404896, 0.338363]
    configdict["constr_p1_Bbar"] = [1.048155, 0.995879, 1.027861]
    configdict["constr_av_Bbar"] = [0.371147, 0.414892, 0.338493]

    configdict["constr_p0_B_err"] = [0.00, 0.00, 0.00]
    configdict["constr_p1_B_err"] = [0.00, 0.00, 0.00]
    configdict["constr_p0_Bbar_err"] = [0.00, 0.00, 0.00]
    configdict["constr_p1_Bbar_err"] = [0.00, 0.00, 0.00]


    #configdict["constr_p0_B_err"] = [0.004389, 0.007146, 0.005959]
    #configdict["constr_p1_B_err"] = [0.039917, 0.148797, 0.038725]
    #configdict["constr_p0_Bbar_err"] = [0.004395, 0.011414, 0.006030]
    #configdict["constr_p1_Bbar_err"] = [0.040072, 0.150355, 0.039962]



    #configdict["calibration_p0"]  = [0.3927, 0.4244]
    #configdict["calibration_p1"]  = [0.9818, 1.2550]
    #configdict["calibration_av"]  = [0.3919, 0.4097]
    
    configdict["tacc_size"]   = 6
    configdict["tacc_knots"]  = [0.5, 1.0, 1.5, 2.0, 3.0, 12.0]
    
    #configdict["tacc_values"] = [1.4525e-01*1.86413e-01/1.93184e-01,
    #                             2.0995e-01*2.83214e-01/3.35302e-01,
    #                             6.2524e-01*7.24952e-01/7.39033e-01,
    #                             1.0291e+00*1.18847e+00/1.16141e+00,
    #                             1.2577e+00*1.33798e+00/1.29660e+00,
    #                             1.2405e+00*1.32593e+00/1.31712e+00]
    configdict["tacc_values"] = [0.4453873694523979, 0.6869245867352556, 0.8719680916278891, 1.1614426699209424, 1.2341250036543179, 1.2852701638596233]
    
    configdict["tagEff_OS"] = 0.387
    configdict["tagEff_SS"] = 0.4772
    configdict["adet_Signal"] = 0.01
    configdict["TagEffSig"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                  configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                  configdict["tagEff_OS"]*configdict["tagEff_SS"]]

    configdict["aTagEffSig"]    = [-0.002756, 0.001837, -0.002315]
    
    configdict["resolutionScaleFactor"] = 1.37 
    configdict["resolutionMeanBias"]    = 0.
    
    configdict["resolutionSigma1"] = 2.21465e-02
    configdict["resolutionSigma2"] = 3.72057e-02
    configdict["resolutionSigma3"] = 6.37859e-02
    configdict["resolutionFrac1"]  = 3.62689e-01
    configdict["resolutionFrac2"]  = 5.65100e-01
        
    configdict["MistagFile"]     = "../data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root"
    configdict["MistagWork"]     = "workspace"
    configdict["MistagTempName"] = ["sigMistagPdf_1", "sigMistagPdf_2", "sigMistagPdf_3"]
    
    configdict["TerrFile"]     = "../data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root"
    configdict["TerrWork"]     = "workspace"
    configdict["TerrTempName"] = "TimeErrorPdf_Bs2DsK"


    configdict["Constrains"] = {
        # multivariate Gaussian constraint for tagging calibration parameters
        'multivar_Bs2DsKMistagCalib_p0p1': [
            # variable names
            [   'p0_B_0', 'p1_B_0', #B
                'p0_B_1', 'p1_B_1', #B
                'p0_B_2', 'p1_B_2', #B
                'p0_Bbar_0', 'p1_Bbar_0', #Bbar
                'p0_Bbar_1', 'p1_Bbar_1', #Bbar
                'p0_Bbar_2', 'p1_Bbar_2', ], #Bbar 
            # errors
            [   0.004389, 0.039917, 0.007146, 0.148797, 0.005959, 0.038725,
                0.004395, 0.040072, 0.011414, 0.150355, 0.006030, 0.039962, ],
            # correlation matrix
            [   [  1.000000000, -0.111790756,  0.000000000,  0.000000000,  0.495659195, -0.121263673,  0.883403568, -0.090341177,  0.000000000,  0.000000000,  0.436308995, -0.115934567 ],
                [ -0.111790756,  1.000000000,  0.000000000,  0.000000000, -0.170723691,  0.368653977, -0.090433543,  0.808300854,  0.000000000,  0.000000000, -0.138612127,  0.303210400 ],
                [  0.000000000,  0.000000000,  1.000000000, -0.122610568,  0.658158523, -0.541239353,  0.000000000,  0.000000000,  0.938782519, -0.120298908,  0.633382320, -0.525375965 ],
                [  0.000000000,  0.000000000, -0.122610568,  1.000000000, -0.631056425,  0.811985505,  0.000000000,  0.000000000, -0.122445304,  0.986409445, -0.608419498,  0.787887823 ],
                [  0.495659195, -0.170723691,  0.658158523, -0.631056425,  1.000000000, -0.874463407,  0.436823522, -0.137898963,  0.622128000, -0.622176239,  0.940276558, -0.841479510 ],
                [ -0.121263673,  0.368653977, -0.541239353,  0.811985505, -0.874463407,  1.000000000, -0.104272659,  0.297793832, -0.514032745,  0.800698231, -0.830102616,  0.950602614 ],
                [  0.883403568, -0.090433543,  0.000000000,  0.000000000,  0.436823522, -0.104272659,  1.000000000, -0.111883376,  0.000000000,  0.000000000,  0.494752953, -0.134191009 ],
                [ -0.090341177,  0.808300854,  0.000000000,  0.000000000, -0.137898963,  0.297793832, -0.111883376,  1.000000000,  0.000000000,  0.000000000, -0.170921923,  0.374807565 ],
                [  0.000000000,  0.000000000,  0.938782519, -0.122445304,  0.622128000, -0.514032745,  0.000000000,  0.000000000,  1.000000000, -0.123454584,  0.672735926, -0.556618676 ],
                [  0.000000000,  0.000000000, -0.120298908,  0.986409445, -0.622176239,  0.800698231,  0.000000000,  0.000000000, -0.123454584,  1.000000000, -0.616497607,  0.798523473 ],
                [  0.436308995, -0.138612127,  0.633382320, -0.608419498,  0.940276558, -0.830102616,  0.494752953, -0.170921923,  0.672735926, -0.616497607,  1.000000000, -0.878334170 ],
                [ -0.115934567,  0.303210400, -0.525375965,  0.787887823, -0.841479510,  0.950602614, -0.134191009,  0.374807565, -0.556618676,  0.798523473, -0.878334170,  1.000000000 ], ],
            ],
        'multivar_Bs2DsKTagEffAsyms': [
            [   'tagEffSig_1', 'tagEffSig_2', 'tagEffSig_3',
                'aTagEff_1', 'aTagEff_2', 'aTagEff_3' ],
            [   0.001952, 0.002330, 0.001843, 0.001628, 0.001029, 0.001629 ],
            [   [   1.0000000000000000e+00,  -9.6310597862753633e-01,   2.4948159233783404e-01,   1.0144953478135443e-02,   7.0203224420703663e-03,   1.0233976427853671e-02 ],
                [  -9.6310597862753633e-01,   1.0000000000000000e+00,   2.0335415458912924e-02,  -8.0556554583657968e-03,  -5.7778847902391142e-03,  -8.1729979402554217e-03 ],
                [   2.4948159233783404e-01,   2.0335415458912924e-02,   1.0000000000000000e+00,   8.9803482925014111e-03,   5.0106145332872738e-03,   8.8849526862593686e-03 ],
                [   1.0144953478135443e-02,  -8.0556554583657968e-03,   8.9803482925014111e-03,   1.0000000000000000e+00,  -9.9965299841531974e-01,   9.9878828433569355e-01 ],
                [   7.0203224420703663e-03,  -5.7778847902391142e-03,   5.0106145332872738e-03,  -9.9965299841531974e-01,   1.0000000000000000e+00,  -9.9759036187377381e-01 ],
                [   1.0233976427853671e-02,  -8.1729979402554217e-03,   8.8849526862593686e-03,   9.9878828433569355e-01,  -9.9759036187377381e-01,   1.0000000000000000e+00 ], ],
            ],
        }
    
        
    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('deltaMs')
    #configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent_BDTGA')
    configdict["constParams"].append('tacc_offset_BDTGA')
    configdict["constParams"].append('tacc_beta_BDTGA')
    configdict["constParams"].append('tacc_turnon_BDTGA')

    return configdict
