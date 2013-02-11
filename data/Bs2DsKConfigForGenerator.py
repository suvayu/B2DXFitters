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

    configdict["tagEff_signal"]    = 0.40
    configdict["tagEff_dk"]        = 0.40
    configdict["tagEff_dsk"]       = 0.40
    configdict["tagEff_dspi"]      = 0.40
    configdict["tagEff_lck"]       = 0.40
    configdict["tagEff_combo"]     = 0.40
    configdict["tagEff_dsdsstp"]   = 0.40
    configdict["tagEff_lm1"]       = 0.40
    configdict["tagEff_lm2"]       = 0.40

    configdict["prodasy_signal"]    = 0.03
    configdict["prodasy_dk"]        = 0.03
    configdict["prodasy_dsk"]       = 0.03
    configdict["prodasy_dspi"]      = 0.03
    configdict["prodasy_lck"]       = 0.03
    configdict["prodasy_combo"]     = 0.03
    configdict["prodasy_dsdsstp"]   = 0.03
    configdict["prodasy_lm1"]       = 0.03
    configdict["prodasy_lm2"]       = 0.03
                                    
    configdict["tageffasy_signal"]    = 0.01
    configdict["tageffasy_dk"]        = 0.02
    configdict["tageffasy_dsk"]       = 0.01
    configdict["tageffasy_dspi"]      = 0.01
    configdict["tageffasy_lck"]       = 0.03
    configdict["tageffasy_combo"]     = 0.01
    configdict["tageffasy_dsdsstp"]   = 0.03
    configdict["tageffasy_lm1"]       = 0.01
    configdict["tageffasy_lm2"]       = 0.01
    
    configdict["num_signal"]    = 1250.
    configdict["num_dk"]        = 40.
    configdict["num_dsk"]       = 500.
    configdict["num_dspi"]      = 150.
    configdict["num_lck"]       = 40.
    configdict["num_combo"]     = 1500.
    configdict["num_dsdsstp"]   = 240.
    configdict["num_lm1"]       = 1700.
    configdict["num_lm2"]       = 250.
        
    #----------------------------Signal----------------------------#

    configdict["mean"]    = 5369
    configdict["sigma1"]  = 10.0880
    configdict["sigma2"]  = 15.708
    configdict["alpha1"]  = 1.8086
    configdict["alpha2"]  = -1.8169
    configdict["n1"]      = 1.3830
    configdict["n2"]      = 8.8559
    configdict["frac"]    = 0.47348
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515
                                        
    configdict["tacc_exponent_pl"] = 1.849
    configdict["tacc_offset_pl"]   = 0.0373
    configdict["tacc_beta_pl"]     = 0.0363
    configdict["tacc_turnon_pl"]   = 1.215
    
    configdict["exposlope_combo"]   = -0.001

    configdict["frac_dsdsstp"]   = 0.5
    
    configdict["frac_g1_1lmk"]  = 0.14536
    configdict["frac_g1_2lmk"]  = 0.169091
                
    configdict["frac_g2_1"]  = 0.31266
    configdict["frac_g2_2"]  = 0.202776
    
       
    return configdict
