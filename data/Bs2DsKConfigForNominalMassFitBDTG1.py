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
                                     
    
    configdict["BDTGDown"]   = 0.3
    configdict["BDTGUp"]   = 0.7
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
    configdict["sigma1"]  = [11.918,    5.9281,    10.000,    11.056,    12.612 ]
    configdict["sigma2"]  = [23.846,    13.728,    13.025,    17.855,    27.706 ]
    configdict["alpha1"]  = [2.3531,    3.1526,    0.09332,   2.1254,    2.4246 ]
    configdict["alpha2"]  = [-2.2111,   -2.1330,   -1.9956,   -2.0608,   -3.1221]
    configdict["n1"]      = [0.51164,   2.4702,    1.9978,    1.0916,   0.77405]
    configdict["n2"]      = [0.59249,   2.2952,    1.9958,    5.8375,   0.00100]
    configdict["frac"]    = [0.74389,   0.15038,   0.16486,   0.60582,   0.85164]

    configdict["sigma1Bsfrac"] = 1.123
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

    configdict["sigma1Dsfrac"] = 1.069
    configdict["sigma2Dsfrac"] = 1.214
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0
    
    configdict["cB"]        = [-1.2584e-03,  -8.9179e-04,  -1.1359e-03, -9.2140e-04, -1.0508e-03]
    configdict["cD"]        = [-7.2485e-03,  -1.0518e-03,  -4.9031e-03, -8.0964e-04, -1.3809e-03]
    configdict["fracComb"]  = [0.77545,      0.33290,      0.63637,      1.0,         1.0]
    
        
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
    configdict["OnLbLcKEvts"]           = [8.3220*100/15+1.1299*1000/15, 0+ 0, 0+ 0] #[4.1088*100./15.,6.7221*100./15.,0,0,0,0]
    configdict["OnBdDKEvts"]            = [6.7238*100/15+1.0097*1000/15, 4.3334*10/15+4.4202*10/15, 0+0] #[14,23,2,3,0,0]
                
    
    configdict["g2_f1"] = 0.42761287
    configdict["g2_f2"] = 0.47275694
    configdict["g2_f3"] = 0.05205979

    return configdict
