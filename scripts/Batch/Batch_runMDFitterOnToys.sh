#!/bin/bash

# @title Batch_runMDFitterOnToys.sh
#
# @author Vincenzo Battista
# @date 13/09/2016 
#
# @brief Run mass fitter on toys in parallel
#        using the LSF CERN batch system
#        on lxplus machines
#
#        Example: 1000 toys with seeds from 1000 to 2000,
#        10 toys per job:
#        ./Batch_runMDFitterOnToys.sh 1000 1010 2000 

#---Setup toy info
#Job name
export jobname="Bd2DPiToysMDFit"
#Starting toy seed
export start=$1
#Stop toy seed for first job (if stop=start+1, one toy per job is made)
export stop=$2
#Final toy seed
export fullstop=$3
#Batch queue
export queue="1nh"
#Memory limit (kB)
export mlimit="150000"
#Nickname for the current generation configuration
#Choose a meaningful name (e.g. SgnAndBkgMeanResSplineAcc2TaggersNoAsymm etc...)
export nicknamegen="SimpleSgnAndBkgTwoTaggersProdDetAsymmAccMeanResTimeFrom04ps"
#Nickname for the current MD fit configuration
#Choose a meaningful name (e.g. OnlyBmassNoLowMass etc...)
export nicknamemd="FullMDFit"
#Configuration file
export config="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForMDFitterOnToys.py"
#Temporary pathname to dump results
export output="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/${nicknamegen}/MDFit/"
#Pathname to dump outputfiles (eos recommendend)
export eosoutput="/eos/lhcb/wg/b2oc/TD_DPi_3fb/Toys/${nicknamegen}/MDFit/"
#Input file directory
export eosinput="/eos/lhcb/wg/b2oc/TD_DPi_3fb/Toys/${nicknamegen}/Generator/"
#Path where scripts are located
export bashscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/scripts/Bash/"
export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/scripts/"

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
    bsub -q $queue -M $mlimit -e ${output}ERROR -o ${output}OUTPUT -n 4 -R "span[hosts=-1]" -J ${jobname}_${seed} source ${bashscriptpath}runMDFitterOnToys.sh $seed $stop $output $eosoutput $eosinput $nicknamegen $nicknamemd $config $pyscriptpath

    #source ${bashscriptpath}runMDFitterOnToys.sh $seed $stop $output $eosoutput $eosinput $nicknamegen $nicknamemd $config $pyscriptpath

    #Sleep to avoid afs overload and buffer space consumption (not sure this is the best trick)
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