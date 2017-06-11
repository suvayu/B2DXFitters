#!/bin/bash

export workpath="/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Workspace/Nominal/"
export scriptpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/scripts/"
export save=${workpath}"work_dpi.root"

#rm -rf $workpath
mkdir -p $workpath
export conf="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForWorkspace_PiHypo_MC.py"
python ${scriptpath}prepareWorkspace.py --noRooKeysPdf --MC --debug -s $save --configName $conf
rm Trash/*.root
python ${scriptpath}prepareWorkspace.py --noRooKeysPdf --Signal --debug -i $save -s $save --configName $conf
rm Trash/*.root
export conf="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForWorkspace_KHypo_MC.py"
python ${scriptpath}prepareWorkspace.py --noRooKeysPdf --MC --debug -i $save -s $save --configName $conf
rm Trash/*.root
python ${scriptpath}prepareWorkspace.py --noRooKeysPdf --Signal --debug -i $save -s $save --configName $conf
rm Trash/*.root
export conf="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForWorkspace_PiHypo_Data.py"
python ${scriptpath}prepareWorkspace.py --noRooKeysPdf --Data --debug -i $save -s $save --configName $conf
rm Trash/*.root
python ${scriptpath}prepareWorkspace.py --noRooKeysPdf --Comb --debug -i $save -s $save --configName $conf
rm Trash/*.root
export conf="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v5r0/PhysFit/B2DXFitters/data/Bd2DPi_3fbCPV/Bd2DPi/Bd2DPiConfigForWorkspace_KHypo_Data.py"
python ${scriptpath}prepareWorkspace.py --noRooKeysPdf --Data --debug -i $save -s $save --configName $conf
rm Trash/*.root
python ${scriptpath}prepareWorkspace.py --noRooKeysPdf --Comb --debug -i $save -s $save --configName $conf
rm Trash/*.root