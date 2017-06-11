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
#"
from B2DXFitters import *
from ROOT import *

from ROOT import RooFit
from optparse import OptionParser

import math 
from math     import pi, log, sqrt

import os, sys, gc

import uncertainties
from uncertainties import ufloat

gROOT.SetBatch()
gStyle.SetOptStat(0)
gStyle.SetOptFit(1011)

# -----------------------------------------------------------------------------
# Common input stuff and options
massfitdescr=''
timefitdescr=''
nickname='SgnAndBkgTwoTaggersProdAsymm001AccMeanResTimeFrom02ps'
debugplots = False

#Uncomment this for mass fit
#massfitdescr='FitB_FullMDFit'
#inputfile = '/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/'+nickname+'/'+'MDFit/PullTree'+massfitdescr+'_'+nickname+'.root'
#outputdir = '/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/'+nickname+'/MassPullsB/'
#selection = 'CovQual == 3 && MINUITStatus == 0 && edm!=0 && edm<0.1'

#Uncomment this for time fit
massfitdescr="FullMDFit"
timefitdescr='SSbarFloating'
inputfile = '/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/'+nickname+'/TimeFit/PullTreeTimeFit_'+nickname+'_'+timefitdescr+'_'+massfitdescr+'.root'
outputdir = '/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/'+nickname+'/TimePulls/'
selection = 'MINUITStatus == 0 && edm!=0 && Sf_err < 0.03 && Sfbar_err < 0.03'

#Leave as it is
inputFile = TFile.Open(inputfile,"READ")
PullTree = inputFile.Get("PullTree")
LeafList = PullTree.GetListOfLeaves()

# -----------------------------------------------------------------------------
plotlabel=''
if massfitdescr == "" and timefitdescr == "":
    print "ERROR: choose nicknames for mass or time fit!"
    exit(-1)
elif massfitdescr != "" and timefitdescr == "":
    plotlabel=massfitdescr
elif massfitdescr == "" and timefitdescr != "":
    plotlabel=timefitdescr
else:
    plotlabel=massfitdescr+"_"+timefitdescr

print "Plot label: "+plotlabel

os.system( "rm -r "+outputdir ) #be careful...
os.system( "mkdir -p "+outputdir )

# -----------------------------------------------------------------------------
def makeprintout(canvas,name) :
    # Set all the different types of plots to make
    plottypestomake = [".pdf"]
    for plottype in plottypestomake :
        canvas.Print(name+plottype)

# -----------------------------------------------------------------------------

GenList = []
FitList = []
ErrList = []
NameList = []
nLeaves = LeafList.GetEntries()
print "Leaf list size: ", nLeaves
print "Loop over leaves:"
for leaf in range(0, nLeaves):
    name = TString(LeafList[leaf].GetName())
    print "Leaf: ", name.Data()
    if name.EndsWith("_gen"):
        GenList.append(name.Data())
    if name.EndsWith("_fit"):
        FitList.append(name.Data())
    if name.EndsWith("_err"):
        ErrList.append(name.Data()) 

# 3 leaves per observables, excluding the CovQual/MINUITStatus/edm leaves
nObs = (nLeaves - 3)/3.0

NameList = []
for name in GenList:
    nametmp = TString(name)
    nametmp.ReplaceAll("_gen","")
    NameList.append(nametmp.Data())

# Fill the histograms
for obs in range(0, int(nObs)):
    selection_string=selection+"&&"+"TMath::Abs(("+FitList[obs]+"-"+GenList[obs]+")"+"/"+ErrList[obs]+")<10"
    if "Sf" in ErrList[obs]:
        selection_string = selection_string + "&&"+ErrList[obs]+"<0.1"
    print "Selection:"
    print selection_string

    print "Plotting:"
    print FitList[obs]
    PullTree.Draw(FitList[obs]+">>fitted"+str(obs),selection_string,"goff")
    fitted = gDirectory.Get("fitted"+str(obs))
    fitted.SetTitle("")
    fitted.GetXaxis().SetTitle("Fitted Value")

    print "Plotting:"
    print ErrList[obs]
    PullTree.Draw(ErrList[obs]+">>errf"+str(obs),selection_string,"goff")
    errf = gDirectory.Get("errf"+str(obs))
    errf.SetTitle("Fitted Error")
    plottitle = str(GenList[obs]).replace("_gen","")
    errf.SetTitle(plottitle)
    errf.GetXaxis().SetTitle("Fitted Error")

    print "Plotting:"
    print "("+FitList[obs]+"-"+GenList[obs]+")"+"/"+ErrList[obs]
    PullTree.Draw("("+FitList[obs]+"-"+GenList[obs]+")"+"/"+ErrList[obs]+">>pull"+str(obs),selection_string,"goff")
    pull = gDirectory.Get("pull"+str(obs))
    pull.SetTitle("")
    pull.GetXaxis().SetTitle("Fitted Pull")

    if debugplots:

        PullTree.Draw(FitList[obs]+":"+ErrList[obs]+">>fitVSerr"+str(obs),selection_string,"goff")
        fitVSerr = gDirectory.Get("fitVSerr"+str(obs))
        fitVSerr.SetTitle("")
        fitVSerr.GetXaxis().SetTitle("Fitted Error")
        fitVSerr.GetYaxis().SetTitle("Fitted Value")
        
        PullTree.Draw("("+FitList[obs]+"-"+GenList[obs]+")"+"/"+ErrList[obs]+":"+ErrList[obs]+">>pullVSerr"+str(obs),selection_string,"goff")
        pullVSerr = gDirectory.Get("pullVSerr"+str(obs))
        pullVSerr.SetTitle("")
        pullVSerr.GetXaxis().SetTitle("Fitted Error")
        pullVSerr.GetYaxis().SetTitle("Fitted Pull")
        pullVSerr.GetYaxis().SetRangeUser(-5.0,5.0)
        
    gStyle.SetStatX(0.95)
    gStyle.SetStatY(0.95)
    gStyle.SetStatW(0.15)
    gStyle.SetStatH(0.15)
    pullcanvas = TCanvas("pullcanvas"+str(obs),"pullcanvas",1500,500)
    pullcanvas.Divide(3,1)
    pullcanvas.cd(1)
    fitted.Fit("gaus")
    fitted.Draw("PE")
    pullcanvas.cd(2)
    errf.Fit("gaus")
    errf.Draw("PE")
    pullcanvas.cd(3)
    pull.Fit("gaus")
    pull.Draw("PE")
    makeprintout(pullcanvas,outputdir+"1DPullPlot_"+NameList[obs]+"_"+plotlabel)

    if debugplots:
    
        pullcanvas2 = TCanvas("pullcanvas2"+str(obs),"pullcanvas2",1500,500)
        pullcanvas2.Divide(2,1)
        pullcanvas2.cd(1)
        fitVSerr.Draw("CONTZ")
        pullcanvas2.cd(2)
        pullVSerr.Draw("CONTZ")
        makeprintout(pullcanvas2,outputdir+"2DPullPlot_"+NameList[obs]+"_"+plotlabel)
        

ntoys = ufloat(PullTree.GetEntries(), sqrt(PullTree.GetEntries()))
nfailed = ufloat(PullTree.GetEntries("!("+selection+")"), sqrt(PullTree.GetEntries("!("+selection+")")))
print "Selection for failed toys:"
print "!("+selection+")"
print "Number of toys:"
print ntoys
print "Number of failed toys:"
print nfailed
print "Fraction of failed toys:"
print nfailed/ntoys

inputFile.Close()
