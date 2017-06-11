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
from math     import pi, log, sqrt
import os, sys, gc
gROOT.SetBatch()
gStyle.SetOptStat(0)
gStyle.SetOptFit(1011)


#---------------------------------------------
# get sum of entries
#---------------------------------------------

def getSumOfEntries(myconfigfile, decayType):
    charmModes = myconfigfile["CharmModes"]
    years = myconfigfile["Years"]
    hypo = myconfigfile["Hypothesys"]

    decayYield = 0
    
    for h in hypo:
        for Dmode in charmModes:
            for y in years: 
                decayYield = decayYield + int(myconfigfile["Components"][decayType][h][y][Dmode][0]) 
            
    return decayYield 

#---------------------------------------------
# find failed toys
#---------------------------------------------
def getFailedToys(myconfigfile, debug, toysdir, nickname, start, stop):
    nfailed = []
    #prefix = "log_Nominal_22082016_"
    prefix = "log_Nominal_"
    suffix = ".txt"

    for thistoy in range(start, stop) :
        f = open(toysdir+prefix+str(thistoy)+suffix)
        counter = 0
        counterstop = -100
        badfit = False
        #print "Processing toy",thistoy
        for line in f :
            counter += 1
            if line.find('NOT POS-DEF') > -1 :
                badfit = True
            if line.find('ERROR MATRIX ACCURATE') > -1 :
                badfit = False
            if line.find("covariance matrix quality: Full, accurate covariance matrix")>-1:
                badfit = False 
            if line.find('FinalValue') >  -1:
                if badfit :
                    nfailed.append(thistoy)
                    break 
        del f 

    if debug:
        print "Number of failed toys: ", len(nfailed)/float(stop-start)," [%]"
    return nfailed 


#--------------------------------------------------
# get sum of yields
#--------------------------------------------------
def getSum(val, err):
    
    globalVal = 0.0
    for v in val:
        #print v, globalVal 
        globalVal = globalVal + v 

    globalErr = 0.0 
    for e in err:
        e2 = e*e
        #print e, e2
        globalErr = globalErr + e2
        #print globalErr 

    globalErr = sqrt(globalErr) 
    #print globalErr 

    return globalVal, globalErr 

#-------------------------------------------------
# get fitted yields from toys
#-------------------------------------------------

def getYieldsFromFile(myconfigfile, debug, directory, nickname, start, stop):

    eventType = myconfigfile["CombinedYields"]

    root = ".root"
    #fileName = "WS_MDFit_Bs2DsPi_Nominal_22082016_"
    fileName = "WS_MDFit_Bs2DsK_Nominal_"
    CharmModes = myconfigfile["CharmModes"]
    years = myconfigfile["Years"]
    hypo = myconfigfile["Hypothesys"]
    if myconfigfile.has_key("MergedYears"):
        if myconfigfile["MergedYears"] == True:
            years = [TString("run1")] 
    
    sample = [TString("both")]
    t = TString("_") 
    sm = []
    for y in years:
        for s in sample:
            for chm in CharmModes:
                m = GeneralUtils.GetModeLower(TString(chm),debug)
                sm.append(s+t+m+t+TString(y))

    yields = {} 
    for thistoy in range(start, stop) :
        print "Progressing toy: ",thistoy 
        yields[thistoy] = {} 


        fileResult = TFile.Open(directory+fileName+str(thistoy)+root) 
        workResult = RooWorkspace(fileResult.Get("FitMeToolWS"))

        for eT in eventType:
            dT = eT
            if eT == "Signal":
                dT = "Sig"
            if eT == "Combinatorial":
                dT = "CombBkg"

            print eT, dT
            yields[thistoy][eT] = {} 
            val = []
            err = [] 
            for samplemode in sm:
                var  = workResult.var("n%s_%s_Evts"%(dT,samplemode.Data()))
                if var:
                    val.append(var.getValV())
                    err.append(var.getError())
                else:
                    val.append(0.0)
                    err.append(0.0) 

 #           print val, err 
            gVal, gErr = getSum(val, err)
            print gVal, gErr 
            yields[thistoy][eT]["Err"] = gErr
            yields[thistoy][eT]["Val"] = gVal 

            del val
            del err 
        del workResult
        del fileResult 

    print yields 
    return yields

#---------------------------------------------------------
# merge generated yields
#---------------------------------------------------------

def mergeGeneratedYields(myconfigfile, genYields):

    #print genYields 
    
    mergedGeneratedYields = {}
    eventType = myconfigfile["CombinedYields"]

    for eType in eventType:
        suma = 0.0
        for skl in myconfigfile["CombinedYields"][eType]:
            #print skl 
            suma = suma + genYields[skl]
            
        mergedGeneratedYields[eType] = suma

    return mergedGeneratedYields


def makeHistograms(myconfigfile, yields, merge, nfailed, directory,debug):

    eventType = myconfigfile["CombinedYields"]

    for eType in eventType:
#        print eType 
        genEv = merge[eType]
        
        for thistoy in yields:
            avErr = yields[thistoy][eType]["Err"]
            i = 1.0
            if i == 1.0:
                break 

        #print genEv 
        #print avErr 
        
        gen    = TH1F("gen_%s"%(eType),"gen_%s"%(eType),100,genEv*0.8,genEv*1.2)
        gen.GetXaxis().SetTitle("Generated %s events"%(eType))
        fitted = TH1F("fitted_%s"%(eType),"fitted_%s"%(eType),100,genEv*0.9,genEv*1.1)
        fitted.GetXaxis().SetTitle("Fitted %s events"%(eType))
        errf   = TH1F("errf_%s"%(eType),"errf_%s"%(eType),100,avErr*0.9,avErr*1.1)
        errf.GetXaxis().SetTitle("Fitted %s error"%(eType))
        pull  = TH1F("pull_%s"%(eType),"pull_%s"%(eType),100, -3.0, 3.0) #nbinspull,lowerpullrange,upperpullrange)
        pull.GetXaxis().SetTitle("Fitted Pull")


        for thistoy in yields :
            if debug:
                print "type %s, generated: %lf, fitted: %s +/- %s, pull %s"%(eType, genEv, 
                                                                             yields[thistoy][eType]["Val"], 
                                                                             yields[thistoy][eType]["Err"], 
                                                                             (genEv-yields[thistoy][eType]["Val"])/yields[thistoy][eType]["Err"]) 
            if thistoy in nfailed : continue
            gen.Fill(genEv)
            fitted.Fill(yields[thistoy][eType]["Val"])
            errf.Fill(yields[thistoy][eType]["Err"])
            pull.Fill((genEv-yields[thistoy][eType]["Val"])/yields[thistoy][eType]["Err"])
            
        canvas = TCanvas("canvas_%s"%(eType),"canvas_%s"%(eType),1200,1200)
        canvas.Divide(2,2)
        canvas.cd(1)
        print "######################### Generated #######################"
        gen.Fit("gaus")
        gen.Draw("PE")
        canvas.cd(2)
        print "########################## Fitted #########################"
        fitted.Draw("PE")
        fitted.Fit("gaus")
        canvas.cd(3)
        print "########################## Error ##########################"
        errf.Fit("gaus")
        errf.Draw("PE")
        canvas.cd(4)
        print "########################## Pull ##########################"
        pull.Fit("gaus")
        pull.Draw("PE")
        #canvas.SaveAs("%s/pulls_%s.pdf"%(directory,eType))
        canvas.SaveAs("pulls_%s.pdf"%(eType))
        

#-----------------------------------------------------------
# the main function
#-----------------------------------------------------------

def getResults(configName, debug, directory, nickname, start, stop):
    
    # Get the configuration file                                                                                                                                                               
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "RUN MD FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="


    RooAbsData.setDefaultStorageType(RooAbsData.Tree)

    eventtype = myconfigfile["TrueID"] 

    print eventtype 
    genYields = {} 
    for ev in eventtype: 
        yieldDecay = getSumOfEntries(myconfigfile, ev)
        genYields[ev] = {}
        genYields[ev] = yieldDecay 
        
    mergedGeneratedYields = mergeGeneratedYields(myconfigfile, genYields) 
    print genYields 
    print mergedGeneratedYields 
    
#    exit(0) 

    #print directory 
    nfailed = getFailedToys(myconfigfile, debug, directory, nickname, start, stop)
    print nfailed

    yields = getYieldsFromFile(myconfigfile, debug, directory, nickname, start, stop)
    
    makeHistograms(myconfigfile, yields, mergedGeneratedYields, nfailed, directory, debug) 
    
    
    
   

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
                   default = '../data/Bs2DsK_3fbCPV/Bs2DsK/Bs2DsKConfigForNominalMassFit.py',
                   help = "name of the configuration file, the full path to the file is mandatory")
parser.add_option( '--directory',"--dir",
                   dest = 'directory',
                   default = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys3fb/Nominal_22082016/MDFit/',
                   help = "toys directory")
parser.add_option( '--nickname',"--nick",
                   dest = 'nick',
                   default = 'Nominal_22082016',
                   help = "nickname")
parser.add_option( '--start',
                   dest = 'start',
                   default = 1000,
                   help = "start (seed number)")
parser.add_option( '--stop',
                   dest = 'stop',
                   default = 1500,
                   help = "stop (seed number + number of toys)")


#------------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
    config = options.configName
    last = config.rfind("/")
    directoryConf = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]

    import sys
    sys.path.append(directoryConf)


    getResults( configName, options.debug, options.directory, 
                options.nick,
                int(options.start), int(options.stop)) 
