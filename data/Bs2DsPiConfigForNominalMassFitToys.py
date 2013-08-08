def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # PHYSICAL PARAMETERS
    configdict["BMassDown"]  = 5300
    configdict["BMassUp"]    = 5800
    configdict["BMassDownData"]  = 5300
    configdict["BMassUpData"]    = 5800
    configdict["BMassDownComb"]  = 5600
    configdict["BMassUpComb"]    = 7000
        
    configdict["DMassDown"]  = 1930
    configdict["DMassUp"]    = 2015
    configdict["TimeDown"]   = 0.0
    configdict["TimeUp"]     = 15.0
    configdict["PDown"]      = 3000.0
    configdict["PUp"]        = 650000.0
    configdict["PTDown"]      = 400.0
    configdict["PTUp"]        = 45000.0
    configdict["PIDDown"]      = -150.0
    configdict["PIDUp"]        = 0.0
    configdict["nTracksDown"]      = 15
    configdict["nTracksUp"]        = 1000.0
    configdict["Bin1"]      = 20
    configdict["Bin2"]      = 20
    configdict["Bin3"]      = 10
    configdict["Var1"]      = "lab1_PT"
    configdict["Var2"]      = "nTracks"
    configdict["Var3"]      = "lab1_P"
    configdict["BDTGDown"]   = 0.3
    configdict["BDTGUp"]     = 1.0
    configdict["PIDBach"]    = 0
    configdict["PIDBach2"]   = 0
    configdict["PIDChild"]   = 0
    configdict["PIDProton"]  = 5    
    configdict["dataName"]   = "../data/config_Bs2Dsh2011TDAna_Bs2DsPi.txt"
    
    configdict["fileCalib"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpPi_0.root"
    configdict["fileCalibDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownPi_0.root"
    configdict["fileCalibKaonUp"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStUpK_0.root"
    configdict["fileCalibKaonDown"]  = "/afs/cern.ch/work/a/adudziak/public/workspace/CalibDStDownK_0.root"
    configdict["workCalib"]  = "RSDStCalib"

    configdict["lumRatio"] =  0.44/(0.59+0.44)

    configdict["Gammas"]      =  1/0.657    # in ps^{-1}
    configdict["DeltaGammas"] = -0.104
    
    configdict["DeltaMs"]     =  17.719     # in ps^{-1}
     
    configdict["TauRes"]    =  0.05
    
    configdict["StrongPhase_s"] = 30. / 180. * pi
    configdict["WeakPhase"]     = 70. / 180. * pi #70. / 180. * pi
    
    configdict["ArgLf_s"]       = configdict["StrongPhase_s"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar_s"] = configdict["StrongPhase_s"] + configdict["WeakPhase"]
    configdict["ModLf_s"]       = 0.372
    
    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    configdict["TagOmegaSig"]   = 0.391
    
    
    # 1: NonRes, 2: PhiPi, 3: KstK, 4: KPiPi, 5: PiPiPi 
    configdict["mean"]    = [5367.51]

    #Bs signal shape with BKGCAT
    configdict["sigma1_bc"]  = [17.396] 
    configdict["sigma2_bc"]  = [11.028] 
    configdict["alpha1_bc"]  = [1.8615] 
    configdict["alpha2_bc"]  = [-2.6267] 
    configdict["n1_bc"]      = [1.3245]
    configdict["n2_bc"]      = [2.1862]
    configdict["frac_bc"]    = [0.55406]

    # ratio data/MC
    configdict["sigma1Bsfrac"] = 1.145 
    configdict["sigma2Bsfrac"] = 1.255
    configdict["alpha1Bsfrac"] = 1.0 
    configdict["alpha2Bsfrac"] = 1.0 

    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49]

    #Ds signal shapes with BKGCAT
    configdict["sigma1Ds_bc"]  = [7.6215]
    configdict["sigma2Ds_bc"]  = [4.4422] 
    configdict["alpha1Ds_bc"]  = [1.8802] 
    configdict["alpha2Ds_bc"]  = [-2.2066]
    configdict["n1Ds_bc"]      = [2.5713]
    configdict["n2Ds_bc"]      = [1.8122]
    configdict["fracDs_bc"]    = [0.44075]
    
    # ratio data/MC
    configdict["sigma1Dsfrac"] = 1.074
    configdict["sigma2Dsfrac"] = 1.185 
    configdict["alpha1Dsfrac"] = 1.0 
    configdict["alpha2Dsfrac"] = 1.0 
        

    # combinatorial background
    configdict["cB1"]                = [-9.9005e-03]
    configdict["cB2"]                = [0.0]
    configdict["fracBsComb"]         = [6.6631e-01]
    
    configdict["cD"]        = [-3.4761e-03] 
    configdict["fracComb"]  = [0.59760]          

    #expected Events
    configdict["BdDPiEvents"]  = [444.]
    configdict["LbLcPiEvents"] = [400.] 
    configdict["BsDsKEvents"]  = [163.]
        
    configdict["assumedSig"]   = [29266./2., 29266./2.]
    configdict["nBd2DsPi"]     = 1./25. #1./30.
    configdict["nBd2DsstPi"]   = 1./25. #1./30.
    configdict["nBd2DstPi"]    = 1./4.
    configdict["nBd2DRho"]     = 1./3.5
    
    return configdict
