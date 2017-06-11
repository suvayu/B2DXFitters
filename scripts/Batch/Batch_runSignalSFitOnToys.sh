#!/bin/bash

# @title Batch_runSFitOnToys.sh
#
# @author Vincenzo Battista
# @date 01/08/2016
#
# @brief Run sFit in parallel on sWeighted toys
#        using the LSF CERN batch system
#        on lxplus machines
#
#        Example: 1000 toys with seeds from 1000 to 2000,
#        10 toys per job
#        ./Batch_runSFitOnToys.sh 1000 1010 2000

#---Setup toy info
#Job name
export jobname="Bd2DPiToysSFit"
#Starting toy
export start=$1
#Stop toy for the first node (if stop=start+1, one toy per node is made)
export stop=$2
#Final toy seed
export fullstop=$3
#Batch candidate queues
export queue="8nh"
#Memory limit (kB)
export mlimit="100000"
#Nickname for the current configuration
#Choose a meaningful name (e.g. SgnAndBkgMeanResSplineAcc2TaggersNoAsymm etc...)
export nickname="SimpleSgnAndBkgTwoTaggersProdDetAsymmAccMeanResTimeFrom04psSignal"
#Tag to describe mass fit configuration
#Choose a meaningful name (e.g. SignalPlusBackground etc...)
export massfitdescr="FullMDFit"
#Tag to describe time fit configuration
#Choose a meaningful name (e.g. SSbarFloating etc...) 
export timefitdescr="SSbarFloatAccProdDetAsymmGausConstHesse"
#Name of tree with weights
export treename="merged"
#Bachelor mass hypothesys
export hypo="Bd2DPi"
#D decay mode
#export mode="KPiPi" #from generation
export mode="kpipi" #after sWeights
#Year
export year="run1"
#Magnet polarity
export pol="both"
#Configuration file
export config="/afs/cern.ch/user/c/cofitzpa/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForSFitOnToys.py"
#Pathname of fitted toys

#export input="root://eoslhcb.cern.ch//eos/lhcb/wg/b2oc/TD_DPi_3fb/Toys/${nickname}/Generator/" 
export input="root://eoslhcb.cern.ch//eos/lhcb/user/c/cofitzpa/TD_DPi_3fb/Toys/${nickname}/Generator/" 
#Pathname to dump results
export output="/afs/cern.ch/work/c/cofitzpa/public/B2DX/Bd2DPi/Toys/${nickname}/TimeFit/${timefitdescr}/"
#export eosoutput="/eos/lhcb/wg/b2oc/TD_DPi_3fb/Toys/${nickname}/TimeFit/${timefitdescr}/"
export eosoutput="/eos/lhcb/user/c/cofitzpa/TD_DPi_3fb/Toys/${nickname}/TimeFit/${timefitdescr}/"
#Path where scripts are located
export bashscriptpath="/afs/cern.ch/user/c/cofitzpa/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/scripts/Bash/"
export pyscriptpath="/afs/cern.ch/user/c/cofitzpa/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/scripts/"

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

    #Submit job
    bsub -q $queue -M $mlimit -e ${output}ERROR -o ${output}OUTPUT -n 1,16 -R "span[hosts=-1]" -J ${jobname}_${job} source ${bashscriptpath}runSFitOnSignalToys.sh $seed $stop $input $output $eosoutput $nickname $massfitdescr $timefitdescr $config $pol $mode $year $hypo $pyscriptpath

    #source ${bashscriptpath}runSFitOnSignalToys.sh $seed $stop $input $output $eosoutput $nickname $massfitdescr $timefitdescr $config $pol $mode $year $hypo $pyscriptpath

    #Sleep to avoid afs overload (not sure this is the best trick)
    if [[ "$(($job % 50))" -eq 0 ]]; then
        echo "Sleeping..."
        sleep 30
    fi

    #Increase counters
    job=$(($job + 1))
    stop=$(($stop + $step))
    seed=$(($seed + $step))

done

#List submitted jobs
bjobs
