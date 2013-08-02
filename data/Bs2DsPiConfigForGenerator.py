def getconfig() :

    configdict = {}
    
    from math import pi

    configdict["lumRatio"] =  0.44/(0.59+0.44)

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  1/0.657    # in ps^{-1}
    configdict["DeltaGammas"] = -0.104

    configdict["Gammad"]      =  1./0.656   # in ps^{-1}
    configdict["DeltaGammad"] =  0.

    configdict["DeltaMs"]     =  17.719     # in ps^{-1}
    configdict["DeltaMd"]     =  0.507      # in ps^{-1}

    configdict["GammaLb"]    =  1./0.702    # in ps^{-1}
    configdict["GammaCombo"] =  1./0.800

    configdict["TauRes"]    =  0.05  
        
    configdict["StrongPhase_d"] = 20. / 180. * pi
    configdict["StrongPhase_s"] = 30. / 180. * pi
    configdict["WeakPhase"]     = 140./180*pi #70. / 180. * pi

    configdict["ArgLf_d"]       = configdict["StrongPhase_d"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_d"] = configdict["StrongPhase_d"] + configdict["WeakPhase"]
    configdict["ModLf_d"]       = 0.015
    
    configdict["ArgLf_s"]       = configdict["StrongPhase_s"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_s"] = configdict["StrongPhase_s"] + configdict["WeakPhase"]
    configdict["ModLf_s"]       = 0.372

    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    configdict["TagOmegaSig"]   = 0.391
    

    configdict["tagEff_signal"]    = 0.40
    configdict["tagEff_dpi"]       = 0.40
    configdict["tagEff_dspi"]      = 0.40
    configdict["tagEff_lcpi"]      = 0.40
    configdict["tagEff_combo"]     = 0.40
    configdict["tagEff_lm1"]       = 0.40
    configdict["tagEff_lm2"]       = 0.40
    configdict["tagEff_dsk"]       = 0.40

    configdict["aprod_signal"]     = 0.00
    configdict["aprod_dpi"]        = 0.00
    configdict["aprod_bddspi"]     = 0.00
    configdict["aprod_lcpi"]       = 0.00
    configdict["aprod_combo"]      = 0.00
    configdict["aprod_lm1"]        = 0.00
    configdict["aprod_lm2"]        = 0.00
    configdict["aprod_dsk"]        = 0.00

    configdict["adet_signal"]     = 0.00
    configdict["adet_dpi"]        = 0.00
    configdict["adet_bddspi"]     = 0.00
    configdict["adet_lcpi"]       = 0.00
    configdict["adet_combo"]      = 0.00
    configdict["adet_lm1"]        = 0.00
    configdict["adet_lm2"]        = 0.00
    configdict["adet_dsk"]        = 0.00

    configdict["atageff_signal"]     = 0.00
    configdict["atageff_dpi"]        = 0.00
    configdict["atageff_bddspi"]     = 0.00
    configdict["atageff_lcpi"]       = 0.00
    configdict["atageff_combo"]      = 0.00
    configdict["atageff_lm1"]        = 0.00
    configdict["atageff_lm2"]        = 0.00
    configdict["atageff_dsk"]        = 0.00
    
    configdict["num_signal"]    = 30000.
    configdict["num_dpi"]       = 500.
    configdict["num_dspi"]      = 200.
    configdict["num_lcpi"]      = 400.
    configdict["num_combo"]     = 13500. #0.
    configdict["num_lm1"]       = 300. #00.
    configdict["num_lm2"]       = 1070.
    configdict["num_dsk"]       = 150.
        
    #----------------------------Signal----------------------------#

    configdict["mean"]    = 5369
    configdict["sigma1"]  = 17.396*1.145
    configdict["sigma2"]  = 11.028*1.255
    configdict["alpha1"]  = 1.8615
    configdict["alpha2"]  = -2.6267
    configdict["n1"]      = 1.3245
    configdict["n2"]      = 2.1862
    configdict["frac"]    = 0.55406
    
    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331

    configdict["meanDs"]    = 1969
    configdict["sigma1Ds"]  = 7.6215*1.074
    configdict["sigma2Ds"]  = 4.4422*1.185
    configdict["alpha1Ds"]  = 1.8802
    configdict["alpha2Ds"]  = -2.2066
    configdict["n1Ds"]      = 2.5713
    configdict["n2Ds"]      = 1.8122
    configdict["fracDs"]    = 0.44075
                                            
    configdict["tacc_exponent_signal"] = 1.8627e+00
    configdict["tacc_offset_signal"]   = 1.6710e-02
    configdict["tacc_beta_signal"]     = 3.4938e-02
    configdict["tacc_turnon_signal"]   = 1.3291e+00
                            
    #----------------------------B->DPi----------------------------#

    configdict["tacc_exponent_dpi"] = 1.8627e+00
    configdict["tacc_offset_dpi"]   = 1.6710e-02
    configdict["tacc_beta_dpi"]     = 3.4938e-02
    configdict["tacc_turnon_dpi"]   = 1.3291e+00
                
    #---------------------------Bd->DsPi----------------------------#

    configdict["tacc_exponent_dspi"] = 1.8627e+00
    configdict["tacc_offset_dspi"]   = 1.6710e-02
    configdict["tacc_beta_dspi"]     = 3.4938e-02
    configdict["tacc_turnon_dspi"]   = 1.3291e+00
              
    #---------------------------Lb->LcPi----------------------------#

    configdict["tacc_exponent_lcpi"] = 1.8627e+00
    configdict["tacc_offset_lcpi"]   = 1.6710e-02
    configdict["tacc_beta_lcpi"]     = 3.4938e-02
    configdict["tacc_turnon_lcpi"]   = 1.3291e+00
    
    #---------------------------Combo----------------------------#

    configdict["exposlope_combo"]   = -1.9977*pow(10,-3)
    
    configdict["cB1"] = -3.0873e-03 
    configdict["cB2"] = 0.0
    configdict["fracBsComb"] = 6.5400e-01

    configdict["cD"] = -2.7273e-03
    configdict["fracDsComb"] = 0.37379

    configdict["fracPIDKComb"] = 9.0404e-01
    
    configdict["tacc_exponent_combo"] = 1.8627e+00
    configdict["tacc_offset_combo"]   = 1.6710e-02
    configdict["tacc_beta_combo"]     = 3.4938e-02
    configdict["tacc_turnon_combo"]   = 1.3291e+00
                
    #--------------------------Low Mass 1--------------------------#

    configdict["frac_g1_1"]  = 0.89361
    configdict["frac_g1_2"]  = 0.092997
                
    configdict["tacc_exponent_lm1"] = 1.8627e+00
    configdict["tacc_offset_lm1"]   = 1.6710e-02
    configdict["tacc_beta_lm1"]     = 3.4938e-02
    configdict["tacc_turnon_lm1"]   = 1.3291e+00
                
    #--------------------------Low Mass 1--------------------------#

    configdict["frac_g2_1"]  = 0.775701
    configdict["frac_g2_2"]  = 0.149533
    
    configdict["tacc_exponent_lm2"] = 1.8627e+00
    configdict["tacc_offset_lm2"]   = 1.6710e-02
    configdict["tacc_beta_lm2"]     = 3.4938e-02
    configdict["tacc_turnon_lm2"]   = 1.3291e+00
                
    #---------------------------Bs->DsK----------------------------#
    
    configdict["tacc_exponent_dsk"] = 1.8627e+00
    configdict["tacc_offset_dsk"]   = 1.6710e-02
    configdict["tacc_beta_dsk"]     = 3.4938e-02
    configdict["tacc_turnon_dsk"]   = 1.3291e+00
                
    
                          
      
    
    return configdict
