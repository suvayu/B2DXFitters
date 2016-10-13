#!/bin/bash

#Prevent core dump
ulimit -c 0

#source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod/InstallArea/scripts/LbLogin.sh
#source `which SetupProject.sh` Urania v5r0

#Options
export nickname="SSbarAccFloatingNoFTcalib"
export inputfile="root://eoslhcb.cern.ch//eos/lhcb/wg/b2oc/TD_DPi_3fb/sWeightedData/sWeights_AllData_from04ps.root"
export outputdir="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/sFit/${nickname}/"
export outputfile=${outputdir}"workResults.root"
export config="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForSFitOnData.py"
export pol="both"
export mode="kpipi"
export year="run1"
export hypo="Bd2DPi"
export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/scripts/"

rm -rf $outputdir
mkdir -p $outputdir

export Start=`date`
echo "==> Start fitting at ${Start}"

python ${pyscriptpath}runSFit_Bd.py --debug --fileName $inputfile --save $outputfile --configName $config --pol $pol --mode $mode --year $year --hypo $hypo --merge both >& ${outputdir}logfile.txt

export Stop=`date`
echo "==> Stop fitting at ${Stop}"