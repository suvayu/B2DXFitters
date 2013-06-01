def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    configdict["BDPi_D_BDTGA_sigma1"]  = [6.0109]
    configdict["BDPi_D_BDTGA_sigma2"]  = [11.710]
    configdict["BDPi_D_BDTGA_n1"]      = [0.3688]
    configdict["BDPi_D_BDTGA_n2"]      = [1.0265]
    configdict["BDPi_D_BDTGA_alpha1"]  = [2.5717]
    configdict["BDPi_D_BDTGA_alpha2"]  = [-2.3337]
    configdict["BDPi_D_BDTGA_frac"]    = [0.71173]

    configdict["BDPi_D_BDTGC_sigma1"]  = [5.9603]
    configdict["BDPi_D_BDTGC_sigma2"]  = [11.173]
    configdict["BDPi_D_BDTGC_n1"]      = [0.40491]
    configdict["BDPi_D_BDTGC_n2"]      = [1.9933]
    configdict["BDPi_D_BDTGC_alpha1"]  = [2.5190]
    configdict["BDPi_D_BDTGC_alpha2"]  = [-2.1635]
    configdict["BDPi_D_BDTGC_frac"]    = [0.6900]

    configdict["BDPi_D_BDTG1_sigma1"]  = [6.4114]
    configdict["BDPi_D_BDTG1_sigma2"]  = [16.149]
    configdict["BDPi_D_BDTG1_n1"]      = [0.38134]
    configdict["BDPi_D_BDTG1_n2"]      = [63.803]
    configdict["BDPi_D_BDTG1_alpha1"]  = [2.6933]
    configdict["BDPi_D_BDTG1_alpha2"]  = [-1.4621]
    configdict["BDPi_D_BDTG1_frac"]    = [0.76487]
    
    configdict["BDPi_D_BDTG2_sigma1"]  = [6.0938]
    configdict["BDPi_D_BDTG2_sigma2"]  = [12.387]
    configdict["BDPi_D_BDTG2_n1"]      = [0.96396]
    configdict["BDPi_D_BDTG2_n2"]      = [0.00022]
    configdict["BDPi_D_BDTG2_alpha1"]  = [2.2139]
    configdict["BDPi_D_BDTG2_alpha2"]  = [-2.7515]
    configdict["BDPi_D_BDTG2_frac"]    = [0.72605]
                            
    configdict["BDPi_D_BDTG3_sigma1"]  = [6.6574]
    configdict["BDPi_D_BDTG3_sigma2"]  = [6.3242]
    configdict["BDPi_D_BDTG3_n1"]      = [6.1752]
    configdict["BDPi_D_BDTG3_n2"]      = [24.887]
    configdict["BDPi_D_BDTG3_alpha1"]  = [0.94966]
    configdict["BDPi_D_BDTG3_alpha2"]  = [-1.2567]
    configdict["BDPi_D_BDTG3_frac"]    = [0.37238]

    ################################################

    configdict["BDPi_B_BDTGA_sigma1"]  = [14.673]
    configdict["BDPi_B_BDTGA_sigma2"]  = [5.5420]
    configdict["BDPi_B_BDTGA_n1"]      = [1.4094]
    configdict["BDPi_B_BDTGA_n2"]      = [5.0423]
    configdict["BDPi_B_BDTGA_alpha1"]  = [1.9154]
    configdict["BDPi_B_BDTGA_alpha2"]  = [-0.49187]
    configdict["BDPi_B_BDTGA_frac"]    = [0.87419]
    
    configdict["BDPi_B_BDTGC_sigma1"]  = [11.584]
    configdict["BDPi_B_BDTGC_sigma2"]  = [17.875]
    configdict["BDPi_B_BDTGC_n1"]      = [1.2648]
    configdict["BDPi_B_BDTGC_n2"]      = [2.5928]
    configdict["BDPi_B_BDTGC_alpha1"]  = [1.7760]
    configdict["BDPi_B_BDTGC_alpha2"]  = [-2.1635]
    configdict["BDPi_B_BDTGC_frac"]    = [0.57768]
    
    configdict["BDPi_B_BDTG1_sigma1"]  = [17.859]
    configdict["BDPi_B_BDTG1_sigma2"]  = [11.855]
    configdict["BDPi_B_BDTG1_n1"]      = [1.1113]
    configdict["BDPi_B_BDTG1_n2"]      = [2.1416]
    configdict["BDPi_B_BDTG1_alpha1"]  = [1.6260]
    configdict["BDPi_B_BDTG1_alpha2"]  = [-1.8632]
    configdict["BDPi_B_BDTG1_frac"]    = [0.45229]
    
    configdict["BDPi_B_BDTG2_sigma1"]  = [11.112]
    configdict["BDPi_B_BDTG2_sigma2"]  = [17.367]
    configdict["BDPi_B_BDTG2_n1"]      = [1.2075]
    configdict["BDPi_B_BDTG2_n2"]      = [2.3282]
    configdict["BDPi_B_BDTG2_alpha1"]  = [1.6733]
    configdict["BDPi_B_BDTG2_alpha2"]  = [-2.2144]
    configdict["BDPi_B_BDTG2_frac"]    = [0.48100]
    
    configdict["BDPi_B_BDTG3_sigma1"]  = [12.229]
    configdict["BDPi_B_BDTG3_sigma2"]  = [19.994]
    configdict["BDPi_B_BDTG3_n1"]      = [1.3458]
    configdict["BDPi_B_BDTG3_n2"]      = [2.3741]
    configdict["BDPi_B_BDTG3_alpha1"]  = [1.9349]
    configdict["BDPi_B_BDTG3_alpha2"]  = [-2.3558]
    configdict["BDPi_B_BDTG3_frac"]    = [0.72748]

    ################################################

    configdict["BDPi_D_BDTGA_slope"]  = [-1.6707e-03]
    configdict["BDPi_D_BDTGC_slope"]  = [-1.4560e-03]
    configdict["BDPi_D_BDTG1_slope"]  = [-1.6397e-03]
    configdict["BDPi_D_BDTG2_slope"]  = [-1.5883e-03]
    configdict["BDPi_D_BDTG3_slope"]  = [-1.5883e-03]
    
    ################################################

    configdict["BDPi_B_BDTGA_slope1"]  = [-9.4861e-04] #[-9.9277e-04]
    configdict["BDPi_B_BDTGC_slope1"]  = [-3.0000e-03] #[-9.4644e-04] #[-1.0000e-03]
    configdict["BDPi_B_BDTG1_slope1"]  = [-1.6111e-02] #[-8.0558e-03]
    configdict["BDPi_B_BDTG2_slope1"]  = [-2.9979e-03] #[-1.0209e-03]
    configdict["BDPi_B_BDTG3_slope1"]  = [-4.6422e-03] #[-7.0689e-04]

    ################################################

    configdict["BDPi_B_BDTGA_slope2"]  = [-4.6334e-03] #[-8.7344e-03]
    configdict["BDPi_B_BDTGC_slope2"]  = [-4.4580e-10] #[-5.1571e-03] #[-9.0343e-03]
    configdict["BDPi_B_BDTG1_slope2"]  = [-1.2051e-03] #[-9.8204e-04]
    configdict["BDPi_B_BDTG2_slope2"]  = [-1.6648e-03] #[-8.1089e-03]
    configdict["BDPi_B_BDTG3_slope2"]  = [-2.3211e-03] #[-1.4318e-02]

     ################################################

    configdict["BDPi_B_BDTGA_fracComb"]  = [7.1416e-01] #[8.7293e-01]
    configdict["BDPi_B_BDTGC_fracComb"]  = [8.0431e-01] #[5.9937e-01] #[8.0879e-01]
    configdict["BDPi_B_BDTG1_fracComb"]  = [1.5500e-06] #[9.6999e-02]
    configdict["BDPi_B_BDTG2_fracComb"]  = [1.5055e-02] #[7.3716e-01]
    configdict["BDPi_B_BDTG3_fracComb"]  = [1.0] #[2.7055e-01]
                        
    
    ################################################

    configdict["BDPi_D_BDTGA_fracComb"]  = [8.3957e-01]
    configdict["BDPi_D_BDTGC_fracComb"]  = [8.6519e-01]
    configdict["BDPi_D_BDTG1_fracComb"]  = [8.2367e-01]
    configdict["BDPi_D_BDTG2_fracComb"]  = [8.7215e-01]
    configdict["BDPi_D_BDTG3_fracComb"]  = [8.7215e-01]
                        
                     
    ################################################

    configdict["BDPi_D_BDTGA_sigma1_bc"]  = [12.818]
    configdict["BDPi_D_BDTGA_sigma2_bc"]  = [6.1793]
    configdict["BDPi_D_BDTGA_n1_bc"]      = [69.999]
    configdict["BDPi_D_BDTGA_n2_bc"]      = [44.783]
    configdict["BDPi_D_BDTGA_alpha1_bc"]  = [1.1198]
    configdict["BDPi_D_BDTGA_alpha2_bc"]  = [-4.7163]
    configdict["BDPi_D_BDTGA_frac_bc"]    = [0.22342]

    configdict["BDPi_D_BDTGC_sigma1_bc"]  = [11.906]
    configdict["BDPi_D_BDTGC_sigma2_bc"]  = [6.2074]
    configdict["BDPi_D_BDTGC_n1_bc"]      = [69.866]
    configdict["BDPi_D_BDTGC_n2_bc"]      = [53.017]
    configdict["BDPi_D_BDTGC_alpha1_bc"]  = [1.1251]
    configdict["BDPi_D_BDTGC_alpha2_bc"]  = [-4.9262]
    configdict["BDPi_D_BDTGC_frac_bc"]    = [0.21623]
    
    configdict["BDPi_D_BDTG1_sigma1_bc"]  = [6.0807]
    configdict["BDPi_D_BDTG1_sigma2_bc"]  = [6.3940]
    configdict["BDPi_D_BDTG1_n1_bc"]      = [69.988]
    configdict["BDPi_D_BDTG1_n2_bc"]      = [69.998]
    configdict["BDPi_D_BDTG1_alpha1_bc"]  = [0.50138]
    configdict["BDPi_D_BDTG1_alpha2_bc"]  = [-1.0893]
    configdict["BDPi_D_BDTG1_frac_bc"]    = [0.26044]
    
    configdict["BDPi_D_BDTG2_sigma1_bc"]  = [13.599]
    configdict["BDPi_D_BDTG2_sigma2_bc"]  = [6.2726]
    configdict["BDPi_D_BDTG2_n1_bc"]      = [69.998]
    configdict["BDPi_D_BDTG2_n2_bc"]      = [10.205]
    configdict["BDPi_D_BDTG2_alpha1_bc"]  = [1.1926]
    configdict["BDPi_D_BDTG2_alpha2_bc"]  = [-6.7549]
    configdict["BDPi_D_BDTG2_frac_bc"]    = [0.22381]

    configdict["BDPi_D_BDTG3_sigma1_bc"]  = [12.004]
    configdict["BDPi_D_BDTG3_sigma2_bc"]  = [6.1265]
    configdict["BDPi_D_BDTG3_n1_bc"]      = [69.993]
    configdict["BDPi_D_BDTG3_n2_bc"]      = [67.581]
    configdict["BDPi_D_BDTG3_alpha1_bc"]  = [1.0924]
    configdict["BDPi_D_BDTG3_alpha2_bc"]  = [-4.7004]
    configdict["BDPi_D_BDTG3_frac_bc"]    = [0.21078]
    
    ################################################
                         
    configdict["BDPi_B_BDTGA_sigma1_bc"]  = [1.1570e+01]
    configdict["BDPi_B_BDTGA_sigma2_bc"]  = [1.7757e+01]
    configdict["BDPi_B_BDTGA_n1_bc"]      = [1.2332e+00]
    configdict["BDPi_B_BDTGA_n2_bc"]      = [5.9538e+00]
    configdict["BDPi_B_BDTGA_alpha1_bc"]  = [1.8612e+00]
    configdict["BDPi_B_BDTGA_alpha2_bc"]  = [-2.1143e+00]
    configdict["BDPi_B_BDTGA_frac_bc"]    = [5.8739e-01]

    configdict["BDPi_B_BDTGC_sigma1_bc"]  = [11.527]
    configdict["BDPi_B_BDTGC_sigma2_bc"]  = [17.684]
    configdict["BDPi_B_BDTGC_n1_bc"]      = [1.2444]
    configdict["BDPi_B_BDTGC_n2_bc"]      = [5.6489]
    configdict["BDPi_B_BDTGC_alpha1_bc"]  = [1.8454]
    configdict["BDPi_B_BDTGC_alpha2_bc"]  = [-2.1261]
    configdict["BDPi_B_BDTGC_frac_bc"]    = [0.58240]
    
    configdict["BDPi_B_BDTG1_sigma1_bc"]  = [21.665]
    configdict["BDPi_B_BDTG1_sigma2_bc"]  = [11.787]
    configdict["BDPi_B_BDTG1_n1_bc"]      = [1.2463]
    configdict["BDPi_B_BDTG1_n2_bc"]      = [0.0049]
    configdict["BDPi_B_BDTG1_alpha1_bc"]  = [1.6421]
    configdict["BDPi_B_BDTG1_alpha2_bc"]  = [-5.7518]
    configdict["BDPi_B_BDTG1_frac_bc"]    = [0.34003]

    configdict["BDPi_B_BDTG2_sigma1_bc"]  = [11.155]
    configdict["BDPi_B_BDTG2_sigma2_bc"]  = [17.518]
    configdict["BDPi_B_BDTG2_n1_bc"]      = [1.1759]
    configdict["BDPi_B_BDTG2_n2_bc"]      = [3.5088]
    configdict["BDPi_B_BDTG2_alpha1_bc"]  = [1.7850]
    configdict["BDPi_B_BDTG2_alpha2_bc"]  = [-2.2694]
    configdict["BDPi_B_BDTG2_frac_bc"]    = [0.50796]
    
    configdict["BDPi_B_BDTG3_sigma1_bc"]  = [12.198]
    configdict["BDPi_B_BDTG3_sigma2_bc"]  = [19.176]
    configdict["BDPi_B_BDTG3_n1_bc"]      = [1.2883]
    configdict["BDPi_B_BDTG3_n2_bc"]      = [7.6431]
    configdict["BDPi_B_BDTG3_alpha1_bc"]  = [1.9855]
    configdict["BDPi_B_BDTG3_alpha2_bc"]  = [-2.1288]
    configdict["BDPi_B_BDTG3_frac_bc"]    = [0.72201]
    
    ################################################

    configdict["pred_Signal_BDTGA"]  = [7.6424e+04] #50759.1, 72612.0 ]
    configdict["pred_Signal_BDTG1"]  = [1.5058e+04] #7535.40, 11114.0 ]
    configdict["pred_Signal_BDTG2"]  = [2.9567e+04] #16994.0, 24484.0 ]
    configdict["pred_Signal_BDTG3"]  = [3.2828e+04]  #22784.0, 32338.0 ]
    configdict["pred_Signal_BDTGC"]  = [7.2251e+04] #[7.1847e+04]  #44781.0, 64314.0 ]
    
    configdict["pred_BDK_BDTGA"]  = 1825 #8.9742e+03  #2282.0 #867.0 #137.0
    configdict["pred_BDK_BDTGC"]  = 1723 #2147.0*0.65 #1.1117e+04 #8.3639e+03   #2147.0 #820.0 #130.0
    configdict["pred_BDK_BDTG1"]  = 322  #420.0*0.65 #2.2098e+03   #420.0 #153.0 #24.0
    configdict["pred_BDK_BDTG2"]  = 686  #867.0*0.65 #3.8441e+03   #867.0 #52.0
    configdict["pred_BDK_BDTG3"]  = 824  #391.0*0.65 #3.3455e+03   #1003.0 # 391.0 #63.0
    
    configdict["pred_BsDsPi_BDTG1"]  = [2.4826e+02]
    configdict["pred_BsDsPi_BDTG2"]  = [1.9868e+03]
    configdict["pred_BsDsPi_BDTG3"]  = [1.2095e+03]
    configdict["pred_BsDsPi_BDTGA"]  = [4.2436e+03]
    configdict["pred_BsDsPi_BDTGC"]  = [6.5538e+03] #[3.9347e+03]
    
    configdict["pred_LbLcPi_BDTG1"]  = [1.0806e+03]
    configdict["pred_LbLcPi_BDTG2"]  = [1.8438e+03]
    configdict["pred_LbLcPi_BDTG3"]  = [1.7210e+03]
    configdict["pred_LbLcPi_BDTGA"]  = [4.4624e+03]
    configdict["pred_LbLcPi_BDTGC"]  = [6.5283e+03] # [4.1374e+03]

    configdict["pred_BDRho_BDTG1"]  = [7.6560e+03]
    configdict["pred_BDRho_BDTG2"]  = [1.6675e+04]
    configdict["pred_BDRho_BDTG3"]  = [1.2957e+04]
    configdict["pred_BDRho_BDTGA"]  = [4.2518e+04]
    configdict["pred_BDRho_BDTGC"]  = [4.5996e+04] #[3.9052e+04]
    
    configdict["pred_BDstPi_BDTG1"]  = [6.7107e+03]
    configdict["pred_BDstPi_BDTG2"]  = [1.0622e+04]
    configdict["pred_BDstPi_BDTG3"]  = [8.8481e+03]
    configdict["pred_BDstPi_BDTGA"]  = [1.9336e+04]
    configdict["pred_BDstPi_BDTGC"]  = [1.5920e+04] #[1.8307e+04]

    configdict["pred_Comb_BDTG1"]  = [1.5058e+04]
    configdict["pred_Comb_BDTG2"]  = [2.9243e+03]
    configdict["pred_Comb_BDTG3"]  = [4.8894e+02]
    configdict["pred_Comb_BDTGA"]  = [2.0933e+04]
    configdict["pred_Comb_BDTGC"]  = [2.0566e+04] #[1.1412e+04]
    
    
    return configdict
