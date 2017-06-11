#!/bin/bash

#Prevent core dump
ulimit -c 0

source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.sh
source `which SetupProject.sh` Urania v4r0

export dirinput=$3
export diroutput=$4
export eosoutput=$5
export seosoutput=$6
export sweightsdiroutput=$7
export nickname=$8
export massfitdescr=$9

export config="Bd2DPiConfigForToys"
export filename="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Workspace/NoSelection/work_dpi.root"

export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"

export outputprefix="DPi_Toys_MassFitResult_"${massfitdescr}"_"
export outputsuffix=".log"

export inputprefix="DPi_Toys_Work_"
export inputsuffix=".root"

export sweightsprefix="DPi_Toys_sWeights_ForTimeFit_"${massfitdescr}"_"
export massplotprefix="DPi_Toys_Work_ForMassPlot_"${massfitdescr}"_"
export pullplotprefix="DPi_Toys_Work_ForPullPlot_"${massfitdescr}"_"

export thissample=$1

while (( $thissample < $2 )); do 
    cd $pyscriptpath
    export thissamplestr=`echo $thissample`
    python ${pyscriptpath}runBd2DPiMassFitterOnToys.py --toys --merge --dim 2 --year 2012 -m both -o KPiPi --massplot --configName $config --fileName $filename --fileNameToys $dirinput$inputprefix$thissamplestr$inputsuffix --sweightoutputname $sweightsprefix$thissamplestr$inputsuffix --sweight --fileNamePull $pullplotprefix$thissamplestr$inputsuffix --save $massplotprefix$thissamplestr$inputsuffix --debug >& $outputprefix$thissamplestr$outputsuffix 
    
    xrdcp -f $sweightsprefix$thissamplestr$inputsuffix root://eoslhcb.cern.ch/${seosoutput}$sweightsprefix$thissamplestr$inputsuffix
    rm -f $sweightsprefix$thissamplestr$inputsuffix

    xrdcp -f $massplotprefix$thissamplestr$inputsuffix root://eoslhcb.cern.ch/${eosoutput}$massplotprefix$thissamplestr$inputsuffix
    rm -f $massplotprefix$thissamplestr$inputsuffix

    mv $pullplotprefix$thissamplestr$inputsuffix $diroutput
    xrdcp -f $diroutput$pullplotprefix$thissamplestr$inputsuffix root://eoslhcb.cern.ch/${eosoutput}$pullplotprefix$thissamplestr$inputsuffix

    mv $outputprefix$thissamplestr$outputsuffix $diroutput
    xrdcp -f $diroutput$outputprefix$thissamplestr$outputsuffix root://eoslhcb.cern.ch/${eosoutput}$outputprefix$thissamplestr$outputsuffix
    
    thissample=$(($thissample + 1))
    echo $thissample
done
