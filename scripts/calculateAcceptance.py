# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to compare datas or pdfs                                    #
#                                                                             #
#   Example usage:                                                            #
#      python comparePDF.py                                                   #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#           Vava Gligorov                                                     #
#   Date  : 28 / 09 / 2016                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
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

from optparse import OptionParser
from math     import pi, log, sqrt
import os, sys, gc

gROOT.SetBatch()                                                                                                  


def printVar( var, label ):
    
    print "---------------------------------------------------------"
    print "[INFO] Printing variables for %s"%(label)
    print "---------------------------------------------------------"
    if ( type(var) == list ):
        for v in var:
            print "[INFO] Parameter: %s with value: %0.6lf +/- %0.6lf"%(v.GetName(),v.getValV(),v.getError())
    else:
        for v in var: 
            print "[INFO] Parameter: %s with value: %0.6lf +/- %0.6lf"%(var[v]["Name"],float(var[v]["Val"]), float(var[v]["Err"]))
    print "---------------------------------------------------------"


def printForConfigFile(var, label, size):
    print "---------------------------------------------------------"
    print "[INFO] Printing variables for %s"%(label)
    print "---------------------------------------------------------"
    string = "["
    for v in var:
        if v > size-1: continue 
        string = string + str(var[v]["Val"]) 
        if v != size and v != size -1:
            string = string + ", "
    string = string + "]" 
    print string 

def getRatio( var1, var2, var3):

    size = len(var1) 
    ratio= {}
    
    if len(var3) > 0.0:
        print "[INFO] Obtaining MC Bs2DsK / MC Bs2DsPi * Data Bs2DsPi"
    else:
        print "[INFO] Obtaining MC Bs2DsK / MC Bs2DsPi"


    for i in range(0,size):
        ratio[i+1] = {} 
        val1 = var1[i].getValV()
        val2 = var2[i].getValV()
        err1 = var1[i].getError()
        err2 = var2[i].getError()
        sV1 = val1*val1
        sE1 = err1*err1
        sV2 = val2*val2
        sE2 = err2*err2 
        ratio[i+1]["Name"] = var1[i].GetName()

        if len(var3) > 0.0:
            val3 = var3[i].getValV()
            err3 = var3[i].getError()
            sV3 = val3*val3
            sE3 = err3*err3
            ratio[i+1]["Val"] = val1/val2*val3
            ratio[i+1]["Err"] = ratio[i+1]["Val"]*sqrt( sE1/ sV1 + sE2/sV2 + sE3/sV3 )

        else: 
            ratio[i+1]["Val"] = val1/val2
            ratio[i+1]["Err"] = ratio[i+1]["Val"]*sqrt( sE1/ sV1 + sE2/sV2 )  
 
    return ratio

def printLatex(varDsK, varDsPi, ratio, bla):

    size = len(varDsK)

    print "---------------------------------------------------------------------"
    print "Printing Latex style: READY TO PUT IN ANA NOTE :-)"
    print "---------------------------------------------------------------------"

    print "\hline" 
    if bla:
        print "Parameters & Fit to \BsDsK       & Fit to \BsDsPi      & $\BsDsK/\BsDsPi$ \\"
    else:
        print "Parameters & Fit to MC \BsDsK       & Fit to MC \BsDsPi      & \BsDsK acceptance in data \\"
    print "\hline \hline"
    for i in range(0,size):
        print "$v_{%1.0lf}$    & %0.3lf $\pm$ %0.3lf   & %0.3lf $\pm$ %0.3lf   & %0.3lf $\pm$ %0.3lf \\"%(float(i+1), 
                                                                                                          varDsK[i].getValV(),varDsK[i].getError(),
                                                                                                          varDsPi[i].getValV(), varDsPi[i].getError(),
                                                                                                          float(ratio[i+1]["Val"]), float(ratio[i+1]["Err"]))
    print "\hline"
        

def calculateAcceptance( debug, 
                         fileMCDsK, fileMCDsPi, fileData, 
                         workNameMCDsK, workNameMCDsPi, workNameData, num) :

    print "[INFO] File MC Bs2DsK: ",fileMCDsK
    print "[INFO] File MC Bs2DsPi: ",fileMCDsPi
    if fileData != "":
        print "[INFO] file Data Bs2DsPi: ",fileData

    workMCDsK  = GeneralUtils.LoadWorkspace(TString(fileMCDsK), TString(workNameMCDsK),debug)
    workMCDsPi = GeneralUtils.LoadWorkspace(TString(fileMCDsPi),TString(workNameMCDsPi),debug)

    rfr_dsk_mc  = workMCDsK.obj("fitresult_time_signal_data_fit_binned")
    rfr_dspi_mc = workMCDsPi.obj("fitresult_time_signal_data_fit_binned")
 
    cov_dsk_mc       = rfr_dsk_mc.covarianceMatrix()
    cov_dspi_mc      = rfr_dspi_mc.covarianceMatrix()
    pars_fin_dsk_mc  = rfr_dsk_mc.floatParsFinal()
    pars_fin_dspi_mc = rfr_dspi_mc.floatParsFinal()
    # Now prepare for the ratio
    resvect_dsk      = ROOT.TVectorT('double')(6)
    resvect_dspi     = ROOT.TVectorT('double')(6)
    resvect_ratio    = ROOT.TVectorT('double')(6)
    for i in range(0,6) : 
        resvect_dsk[i]    = pow(pars_fin_dsk_mc[i].getVal(),2)
        resvect_dspi[i]   = pow(pars_fin_dspi_mc[i].getVal(),2)
        resvect_ratio[i]  = pow(pars_fin_dsk_mc[i].getVal()/pars_fin_dspi_mc[i].getVal(),2)
    cov_dsk_mc.NormByDiag(resvect_dsk)
    cov_dspi_mc.NormByDiag(resvect_dspi)
    ratiocov_mc   = cov_dsk_mc
    ratiocov_mc  += cov_dspi_mc
    ratiocov_mc.NormByDiag(resvect_ratio,"M")

    print "//////////////////////////////////"
    print "/Correlation of DsK/DsPi MC ratio/"
    print "//////////////////////////////////"
    print "\hline"
    print "        & $v_{1}$ & $v_{2}$ & $v_{3}$ & $v_{4}$ & $v_{5}$ & $v_{6}$ \\\\" 
    print "\hline"
    for i in range(0,6) :
        toprint = "$v_{"+str(i+1)+"}$ &"
        for j in range(0,6) :
            if i == j : 
                toprint += "  1.00   "
            else :
                toprint += "  "+format(ratiocov_mc[i][j]/sqrt(ratiocov_mc[i][i]*ratiocov_mc[j][j]),'.2f')+"   "
            if j < 5 :
                toprint += "&"
            else :
                toprint += "\\\\"
        print toprint
    print "\hline"
    print "//////////////////////////////////" 

    if fileData != "":
        workData = GeneralUtils.LoadWorkspace(TString(fileData),TString(workNameData),debug)
        rfr_data = workData.obj("fitresult_signal_TimeTimeerrPdf_dataWA_binned")

        pars_fit_data = rfr_data.floatParsFinal()
        totcov_mc = rfr_data.covarianceMatrix()
        totcov_mc_red = ROOT.TMatrixTSym('double')(6,6)
        totcov_mc.GetSub(1,6,1,6,totcov_mc_red)

        resvect_data = ROOT.TVectorT('double')(6) 
        resvect_final = ROOT.TVectorT('double')(6)
        for i in range(0,6) :
            resvect_data[i] = pow(pars_fit_data[i+1].getVal(),2)
            resvect_final[i] = resvect_data[i]*resvect_ratio[i]
        ratiocov_mc.NormByDiag(resvect_ratio)
        totcov_mc_red.NormByDiag(resvect_data)

        totcov_mc_red += ratiocov_mc
        totcov_mc_red.NormByDiag(resvect_final,"M") 
    
        print "///////////////////////////////////////////////"
        print "/Correlation of DsPi data times DsK/DsPi ratio/"
        print "///////////////////////////////////////////////"
        print "\hline"
        print "        & $v_{1}$ & $v_{2}$ & $v_{3}$ & $v_{4}$ & $v_{5}$ & $v_{6}$ \\\\" 
        print "\hline"
        for i in range(0,6) :
            toprint = "$v_{"+str(i+1)+"}$ &"
            for j in range(0,6) :
              if i == j : 
                  toprint += "  1.00   "
              else :
                  toprint += "  "+format(totcov_mc_red[i][j]/sqrt(totcov_mc_red[i][i]*totcov_mc_red[j][j]),'.2f')+"   "
              if j < 5 :
                  toprint += "&"
              else :
                  toprint += "\\\\"
            print toprint
        print "\hline"
        print "///////////////////////////////////////////////"  

    varDsK = []
    varDsPi = [] 
    varData = [] 
    
    for i in range(0,int(num)):
        varName = "var"+str(i+1) 
        varDsK.append(GeneralUtils.GetObservable(workMCDsK,TString(varName), debug))
        varDsPi.append(GeneralUtils.GetObservable(workMCDsPi,TString(varName), debug))
    
        
    if fileData != "":
        for i in range(0,int(num)):
            varName= "var"+str(i+1)
            varData.append(GeneralUtils.GetObservable(workData,TString(varName), debug))

    printVar(varDsK, "MC Bs2DsK")
    printVar(varDsPi, "MC Bs2DsPi")
    
    if fileData != "":
        printVar(varData, "Data Bs2DsPi") 

    ratio = getRatio(varDsK, varDsPi, varData)

    printVar(ratio, "ratio")
    printForConfigFile(ratio,"config file: ratio", len(varDsK))
  
    if fileData == "":
        printLatex(varDsK, varDsPi, ratio, True)
    else:
        printLatex(varDsK, varDsPi, ratio, False)

#------------------------------------------------------------------------------                                                                                                                 
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--fileMCDsK',
                   dest = 'fileMCDsK',
                   default = 'WS_Splines_Bs2DsK.root')

parser.add_option( '--fileMCDsPi',
                   dest = 'fileMCDsPi',
                   default = 'WS_Splines_Bs2DsPi.root')

parser.add_option( '--fileDataDsPi',
                   dest = 'fileDataDsPi',
                   default = '')

parser.add_option( '--workMCDsK',
                   dest = 'workMCDsK',
                   default = 'workspace')

parser.add_option( '--workMCDsPi',
                   dest = 'workMCDsPi',
                   default = 'workspace')

parser.add_option( '--workDataDsPi',
                   dest = 'workDataDsPi',
                   default = 'workspace')

parser.add_option( '--splineNum', '--num',
                   dest = 'num',
                   default = 7.0)



# -----------------------------------------------------------------------------                                                                                                                 

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )


    import sys
    sys.path.append("../data/")

    calculateAcceptance( options.debug,
                         options.fileMCDsK, options.fileMCDsPi, options.fileDataDsPi, 
                         options.workMCDsK, options.workMCDsPi, options.workDataDsPi,
                         options.num
                         )
# ----------------------------------------------------------------------------- 
