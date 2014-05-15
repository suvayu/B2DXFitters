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
    '''
    #tac varr 1
    configdict["tacc_knots"]  = [0.25, 0.6, 1.0, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [1.4660e-01*0.886,
                                 2.5055e-01*0.923,
                                 6.5821e-01*0.950,
                                 1.0272e+00*0.999,
                                 1.2518e+00*1.000,
                                 1.2233e+00*1.021]
    
    #tac varr 1                                                                                                                                                                               
    configdict["tacc_knots"]  = [0.25, 0.6, 1.0, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [1.4660e-01*1.59119e-01/1.79588e-01,
                                 2.5055e-01*3.19402e-01/3.43393e-01,
                                 6.5821e-01*6.92211e-01/7.25033e-01,
                                 1.0272e+00*1.12267e+00/1.12312e+00,
                                 1.2518e+00*1.24495e+00/1.24522e+00,
                                 1.2233e+00*1.29146e+00/1.26480e+00]                             
    
    #tac var 2                                                                                                                                                                         
    configdict["tacc_knots"]  = [0.3, 0.6, 1.0, 2.0, 3.0, 12.0]                                                                                                                        
    configdict["tacc_values"] = [2.0353e-01*0.886,
                                 3.1439e-01*0.923,                                                                                                                          
                                 8.6740e-01*0.950,                                                                                                                          
                                 1.0716e+00*0.999,                                                                                                                          
                                 1.2516e+00*1.000,                                                                                                                          
                                 1.2244e+00*1.021]                                 
    
    #tac var 2
    configdict["tacc_knots"]  = [0.3, 0.6, 1.0, 2.0, 3.0, 12.0]                                                                                                                               
    configdict["tacc_values"] = [2.0353e-01*2.28758e-01/2.50541e-01,                                                                                                                         
                                 3.1441e-01*3.67539e-01/3.91807e-01,                                                                                                                         
                                 8.6750e-01*7.04870e-01/7.37456e-01,                                                                                                                         
                                 1.0717e+00*1.12221e+00/1.12198e+00,                                                                                                                          
                                 1.2516e+00*1.24491e+00/1.24520e+00,                                                                                                                                                           1.2246e+00*1.29103e+00/1.26390e+00]                                              
    #tac varr 4                                                                                                                                                                               
    configdict["tacc_knots"]  = [0.4, 0.6, 1.0, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [3.1986e-01*3.66515e-01/3.91532e-01,
                                 3.9650e-01*4.58456e-01/4.85499e-01,
                                 6.8934e-01*7.31873e-01/7.61549e-01,
                                 1.0288e+00*1.11973e+00/1.12057e+00,
                                 1.2517e+00*1.24510e+00/1.24539e+00,
                                 1.2247e+00*1.28920e+00/1.26286e+00]

    
    #tac varr 5                                                                                                                                                                                 
    configdict["tacc_knots"]  = [0.45, 0.75, 1.0, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [3.8610e-01*4.34678e-01/4.59885e-01,
                                 5.0599e-01*5.72151e-01/5.99696e-01,
                                 7.3814e-01*7.87215e-01/8.14427e-01,
                                 1.0408e+00*1.12410e+00/1.12255e+00,
                                 1.2518e+00*1.24565e+00/1.24574e+00,
                                 1.2235e+00*1.28675e+00/1.25830e+00]

    
    #tac varr 6                                                                                                                                                                                 
    configdict["tacc_knots"]  = [0.5, 0.75, 1.0, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [4.4822e-01*5.00885e-01/5.26632e-01,
                                 5.4895e-01*6.14504e-01/6.41915e-01,
                                 7.4500e-01*7.96735e-01/8.23778e-01,
                                 1.0435e+00*1.12472e+00/1.12286e+00,
                                 1.2516e+00*1.24530e+00/1.24573e+00,
                                 1.2256e+00*1.28692e+00/1.25850e+00]
    
    #tac varr 7                                                                                                                                                                                 
    configdict["tacc_knots"]  = [0.5, 1.0, 1.5, 2.0, 3.0, 12.0]
    #LT 0.4 - 12.5
    
    configdict["tacc_values"] = [4.6290e-01*5.00641e-01/5.22135e-01,
                                 6.9859e-01*7.27863e-01/7.50192e-01,
                                 8.9587e-01*9.89815e-01/1.01042e+00,
                                 1.1520e+00*1.16015e+00/1.13915e+00,
                                 1.2544e+00*1.24745e+00/1.24743e+00,
                                 1.2582e+00*1.28263e+00/1.23483e+00]
    '''
    # LT 0.4 - 15
    configdict["tacc_knots"]  = [0.5, 1.0, 1.5, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [4.5832e-01*5.03902e-01/5.26256e-01,
                                 6.8898e-01*7.32741e-01/7.40768e-01,
                                 8.8522e-01*9.98736e-01/1.02107e+00,
                                 1.1292e+00*1.16514e+00/1.13483e+00,
                                 1.2233e+00*1.25167e+00/1.24545e+00,
                                 1.2277e+00*1.28624e+00/1.23243e+00]
    
    configdict["tagEff_OS"] = 0.387
    configdict["tagEff_SS"] = 0.4772
    configdict["adet"] = 0.01
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
    
    configdict["TerrFile"]     = "../data/workspace/MDFitter/template_Data_Terr_BsDsK.root"
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
