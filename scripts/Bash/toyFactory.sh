#!/bin/bash

#Prevent core dump
ulimit -c 0

#Get options
export seed=$1
export stop=$2
export output=$3
export eosoutput=$4
export nickname=$5
export config=$6
export pyscriptpath=$7

#Setup environment
source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.sh
source `which SetupProject.sh` Urania v4r0

while (( $seed < $stop )); do
    
    cd $pyscriptpath

    python ${pyscriptpath}toyFactory.py --configName $config --seed $seed --workfileOut GenToy_${nickname}_${seed}.root --debug --outputdir $output >& ${output}log_${nickname}_${seed}.txt

    xrdcp -f ${output}GenToy_${nickname}_${seed}.root root://eoslhcb.cern.ch/${eosoutput}GenToy_${nickname}_${seed}.root
    rm -f ${output}GenToy_${nickname}_${seed}.root

    xrdcp -f ${output}log_${nickname}_${seed}.txt root://eoslhcb.cern.ch/${eosoutput}log_${nickname}_${seed}.txt

    seed=$(($seed + 1))

done