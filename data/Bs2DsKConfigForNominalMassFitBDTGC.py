def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # PHYSICAL PARAMETERS
    configdict["BMassDown"]  = 5300
    configdict["BMassUp"]    = 5800
    configdict["DMassDown"]  = 1930
    configdict["DMassUp"]    = 2015
    configdict["TimeDown"]   = 0.0
    configdict["TimeUp"]     = 15.0
    configdict["PDown"]      = 0.0
    configdict["PUp"]        = 650000.0
    configdict["PTDown"]      = 100.0
    configdict["PTUp"]        = 45000.0
    configdict["PIDDown"]      = log(5.0)
    configdict["PIDUp"]        = log(150.0)
    configdict["nTracksDown"]      = 15
    configdict["nTracksUp"]        = 1000.0
    configdict["Bin1"]      = 20
    configdict["Bin2"]      = 20
    configdict["Var1"]      = "lab1_PT"
    configdict["Var2"]      = "nTracks"
                                     
    
    configdict["BDTGDown"]   = 0.5
    configdict["BDTGUp"]   = 1.0
    configdict["PIDBach"]    = 5
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsK.txt"

    configdict["fileCalibUpPion"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpPi_DsK.root"
    configdict["fileCalibDownPion"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownPi_DsK.root"
    configdict["workCalibPion"]  = "RSDStCalib"
    configdict["fileCalibUpKaon"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpK_DsK.root"
    configdict["fileCalibDownKaon"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownK_DsK.root"
    configdict["workCalibKaon"]  = "RSDStCalib"
    configdict["fileCalibUpProton"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/work_lblcpi_up_sw.root"
    #"/afs/cern.ch/work/a/adudziak/public/workspace/CalibLam0UpP_DsK.root"
    configdict["fileCalibDownProton"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/work_lblcpi_down_sw.root"
    #"/afs/cern.ch/work/a/adudziak/public/workspace/CalibLam0DownP_DsK.root"
    configdict["workCalibProton"]  = "workspace"
    configdict["pathFileLcPi"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/sWeights_LbLcPi_both_PIDK10.root"
    configdict["treeNameLcPi"] = "merged"

    configdict["lumRatio"] =  0.44/(0.59+0.44)

    # 1: NonRes, 2: PhiPi, 3: KstK, 4: KPiPi, 5: PiPiPi
    configdict["mean"]    = [5367.51,   5367.51,   5367.51,   5367.51,   5367.51]
    configdict["sigma1"]  = [17.633,    11.363,    11.433,    24.608,    10.790 ] 
    configdict["sigma2"]  = [10.657,    14.667,    15.003,    12.179,    16.232 ]
    configdict["alpha1"]  = [1.9588,    1.4871,    1.7353,    1.7824,    1.6425 ]   
    configdict["alpha2"]  = [-2.7914,   -1.5999,   -1.7643,   -4.9073,   -1.9082] 
    configdict["n1"]      = [1.0626,    1.7214,    1.4734,    1.0684,    1.4758 ]
    configdict["n2"]      = [0.67240,   10.899,    5.6102,    46.173,    5.3862 ]
    configdict["frac"]    = [0.47709,   0.43676,   0.46666,   0.20530,   0.44326]

    configdict["sigma1_bc"]  = [10.648,  10.578,  20.897,  10.861,  19.632 ]
    configdict["sigma2_bc"]  = [17.140,  15.342,  11.920,  16.688,  11.538 ]
    configdict["alpha1_bc"]  = [2.1250,  1.6054,  1.7399,   1.9777,  1.8833 ]
    configdict["alpha2_bc"]  = [-2.5565, -1.9820, -3.0799, -2.2358, -2.9423]
    configdict["n1_bc"]      = [1.0958,  1.5875,  1.3758,  1.3163,  1.3591 ]
    configdict["n2_bc"]      = [2.3902,  5.2562,  1.1957,  5.9166,  1.4584 ]
    configdict["frac_bc"]    = [0.57892, 0.43057, 0.25549, 0.56533, 0.38197] 
                            

    configdict["sigma1Bsfrac"] = 1.115
    configdict["sigma2Bsfrac"] = 1.225
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0
        
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    configdict["sigma1Ds"]  = [4.5318,  12.165,  7.2651,  9.1278,  7.0233 ]  
    configdict["sigma2Ds"]  = [8.5477,  5.1476,  4.3446,  5.2328,  12.854 ]
    configdict["alpha1Ds"]  = [3.0861,  1.6409,  1.6323,  1.8280,  2.2457 ]
    configdict["alpha2Ds"]  = [-2.3834, -4.7983, -2.0242, -2.7475, -2.4535]
    configdict["n1Ds"]      = [0.0003,  1.5183,  5.1154,  1.4139,  0.4679 ]
    configdict["n2Ds"]      = [0.7323,  48.812,  1.7394,  0.4224,  0.7075 ]
    configdict["fracDs"]    = [0.59582, 0.19160, 0.56708, 0.57017, 0.61692]

    configdict["sigma1Ds_bc"]  = [9.7500,  10.690,  4.4167,  11.519,  13.362 ]
    configdict["sigma2Ds_bc"]  = [4.8274,  4.9654,  7.6252,  6.0434,  7.1585 ]
    configdict["alpha1Ds_bc"]  = [2.7668,  1.8580,  2.4918,  1.5367,  1.0697 ]
    configdict["alpha2Ds_bc"]  = [-6.7682, -5.8877, -2.1923, -6.9993, -4.5605]
    configdict["n1Ds_bc"]      = [0.0100,  1.0482,  0.69412, 2.0860,  99.986 ]
    configdict["n2Ds_bc"]      = [5.0698,  32.628,  6.6328,  39.864,  9.2469 ]
    configdict["fracDs_bc"]    = [0.27228, 0.22536, 0.49541, 0.29093, 0.33641]
                            

    configdict["sigma1Dsfrac"] = 1.068
    configdict["sigma2Dsfrac"] = 1.182
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0
    
    configdict["cB"]        = [-1.0338e-03,  -1.1407e-03,  -1.8780e-03, -8.5626e-04, -1.2470e-03]
    configdict["cD"]        = [-2.3243e-03,  -1.1806e-02,  -4.8568e-03, -5.6559e-04, -8.9285e-04]
    configdict["fracComb"]  = [0.76621,      0.30957,      0.67304,      1.0,         1.0]
    
        
    configdict["nBs2DsDsstPiRhoEvts"]  = [170.0/2.0, 170.0/2.0,
                                          198.0/2.0, 198.0/2.0,
                                          181.0/2.0, 181.0/2.0,
                                          36.0/2.0,  36.0/2.0,
                                          93.0/2.0,  93.0/2.0]

    configdict["nBs2DsPiEvts"]  = [170.0/2.0, 170.0/2.0,
                                   198.0/2.0, 198.0/2.0,
                                   181.0/2.0, 181.0/2.0,
                                   36.0/2.0,  36.0/2.0,
                                   93.0/2.0,  93.0/2.0]
    

    configdict["nLbDspEvts"]           = [46,78,
                                          46,78,
                                          46,78,
                                          5,8,
                                          10,16]
    
    configdict["nLbLcKEvts"]    = [15.0/2.0, 15.0/2.0,
                                   2.0/2.0,  2.0/2.0,
                                   4.0/2.0,  4.0/2.0,
                                   0, 0,
                                   0, 0]

    
    configdict["nBdDKEvts"]      = [14.0/2.0, 14.0/2.0,
                                    0.0/2.0,  0.0/2.0,
                                    4.0/2.0,  4.0/2.0,
                                    0, 0,
                                    0 ,0]
    
    configdict["NEWnBs2DsDsstPiRhoEvts"]  = [56*100./38.2651+80*100./38.2651, 5*100./38.2651+7*100./38.2651, 10*100./38.2651+14*100./38.2651]
    configdict["NEWnLbDspEvts"]           = [46+78,5+8,10+16]
    configdict["NEWnLbLcKEvts"]           = [8.3220*100/15+1.1299*1000/15, 0+0, 0+0] #[4.1088*100./15.,6.7221*100./15.,0,0,0,0]
    configdict["NEWnBdDKEvts"]            = [6.7238*100/15+1.0097*1000/15, 4.3334*10/15+4.4202*10/15, 0+0] #[14,23,2,3,0,0]
                
    
    configdict["g2_f1"] = 0.42761287
    configdict["g2_f2"] = 0.47275694
    configdict["g2_f3"] = 0.05205979

    return configdict
