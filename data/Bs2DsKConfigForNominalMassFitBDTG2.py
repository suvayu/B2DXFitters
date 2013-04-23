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

    configdict["mean"]    = 5367.51
    configdict["sigma1"]  = 11.898*14.01/11.63 #10.0880
    configdict["sigma2"]  = 17.643*24.96/17.99 #15.708
    configdict["alpha1"]  = 2.0600*2.634/1.839 #1.8086
    configdict["alpha2"]  = -1.7601*2.147/2.021 #-1.8169
    configdict["n1"]      = 1.1934
    configdict["n2"]      = 10.00
    configdict["frac"]    = 0.64924
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
    configdict["sigma1Ds"]  = [5.0560*6.88/5.73, 5.0560*6.88/5.73, 5.0560*6.88/5.73, 6.2093*6.88/5.73, 7.3576*6.88/5.73] #8.2726
    configdict["sigma2Ds"]  = [5.2700*7.47/6.41, 5.2700*7.47/6.41, 5.2700*7.47/6.41, 5.6614*7.47/6.41, 7.5516*7.47/6.41] #4.5723
    configdict["alpha1Ds"]  = [0.14745, 0.14745, 0.14745, 0.25668, 0.19311 ]
    configdict["alpha2Ds"]  = [0.11578, 0.11578, 0.11578, 0.26943, 0.12664 ]
    configdict["fracDs"]    = [0.44465, 0.5, 0.5, 0.5, 0.5]
        
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
