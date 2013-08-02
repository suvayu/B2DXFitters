def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  1/0.657   # in ps^{-1}
    configdict["DeltaGammas"] = -0.105

    configdict["Gammad"]      =  1./0.656   # in ps^{-1}
    configdict["DeltaGammad"] =  0.

    configdict["DeltaMs"]     =  17.719    # in ps^{-1}
    configdict["DeltaMd"]     =  0.507   # in ps^{-1}

    configdict["GammaLb"]    =  1./0.702    # in ps^{-1}
    configdict["GammaCombo"] =  1./0.800
       
    configdict["TauRes"]    =  0.05  
        
    configdict["StrongPhase_d"] = 20. / 180. * pi
    configdict["StrongPhase_s"] = 30. / 180. * pi
    configdict["WeakPhase"]     = 140. / 180. * pi

    configdict["ArgLf_d"]       = configdict["StrongPhase_d"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_d"] = configdict["StrongPhase_d"] + configdict["WeakPhase"]
    configdict["ModLf_d"]       = 0.015
    
    configdict["ArgLf_s"]       = configdict["StrongPhase_s"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_s"] = configdict["StrongPhase_s"] + configdict["WeakPhase"]
    configdict["ModLf_s"]       = 0.372

    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    configdict["TagOmegaSig"]   = 0.391

    configdict["lumRatio"] =  0.44/(0.59+0.44)

    configdict["tagEff_signal"]    = 0.40
    configdict["tagEff_dk"]        = 0.40
    configdict["tagEff_dsk"]       = 0.40
    configdict["tagEff_dspi"]      = 0.40
    configdict["tagEff_lck"]       = 0.40
    configdict["tagEff_combo"]     = 0.40
    configdict["tagEff_dsdsstp"]   = 0.40
    configdict["tagEff_lm1"]       = 0.40
    configdict["tagEff_lm2"]       = 0.40

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
    
    configdict["num_signal"]    = 1850.
    configdict["num_dk"]        = 20.
    configdict["num_dsk"]       = 100.
    configdict["num_dspi"]      = 715.
    configdict["num_lck"]       = 25.
    configdict["num_combo"]     = 4040.
    configdict["num_dsdsstp"]   = 180.
    configdict["num_lm1"]       = 50.
    configdict["num_lm2"]       = 430.
        
    #----------------------------Signal----------------------------#

    configdict["mean"]    = 5369
    configdict["sigma1"]  = 10.627*1.145
    configdict["sigma2"]  = 15.289*1.255
    configdict["alpha1"]  = 1.6086
    configdict["alpha2"]  = -1.9642
    configdict["n1"]      = 1.5879
    configdict["n2"]      = 5.1315
    configdict["frac"]    = 0.43480

    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = 1969
    configdict["sigma1Ds"]  = 8.7205*1.074
    configdict["sigma2Ds"]  = 4.5795*1.185
    configdict["alpha1Ds"]  = 1.9260
    configdict["alpha2Ds"]  = -3.2773
    configdict["n1Ds"]      = 1.4224
    configdict["n2Ds"]      = 0.36197
    configdict["fracDs"]    = 0.36627
        
                                        
    configdict["tacc_exponent_pl"] = 1.8627e+00 #1.849
    configdict["tacc_offset_pl"]   = 1.6710e-02 #0.0373
    configdict["tacc_beta_pl"]     = 3.4938e-02 #0.0363
    configdict["tacc_turnon_pl"]   = 1.3291e+00 #1.215
    
    configdict["cB"] = -9.2354e-04
        
    configdict["cD"] = -8.8642e-03
    configdict["fracDsComb"] = 5.1911e-01

    configdict["fracPIDKComb1"] = 6.3516e-01
    configdict["fracPIDKComb2"] = 5.9685e-01
    
    configdict["frac_dsdsstp"]   = 0.9
    
    #configdict["frac_g1_1lmk"]  = 0.14536
    #configdict["frac_g1_2lmk"]  = 0.169091
                
    configdict["frac_g2_1"]  = 5.6122e-08 #0.31266
    #configdict["frac_g2_2"]  = 0.202776
    
       
    return configdict
