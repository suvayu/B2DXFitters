def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # PHYSICAL PARAMETERS
    configdict["BMass"]      = [5100,    5800    ]
    configdict["DMass"]      = [1930,    2015    ]
    configdict["Time"]       = [0.2,     15.0    ]
    configdict["Momentum"]   = [3000.0,  650000.0]
    configdict["TrMom"]      = [400.0,   45000.0 ]
    configdict["PIDK"]       = [1.61,    5.0     ]
    configdict["nTracks"]    = [15.0,    1000.0  ]

    configdict["TagDec"]     = ["Bs_BsTaggingTool_TAGDECISION_OS","Bs_BsTaggingTool_SS_nnetKaon_DEC"]
    configdict["Bs_BsTaggingTool_TAGDECISION_OS"]  = [-1.0, 1.0]
    configdict["Bs_BsTaggingTool_SS_nnetKaon_DEC"] = [-1.0, 1.0]

    configdict["TagOmega"]   = ["Bs_BsTaggingTool_TAGOMEGA_OS","Bs_BsTaggingTool_SS_nnetKaon_PROB"]
    configdict["Bs_BsTaggingTool_TAGOMEGA_OS"]  = [0.0, 0.5]
    configdict["Bs_BsTaggingTool_SS_nnetKaon_PROB"] = [0.0, 0.5]

    configdict["calibration_p0"]  = [0.3927, 0.4244]
    configdict["calibration_p1"]  = [0.9818, 1.2550]
    configdict["calibration_av"]  = [0.3919, 0.4097]
                                               
    configdict["Terr"]       = [0.01,    0.1     ]
    configdict["BachCharge"] = [-1000.0, 1000.0  ]

    configdict["labX"] = 0
    configdict["AdditionalDataCuts"] = "Pi0_PT>1000&&Ds_FD_ORIVX>0&&Ds_FDCHI2_ORIVX>2&&Km_PIDK>5&&Kp_PIDK>5&&Pi_PIDK<0"
    configdict["AdditionalMCCuts"] = "Pi0_PT>1000&&Ds_FD_ORIVX>0&&Ds_FDCHI2_ORIVX>2"
            
    configdict["Bin1"]       = 20
    configdict["Bin2"]       = 20
    configdict["Bin3"]       = 10
    configdict["Var1"]       = "lab1_PT"
    configdict["Var2"]       = "nTracks"
    configdict["Var3"]       = "lab1_P"
    configdict["WeightingDimensions"] = 2
    
    configdict["PIDBach"]    = 5
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2DsK_for_Bs2DsKst.txt"
    
    configdict["fileCalibPionUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpPi_0.root"
    configdict["fileCalibPionDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownPi_0.root"
    configdict["fileCalibKaonUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpK_0.root"
    configdict["fileCalibKaonDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownK_0.root"
    configdict["workCalibPion"]  = "RSDStCalib"
    configdict["workCalibKaon"]  = "RSDStCalib"

    configdict["lumRatioDown"] =  0.5
    configdict["lumRatioUp"] =  0.5
    configdict["lumRatio"] =  configdict["lumRatioUp"]/(configdict["lumRatioDown"]+configdict["lumRatioUp"])
    
    # 1: NonRes, 2: PhiPi, 3: KstK, 4: KPiPi, 5: PiPiPi 
    configdict["mean"]    = [5367.51, 5367.51, 5367.51, 5367.51, 5367.51]

    # Bs signal shale without BKGCAT
    #configdict["sigma1"]  = [14.240,  18.107,  12.092,  11.88,   12.504 ] #*1.252
    #configdict["sigma2"]  = [9.0773,  11.925,  16.078,  18.539,  20.000 ] #*1.777
    #configdict["alpha1"]  = [1.8539,  1.6328,  1.7344,  1.9468,  1.8922 ] #*1.004 
    #configdict["alpha2"]  = [-1.3223, -2.3348, -1.9130, -2.1141, -2.1200] #*0.832
    #configdict["n1"]      = [1.2508,  1.4973,  1.2819,  1.0945,  1.2074 ] 
    #configdict["n2"]      = [1.7330,  1.8582,  4.0326,  2.8556,  2.6656 ]
    #configdict["frac"]    = [0.85102, 0.46495, 0.51567, 0.65731, 0.68870]

    #Bs signal shape with BKGCAT
    configdict["sigma1_bc"]  = [17.2698] 
    configdict["sigma2_bc"]  = [17.756] 
    configdict["alpha1_bc"]  = [1.] 
    configdict["alpha2_bc"]  = [-1.27596] 
    configdict["n1_bc"]      = [0.92]
    configdict["n2_bc"]      = [0.54]
    configdict["frac_bc"]    = [0.579]

    # ratio data/MC
    configdict["sigma1Bsfrac"] = 1.145 
    configdict["sigma2Bsfrac"] = 1.255
    configdict["alpha1Bsfrac"] = 1.0 
    configdict["alpha2Bsfrac"] = 1.0 

    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49 ]

    #Ds signal shapes without BKGCAT
    #configdict["sigma1Ds"]  = [4.8865,   5.0649,  5.4377,  5.8510,  5.5906 ] #*1.167
    #configdict["sigma2Ds"]  = [5.0645,   5.5344,  5.3877,  10.180,  10.073 ] #*1.096 
    #configdict["alpha1Ds"]  = [0.51973,  1.1934,  0.7734,  2.8195,  1.9343 ] #*1.140
    #configdict["alpha2Ds"]  = [-0.9908,  -1.1806, -1.1424, -2.2422,  -1.7027] #*1.022
    #configdict["n1Ds"]      = [50.000,   4.0702,  49.999,  0.0262,  0.2633 ]
    #configdict["n2Ds"]      = [50.000,   10.643,  50.000,  1.9293,  8.6233 ]
    #configdict["fracDs"]    = [0.25406,  0.48465, 0.32864, 0.59958, 0.27873]

    #Ds signal shapes with BKGCAT
    configdict["sigma1Ds_bc"]  = [27.81]
    configdict["sigma2Ds_bc"]  = [] 
    configdict["alpha1Ds_bc"]  = [] 
    configdict["alpha2Ds_bc"]  = []
    configdict["n1Ds_bc"]      = []
    configdict["n2Ds_bc"]      = []
    configdict["fracDs_bc"]    = []
    
    # ratio data/MC
    configdict["sigma1Dsfrac"] = 1.074
    configdict["sigma2Dsfrac"] = 1.185 
    configdict["alpha1Dsfrac"] = 1.0 
    configdict["alpha2Dsfrac"] = 1.0 
        

    # combinatorial background
    configdict["cB1"]                = [-3.5211e-03]
    configdict["cB2"]                = [0.0,      ]
    configdict["fracBsComb"]         = [4.3067e-01]
    
    configdict["cD"]        = [-2.7520e-03] 
    configdict["fracComb"]  = [1.0]          

    #expected Events
    configdict["BdDPiEvents"]  = [331.0, 4.0,  81.0, 28.0, 0.0]
    configdict["LbLcPiEvents"] = [301.0, 30.0, 68.0, 0.0,  0.0] #[312.0, 38.0, 69.0, 17.0,  0.0] #[301.0, 30.0, 68.0, 0.0,  0.0]
    configdict["BsDsKEvents"]  = [42.0,  48.0, 43.0, 8.0,  22.0]
        
    configdict["assumedSig"]   = [10146.7, 13952.8,
                                  10146.7, 13952.8,
                                  10146.7, 13952.8,
                                  752., 1195.,
                                  1730., 2384.] #[9180.,13005.,730.,1160.,1680.,2315.]
    configdict["nBd2DsPi"]     = 1./25. #1./30.
    configdict["nBd2DsstPi"]   = 1./25. #1./30.
    configdict["nBd2DstPi"]    = 1./4.
    configdict["nBd2DRho"]     = 1./3.5
    
    return configdict
