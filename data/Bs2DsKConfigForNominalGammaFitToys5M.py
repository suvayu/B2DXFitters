def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.661   # in ps^{-1}
    configdict["DeltaGammas"] = -0.105
    configdict["DeltaMs"]     =  17.768   # in ps^{-1}
    configdict["TagEffSig"]   = 0.403 #392 #403
    configdict["TagOmegaSig"] = 0.391
    configdict["StrongPhase"] = 4. / 180. * pi
    configdict["WeakPhase"]   = 116. / 180. * pi
    configdict["ArgLf"]       = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"] = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]       = 0.51
    
    configdict["calibration_p0"]  = [0.3927, 0.4244]
    configdict["calibration_p1"]  = [0.9818, 1.2550]
    configdict["calibration_av"]  = [0.3919, 0.4097]

    configdict["constr_p0_B"] = [0.0, 0.0, 0.0]
    configdict["constr_p1_B"] = [1.0, 1.0, 1.0]
    configdict["constr_av_B"] = [0.0, 0.0, 0.0]

    configdict["constr_p0_Bbar"] = [0.0, 0.0, 0.0]
    configdict["constr_p1_Bbar"] = [1.0, 1.0, 1.0]
    configdict["constr_av_Bbar"] = [0.0, 0.0, 0.0]
                    
    configdict["resolutionScaleFactor"] = 1.37 
    configdict["resolutionMeanBias"]    = 0.
    
    configdict["resolutionSigma1"] = 2.21465e-02
    configdict["resolutionSigma2"] = 3.72057e-02
    configdict["resolutionSigma3"] = 6.37859e-02
    configdict["resolutionFrac1"]  = 3.62689e-01
    configdict["resolutionFrac2"]  = 5.65100e-01

    configdict["tacc_size"]   = 6
    configdict["tacc_knots"]  = [0.5, 1.0, 1.5, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [0.4453873694523979, 0.6869245867352556, 0.8719680916278891, 1.1614426699209424, 1.2341250036543179, 1.2852701638596233]

    configdict["tagEff_OS"] = 0.387
    configdict["tagEff_SS"] = 0.4772
    
    configdict["TagEffSig"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                  configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                  configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    
    configdict["aTagEffSig"]    = [0.0, 0.0, 0.0]
                
    configdict["MistagFile"]     = "../data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root"
    configdict["MistagWork"]     = "workspace"
    configdict["MistagTempName"] = ["sigMistagPdf_1", "sigMistagPdf_2", "sigMistagPdf_3"]
    
    configdict["TerrFile"]     = "../data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root"
    configdict["TerrWork"]     = "workspace"
    configdict["TerrTempName"] = "TimeErrorPdf_Bs2DsK"

    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('deltaMs')
    #configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent')
    configdict["constParams"].append('tacc_offset')
    configdict["constParams"].append('tacc_beta')
    configdict["constParams"].append('tacc_turnon')
    
    configdict["constParams"].append('p0_B_0')
    configdict["constParams"].append('p0_B_1')
    configdict["constParams"].append('p0_B_2')
    configdict["constParams"].append('p0_Bbar_0')
    configdict["constParams"].append('p0_Bbar_1')
    configdict["constParams"].append('p0_Bbar_2')

    configdict["constParams"].append('p1_B_0')
    configdict["constParams"].append('p1_B_1')
    configdict["constParams"].append('p1_B_2')
    configdict["constParams"].append('p1_Bbar_0')
    configdict["constParams"].append('p1_Bbar_1')
    configdict["constParams"].append('p1_Bbar_2')


    return configdict
