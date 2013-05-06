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
                                     
    
    configdict["BDTGDown"]   = 0.7
    configdict["BDTGUp"]   = 0.9
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
    configdict["sigma1"]  = [11.227,    12.964,    12.604,    23.179,    11.407 ]
    configdict["sigma2"]  = [16.924,    27.692,    15.436,    12.022,    15.904 ]
    configdict["alpha1"]  = [1.9569,    2.3193,    1.9330,    2.0008,    1.6604 ]
    configdict["alpha2"]  = [-2.2580,   -2.8025,   -1.6045,   -4.5619,   -1.9035]
    configdict["n1"]      = [0.95297,   1.0325,    1.3461,    0.81900,   1.3752 ]
    configdict["n2"]      = [1.7935,    0.87978,   7.0189,    41.050,    3.6713 ] 
    configdict["frac"]    = [0.54326,   0.87682,   0.59296,   0.27455,   0.45538]

    configdict["sigma1Bsfrac"] = 1.256
    configdict["sigma2Bsfrac"] = 1.116
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0
    
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    configdict["sigma1Ds"]  = [3.0188,  4.6249,  6.6413,  4.8833,  7.1645 ]
    configdict["sigma2Ds"]  = [6.8363,  8.9847,  4.7140,  8.6363,  12.931 ]
    configdict["alpha1Ds"]  = [2.2347,  2.8112,  1.0685,  2.4116,  2.2429 ]
    configdict["alpha2Ds"]  = [-2.1451, -2.0557, -1.4100, -2.1357, -2.4206]
    configdict["n1Ds"]      = [0.2647,  0.1050,  19.794,  0.0726,  0.3197 ]
    configdict["n2Ds"]      = [1.4626,  2.7599,  4.3085,  2.6879,  0.5377 ]
    configdict["fracDs"]    = [0.19892, 0.62386, 0.50402, 0.33139, 0.61798]

    configdict["sigma1Dsfrac"] = 1.036
    configdict["sigma2Dsfrac"] = 1.167
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0
    
    configdict["cB"]        = [-5.1335e-04,  -1.0351e-03,  -3.4412e-03, -1.2013e-03, -1.3473e-03]
    configdict["cD"]        = [-5.0595e-09,  -1.0961e-07,  -8.9066e-03, -3.2762e-03, -2.6176e-04]
    configdict["fracComb"]  = [0.72701,      0.24137,      0.57409,      1.0,         1.0]
    
        
    configdict["nBs2DsDsstPiRhoEvts"]  = [56*100./38.2651, 80*100./38.2651,
                                          56*100./38.2651, 80*100./38.2651,
                                          56*100./38.2651, 80*100./38.2651,
                                          5*100./38.2651, 7*100./38.2651,
                                          10*100./38.2651, 14*100./38.2651]
    
    configdict["nLbDspEvts"]           = [46,78,
                                          46,78,
                                          46,78,
                                          5,8,
                                          10,16]
    
    configdict["nLbLcKEvts"]           = [8.3220*100/15, 1.1299*1000/15,
                                          8.3220*100/15, 1.1299*1000/15,
                                          8.3220*100/15, 1.1299*1000/15,
                                          0, 0,
                                          0, 0] #[4.1088*100./15.,6.7221*100./15.,0,0,0,0]
    
    configdict["nBdDKEvts"]            = [6.7238*100/15, 1.0097*1000/15,
                                          6.7238*100/15, 1.0097*1000/15,
                                          6.7238*100/15, 1.0097*1000/15,
                                          4.3334*10/15, 4.4202*10/15,
                                          0 ,0] #[14,23,2,3,0,0]

    configdict["OnBs2DsDsstPiRhoEvts"]  = [56*100./38.2651+80*100./38.2651, 5*100./38.2651+7*100./38.2651, 10*100./38.2651+14*100./38.2651]
    configdict["OnLbDspEvts"]           = [46+78,5+8,10+16]
    configdict["OnLbLcKEvts"]           = [8.3220*100/15+1.1299*1000/15, 0+0, 0+0] #[4.1088*100./15.,6.7221*100./15.,0,0,0,0]
    configdict["OnBdDKEvts"]            = [6.7238*100/15+1.0097*1000/15, 4.3334*10/15+4.4202*10/15, 0+0] #[14,23,2,3,0,0]
                
    
    configdict["g2_f1"] = 0.42761287
    configdict["g2_f2"] = 0.47275694
    configdict["g2_f3"] = 0.05205979

    return configdict
