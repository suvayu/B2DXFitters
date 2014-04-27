def getconfig() :

    from Bs2DsKConfigForGenerator5M import getconfig as getconfig_nominal
    baselineconfig = getconfig_nominal()

    baselineconfig["aprod_Signal"]       = -0.014 #0.03
    baselineconfig["aprod_Bd2DK"]        = 0.011 #0.03
    baselineconfig["aprod_Bd2DPi"]       = 0.011 #0.03 
    baselineconfig["aprod_Bd2DsK"]       = 0.011 #3
    baselineconfig["aprod_Bs2DsPi"]      = -0.014 # 3
    baselineconfig["aprod_Lb2LcK"]       = 0.03 # 3
    baselineconfig["aprod_Lb2LcPi"]      = 0.03 # 3
    baselineconfig["aprod_Combo"]        = 0.0 #3
    baselineconfig["aprod_Lb2Dsp"]       = 0.03 #3
    baselineconfig["aprod_Lb2Dsstp"]     = 0.03 #3
    baselineconfig["aprod_LM1"]          = 0.03 #3
    baselineconfig["aprod_Bs2DsstPi"]    = -0.014 #3
    baselineconfig["aprod_Bs2DsRho"]     = -0.014 #3

    baselineconfig["adet_Signal"]       = 0.01
    baselineconfig["adet_Bd2DK"]        = 0.01
    baselineconfig["adet_Bd2DPi"]       = 0.005
    baselineconfig["adet_Bd2DsK"]       = 0.01
    baselineconfig["adet_Bs2DsPi"]      = 0.005
    baselineconfig["adet_Lb2LcK"]       = 0.01
    baselineconfig["adet_Lb2LcPi"]      = 0.005
    baselineconfig["adet_Combo"]        = 0.01
    baselineconfig["adet_Lb2Dsp"]       = 0.02
    baselineconfig["adet_Lb2Dsstp"]     = 0.02
    baselineconfig["adet_LM1"]          = 0.01
    baselineconfig["adet_Bs2DsstPi"]    = 0.005
    baselineconfig["adet_Bs2DsRho"]     = 0.005
    
    return baselineconfig
