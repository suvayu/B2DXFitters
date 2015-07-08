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
gROOT.SetBatch()
gStyle.SetOptStat(0)
gStyle.SetOptFit(1011)

import sys
sys.path.append("../data/")

debug = True
largeToys = False
drawGeneratedYields = False

ntoys               = 1000
toysdir             = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/Gamma70_5M_2T_MD/'
toystupleprefix     = 'DsPi_Toys_sWeights_ForTimeFit_'
if largeToys : toystupleprefix     = 'DsPi_Toys_FullLarge_Tree_'
toystuplesuffix     = '.root'
toysresultprefix    = 'DsPi_Toys_MassFitResult_'
if largeToys : toysresultprefix    = 'DsPi_Toys_FullLarge_MassFitResult_'
toysresultsuffix    = '.log'    

#outputdir = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToysAgnieszka_010813/'
outputdir = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/Gamma70_5M_2T_MD/'
#outputdir = "./"

nbinspull = 50
lowerpullrange = -3
upperpullrange = 3


eventtypes = {"Signal" : 1.0, 
              "DPi"    : 2.0,
              "Bd2DsPi": 3.0,
              "LcPi"   : 4.0,
              "LMPi"   : 5.0,
              "DsK"    : 7.0,
              "Combo"  : 10.0 }

# Get the configuration file
myconfigfilegrabber = __import__("Bs2DsPiConfigForGenerator",fromlist=['getconfig']).getconfig
myconfigfile = myconfigfilegrabber()

numgenevt ={"Signal" : ntoys*[29427.0]} 
numfitted ={"Signal1" : ntoys*[(0,0)]}
numfitted["Signal2"] = ntoys*[(0,0)]
numfitted["Signal3"] = ntoys*[(0,0)]
numfitted["Signal4"] = ntoys*[(0,0)]
numfitted["Signal5"] = ntoys*[(0,0)]

numgenevt["Combo"] = ntoys*[12238.0]
numfitted["Combo1"] = ntoys*[(0,0)]
numfitted["Combo2"] = ntoys*[(0,0)]
numfitted["Combo3"] = ntoys*[(0,0)]
numfitted["Combo4"] = ntoys*[(0,0)]
numfitted["Combo5"] = ntoys*[(0,0)]

numgenevt["LMPi"] = ntoys*[322.6]
numfitted["LMPi1"] = ntoys*[(0,0)]
numfitted["LMPi2"] = ntoys*[(0,0)]
numfitted["LMPi3"] = ntoys*[(0,0)]
numfitted["LMPi4"] = ntoys*[(0,0)]
numfitted["LMPi5"] = ntoys*[(0,0)]


numgenevt["g1_f1"] = ntoys*[0.5]
numfitted["g1_f1"] = ntoys*[(0,0)]

numevents       = {}
numeventshistos = {}

for eventtype in eventtypes :
    numevents[eventtype]    = ntoys*[0]
    maxevents = 5000
    minevents = 0
    if eventtype in ["Bd2DPi","Bd2DsPi","Lb2LcPi","LMPi", "Bs2DsK"] :
        maxevents = 700
    if eventtype in ["Signal"] :
        maxevents = 40000
        minevents = 20000
    if eventtype in ["Combo"]:
        maxevents = 18000
        minevents = 6000

    numeventshistos[eventtype] = TH1F("genhist"+eventtype,"genhist"+eventtype,400,0,maxevents)
    numeventshistos[eventtype].GetXaxis().SetTitle("Number of generated "+eventtype+" events")

if drawGeneratedYields :
                    
    for thistoy in range(0,ntoys) :
        print "Processing toy",thistoy
        #try :
        thistoyfile = TFile(toysdir+toystupleprefix+str(thistoy)+toystuplesuffix)
        #except :
        #    print 'Toy number',thistoy,'failed to converge properly!'
        #    continue                                            
        #thistoyfile = TFile(toysdir+toystupleprefix+str(thistoy)+toystuplesuffix)
        thistoytree = thistoyfile.Get('merged') 
        for thisentry in range(0,thistoytree.GetEntries()) :
            thistoytree.GetEntry(thisentry)
            for eventtype in eventtypes :
                if abs(thistoytree.lab0_TRUEID-eventtypes[eventtype]) < 0.5 :
                    numevents[eventtype][thistoy] += 1
        for eventtype in eventtypes :
            if eventtype == "LMPi" :
                numeventshistos[eventtype].Fill(numevents["LMPi"][thistoy]+numevents["Bd2DsPi"][thistoy])
            else :
                numeventshistos[eventtype].Fill(numevents[eventtype][thistoy])
        numevents["LMPi"][thistoy] += numevents["Bd2DsPi"][thistoy]
    
    if debug : print numevents
    
    geneventcanvas = TCanvas("geneventcanvas","geneventcanvas",1600,1600)
    geneventcanvas.Divide(3,3)
    for i,eventtype in enumerate(eventtypes) :
        print "Fitting number of generated",eventtype,"events now!"
        geneventcanvas.cd(i+1) 
        numeventshistos[eventtype].Fit("gaus")
        numeventshistos[eventtype].Draw("EP")
    
    if largeToys :
        geneventcanvas.Print(outputdir+"NumGenByChannel_DsK_Large_Mass.pdf")     
    else :
        geneventcanvas.Print(outputdir+"NumGenByChannel_DsK_Mass.pdf")

nfailed = []
#exit(0)

for thistoy in range(0,ntoys) :
    f = open(toysdir+toysresultprefix+str(thistoy)+toysresultsuffix)
    counter = 0 
    counterstop = -100
    badfit = False
    print "Processing toy",thistoy
    for line in f :
        counter += 1
        if line.find('MIGRAD=4') > -1 :
            badfit = True
            nfailed.append(thistoy)
            break
        if line.find('NOT POS-DEF') > -1 :
            badfit = True
        if line.find('ERROR MATRIX ACCURATE') > -1 :
            badfit = False
        if line.find('FinalValue') >  -1 :
            if badfit : 
                nfailed.append(thistoy)
                break
            #print line
            counterstop = counter    
                                                
        if counter == counterstop + 23 :
            result = line.split()
            numfitted["g1_f1"][thistoy] =  (float(result[2]), float(result[4]))
            print numfitted["g1_f1"][thistoy]
            
        #----------------------------------------------------------------------#                    
             
        if counter == counterstop + 24 :
            result = line.split()
            numfitted["LMPi1"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 25 :
            result = line.split()
            numfitted["LMPi2"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 26 :
            result = line.split()
            numfitted["LMPi3"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 27 :
            result = line.split()
            numfitted["LMPi4"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 28 :
            result = line.split()
            numfitted["LMPi5"][thistoy] =  (float(result[2]), float(result[4]))
            
        #----------------------------------------------------------------------#
                 
        if counter == counterstop + 29 :
            result = line.split()
            numfitted["Combo1"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 30 :
            result = line.split()
            numfitted["Combo2"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 31 :
            result = line.split()
            numfitted["Combo3"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 32 :
            result = line.split()
            numfitted["Combo4"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 33:
            result = line.split()
            numfitted["Combo5"][thistoy] =  (float(result[2]), float(result[4]))

        #----------------------------------------------------------------------#
                                    
        if counter == counterstop + 34:
            result = line.split()
            numfitted["Signal1"][thistoy] =  (float(result[2]), float(result[4]))
            print "Signal"
            print numfitted["Signal1"][thistoy]
            #exit(0)
        if counter == counterstop + 35:
            result = line.split()
            numfitted["Signal2"][thistoy] =  (float(result[2]), float(result[4]))
            print numfitted["Signal2"][thistoy]
        if counter == counterstop + 36:
            result = line.split()
            numfitted["Signal3"][thistoy] =  (float(result[2]), float(result[4]))
            print numfitted["Signal3"][thistoy]
        if counter == counterstop + 37:
            result = line.split()
            numfitted["Signal4"][thistoy] =  (float(result[2]), float(result[4]))
            print numfitted["Signal4"][thistoy]
        if counter == counterstop + 38:
            result = line.split()
            numfitted["Signal5"][thistoy] =  (float(result[2]), float(result[4]))
            print numfitted["Signal5"][thistoy]
            #exit(0)
            break
    if counterstop == -100 and not badfit :
        print "Something went wrong with fit",thistoy
        nfailed.append(thistoy)
    f.close()
#exit(0)
if debug : 
    print nfailed
    print '\n\n\n'
    print numfitted
    print "Number of failed toys: ", nfailed.__len__()
nfailed.append(96)

'''
nDspfailed = []
for thistoy in range(0,ntoys):
    if thistoy in nfailed: continue
    
    Dsp1E = numfitted["Dsp1"][thistoy][1]
    Dsp2E = numfitted["Dsp2"][thistoy][1]
    Dsp3E = numfitted["Dsp3"][thistoy][1]
    Dsp4E = numfitted["Dsp4"][thistoy][1]
    Dsp5E = numfitted["Dsp5"][thistoy][1]
    DspE = sqrt( (Dsp1E*Dsp1E)+(Dsp2E*Dsp2E)+(Dsp3E*Dsp3E)+(Dsp4E*Dsp4E)+(Dsp5E*Dsp5E))
    if DspE > 90:
        nDspfailed.append(thistoy)

nDsPifailed = []
for thistoy in range(0,ntoys):
    if thistoy in nfailed: continue
    
    DsPi1E = numfitted["LMPi1"][thistoy][1]
    DsPi2E = numfitted["LMPi2"][thistoy][1]
    DsPi3E = numfitted["LMPi3"][thistoy][1]
    DsPi4E = numfitted["LMPi4"][thistoy][1]
    DsPi5E = numfitted["LMPi5"][thistoy][1]
    DsPiE = sqrt( (DsPi1E*DsPi1E)+(DsPi2E*DsPi2E)+(DsPi3E*DsPi3E)+(DsPi4E*DsPi4E)+(DsPi5E*DsPi5E))
    if DsPiE > 250:
        nDsPifailed.append(thistoy)

                                        

if debug:
    print nDspfailed
    print "Number of Dsp failed toys: ", nDspfailed.__len__()

if debug:
    print nDsPifailed
    print "Number of DsPi failed toys: ", nDsPifailed.__len__()
'''            
    
gen_signal    = TH1F("gen_signal","gen_signal",100,28000,32000)
gen_signal.GetXaxis().SetTitle("Generated signal events")
fitted_signal = TH1F("fitted_signal","fitted_signal",100,28000,32000)
fitted_signal.GetXaxis().SetTitle("Fitted signal events")
errf_signal   = TH1F("errf_signal","errf_signal",100,100,300)
errf_signal.GetXaxis().SetTitle("Fitted signal error")
pull_signal   = TH1F("pull_signal","pull_signal",nbinspull,lowerpullrange,upperpullrange)
pull_signal.GetXaxis().SetTitle("Fitted Signal Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    SF = numfitted["Signal1"][thistoy][0]+numfitted["Signal2"][thistoy][0]+numfitted["Signal3"][thistoy][0]+numfitted["Signal4"][thistoy][0]+numfitted["Signal5"][thistoy][0]
    S1E = numfitted["Signal1"][thistoy][1]
    S2E = numfitted["Signal2"][thistoy][1]
    S3E = numfitted["Signal3"][thistoy][1]
    S4E = numfitted["Signal4"][thistoy][1]
    S5E = numfitted["Signal5"][thistoy][1]
    SE = sqrt( (S1E*S1E)+(S2E*S2E)+(S3E*S3E)+(S4E*S4E)+(S5E*S5E))
    gen_signal.Fill(numevents["Signal"][thistoy])
    fitted_signal.Fill(SF)
    errf_signal.Fill(SE)
    #print "%d %d %d %d %d %d %d %d %d"%(thistoy, SF, S1E, S2E, S3E, S4E, S5E, SE, numgenevt["Signal"][thistoy])
    #print "%d %d %d %f"%(thistoy, numgenevt["Signal"][thistoy], numfitted["Signal"][thistoy][0],
    #                     numgenevt["Signal"][thistoy]-numfitted["Signal"][thistoy][0])
    pull_signal.Fill((numgenevt["Signal"][thistoy]-SF)/SE)
pullcanvassignal = TCanvas("pullcanvassignal","pullcanvassignal",800,800)
pullcanvassignal.Divide(2,2)
pullcanvassignal.cd(1)
gen_signal.Fit("gaus")
gen_signal.Draw("PE")
pullcanvassignal.cd(2)
fitted_signal.Fit("gaus")
fitted_signal.Draw("PE")
pullcanvassignal.cd(3)
errf_signal.Fit("gaus")
errf_signal.Draw("PE")
pullcanvassignal.cd(4)
pull_signal.Fit("gaus")
pull_signal.Draw("PE")

if largeToys :
    pullcanvassignal.Print(outputdir+"PullPlot_DsPi_Mass_Large_Signal.pdf")
else :
    pullcanvassignal.Print(outputdir+"PullPlot_DsPi_Mass_Signal.pdf")

gen_combo    = TH1F("gen_combo","gen_combo",100,9000,15000)
gen_combo.GetXaxis().SetTitle("Generated combo events")
fitted_combo = TH1F("fitted_combo","fitted_combo",100,9000,15000)
fitted_combo.GetXaxis().SetTitle("Fitted combo events")
errf_combo   = TH1F("errf_combo","errf_combo",100,0,200)
errf_combo.GetXaxis().SetTitle("Fitted error")
pull_combo   = TH1F("pull_combo","pull_combo",nbinspull,lowerpullrange,upperpullrange)
pull_combo.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    CF = numfitted["Combo1"][thistoy][0]+numfitted["Combo2"][thistoy][0]+numfitted["Combo3"][thistoy][0]+numfitted["Combo4"][thistoy][0]+numfitted["Combo5"][thistoy][0] 
    C1E= numfitted["Combo1"][thistoy][1]
    C2E= numfitted["Combo2"][thistoy][1]
    C3E= numfitted["Combo3"][thistoy][1]
    C4E= numfitted["Combo4"][thistoy][1]
    C5E= numfitted["Combo5"][thistoy][1]
    
    CE = sqrt( (C1E*C1E)+(C2E*C2E)+(C3E*C3E)+(C4E*C4E)+(C5E*C5E))
    gen_combo.Fill(numevents["Combo"][thistoy])
    fitted_combo.Fill(CF)
    errf_combo.Fill(CE)
    pull_combo.Fill((numgenevt["Combo"][thistoy]-CF)/CE)

pullcanvascombo = TCanvas("pullcanvascombo","pullcanvascombo",800,800)
pullcanvascombo.Divide(2,2)
pullcanvascombo.cd(1)
gen_combo.Fit("gaus")
gen_combo.Draw("PE")
pullcanvascombo.cd(2)
fitted_combo.Draw("PE")
fitted_combo.Fit("gaus")
pullcanvascombo.cd(3)
errf_combo.Fit("gaus")
errf_combo.Draw("PE")
pullcanvascombo.cd(4)
pull_combo.Fit("gaus")
pull_combo.Draw("PE")

if largeToys :
    pullcanvascombo.Print(outputdir+"PullPlot_DsPi_Mass_Large_Combo.pdf")
else :
    pullcanvascombo.Print(outputdir+"PullPlot_DsPi_Mass_Combo.pdf")

gen_lmpi    = TH1F("gen_lmpi","gen_lmpi",100,0,700)
gen_lmpi.GetXaxis().SetTitle("Generated lmpi events")
fitted_lmpi = TH1F("fitted_lmpi","fitted_lmpi",100,0,700)
fitted_lmpi.GetXaxis().SetTitle("Fitted lmpi events")
errf_lmpi   = TH1F("errf_lmpi","errf_lmpi",100,0,150)
errf_lmpi.GetXaxis().SetTitle("Fitted error")
pull_lmpi   = TH1F("pull_lmpi","pull_lmpi",nbinspull,lowerpullrange,upperpullrange)
pull_lmpi.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    LMPiF = numfitted["LMPi1"][thistoy][0] + numfitted["LMPi2"][thistoy][0] + numfitted["LMPi3"][thistoy][0] + numfitted["LMPi4"][thistoy][0] + numfitted["LMPi5"][thistoy][0]
    LMPi1E = numfitted["LMPi1"][thistoy][1]
    LMPi2E = numfitted["LMPi2"][thistoy][1]
    LMPi3E = numfitted["LMPi3"][thistoy][1]
    LMPi4E = numfitted["LMPi4"][thistoy][1]
    LMPi5E = numfitted["LMPi5"][thistoy][1]
    LMPiE = sqrt( (LMPi1E*LMPi1E)+(LMPi2E*LMPi2E)+(LMPi3E*LMPi3E)+(LMPi4E*LMPi4E)+(LMPi5E*LMPi5E))
                            
    gen_lmpi.Fill(numevents["LMPi"][thistoy])
    fitted_lmpi.Fill(LMPiF)
    errf_lmpi.Fill(LMPiE)
    pull_lmpi.Fill((numgenevt["LMPi"][thistoy]-LMPiF)/LMPiE)
                
pullcanvaslmpi = TCanvas("pullcanvaslmpi","pullcanvaslmpi",800,800)
pullcanvaslmpi.Divide(2,2)
pullcanvaslmpi.cd(1)
gen_lmpi.Fit("gaus")
gen_lmpi.Draw("PE")
pullcanvaslmpi.cd(2)
fitted_lmpi.Draw("PE")
fitted_lmpi.Fit("gaus")
pullcanvaslmpi.cd(3)
errf_lmpi.Fit("gaus")
errf_lmpi.Draw("PE")
pullcanvaslmpi.cd(4)
pull_lmpi.Fit("gaus")
pull_lmpi.Draw("PE")

if largeToys:
    pullcanvaslmpi.Print(outputdir+"PullPlot_DsPi_Mass_Large_LMPi.pdf")
else :
    pullcanvaslmpi.Print(outputdir+"PullPlot_DsPi_Mass_LMPi.pdf")
                
'''
gen_dspi    = TH1F("gen_dspi","gen_dspi",500,0,1000)
gen_dspi.GetXaxis().SetTitle("Generated dspi events")
fitted_dspi = TH1F("fitted_dspi","fitted_dspi",500,0,1000)
fitted_dspi.GetXaxis().SetTitle("Fitted dspi events")
errf_dspi   = TH1F("errf_dspi","errf_dspi",100,0,500)
errf_dspi.GetXaxis().SetTitle("Fitted error")
pull_dspi   = TH1F("pull_dspi","pull_dspi",nbinspull,lowerpullrange,upperpullrange)
pull_dspi.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    DsPiF = numfitted["DsPi1"][thistoy][0] + numfitted["DsPi2"][thistoy][0] + numfitted["DsPi3"][thistoy][0] + numfitted["DsPi4"][thistoy][0] + numfitted["DsPi5"][thistoy][0]
    DsPi1E = numfitted["DsPi1"][thistoy][1]
    DsPi2E = numfitted["DsPi2"][thistoy][1]
    DsPi3E = numfitted["DsPi3"][thistoy][1]
    DsPi4E = numfitted["DsPi4"][thistoy][1]
    DsPi5E = numfitted["DsPi5"][thistoy][1]
    DsPiE = sqrt( (DsPi1E*DsPi1E)+(DsPi2E*DsPi2E)+(DsPi3E*DsPi3E)+(DsPi4E*DsPi4E)+(DsPi5E*DsPi5E))
    
    gen_dspi.Fill(numevents["DsPi"][thistoy])
    fitted_dspi.Fill(DsPiF)
    errf_dspi.Fill(DsPiE)
    pull_dspi.Fill((numgenevt["DsPi"][thistoy]-DsPiF)/(DsPiE))
    
pullcanvasdspi = TCanvas("pullcanvasdspi","pullcanvaslmpi",800,800)
pullcanvasdspi.Divide(2,2)
pullcanvasdspi.cd(1)
gen_dspi.Draw("PE")
pullcanvasdspi.cd(2)
fitted_dspi.Draw("PE")
fitted_dspi.Fit("gaus")
pullcanvasdspi.cd(3)
errf_dspi.Draw("PE")
pullcanvasdspi.cd(4)
pull_dspi.Fit("gaus")
pull_dspi.Draw("PE")


if largeToys:
    pullcanvasdspi.Print(outputdir+"PullPlot_DsK_Mass_Large_DsPi.pdf")
else :
    pullcanvasdspi.Print(outputdir+"PullPlot_DsK_Mass_DsPi.pdf")
'''
'''
gen_dsp    = TH1F("gen_dsp","gen_dsp",100,0,700)
gen_dsp.GetXaxis().SetTitle("Generated Dsp events")
fitted_dsp = TH1F("fitted_dsp","fitted_dsp",100,0,700)
fitted_dsp.GetXaxis().SetTitle("Fitted dsp events")
errf_dsp   = TH1F("errf_dsp","errf_dsp",100,0,500)
errf_dsp.GetXaxis().SetTitle("Fitted error")
pull_dsp   = TH1F("pull_dsp","pull_dsp",50,-5,5)
pull_dsp.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    DspF = numfitted["Dsp1"][thistoy][0] + numfitted["Dsp2"][thistoy][0] + numfitted["Dsp3"][thistoy][0] + numfitted["Dsp4"][thistoy][0] + numfitted["Dsp5"][thistoy][0]
    Dsp1E = numfitted["Dsp1"][thistoy][1]
    Dsp2E = numfitted["Dsp2"][thistoy][1]
    Dsp3E = numfitted["Dsp3"][thistoy][1]
    Dsp4E = numfitted["Dsp4"][thistoy][1]
    Dsp5E = numfitted["Dsp5"][thistoy][1]
    DspE = sqrt( (Dsp1E*Dsp1E)+(Dsp2E*Dsp2E)+(Dsp3E*Dsp3E)+(Dsp4E*Dsp4E)+(Dsp5E*Dsp5E))
                            
    gen_dsp.Fill(numevents["Dsp"][thistoy])
    fitted_dsp.Fill(DspF)
    errf_dsp.Fill(DspE)
    pull_dsp.Fill((numgenevt["Dsp"][thistoy]-DspF)/DspE)
    
pullcanvasdsp = TCanvas("pullcanvasdsp","pullcanvasdsp",800,800)
pullcanvasdsp.Divide(2,2)
pullcanvasdsp.cd(1)
gen_dsp.Draw("PE")
pullcanvasdsp.cd(2)
fitted_dsp.Draw("PE")
fitted_dsp.Fit("gaus")
pullcanvasdsp.cd(3)
errf_dsp.Draw("PE")
pullcanvasdsp.cd(4)
pull_dsp.Fit("gaus")
pull_dsp.Draw("PE")

if largeToys:
    pullcanvasdsp.Print(outputdir+"PullPlot_DsK_Mass_Large_Dsp.pdf")
else :
    pullcanvasdsp.Print(outputdir+"PullPlot_DsK_Mass_Dsp.pdf")
'''

gen_f1    = TH1F("gen_f1","gen_f1",100,0.5,1)
gen_f1.GetXaxis().SetTitle("Generated g1_f1 events")
fitted_f1 = TH1F("fitted_f1","fitted_f5",100,0.5,1)
fitted_f1.GetXaxis().SetTitle("Fitted g1_f1 events")
errf_f1   = TH1F("errf_f1","errf_f1",100,0,0.3)
errf_f1.GetXaxis().SetTitle("Fitted error")
pull_f1   = TH1F("pull_f1","pull_f1",nbinspull,lowerpullrange,upperpullrange)
pull_f1.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_f1.Fill(numgenevt["g1_f1"][thistoy])
    fitted_f1.Fill(numfitted["g1_f1"][thistoy][0])
    errf_f1.Fill(numfitted["g1_f1"][thistoy][1])
    pull_f1.Fill((numgenevt["g1_f1"][thistoy]-numfitted["g1_f1"][thistoy][0])/numfitted["g1_f1"][thistoy][1])
    
pullcanvasf1 = TCanvas("pullcanvasf1","pullcanvasf1",1500,500)
pullcanvasf1.Divide(3,1)
#pullcanvasf5.cd(1)
#gen_f5.Fit("gaus")
#gen_f5.Draw("PE")
pullcanvasf1.cd(1)
fitted_f1.Draw("PE")
fitted_f1.Fit("gaus")
pullcanvasf1.cd(2)
errf_f1.Fit("gaus")
errf_f1.Draw("PE")
pullcanvasf1.cd(3)
pull_f1.Fit("gaus")
pull_f1.Draw("PE")

if largeToys:
    pullcanvasf1.Print(outputdir+"PullPlot_DsPi_Mass_Large_f1g1.pdf")
else :
    pullcanvasf1.Print(outputdir+"PullPlot_DsPi_Mass_f1g1.pdf")
                
'''
gen_f2    = TH1F("gen_f2","gen_f2",100,0.4,1)
gen_f2.GetXaxis().SetTitle("Generated g2_f1 events")
fitted_f2 = TH1F("fitted_f2","fitted_f2",100,0.4,1)
fitted_f2.GetXaxis().SetTitle("Fitted g2_f1 events")
errf_f2   = TH1F("errf_f2","errf_f2",100,0,0.3)
errf_f2.GetXaxis().SetTitle("Fitted error")
pull_f2   = TH1F("pull_f2","pull_f2",50,-5,5)
pull_f2.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_f2.Fill(numgenevt["g2_f1"][thistoy])
    fitted_f2.Fill(numfitted["g2_f1"][thistoy][0])
    errf_f2.Fill(numfitted["g2_f1"][thistoy][1])
    pull_f2.Fill((numgenevt["g2_f1"][thistoy]-numfitted["g2_f1"][thistoy][0])/numfitted["g2_f1"][thistoy][1])
    
pullcanvasf2 = TCanvas("pullcanvasf2","pullcanvasf2",1500,500)
pullcanvasf2.Divide(3,1)
#pullcanvasf2.cd(1)
#gen_f2.Fit("gaus")
#gen_f2.Draw("PE")
pullcanvasf2.cd(1)
fitted_f2.Draw("PE")
fitted_f2.Fit("gaus")
pullcanvasf2.cd(2)
errf_f2.Fit("gaus")
errf_f2.Draw("PE")
pullcanvasf2.cd(3)
pull_f2.Fit("gaus")
pull_f2.Draw("PE")

if largeToys:
    pullcanvasf2.Print(outputdir+"PullPlot_DsK_Mass_Large_f2g1.pdf")
else :
    pullcanvasf2.Print(outputdir+"PullPlot_DsK_Mass_f2g1.pdf")

exit(0)
gen_f3    = TH1F("gen_f3","gen_f3",100,0,1)
gen_f3.GetXaxis().SetTitle("Generated g3_f1 events")
fitted_f3 = TH1F("fitted_f3","fitted_f3",100,0,1)
fitted_f3.GetXaxis().SetTitle("Fitted g3_f1 events")
errf_f3   = TH1F("errf_f3","errf_f3",100,0,100)
errf_f3.GetXaxis().SetTitle("Fitted error")
pull_f3   = TH1F("pull_f3","pull_f3",50,-5,5)
pull_f3.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_f3.Fill(numgenevt["g3_f1"][thistoy])
    fitted_f3.Fill(numfitted["g3_f1"][thistoy][0])
    errf_f3.Fill(numfitted["g3_f1"][thistoy][1])
    pull_f3.Fill((numgenevt["g3_f1"][thistoy]-numfitted["g3_f1"][thistoy][0])/numfitted["g3_f1"][thistoy][1])

pullcanvasf3 = TCanvas("pullcanvasf2","pullcanvasf2",800,800)
pullcanvasf3.Divide(2,2)
pullcanvasf3.cd(1)
gen_f3.Draw("PE")
pullcanvasf3.cd(2)
fitted_f3.Draw("PE")
fitted_f3.Fit("gaus")
pullcanvasf3.cd(3)
errf_f3.Draw("PE")
pullcanvasf3.cd(4)
pull_f3.Fit("gaus")
pull_f3.Draw("PE")

if largeToys:
    pullcanvasf3.Print(outputdir+"PullPlot_DsK_Mass_Large_f3g1.pdf")
else :
    pullcanvasf3.Print(outputdir+"PullPlot_DsK_Mass_f3g1.pdf")
                
                                    
exit(0)

gen_dk    = TH1F("gen_dk","gen_dk",100,0,100)
gen_dk.GetXaxis().SetTitle("Generated DK events")
fitted_dk = TH1F("fitted_dk","fitted_dk",100,0,100)
fitted_dk.GetXaxis().SetTitle("Fitted dk events")
errf_dk   = TH1F("errf_dk","errf_dk",100,0,100)
errf_dk.GetXaxis().SetTitle("Fitted error")
pull_dk   = TH1F("pull_dk","pull_dk",50,-5,5)
pull_dk.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_dk.Fill(numevents["DK"][thistoy])
    fitted_dk.Fill(numfitted["DK"][thistoy][0])
    errf_dk.Fill(numfitted["DK"][thistoy][1])
    pull_dk.Fill((numgenevt["DK"][thistoy]-numfitted["DK"][thistoy][0])/numfitted["DK"][thistoy][1])

pullcanvasdk = TCanvas("pullcanvasdk","pullcanvasdk",800,800)
pullcanvasdk.Divide(2,2)
pullcanvasdk.cd(1)
gen_dk.Draw("PE")
pullcanvasdk.cd(2)
fitted_dk.Draw("PE")
fitted_dk.Fit("gaus")
pullcanvasdk.cd(3)
errf_dk.Draw("PE")
pullcanvasdk.cd(4)
pull_dk.Fit("gaus")
pull_dk.Draw("PE")

if largeToys:
    pullcanvasdk.Print(outputdir+"PullPlot_DsK_Mass_Large_DK.pdf")
else :
    pullcanvasdk.Print(outputdir+"PullPlot_DsK_Mass_DK.pdf")

gen_lck    = TH1F("gen_lck","gen_lck",100,0,100)
gen_lck.GetXaxis().SetTitle("Generated LcK events")
fitted_lck = TH1F("fitted_lck","fitted_lck",100,0,100)
fitted_lck.GetXaxis().SetTitle("Fitted lck events")
errf_lck   = TH1F("errf_lck","errf_lck",100,0,100)
errf_lck.GetXaxis().SetTitle("Fitted error")
pull_lck   = TH1F("pull_lck","pull_lck",50,-5,5)
pull_lck.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_lck.Fill(numevents["LcK"][thistoy])
    fitted_lck.Fill(numfitted["LcK"][thistoy][0])
    errf_lck.Fill(numfitted["LcK"][thistoy][1])
    pull_lck.Fill((numgenevt["LcK"][thistoy]-numfitted["LcK"][thistoy][0])/numfitted["LcK"][thistoy][1])
                    
pullcanvaslck = TCanvas("pullcanvaslck","pullcanvaslck",800,800)
pullcanvaslck.Divide(2,2)
pullcanvaslck.cd(1)
gen_lck.Draw("PE")
pullcanvaslck.cd(2)
fitted_lck.Draw("PE")
fitted_lck.Fit("gaus")
pullcanvaslck.cd(3)
errf_lck.Draw("PE")
pullcanvaslck.cd(4)
pull_lck.Fit("gaus")
pull_lck.Draw("PE")

if largeToys:
    pullcanvaslck.Print(outputdir+"PullPlot_DsK_Mass_Large_LcK.pdf")
else :
    pullcanvaslck.Print(outputdir+"PullPlot_DsK_Mass_LcK.pdf")
                
'''
