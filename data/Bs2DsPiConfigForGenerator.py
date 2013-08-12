def getconfig() :

    configdict = {}
    
    from math import pi

    configdict["lumRatio"] =  0.44/(0.59+0.44)

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.105

    configdict["Gammad"]      =  0.658   # in ps^{-1}
    configdict["DeltaGammad"] =  0.

    configdict["DeltaMs"]     =  17.768     # in ps^{-1}
    configdict["DeltaMd"]     =  0.507      # in ps^{-1}

    configdict["GammaLb"]    =  0.702    # in ps^{-1}
    configdict["GammaCombo"] =  0.800

    configdict["StrongPhase_d"] = 20. / 180. * pi
    configdict["StrongPhase_s"] = 30. / 180. * pi
    configdict["WeakPhase"]     = 70. / 180. * pi #70. / 180. * pi

    configdict["ArgLf_d"]       = configdict["StrongPhase_d"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_d"] = configdict["StrongPhase_d"] + configdict["WeakPhase"]
    configdict["ModLf_d"]       = 0.015
    
    configdict["ArgLf_s"]       = configdict["StrongPhase_s"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_s"] = configdict["StrongPhase_s"] + configdict["WeakPhase"]
    configdict["ModLf_s"]       = 0.372

    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    configdict["TagOmegaSig"]   = 0.391

    configdict["resolutionScaleFactor"] = 1.37
    configdict["resolutionMeanBias"]    = 0.0

    configdict["nBinsMistag"]   = 50
    configdict["nBinsProperTimeErr"]   = 50
    configdict["nBinsAcceptance"]   = 740
            

    configdict["tagEff_signal"]    = 0.403
    configdict["tagEff_dpi"]       = 0.403
    configdict["tagEff_dspi"]      = 0.403
    configdict["tagEff_lcpi"]      = 0.403
    configdict["tagEff_combo"]     = 0.403
    configdict["tagEff_lm1"]       = 0.403
    configdict["tagEff_lm2"]       = 0.403
    configdict["tagEff_dsk"]       = 0.403

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
    
    configdict["num_signal"]    = 29266.
    configdict["num_dpi"]       = 444.
    configdict["num_dspi"]      = 88.
    configdict["num_lcpi"]      = 400.
    configdict["num_combo"]     = 12905 #13500. #0.
    configdict["num_lm1"]       = 200. #00.
    #configdict["num_lm2"]       = 1070.
    configdict["num_dsk"]       = 163.
        
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
                                            
    configdict["tacc_exponent"] = 1.83165e+00
    configdict["tacc_offset"]   = 1.94941e-02
    configdict["tacc_beta"]     = 3.55134e-02
    configdict["tacc_turnon"]   = 1.31231e+00
    
    #---------------------------Combo----------------------------#
      
    configdict["cB1"] = -9.9005e-03 
    configdict["cB2"] = 0.0
    configdict["fracBsComb"] = 6.6631e-01

    configdict["cD"] = -3.4761e-03
    configdict["fracDsComb"] = 0.59760

    configdict["fracPIDKComb"] = 9.0101e-01
                
    #--------------------------Low Mass 1--------------------------#

    #configdict["frac_g1_1"]  = 0.89361
    #configdict["frac_g1_2"]  = 0.092997
                
    #--------------------------Low Mass 1--------------------------#

    #configdict["frac_g2_1"]  = 0.693333
    #configdict["frac_g2_2"]  = 0.149533
       
    return configdict
