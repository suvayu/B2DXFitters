from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # PrefixID's: all the following fields are mandatory (choose either ID or newID for each particle)
    # The number of Bachelors, Charm particles and Charm children is flexible
    configdict["Charm1ChildrenPrefix"] = { "Child1"   : {"Name": "lab0_FitDaughtersConst_Dplus_P0",
                                                         "ID": "K"},

                                           "Child2"   : {"Name": "lab0_FitDaughtersConst_Dplus_P1",
                                                         "ID": "Pi"},

                                           "Child3"   : {"Name": "lab0_FitDaughtersConst_Dplus_P2",
                                                         "ID": "Pi"}
                                           }
    
    configdict["BeautyChildrenPrefix"] = { "Bachelor1" : {"Name": "lab0_FitDaughtersConst_P0",
                                                          "newID": "K"},
                                           
                                           "Charm1"    : {"Name": "lab0_FitDaughtersConst_Dplus",
                                                          "ID": "D"}
                                           }
    
    configdict["BeautyPrefix"] = { "Name": "lab0_FitDaughtersConst" }

    # Handle multiple candidates (if any). Comment out if not needed
    #configdict["Index"] = "lab0_FitDaughtersConst_nPV"

    #Additional "_pedix" in the branch name. Leave "" if not pedix is required
    configdict["Pedix"] = "_flat"

    #Mass name pedix (_M, _MM etc...)
    configdict["MassPedix"] = "_M"
    
    return configdict
