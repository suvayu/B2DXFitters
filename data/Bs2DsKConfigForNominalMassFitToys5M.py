def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # PHYSICAL PARAMETERS
    configdict["BMass"]      = [5300,    5800    ]
    configdict["DMass"]      = [1930,    2015    ]
    configdict["Time"]       = [0.2,     15.0    ]
    configdict["Momentum"]   = [3000.0,  650000.0]
    configdict["TrMom"]      = [400.0,   45000.0 ]
    configdict["PIDK"]       = [0.0,     150.0   ]
    configdict["nTracks"]    = [15.0,    1000.0  ]

    configdict["TagDec"]     = ["lab0_TAGDECISION_OS","lab0_SS_nnetKaon_DEC"]
    configdict["lab0_TAGDECISION_OS"]  = [-1.0, 1.0]
    configdict["lab0_SS_nnetKaon_DEC"] = [-1.0, 1.0]
    
    configdict["TagOmega"]   = ["lab0_TAGOMEGA_OS","lab0_SS_nnetKaon_PROB"]
    configdict["lab0_TAGOMEGA_OS"]  = [0.0, 0.5]
    configdict["lab0_SS_nnetKaon_PROB"] = [0.0, 0.5]
    
    configdict["calibration_p0"]  = [0.3927, 0.4244]
    configdict["calibration_p1"]  = [0.9818, 1.2550]
    configdict["calibration_av"]  = [0.3919, 0.4097]
        
    configdict["Terr"]       = [0.01,    0.1     ]
    configdict["BachCharge"] = [-1000.0, 1000.0  ]
    configdict["BDTG"]       = [0.3,     1.0     ]
                                            
                               
    configdict["Bin1"]      = 20
    configdict["Bin2"]      = 20
    configdict["Var1"]      = "lab1_PT"
    configdict["Var2"]      = "nTracks"
    configdict["WeightingDimensions"] = 2                                 
    
    
    configdict["PIDBach"]    = 5
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsK.txt"

    configdict["fileCalibPionUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpPi_DsK.root"
    configdict["fileCalibPionDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownPi_DsK.root"
    configdict["workCalibPion"]  = "RSDStCalib"
    configdict["fileCalibKaonUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpK_DsK.root"
    configdict["fileCalibKaonDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownK_DsK.root"
    configdict["workCalibKaon"]  = "RSDStCalib"
    configdict["fileCalibProtonUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/work_lblcpi_up_sw.root"
    configdict["fileCalibProtonDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/work_lblcpi_down_sw.root"
    configdict["workCalibProton"]  = "workspace"
    configdict["pathFileLcPi"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/sWeights_LbLcPi_both_PIDK10.root"
    configdict["treeNameLcPi"] = "merged"
                                           
    configdict["lumRatioDown"] =  0.59
    configdict["lumRatioUp"] =  0.44
    configdict["lumRatio"] =  configdict["lumRatioUp"]/(configdict["lumRatioDown"]+configdict["lumRatioUp"])
    
    # 1: NonRes, 2: PhiPi, 3: KstK, 4: KPiPi, 5: PiPiPi
    configdict["mean"]    = [5367.51, 5367.51, 5367.51, 5367.51, 5367.51]

    configdict["sigma1_bc"]  = [1.0717e+01,  1.1235e+01,  1.0772e+01,  1.1268e+01,  1.1391e+01 ]
    configdict["sigma2_bc"]  = [1.6005e+01,  1.7031e+01,  1.5339e+01,  1.9408e+01,  1.7647e+01 ]
    configdict["alpha1_bc"]  = [2.2118e+00,  2.2144e+00,  2.0480e+00,  2.3954e+00,  2.0930e+00 ]
    configdict["alpha2_bc"]  = [-2.4185e+00, -2.1918e+00, -2.0291e+00, -3.4196e+00, -2.3295e+00]
    configdict["n1_bc"]      = [1.0019e+00,  1.1193e+00,  1.2137e+00,  9.8202e-01,  1.2674e+00 ]
    configdict["n2_bc"]      = [3.1469e+00,  3.6097e+00,  6.5735e+00,  5.2237e-01,  4.0195e+00 ]
    configdict["frac_bc"]    = [6.1755e-01,  7.0166e-01,  5.8012e-01,  7.8103e-01,  7.0398e-01 ]

    configdict["sigma1Bsfrac"] = 1.22 
    configdict["sigma2Bsfrac"] = 1.28
    configdict["alpha1Bsfrac"] = 1.0 
    configdict["alpha2Bsfrac"] = 1.0 
    
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    
    configdict["sigma1Ds_bc"]  = [5.3468e+00,  8.2412e+00,  6.0845e+00,  8.8531e+00,  8.0860e+00 ]
    configdict["sigma2Ds_bc"]  = [5.1848e+00,  4.4944e+00,  5.1266e+00,  5.2073e+00,  7.3773e+00 ]
    configdict["alpha1Ds_bc"]  = [1.2252e+00,  1.9827e+00,  1.1316e+00,  1.7131e+00,  9.0639e-01 ]
    configdict["alpha2Ds_bc"]  = [-1.1167e+00, -3.0525e+00, -1.3760e+00, -2.5276e+00, -1.1122e+00]
    configdict["n1Ds_bc"]      = [4.6625e+00,  1.4867e+00,  1.3280e+01,  2.0239e+00,  1.1486e+01 ]
    configdict["n2Ds_bc"]      = [6.9989e+01,  6.1022e-01,  1.1017e+01,  1.0860e+00,  4.0001e+01 ]
    configdict["fracDs_bc"]    = [4.7565e-01,  3.9628e-01 , 4.0048e-01,  5.5084e-01,  4.8729e-01 ]


    configdict["sigma1Dsfrac"] = 1.16 
    configdict["sigma2Dsfrac"] = 1.19 
    configdict["alpha1Dsfrac"] = 1.0 
    configdict["alpha2Dsfrac"] = 1.0 
        
    configdict["cB"] = [-3.2717e-03, -2.0784e-03, -3.0429e-03, -1.5052e-03, -2.2054e-03]
    configdict["cD"] = [-2.7157e-03, -2.4707e-03, -5.1842e-03, -3.3044e-04, -3.7356e-03]
    configdict["fracComb"] = [9.4614e-01, 5.3355e-01, 7.7153e-01,  1.0, 1.0]
            
        
    configdict["nBs2DsDsstPiRhoEvts"]  = [232.0/2.0, 232.0/2.0,
                                          502.0/2.0, 502.0/2.0,
                                          331.0/2.0, 331.0/2.0,
                                          87.0/2.0,  87.0/2.0,
                                          239.0/2.0, 239.0/2.0]
    

    #[180.0/2.0, 180.0/2.0,
    #                                      208.0/2.0, 208.0/2.0,
    #                                      191.0/2.0, 191.0/2.0,
    #                                      37.0/2.0,  37.0/2.0,
    #                                      98.0/2.0,  98.0/2.0
    #                                      ]

    configdict["nBs2DsPiEvts"]  = [160.0/2.0, 160.0/2.0,
                                   306.0/2.0, 306.0/2.0,
                                   226.0/2.0, 226.0/2.0,
                                   51.0/2.0,  51.0/2.0,
                                   153.0/2.0, 153.0/2.0]


    #[180.0/2.0, 180.0/2.0,
    #                               208.0/2.0, 208.0/2.0,
    #                               191.0/2.0, 191.0/2.0,
    #                               37.0/2.0,  37.0/2.0,
    #                               98.0/2.0,  98.0/2.0
    #                               ]
    
    configdict["nLbDspEvts"]           = [17.0/2,0,  17.0/2.0,
                                          70.0/2.0,  70.0/2.0,
                                          2.0/2.0,   2.0/2.0,
                                          12.0/2.0,  12.0/2.0,
                                          19.0/2.0,  19.0/2.0]

    configdict["nLbLcKEvts"]           = [15.0/2.0, 15.0/2.0,
                                          2.0/2.0,  2.0/2.0,
                                          4.0/2.0,  4.0/2.0,
                                          0, 0,
                                          0, 0]
    
    configdict["nLbLcPiEvts"]           = [11.0/2.0, 11.0/2.0,
                                           1.0/2.0,  1.0/2.0,
                                           3.0/2.0,  3.0/2.0,
                                           0, 0,
                                           0, 0]

    configdict["nBdDKEvts"]            = [15.0/2.0, 15.0/2.0,
                                          0.0,  0.0,
                                          4.0/2.0,  4.0/2.0,
                                          0.0, 0.0,
                                          0.0, 0.0]

    configdict["nBdDPiEvts"]            = [14.0/2.0, 14.0/2.0,
                                           0.0/2.0,  0.0/2.0,
                                           3.0/2.0,  3.0/2.0,
                                           3.0/2.0,  3.0/2.0,
                                           0, 0]                
    
    configdict["g2_f1"] = 0.42761287
    configdict["g2_f2"] = 0.47275694
    configdict["g2_f3"] = 0.05205979

    return configdict
