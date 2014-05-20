def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
        
    # PHYSICAL PARAMETERS
    configdict["BMass"]      = [5300,    5800    ]
    configdict["DMass"]      = [1930,    2015    ]
    configdict["Time"]       = [0.5,     15.0    ]
    configdict["Momentum"]   = [3000.0,  650000.0]
    configdict["TrMom"]      = [400.0,   45000.0 ]
    configdict["PIDK"]       = [1.61,    5.0     ]
    configdict["nTracks"]    = [15.0,    1000.0  ]

    configdict["TagDec"]     = ["lab0_TAGDECISION_OS","lab0_SS_nnetKaon_DEC"]
    configdict["lab0_TAGDECISION_OS"]  = [-1.0, 1.0]
    configdict["lab0_SS_nnetKaon_DEC"] = [-1.0, 1.0]
    
    configdict["TagOmega"]   = ["lab0_TAGOMEGA_OS","lab0_SS_nnetKaon_PROB"]
    configdict["lab0_TAGOMEGA_OS"]  = [0.0, 0.5]
    configdict["lab0_SS_nnetKaon_PROB"] = [0.0, 0.5]

    configdict["calibration_p0"]  = [0.3834, 0.4244]
    configdict["calibration_p1"]  = [0.9720, 1.2180]
    configdict["calibration_av"]  = [0.3813, 0.4097]
       
    configdict["Terr"]       = [0.01,    0.1     ]
    configdict["BachCharge"] = [-1000.0, 1000.0  ]
    configdict["BDTG"]       = [0.3,     1.0     ]

    configdict["AdditionalVariables"] = [ "lab0_SS_Kaon_PROB", "lab0_SS_Kaon_DEC", 
                                          "lab0_OS_Muon_PROB" , "lab0_OS_Muon_DEC",
                                          "lab0_OS_Electron_PROB", "lab0_OS_Electron_DEC",
                                          "lab0_OS_Kaon_PROB",  "lab0_OS_Kaon_DEC",
                                          "lab0_OS_nnetKaon_PROB", "lab0_OS_nnetKaon_DEC",
                                          "lab0_VtxCharge_PROB", "lab0_VtxCharge_DEC" ]

    configdict["AdditionalDataCuts"] = "lab2_TAU>0"
    configdict["AdditionalMCCuts"] = "lab2_TAU>0"

    configdict["lab0_SS_Kaon_PROB"]      = [ -3.0, 1,0 ]
    configdict["lab0_SS_Kaon_DEC"]       = [ -2.0, 2.0 ]
    configdict["lab0_OS_Muon_PROB"]      = [ -3.0, 1.0 ]
    configdict["lab0_OS_Muon_DEC"]       = [ -2.0, 2.0 ]
    configdict["lab0_OS_Electron_PROB"]  = [-3.0, 1.0 ]
    configdict["lab0_OS_Electron_DEC"]   = [ -2.0, 2.0 ]
    configdict["lab0_OS_Kaon_PROB"]      = [ -3.0, 1.0 ]
    configdict["lab0_OS_Kaon_DEC"]       = [ -2.0, 2.0 ]
    configdict["lab0_OS_nnetKaon_PROB"]  = [ -3.0, 1.0 ]
    configdict["lab0_OS_nnetKaon_DEC"]   = [ -2.0, 2.0 ]
    configdict["lab0_VtxCharge_PROB"]    = [-3.0, 1.0 ]
    configdict["lab0_VtxCharge_DEC"]     = [-2.0, 2.0 ]
    
    configdict["Bin1"]      = 20
    configdict["Bin2"]      = 20
    configdict["Bin3"]      = 10
    configdict["Var1"]      = "lab1_PT"
    configdict["Var2"]      = "nTracks"
    configdict["Var3"]      = "lab1_P"
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
    configdict["pathFileLcPi"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/sWeights_LbLcPi_both_PID10.root"
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
    configdict["frac_bc"]    = [6.1755e-01,  7.0166e-01,  5.8012e-01,  7.8103e-01,  7.0398e-01]

    configdict["sigma1_old"]  = [18.082,  10.627,  11.417,  18.901,  19.658 ]
    configdict["sigma2_old"]  = [10.727,  15.289,  16.858,  11.058,  11.512 ]
    configdict["alpha1_old"]  = [2.0550,  1.6086,  2.0304,  2.0490,  1.8844 ]
    configdict["alpha2_old"]  = [-2.9184, -1.9642, -1.9823, -3.3876, -3.0227]
    configdict["n1_old"]      = [1.1123,  1.5879,  1.3059,  1.0988,  1.3397 ]
    configdict["n2_old"]      = [1.3312,  5.1315,  4.2083,  0.96197,  1.2083 ]
    configdict["frac_old"]    = [0.42743, 0.43480, 0.61540, 0.38142, 0.37901]

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
    
    configdict["sigma1Ds_old"]  = [7.6526,  8.7205,  5.3844,  11.590,  11.217 ]
    configdict["sigma2Ds_old"]  = [4.2202,  4.5795,  11.981,  6.0350,  6.8617 ]
    configdict["alpha1Ds_old"]  = [1.9266,  1.9260,  4.8339,  1.5839,  1.0902 ]
    configdict["alpha2Ds_old"]  = [-2.5456, -3.2773, -3.0116, -6.2018, -2.4987]
    configdict["n1Ds_old"]      = [2.8434,  1.4224,  48.516,  1.8532,  69.861 ]
    configdict["n2Ds_old"]      = [1.5942,  0.36197, 0.25888, 65.824,  1.0790 ]
    configdict["fracDs_old"]    = [0.50702, 0.36627, 0.84549, 0.29362, 0.46289]

    configdict["sigma1Dsfrac"] = 1.16 
    configdict["sigma2Dsfrac"] = 1.19 
    configdict["alpha1Dsfrac"] = 1.0 
    configdict["alpha2Dsfrac"] = 1.0 
        
    configdict["cB"]        = [-1.1530e-03,  -9.2354e-04,  -1.3675e-03, -9.8158e-04, -1.0890e-03]
    configdict["cD"]        = [-4.4329e-03,  -8.8642e-03,  -5.2652e-03, -1.0743e-03, -1.1877e-03]
    configdict["fracComb"]  = [0.78490,      0.34206,      0.63593,     1.0,         1.0]
    configdict["cB2"]                = [0.0,          0.0,          0.0,         0.0,          0.0       ]
    configdict["fracBsComb"]         = [4.3067e-01,   6.5400e-01,   3.7409e-01,  1.7420e-01,  2.2100e-01]

        
    configdict["nBs2DsDsstPiRhoEvts"]  = [180.0, 208.0, 191.0, 37.0, 98.0]
    configdict["nBs2DsPiEvts"]         = [180.0, 208.0, 191.0, 37.0, 98.0]
    configdict["nLbDspEvts"]           = [125.0, 125.0, 125.0, 20.0, 40.0]
    configdict["nLbLcKEvts"]           = [15.0, 2.0,  4.0,  0.0,  0.0]
    configdict["nLbLcPiEvts"]          = [11.0, 1.0,  3.0,  0.0,  0.0]
    configdict["nBdDKEvts"]            = [17.0, 0.0,  5.0,  0.0,  0.0]
    configdict["nBdDPiEvts"]           = [14.0, 0.0,  3.0,  3.0,  0.0]
    
    configdict["g2_f1"] = 0.42761287
    configdict["g2_f2"] = 0.47275694
    configdict["g2_f3"] = 0.05205979

    return configdict
