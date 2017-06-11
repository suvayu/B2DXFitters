#!/bin/bash

# Parallelize toy mass fitting using LSF cern batch system
# Author: Vincenzo Battista (16/05/2015)

#---Setup toy info
#Job name
export jobname="Bd2DPiToysMassFit"
#Starting toy
export start=$1
#Final toy for the first node (if stop=start+1, one toy per node is made)
export stop=$2
#Very last toy
export fullstop=$3
#Batch queue
export queue="1nh"
#Memory limit (kB)
export mlimit="25000"
#Nickname for the current configuration
export nickname="OldTemplatesSimpleNonZeroDGAllCPterms"
#Tag to describe mass fit configuration
export massfitdescr="NoBkg"
#Pathname of generated toys
export input="root://eoslhcb.cern.ch//eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toysv3r0/${nickname}/Generator/" 
#Pathname to dump results
export output="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/${nickname}/MassFit/"
export eosoutput="/eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toysv3r0/${nickname}/MassFit/"
export seosoutput="/eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toysv3r0/${nickname}/sWeights/"
#Pathname to dump sWeights
export soutput="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/${nickname}/sWeights/"
#export soutput="root://eoslhcb.cern.ch//eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toysv3r0/${nickname}/sWeights/"

export bashscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/Bash/"
export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"

export step=$(($stop - $start))

rm -rf $output
mkdir -p $output

rm -rf $soutput
mkdir -p $soutput

/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select rm -r ${eosoutput}
/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select mkdir -p ${eosoutput}

/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select rm -r ${seosoutput}
/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select mkdir -p ${seosoutput}

cd $pyscriptpath

job=1
while (( $stop <= $fullstop )); do

    bsub -q $queue -M $mlimit -e ${output}ERROR -o ${output}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${bashscriptpath}runBd2DPiMassFitterOnToys.sh $start $stop $input $output $eosoutput $seosoutput $soutput $nickname $massfitdescr

    #source ${bashscriptpath}runBd2DPiMassFitterOnToys.sh $start $stop $input $output $eosoutput $seosoutput $soutput $nickname $massfitdescr

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