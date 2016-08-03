#!/bin/bash

# @title Batch_toyFactory.sh
#
# @author Vincenzo Battista
# @date 21/07/2016
#
# @brief Run toy generation in parallel
#        using the LSF CERN batch system
#        on lxplus machines
#
#        Example: 1000 toys with seeds from 1000 to 2000,
#        10 toys per job
#        ./Batch_toyFactory.sh 1000 1010 2000

#---Setup toy info
#Job name
export jobname="Bd2DPiToysGen"
#Starting toy seed
export start=$1
#Stop toy seed for first job (if stop=start+1, one toy per job is made)
export stop=$2
#Final toy seed
export fullstop=$3
#Batch queue
export queue="1nh"
#Memory limit (kB)
export mlimit="50000"
#Nickname for the current configuration
#Choose a meaningful name (e.g. SgnAndBkgMeanResSplineAcc2TaggersNoAsymm etc...)
export nickname="MyTestToys"
#Configuration file
export config="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/data/toyFactoryConfig.py"
#Temporary pathname to dump results
export output="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/${nickname}/Generator/"
#Pathname to dump outputfiles (eos recommendend)
export eosoutput="/eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toys/${nickname}/Generator/"
#Path where scripts are located
export bashscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/Bash/"
export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"

#Clear directories
rm -rf $output
mkdir -p $output

/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select rm -r ${eosoutput}
/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select mkdir -p ${eosoutput}

cd $pyscriptpath

job=1
seed=$start
export step=$(($stop - $start))

echo ""
echo "################################"
echo "Submitting toys from ${start} to ${fullstop}"
echo "in steps of ${step}"
echo "################################"
echo ""

while (( $stop <= $fullstop )); do

    echo "...submitting job ${job} with starting seed ${seed}"

    #Submit jobs
    bsub -q $queue -M $mlimit -e ${output}ERROR -o ${output}OUTPUT -n 1,2 -R "span[hosts=-1]" -J ${jobname}_${seed} source ${bashscriptpath}toyFactory.sh $seed $stop $output $eosoutput $nickname $config $pyscriptpath
    
    source ${bashscriptpath}toyFactory.sh $seed $stop $output $eosoutput $nickname $config $pyscriptpath

    #Sleep to avoid afs overload (not sure this is the best trick)
    if [[ "$(($job % 50))" -eq 0 ]]; then
	echo "Sleeping..."
	sleep 30
    fi
    
    #Increase counters
    job=$(($job + 1))
    seed=$(($seed + $step))
    stop=$(($stop + $step))

done

#List submitted jobs
bjobs