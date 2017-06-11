#!/bin/bash

#Prevent core dump
ulimit -c 0

#Get options
export seed=$1
export stop=$2
export output=$3
export eosoutput=$4
export eosinput=$5
export nicknamegen=$6
export nicknamemd=$7
export config=$8
export pyscriptpath=$9

#Setup environment
source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.sh
source `which SetupProject.sh` Urania v5r0

while (( $seed < $stop )); do

    cd $pyscriptpath

    #Run script
    python ${pyscriptpath}runMDFitter_Bd.py -d --seed $seed --configName $config --inputFile root://eoslhcb.cern.ch/${eosinput}GenToyWorkspace_${nicknamegen}_${seed}.root --merge alreadyboth --decay Bd2DPi --pol both --mode kpipi --year run1 --hypo Bd2DPi_Bd2DK --sWeightsName ${output}sWeights_${nicknamemd}_${nicknamegen}_${seed}.root --dim 1 --binned --sWeights --toys --pullFile root://eoslhcb.cern.ch/${eosoutput}PullTreeFitA_${nicknamemd}_${nicknamegen}_${seed}.root --pullFilesWeights root://eoslhcb.cern.ch/${eosoutput}PullTreeFitB_${nicknamemd}_${nicknamegen}_${seed}.root --outputFile ${output}MDFitResult_${nicknamemd}_${nicknamegen}_${seed}.root >& ${output}log_${nicknamemd}_${nicknamegen}_${seed}.txt  

    #Dump to EOS
    xrdcp -f ${output}sWeights_${nicknamemd}_${nicknamegen}_${seed}.root root://eoslhcb.cern.ch/${eosoutput}sWeights_${nicknamemd}_${nicknamegen}_${seed}.root
    rm -f ${output}sWeights_${nicknamemd}_${nicknamegen}_${seed}.root

    xrdcp -f ${output}MDFitResult_${nicknamemd}_${nicknamegen}_${seed}.root root://eoslhcb.cern.ch/${eosoutput}MDFitResult_${nicknamemd}_${nicknamegen}_${seed}.root
    rm -f ${output}MDFitResult_${nicknamemd}_${nicknamegen}_${seed}.root

    xrdcp -f ${output}log_${nicknamemd}_${nicknamegen}_${seed}.txt root://eoslhcb.cern.ch/${eosoutput}log_${nicknamemd}_${nicknamegen}_${seed}.txt
    
    seed=$(($seed + 1))

done