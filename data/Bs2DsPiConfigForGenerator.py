def getconfig() :

    configdict = {}
    
    from math import pi

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
    configdict["StrongPhase_s"] = 20. / 180. * pi
    configdict["WeakPhase"]   = 70. / 180. * pi

    configdict["ArgLf_d"]       = configdict["StrongPhase_d"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_d"] = configdict["StrongPhase_d"] + configdict["WeakPhase"]
    configdict["ModLf_d"]       = 0.015
    
    configdict["ArgLf_s"]       = configdict["StrongPhase_s"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_s"] = configdict["StrongPhase_s"] + configdict["WeakPhase"]
    configdict["ModLf_s"]       = 0.372

    configdict["tagEff_signal"]    = 0.40
    configdict["tagEff_dpi"]       = 0.40
    configdict["tagEff_dspi"]      = 0.40
    configdict["tagEff_lcpi"]      = 0.40
    configdict["tagEff_combo"]     = 0.40
    configdict["tagEff_lm1"]       = 0.40
    configdict["tagEff_lm2"]       = 0.40

    configdict["num_signal"]    = 25000.
    configdict["num_dpi"]       = 1000.
    configdict["num_dspi"]      = 830.
    configdict["num_lcpi"]      = 1000.
    configdict["num_combo"]     = 15000.
    configdict["num_lm1"]       = 33000.
    configdict["num_lm2"]       = 1070.
        
    #----------------------------Signal----------------------------#

    configdict["mean"]    = 5369
    configdict["sigma1"]  = 12.691
    configdict["sigma2"]  = 20.486
    configdict["alpha1"]  = 2.1260
    configdict["alpha2"]  = -2.0649
    configdict["n1"]      = 1.1019
    configdict["n2"]      = 5.8097
    configdict["frac"]    = 0.78044
    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331
                                        
    configdict["tacc_slope_signal"]   = 1.1
    configdict["tacc_offset_signal"]  = 0.186
    configdict["tacc_beta_signal"]    = 0.039
            
    #----------------------------B->DPi----------------------------#

    configdict["tacc_slope_dpi"]   = 1.1
    configdict["tacc_offset_dpi"]  = 0.186
    configdict["tacc_beta_dpi"]    = 0.039

    #---------------------------Bd->DsPi----------------------------#

    configdict["tacc_slope_dspi"]   = 1.1
    configdict["tacc_offset_dspi"]  = 0.186
    configdict["tacc_beta_dspi"]    = 0.039
            
    #---------------------------Lb->LcPi----------------------------#

    configdict["tacc_slope_lcpi"]   = 1.1
    configdict["tacc_offset_lcpi"]  = 0.186
    configdict["tacc_beta_lcpi"]    = 0.039

    #---------------------------Combo----------------------------#

    configdict["exposlope_combo"]   = -1.9977*pow(10,-3)
    
    configdict["tacc_slope_combo"]   = 1.1
    configdict["tacc_offset_combo"]  = 0.186
    configdict["tacc_beta_combo"]    = 0.039

    #--------------------------Low Mass 1--------------------------#

    configdict["frac_g1_1"]  = 0.89361
    configdict["frac_g1_2"]  = 0.092997
                
    configdict["tacc_slope_lm1"]   = 1.1
    configdict["tacc_offset_lm1"]  = 0.186
    configdict["tacc_beta_lm1"]    = 0.039

    #--------------------------Low Mass 1--------------------------#

    configdict["frac_g2_1"]  = 0.775701
    configdict["frac_g2_2"]  = 0.149533
    
    configdict["tacc_slope_lm2"]   = 1.1
    configdict["tacc_offset_lm2"]  = 0.186
    configdict["tacc_beta_lm2"]    = 0.039
    
    
    return configdict
