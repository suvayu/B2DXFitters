#!/bin/bash

export workdir="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"
export inputfile="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Workspace/Nominal/work_dpi.root"
export outputfile="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Workspace/Nominal/work_dpi_mdfit_bd.root"
export outputweightstree="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/sWeights/Nominal/sWeights_RunIdata.root"
export conf="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForMDFitter_Bd.py"
export outputplotdir="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/MDFitPlots_Bd/"

rm -rf $outputplotdir
mkdir -p $outputplotdir

rm -f $outputfile

python ${workdir}runMDFitter_Bd.py -d --configName $conf --inputFile $inputfile --sWeightsName $outputweightstree --mode kpipi --merge both --hypo Bd2DPi_Bd2DK --outputplotdir $outputplotdir --outputFile $outputfile --dim 1 --binned --sWeights >& ${outputplotdir}log_fit_Bd2DPi.txt

