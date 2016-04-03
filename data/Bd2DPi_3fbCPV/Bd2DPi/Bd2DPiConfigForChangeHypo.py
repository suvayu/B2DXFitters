from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # PrefixID's: all the following fields are mandatory (choose either ID or newID for each particle)
    # The number of Bachelors, Charm particles and Charm children is flexible
    configdict["Charm1ChildrenPrefix"] = { "Child1"   : {"Name": "lab0_FitDaughtersPVConst_Dplus_P0",
                                                         "ID": "K"},

                                           "Child2"   : {"Name": "lab0_FitDaughtersPVConst_Dplus_P1",
                                                         "ID": "Pi"},

                                           "Child3"   : {"Name": "lab0_FitDaughtersPVConst_Dplus_P2",
                                                         "ID": "Pi"}
                                           }
    
    configdict["BeautyChildrenPrefix"] = { "Bachelor1" : {"Name": "lab0_FitDaughtersPVConst_P0",
                                                          "newID": "K"},
                                           
                                           "Charm1"    : {"Name": "lab0_FitDaughtersPVConst_Dplus",
                                                          "ID": "D"}
                                           }
    
    configdict["BeautyPrefix"] = { "Name": "lab0_FitDaughtersPVConst" }

    # Handle multiple candidates (if any). Comment out if not needed
    # configdict["Index"] = "lab0_FitDaughtersPVConst_nPV"

    #Additional "_pedix" in the branch name. Leave "" in not pedix is required
    configdict["Pedix"] = "_flat"
    
    return configdict
