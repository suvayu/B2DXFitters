#!/bin/bash

#Prevent core dump
ulimit -c 0

source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.sh
source `which SetupProject.sh` Urania v4r0

export workpath=$1
export tuplepath=$2
export conf=$3
export inputfile=$4
export inputtree=$5
export outputfile=$6
export outputtree=$7
export maxTreeEntries=$8
export jobname=$9

cd $workpath

python ${workpath}ChangeMassHypo.py --debug --configName $conf --inputfile $inputfile --inputtree $inputtree --outputfile $outputfile --outputtree $outputtree --maxTreeEntries $maxTreeEntries --constraintCharmMass >& ${workdir}${jobname}.log