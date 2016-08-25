#!/bin/tcsh -f 

set seed=$1
set stop=$2
set nickname=$3 
set one = 1

set output = "/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys3fb/${nickname}/Generator/"
set eosoutput="/eos/lhcb/user/a/adudziak/Bs2DsK_3fbCPV/Bs2DsPiToys/${nickname}/Generator/"
set config="/afs/cern.ch/user/a/adudziak/cmtuser/Urania_v3r0/Phys/PhysFit/B2DXFitters/data/Bs2DsK_3fbCPV/Bs2DsPi/Bs2DsPiConfigForToyGenerator.py"

set log = "log_"
set space = "_"
set text = ".txt"
set eosroot = "root://eoslhcb.cern.ch/"

set prefixWork = "GenToyWorkspace_"
set prefixTree = "GenToyTree_"
set root = ".root"
 
echo $seed
echo $stop
echo $eosoutput
echo $nickname
echo $config

set seedStr = "0" 
#Setup environment                                                                                                                                                                               
#source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.csh
#source `which SetupProject.csh` Urania v3r0
#source ../cmt/setup.csh 

while (( $seed < $stop ))
    
    echo $seed 
    #set seed = $seed + $one

    set seedStr = ("$seed") 
    echo $seedStr 
    echo $output$log$nickname$space$seedStr$text
    echo $eosroot$eosoutput$log$nickname$space$seedStr$text

    echo $prefixWork$nickname$space$seedStr$root 
    echo $prefixTree$nickname$space$seedStr$root 
    rm $output$log$nickname$space$seedStr$text
    #rm $eosroot$eosoutput$log$nickname$space$seedStr$text
    #touch $eosroot$eosoutput$log$nickname$space$seedStr$text

    mkdir $output

    python toyFactory.py --saveTree --configName $config --seed $seed --workfileOut $prefixWork$nickname$space$seedStr$root --treefileOut $prefixTree$nickname$space$seedStr$root  --debug --outputdir $output >& $output$log$nickname$space$seedStr$text  

    #xrdcp -f ${output}GenToyWorkspace_${nickname}_${seed}.root root://eoslhcb.cern.ch/${eosoutput}GenToyWorkspace_${nickname}_${seed}.root
    #rm -f ${output}GenToyWorkspace_${nickname}_${seed}.root

    #xrdcp -f ${output}GenToyTree_${nickname}_${seed}.root root://eoslhcb.cern.ch/${eosoutput}GenToyTree_${nickname}_${seed}.root
    #rm -f ${output}GenToyTree_${nickname}_${seed}.root

    #xrdcp -f ${output}log_${nickname}_${seed}.txt root://eoslhcb.cern.ch/${eosoutput}log_${nickname}_${seed}.txt

    
    set seed=`expr $seed + 1`
    echo $seed
    #@seed++

    #echo $($seed+1)
end
