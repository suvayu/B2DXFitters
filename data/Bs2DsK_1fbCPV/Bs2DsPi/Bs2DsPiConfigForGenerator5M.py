def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.661   # in ps^{-1}
    configdict["DeltaGammas"] = -0.105

    configdict["Gammad"]      =  0.656   # in ps^{-1}
    configdict["DeltaGammad"] =  0.

    configdict["DeltaMs"]     =  17.768    # in ps^{-1}
    configdict["DeltaMd"]     =  0.507   # in ps^{-1}

    configdict["GammaLb"]    =  0.700    # in ps^{-1}
    configdict["GammaCombo"] =  0.800
       
    configdict["StrongPhase_d"] = 20. / 180. * pi
    configdict["StrongPhase_s"] = 30. / 180. * pi
    configdict["WeakPhase"]     = 70. / 180. * pi

    configdict["ArgLf_d"]       = configdict["StrongPhase_d"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_d"] = configdict["StrongPhase_d"] + configdict["WeakPhase"]
    configdict["ModLf_d"]       = 0.015
    
    configdict["ArgLf_s"]       = configdict["StrongPhase_s"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_s"] = configdict["StrongPhase_s"] + configdict["WeakPhase"]
    configdict["ModLf_s"]       = 0.372

    configdict["calibration_p0"]  = [0.3927, 0.4244]
    configdict["calibration_p1"]  = [0.9818, 1.2550]
    configdict["calibration_av"]  = [0.3919, 0.4097]
       
    configdict["resolutionScaleFactor"] = 1.37
    configdict["resolutionMeanBias"]    = 0.0
    
    configdict["nBinsMistag"]   = 50
    configdict["nBinsProperTimeErr"]   = 50
    configdict["nBinsAcceptance"]   = 740
    
    configdict["lumRatioDown"] =  0.59
    configdict["lumRatioUp"] =  0.44
    configdict["lumRatio"] =  configdict["lumRatioUp"]/(configdict["lumRatioDown"]+configdict["lumRatioUp"])
            
    configdict["timeRange"] = [0.2, 15]

    configdict["tacc_size"]   = 6
    configdict["tacc_knots"]  = [0.25, 0.5, 1.0, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [1.77520e-01, 2.89603e-01, 6.79455e-01, 1.11726e+00, 1.23189e+00, 1.26661e+00] 

    configdict["tagEff_OS"] = 0.387
    configdict["tagEff_SS"] = 0.4772

    configdict["tagEff_signal"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_dpi"]       = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_dsk"]       = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_dspi"]      = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_lcpi"]      = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_combo"]     = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_dsstpi"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_dsrho"]     = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    

    configdict["aprod_signal"]    = 0.0 #0.0
    configdict["aprod_dpi"]       = 0.0 #0.0 
    configdict["aprod_dsk"]       = 0.0 #3
    configdict["aprod_dspi"]      = 0.0 # 3
    configdict["aprod_lcpi"]      = 0.0 # 3
    configdict["aprod_combo"]     = 0.0 #3
    configdict["aprod_dsstpi"]    = 0.0 #3
    configdict["aprod_dsrho"]     = 0.0 #3
                                    
    configdict["atageff_signal"]    = [0.0, 0.0, 0.0]
    configdict["atageff_dpi"]       = [0.0, 0.0, 0.0]
    configdict["atageff_dsk"]       = [0.0, 0.0, 0.0]
    configdict["atageff_dspi"]      = [0.0, 0.0, 0.0]
    configdict["atageff_lcpi"]      = [0.0, 0.0, 0.0]
    configdict["atageff_combo"]     = [0.0, 0.0, 0.0]
    configdict["atageff_dsstpi"]    = [0.0, 0.0, 0.0]
    configdict["atageff_dsrho"]     = [0.0, 0.0, 0.0]

    configdict["adet_signal"]    = 0.0
    configdict["adet_dpi"]       = 0.0
    configdict["adet_dsk"]       = 0.0
    configdict["adet_dspi"]      = 0.0
    configdict["adet_lcpi"]      = 0.0
    configdict["adet_combo"]     = 0.0
    configdict["adet_dsstpi"]    = 0.0
    configdict["adet_dsrho"]     = 0.0
    
    configdict["num_signal"]    = [4884, 10783, 7585, 1702, 4473]
    configdict["num_dpi"]       = [374,  6,     93,   30,   0   ]
    configdict["num_dsk"]       = [40,   47,    40,   8,    21  ]
    configdict["num_dspi"]      = [77*0.5,   96*0.5,  84*0.5,   25*0.5,   41*0.5]
    configdict["num_lcpi"]      = [290,  36,    69,   1,    0   ]
    configdict["num_combo"]     = [3188, 1537,  1403, 1617, 4493]
    configdict["num_dsstpi"]    = [77*0.5,   96*0.5,  84*0.5,   25*0.5,   41*0.5]
    configdict["num_dsrho"]     = [0.0,  0.0,   0.0,  0.0,  0.0 ]

    #----------------------------Signal----------------------------#

    configdict["mean"]    = [5367.51, 5367.51, 5367.51, 5367.51, 5367.51]
    configdict["sigma1"]  = [1.1538e+01*1.28,  1.6598e+01*1.22,  1.1646e+01*1.28,  1.1428e+01*1.28,  1.1989e+01*1.28]                            
    configdict["sigma2"]  = [1.6181e+01*1.22,  1.1488e+01*1.28,  1.4992e+01*1.22,  1.6866e+01*1.22,  1.7588e+01*1.22]                                    
    configdict["alpha1"]  = [1.9050e+00,  -2.0856e+00, 1.7019e+00,  1.9066e+00,  1.8497e+00 ]                                                     
    configdict["alpha2"]  = [-2.0423e+00, 1.8947e+00,  -1.8418e+00, -2.2615e+00, -2.0560e+00]                                                     
    configdict["n1"]      = [1.1327e+00,  5.2735e+00,  1.2686e+00,  1.1585e+00,  1.2326e+00]
    configdict["n2"]      = [6.1273e+00,  1.1497e+00,  9.6571e+00,  4.1167e+00,  7.8246e+00]
    configdict["frac"]    = [5.5417e-01,  4.4171e-01,  4.6731e-01,  5.9179e-01,  6.2376e-01]

    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    configdict["sigma1Ds"]  = [4.3930e+00*1.19,  8.7215e+00*1.16,  7.8768e+00*1.16,  6.7734e+00*1.16,  8.4187e+00*1.16 ]   
    configdict["sigma2Ds"]  = [7.1493e+00*1.16,  4.6238e+00*1.19,  4.5946e+00*1.19,  6.4937e+00*1.19,  7.2604e+00*1.19 ]   
    configdict["alpha1Ds"]  = [2.1989e+00,  1.7979e+00,  1.9708e+00,  9.1754e-01,  9.4869e-01 ]                       
    configdict["alpha2Ds"]  = [-2.0186e+00, -3.2123e+00, -2.7746e+00, -1.2753e+00, -1.0429e+00]                                                    
    configdict["n1Ds"]      = [7.9389e-01,  2.6693e+00,  2.0849e+00,  9.2763e+00,  1.2886e+01 ]
    configdict["n2Ds"]      = [5.5608e+00,  4.4751e-01,  1.0774e+00,  4.6466e+01,  6.9998e+01 ]
    configdict["fracDs"]    = [0.25406,     3.5389e-01,  4.5702e-01,  3.5803e-01,  4.9901e-01 ]
           
    configdict["cB1"] = [-6.2895e-03, -9.3775e-03, -7.9542e-03, -7.1989e-03, -4.8664e-03]
    configdict["cB2"] = [0.0, 0.0, 0.0, 0.0, 0.0]
    configdict["fracBsComb"] = [7.8065e-01, 6.4053e-01, 7.7315e-01, 4.0456e-01, 5.1449e-01]

    configdict["cD"] = [-4.2766e-03, -2.0470e-03, -4.4298e-03, -4.9326e-03, -2.1470e-03]
    configdict["fracDsComb"] = [9.5698e-01, 5.9161e-01, 8.2227e-01,  1.0, 1.0]

    configdict["fracPIDKComb"] = 8.9331e-01
       
    return configdict
