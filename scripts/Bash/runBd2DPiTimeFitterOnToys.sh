#!/bin/bash

#Prevent core dump
ulimit -c 0

source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.sh
source `which SetupProject.sh` Urania v4r0

export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"

export dirinput=$3
export diroutput=$4
export eosoutput=$5
export nickname=$6
export massfitdescr=$7
export timefitdescr=$8

export outputprefix="DPi_Toys_TimeFitResult_"${timefitdescr}"_"
export outputsuffix=".log"

export inputprefix="DPi_Toys_sWeights_ForTimeFit_"${massfitdescr}"_"
export inputsuffix=".root"

export timeplotprefix="DPi_Toys_Work_TimeFitResult_"${timefitdescr}"_"
export pullplotprefix="DPi_Toys_Work_ForPullPlot_"${timefitdescr}"_"

export configMass="Bd2DPiConfigForToys"
export configTime="Bd2DPiConfigForToys"

export thissample=$1

export Start=`date`
echo "==> Start fitting at ${Start}"

while (( $thissample < $2 )); do 
    cd $pyscriptpath
    export thissamplestr=`echo $thissample`
    rm $diroutput$outputprefix$thissamplestr$outputsuffix
    rm $diroutput$outputprefix$thissamplestr$outputsuffix.gz

    python ${pyscriptpath}runBd2DPiCPAsymmObsFitterOnToys.py -d --nosWeights --configName $configTime --toys --nodetasymmetry --noprodasymmetry --notagasymmetries --noresolution --noacceptance --notagging --singletagger --configNameMDFitter $configMass --pathName $dirinput$inputprefix$thissamplestr$inputsuffix --save $timeplotprefix$thissamplestr$inputsuffix --fileNamePull $pullplotprefix$thissamplestr$inputsuffix >& $outputprefix$thissamplestr$outputsuffix

    xrdcp -f $timeplotprefix$thissamplestr$inputsuffix root://eoslhcb.cern.ch/${eosoutput}$timeplotprefix$thissamplestr$inputsuffix
    rm -f $timeplotprefix$thissamplestr$inputsuffix

    mv $outputprefix$thissamplestr$outputsuffix $diroutput
    xrdcp -f $diroutput$outputprefix$thissamplestr$outputsuffix root://eoslhcb.cern.ch/${eosoutput}$outputprefix$thissamplestr$outputsuffix

    mv $pullplotprefix$thissamplestr$inputsuffix $diroutput
    xrdcp -f $diroutput$pullplotprefix$thissamplestr$inputsuffix root://eoslhcb.cern.ch/${eosoutput}$pullplotprefix$thissamplestr$inputsuffix

    thissample=$(($thissample + 1))
    echo $thissample
done

export Stop=`date`
echo "==> Stop fitting at ${Stop}"