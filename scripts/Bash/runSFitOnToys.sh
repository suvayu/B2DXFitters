#!/bin/bash

#Prevent core dump
ulimit -c 0

source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.sh
source `which SetupProject.sh` Urania v5r0

#Get options
export seed=$1
export stop=$2
export input=$3
export output=$4
export eosoutput=$5
export nickname=$6
export massfitdescr=$7
export timefitdescr=$8
export config=$9
export pol=${10}
export mode=${11}
export year=${12}
export hypo=${13}
export pyscriptpath=${14}

export Start=`date`
echo "==> Start fitting at ${Start}"

while (( $seed < $stop )); do 
    
    cd $pyscriptpath
    
    #sWeights_${massfitdescr}_${nickname}_${seed}.root
    #GenToyTree_${nickname}_${seed}.root

    #preselection="TMath::Abs(TrueID-100)<50"

    python ${pyscriptpath}runSFit_Bd.py --pereventmistag --toys --debug --fileName ${input}sWeights_${massfitdescr}_${nickname}_${seed}.root --save ${output}TimeFitToysResult_${nickname}_${timefitdescr}_${massfitdescr}_${seed}.root --fileNamePull root://eoslhcb.cern.ch/${eosoutput}PullTreeTimeFit_${nickname}_${timefitdescr}_${massfitdescr}_${seed}.root --outputdir $output --configName $config --pol $pol --mode $mode --year $year --hypo $hypo --merge both --randomise --seed $seed >& ${output}log_${nickname}_${timefitdescr}_${massfitdescr}_${seed}.txt

    xrdcp -f ${output}TimeFitToysResult_${nickname}_${timefitdescr}_${massfitdescr}_${seed}.root root://eoslhcb.cern.ch/${eosoutput}TimeFitToysResult_${nickname}_${timefitdescr}_${massfitdescr}_${seed}.root
    rm -f ${output}TimeFitToysResult_${nickname}_${timefitdescr}_${massfitdescr}_${seed}.root

    xrdcp -f ${output}log_${nickname}_${timefitdescr}_${massfitdescr}_${seed}.txt root://eoslhcb.cern.ch/${eosoutput}log_${nickname}_${timefitdescr}_${massfitdescr}_${seed}.txt

    seed=$(($seed + 1))

done

export Stop=`date`
echo "==> Stop fitting at ${Stop}"