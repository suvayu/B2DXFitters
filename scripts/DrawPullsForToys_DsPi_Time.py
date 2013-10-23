# -----------------------------------------------------------------------------
# settings for running without GaudiPython
# -----------------------------------------------------------------------------
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
        if test -z "$(dirname $0)"; then
            # have to guess location of setup.sh
            cd ../standalone
            . ./setup.sh
            cd "$cwd"
        else
            # know where to look for setup.sh
            cd "$(dirname $0)"/../standalone
            . ./setup.sh
            cd "$cwd"
        fi
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

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from B2DXFitters import *
from ROOT import *

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
import os, sys, gc

gStyle.SetOptStat(0)
gStyle.SetOptFit(1011)
gROOT.SetBatch()

import sys
sys.path.append("../data/")

PlotAcceptance = False

# Save the results?
saveToFile = False
# Make toy-by-toy difference plots?
tbtd = True

ntoys               = 1000
toysdir_time        = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/PETE/NoPETE/'
toysdir_time_tbtd   = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/PETE/PETE/'
toysdir_mass        = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/PETE/'
toysdir_mass_tbtd   = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/PETE/'
toysresultprefix_time  = 'DsPi_Toys_TimeFitResult_DMS_'
toysresultprefix_mass  = 'DsPi_Toys_MassFitResult_'
toysresultsuffix       = '.log'    

# Plot suffixes in order, tbtd second, this could all be better coded
# but it will do for now
plotsuffix_time         = ["NoPETE","PETE"]

outputdir = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/PETE/NoPETE/'

generated = {}
fitted    = {}

generated["DMS"] = 17.768
fitted["DMS"]    = [ntoys*[(0,0)]]

if PlotAcceptance:
    generated["TaccExpo"]   = 1.8627e+00
    fitted["TaccExpo"]      = [ntoys*[(0,0)]]
    
    generated["TaccOff"]    = 1.6710e-02
    fitted["TaccOff"]       = [ntoys*[(0,0)]]
    
    generated["TaccBeta"]   = 3.4938e-02
    fitted["TaccBeta"]      = [ntoys*[(0,0)]]
    
    generated["TaccTurnOn"] = 1.3291e+00
    fitted["TaccTurnOn"]    = [ntoys*[(0,0)]]
  
if tbtd :
    for variable in fitted :
        fitted[variable].append(ntoys*[(0,0)])

nfailed = [[]]
toyfilestorunon = [toysdir_mass]
if tbtd :
    toyfilestorunon.append(toysdir_mass_tbtd)
    nfailed.append([])
for dirindex,toydir in enumerate(toyfilestorunon) :
    for thistoy in range(0,ntoys) :
        f = open(toydir+toysresultprefix_mass+str(thistoy)+toysresultsuffix)
        counter = 0
        counterstop = -100
        badfit = False
        print "Processing toy",thistoy
        for line in f :
            counter += 1
            if line.find('MIGRAD=4') > -1 :
                badfit = True
                nfailed[dirindex].append(thistoy)
                break
            if line.find('NOT POS-DEF') > -1 :
                badfit = True
            if line.find('ERROR MATRIX ACCURATE') > -1 :
                badfit = False
            if line.find('FinalValue') >  -1 :
                if badfit :
                    nfailed[dirindex].append(thistoy)
                    break
                #print line
                counterstop = counter
                break

for dirindex,toydir in enumerate(toyfilestorunon) :
    print "Printing failed toys for directory", toydir
    print nfailed[dirindex].__len__(),'toys failed to converge properly'
    print nfailed[dirindex]
    print "############################################################"

toyfilestorunon = [toysdir_time]
if tbtd :
    toyfilestorunon.append(toysdir_time_tbtd)
for dirindex,toydir in enumerate(toyfilestorunon) :
    for thistoy in range(0,ntoys) :
        f = open(toydir+toysresultprefix_time+str(thistoy)+toysresultsuffix)
        counter = 0 
        counterstop = -100
        badfit = False
        print "Processing toy",thistoy
            
        for line in f :
            counter += 1
            if line.find('MIGRAD=4') > -1 :
                badfit = True
                nfailed[dirindex].append(thistoy)
                break
            if line.find('NOT POS-DEF') > -1 :
                badfit = True
                
            if line.find('ERROR MATRIX ACCURATE') > -1 :
                badfit = False
                
            if line.find('FinalValue') >  -1 :
                if badfit :
                    nfailed[dirindex].append(thistoy)
                    break
                #print line
                counterstop = counter
                                                                                                                                            
            if counter == counterstop + 2 :
                result = line.split()
                fitted["DMS"][dirindex][thistoy] =  (float(result[2]), float(result[4]))
                break
            if PlotAcceptance:
                if counter == counterstop + 3 :
                    result = line.split()
                    fitted["TaccBeta"][dirindex][thistoy]   =  (float(result[2]), float(result[4]))
                if counter == counterstop + 4 :
                    result = line.split()
                    fitted["TaccExpo"][dirindex][thistoy]   =  (float(result[2]), float(result[4]))
                if counter == counterstop + 5 :
                    result = line.split()
                    fitted["TaccOff"][dirindex][thistoy]    =  (float(result[2]), float(result[4]))
                if counter == counterstop + 6 :
                    result = line.split()
                    fitted["TaccTurnOn"][dirindex][thistoy] =  (float(result[2]), float(result[4]))
                break
        f.close()

for dirindex,toydir in enumerate(toyfilestorunon) :
    print "Printing failed toys for directory", toydir
    print fitted["DMS"][dirindex]
    print nfailed[dirindex].__len__(),'toys failed to converge properly'
    print nfailed[dirindex]
    print "############################################################"

    fitted_signal = TH1F("fitted_delta_ms","fitted_delta_ms",100,17.5,18.0) 
    fitted_signal.GetXaxis().SetTitle("Fitted delta ms")
    errf_signal   = TH1F("errf_delta_ms","errf_delta_ms",100,0,0.05)
    errf_signal.GetXaxis().SetTitle("Fitted error")
    pull_signal   = TH1F("pull_delta_ms","pull_delta_ms",50,-5,5)
    pull_signal.GetXaxis().SetTitle("Fitted Pull")
    
    for thistoy in range(0,ntoys) :
        if thistoy in nfailed : continue
        fitted_signal.Fill(fitted["DMS"][dirindex][thistoy][0])
        errf_signal.Fill(fitted["DMS"][dirindex][thistoy][1])
        pull_signal.Fill((generated["DMS"]-fitted["DMS"][dirindex][thistoy][0])/fitted["DMS"][dirindex][thistoy][1])
 
    pullcanvassignal = TCanvas("pullcanvassignal","pullcanvassignal",1500,500)
    pullcanvassignal.Divide(3,1)
    pullcanvassignal.cd(1)
    fitted_signal.Fit("gaus")
    fitted_signal.Draw("PE")
    pullcanvassignal.cd(2)
    errf_signal.Fit("gaus")
    errf_signal.Draw("PE")
    pullcanvassignal.cd(3)
    pull_signal.Fit("gaus")
    pull_signal.Draw("PE")
    if saveToFile :
        pullcanvassignal.Print(outputdir+"PullPlot_DsPi_Time_DMS_"+plotsuffix_time[dirindex]+".pdf")
    
    if PlotAcceptance:
        
        fitted_expo = TH1F("fitted_tacc_expo","fitted_tacc_expo",100,1.0,4.0)
        fitted_expo.GetXaxis().SetTitle("Fitted tacc exponential")
        errf_expo   = TH1F("errf_tacc_expo","errf_tacc_expo",100,0,0.2)
        errf_expo.GetXaxis().SetTitle("Fitted error")
        pull_expo   = TH1F("pull_tacc_expo","pull_tacc_expo",50,-5,5)
        pull_expo.GetXaxis().SetTitle("Fitted Pull")
    
        for thistoy in range(0,ntoys) :
            if thistoy in nfailed : continue
            fitted_expo.Fill(fitted["TaccExpo"][dirindex][thistoy][0])
            errf_expo.Fill(fitted["TaccExpo"][dirindex][thistoy][1])
            pull_expo.Fill((generated["TaccExpo"]-fitted["TaccExpo"][dirindex][thistoy][0])/fitted["TaccExpo"][dirindex][thistoy][1])
    
        pullcanvasexpo = TCanvas("pullcanvasexpo","pullcanvasexpo",1500,500)
        pullcanvasexpo.Divide(3,1)
        pullcanvasexpo.cd(1)
        fitted_expo.Draw("PE")
        pullcanvasexpo.cd(2)
        errf_expo.Draw("PE")
        pullcanvasexpo.cd(3)
        pull_expo.Fit("gaus")
        pull_expo.Draw("PE")
    
        if saveToFile:
            pullcanvasexpo.Print(outputdir+"PullPlot_DsPi_Time_TaccExponent_"+plotsuffix_time[dirindex]+".pdf")
    
        fitted_off = TH1F("fitted_tacc_off","fitted_tacc_off",100,-0.2,0.10)
        fitted_off.GetXaxis().SetTitle("Fitted tacc offset")
        errf_off   = TH1F("errf_tacc_off","errf_tacc_off",100,0,0.1)
        errf_off.GetXaxis().SetTitle("Fitted error")
        pull_off   = TH1F("pull_tacc_off","pull_tacc_off",50,-5,5)
        pull_off.GetXaxis().SetTitle("Fitted Pull")
        
        for thistoy in range(0,ntoys) :
            if thistoy in nfailed : continue
            fitted_off.Fill(fitted["TaccOff"][dirindex][thistoy][0])
            errf_off.Fill(fitted["TaccOff"][dirindex][thistoy][1])
            pull_off.Fill((generated["TaccOff"]-[thistoy]-fitted["TaccOff"][dirindex][thistoy][0])/fitted["TaccOff"][dirindex][thistoy][1])
    
        pullcanvasoff = TCanvas("pullcanvasoff","pullcanvasoff",1500,500)
        pullcanvasoff.Divide(3,1)
        pullcanvasoff.cd(1)
        fitted_off.Draw("PE")
        pullcanvasoff.cd(2)
        errf_off.Draw("PE")
        pullcanvasoff.cd(3)
        pull_off.Fit("gaus")
        pull_off.Draw("PE")
        
        if saveToFile :
            pullcanvasoff.Print(outputdir+"PullPlot_DsPi_Time_TaccOffset_"+plotsuffix_time[dirindex]+".pdf")
    
        fitted_beta = TH1F("fitted_tacc_beta","fitted_tacc_beta",100,0.00,0.15)
        fitted_beta.GetXaxis().SetTitle("Fitted tacc beta")
        errf_beta   = TH1F("errf_tacc_beta","errf_tacc_beta",100,0,0.01)
        errf_beta.GetXaxis().SetTitle("Fitted error")
        pull_beta   = TH1F("pull_tacc_beta","pull_tacc_beta",50,-5,5)
        pull_beta.GetXaxis().SetTitle("Fitted Pull")
        
        for thistoy in range(0,ntoys) :
            if thistoy in nfailed : continue
            fitted_beta.Fill(fitted["TaccBeta"][dirindex][thistoy][0])
            errf_beta.Fill(fitted["TaccBeta"][dirindex][thistoy][1])
            pull_beta.Fill((generated["TaccBeta"]-fitted["TaccBeta"][dirindex][thistoy][0])/fitted["TaccBeta"][dirindex][thistoy][1])
            
        pullcanvasbeta = TCanvas("pullcanvasbeta","pullcanvasbeta",1500,500)
        pullcanvasbeta.Divide(3,1)
        pullcanvasbeta.cd(1)
        fitted_beta.Draw("PE")
        pullcanvasbeta.cd(2)
        errf_beta.Draw("PE")
        pullcanvasbeta.cd(3)
        pull_beta.Fit("gaus")
        pull_beta.Draw("PE")
        
        if saveToFile :
            pullcanvasbeta.Print(outputdir+"PullPlot_DsPi_Time_TaccBeta_"+plotsuffix_time[dirindex]+".pdf")
        
        
        fitted_on = TH1F("fitted_tacc_turnon","fitted_tacc_turnon",100,0.50,7.0)
        fitted_on.GetXaxis().SetTitle("Fitted tacc turnon")
        errf_on   = TH1F("errf_tacc_turnon","errf_tacc_turnon",100,0,0.1)
        errf_on.GetXaxis().SetTitle("Fitted error")
        pull_on   = TH1F("pull_tacc_turnon","pull_tacc_turnon",50,-5,5)
        pull_on.GetXaxis().SetTitle("Fitted Pull")
        
        for thistoy in range(0,ntoys) :
            if thistoy in nfailed : continue
            fitted_on.Fill(fitted["TaccTurnOn"][dirindex][thistoy][0])
            errf_on.Fill(fitted["TaccTurnOn"][dirindex][thistoy][1])
            pull_on.Fill((generated["TaccTurnOn"]-fitted["TaccTurnOn"][dirindex][thistoy][0])/fitted["TaccTurnOn"][dirindex][thistoy][1])
    
        pullcanvason = TCanvas("pullcanvason","pullcanvason",1500,500)
        pullcanvason.Divide(3,1)
        pullcanvason.cd(1)
        fitted_on.Draw("PE")
        pullcanvason.cd(2)
        errf_on.Draw("PE")
        pullcanvason.cd(3)
        pull_on.Fit("gaus")
        pull_on.Draw("PE")
        
        if saveToFile:
            pullcanvason.Print(outputdir+"PullPlot_DsPi_Time_TaccTurnOn_"+plotsuffix_time[dirindex]+".pdf")

# The array with the toy by toy differences
# the pair is the difference in values, the difference in errors
differences = {}
for variable in fitted :
    differences[variable] = {}
    differences[variable]["Values"] = TH1F("differences_values_"+variable,"differences_values_"+variable,200,-0.02,0.02)
    differences[variable]["Values"].GetXaxis().SetTitle("Difference in fitted values for "+variable)
    differences[variable]["Errors"] = TH1F("differences_errors_"+variable,"differences_errors_"+variable,200,-0.002,0.002)
    differences[variable]["Errors"].GetXaxis().SetTitle("Difference in fitted errors for "+variable)
for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    for variable in fitted :
        differences[variable]["Values"].Fill(fitted[variable][1][thistoy][0]-fitted[variable][0][thistoy][0])
        differences[variable]["Errors"].Fill(fitted[variable][1][thistoy][1]-fitted[variable][0][thistoy][1])
    
diffcanvas = TCanvas("diffcanvas","diffcanvas",1000,500)
diffcanvas.Divide(2,1)
diffcanvas.cd(1)
differences[variable]["Values"].Fit("gaus")
differences[variable]["Values"].Draw("PE")
diffcanvas.cd(2)
differences[variable]["Errors"].Fit("gaus")
differences[variable]["Errors"].Draw("PE") 

if saveToFile:
    pullcanvason.Print(outputdir+"DifferenceCanvas_"+plotsuffix_time[0]+"_"+plotsuffix_time[1]+".pdf")
