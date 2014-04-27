def getconfig() :

    configdict = {}
    
    from math import pi

    # FILENAMES
    configdict["fileName"]           = "/afs/cern.ch/work/a/adudziak/public/workspace/DsKNoteV11/work_dsk_pid_53005800_PIDK5_5M_BDTGA_4.root"
    configdict["fileNameData"]       = "/afs/cern.ch/work/a/adudziak/public/workspace/DsKNoteV11/work_dsk_pid_53005800_PIDK5_5M_BDTGA_4.root"
    configdict["fileNameTerr"]       = "../data/workspace/MDFitter/template_Data_Terr_BsDsK.root"
    configdict["fileNameMistag"]     = "../data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root"
    configdict["fileNameMistagBDPi"] = "../data/workspace/MDFitter/template_Data_Mistag_BDPi.root"
    configdict["fileNameMistagComb"] = "../data/workspace/MDFitter/template_Data_Mistag_CombBkg.root"
    configdict["fileNameKFactHists"] = "../data/workspace/MDFitter/kFactorsInMassBins/histograms_MC_KFactor_BsDsK.root"

    # EVENTUALLY MUCH OF THE REST OF THIS CONFIG SHOULD BE REWRITTEN
    # INTO THIS DICTIONARY. FOR NOW PUT THE MC TRUTH AND WHO NEEDS
    # A K-FACTOR HERE.
    configdict["DecayModeParameters"] = {}
    configdict["DecayModeParameters"]["Signal"]     = { "TRUEID" : "1"    , "KFACTOR" : False }
    configdict["DecayModeParameters"]["Bd2DK"]      = { "TRUEID" : "2"    , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["Bd2DPi"]     = { "TRUEID" : "12"   , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["Bd2DsK"]     = { "TRUEID" : "3"    , "KFACTOR" : False }
    configdict["DecayModeParameters"]["Bs2DsPi"]    = { "TRUEID" : "4"    , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["Bs2DsstPi"]  = { "TRUEID" : "8"    , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["Bs2DsRho"]   = { "TRUEID" : "18"   , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["Lb2LcK"]     = { "TRUEID" : "5"    , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["Lb2LcPi"]    = { "TRUEID" : "15"   , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["Lb2Dsp"]     = { "TRUEID" : "6"    , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["Lb2Dsstp"]   = { "TRUEID" : "16"   , "KFACTOR" : True  }
    configdict["DecayModeParameters"]["LM1"]        = { "TRUEID" : "7"    , "KFACTOR" : False }
    configdict["DecayModeParameters"]["Combo"]      = { "TRUEID" : "10"   , "KFACTOR" : False }
 
    # PHYSICAL PARAMETERS
    configdict["kFactorBinning"]= 50    # in MeV

    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   = -0.105

    configdict["Gammad"]        =  0.656   # in ps^{-1}
    configdict["DeltaGammad"]   =  0.

    configdict["DeltaMs"]       =  17.768    # in ps^{-1}
    configdict["DeltaMd"]       =  0.507   # in ps^{-1}

    configdict["GammaLb"]       =  0.700    # in ps^{-1}
    configdict["GammaCombo"]    =  0.800
       
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
    
    configdict["lumRatioDown"]  =  0.59
    configdict["lumRatioUp"]    =  0.44
    configdict["lumRatio"]      =  configdict["lumRatioUp"]/(configdict["lumRatioDown"]+configdict["lumRatioUp"])
    
    configdict["massRange"]     = [5300,5800] # in MeV 
    configdict["timeRange"]     = [0.2, 15] # in ps

    configdict["tacc_size"]   = 6
    configdict["tacc_knots"]  = [0.25, 0.5, 1.0, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [1.77520e-01, 2.89603e-01, 6.79455e-01, 1.11726e+00, 1.23189e+00, 1.26661e+00] 

    configdict["tagEff_OS"] = 0.387
    configdict["tagEff_SS"] = 0.4772

    configdict["tagEff_Signal"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Bd2DK"]        = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Bd2DPi"]        = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Bd2DsK"]       = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Bs2DsPi"]      = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Lb2LcK"]       = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Lb2LcPi"]       = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Combo"]     = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Lb2Dsp"]       = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Lb2Dsstp"]     = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    
    configdict["tagEff_LM1"]       = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Bs2DsstPi"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Bs2DsRho"]     = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    

    configdict["aprod_Signal"]    = 0.0 #0.03
    configdict["aprod_Bd2DK"]        = 0.0 #0.03
    configdict["aprod_Bd2DPi"]       = 0.0 #0.03 
    configdict["aprod_Bd2DsK"]    = 0.0 #3
    configdict["aprod_Bs2DsPi"]      = 0.0 # 3
    configdict["aprod_Lb2LcK"]       = 0.0 # 3
    configdict["aprod_Lb2LcPi"]      = 0.0 # 3
    configdict["aprod_Combo"]     = 0.0 #3
    configdict["aprod_Lb2Dsp"]       = 0.0 #3
    configdict["aprod_Lb2Dsstp"]     = 0.0 #3
    configdict["aprod_LM1"]       = 0.0 #3
    configdict["aprod_Bs2DsstPi"]    = 0.0 #3
    configdict["aprod_Bs2DsRho"]     = 0.0 #3
                                    
    configdict["atageff_Signal"]    = [0.0, 0.0, 0.0]
    configdict["atageff_Bd2DK"]        = [0.0, 0.0, 0.0]
    configdict["atageff_Bd2DPi"]       = [0.0, 0.0, 0.0]
    configdict["atageff_Bd2DsK"]    = [0.0, 0.0, 0.0]
    configdict["atageff_Bs2DsPi"]      = [0.0, 0.0, 0.0]
    configdict["atageff_Lb2LcK"]       = [0.0, 0.0, 0.0]
    configdict["atageff_Lb2LcPi"]      = [0.0, 0.0, 0.0]
    configdict["atageff_Combo"]     = [0.0, 0.0, 0.0]
    configdict["atageff_Lb2Dsp"]       = [0.0, 0.0, 0.0]
    configdict["atageff_Lb2Dsstp"]     = [0.0, 0.0, 0.0]
    configdict["atageff_LM1"]       = [0.0, 0.0, 0.0]
    configdict["atageff_Bs2DsstPi"]    = [0.0, 0.0, 0.0]
    configdict["atageff_Bs2DsRho"]     = [0.0, 0.0, 0.0]

    configdict["adet_Signal"]    = 0.0
    configdict["adet_Bd2DK"]        = 0.0
    configdict["adet_Bd2DPi"]       = 0.0
    configdict["adet_Bd2DsK"]    = 0.0
    configdict["adet_Bs2DsPi"]      = 0.0
    configdict["adet_Lb2LcK"]       = 0.0
    configdict["adet_Lb2LcPi"]      = 0.0
    configdict["adet_Combo"]     = 0.0
    configdict["adet_Lb2Dsp"]       = 0.0
    configdict["adet_Lb2Dsstp"]     = 0.0
    configdict["adet_LM1"]       = 0.0
    configdict["adet_Bs2DsstPi"]    = 0.0
    configdict["adet_Bs2DsRho"]     = 0.0
    
    configdict["num_Signal"]    = [308, 591, 487, 109,  314]
    configdict["num_Bd2DK"]        = [17,    0,   5,   0,    0]
    configdict["num_Bd2DPi"]       = [14,    3,   3,   0,    0]
    configdict["num_Bd2DsK"]    = [18,   35,  42,  11,   32]
    configdict["num_Bs2DsPi"]      = [231*0.979*0.653, 514*0.979*0.653, 342*0.979*0.653, 90*0.979*0.653, 258*0.979*0.653]
    configdict["num_Lb2LcK"]       = [15,    2,   4,   0,    0]
    configdict["num_Lb2LcPi"]      = [11,    1,   3,   0,    0]
    configdict["num_Combo"]     = [664, 439, 327, 619, 1702]
    configdict["num_Lb2Dsp"]       = [231*0.021*0.75, 514*0.021*0.75, 342*0.021*0.75, 90*0.021*0.75, 258*0.021*0.75]
    configdict["num_Lb2Dsstp"]     = [231*0.021*0.25, 514*0.021*0.25, 342*0.021*0.25, 90*0.021*0.25, 258*0.021*0.25]
    configdict["num_LM1"]       = [0,     0,   0,   0,    0]
    configdict["num_Bs2DsstPi"]    = [231*0.979*0.347*0.5, 514*0.979*0.347*0.5, 342*0.979*0.347*0.5, 90*0.979*0.347*0.5, 258*0.979*0.347*0.5]
    configdict["num_Bs2DsRho"]     = [231*0.979*0.347*0.5, 514*0.979*0.347*0.5, 342*0.979*0.347*0.5, 90*0.979*0.347*0.5, 258*0.979*0.347*0.5]

    #----------------------------Signal----------------------------#

    configdict["mean"]    = [5367.51, 5367.51, 5367.51, 5367.51, 5367.51]

    configdict["sigma1"]  = [1.0717e+01*1.28,  1.1235e+01*1.28,  1.0772e+01*1.28,  1.1268e+01*1.28,  1.1391e+01*1.28 ]
    configdict["sigma2"]  = [1.6005e+01*1.22,  1.7031e+01*1.22,  1.5339e+01*1.22,  1.9408e+01*1.22,  1.7647e+01*1.22 ]
    configdict["alpha1"]  = [2.2118e+00,       2.2144e+00,       2.0480e+00,       2.3954e+00,       2.0930e+00 ]
    configdict["alpha2"]  = [-2.4185e+00,      -2.1918e+00,      -2.0291e+00,      -3.4196e+00,      -2.3295e+00]
    configdict["n1"]      = [1.0019e+00,       1.1193e+00,       1.2137e+00,       9.8202e-01,       1.2674e+00 ]
    configdict["n2"]      = [3.1469e+00,       3.6097e+00,       6.5735e+00,       5.2237e-01,       4.0195e+00 ]
    configdict["frac"]    = [6.1755e-01,       7.0166e-01,       5.8012e-01,       7.8103e-01,       7.0398e-01]


    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]

    configdict["sigma1Ds"]  = [5.3468e+00*1.16,  8.2412e+00*1.16,  6.0845e+00*1.16,  8.8531e+00*1.16,  8.0860e+00*1.16 ]
    configdict["sigma2Ds"]  = [5.1848e+00*1.19,  4.4944e+00*1.19,  5.1266e+00*1.19,  5.2073e+00*1.19,  7.3773e+00*1.19 ]
    configdict["alpha1Ds"]  = [1.2252e+00,       1.9827e+00,       1.1316e+00,       1.7131e+00,       9.0639e-01 ]
    configdict["alpha2Ds"]  = [-1.1167e+00,      -3.0525e+00,      -1.3760e+00,      -2.5276e+00,      -1.1122e+00]
    configdict["n1Ds"]      = [4.6625e+00,       1.4867e+00,       1.3280e+01,       2.0239e+00,       1.1486e+01 ]
    configdict["n2Ds"]      = [6.9989e+01,       6.1022e-01,       1.1017e+01,       1.0860e+00,       4.0001e+01 ]
    configdict["fracDs"]    = [4.7565e-01,       3.9628e-01 ,      4.0048e-01,       5.5084e-01,       4.8729e-01 ]

           
    configdict["cB"] = [-3.2717e-03, -2.0784e-03, -3.0429e-03, -1.5052e-03, -2.2054e-03]
    configdict["cD"] = [-2.7157e-03, -2.4707e-03, -5.1842e-03, -3.3044e-04, -3.7356e-03]
    configdict["fracDsComb"] = [9.4614e-01, 5.3355e-01, 7.7153e-01,  1.0, 1.0]

    configdict["fracPIDKComb1"] = 6.2485e-01
    configdict["fracPIDKComb2"] = 5.4107e-01
       
    return configdict
