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

    configdict["GammaLb"]    =  0.702    # in ps^{-1}
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

    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    configdict["TagOmegaSig"]   = 0.391

    configdict["resolutionScaleFactor"] = 1.15 #1.37
    configdict["resolutionMeanBias"]    = 0.0
    
    configdict["nBinsMistag"]   = 50
    configdict["nBinsProperTimeErr"]   = 50
    configdict["nBinsAcceptance"]   = 740
    
    configdict["lumRatio"] =  0.44/(0.59+0.44)

    configdict["tagEff_signal"]    = 0.403
    configdict["tagEff_dk"]        = 0.403
    configdict["tagEff_dsk"]       = 0.403
    configdict["tagEff_dspi"]      = 0.403
    configdict["tagEff_lck"]       = 0.403
    configdict["tagEff_combo"]     = 0.403
    configdict["tagEff_dsdsstp"]   = 0.403
    configdict["tagEff_lm1"]       = 0.403
    configdict["tagEff_lm2"]       = 0.403

    configdict["aprod_signal"]    = 0.0 #0.03
    configdict["aprod_dk"]        = 0.0 #0.03
    configdict["aprod_dsk"]       = 0.0 #3
    configdict["aprod_dspi"]      = 0.0 # 3
    configdict["aprod_lck"]       = 0.0 # 3
    configdict["aprod_combo"]     = 0.0 #3
    configdict["aprod_dsdsstp"]   = 0.0 #3
    configdict["aprod_lm1"]       = 0.0 #3
    configdict["aprod_lm2"]       = 0.0 #3
                                    
    configdict["atageff_signal"]    = 0.0 #1
    configdict["atageff_dk"]        = 0.0 #2
    configdict["atageff_dsk"]       = 0.0 #1
    configdict["atageff_dspi"]      = 0.0 #1
    configdict["atageff_lck"]       = 0.0 #3
    configdict["atageff_combo"]     = 0.0 #1
    configdict["atageff_dsdsstp"]   = 0.0 #3
    configdict["atageff_lm1"]       = 0.0 #1
    configdict["atageff_lm2"]       = 0.0 #1

    configdict["adet_signal"]    = 0.0
    configdict["adet_dk"]        = 0.0
    configdict["adet_dsk"]       = 0.0
    configdict["adet_dspi"]      = 0.0
    configdict["adet_lck"]       = 0.0
    configdict["adet_combo"]     = 0.0
    configdict["adet_dsdsstp"]   = 0.0
    configdict["adet_lm1"]       = 0.0
    configdict["adet_lm2"]       = 0.0
    
    configdict["num_signal"]    = [308, 608, 500, 115,  326]
    configdict["num_dk"]        = [15,    0,   4,   0,    0]
    configdict["num_dsk"]       = [19,   36,  46,  12,   36]
    configdict["num_dspi"]      = [230*0.936*0.711, 496*0.936*0.711, 328*0.936*0.711, 86*0.936*0.711, 238*0.936*0.711]
    configdict["num_lck"]       = [15,    2,   4,   0,    0]
    configdict["num_combo"]     = [723, 474, 346, 648, 1776]
    configdict["num_dsdsstp"]   = [230*0.064, 496*0.064, 328*0.064, 86*0.064, 238*0.064]
    configdict["num_lm1"]       = [0,     0,   0,   0,    0]
    configdict["num_lm2"]       = [230*0.936*0.289, 496*0.936*0.289, 328*0.936*0.289, 86*0.936*0.289, 238*0.936*0.289]
        
    #----------------------------Signal----------------------------#

    configdict["mean"]    = [5367.51, 5367.51, 5367.51, 5367.51, 5367.51]
    configdict["sigma1"]  = [18.082*1.145,  10.627*1.255,  11.417*1.255,  18.901*1.145,  19.658*1.145 ] 
    configdict["sigma2"]  = [10.727*1.255,  15.289*1.145,  16.858*1.145,  11.058*1.255,  11.512*1.255 ] 
    configdict["alpha1"]  = [2.0550,  1.6086,  2.0304,  2.0490,  1.8844 ]
    configdict["alpha2"]  = [-2.9184, -1.9642, -1.9823, -3.3876, -3.0227]
    configdict["n1"]      = [1.1123,  1.5879,  1.3059,  1.0988,  1.3397 ]
    configdict["n2"]      = [1.3312,  5.1315,  4.2083,  0.96197,  1.2083 ]
    configdict["frac"]    = [0.42743, 0.43480, 0.61540, 0.38142, 0.37901]

    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    configdict["sigma1Ds"]  = [7.6526*1.074,  8.7205*1.074,  5.3844*1.185,  11.590*1.074,  11.217*1.074 ]
    configdict["sigma2Ds"]  = [4.2202*1.185,  4.5795*1.185,  11.981*1.074,  6.0350*1.185,  6.8617*1.185 ]
    configdict["alpha1Ds"]  = [1.9266,  1.9260,  4.8339,  1.5839,  1.0902 ]
    configdict["alpha2Ds"]  = [-2.5456, -3.2773, -3.0116, -6.2018, -2.4987]
    configdict["n1Ds"]      = [2.8434,  1.4224,  48.516,  1.8532,  69.861 ]
    configdict["n2Ds"]      = [1.5942,  0.36197, 0.25888, 65.824,  1.0790 ]
    configdict["fracDs"]    = [0.50702, 0.36627, 0.84549, 0.29362, 0.46289]
        
                                        
    configdict["tacc_exponent_pl"] = 1.8627e+00 #1.849
    configdict["tacc_offset_pl"]   = 1.6710e-02 #0.0373
    configdict["tacc_beta_pl"]     = 3.4938e-02 #0.0363
    configdict["tacc_turnon_pl"]   = 1.3291e+00 #1.215
    
    configdict["cB"] = [-3.3787e-03, -2.1411e-03, -2.9391e-03, -1.5331e-03, -2.1068e-03]
    configdict["cD"] = [-1.5285e-03, -2.0302e-03, -5.4197e-03, -2.7012e-04, -3.5133e-03]
    configdict["fracDsComb"] = [9.4632e-01, 5.2072e-01, 7.5645e-01,  1.0, 1.0]

    configdict["fracPIDKComb1"] = 6.2260e-01
    configdict["fracPIDKComb2"] = 5.6321e-01
    
    configdict["frac_dsdsstp"]   = 0.75
    
    #configdict["frac_g1_1lmk"]  = 0.14536
    #configdict["frac_g1_2lmk"]  = 0.169091
                
    configdict["frac_g2_1"]  = 0.5
    #configdict["frac_g2_2"]  = 0.202776
    
       
    return configdict
