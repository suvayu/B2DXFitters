from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log

    # PrefixID's: all the following fields are mandatory (choose either ID or newID for each particle)
    # The number of Bachelors, Charm particles and Charm children is flexible
    configdict["Charm1ChildrenPrefix"] = { "Child1"   : {"Name": "lab3",
                                                         "ID": "K",
                                                         "Type": "D"},

                                           "Child2"   : {"Name": "lab4",
                                                         "ID": "Pi",
                                                         "Type": "D"},
                                           }
    
    configdict["BeautyChildrenPrefix"] = { "Bachelor1" : {"Name": "lab1",
                                                          "newID": "K",
                                                          "Type": "D"},
                                           
                                           "Charm1"    : {"Name": "lab2",
                                                          "ID": "D0",
                                                          "Type": "D"}
                                           }
    
    configdict["BeautyPrefix"] = { "Name": "lab0",
                                   "Type": "D"}

    # Handle multiple candidates (if any). Comment out if not needed
    #configdict["Index"] = "nPV"

    #Additional "pedix" in the branch name. Leave "" if not pedix is required
    configdict["Pedix"] = ""

    #Mass name pedix (M, MM etc...)
    configdict["MassPedix"] = "_MM"
    
    return configdict
