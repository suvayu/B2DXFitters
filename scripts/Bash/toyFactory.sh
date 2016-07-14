#!/bin/bash

export workpath="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/scripts/"
export conf="/afs/cern.ch/user/v/vibattis/cmtuser/Urania_v4r0/PhysFit/B2DXFitters/data/toyFactoryConfig.py"

python ${workpath}toyFactory.py --configName $conf --workOut workspace --debug --saveTree --outputdir $workpath