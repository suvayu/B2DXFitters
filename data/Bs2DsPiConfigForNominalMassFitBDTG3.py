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
    configdict["BDTGDown"]   = 0.9
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

    configdict["mean"]    = 5367.51
    configdict["sigma1"]  = 12.304*14.007/11.631
    configdict["sigma2"]  = 14.942*24.957/17.991
    configdict["alpha1"]  = 1.5708*2.6338/1.8393
    configdict["alpha2"]  = -1.7385*2.1473/2.0208
#    configdict["sigma1"]  = 11.769*14.337/11.967
#    configdict["sigma2"]  = 12.925*16.326/12.755
#    configdict["alpha1"]  = 0.15710
#    configdict["alpha2"]  = 0.088142

    configdict["n1"]      = 1.5411
    configdict["n2"]      = 10.000
    configdict["frac"]    = 0.45637
    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
#    configdict["sigma1Ds"]  = 8.2726
#    configdict["sigma2Ds"]  = 4.5723
    configdict["fracDs"]    = [0.5, 0.5, 0.5, 0.5, 0.5] #44465
    configdict["sigma1Ds"]  = [4.8978*6.8765/5.7317, 4.8978*6.8765/5.7317, 4.8978*6.8765/5.7317, 6.0734*6.8765/5.7317, 7.2560*6.8765/5.7317]
    configdict["sigma2Ds"]  = [5.3464*7.4714/6.4135, 5.3464*7.4714/6.4135, 5.3464*7.4714/6.4135, 5.5931*7.4714/6.4135, 7.7099*7.4714/6.4135]
    configdict["alpha1Ds"]    = [0.14109, 0.14109, 0.14109, 0.24808, 0.16592]
    configdict["alpha2Ds"]    = [0.11095, 0.11095, 0.11095, 0.25651, 0.10890]

    configdict["BdDPiEvents"]  = [260, 363,
                                  260, 363,
                                  260, 363,
                                  27*10, 38*10,
                                  0, 0]
    
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
