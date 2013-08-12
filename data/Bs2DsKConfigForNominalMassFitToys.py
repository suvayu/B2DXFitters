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

    configdict["mean"]    = [5369]

    configdict["sigma1_bc"]  = [10.627]
    configdict["sigma2_bc"]  = [15.289]
    configdict["alpha1_bc"]  = [1.6086]
    configdict["alpha2_bc"]  = [-1.9642]
    configdict["n1_bc"]      = [1.5879]
    configdict["n2_bc"]      = [5.1315]
    configdict["frac_bc"]    = [0.43480]
    
    configdict["ratio1"]  = 0.998944636665
    configdict["ratio2"]  = 1.00022181515

    configdict["sigma1Bsfrac"] = 1.145
    configdict["sigma2Bsfrac"] = 1.255
    configdict["alpha1Bsfrac"] = 1.0
    configdict["alpha2Bsfrac"] = 1.0
                    
    
    configdict["meanDs"]    = [1969]
    configdict["sigma1Ds_bc"]  = [8.7205]
    configdict["sigma2Ds_bc"]  = [4.5795]
    configdict["alpha1Ds_bc"]  = [1.9260]
    configdict["alpha2Ds_bc"]  = [-3.2773]
    configdict["n1Ds_bc"]      = [1.4224]
    configdict["n2Ds_bc"]      = [0.36197]
    configdict["fracDs_bc"]    = [0.36627]

    configdict["sigma1Dsfrac"] = 1.074
    configdict["sigma2Dsfrac"] = 1.185
    configdict["alpha1Dsfrac"] = 1.0
    configdict["alpha2Dsfrac"] = 1.0
    
    configdict["cB"] = [-9.2354e-04] #[-1.9385e-03]
    configdict["cD"] = [-8.8642e-03] #[-1.9408e-03]
    configdict["fracComb"] = [0.34206] #[5.1218e-01]

    configdict["nBs2DsDsstPiRhoEvts"]  = [715.0/2.0, 715.0/2.0]
    configdict["nBs2DsPiEvts"]         = [715.0/2.0, 715.0/2.0]
    configdict["nLbDspEvts"]           = [153.0/2.0, 153.0/2.0]
    configdict["nLbLcKEvts"]           = [21.0/2.0,   21.0/2.0]
    configdict["nBdDKEvts"]            = [19.0/2.0,   19.0/2.0]
         
    configdict["g2_f1"] = 0.374
    configdict["g2_f2"] = 0.196
    configdict["g2_f3"] = 0.127

    return configdict
