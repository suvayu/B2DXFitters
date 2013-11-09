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
    configdict["PIDK"]       = [1.61,    5.0     ]
    configdict["nTracks"]    = [15.0,    1000.0  ]
    configdict["TagDec"]     = [-1.0,    1.0     ]
    configdict["TagOmega"]   = [0.0,     0.5     ]
    configdict["Terr"]       = [0.01,    0.1     ]
    configdict["BachCharge"] = [-1000.0, 1000.0  ]
    configdict["BDTG"]       = [0.3,     0.7     ]
                                                
       
    configdict["Bin1"]      = 20
    configdict["Bin2"]      = 20
    configdict["Bin3"]      = 10
    configdict["Var1"]      = "lab1_PT"
    configdict["Var2"]      = "nTracks"
    configdict["Var3"]       = "lab1_P"
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
    configdict["mean"]    = [5367.51,   5367.51,   5367.51,   5367.51,   5367.51]
    configdict["sigma1"]  = [11.918,    5.9281,    10.000,    11.056,    12.612 ]
    configdict["sigma2"]  = [23.846,    13.728,    13.025,    17.855,    27.706 ]
    configdict["alpha1"]  = [2.3531,    3.1526,    0.09332,   2.1254,    2.4246 ]
    configdict["alpha2"]  = [-2.2111,   -2.1330,   -1.9956,   -2.0608,   -3.1221]
    configdict["n1"]      = [0.51164,   2.4702,    1.9978,    1.0916,   0.77405]
    configdict["n2"]      = [0.59249,   2.2952,    1.9958,    5.8375,   0.00100]
    configdict["frac"]    = [0.74389,   0.15038,   0.16486,   0.60582,   0.85164]

    configdict["sigma1_bc"]  = [18.934,  18.447,  10.000,   20.983,  24.613 ]
    configdict["sigma2_bc"]  = [9.6762,  11.850,  13.025,   10.928,  11.852 ]
    configdict["alpha1_bc"]  = [2.1964,  1.5942,  0.9332,   2.0444,  1.9209 ]
    configdict["alpha2_bc"]  = [-2.7283, -2.4168, -1.9956,  -3.5144, -4.0848]
    configdict["n1_bc"]      = [0.89044, 1.5644,  1.9978,   0.87044, 0.88570]
    configdict["n2_bc"]      = [0.96861, 2.0040,  1.9958,   0.30156, 0.00101]
    configdict["frac_bc"]    = [0.53414, 0.34001, 0.16486,  0.32682, 0.23252]
                            

    configdict["sigma1Bsfrac"] = 1.061
    configdict["sigma2Bsfrac"] = 1.255
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0
                    
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    configdict["sigma1Ds"]  = [4.7411,  2.5361,  7.3631,  6.1454,  7.5586 ]
    configdict["sigma2Ds"]  = [10.842,  6.1485,  3.5137,  11.007,  14.724 ]
    configdict["alpha1Ds"]  = [2.8086,  1.1802,  2.2427,  2.1387,  2.8327 ]
    configdict["alpha2Ds"]  = [-2.4221, -1.6223, -1.4475, -2.0614, -2.1168]
    configdict["n1Ds"]      = [0.0001,  0.6575,  0.7693,  0.80007, 0.0002 ]
    configdict["n2Ds"]      = [0.0001,  3.9486,  1.7064,  0.76423, 1.2687 ]
    configdict["fracDs"]    = [0.64972, 0.15555, 0.62754, 0.80417, 0.63724]

    configdict["sigma1Ds_bc"]  = [9.8605,  13.340,  3.5176,  12.739,  10.698 ]
    configdict["sigma2Ds_bc"]  = [4.5908,  5.3657,  7.4371,  6.2401,  7.1206 ]
    configdict["alpha1Ds_bc"]  = [2.4405,  1.2116,  2.9451,  1.4772,  1.1216 ]
    configdict["alpha2Ds_bc"]  = [-3.9725, -6.3223, -2.1548, -6.7187, -1.3441]
    configdict["n1Ds_bc"]      = [0.0202,  1.7116,  0.0010,  50.000,  49.999 ]
    configdict["n2Ds_bc"]      = [41.126,  8.9688,  3.0951,  2.8824,  5.5825 ]
    configdict["fracDs_bc"]    = [0.36279, 0.16606, 0.34482, 0.29598, 0.48947]
    

    configdict["sigma1Dsfrac"] = 1.063
    configdict["sigma2Dsfrac"] = 1.221
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0
    
    configdict["cB"]        = [-1.2584e-03,  -8.9179e-04,  -1.1359e-03, -9.2140e-04, -1.0508e-03]
    configdict["cD"]        = [-7.2485e-03,  -1.0518e-03,  -4.9031e-03, -8.0964e-04, -1.3809e-03]
    configdict["fracComb"]  = [0.77545,      0.33290,      0.63637,      1.0,         1.0]
    
        
    configdict["nBs2DsDsstPiRhoEvts"]  = [29.0/2.0, 29.0/2.0,
                                          34.0/2.0, 34.0/2.0,
                                          33.0/2.0, 33.0/2.0,
                                          5.0/2.0,  5.0/2.0,
                                          15.0/2.0, 15.0/2.0]

    configdict["nBs2DsPiEvts"]  = [29.0/2.0, 29.0/2.0,
                                   34.0/2.0, 34.0/2.0,
                                   33.0/2.0, 33.0/2.0,
                                   5.0/2.0,  5.0/2.0,
                                   15.0/2.0, 15.0/2.0]
    
    
    configdict["nLbDspEvts"]           = [46,78,
                                          46,78,
                                          46,78,
                                          5,8,
                                          10,16]
    
    configdict["nLbLcKEvts"]           = [3.0/2.0, 3.0/2.0,
                                          0, 0,
                                          1.0/2.0, 1.0/2.0,
                                          0, 0,
                                          0, 0]
    
    configdict["nBdDKEvts"]            = [3.0/2.0, 3.0/2.0,
                                          0, 0,
                                          1.0/2.0, 1.0/2.0,
                                          0, 0,
                                          0, 0]

    configdict["OnBs2DsDsstPiRhoEvts"]  = [56*100./38.2651+80*100./38.2651, 5*100./38.2651+7*100./38.2651, 10*100./38.2651+14*100./38.2651]
    configdict["OnLbDspEvts"]           = [46+78,5+8,10+16]
    configdict["OnLbLcKEvts"]           = [8.3220*100/15+1.1299*1000/15, 0+ 0, 0+ 0] #[4.1088*100./15.,6.7221*100./15.,0,0,0,0]
    configdict["OnBdDKEvts"]            = [6.7238*100/15+1.0097*1000/15, 4.3334*10/15+4.4202*10/15, 0+0] #[14,23,2,3,0,0]
                
    
    configdict["g2_f1"] = 0.42761287
    configdict["g2_f2"] = 0.47275694
    configdict["g2_f3"] = 0.05205979

    return configdict
