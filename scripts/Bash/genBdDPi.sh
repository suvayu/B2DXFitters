#!/bin/bash

#Prevent core dump
ulimit -c 0

source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.sh
source `which SetupProject.sh` Urania v4r0

export diroutput=$4

export eosoutput=$5

export nickname=$6

export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"

export thissample=$1
export ten=100

export logfile="log_gen_"
export logfileext=".txt"

export seed=$3

export config="Bd2DPiConfigForToys"

while (( $thissample < $2 )); do 
   export thissamplestr=`echo $thissample`
   export thissampleU=$(($thissample + 1))
   echo $thissample
   echo $thissampleU
   
   seed=$(($seed + $ten))
   echo $seed

   cd $pyscriptpath

   python ${pyscriptpath}GenerateToySWeights_DPi.py --configName $config --dir $pyscriptpath --start $thissample --end $thissampleU --seed $seed --debug --nodetasymmetry --noprodasymmetry --notagasymmetries --notagging --singletagger --noresolution --noacceptance >& $logfile$thissamplestr$logfileext

   xrdcp -f DPi_Toys_Work_$thissample.root root://eoslhcb.cern.ch/${eosoutput}DPi_Toys_Work_$thissample.root
   rm -f DPi_Toys_Work_$thissample.root

   mv $logfile$thissamplestr$logfileext $diroutput
   xrdcp -f $diroutput$logfile$thissamplestr$logfileext root://eoslhcb.cern.ch/$eosoutput$logfile$thissamplestr$logfileext

   thissample=$(($thissample + 1))

done

