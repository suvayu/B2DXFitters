#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78:expandtab
# --------------------------------------------------------------------------- 
# @file ChangeMassHypo.py
#
# @brief Change mass hypothesys for one or more particles in the decay,
#        and store resulting tree in a new file
#
# @author Vincenzo Battista
# @date 2016-02-25
#
# --------------------------------------------------------------------------- 
# This file is used as both a shell script and as a Python script.
""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.

# make sure the environment is set up properly
if test -n "$CMTCONFIG" \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersDict.so \
     -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersLib.so; then
    # all ok, software environment set up correctly, so don't need to do 
    # anything
    true
else
    if test -n "$CMTCONFIG"; then
    # clean up incomplete LHCb software environment so we can run
    # standalone
        echo Cleaning up incomplete LHCb software environment.
        PYTHONPATH=`echo $PYTHONPATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export PYTHONPATH
        LD_LIBRARY_PATH=`echo $LD_LIBRARY_PATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export LD_LIBRARY_PATH
        exec env -u CMTCONFIG -u B2DXFITTERSROOT "$0" "$@"
    fi
    # automatic set up in standalone build mode
    if test -z "$B2DXFITTERSROOT"; then
        cwd="$(pwd)"
        # try to find from where script is executed, use current directory as
        # fallback
        tmp="$(dirname $0)"
        tmp=${tmp:-"$cwd"}
        # convert to absolute path
        tmp=`readlink -f "$tmp"`
        # move up until standalone/setup.sh found, or root reached
        while test \( \! -d "$tmp"/standalone \) -a -n "$tmp" -a "$tmp"\!="/"; do
            tmp=`dirname "$tmp"`
        done
        if test -d "$tmp"/standalone; then
            cd "$tmp"/standalone
            . ./setup.sh
        else
            echo `basename $0`: Unable to locate standalone/setup.sh
            exit 1
        fi
        cd "$cwd"
        unset tmp
        unset cwd
    fi
fi

# figure out which custom allocators are available
# prefer jemalloc over tcmalloc
for i in libjemalloc libtcmalloc; do
    for j in `echo "$LD_LIBRARY_PATH" | tr ':' ' '` \
        /usr/local/lib /usr/lib /lib; do
        for k in `find "$j" -name "$i"'*.so.?' | sort -r`; do
            if test \! -e "$k"; then
            continue
        fi
        echo adding $k to LD_PRELOAD
        if test -z "$LD_PRELOAD"; then
            export LD_PRELOAD="$k"
            break 3
        else
            export LD_PRELOAD="$LD_PRELOAD":"$k"
            break 3
        fi
    done
    done
done

# set batch scheduling (if schedtool is available)
schedtool="`which schedtool 2>/dev/zero`"
if test -n "$schedtool" -a -x "$schedtool"; then
    echo "enabling batch scheduling for this job (schedtool -B)"
    schedtool="$schedtool -B -e"
else
    schedtool=""
fi

# set ulimit to protect against bugs which crash the machine: 3G vmem max,
# no more then 8M stack
ulimit -v $((3072 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O "$0" - "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
#"
import B2DXFitters
import ROOT

from B2DXFitters import *
from ROOT import *

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc

import array
from array import array

gROOT.SetBatch()

#------------------------------------------------------------------------------
def GetMass(particle):

    if particle in ['Pi','pi']:
        return 139.57018
    elif particle in ['Pi0','pi0']:
        return 134.9766
    elif particle in ['K','k']:
        return 493.677
    elif particle in ['D','d']:
        return 1869.61
    elif particle in ['Ds','ds']:
        return 1968.30
    elif particle in ['D0','d0']:
        return 1864.84
    else:
        print "ERROR: particle "+particle+" unknown"
        exit(-1)
        
#------------------------------------------------------------------------------
def CreateMassDictionary(configfile, debug):

    massDict = {}

    #Loop over Beauty children
    for bchild in configfile["BeautyChildrenPrefix"].iterkeys():
        name = configfile["BeautyChildrenPrefix"][bchild]["Name"]
        if 'newID' in configfile["BeautyChildrenPrefix"][bchild].keys():
            particle = configfile["BeautyChildrenPrefix"][bchild]['newID']
        elif 'ID' in configfile["BeautyChildrenPrefix"][bchild].keys():
            particle = configfile["BeautyChildrenPrefix"][bchild]['ID']
        else:
            print "ERROR: particle "+name+" doesn't have a specified ID. Please check your config file"
            exit(-1)
        mass = GetMass(particle)
        massDict[name] = {}
        massDict[name] = mass
            
        if 'Charm' in bchild:
            #Loop over Charm(s) children
            for cchild in configfile[bchild+"ChildrenPrefix"].iterkeys():
                name = configfile[bchild+"ChildrenPrefix"][cchild]["Name"]
                if 'newID' in configfile[bchild+"ChildrenPrefix"][cchild].keys():
                    particle = configfile[bchild+"ChildrenPrefix"][cchild]['newID']
                elif 'ID' in configfile[bchild+"ChildrenPrefix"][cchild].keys():
                    particle = configfile[bchild+"ChildrenPrefix"][cchild]['ID']
                else:
                    print "ERROR: particle "+name+" doesn't have a specified ID. Please check your config file"
                    exit(-1)
                mass = GetMass(particle)
                massDict[name] = {}
                massDict[name] = mass
                    
    if debug:
        print "Mass dictionary:"
        print massDict
        
    return massDict

#------------------------------------------------------------------------------
def ChangeBranchStatus(tree,configfile,status,debug):
    debugDict = []

    #Change (at least) Beauty mass
    tree.SetBranchStatus(configfile["BeautyPrefix"]["Name"]+'_M'+configfile["Pedix"],status)
    debugDict.append(configfile["BeautyPrefix"]["Name"]+'_M'+configfile["Pedix"])

    #Loop over Beauty children
    for bchild in configfile["BeautyChildrenPrefix"].iterkeys():
        #Change Charm mass if required (updating Charm children are detected)
        if 'Charm' in bchild:
            for cchild in configfile[bchild+'ChildrenPrefix'].iterkeys():
                if 'newID' in configfile[bchild+'ChildrenPrefix'][cchild].keys():
                    tree.SetBranchStatus(configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_M'+configfile["Pedix"],status)
                    debugDict.append(configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_M'+configfile["Pedix"])
                    break

    if debug:
        print "Tree "+str(tree.GetName())+"; changed status of following branches to "+str(status)+":"
        for br in debugDict:
            print br
        
    return tree

#------------------------------------------------------------------------------ 
def CreateBranchDictionary(configfile,maxBcand,debug):
    #Take Beauty mass first
    branchDict={}
    branchDict[configfile["BeautyPrefix"]["Name"]]={}
    if 'Index' in configfile.keys():
        branchDict[configfile["BeautyPrefix"]["Name"]][configfile["BeautyPrefix"]["Index"]] = array('i',[0])
        branchDict[configfile["BeautyPrefix"]["Name"]][configfile["BeautyPrefix"]["Name"]+'_M'+configfile["Pedix"]] = array('f',maxBcand*[0])
    else:
        branchDict[configfile["BeautyPrefix"]["Name"]][configfile["BeautyPrefix"]["Name"]+'_M'+configfile["Pedix"]] = array('f',[0])
        
    #Then, Bachelor(s) momenta
    for bchild in configfile["BeautyChildrenPrefix"].iterkeys():
        if 'Bachelor' in bchild:
            branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]]={}
            if 'Index' in configfile.keys():
                branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_PX'+configfile["Pedix"]] = array('f',maxBcand*[0])
                branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_PY'+configfile["Pedix"]] = array('f',maxBcand*[0])
                branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_PZ'+configfile["Pedix"]] = array('f',maxBcand*[0])
            else:
                branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_PX'+configfile["Pedix"]] = array('f',[0])
                branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_PY'+configfile["Pedix"]] = array('f',[0])
                branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_PZ'+configfile["Pedix"]] = array('f',[0])

        #Then, Charm(s) children (if any)
        if 'Charm' in bchild:
            for cchild in configfile[bchild+'ChildrenPrefix'].iterkeys():
                if 'newID' in configfile[bchild+'ChildrenPrefix'][cchild].keys():
                    #Charm children detected; need to update Charm invariant mass as well
                    branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]]={}
                    if 'Index' in configfile.keys():
                        branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_M'+configfile["Pedix"]] = array('f',maxBcand*[0])
                    else:
                        branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_M'+configfile["Pedix"]] = array('f',[0])
                    break
            #Now take Charm children momenta
            for cchild in configfile[bchild+"ChildrenPrefix"].iterkeys():
                branchDict[configfile[bchild+"ChildrenPrefix"][cchild]["Name"]]={}
                if 'Index' in configfile.keys():
                    branchDict[configfile[bchild+"ChildrenPrefix"][cchild]["Name"]][configfile[bchild+"ChildrenPrefix"][cchild]["Name"]+'_PX'+configfile["Pedix"]] = array('f',maxBcand*[0])
                    branchDict[configfile[bchild+"ChildrenPrefix"][cchild]["Name"]][configfile[bchild+"ChildrenPrefix"][cchild]["Name"]+'_PY'+configfile["Pedix"]] = array('f',maxBcand*[0])
                    branchDict[configfile[bchild+"ChildrenPrefix"][cchild]["Name"]][configfile[bchild+"ChildrenPrefix"][cchild]["Name"]+'_PZ'+configfile["Pedix"]] = array('f',maxBcand*[0])
                else:
                    branchDict[configfile[bchild+"ChildrenPrefix"][cchild]["Name"]][configfile[bchild+"ChildrenPrefix"][cchild]["Name"]+'_PX'+configfile["Pedix"]] = array('f',[0])
                    branchDict[configfile[bchild+"ChildrenPrefix"][cchild]["Name"]][configfile[bchild+"ChildrenPrefix"][cchild]["Name"]+'_PY'+configfile["Pedix"]] = array('f',[0])
                    branchDict[configfile[bchild+"ChildrenPrefix"][cchild]["Name"]][configfile[bchild+"ChildrenPrefix"][cchild]["Name"]+'_PZ'+configfile["Pedix"]] = array('f',[0])
                

    if debug:
        print "Branch dictionary:"
        print branchDict
        
    return branchDict

#------------------------------------------------------------------------------
def SetAddress(tree, branchDict, configfile, debug):
    for lab in branchDict.iterkeys():
        for branch in branchDict[lab].iterkeys():
            tree.SetBranchAddress(branch, branchDict[lab][branch])
            if debug:
                print "Pointing "+str(branch)+" branch ("+str(tree.GetName())+") to the following address:"
                print branchDict[lab][branch]

    return tree

#------------------------------------------------------------------------------
def CreateBranches(tree,branchDict,configfile,debug):
    debugDict = []
    
    #Beauty mass
    if 'Index' in configfile["BeautyPrefix"].keys():
        brString = configfile["BeautyPrefix"]["Name"]+'_M'+configfile["Pedix"]+'['+configfile["BeautyPrefix"]["Index"]+']/F'
    else:
        brString = configfile["BeautyPrefix"]["Name"]+'_M'+configfile["Pedix"]+'/F'
        
    tree.Branch(configfile["BeautyPrefix"]["Name"]+'_M'+configfile["Pedix"],
                branchDict[configfile["BeautyPrefix"]["Name"]][configfile["BeautyPrefix"]["Name"]+'_M'+configfile["Pedix"]],
                brString)
    debugDict += [brString]
    
    #Loop over Beauty children
    for bchild in configfile["BeautyChildrenPrefix"].iterkeys():
        #Change Charm mass if required (Charm children are detected)
        if 'Charm' in bchild:
            for cchild in configfile[bchild+'ChildrenPrefix'].iterkeys():
                if 'newID' in configfile[bchild+'ChildrenPrefix'][cchild].keys():
                    if 'Index' in configfile["BeautyChildrenPrefix"][bchild].keys():
                        brString = configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_M'+configfile["Pedix"]+'['+configfile["BeautyPrefix"]["Index"]+']/F'
                    else:
                        brString = configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_M'+configfile["Pedix"]+'/F'
            
                    tree.Branch(configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_M'+configfile["Pedix"],
                                branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+'_M'+configfile["Pedix"]],
                                brString)
                    debugDict += [brString]
                    break
            
    if debug:
        print "Tree "+str(tree.GetName())+"; created following branches:"
        for br in debugDict:
            print br
            
    return tree

#------------------------------------------------------------------------------
def ComputeNewBMass(branchDict, massDict, nBCand, configfile):

    #Compute Beauty mass taking Charm(s) energy from its(their) daughter(s)

    PX=0.0
    PY=0.0
    PZ=0.0
    mass=0.0
    name=''

    #Loop over B candidates
    for bcand in range(0, nBCand):

        totPX=0.0
        totPY=0.0
        totPZ=0.0
        totE=0.0
        
        #Loop over B children
        for bchild in configfile["BeautyChildrenPrefix"].iterkeys():
            if 'Bachelor' in bchild:
                #Bachelor: take directly its energy/momentum
                name = configfile["BeautyChildrenPrefix"][bchild]["Name"]
                PX = branchDict[name][name+"_PX"+configfile["Pedix"]][bcand]
                PY = branchDict[name][name+"_PY"+configfile["Pedix"]][bcand]
                PZ = branchDict[name][name+"_PZ"+configfile["Pedix"]][bcand]
                mass = massDict[name]

                totPX = totPX + PX
                totPY = totPY + PY
                totPZ = totPZ + PZ
                totE = totE + TMath.Sqrt(PX*PX + PY*PY + PZ*PZ + mass*mass)
                
            else:
                #Charm: take Charm(s) children momenta/energies
                for cchild in configfile[bchild+"ChildrenPrefix"].iterkeys():
                    name = configfile[bchild+"ChildrenPrefix"][cchild]["Name"]
                    PX = branchDict[name][name+"_PX"+configfile["Pedix"]][bcand]
                    PY = branchDict[name][name+"_PY"+configfile["Pedix"]][bcand]
                    PZ = branchDict[name][name+"_PZ"+configfile["Pedix"]][bcand]    
                    mass = massDict[name]
                    
                    totPX = totPX + PX
                    totPY = totPY + PY
                    totPZ = totPZ + PZ
                    totE = totE + TMath.Sqrt(PX*PX + PY*PY + PZ*PZ + mass*mass)

        #Compute new mass for this Beauty candidate
        branchDict[configfile["BeautyPrefix"]["Name"]][configfile["BeautyPrefix"]["Name"]+"_M"+configfile["Pedix"]][bcand] = TMath.Sqrt(totE*totE
                                                                                                                                        - totPX*totPX
                                                                                                                                        - totPY*totPY
                                                                                                                                        - totPZ*totPZ)
        
#------------------------------------------------------------------------------
def ComputeNewBMassDconstr(branchDict, massDict, nBCand, configfile):

     #Compute Beauty mass constraining Charm(s) mass to its(their) PDG mass(es)

     PX=0.0
     PY=0.0
     PZ=0.0
     mass=0.0
     name=''

     #Loop over B candidates
     for bcand in range(0, nBCand):

         totPX=0.0
         totPY=0.0
         totPZ=0.0
         totE=0.0

         #Loop over B children
         for bchild in configfile["BeautyChildrenPrefix"].iterkeys():
             mass = massDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]]
             if 'Bachelor' in bchild:
                 #Bachelor: take directly its energy/momentum
                 name = configfile["BeautyChildrenPrefix"][bchild]["Name"]
                 PX = branchDict[name][name+"_PX"+configfile["Pedix"]][bcand]
                 PY = branchDict[name][name+"_PY"+configfile["Pedix"]][bcand]
                 PZ = branchDict[name][name+"_PZ"+configfile["Pedix"]][bcand]
                 
                 totPX = totPX + PX
                 totPY = totPY + PY
                 totPZ = totPZ + PZ
                 totE = totE + TMath.Sqrt(PX*PX + PY*PY + PZ*PZ + mass*mass)

             else:

                 CharmPX = 0.0
                 CharmPY = 0.0
                 CharmPZ = 0.0
                 
                 #Charm: take Charm(s) children momenta to build total Charm(s) momentum
                 for cchild in configfile[bchild+"ChildrenPrefix"].iterkeys():
                     name = configfile[bchild+"ChildrenPrefix"][cchild]["Name"]
                     PX = branchDict[name][name+"_PX"+configfile["Pedix"]][bcand]
                     PY = branchDict[name][name+"_PY"+configfile["Pedix"]][bcand]
                     PZ = branchDict[name][name+"_PZ"+configfile["Pedix"]][bcand]
                     
                     CharmPX = CharmPX + PX
                     CharmPY = CharmPY + PY
                     CharmPZ = CharmPZ + PZ

                 totPX = totPX + CharmPX
                 totPY = totPY + CharmPY
                 totPZ = totPZ + CharmPZ
                 totE = totE + TMath.Sqrt(CharmPX*CharmPX
                                          + CharmPY*CharmPY
                                          + CharmPZ*CharmPZ
                                          + mass*mass)


         #Compute new mass for this Beauty candidate
         branchDict[configfile["BeautyPrefix"]["Name"]][configfile["BeautyPrefix"]["Name"]+"_M"+configfile["Pedix"]][bcand] = TMath.Sqrt(totE*totE
                                                                                                                                         - totPX*totPX
                                                                                                                                         - totPY*totPY
                                                                                                                                         - totPZ*totPZ)
         
#------------------------------------------------------------------------------
def ComputeNewDMass(branchDict, massDict, CharmChildrenUpdates, nBCand, configfile):

    #Updating Charm mass

    PX=0.0
    PY=0.0
    PZ=0.0
    mass=0.0
    name=''

    #Loop over B candidates
    for bcand in range(0, nBCand):

        totPX=0.0
        totPY=0.0
        totPZ=0.0
        totE=0.0

        #Loop over Charm(s) with updating children
        for bchild in CharmChildrenUpdates.iterkeys():
            #Loop over this Charm children
            for cchild in configfile[bchild+"ChildrenPrefix"].iterkeys():
                name = configfile[bchild+"ChildrenPrefix"][cchild]["Name"]
                PX = branchDict[name][name+"_PX"+configfile["Pedix"]][bcand]
                PY = branchDict[name][name+"_PY"+configfile["Pedix"]][bcand]
                PZ = branchDict[name][name+"_PZ"+configfile["Pedix"]][bcand]
                mass = massDict[name]
                
                totPX = totPX + PX
                totPY = totPY + PY
                totPZ = totPZ + PZ
                totE = totE + TMath.Sqrt(PX*PX + PY*PY + PZ*PZ + mass*mass)
                
            #Compute new Charm mass for this Charm
            branchDict[configfile["BeautyChildrenPrefix"][bchild]["Name"]][configfile["BeautyChildrenPrefix"][bchild]["Name"]+"_M"+configfile["Pedix"]][bcand] = TMath.Sqrt(totE*totE
                                                                                                                                                                            - totPX*totPX
                                                                                                                                                                            - totPY*totPY
                                                                                                                                                                            - totPZ*totPZ)
            
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def ChangeMassHypo(debug,
                   configName,
                   inputfile,
                   inputtree,
                   outputfile,
                   outputdir,
                   outputtree,
                   maxBcand,
                   maxTreeEntries,
                   constraintCharmMass):

    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "CHANGEMASSHYPO IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="

    print ""
    print "========================================="
    print "Get input tree "+str(inputtree)+" from:"
    print str(inputfile)
    print "========================================="
    print ""

    inputFile = TFile.Open(inputfile,"READ")
    inputTree = inputFile.Get(inputtree)

    print ""
    print "========================================="
    print "Counting particles"
    print "========================================="
    print ""

    nBachelor = 0
    nCharm = 0
    nParentUpdates = 0

    for parent in myconfigfile["BeautyChildrenPrefix"].iterkeys():
        if "Bachelor" in parent:
            nBachelor = nBachelor + 1
        if "Charm" in parent:
            nCharm = nCharm + 1
        if 'newID' in myconfigfile["BeautyChildrenPrefix"][parent].keys():
            print str(parent)+" is updating its ID to "+str(myconfigfile["BeautyChildrenPrefix"][parent]['newID'])
            nParentUpdates = nParentUpdates + 1

    if (nCharm<=1 and nBachelor==0) or (nCharm==0 and nBachelor<=1):
        print "ERROR: Beauty has only <=1 child! Please check your config file"
        exit(-1)
        
    if debug:
        print "Number of bachelor(s): "+str(nBachelor)
        print "Number of charm(s): "+str(nCharm)

    nCharmChildren = {}
    CharmChildrenUpdates = {}
    
    if nCharm>0:
        for charm in range(1,nCharm+1):
            nCharmChildren["Charm"+str(charm)] = 0
            CharmChildrenUpdates["Charm"+str(charm)] = {}
            for child in myconfigfile["Charm"+str(charm)+"ChildrenPrefix"].iterkeys():
                nCharmChildren["Charm"+str(charm)] = nCharmChildren["Charm"+str(charm)] + 1
                if 'newID' in myconfigfile["Charm"+str(charm)+"ChildrenPrefix"][child].keys():
                    print str(child)+" is updating its ID to "+str(myconfigfile["Charm"+str(charm)+"ChildrenPrefix"][child]['newID'])
                    CharmChildrenUpdates["Charm"+str(charm)] = []
                    CharmChildrenUpdates["Charm"+str(charm)].append(child)
            if CharmChildrenUpdates["Charm"+str(charm)] == {}:
                CharmChildrenUpdates = {}
            if nCharmChildren["Charm"+str(charm)]<=1:
                print "ERROR: Charm"+str(charm)+" has only <=1 child! Please check your config file"
                exit(-1)
    if debug:
        print "Number of Charm(s) children:"
        print nCharmChildren
        print "Updating Charm(s) children:"
        print CharmChildrenUpdates
    
    print ""
    print "========================================="
    print "Creating output tree "+str(outputtree)+" in:"
    print str(outputfile)
    print "========================================="
    print ""

    #Clone tree, but deactivate branches that need to be updated (will copy later with updated values)
    print "Deactivate branches to be updated in old tree"
    inputTree = ChangeBranchStatus(inputTree,myconfigfile,0,debug)
    outputFile = TFile.Open(outputfile,"RECREATE")
    if outputdir!='':
        outputFile.mkdir(outputdir)
        outputFile.cd(outputdir)
    outputTree = inputTree.CloneTree(int(maxTreeEntries))
    outputTree.SetName(outputtree)
    outputTree.SetTitle(outputtree)
    
    if int(maxTreeEntries)>0:
        if int(maxTreeEntries) != outputTree.GetEntries():
            print "ERROR: number of entries in outputtree not correct!"
            exit(-1)
    else:
        if inputTree.GetEntries() != outputTree.GetEntries():
            print "ERROR: number of entries in outputtree not correct!"
            exit(-1)

    print ""
    print "========================================="
    print "Adding updated branches to new tree"
    print "========================================="
    print ""

    #Create dictionary of branches
    nBcand = int(maxBcand)
    branchDict = CreateBranchDictionary(myconfigfile,nBcand,debug)

    #Create mass dictionary
    massDict = CreateMassDictionary(myconfigfile,debug)
    
    #Re-enable branches
    print "Re-enable branches to be updated in old tree"
    inputTree = ChangeBranchStatus(inputTree,myconfigfile,1,debug)

    #Set address in old tree
    print "Set branch addresses in old tree"
    inputTree = SetAddress(inputTree,branchDict,myconfigfile,debug)

    #Create branches in new tree and set branch address
    print "Create branches to be updated in new tree"
    outputTree = CreateBranches(outputTree,branchDict,myconfigfile,debug)
    print "Set branch addresses in new tree"
    outputTree = SetAddress(outputTree,branchDict,myconfigfile,debug)

    print ""
    print "========================================="
    print "Filling new tree"
    print "========================================="
    print ""

    #Number of entries
    if int(maxTreeEntries) < 0:
        entries = inputTree.GetEntries()
    else:
        entries = int(maxTreeEntries)
        
    #Start loop over tree entries. The different cases are splitted. This is ugly, but it avoids
    #too many "if...else..." inside the loop itself which can slow down the process
    if constraintCharmMass and CharmChildrenUpdates == {}:
        print "Computing new Beauty mass constraining Charm(s) mass to its(their) PDG value(s)"
        print "No need to update Charm(s) invariant mass"
        print ""
        print "Looping over "+str(entries)+" entries"
        nBCand=1
        for entry in range(0,entries):
            if entry%10000 == 0 and debug:
                print "Processing entry "+str(entry)+"..."
            inputTree.GetEntry(entry)
            if 'Index' in myconfigfile["BeautyPrefix"].keys():
                nBCand = branchDict[myconfigfile["BeautyPrefix"]["Name"]][myconfigfile["BeautyPrefix"]["Index"]][0] 
            ComputeNewBMassDconstr(branchDict, massDict, nBCand, myconfigfile)
            outputTree.Fill()
            
    elif constraintCharmMass and CharmChildrenUpdates != {}:
        print "Computing new Beauty mass constraining Charm(s) mass to its(their) PDG value(s)"
        print "Updating Charm(s) invariant mass as well"
        print ""
        print "Looping over "+str(entries)+" entries"
        nBCand=1
        for entry in range(0,entries):
            if entry%10000 == 0 and debug:
                print "Processing entry "+str(entry)+"..."
            inputTree.GetEntry(entry)
            if 'Index' in myconfigfile["BeautyPrefix"].keys():
                nBCand = branchDict[myconfigfile["BeautyPrefix"]["Name"]][myconfigfile["BeautyPrefix"]["Index"]][0]
            ComputeNewBMassDconstr(branchDict, massDict, nBCand, myconfigfile)
            ComputeNewDMass(branchDict, massDict, CharmChildrenUpdates, nBCand, myconfigfile)
            outputTree.Fill()

    elif not constraintCharmMass and CharmChildrenUpdates == {}:
        print "Computing new Beauty mass"
        print "No need to update Charm(s) invariant mass"
        print ""
        print "Looping over "+str(entries)+" entries"
        nBCand=1
        for entry in range(0,entries):
            if entry%10000 == 0 and debug:
                print "Processing entry "+str(entry)+"..."
            inputTree.GetEntry(entry)
            if 'Index' in myconfigfile["BeautyPrefix"].keys():
                nBCand = branchDict[myconfigfile["BeautyPrefix"]["Name"]][myconfigfile["BeautyPrefix"]["Index"]][0]
            ComputeNewBMass(branchDict, massDict, nBCand, myconfigfile)
            outputTree.Fill()

    elif not constraintCharmMass and CharmChildrenUpdates != {}:
        print "Computing new Beauty mass"
        print "Updating Charm(s) invariant mass as well"
        print ""
        print "Looping over "+str(entries)+" entries"
        nBCand=1
        for entry in range(0,entries):
            if entry%10000 == 0 and debug:
                print "Processing entry "+str(entry)+"..."
            inputTree.GetEntry(entry)
            if 'Index' in myconfigfile["BeautyPrefix"].keys():
                nBCand = branchDict[myconfigfile["BeautyPrefix"]["Name"]][myconfigfile["BeautyPrefix"]["Index"]][0]
            ComputeNewBMass(branchDict, massDict, nBCand, myconfigfile)
            ComputeNewDMass(branchDict, massDict, CharmChildrenUpdates, nBCand, myconfigfile)
            outputTree.Fill()

    else:
        print "ERROR: something went wrong. Please check your config file"
        exit(-1)

    outputTree.SetEntries(entries)

    print ""
    print "Loop finished!"
    print ""
    print "Expected entries: "+str(entries)
    print "Effective entries: "+str(outputTree.GetEntries())

    print ""
    print "========================================="
    print "Saving new tree"
    print "========================================="
    print ""

    outputFile.cd()
    if outputdir != '':
        outputFile.cd(outputdir)
    outputTree.Write("",TObject.kWriteDelete)
    outputFile.ls()
    outputFile.Close()
    
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )
parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'MyConfigFile',
                   help = 'configuration file name'
                   )
parser.add_option( '--inputfile',
                   dest = 'inputfile',
                   default = 'MyInputFile.root',
                   help = 'input file with tree to update'
                   )
parser.add_option( '--inputtree',
                   dest = 'inputtree',
                   default = 'MyDir/MyTree',
                   help = 'input tree name (including TFile directory)'
                   )
parser.add_option( '--outputfile',
                   dest = 'outputfile',
                   default = 'MyOutputFile.root',
                   help = 'output file with updated tree'
                   )
parser.add_option( '--outputdir',
                   dest = 'outputdir',
                   default = '',
                   help = 'TFile directory for output tree'
                   )
parser.add_option( '--outputtree',
                   dest = 'outputtree',
                   default = 'MyTree',
                   help = 'output tree name'
                   )
parser.add_option( '--maxBcand',
                   dest = 'maxBcand',
                   default = '50',
                   help = 'max length of B-related branches'
                   )
parser.add_option( '--maxTreeEntries',
                   dest = 'maxTreeEntries',
                   default = '-1',
                   help = 'max number of entries for output tree'
                   )
parser.add_option( '--constraintCharmMass',
                   action = 'store_true',
                   dest = 'constraintCharmMass',
                   default = False,
                   help = 'constraint Charm(s) mass(es) to its(their) PDG value(s)'
                   )

# -----------------------------------------------------------------------------
if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    config = options.configName
    last = config.rfind("/")
    directory = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]

    import sys
    sys.path.append(directory)

    print "Config file name: "+configName
    print "Directory: "+directory
    
    ChangeMassHypo(options.debug,
                   configName,
                   options.inputfile,
                   options.inputtree,
                   options.outputfile,
                   options.outputdir,
                   options.outputtree,
                   options.maxBcand,
                   options.maxTreeEntries,
                   options.constraintCharmMass)
    
# -----------------------------------------------------------------------------
