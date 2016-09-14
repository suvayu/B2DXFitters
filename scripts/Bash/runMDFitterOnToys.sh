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
    python ${pyscriptpath}runMDFitter_Bd.py -d --configName $config --inputFile root://eoslhcb.cern.ch/${eosinput}GenToyWorkspace_${nicknamegen}_${seed}.root --decay Bd2DPi --pol both --mode kpipi --year run1 --hypo Bd2DPi_Bd2DK --sWeightsName ${output}sWeights_${nicknamemd}_${nicknamegen}_${seed}.root --dim 1 --binned --sWeights --toys --noFitPlot --pullFile ${output}PullTree_${nicknamemd}_${nicknamegen}_${seed}.root >& ${output}log_${nicknamemd}_${nicknamegen}_${seed}.txt  

    #Dump to EOS
    xrdcp -f ${output}sWeights_${nicknamemd}_${nicknamegen}_${seed}.root root://eoslhcb.cern.ch/${eosoutput}sWeights_${nicknamemd}_${nicknamegen}_${seed}.root
    rm -f ${output}sWeights_${nicknamemd}_${nicknamegen}_${seed}.root
    
    xrdcp -f ${output}PullTree_${nicknamemd}_${nicknamegen}_${seed}.root root://eoslhcb.cern.ch/${eosoutput}PullTree_${nicknamemd}_${nicknamegen}_${seed}.root
    rm -f ${output}PullTree_${nicknamemd}_${nicknamegen}_${seed}.root

    xrdcp -f ${output}log_${nicknamemd}_${nicknamegen}_${seed}.txt root://eoslhcb.cern.ch/${eosoutput}log_${nicknamemd}_${nicknamegen}_${seed}.txt

    #If everything worked, add pull tree file to list
    fileExist=`/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select ls root://eoslhcb.cern.ch/${eosoutput}`
    for item in $fileExist; do
	if [ "$item" == "PullTree_${nicknamemd}_${nicknamegen}_${seed}.root" ]; then
	    echo "File root://eoslhcb.cern.ch/${eosoutput}PullTree_${nicknamemd}_${nicknamegen}_${seed}.root exist; copying to ${output}PullTreeListFile.txt"
	    echo "root://eoslhcb.cern.ch/${eosoutput}PullTree_${nicknamemd}_${nicknamegen}_${seed}.root" >> ${output}PullTreeListFile.txt
	    break
	else
	    echo "File root://eoslhcb.cern.ch/${eosoutput}PullTree_${nicknamemd}_${nicknamegen}_${seed}.root not found!!! Toy failed somehow..."
	fi
    done
    
    seed=$(($seed + 1))

done