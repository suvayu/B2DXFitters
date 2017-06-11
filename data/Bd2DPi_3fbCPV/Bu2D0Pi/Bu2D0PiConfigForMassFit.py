from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    import ROOT
    from ROOT import *

    happystar = "#lower[-0.65]{#scale[0.6]{*}}"

    configdict["Decay"] = "Bu2D0Pi"
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5000,    6000    ],
                                                      "Name"                   : "BeautyMass",
                                                      "InputName"              : "lab0_MM"}

    configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1904    ],
                                                      "Name"                   : "CharmMass",
                                                      "InputName"              : "lab2_MM"}

    configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.0002,     0.015    ],
                                                      "Bins"                   : 40,
                                                      "Name"                   : "BeautyTime",
                                                      "InputName"              : "lab0_TAU"}
    
    configdict["BasicVariables"]["BacP"]          = { "Range"                  : [2000.0,  650000.0],
                                                      "Name"                   : "BacP",
                                                      "InputName"              : "lab1_P"}

    configdict["BasicVariables"]["BacPT"]         = { "Range"                  : [400.0,   45000.0 ],
                                                      "Name"                   : "BacPT",
                                                      "InputName"              : "lab1_PT"}

    configdict["BasicVariables"]["BacPIDK"]       = { "Range"                  : [-999.0, 999.0     ],
                                                      "Name"                   : "BacPIDK",
                                                      "InputName"              : "lab1_PIDKcorr"}

    configdict["BasicVariables"]["nTracks"]       = { "Range"                  : [15.0,    1000.0  ],
                                                      "Name"                   : "nTracks",
                                                      "InputName"              : "nTracks"}

    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range"                  : [0.00001,    0.0001     ],
                                                      "Name"                   : "BeautyTimeErr",
                                                      "InputName"              : "lab0_TAUERR"}

    configdict["BasicVariables"]["BacCharge"]     = { "Range"                  : [-1000.0, 1000.0  ],
                                                      "Name"                   : "BacCharge",
                                                      "InputName"              : "lab1_ID"}

    #PDF for each fitted component
    #Structure: decay->hypo->observable
    configdict["pdfList"] = {}
    #
    configdict["pdfList"]["Signal"] = {}
    configdict["pdfList"]["Signal"]["Bu2D0Pi"] = {}
    configdict["pdfList"]["Signal"]["Bu2D0Pi"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                                 "Title"      : "B_{u}#rightarrowD^{0}#pi",
                                                                 "Bins"       : 130,
                                                                 "Min"        : 5190.0,
                                                                 "Max"        : 5450.0,
                                                                 "Unit"       : "MeV/c^{2}",
                                                                 "mean"       : [5280,5200,5350],
                                                                 "sigma"      : [25.0,1.0,100.0],
                                                                 "zeta"       : [0.0],
                                                                 "fb"         : [0.0],
                                                                 "l"          : [-2.0,-5.0,-0.01],
                                                                 "a1"         : [3.0,0.01,6.0],
                                                                 "a2"         : [3.0,0.01,6.0],
                                                                 "n1"         : [3.0,0.01,6.0],
                                                                 "n2"         : [3.0,0.01,6.0]}
    configdict["pdfList"]["Signal"]["Bu2D0K"] = {}
    configdict["pdfList"]["Signal"]["Bu2D0K"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                                "Title"      : "B_{u}#rightarrowD^{0}#pi",
                                                                "Bins"       : 50,
                                                                "Min"        : 5200.0,
                                                                "Max"        : 5600.0,
                                                                "Unit"       : "MeV/c^{2}",
                                                                "mean"       : [5.3265e+03,5300.0,5400.0],
                                                                "sigma"      : [2.1556e+01,10.0,50.0],
                                                                "zeta"       : [0.0],
                                                                "fb"         : [0.0],
                                                                "l"          : [-6.9977e+00,-9.0,-5.0],
                                                                "a1"         : [3.0,0.0,6.0],
                                                                "a2"         : [3.0,0.0,6.0],
                                                                "n1"         : [3.0,0.0,6.0],
                                                                "n2"         : [3.0,0.0,6.0]}
    #
    configdict["pdfList"]["Bu2D0K"] = {}
    configdict["pdfList"]["Bu2D0K"]["Bu2D0Pi"] = {}
    configdict["pdfList"]["Bu2D0K"]["Bu2D0Pi"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                                 "Title"      : "B_{u}#rightarrowD^{0}K",
                                                                 "Bins"       : 82,
                                                                 "Min"        : 5090.0,
                                                                 "Max"        : 5500.0,
                                                                 "Unit"       : "MeV/c^{2}",
                                                                 "mean"       : [5239.0,5200.0,5250.0],
                                                                 "sigma"      : [26.3,10.0,50.0],
                                                                 "zeta"       : [0.0],
                                                                 "fb"         : [0.0],
                                                                 "l"          : [-28.0,-35.0,-25.0],
                                                                 "a1"         : [0.96,0.01,5.0],
                                                                 "a2"         : [1.23,0.01,5.0],
                                                                 "n1"         : [3.5,0.01,5.0],
                                                                 "n2"         : [10.0,0.01,15.0]}
    configdict["pdfList"]["Bu2D0K"]["Bu2D0K"] = {}
    configdict["pdfList"]["Bu2D0K"]["Bu2D0K"]["BeautyMass"] = { "PDF"        : "Ipatia",
                                                                "Title"      : "B_{u}#rightarrowD^{0}K",
                                                                "Bins"       : 80,
                                                                "Min"        : 5100.0,#5200.0,
                                                                "Max"        : 5500.0,#5380.0,
                                                                "Unit"       : "MeV/c^{2}",
                                                                "mean"       : [5280.0,5200.0,5350.0],
                                                                "sigma"      : [17.0,5.0,50.0],
                                                                "zeta"       : [0.0],
                                                                "fb"         : [0.0],
                                                                "l"          : [-3.6,-15.0,-0.01],
                                                                "a1"         : [2.6,1.0,10.0],
                                                                "a2"         : [1e+09],
                                                                "n1"         : [0.95,0.001,15.0],
                                                                "n2"         : [0.0]}
    #
    configdict["pdfList"]["Bd2D0PiPi"] = {}
    configdict["pdfList"]["Bd2D0PiPi"]["Bu2D0Pi"] = {}
    configdict["pdfList"]["Bd2D0PiPi"]["Bu2D0Pi"]["BeautyMass"] = {"PDF"        : "CrystalBallPlusGaussian",
                                                                   "Title"      : "B_{d}#rightarrowD^{0}#pi#pi",
                                                                   "Bins"       : 100,
                                                                   "Min"        : 5090.0,
                                                                   "Max"        : 5500.0,
                                                                   "Unit"       : "MeV/c^{2}",
                                                                   "shiftMean"  : False,
                                                                   "mean"       : [5100.92,5000.0,5200.0],
                                                                   "alpha"      : [-2.181,-10.0,10.0],
                                                                   "n"          : [1.08,0.0,10.0],
                                                                   "sigmaCB"    : [26.59,1.0,100.0],
                                                                   "sigmaG"     : [25.0,1.0,100.0],
                                                                   "fracG"      : [0.5,0.1,0.9]}
    configdict["pdfList"]["Bd2D0PiPi"]["Bu2D0K"] = {}
    configdict["pdfList"]["Bd2D0PiPi"]["Bu2D0K"]["BeautyMass"] = {"PDF"        : "CrystalBallPlusGaussian",
                                                                  "Title"      : "B_{d}#rightarrowD^{0}#pi#pi",
                                                                  "Bins"       : 100,
                                                                  "Min"        : 5090.0,
                                                                  "Max"        : 5500.0,
                                                                  "Unit"       : "MeV/c^{2}",
                                                                  "shiftMean"  : False,
                                                                  "mean"       : [5100.92,5000.0,5200.0],
                                                                  "alpha"      : [-2.181,-10.0,10.0],
                                                                  "n"          : [1.08,0.0,10.0],
                                                                  "sigmaCB"    : [26.59,1.0,100.0],
                                                                  "sigmaG"     : [25.0,1.0,100.0],
                                                                  "fracG"      : [0.5,0.1,0.9]}
    #
    configdict["pdfList"]["Bu2Dst0Pi"] = {}
    configdict["pdfList"]["Bu2Dst0Pi"]["Bu2D0Pi"] = {}
    configdict["pdfList"]["Bu2Dst0Pi"]["Bu2D0Pi"]["BeautyMass"] = {"PDF"        : "CrystalBallPlusGaussian",
                                                                   "Title"      : "B_{u}#rightarrowD"+happystar+"^{0}#pi",
                                                                   "Bins"       : 100,
                                                                   "Min"        : 5090.0,
                                                                   "Max"        : 5500.0,
                                                                   "Unit"       : "MeV/c^{2}",
                                                                   "shiftMean"  : False,
                                                                   "mean"       : [5100.92,5000.0,5200.0],
                                                                   "alpha"      : [-2.181,-10.0,10.0],
                                                                   "n"          : [1.08,0.0,10.0],
                                                                   "sigmaCB"    : [26.59,1.0,100.0],
                                                                   "sigmaG"     : [25.0,1.0,100.0],
                                                                   "fracG"      : [0.5,0.1,0.9]}
    configdict["pdfList"]["Bu2Dst0Pi"]["Bu2D0K"] = {}
    configdict["pdfList"]["Bu2Dst0Pi"]["Bu2D0K"]["BeautyMass"] = {"PDF"        : "CrystalBall",
                                                                  "Title"      : "B_{u}#rightarrowD"+happystar+"^{0}#pi",
                                                                  "Bins"       : 50,
                                                                  "Min"        : 5090.0,
                                                                  "Max"        : 5500.0,
                                                                  "Unit"       : "MeV/c^{2}",
                                                                  "shiftMean"  : False,
                                                                  "mean"       : [5100.92,5000.0,5200.0],
                                                                  "alpha"      : [-2.181,-10.0,10.0],
                                                                  "n"          : [1.08,0.0,10.0],
                                                                  "sigma"      : [26.59,1.0,100]}
    #
    configdict["pdfList"]["Bs2D0KPi"] = {}
    configdict["pdfList"]["Bs2D0KPi"]["Bu2D0Pi"] = {}
    configdict["pdfList"]["Bs2D0KPi"]["Bu2D0Pi"]["BeautyMass"] = {"PDF"        : "JohnsonSU",
                                                                  "Title"      : "B_{s}#rightarrowD^{0}K#pi",
                                                                  "Bins"       : 100,
                                                                  "Min"        : 5090.0,
                                                                  "Max"        : 5500.0,
                                                                  "Unit"       : "MeV/c^{2}",
                                                                  "mean"       : [5100.92,5000.0,5200.0],
                                                                  "sigma"      : [600, 40.0, 1000.0],
                                                                  "nu"         : [-1.9084e+00, -10.8, -1.3],
                                                                  "tau"        : [1.3406e+00, 0.7, 1.8]}
    configdict["pdfList"]["Bs2D0KPi"]["Bu2D0K"] = {}
    configdict["pdfList"]["Bs2D0KPi"]["Bu2D0K"]["BeautyMass"] = {"PDF"        : "JohnsonSU",
                                                                 "Title"      : "B_{s}#rightarrowD^{0}K#pi",
                                                                 "Bins"       : 100,
                                                                 "Min"        : 5090.0,
                                                                 "Max"        : 5500.0,
                                                                 "Unit"       : "MeV/c^{2}",
                                                                 "mean"       : [5100.92,5000.0,5200.0],
                                                                 "sigma"      : [600, 40.0, 1000.0],
                                                                 "nu"         : [-1.9084e+00, -10.8, -1.3],
                                                                 "tau"        : [1.3406e+00, 0.7, 1.8]}

    #Dataset prefix
    configdict["dataSetPrefix"] = {"Signal"   : "dataSetMC_Bu2D0Pi_",
                                   "Bu2D0K"    : "dataSetMC_Bu2D0K_",
                                   "Bd2D0PiPi" : "dataSetMC_Bd2D0PiPi_",
                                   "Bu2Dst0Pi" : "dataSetMC_Bu2Dst0Pi_",
                                   "Bs2D0KPi"  : "dataSetMC_Bs2D0KPi_"}
    #Axes titles
    configdict["AxisTitle"] = {"BeautyMass": {"Bu2D0Pi":"D^{0}#pi mass (MeV/c^{2})","Bu2D0K":"D^{0}K mass (MeV/c^{2})"}}
    
    return configdict
