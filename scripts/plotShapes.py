# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot background shapes                                   #
#                                                                             #
#   Example usage:                                                            #
#      python plotShapes.py --file work_dspi.root --work workspace            #
#                           --mode BsDsPi  --obs lab1_PIDK  --debug           #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 06 / 10 / 2013                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #
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
from  os.path import exists
import os, sys, gc
gROOT.SetBatch()



#------------------------------------------------------------------------------
def plotShapes( debug, fileName, workName, obs, mode, data ) :

    obsTS = TString(obs)
    modeTS = TString(mode)
    print obs
    print mode
    print fileName
    work = GeneralUtils.LoadWorkspace(TString(fileName),TString(workName),debug)
    obs   = GeneralUtils.GetObservable(work,obsTS, debug)
    t = TString(" ")

    modesDs = ["nonres", "", "phipi", "kstk", "kpipi", "pipipi"]

    if modeTS.Contains("DsPi") == true:
        modes = ["Bd2DsPi","Bs2DsstPi","Bd2DPi","Lb2LcPi","Bs2DsK"]
        color = [kBlue-10, kBlue-10, kOrange-2, kRed, kGreen+3 ]
        style = [1,2,1,1,1]
        ranType = 4
        ran = 5
              
    elif modeTS.Contains("DsK") == true:
        modes = ["Bs2DsRho","Bs2DsstPi", "Lb2Dsp","Lb2Dsstp", "Bd2DK","Lb2LcK"]
        modes5M = "Bs2DsPi"
        color = [kBlue-2, kBlue-2, kYellow+1, kYellow+1, kRed, kGreen+3] 
        style = [1, 2, 1, 2, 1, 1, 1, ]
        color5M = [kBlue-2, kWhite, kBlue-2, kBlue-2, kBlue-2, kBlue-2]
        style5M = [1,1, 2,3,6,9]
        ranType = 4
        ran = 6
                                                                  
    namePrefix = "PhysBkg"
    nameSufix1  = "Pdf_m_both"
    nameSufix2  = "Tot"
    p = "_"
    pTS = TString(p)
    
    names = []
    names5M = []
    namesLatex = []
    pdf = []
    pdf5M = []
    namesLatex5M = []
    for m in modes:
        if m =="Bd2DK" or m == "Lb2LcK":
            n = namePrefix+m+nameSufix1+p+nameSufix2
        else:
            n = namePrefix+m+nameSufix1+p+modesDs[0]+p+nameSufix2
        names.append(n)
        namesLatex.append(GeneralUtils.GetLabel(TString(n),true,false,false,debug))
        
    for m in modesDs:
        if m != "":
            n = namePrefix+modes5M+nameSufix1+p+m+p+nameSufix2
        else:
            n = ""
        names5M.append(n)
        namesLatex5M.append(GeneralUtils.GetLabel(TString(n),false,true,false,debug))
                
    print names
    print namesLatex
    print namesLatex5M
    
    for n in names:
        print n
        pdf.append(Bs2Dsh2011TDAnaModels.GetRooAbsPdfFromWorkspace(work,TString(n), debug))

    for n in names5M:
        print n
        if n != "":
            pdf5M.append(Bs2Dsh2011TDAnaModels.GetRooAbsPdfFromWorkspace(work,TString(n), debug))
                        
    canv = []
    frame = []
    legend = []
    line = []
    line5M = []
    for i in range(0, ranType+1):

        nameCanv =  "can_"+str(i)
        canv.append(TCanvas(nameCanv,nameCanv, 1200,1000))

        frame.append(obs.frame())
        frame[i].SetTitle("")
        frame[i].SetLabelFont(132);
        frame[i].SetTitleFont(132);

        label = GeneralUtils.CheckObservable(obsTS,debug)
        frame[i].GetXaxis().SetTitle(label.Data())
        frame[i].GetYaxis().SetTitle(' ')
        frame[i].GetXaxis().SetLabelFont( 132 );
        frame[i].GetYaxis().SetLabelFont( 132 );
        frame[i].GetXaxis().SetLabelSize( 0.035 );
        frame[i].GetYaxis().SetLabelSize( 0.035 );
           
        if i == ranType:
            if( obsTS == "lab2_MM"):
                legend.append(TLegend( 0.12, 0.53, 0.38, 0.88 ))
            else:
                legend.append(TLegend( 0.55, 0.53, 0.88, 0.88 ))
        else:
            legend.append(TLegend( 0.60, 0.68, 0.88, 0.88 ))

        legend[i].SetTextSize(0.05)
        legend[i].SetTextFont(12)
        legend[i].SetFillColor(4000)
        legend[i].SetShadowColor(0)
        legend[i].SetBorderSize(0)
        legend[i].SetTextFont(132)
        legend[i].SetHeader("LHCb")

    for i in range(0, ran):
        line.append(TLine())
        line[i].SetLineColor(color[i])
        line[i].SetLineWidth(4)
        line[i].SetLineStyle(style[i])

    if modeTS.Contains("DsK") == true:
        for i in range(0,6):
            line5M.append(TLine())
            line5M[i].SetLineColor(color5M[i])
            line5M[i].SetLineWidth(4)
            line5M[i].SetLineStyle(style5M[i])
                        
       
     
    canv[0].cd()
    pdf[0].plotOn(frame[0], RooFit.LineColor(color[0]), RooFit.LineStyle(style[0]))
    pdf[1].plotOn(frame[0], RooFit.LineColor(color[1]), RooFit.LineStyle(style[1]))
    legend[0].AddEntry(line[0], namesLatex[0].Data() , "L")
    legend[0].AddEntry(line[1], namesLatex[1].Data() , "L")
    frame[0].Draw()
    legend[0].Draw("same")
    nameSavePdf = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString("Bs2DsstPiRho.pdf")
    nameSaveRoot = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString("Bs2DsstPiRho.root")
    canv[0].Print(nameSavePdf.Data())
    canv[0].Print(nameSaveRoot.Data())

    if modeTS.Contains("DsPi") == true:
        for i in range(1,ranType):
            canv[i].cd()
            pdf[i+1].plotOn(frame[i],RooFit.LineColor(color[i+1]), RooFit.LineStyle(style[i+1]))
            legend[i].AddEntry(line[i+1], namesLatex[i+1].Data() , "L")
            frame[i].Draw()
            legend[i].Draw("same")
            nameSavePdf = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString(modes[i+1])+TString(".pdf")
            nameSaveRoot = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString(modes[i+1])+TString(".root")
            canv[i].Print(nameSavePdf.Data())
            canv[i].Print(nameSaveRoot.Data())
                    
    else:
        canv[1].cd()
        pdf[2].plotOn(frame[1], RooFit.LineColor(color[2]), RooFit.LineStyle(style[2]))
        pdf[3].plotOn(frame[1], RooFit.LineColor(color[3]), RooFit.LineStyle(style[3]))
        legend[1].AddEntry(line[2], namesLatex[2].Data() , "L")
        legend[1].AddEntry(line[3], namesLatex[3].Data() , "L")
        frame[1].Draw()
        legend[1].Draw("same")
        nameSavePdf = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString("Lb2Dsstp.pdf")
        nameSaveRoot = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString("Lb2Dsstp.root")
        canv[1].Print(nameSavePdf.Data())
        canv[1].Print(nameSaveRoot.Data())
                
        for i in range(2,ranType):
            canv[i].cd()
            pdf[i+2].plotOn(frame[i],RooFit.LineColor(color[i+2]), RooFit.LineStyle(style[i+2]))
            legend[i].AddEntry(line[i+2], namesLatex[i+2].Data() , "L")
            frame[i].Draw()
            legend[i].Draw("same")
            nameSavePdf = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString(modes[i+2])+TString(".pdf")
            nameSaveRoot = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString(modes[i+2])+TString(".root")
            canv[i].Print(nameSavePdf.Data())
            canv[i].Print(nameSaveRoot.Data())
            
        canv[ranType].cd()
        legend[i].SetTextSize(0.03)
        namesLatex5M[0].ReplaceAll("(Non Resonant)","") 
        namesLatex5M[1] = TString("(Non Resonant)")

        pdf5M[0].plotOn(frame[ranType],RooFit.LineColor(color5M[0]), RooFit.LineStyle(style5M[0]))
        for i in range (2,6):
            pdf5M[i-1].plotOn(frame[ranType],RooFit.LineColor(color5M[i]), RooFit.LineStyle(style5M[i]))
        
        for i in range(0,6):
            legend[ranType].AddEntry(line5M[i], namesLatex5M[i].Data() , "L")
        frame[ranType].Draw()
        legend[ranType].Draw("same")
        nameSavePdf = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString(modes5M)+TString(".pdf")
        nameSaveRoot = TString("template")+pTS+modeTS+pTS+obsTS+pTS+TString(modes5M)+TString(".root")
        canv[ranType].Print(nameSavePdf.Data())
        canv[ranType].Print(nameSaveRoot.Data())
        
                                                                                    

#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--file',
                   dest = 'file',
                   default = 'WS_Mass_DsPi_5M_BDTGA.root')

parser.add_option( '--work',
                   dest = 'work',
                   default = 'FitMeToolWS')
parser.add_option( '--obs',
                   dest = 'obs',
                   default = 'lab1_PIDK')
parser.add_option( '--mode',
                   dest = 'mode',
                   default = 'BsDsPi')

parser.add_option( '--data',
                   dest = 'data',
                   action = 'store_true',
                   default = False)

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    plotShapes( options.debug,
                options.file, options.work, 
                options.obs, options.mode,
                options.data
                )                                
# -----------------------------------------------------------------------------
                                
