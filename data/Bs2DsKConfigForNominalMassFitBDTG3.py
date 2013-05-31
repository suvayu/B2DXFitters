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
                                     
    
    configdict["BDTGDown"]   = 0.9
    configdict["BDTGUp"]     = 1.0
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

    configdict["lumRatio"] =  0.44/(0.44+0.59)

    # 1: NonRes, 2: PhiPi, 3: KstK, 4: KPiPi, 5: PiPiPi
    configdict["mean"]    = [5367.51,   5367.51,   5367.51,   5367.51,   5367.51]

    configdict["sigma1"]  = [9.0472,    12.379,    11.214,    22.129,    24.367 ]
    configdict["sigma2"]  = [13.811,    24.650,    15.251,    11.881,    12.434 ]
    configdict["alpha1"]  = [1.2220,    2.2174,    1.7521,    1.7321,    1.7567 ]
    configdict["alpha2"]  = [-1.8682,   -4.6215,   -1.6188,   -4.9613,   -4.9935]
    configdict["n1"]      = [1.7979,    1.2885,    1.6414,    1.4587,    1.4412 ]
    configdict["n2"]      = [5.6418,    2.5622,    14.969,    24.767,    17.813 ]  
    configdict["frac"]    = [0.27738,    0.85163,   0.51524,   0.22956,   0.23445]

    configdict["sigma1_bc"]  = [9.3594,  10.246,  11.736,    11.379,  10.273 ]
    configdict["sigma2_bc"]  = [13.976,  15.009,  13.160,    18.519,  16.054 ]
    configdict["alpha1_bc"]  = [1.4771,  1.5002,  0.094948,  2.2280,  1.6299 ]
    configdict["alpha2_bc"]  = [-1.8186, -2.0507, -1.9799,   -4.2546, -2.0443]
    configdict["n1_bc"]      = [1.6233,  1.7957,  2.4326,    1.2341,  1.6175 ]
    configdict["n2_bc"]      = [12.621,  4.6849,  5.5777,    0.00127, 7.5742 ]
    configdict["frac_bc"]    = [0.20484, 0.41563, 0.096174,  0.71079, 0.41134]
    

    configdict["sigma1Bsfrac"] = 1.175
    configdict["sigma2Bsfrac"] = 1.241
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0
        
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    configdict["sigma1Ds"]  = [7.4064,  5.3325,  10.906,  12.906,  8.2026 ]
    configdict["sigma2Ds"]  = [4.1307,  4.9137,  5.3241,  6.3213,  7.2805 ]
    configdict["alpha1Ds"]  = [1.7264,  1.2324,  2.6912,  0.86509, 0.8462 ]
    configdict["alpha2Ds"]  = [-2.7109, -0.9240, -5.1596, -1.8347, -1.0673]
    configdict["n1Ds"]      = [4.0476,  5.9400,  0.0001,  49.940,  25.000 ]
    configdict["n2Ds"]      = [0.7406,  49.986,  23.600,  49.994,  25.000 ]
    configdict["fracDs"]    = [0.50116, 0.59858, 0.18356, 0.17298, 0.50178]

    configdict["sigma1Ds_bc"]  = [8.8751,  9.2809,  9.5493,  11.056,  13.168 ]
    configdict["sigma2Ds_bc"]  = [4.5467,  4.7344,  5.1230,  5.8102,  7.0023 ]
    configdict["alpha1Ds_bc"]  = [2.0523,  2.1115,  2.8816,  1.7695,  1.1240 ] 
    configdict["alpha2Ds_bc"]  = [-5.9174, -5.1894, -5.8791, -6.7247, -5.0621]
    configdict["n1Ds_bc"]      = [2.1525,  1.2338,  0.001,   1.1312,  70.000 ] 
    configdict["n2Ds_bc"]      = [14.313,  47.932,  17.069,  41.176,  53.970 ]
    configdict["fracDs_bc"]    = [0.31424, 0.28752, 0.24472, 0.31573, 0.33700]
                            

    configdict["sigma1Dsfrac"] = 1.109
    configdict["sigma2Dsfrac"] = 1.182
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0

    configdict["cB"]        = [-5.1335e-04,  -1.0351e-03,  -3.4412e-03, -1.2013e-03, -1.3473e-03]
    configdict["cD"]        = [-5.0595e-03,  -1.0961e-03,  -8.9066e-03, -3.2762e-03, -2.6176e-04]
    configdict["fracComb"]  = [0.72701,      0.24137,      0.57409,      1.0,         1.0]
            

    configdict["nBs2DsPiEvts"]  = [72.0/2.0, 72.0/2.0,
                                   84.0/2.0, 84.0/2.0,
                                   72.0/2.0, 72.0/2.0,
                                   17.0/2.0, 17.0/2.0,
                                   41.0/2.0, 41.0/2.0]
    
    configdict["nBs2DsDsstPiRhoEvts"]  = [86.0/2.0,  86.0/2.0,
                                          101.0/2.0, 101.0/2.0,
                                          88.0/2.0,  88.0/2.0,
                                          19.0/2.0,  19.0/2.0,
                                          49.0/2.0,  49.0/2.0]
    
    configdict["nLbDspEvts"]           = [46,78,
                                          46,78,
                                          46,78,
                                          5,8,
                                          10,16]
    
    configdict["nLbLcKEvts"]           = [6.0/2.0,  6.0/2.0,
                                          1.0/2.0,  1.0/2.0,
                                          2.0/2.0,  2.0/2.0,
                                          0, 0,
                                          0, 0]
    
    configdict["nBdDKEvts"]            = [6.0/2.0, 6.0/2.0,
                                          0, 0,
                                          2.0/2.0, 2.0/2.0,
                                          0, 0,
                                          0, 0] 
    
    configdict["g2_f1"] = 0.42761287
    configdict["g2_f2"] = 0.47275694
    configdict["g2_f3"] = 0.05205979

    return configdict
