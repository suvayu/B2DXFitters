def getconfig() :

    configdict = {}
    
    from math import pi

    # FILENAMES
    configdict["fileName"]           = "/afs/cern.ch/work/g/gligorov/public/Bs2DsKPlotsForPaper/NominalFit/work_dsk_pid_53005800_PIDK5_5M_BDTGA.root"
    configdict["fileNameData"]       = "/afs/cern.ch/work/g/gligorov/public/Bs2DsKPlotsForPaper/NominalFit/work_dsk_pid_53005800_PIDK5_5M_BDTGA.root"
    configdict["fileNameTerr"]       = "../data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root"
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

    configdict["GammaLb"]       =  0.676    # in ps^{-1}

    #order: OS, SSK, OS+SSK, untagged
    configdict["D_Combo"]            =  [-0.908, -0.775, -0.913, -0.938]
    configdict["DeltaGammaCombo"]    =  [ 0.845,  1.266,  1.282,  0.753]
    configdict["GammaCombo"]         =  [ 0.913,  1.451,  1.371,  0.745]
    configdict["tagEff_Combo_full"]  =  [ [1.0, 0.0, 0.0], 
                                          [0.0, 1.0, 0.0], 
                                          [0.0, 0.0, 1.0], 
                                          [0.0, 0.0, 0.0] ]

    configdict["StrongPhase_d"] = 20. / 180. * pi
    configdict["StrongPhase_s"] = 4. / 180. * pi
    configdict["WeakPhase"]     = 116. / 180. * pi

    configdict["ArgLf_d"]       = configdict["StrongPhase_d"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_d"] = configdict["StrongPhase_d"] + configdict["WeakPhase"]
    configdict["ModLf_d"]       = 0.015
    
    configdict["ArgLf_s"]       = configdict["StrongPhase_s"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_s"] = configdict["StrongPhase_s"] + configdict["WeakPhase"]
    configdict["ModLf_s"]       = 0.51 #0.372

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
    configdict["timeRange"]     = [0.4, 15] # in ps

    configdict["tacc_size"]   = 6
    configdict["tacc_knots"]  = [0.5, 1.0, 1.5, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [0.4453873694523979, 0.6869245867352556, 0.8719680916278891, 1.1614426699209424, 1.2341250036543179, 1.2852701638596233]

    configdict["tagEff_OS"] = 0.387
    configdict["tagEff_SS"] = 0.4772
    
    configdict["tagEff_OS_Bd"] = 0.844757
    configdict["tagEff_SS_Bd"] = 1.0 

    configdict["tagEff_Bd"] = [configdict["tagEff_OS_Bd"] - configdict["tagEff_OS_Bd"]*configdict["tagEff_SS_Bd"],
                               configdict["tagEff_SS_Bd"] - configdict["tagEff_OS_Bd"]*configdict["tagEff_SS_Bd"],
                               configdict["tagEff_OS_Bd"]*configdict["tagEff_SS_Bd"]]

    configdict["tagEff_OS_Lb"] = 0.0
    configdict["tagEff_SS_Lb"] = 1.0

    configdict["tagEff_Lb"] = [configdict["tagEff_OS_Lb"] - configdict["tagEff_OS_Lb"]*configdict["tagEff_SS_Lb"],
                               configdict["tagEff_SS_Lb"] - configdict["tagEff_OS_Lb"]*configdict["tagEff_SS_Lb"],
                               configdict["tagEff_OS_Lb"]*configdict["tagEff_SS_Lb"]]
    
    configdict["tagEff_OS_Combo"] = 0.594
    configdict["tagEff_SS_Combo"] = 0.462

    configdict["tagEff_Signal"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Bd2DK"]     = configdict["tagEff_Signal"]
    configdict["tagEff_Bd2DPi"]       = configdict["tagEff_Signal"]
    configdict["tagEff_Bd2DsK"]       = configdict["tagEff_Signal"]
    configdict["tagEff_Bs2DsPi"]   = configdict["tagEff_Signal"]   
    configdict["tagEff_Lb2LcK"]       = configdict["tagEff_Signal"]
    configdict["tagEff_Lb2LcPi"]      = configdict["tagEff_Signal"]
    configdict["tagEff_Combo"]     = [configdict["tagEff_OS_Combo"] - configdict["tagEff_OS_Combo"]*configdict["tagEff_SS_Combo"],
                                      configdict["tagEff_SS_Combo"] - configdict["tagEff_OS_Combo"]*configdict["tagEff_SS_Combo"],
                                      configdict["tagEff_OS_Combo"]*configdict["tagEff_SS_Combo"]]
    configdict["tagEff_Lb2Dsp"]       = configdict["tagEff_Signal"]
    configdict["tagEff_Lb2Dsstp"]     = configdict["tagEff_Signal"]    
    configdict["tagEff_LM1"]       = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Bs2DsstPi"]    = configdict["tagEff_Signal"]
    configdict["tagEff_Bs2DsRho"]     = configdict["tagEff_Signal"]

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
    
    configdict["num_Signal"]    = [309, 576, 475, 107,  301]
    configdict["num_Bd2DK"]        = [17,    0,   5,   0,    0]
    configdict["num_Bd2DPi"]       = [14,    3,   3,   0,    0]
    configdict["num_Bd2DsK"]    = [18,   34,  39,  9,   27]
    configdict["num_Bs2DsPi"]      = [225*0.986*0.648, 498*0.986*0.648, 327*0.986*0.648, 89*0.986*0.648, 258*0.986*0.648]
    configdict["num_Lb2LcK"]       = [15,    2,   4,   0,    0]
    configdict["num_Lb2LcPi"]      = [11,    1,   3,   0,    0]
    configdict["num_Combo"]     = [487, 311, 258, 428, 946]
    configdict["num_Lb2Dsp"]       = [225*0.014*0.75, 498*0.014*0.75, 327*0.014*0.75, 89*0.014*0.75, 258*0.014*0.75]
    configdict["num_Lb2Dsstp"]     = [225*0.014*0.25, 498*0.014*0.25, 327*0.014*0.25, 89*0.014*0.25, 258*0.014*0.25]
    configdict["num_LM1"]       = [0,     0,   0,   0,    0]
    configdict["num_Bs2DsstPi"]    = [225*0.986*0.352*0.5, 498*0.986*0.352*0.5, 327*0.986*0.352*0.5, 89*0.986*0.352*0.5, 258*0.986*0.352*0.5]
    configdict["num_Bs2DsRho"]     = [225*0.986*0.352*0.5, 498*0.986*0.352*0.5, 327*0.986*0.352*0.5, 89*0.986*0.352*0.5, 258*0.986*0.352*0.5]

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

           
    configdict["cB"] = [-3.17e-03, -1.82e-03, -2.91e-03, -1.09e-03, -1.55e-03]
    configdict["cD"] = [-4.29e-03, -2.92e-03, -3.39e-03, -0.0,      -1.97e-03]
    configdict["fracDsComb"] = [0.95, 0.54, 0.80,  1.0, 1.0]

    configdict["fracPIDKComb1"] = 0.504
    configdict["fracPIDKComb2"] = 0.346
       
    return configdict
