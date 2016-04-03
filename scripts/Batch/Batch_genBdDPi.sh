#!/bin/bash

# Parallelize toy generation using LSF cern batch system
# Run it from the "script" directory!
# Author: Vincenzo Battista (16/05/2015)

#---Setup toy info
#Job name
export jobname="Bd2DPiToysGen"
#Starting toy
export start=$1
#Final toy for the first node (if stop=start+1, one toy per node is made)
export stop=$2
#Very last toy
export fullstop=$3
#Starting seed
export seed=$(($seed + $start))
#Batch queue
export queue="1nh"
#Memory limit (kB)
export mlimit="25000"
#Nickname for the current configuration
export nickname="OldTemplatesSimpleNonZeroDGAllCPterms"
#Pathname to dump results
export output="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Toys/${nickname}/Generator/"
export eosoutput="/eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toysv3r0/${nickname}/Generator/"

export bashscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/Bash/"
export pyscriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"

export step=$(($stop - $start))

rm -rf $output
mkdir -p $output

/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select rm -r ${eosoutput}
/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select mkdir -p ${eosoutput}

cd $pyscriptpath

job=1
while (( $stop <= $fullstop )); do

    #Sumbit jobs
    bsub -q $queue -M $mlimit -e ${output}ERROR -o ${output}OUTPUT -n 1,4 -R "span[hosts=-1]" -J $jobname source ${bashscriptpath}genBdDPi.sh $start $stop $seed $output $eosoutput $nickname
    
    #source ${bashscriptpath}genBdDPi.sh $start $stop $seed $output $eosoutput $nickname

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