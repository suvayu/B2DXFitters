#!/bin/bash

#Input options
export inputdir="/eos/lhcb/user/v/vibattis/B2DX/Bd2DPi/Toys/SgnAndBkgTwoTaggersProdAsymm001AccMeanResTimeFrom02ps/MDFit/"
export inputprefix="PullTreeFitB_FullMDFit_SgnAndBkgTwoTaggersProdAsymm001AccMeanResTimeFrom02ps"
export outputfile="PullTreeFitB_FullMDFit_SgnAndBkgTwoTaggersProdAsymm001AccMeanResTimeFrom02ps.root"
export workpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/scripts/Bash/"
export start=0
export stop=5000

#Do merging
rm -f ${workpath}listOfPullTrees.txt
for (( file=$start; file<$stop; file++ )); do
    fileExist=`/afs/cern.ch/project/eos/installation/lhcb/bin/eos.select ls ${inputdir}${inputprefix}_${file}.root`
    exist=0
    if [ "$fileExist" == "${inputprefix}_${file}.root" ]; then
	exist=1
    fi
    if [ $exist -eq 0 ]; then
	echo "File ${inputdir}${inputprefix}_${file}.root does not exist. Skipping..."
    else
	if [ $file -eq 0 ]; then
	    echo "root://eoslhcb.cern.ch/${inputdir}${inputprefix}_${file}.root" > ${workpath}listOfPullTrees.txt
	else
	    echo "root://eoslhcb.cern.ch/${inputdir}${inputprefix}_${file}.root" >> ${workpath}listOfPullTrees.txt
	fi
    fi
done

echo "List of files to hadd:"
cat ${workpath}listOfPullTrees.txt