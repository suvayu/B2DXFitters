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
    configdict["BDTGDown"]   = 0.5
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
    configdict["sigma1"]  = 12.582*14.007/11.631 #12.635*14.007/11.631
    configdict["sigma2"]  = 20.000*24.957/17.991
    configdict["alpha1"]  = 2.0519*2.6338/1.8393 #2.0657*2.6338/1.8393
    configdict["alpha2"]  = -2.1164*2.1473/2.0208 #-2.0950*2.1473/2.0208
#    configdict["sigma1"]  = 11.769*14.337/11.967
#    configdict["sigma2"]  = 12.925*16.326/12.755
#    configdict["alpha1"]  = 0.15710
#    configdict["alpha2"]  = 0.088142

    configdict["n1"]      = 1.1560 #1.1466
    configdict["n2"]      = 4.4064 #4.6846
    configdict["frac"]    = 0.75401 #0.75903
    configdict["ratio1"]  = 1.00808721452
    configdict["ratio2"]  = 1.0386867331        

    configdict["meanDs"]    = [1968.49, 1968.49, 1968.49, 1968.49, 1968.49]
#    configdict["sigma1Ds"]  = 8.2726
#    configdict["sigma2Ds"]  = 4.5723
    configdict["fracDs"]    = [0.5, 0.5, 0.5, 0.5, 0.5]  #44465
    configdict["sigma1Ds"]  = [4.8978*6.8765/5.7317, 4.8978*6.8765/5.7317, 4.8978*6.8765/5.7317, 6.1294*6.8765/5.7317, 7.4626*6.8765/5.7317]
    configdict["sigma2Ds"]  = [5.3464*7.4714/6.4135, 5.3464*7.4714/6.4135, 5.3464*7.4714/6.4135, 5.6465*7.4714/6.4135, 7.7053*7.4714/6.4135] 
    configdict["alpha1Ds"]    = [0.14109, 0.14109, 0.14109, 0.25788, 0.17674]
    configdict["alpha2Ds"]    = [0.11095, 0.11095, 0.11095, 0.26196, 0.12480]

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
