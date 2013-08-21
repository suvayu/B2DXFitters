def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    configdict["lumRatio"] =  0.44/(0.59+0.44)

    configdict["BDPi_BDTGA_sigma1"]  = [6.0109]
    configdict["BDPi_BDTGA_sigma2"]  = [11.710]
    configdict["BDPi_BDTGA_n1"]      = [0.3688]
    configdict["BDPi_BDTGA_n2"]      = [1.0265]
    configdict["BDPi_BDTGA_alpha1"]  = [2.5717]
    configdict["BDPi_BDTGA_alpha2"]  = [-2.3337]
    configdict["BDPi_BDTGA_frac"]    = [0.71173]

    configdict["BDPi_BDTGC_sigma1"]  = [5.9603]
    configdict["BDPi_BDTGC_sigma2"]  = [11.173]
    configdict["BDPi_BDTGC_n1"]      = [0.40491]
    configdict["BDPi_BDTGC_n2"]      = [1.9933]
    configdict["BDPi_BDTGC_alpha1"]  = [2.5190]
    configdict["BDPi_BDTGC_alpha2"]  = [-2.1635]
    configdict["BDPi_BDTGC_frac"]    = [0.6900]

    configdict["BDPi_BDTG1_sigma1"]  = [6.4114]
    configdict["BDPi_BDTG1_sigma2"]  = [16.149]
    configdict["BDPi_BDTG1_n1"]      = [0.38134]
    configdict["BDPi_BDTG1_n2"]      = [63.803]
    configdict["BDPi_BDTG1_alpha1"]  = [2.6933]
    configdict["BDPi_BDTG1_alpha2"]  = [-1.4621]
    configdict["BDPi_BDTG1_frac"]    = [0.76487]
    
    configdict["BDPi_BDTG2_sigma1"]  = [6.0938]
    configdict["BDPi_BDTG2_sigma2"]  = [12.387]
    configdict["BDPi_BDTG2_n1"]      = [0.96396]
    configdict["BDPi_BDTG2_n2"]      = [0.00022]
    configdict["BDPi_BDTG2_alpha1"]  = [2.2139]
    configdict["BDPi_BDTG2_alpha2"]  = [-2.7515]
    configdict["BDPi_BDTG2_frac"]    = [0.72605]
                            
    configdict["BDPi_BDTG3_sigma1"]  = [6.6574]
    configdict["BDPi_BDTG3_sigma2"]  = [6.3242]
    configdict["BDPi_BDTG3_n1"]      = [6.1752]
    configdict["BDPi_BDTG3_n2"]      = [24.887]
    configdict["BDPi_BDTG3_alpha1"]  = [0.94966]
    configdict["BDPi_BDTG3_alpha2"]  = [-1.2567]
    configdict["BDPi_BDTG3_frac"]    = [0.37238]

    ################################################

    # 1: nonres, 2: phipi, 3: kstk, 4: kpipi,  5: pipipi
    configdict["BsDsPi_BDTGA_sigma1"]  = [4.8865,   5.0649,  5.4377,  5.8510,  5.5906]
    configdict["BsDsPi_BDTGA_sigma2"]  = [5.0645,   5.5344,  5.3877,  10.180,  10.073]
    configdict["BsDsPi_BDTGA_n1"]      = [50.000,   4.0702,  49.999,  0.0262,  0.2633]
    configdict["BsDsPi_BDTGA_n2"]      = [50.000,   10.643,  50.000,  1.9293,  8.6233]
    configdict["BsDsPi_BDTGA_alpha1"]  = [0.51973,  1.1934,  0.7734,  2.8195,  1.9343]
    configdict["BsDsPi_BDTGA_alpha2"]  = [-0.9908,  -1.1806, -1.1424, -2.2422  -1.7027]
    configdict["BsDsPi_BDTGA_frac"]    = [0.25406,  0.48465, 0.32864, 0.59958, 0.27873]
 
    configdict["BsDsPi_BDTGC_sigma1"]  = [4.9030,   4.9945,  6.8707,  9.3307,  14.424]
    configdict["BsDsPi_BDTGC_sigma2"]  = [5.1357,   5.0709,  4.5046,  5.4919,  7.3471]
    configdict["BsDsPi_BDTGC_n1"]      = [50.000,   49.999,  4.8458,  2.1616,  24.986]
    configdict["BsDsPi_BDTGC_n2"]      = [50.000,   50.000,  3.2652,  0.2775,  24.669]
    configdict["BsDsPi_BDTGC_alpha1"]  = [0.49086,  0.7512,  1.6112,  1.7168,  1.2159]
    configdict["BsDsPi_BDTGC_alpha2"]  = [-1.0601,  -1.0394, -1.7284, -2.9551, -4.7400] 
    configdict["BsDsPi_BDTGC_frac"]    = [0.21960,  0.36831, 0.54688, 0.52642, 0.34507]

    configdict["BsDsPi_BDTG1_sigma1"]  = [7.0832,   5.4681,   6.0124,  6.5995,  2.8947]
    configdict["BsDsPi_BDTG1_sigma2"]  = [3.2356,   15.432,  16.595,  17.449,  9.5773]
    configdict["BsDsPi_BDTG1_n1"]      = [0.5455,   49.999,   50.000,  50.000,  2.2711]
    configdict["BsDsPi_BDTG1_n2"]      = [0.78065,  50.000,  50.000,  50.000,  1.0715] 
    configdict["BsDsPi_BDTG1_alpha1"]  = [1.9073,   5.2509,  4.0954,  3.6512,  0.3121]
    configdict["BsDsPi_BDTG1_alpha2"]  = [-1.4766,  -2.2031, -1.6372, -1.8242, -2.0500]
    configdict["BsDsPi_BDTG1_frac"]    = [0.71417,  0.8256,  0.86570, 0.77958, 0.2402]

    configdict["BsDsPi_BDTG2_sigma1"]  = [4.3706,   4.1764,  5.6643,  5.7021,  14.086]
    configdict["BsDsPi_BDTG2_sigma2"]  = [5.1808,   7.4918,  7.1832,  9.7796,  7.3518] 
    configdict["BsDsPi_BDTG2_n1"]      = [49.999,   0.6986,  1.5631,  0.0009,  24.980]                                          
    configdict["BsDsPi_BDTG2_n2"]      = [50.000,   4.2868,  49.999,  1.2731,  16.636]
    configdict["BsDsPi_BDTG2_alpha1"]  = [3.9557,   2.1992,  2.0148,  2.7484,  1.1540]
    configdict["BsDsPi_BDTG2_alpha2"]  = [-0.9993,  -1.7834, -0.9324, -2.3461, -6.2458]
    configdict["BsDsPi_BDTG2_frac"]    = [0.19321,  0.4411,  0.81112, 0.52045, 0.38730]

    configdict["BsDsPi_BDTG3_sigma1"]  = [12.019,   12.262,  6.8707,  6.7809,  5.6922]
    configdict["BsDsPi_BDTG3_sigma2"]  = [5.3351,   5.1593,  4.5046,  6.4308,  9.8748]
    configdict["BsDsPi_BDTG3_n1"]      = [49.999,   49.931,  4.8458,  13.365,  0.6453]
    configdict["BsDsPi_BDTG3_n2"]      = [12.005,   17.454,  3.2652,  50.000,  25.000]
    configdict["BsDsPi_BDTG3_alpha1"]  = [1.0735,   1.4434,  1.6112,  0.8697,  1.7332] 
    configdict["BsDsPi_BDTG3_alpha2"]  = [-5.4194,  -6.9800, -1.7284, -1.2763,  -1.6537]
    configdict["BsDsPi_BDTG3_frac"]    = [0.14123,  0.14596, 0.54688, 0.34600,  0.31166]
                            

    ################################################
    # 1: nonres, 2: phipi, 3: kstk, 4: kpipi,  5: pipipi
    
    configdict["BsDsK_BDTGA_sigma1"]  = [7.6072,  12.365,  7.2695,  5.6933,  7.1100]
    configdict["BsDsK_BDTGA_sigma2"]  = [4.2208,  5.1626,  4.3215,  10.246,  13.122]
    configdict["BsDsK_BDTGA_n1"]      = [1.9454,  1.6567,  4.9069,  0.0001,  0.5686]
    configdict["BsDsK_BDTGA_n2"]      = [0.4889,  46.494,  1.5736,  0.3507,  0.9733]
    configdict["BsDsK_BDTGA_alpha1"]  = [1.8268,  1.6222,  1.6434,  2.8423,  2.1959]
    configdict["BsDsK_BDTGA_alpha2"]  = [-2.5602, -6.2415, -2.0514, -2.6759, -2.3791]
    configdict["BsDsK_BDTGA_frac"]    = [0.53155, 0.19015, 0.57295, 0.58468, 0.63449]
                            
    configdict["BsDsK_BDTGC_sigma1"]  = [4.5318,  12.165,  7.2651,  9.1278,  7.0233]
    configdict["BsDsK_BDTGC_sigma2"]  = [8.5477,  5.1476,  4.3446,  5.2328,  12.854]
    configdict["BsDsK_BDTGC_n1"]      = [0.0003,  1.5183,  5.1154,  1.4139,  0.4679]
    configdict["BsDsK_BDTGC_n2"]      = [0.7323,  48.812,  1.7394,  0.4224,  0.7075]
    configdict["BsDsK_BDTGC_alpha1"]  = [3.0861,  1.6409,  1.6323,  1.8280,  2.2457]
    configdict["BsDsK_BDTGC_alpha2"]  = [-2.3834, -4.7983, -2.0242, -2.7475, -2.4535] 
    configdict["BsDsK_BDTGC_frac"]    = [0.59582, 0.19160, 0.56708, 0.57017, 0.61692]

    configdict["BsDsK_BDTG1_sigma1"]  = [4.7411,  2.5361,  7.3631,  6.8733,  7.5586]
    configdict["BsDsK_BDTG1_sigma2"]  = [10.842,  6.1485,  3.5137,  17.960,  14.724]
    configdict["BsDsK_BDTG1_n1"]      = [0.0001,  0.6575,  0.7693,  4.9808,  0.0002] 
    configdict["BsDsK_BDTG1_n2"]      = [0.0001,  3.9486,  1.7064,  10.647,  1.2687]
    configdict["BsDsK_BDTG1_alpha1"]  = [2.8086,  1.1802,  2.2427,  4.4696,  2.8327]
    configdict["BsDsK_BDTG1_alpha2"]  = [-2.4221, -1.6223, -1.4475, -3.4591, -2.1168]
    configdict["BsDsK_BDTG1_frac"]    = [0.64972, 0.15555, 0.62754, 0.80417, 0.63724]

    configdict["BsDsK_BDTG2_sigma1"]  = [3.0188,  4.6249,  6.6413,  4.8833,  7.1645]
    configdict["BsDsK_BDTG2_sigma2"]  = [6.8363,  8.9847,  4.7140,  8.6363,  12.931]
    configdict["BsDsK_BDTG2_n1"]      = [0.2647,  0.1050,  19.794,  0.0726,  0.3197]
    configdict["BsDsK_BDTG2_n2"]      = [1.4626,  2.7599,  4.3085,  2.6879,  0.5377]
    configdict["BsDsK_BDTG2_alpha1"]  = [2.2347,  2.8112,  1.0685,  2.4116,  2.2429]
    configdict["BsDsK_BDTG2_alpha2"]  = [-2.1451, -2.0557, -1.4100, -2.1357, -2.4206]
    configdict["BsDsK_BDTG2_frac"]    = [0.19892, 0.62386, 0.50402, 0.33139, 0.61798]

    configdict["BsDsK_BDTG3_sigma1"]  = [7.4064,  5.3325,  10.906,  12.906,  8.2026]    
    configdict["BsDsK_BDTG3_sigma2"]  = [4.1307,  4.9137,  5.3241,  6.3213,  7.2805]
    configdict["BsDsK_BDTG3_n1"]      = [4.0476,  5.9400,  0.0001,  49.940,  25.000]
    configdict["BsDsK_BDTG3_n2"]      = [0.7406,  49.986,  23.600,  49.994,  25.000]
    configdict["BsDsK_BDTG3_alpha1"]  = [1.7264,  1.2324,  2.6912,  0.86509, 0.8462]
    configdict["BsDsK_BDTG3_alpha2"]  = [-2.7109, -0.9240, -5.1596, -1.8347, -1.0673]
    configdict["BsDsK_BDTG3_frac"]    = [0.50116, 0.59858, 0.18356, 0.17298, 0.50178]
    

    return configdict
