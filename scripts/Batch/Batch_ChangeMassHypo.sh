#!/bin/bash

export workpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"
export tuplepath="root://eoslhcb.cern.ch//eos/lhcb/user/v/vibattis/B2DX/ntuples/"
export conf="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForChangeHypo.py"
export mlimit="25000"
export maxTreeEntries="-1"

cd $workpath

#Bd2DPi
inputfile=${tuplepath}"MC_Bd2DPi_Bd2DPiHypo_magDown_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bd2DPi_Bd2DKHypo_magDown_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bd2DPi_magD"
queue="2nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

inputfile=${tuplepath}"MC_Bd2DPi_Bd2DPiHypo_magUp_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bd2DPi_Bd2DKHypo_magUp_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bd2DPi_magU"
queue="2nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

#Bd2DK
inputfile=${tuplepath}"MC_Bd2DK_Bd2DPiHypo_magDown_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bd2DK_Bd2DKHypo_magDown_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bd2DK_magD"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

inputfile=${tuplepath}"MC_Bd2DK_Bd2DPiHypo_magUp_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bd2DK_Bd2DKHypo_magUp_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bd2DK_magU"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

#Bs2DsPi
inputfile=${tuplepath}"MC_Bs2DsPi_Bd2DPiHypo_magDown_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bs2DsPi_Bd2DKHypo_magDown_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bs2DsPi_magD"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

inputfile=${tuplepath}"MC_Bs2DsPi_Bd2DPiHypo_magUp_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bs2DsPi_Bd2DKHypo_magUp_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bs2DsPi_magU"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

#Bd2DstPi
inputfile=${tuplepath}"MC_Bd2DstPi_Bd2DPiHypo_magDown_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bd2DstPi_Bd2DKHypo_magDown_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bd2DstPi_magD"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

inputfile=${tuplepath}"MC_Bd2DstPi_Bd2DPiHypo_magUp_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bd2DstPi_Bd2DKHypo_magUp_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bd2DstPi_magU"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

#Bd2DRho
inputfile=${tuplepath}"MC_Bd2DRho_Bd2DPiHypo_magDown_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bd2DRho_Bd2DKHypo_magDown_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bd2DRho_magD"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

inputfile=${tuplepath}"MC_Bd2DRho_Bd2DPiHypo_magUp_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Bd2DRho_Bd2DKHypo_magUp_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Bd2DRho_magU"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

#Lb2LcPi
inputfile=${tuplepath}"MC_Lb2LcPi_Bd2DPiHypo_magDown_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Lb2LcPi_Bd2DKHypo_magDown_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Lb2LcPi_magD"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

inputfile=${tuplepath}"MC_Lb2LcPi_Bd2DPiHypo_magUp_S21_afterSelection.root"
inputtree="Bd2Dpi"
outputfile=${tuplepath}"MC_Lb2LcPi_Bd2DKHypo_magUp_S21_afterSelection.root"
outputtree="Bd2DK"
jobname="PiToK_Lb2LcPi_magU"
queue="1nd"
bsub -q $queue -M $mlimit -e ${workpath}ERROR -o ${workpath}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${workpath}Bash/ChangeMassHypo.sh $workpath $tuplepath $conf $inputfile $inputtree $outputfile $outputtree $maxTreeEntries $jobname

#Check jobs submission
bjobs