#!/bin/bash

# Parallelize toy time fitting using LSF cern batch system
# Author: Vincenzo Battista (16/05/2015)

#---Setup toy info
#Job name
export jobname="Bd2DPiToysTimeFit"
#Starting toy
export start=$1
#Final toy for the first node (if stop=start+1, one toy per node is made)
export stop=$2
#Very last toy
export fullstop=$3
#Batch candidate queues
export queue="8nh"
#Memory limit (kB)
export mlimit="25000"
#Nickname for the current configuration
export nickname="OldTemplatesSimpleNonZeroDGAllCPterms"
#Tag to describe mass fit configuration
export massfitdescr="NoBkg"
#Tag to describe time fit configuration
export timefitdescr="DGSSbarDDbarFloating"
#Pathname of fitted toys
export input="root://eoslhcb.cern.ch//eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toysv3r0/${nickname}/sWeights/"
#Pathname to dump results
export output="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/${nickname}/TimeFit/"
export eosoutput="/eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toysv3r0/${nickname}/TimeFit/"

export bashscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/Bash/"
export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"

rm -rf $output
mkdir -p $output

/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select rm -r ${eosoutput}
/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select mkdir -p ${eosoutput}

export step=$(($stop - $start))

cd $pyscriptpath

job=1
while (( $stop <= $fullstop )); do

    bsub -q $queue -M $mlimit -e ${output}ERROR -o ${output}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${bashscriptpath}runBd2DPiTimeFitterOnToys.sh $start $stop $input $output $eosoutput $nickname $massfitdescr $timefitdescr

    #source ${bashscriptpath}runBd2DPiTimeFitterOnToys.sh $start $stop $input $output $eosoutput $nickname $massfitdescr $timefitdescr

    #Sleep to let afs breathing a bit
    if [[ "$(($job % 50))" -eq 0 ]]; then
        echo "Sleeping..."
        sleep 30
        job=0
    fi

    #Increase counters
    job=$(($job + 1))
    start=$(($start + $step))
    stop=$(($stop + $step))
    seed=$(($seed + $step))

done

#List submitted jobs
bjobs